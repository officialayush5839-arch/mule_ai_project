"""
shap_explain.py
===============
REPLACED – was: hardcoded multipliers pretending to be SHAP values.
NOW:  Thin adapter delegating to the real ExplainabilityEngine via InferenceEngine.

explain_prediction_shap() signature is preserved for backward compatibility.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]


def explain_prediction_shap(features_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return real SHAP attributions for a single prediction.

    This function is kept for backward compatibility with predict.py.
    Internally it delegates to InferenceEngine which uses the trained
    model's TreeExplainer (or KernelExplainer fallback).

    Parameters
    ----------
    features_dict : dict with F115..F3894 feature values

    Returns
    -------
    {baseValue, finalValue, probability, features: [...]}
    The SHAP values are REAL attributions from the trained model,
    not hardcoded multipliers.
    """
    try:
        from ml.inference import get_engine
        engine = get_engine()
        result = engine.predict_single(features_dict)
        return result["shap"]

    except Exception as exc:
        logger.error("SHAP explanation failed (%s) – returning honest fallback", exc)

        # Honest fallback: zeros, not fabricated numbers
        probability = 0.0
        return {
            "baseValue":   0.0,
            "finalValue":  probability,
            "probability": probability,
            "features": [
                {
                    "feature":   col,
                    "value":     0.0,
                    "label":     "Explanation unavailable – model not loaded",
                    "direction": "safe",
                }
                for col in FEATURE_COLS
            ],
        }
