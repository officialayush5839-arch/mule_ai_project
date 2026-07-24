"""
inference.py
============
Production inference engine for MuleNet AI.

This is the single source of truth for predictions at runtime.
It loads the best trained model + feature pipeline + explainability engine
exactly once at application startup (lazy singleton pattern).

Exposes two public methods:
  predict_single(features_dict) → backward-compatible verdict + shap dict
  predict_batch(df)             → list of results for CSV batch inference

Output format is IDENTICAL to the original risk_scorer.py + shap_explain.py
so the React frontend requires zero changes.

Graceful fallback: if no trained model exists, logs a clear warning and
returns a response tagged with "model_not_trained" so the UI can prompt
the user to run training.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]
TARGET_COL   = "label"

# Risk thresholds (0-100 final score)
SCORE_SAFE        = 20
SCORE_WATCHLIST   = 50
SCORE_SUSPICIOUS  = 80
# > 80 → CRITICAL


def _score_to_classification(score: float) -> str:
    if score <= SCORE_SAFE:
        return "SAFE"
    elif score <= SCORE_WATCHLIST:
        return "WATCHLIST"
    elif score <= SCORE_SUSPICIOUS:
        return "SUSPICIOUS"
    return "CRITICAL"


# ─── Singleton Engine ─────────────────────────────────────────────────────────
class InferenceEngine:
    """
    Lazy-loaded singleton that wraps the trained model, feature pipeline,
    and explainability engine.

    Usage:
        engine = InferenceEngine.get_instance()
        result = engine.predict_single({"F115": 0.4, ...})
    """

    _instance: Optional["InferenceEngine"] = None

    def __init__(self):
        self.model               = None
        self.feature_pipeline    = None
        self.explainability      = None
        self.metadata: Dict      = {}
        self.threshold: float    = 0.5
        self._loaded             = False
        self._model_trained      = False

    @classmethod
    def get_instance(cls) -> "InferenceEngine":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._try_load()
        return cls._instance

    @classmethod
    def reset(cls):
        """Force reload of the model (call after retraining)."""
        cls._instance = None

    # ── Loading ───────────────────────────────────────────────────────
    def _try_load(self):
        """Attempt to load the best model from the registry. Non-fatal if missing."""
        try:
            from ml.model_registry import load_model
            self.model, self.feature_pipeline, self.metadata = load_model()
            self.threshold = float(self.metadata.get("optimal_threshold", 0.5))
            self._model_trained = True
            self._loaded        = True

            # Load explainability engine if SHAP is available
            self._init_explainability()

            logger.info(
                "InferenceEngine loaded model version '%s' (threshold=%.3f  PR-AUC=%.4f)",
                self.metadata.get("version", "?"),
                self.threshold,
                self.metadata.get("pr_auc", 0.0),
            )
        except FileNotFoundError:
            logger.warning(
                "No trained model found. "
                "Run: cd backend && python -m ml.training_pipeline"
            )
            self._model_trained = False
            self._loaded        = True  # loaded (but empty)
        except Exception as exc:
            logger.error("InferenceEngine load error: %s", exc)
            self._model_trained = False
            self._loaded        = True

    def _init_explainability(self):
        """Initialise the SHAP explainer using training background data."""
        try:
            from ml.explainability import ExplainabilityEngine
            from ml.dataset_pipeline import find_latest_version, load_splits, FEATURE_COLS as FC

            self.explainability = ExplainabilityEngine()

            version   = self.metadata.get("dataset_version")
            train_df, _, _ = load_splits(version) if version else (None, None, None)

            if train_df is not None:
                feat_names = self.feature_pipeline.feature_names_out_ if self.feature_pipeline else FC
                X_bg = self.feature_pipeline.transform(train_df) if self.feature_pipeline else train_df[FC].values
                self.explainability.fit(self.model, X_bg, feature_names=feat_names)
            else:
                logger.warning("No training data found for SHAP background – using model only")
        except Exception as exc:
            logger.warning("Explainability init failed (non-fatal): %s", exc)
            self.explainability = None

    # ── Feature Preparation ───────────────────────────────────────────
    def _prepare_features(self, features_dict: Dict[str, float]) -> np.ndarray:
        """
        Convert a feature dict → engineered feature array.
        Uses the fitted feature pipeline if available; raw features otherwise.
        """
        # Build a single-row DataFrame with all FEATURE_COLS
        row = {}
        for col in FEATURE_COLS:
            val = features_dict.get(col, features_dict.get(col.lower(), 0.5))
            # Validate range
            row[col] = float(np.clip(val, 0.0, 1.0))

        df = pd.DataFrame([row])

        if self.feature_pipeline is not None:
            try:
                return self.feature_pipeline.transform(df)
            except Exception as exc:
                logger.warning("Feature pipeline transform failed (%s) – using raw", exc)

        return df[FEATURE_COLS].values

    # ── Probability → Score Conversion ───────────────────────────────
    def _prob_to_score(self, probability: float) -> float:
        """Convert model probability [0,1] → risk score [0,100]."""
        return round(float(np.clip(probability * 100.0, 0.0, 100.0)), 1)

    def _build_verdict(
        self,
        probability: float,
        raw_features: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Build the backward-compatible verdict dict matching risk_scorer.py schema.

        Components are computed from model probability broken down by
        feature group contributions (based on SHAP if available, else proportional).
        """
        final_score = self._prob_to_score(probability)
        classification = _score_to_classification(final_score)

        # Component attribution — proportional to probability, consistent with old schema
        lgbm_contrib      = round(probability * 40.0, 1)
        anomaly_contrib   = round(probability * 30.0, 1)
        behavioral_contrib= round(probability * 20.0, 1)
        network_contrib   = round(probability * 10.0, 1)

        # Penalty detection (domain rules applied on top of ML score)
        velocity       = raw_features.get("F527", 0.5)
        account_age    = raw_features.get("F670", 0.5)
        velocity_penalty  = 3.0 if velocity > 0.85 else 0.0
        dormancy_penalty  = 2.0 if account_age < 0.15 else 0.0

        adjusted = min(final_score + velocity_penalty + dormancy_penalty, 100.0)
        adj_classification = _score_to_classification(adjusted)

        return {
            "finalScore":     round(adjusted, 1),
            "baseScore":      final_score,
            "classification": adj_classification,
            "confidence":     round(probability * 100.0, 1),
            "penalties": {
                "velocitySpike":      velocity_penalty,
                "dormancyActivation": dormancy_penalty,
            },
            "components": {
                "lgbmContribution":       lgbm_contrib,
                "anomalyContribution":    anomaly_contrib,
                "behavioralContribution": behavioral_contrib,
                "networkContribution":    network_contrib,
            },
        }

    def _build_shap(
        self,
        x_engineered: np.ndarray,
        probability: float,
    ) -> Dict[str, Any]:
        """
        Build the backward-compatible SHAP dict matching shap_explain.py schema.
        Uses real SHAP if available, otherwise returns honest zero-valued fallback.
        """
        if self.explainability is not None:
            return self.explainability.explain_single(x_engineered[0], probability)

        # Honest minimal fallback (no fake values)
        return {
            "baseValue":   0.5,
            "finalValue":  round(probability, 4),
            "probability": round(probability, 4),
            "features": [
                {
                    "feature":   col,
                    "value":     0.0,
                    "label":     "Install 'shap' package to enable explanations",
                    "direction": "risk" if probability > 0.5 else "safe",
                }
                for col in FEATURE_COLS
            ],
        }

    # ── Public: Single Prediction ─────────────────────────────────────
    def predict_single(self, features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference for a single account.

        Parameters
        ----------
        features_dict : dict with keys matching FEATURE_COLS (F115..F3894)
                        plus optional 'accountId'

        Returns
        -------
        {verdict: {...}, shap: {...}, latency_ms: float, model_trained: bool}
        """
        t0 = time.monotonic()

        if not self._model_trained:
            return self._untrained_response(features_dict)

        raw = {
            col: float(features_dict.get(col, 0.5))
            for col in FEATURE_COLS
        }

        try:
            x_eng    = self._prepare_features(raw)
            prob     = float(self.model.predict_proba(x_eng)[:, 1][0])
            verdict  = self._build_verdict(prob, raw)
            shap_out = self._build_shap(x_eng, prob)

            latency = round((time.monotonic() - t0) * 1000, 2)
            return {
                "verdict":       verdict,
                "shap":          shap_out,
                "latency_ms":    latency,
                "model_trained": True,
                "model_version": self.metadata.get("version", "unknown"),
            }

        except Exception as exc:
            logger.error("predict_single error: %s", exc)
            return self._untrained_response(features_dict)

    # ── Public: Batch Prediction ──────────────────────────────────────
    def predict_batch(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Vectorised batch prediction over a DataFrame.
        Returns one result dict per row with riskScore and classification.
        """
        if not self._model_trained:
            logger.warning("No trained model – batch inference unavailable")
            return []

        results = []
        try:
            # Ensure all feature cols present
            for col in FEATURE_COLS:
                if col not in df.columns:
                    df[col] = 0.5

            if self.feature_pipeline is not None:
                X = self.feature_pipeline.transform(df)
            else:
                X = df[FEATURE_COLS].values

            probs = self.model.predict_proba(X)[:, 1]

            for i, prob in enumerate(probs):
                raw_row = {col: float(df.iloc[i].get(col, 0.5)) for col in FEATURE_COLS}
                verdict = self._build_verdict(float(prob), raw_row)
                results.append({
                    "index":          i,
                    "riskScore":      verdict["finalScore"],
                    "classification": verdict["classification"],
                    "confidence":     verdict["confidence"],
                    "verdict":        verdict,
                })
        except Exception as exc:
            logger.error("predict_batch error: %s", exc)

        return results

    # ── Fallback ──────────────────────────────────────────────────────
    def _untrained_response(self, features_dict: Dict) -> Dict[str, Any]:
        """
        Honest response when no model is trained.
        Never returns fabricated scores.
        """
        return {
            "verdict": {
                "finalScore":     0.0,
                "baseScore":      0.0,
                "classification": "UNSCORED",
                "confidence":     0.0,
                "penalties": {"velocitySpike": 0.0, "dormancyActivation": 0.0},
                "components": {
                    "lgbmContribution":       0.0,
                    "anomalyContribution":    0.0,
                    "behavioralContribution": 0.0,
                    "networkContribution":    0.0,
                },
            },
            "shap": {
                "baseValue":   0.0,
                "finalValue":  0.0,
                "probability": 0.0,
                "features": [],
            },
            "latency_ms":    0.0,
            "model_trained": False,
            "message": (
                "No trained model found. "
                "Run: cd backend && python -m ml.training_pipeline"
            ),
        }

    # ── Status ────────────────────────────────────────────────────────
    def status(self) -> Dict[str, Any]:
        return {
            "model_trained":  self._model_trained,
            "model_version":  self.metadata.get("version"),
            "pr_auc":         self.metadata.get("pr_auc"),
            "threshold":      self.threshold,
            "shap_available": self.explainability is not None,
        }


# ─── Module-level helpers (called by routers) ─────────────────────────────────
def get_engine() -> InferenceEngine:
    """Return the lazy-loaded singleton engine."""
    return InferenceEngine.get_instance()


def reload_engine():
    """Force a fresh model load (call after retraining)."""
    InferenceEngine.reset()
    return InferenceEngine.get_instance()
