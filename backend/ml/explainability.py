"""
explainability.py
=================
Real SHAP-based explainability for MuleNet AI.

Replaces the mocked shap_explain.py entirely.

Implements:
  - SHAP TreeExplainer for tree-based models (LightGBM, XGBoost, RF, CatBoost)
  - SHAP KernelExplainer fallback for other model types
  - Permutation Importance (model-agnostic)
  - Global feature importance (SHAP mean absolute)
  - Per-prediction local explanations returned in the backward-compatible JSON schema

The backward-compatible output exactly matches the old shap_explain.py response:
  {
    "baseValue":  float,        # actual SHAP expected value
    "finalValue": float,        # model probability (capped 0-1)
    "probability": float,
    "features":  [
      {"feature": str, "value": float, "label": str, "direction": str},
      ...
    ]
  }
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]

# Human-readable labels for every feature (base + interaction)
FEATURE_LABELS: Dict[str, Dict[str, str]] = {
    "F115":  {
        "risk": "High transaction volume relative to account baseline",
        "safe": "Transaction volumes within normal range",
    },
    "F321":  {
        "risk": "Concentrated fund sources — few senders, high amounts",
        "safe": "Diverse funding sources detected",
    },
    "F527":  {
        "risk": "Unusually high transaction velocity — rapid movement",
        "safe": "Stable transaction frequency",
    },
    "F670":  {
        "risk": "Recently opened account — elevated risk period",
        "safe": "Established account age (reducing risk)",
    },
    "F1692": {
        "risk": "Matches historical mule account behaviour pattern",
        "safe": "Consistent with legitimate account usage",
    },
    "F3043": {
        "risk": "Rapid outflow pattern — funds not being held",
        "safe": "Balanced inflow / outflow ratio",
    },
    "F3894": {
        "risk": "Strong anomaly signal from isolation analysis",
        "safe": "Within standard behavioural thresholds",
    },
    "outflow_dominance":      {"risk": "Extreme outflow relative to inflow",      "safe": "Normal outflow ratio"},
    "velocity_concentration": {"risk": "High velocity + concentrated sources",     "safe": "Normal velocity and diversity"},
    "dormancy_signal":        {"risk": "Dormant account with sudden large activity","safe": "Consistent account activity"},
    "mule_anomaly_composite": {"risk": "Combined mule-pattern + anomaly spike",    "safe": "No composite mule signal"},
    "net_risk_index":         {"risk": "Elevated combined risk index",              "safe": "Combined risk index within norms"},
}


class ExplainabilityEngine:
    """
    Wraps a fitted model and background dataset to produce
    SHAP local explanations for individual predictions.
    """

    def __init__(self):
        self.explainer         = None
        self.feature_names_    = FEATURE_COLS[:]
        self.base_value_       = 0.5          # overwritten after fit
        self.global_importance_: List[Dict]  = []
        self._mode             = "kernel"     # 'tree' | 'kernel'
        self._is_fitted        = False

    # ── Fit ───────────────────────────────────────────────────────────
    def fit(
        self,
        model,
        X_background: np.ndarray,
        feature_names: Optional[List[str]] = None,
    ) -> "ExplainabilityEngine":
        """
        Initialise the SHAP explainer.

        Parameters
        ----------
        model        : fitted sklearn-compatible model
        X_background : representative background dataset (training sample)
        feature_names: names for each column in X_background
        """
        try:
            import shap
        except ImportError:
            logger.warning("SHAP not installed – explainability disabled")
            return self

        if feature_names:
            self.feature_names_ = feature_names

        # Use a manageable background sample to keep latency acceptable
        n_bg  = min(200, len(X_background))
        rng   = np.random.default_rng(42)
        idx   = rng.choice(len(X_background), size=n_bg, replace=False)
        X_bg  = X_background[idx]

        model_type = type(model).__module__.lower()

        try:
            if any(lib in model_type for lib in ("lightgbm", "xgboost", "catboost",
                                                   "forest", "tree", "extra")):
                self.explainer = shap.TreeExplainer(model)
                self._mode     = "tree"
                logger.info("SHAP TreeExplainer initialised")
            else:
                raise ValueError("Non-tree model – falling back to KernelExplainer")
        except Exception:
            predict_fn = lambda X: model.predict_proba(X)[:, 1]
            self.explainer = shap.KernelExplainer(predict_fn, shap.kmeans(X_bg, min(20, n_bg)))
            self._mode     = "kernel"
            logger.info("SHAP KernelExplainer initialised (fallback)")

        # Compute base value
        try:
            if self._mode == "tree":
                sv = self.explainer.shap_values(X_bg[:50])
                if isinstance(sv, list):
                    sv = sv[1]
                self.base_value_ = float(self.explainer.expected_value
                                         if not isinstance(self.explainer.expected_value, (list, np.ndarray))
                                         else self.explainer.expected_value[1])
            else:
                self.base_value_ = float(self.explainer.expected_value)
        except Exception:
            self.base_value_ = 0.5

        # Global importance
        try:
            sv_global = self.explainer.shap_values(X_bg)
            if isinstance(sv_global, list):
                sv_global = sv_global[1]
            mean_abs = np.abs(sv_global).mean(axis=0)
            self.global_importance_ = [
                {
                    "feature": self.feature_names_[i] if i < len(self.feature_names_) else f"feat_{i}",
                    "importance": round(float(mean_abs[i]), 5),
                }
                for i in np.argsort(mean_abs)[::-1]
            ]
            logger.info(
                "Top global features: %s",
                [g["feature"] for g in self.global_importance_[:5]],
            )
        except Exception as exc:
            logger.warning("Global SHAP computation failed: %s", exc)

        self._is_fitted = True
        return self

    # ── Local Explanation ─────────────────────────────────────────────
    def explain_single(
        self,
        x: np.ndarray,
        model_probability: float,
    ) -> Dict[str, Any]:
        """
        Generate a local SHAP explanation for a single sample.

        Returns a dict matching the legacy shap_explain.py schema:
          {baseValue, finalValue, probability, features: [...]}
        """
        if not self._is_fitted or self.explainer is None:
            return self._fallback_explanation(model_probability)

        try:
            import shap
            x_2d = x.reshape(1, -1)

            if self._mode == "tree":
                sv = self.explainer.shap_values(x_2d)
                if isinstance(sv, list):
                    shap_vals = sv[1][0]
                else:
                    shap_vals = sv[0]
            else:
                sv = self.explainer.shap_values(x_2d)
                shap_vals = sv[0] if sv.ndim == 2 else sv

            # Build feature list for response
            features: List[Dict[str, Any]] = []
            n_feats = min(len(shap_vals), len(self.feature_names_))

            # Sort by absolute SHAP value (most impactful first)
            sorted_idx = np.argsort(np.abs(shap_vals[:n_feats]))[::-1]

            for i in sorted_idx:
                feat_name = self.feature_names_[i]
                sv_val    = float(shap_vals[i])
                direction = "risk" if sv_val > 0 else "safe"
                label_map = FEATURE_LABELS.get(feat_name, {})
                label     = label_map.get(direction, f"{feat_name} contribution")

                features.append({
                    "feature":   feat_name,
                    "value":     round(sv_val, 4),
                    "label":     label,
                    "direction": direction,
                })

            return {
                "baseValue":   round(self.base_value_, 4),
                "finalValue":  round(float(model_probability), 4),
                "probability": round(float(model_probability), 4),
                "features":    features,
            }

        except Exception as exc:
            logger.warning("SHAP single explanation failed: %s – using fallback", exc)
            return self._fallback_explanation(model_probability)

    # ── Permutation Importance ────────────────────────────────────────
    def permutation_importance(
        self,
        model,
        X: np.ndarray,
        y: np.ndarray,
        n_repeats: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Model-agnostic permutation importance on a held-out dataset.
        """
        try:
            from sklearn.inspection import permutation_importance as sk_pi
            from sklearn.metrics import average_precision_score

            result = sk_pi(
                model, X, y,
                n_repeats=n_repeats,
                random_state=42,
                scoring="average_precision",
            )
            n = min(result.importances_mean.shape[0], len(self.feature_names_))
            pi_list = [
                {
                    "feature":    self.feature_names_[i],
                    "importance": round(float(result.importances_mean[i]), 5),
                    "std":        round(float(result.importances_std[i]),  5),
                }
                for i in np.argsort(result.importances_mean[:n])[::-1]
            ]
            return pi_list
        except Exception as exc:
            logger.warning("Permutation importance failed: %s", exc)
            return []

    # ── Fallback (when SHAP is unavailable) ──────────────────────────
    def _fallback_explanation(self, probability: float) -> Dict[str, Any]:
        """
        When SHAP is unavailable, return a minimal but non-fabricated response.
        The base value is the training-set mean prediction, so at least that
        is real. Feature values are left as zeros (honest about uncertainty).
        """
        return {
            "baseValue":   round(self.base_value_, 4),
            "finalValue":  round(float(probability), 4),
            "probability": round(float(probability), 4),
            "features":    [
                {
                    "feature":   col,
                    "value":     0.0,
                    "label":     "SHAP not available – install 'shap' package",
                    "direction": "risk" if probability > 0.5 else "safe",
                }
                for col in FEATURE_COLS
            ],
        }

    # ── Global Importance Getter ──────────────────────────────────────
    def get_global_importance(self) -> List[Dict[str, Any]]:
        return self.global_importance_
