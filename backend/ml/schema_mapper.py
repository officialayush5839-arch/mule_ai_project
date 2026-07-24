"""
schema_mapper.py
================
Automatic mapping of arbitrary user column names to the internal F-code schema.

Uses a curated alias dictionary plus fuzzy sequence matching to handle typos,
abbreviations, and variant naming conventions from diverse banking datasets.
"""

import json
import logging
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILES_DIR = BASE_DIR / "data" / "mapping_profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# ─── Alias Registry ───────────────────────────────────────────────────────────
# Each F-code maps to a list of known column name variants found in banking CSVs.
COLUMN_ALIASES: Dict[str, List[str]] = {
    "F115": [
        "transaction_amount", "txn_amount", "amount", "transfer_amount",
        "transaction_volume", "volume", "balance", "account_balance",
        "total_amount", "fund_amount", "debit_amount", "credit_amount",
        "avg_txn_amount", "average_amount",
    ],
    "F321": [
        "source_concentration", "fund_concentration", "concentration_score",
        "source_diversity", "counterparty_concentration", "unique_senders",
        "sender_count", "source_count", "funding_diversity", "payer_diversity",
    ],
    "F527": [
        "velocity", "txn_velocity", "transaction_velocity", "velocity_ratio",
        "frequency", "txn_frequency", "transaction_frequency", "transaction_rate",
        "transaction_count", "txn_count", "monthly_txn_count", "daily_txn_count",
        "activity_rate",
    ],
    "F670": [
        "account_age", "age", "account_tenure", "tenure", "days_since_opening",
        "account_days", "account_maturity", "age_normalized", "account_vintage",
        "days_active", "open_days",
    ],
    "F1692": [
        "mule_score", "mule_pattern", "mule_probability", "fraud_pattern",
        "behavioural_score", "behavior_score", "behavioral_score",
        "pattern_score", "anomaly_pattern", "mule_indicator",
        "risk_pattern", "fraud_pattern_score",
    ],
    "F3043": [
        "outflow", "outflow_ratio", "outflow_dominance", "debit_ratio",
        "withdrawal_ratio", "fund_outflow", "outflow_rate",
        "transfer_out_ratio", "net_outflow", "cash_out_ratio",
    ],
    "F3894": [
        "anomaly_score", "anomaly_index", "outlier_score", "isolation_score",
        "lof_score", "anomaly", "fraud_score", "risk_anomaly",
        "isolation_forest_score", "one_class_score",
    ],
}

HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.60


# ─── Core Matching ────────────────────────────────────────────────────────────
def _similarity(a: str, b: str) -> float:
    """Character-level sequence similarity, case-insensitive."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _token_overlap(a: str, b: str) -> float:
    """Token-set overlap ratio (handles word-order variation)."""
    tokens_a = set(a.lower().replace("_", " ").split())
    tokens_b = set(b.lower().replace("_", " ").split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))


def _best_score(user_col: str, f_code: str) -> float:
    """Compute max match confidence between user_col and an F-code (+ its aliases)."""
    # Direct F-code match
    if user_col.lower() == f_code.lower():
        return 1.0

    best = 0.0
    for alias in COLUMN_ALIASES.get(f_code, []):
        sim = max(_similarity(user_col, alias), _token_overlap(user_col, alias))
        if sim > best:
            best = sim
    return best


# ─── Public API ───────────────────────────────────────────────────────────────
def map_columns(
    df_columns: List[str],
    confidence_threshold: float = MEDIUM_CONFIDENCE,
) -> Tuple[Dict[str, str], Dict[str, float], List[str]]:
    """
    Map arbitrary user column names → internal F-codes.

    Parameters
    ----------
    df_columns : list of column names from user's CSV
    confidence_threshold : minimum score to accept a mapping

    Returns
    -------
    mapping   : {user_col → F_code} (accepted mappings only)
    confidence: {user_col → score}  (all scores)
    unmapped  : user columns that did not reach the threshold
    """
    mapping: Dict[str, str]    = {}
    confidence: Dict[str, float] = {}
    used_targets: set = set()

    non_feature_cols = {"label", "is_fraud", "fraud", "target", "is_mule", "mule",
                        "id", "account_id", "accountid"}

    # Sort user columns by length desc so longer/more-specific names match first
    ordered_cols = sorted(df_columns, key=len, reverse=True)

    for user_col in ordered_cols:
        if user_col.lower() in non_feature_cols:
            continue

        best_target: Optional[str] = None
        best_score = 0.0

        for f_code in COLUMN_ALIASES:
            if f_code in used_targets:
                continue
            score = _best_score(user_col, f_code)
            if score > best_score:
                best_score  = score
                best_target = f_code

        confidence[user_col] = round(best_score, 3)

        if best_target and best_score >= confidence_threshold:
            mapping[user_col] = best_target
            used_targets.add(best_target)
            logger.debug(
                "Mapped '%s' → '%s'  (score=%.3f)", user_col, best_target, best_score
            )
        else:
            logger.debug(
                "Could not map '%s'  (best_score=%.3f)", user_col, best_score
            )

    unmapped = [
        c for c in df_columns
        if c not in mapping and c.lower() not in non_feature_cols
    ]

    return mapping, confidence, unmapped


def apply_mapping(df, mapping: Dict[str, str]):
    """Rename DataFrame columns using the computed mapping."""
    import pandas as pd
    return df.rename(columns=mapping)


def auto_map_dataframe(df, confidence_threshold: float = MEDIUM_CONFIDENCE):
    """
    Convenience wrapper: attempt to map columns and return the renamed DataFrame
    along with the mapping report.
    """
    mapping, confidence, unmapped = map_columns(
        list(df.columns), confidence_threshold
    )
    renamed_df = apply_mapping(df, mapping)

    report = {
        "mapping": mapping,
        "confidence": confidence,
        "unmapped": unmapped,
        "low_confidence_mappings": {
            c: {"mapped_to": mapping[c], "score": confidence[c]}
            for c in mapping
            if confidence[c] < HIGH_CONFIDENCE
        },
    }
    return renamed_df, report


# ─── Profile Persistence ──────────────────────────────────────────────────────
def save_mapping_profile(mapping: Dict[str, str], profile_name: str) -> None:
    """Save a column mapping profile for reuse on future uploads."""
    path = PROFILES_DIR / f"{profile_name}.json"
    with open(path, "w") as fh:
        json.dump(mapping, fh, indent=2)
    logger.info("Saved mapping profile: %s", path)


def load_mapping_profile(profile_name: str) -> Optional[Dict[str, str]]:
    """Load a previously saved mapping profile."""
    path = PROFILES_DIR / f"{profile_name}.json"
    if path.exists():
        with open(path) as fh:
            return json.load(fh)
    return None


def list_mapping_profiles() -> List[str]:
    """List all saved mapping profile names."""
    return [p.stem for p in PROFILES_DIR.glob("*.json")]
