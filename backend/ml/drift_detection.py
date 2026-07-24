"""
drift_detection.py
==================
Data drift and model drift detection between a reference dataset (training)
and a new dataset (uploaded by user or scored in production).

Implements:
  - Population Stability Index (PSI) per feature
  - Kolmogorov–Smirnov test (KS) per feature
  - Jensen–Shannon divergence per feature
  - Overall drift verdict with recommended action
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]

# PSI thresholds (industry standard)
PSI_STABLE      = 0.10   # < 0.10  → no drift
PSI_MODERATE    = 0.20   # 0.10–0.20 → minor drift, monitor
PSI_SIGNIFICANT = 0.20   # > 0.20  → significant drift, retrain

# KS p-value threshold
KS_ALPHA = 0.05


# ─── PSI ─────────────────────────────────────────────────────────────────────
def _compute_psi_single(
    expected: np.ndarray,
    actual: np.ndarray,
    n_bins: int = 10,
) -> float:
    """
    Compute Population Stability Index (PSI) for a single feature.
    PSI = Σ (actual_pct - expected_pct) × ln(actual_pct / expected_pct)
    """
    eps = 1e-8
    # Use expected-data-based bin edges
    _, bin_edges = np.histogram(expected, bins=n_bins)
    bin_edges[0]  = -np.inf
    bin_edges[-1] =  np.inf

    exp_hist, _ = np.histogram(expected, bins=bin_edges)
    act_hist, _ = np.histogram(actual,   bins=bin_edges)

    exp_pct = exp_hist / max(len(expected), 1) + eps
    act_pct = act_hist / max(len(actual), 1)   + eps

    psi_val = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
    return round(psi_val, 6)


def compute_psi_all_features(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    feature_cols: List[str] = None,
    n_bins: int = 10,
) -> Dict[str, float]:
    """Compute PSI for every feature column."""
    if feature_cols is None:
        feature_cols = [c for c in FEATURE_COLS if c in reference_df.columns and c in new_df.columns]

    return {
        col: _compute_psi_single(
            reference_df[col].dropna().values,
            new_df[col].dropna().values,
            n_bins=n_bins,
        )
        for col in feature_cols
    }


# ─── KS Test ──────────────────────────────────────────────────────────────────
def compute_ks_all_features(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    feature_cols: List[str] = None,
) -> Dict[str, Dict[str, float]]:
    """Run two-sample KS test for every feature column."""
    if feature_cols is None:
        feature_cols = [c for c in FEATURE_COLS if c in reference_df.columns and c in new_df.columns]

    results: Dict[str, Dict[str, float]] = {}
    for col in feature_cols:
        ks_stat, p_value = stats.ks_2samp(
            reference_df[col].dropna().values,
            new_df[col].dropna().values,
        )
        results[col] = {
            "ks_statistic": round(float(ks_stat), 5),
            "p_value":       round(float(p_value), 5),
            "drift_detected": bool(p_value < KS_ALPHA),
        }
    return results


# ─── Jensen–Shannon Divergence ────────────────────────────────────────────────
def _js_divergence(
    p_arr: np.ndarray,
    q_arr: np.ndarray,
    n_bins: int = 20,
) -> float:
    """Compute JS divergence between two 1-D arrays via histogram approximation."""
    eps = 1e-10
    all_vals = np.concatenate([p_arr, q_arr])
    bins = np.linspace(all_vals.min(), all_vals.max(), n_bins + 1)

    p_hist, _ = np.histogram(p_arr, bins=bins, density=True)
    q_hist, _ = np.histogram(q_arr, bins=bins, density=True)

    p_hist = p_hist + eps
    q_hist = q_hist + eps
    p_hist /= p_hist.sum()
    q_hist /= q_hist.sum()

    m = 0.5 * (p_hist + q_hist)
    jsd = 0.5 * np.sum(p_hist * np.log(p_hist / m)) + \
          0.5 * np.sum(q_hist * np.log(q_hist / m))
    return round(float(jsd), 6)


def compute_js_all_features(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    feature_cols: List[str] = None,
) -> Dict[str, float]:
    if feature_cols is None:
        feature_cols = [c for c in FEATURE_COLS if c in reference_df.columns and c in new_df.columns]
    return {
        col: _js_divergence(
            reference_df[col].dropna().values,
            new_df[col].dropna().values,
        )
        for col in feature_cols
    }


# ─── Target / Label Drift ────────────────────────────────────────────────────
def detect_target_drift(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    target_col: str = "label",
) -> Dict[str, Any]:
    """Detect shift in fraud rate between reference and new dataset."""
    result: Dict[str, Any] = {"has_target": False}

    if target_col not in reference_df.columns or target_col not in new_df.columns:
        return result

    result["has_target"] = True
    ref_rate = float(reference_df[target_col].mean())
    new_rate = float(new_df[target_col].mean())
    delta    = abs(new_rate - ref_rate)

    result["reference_fraud_rate"] = round(ref_rate, 4)
    result["new_fraud_rate"]        = round(new_rate, 4)
    result["absolute_delta"]        = round(delta,    4)
    result["relative_change_pct"]   = round(delta / max(ref_rate, 1e-8) * 100, 2)
    result["drift_detected"]        = delta > 0.01  # 1pp threshold

    return result


# ─── Comprehensive Drift Report ───────────────────────────────────────────────
def detect_drift(
    reference_df: pd.DataFrame,
    new_df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run full drift analysis and return a structured report.

    Returns
    -------
    drift_report : dict with PSI, KS, JS scores per feature plus overall verdict
    """
    if feature_cols is None:
        feature_cols = [
            c for c in FEATURE_COLS
            if c in reference_df.columns and c in new_df.columns
        ]

    psi_scores = compute_psi_all_features(reference_df, new_df, feature_cols)
    ks_scores  = compute_ks_all_features( reference_df, new_df, feature_cols)
    js_scores  = compute_js_all_features( reference_df, new_df, feature_cols)
    target_drift = detect_target_drift(reference_df, new_df)

    # ── Per-feature verdict ───────────────────────────────────────────────
    feature_verdicts: Dict[str, Dict[str, Any]] = {}
    drifted_features: List[str] = []

    for col in feature_cols:
        psi = psi_scores.get(col, 0)
        ks  = ks_scores.get(col, {})
        js  = js_scores.get(col, 0)

        drift_flags = [
            psi >= PSI_MODERATE,
            ks.get("drift_detected", False),
            js > 0.1,
        ]
        feature_drift = sum(drift_flags) >= 2  # majority vote

        feature_verdicts[col] = {
            "psi":            psi,
            "ks_statistic":   ks.get("ks_statistic", None),
            "ks_p_value":     ks.get("p_value",       None),
            "js_divergence":  js,
            "drift_detected": feature_drift,
            "psi_category":   (
                "stable"      if psi < PSI_STABLE else
                "moderate"    if psi < PSI_SIGNIFICANT else
                "significant"
            ),
        }
        if feature_drift:
            drifted_features.append(col)

    # ── Overall verdict ───────────────────────────────────────────────────
    avg_psi         = float(np.mean(list(psi_scores.values()))) if psi_scores else 0.0
    n_drifted       = len(drifted_features)
    overall_drift   = n_drifted >= max(1, len(feature_cols) // 3)
    recommend_retrain = overall_drift or target_drift.get("drift_detected", False)

    report: Dict[str, Any] = {
        "summary": {
            "n_features_checked":  len(feature_cols),
            "n_features_drifted":  n_drifted,
            "drifted_features":    drifted_features,
            "average_psi":         round(avg_psi, 4),
            "overall_drift":       overall_drift,
            "recommend_retrain":   recommend_retrain,
            "recommendation": (
                "RETRAIN IMMEDIATELY – significant population shift detected."
                if recommend_retrain else
                "No significant drift. Continue monitoring."
            ),
        },
        "feature_drift": feature_verdicts,
        "target_drift":  target_drift,
    }

    if recommend_retrain:
        logger.warning("Drift detected! Retraining recommended. Drifted features: %s", drifted_features)
    else:
        logger.info("No significant drift detected.")

    return report
