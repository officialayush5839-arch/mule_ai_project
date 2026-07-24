"""
feature_engineering.py
=======================
Production feature engineering pipeline for MuleNet AI.

Implements a leak-free sklearn Pipeline that is:
  - Fit only on training data
  - Applied identically to validation and test splits
  - Persisted as a joblib artifact for inference reuse

Steps:
  1. Interaction features (domain-derived ratios & composites)
  2. RobustScaler  (chosen for skewed fraud feature distributions)
  3. Correlation pruning (drop columns with ρ > 0.95 to remove redundancy)
  4. Mutual Information feature ranking (informational, not filtration)
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import mutual_info_classif
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]
TARGET_COL   = "label"
RANDOM_SEED  = 42


# ─── Domain Interaction Feature Generator ─────────────────────────────────────
class InteractionFeatureGenerator(BaseEstimator, TransformerMixin):
    """
    Generates five domain-derived interaction features that capture
    mule-account patterns not visible in raw features alone.

    All input features are assumed to be in [0, 1] (post-normalisation).
    """

    INTERACTION_NAMES = [
        "outflow_dominance",       # F3043 / (F115 + eps) – how fast funds leave
        "velocity_concentration",  # F527 × F321          – fast + concentrated
        "dormancy_signal",         # 1 – F670             – newer account proxy
        "mule_anomaly_composite",  # F1692 × 0.6 + F3894 × 0.4
        "net_risk_index",          # mean of top-3 risk features
    ]

    def fit(self, X, y=None):
        # stateless transformer – nothing to fit
        return self

    def transform(self, X):
        """X must be a DataFrame with FEATURE_COLS columns."""
        df = pd.DataFrame(X, columns=FEATURE_COLS) if not isinstance(X, pd.DataFrame) else X.copy()
        eps = 1e-8

        df["outflow_dominance"]      = df["F3043"] / (df["F115"] + eps)
        df["velocity_concentration"] = df["F527"]  * df["F321"]
        df["dormancy_signal"]        = 1.0 - df["F670"]
        df["mule_anomaly_composite"] = df["F1692"] * 0.6 + df["F3894"] * 0.4
        df["net_risk_index"]         = df[["F527", "F1692", "F3043"]].mean(axis=1)

        # Clip any division artefacts
        for col in self.INTERACTION_NAMES:
            df[col] = df[col].clip(0.0, 10.0)

        return df.values

    def get_feature_names_out(self, input_features=None):
        return FEATURE_COLS + self.INTERACTION_NAMES


# ─── Correlation Pruner ───────────────────────────────────────────────────────
class CorrelationPruner(BaseEstimator, TransformerMixin):
    """
    Remove features whose absolute Pearson correlation with another feature
    exceeds `threshold` (default 0.95).  The first feature in each pair is kept.
    """

    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
        self.to_drop_: List[int] = []

    def fit(self, X, y=None):
        df = pd.DataFrame(X)
        corr = df.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        self.to_drop_ = [
            col for col in upper.columns if any(upper[col] > self.threshold)
        ]
        if self.to_drop_:
            logger.info("CorrelationPruner dropping columns: %s", self.to_drop_)
        return self

    def transform(self, X):
        df = pd.DataFrame(X)
        df = df.drop(columns=self.to_drop_, errors="ignore")
        return df.values


# ─── Full Pipeline ─────────────────────────────────────────────────────────────
def build_pipeline() -> Pipeline:
    """
    Construct the end-to-end feature engineering pipeline.
    Order matters: interactions → scale → prune correlations.
    """
    return Pipeline([
        ("interactions",   InteractionFeatureGenerator()),
        ("scaler",         RobustScaler()),
        ("corr_prune",     CorrelationPruner(threshold=0.95)),
    ])


class FeatureEngineeringPipeline:
    """
    Wrapper around the sklearn Pipeline that also stores feature names,
    mutual information scores, and provides serialisation helpers.
    """

    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.feature_names_in_: List[str] = FEATURE_COLS
        self.feature_names_out_: List[str] = []
        self.mi_scores_: Optional[np.ndarray] = None
        self.mi_ranking_: List[Dict[str, Any]] = []
        self._is_fitted = False

    # ── Fit ──────────────────────────────────────────────────────────────
    def fit(self, train_df: pd.DataFrame) -> "FeatureEngineeringPipeline":
        """
        Fit the pipeline on the training split ONLY.
        train_df must contain FEATURE_COLS columns.
        """
        X_raw = train_df[FEATURE_COLS].values
        y     = train_df[TARGET_COL].values if TARGET_COL in train_df.columns else None

        self.pipeline = build_pipeline()
        X_transformed = self.pipeline.fit_transform(X_raw)

        # ── Derive output feature names ───────────────────────────────
        n_out = X_transformed.shape[1]
        gen_names = FEATURE_COLS + InteractionFeatureGenerator.INTERACTION_NAMES
        # CorrelationPruner may have dropped some; recompute
        full_frame = pd.DataFrame(
            self.pipeline.named_steps["scaler"].transform(
                self.pipeline.named_steps["interactions"].transform(X_raw)
            )
        )
        dropped = self.pipeline.named_steps["corr_prune"].to_drop_
        kept_indices = [i for i in range(len(gen_names)) if i not in dropped]
        self.feature_names_out_ = [gen_names[i] for i in kept_indices]

        # ── Mutual information ────────────────────────────────────────
        if y is not None:
            try:
                mi = mutual_info_classif(
                    X_transformed, y, random_state=RANDOM_SEED
                )
                self.mi_scores_ = mi
                sorted_idx = np.argsort(mi)[::-1]
                self.mi_ranking_ = [
                    {
                        "feature": self.feature_names_out_[i],
                        "mi_score": round(float(mi[i]), 5),
                        "rank": rank + 1,
                    }
                    for rank, i in enumerate(sorted_idx)
                ]
                logger.info(
                    "Top MI features: %s",
                    [r["feature"] for r in self.mi_ranking_[:5]],
                )
            except Exception as exc:
                logger.warning("Mutual information computation failed: %s", exc)

        self._is_fitted = True
        logger.info(
            "FeatureEngineeringPipeline fitted. Input: %d  Output: %d features",
            len(FEATURE_COLS), X_transformed.shape[1],
        )
        return self

    # ── Transform ────────────────────────────────────────────────────────
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted:
            raise RuntimeError("Pipeline not fitted. Call fit() first.")
        # Ensure all FEATURE_COLS are present; use 0.5 as structural default
        for col in FEATURE_COLS:
            if col not in df.columns:
                logger.warning("Column %s missing – using 0.5 structural default", col)
                df = df.copy()
                df[col] = 0.5
        return self.pipeline.transform(df[FEATURE_COLS].values)

    def fit_transform(self, train_df: pd.DataFrame) -> np.ndarray:
        self.fit(train_df)
        return self.transform(train_df)

    # ── Serialisation ────────────────────────────────────────────────────
    def save(self, version: str) -> Path:
        vdir = MODELS_DIR / version
        vdir.mkdir(parents=True, exist_ok=True)
        artifact_path = vdir / "feature_pipeline.joblib"
        joblib.dump(self, artifact_path)
        # Also save MI ranking as JSON for reporting
        mi_path = vdir / "mi_ranking.json"
        with open(mi_path, "w") as fh:
            json.dump(self.mi_ranking_, fh, indent=2)
        logger.info("Feature pipeline saved to %s", artifact_path)
        return artifact_path

    @classmethod
    def load(cls, version: str) -> "FeatureEngineeringPipeline":
        artifact_path = MODELS_DIR / version / "feature_pipeline.joblib"
        if not artifact_path.exists():
            raise FileNotFoundError(f"Feature pipeline not found: {artifact_path}")
        instance = joblib.load(artifact_path)
        logger.info("Feature pipeline loaded from %s", artifact_path)
        return instance

    # ── Info ─────────────────────────────────────────────────────────────
    def get_feature_info(self) -> Dict[str, Any]:
        return {
            "input_features":  self.feature_names_in_,
            "output_features": self.feature_names_out_,
            "mi_ranking":      self.mi_ranking_,
        }
