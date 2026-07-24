"""
risk_scorer.py
==============
REPLACED – was: hardcoded weights (40/30/20/10) and fixed thresholds.
NOW:  Thin adapter that delegates to the InferenceEngine.

compute_unified_risk_score() signature is preserved for backward compatibility.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def compute_unified_risk_score(
    ensemble_prob: float,
    anomaly_score: float,
    behavioral_deviation: float,
    network_risk: float,
    velocity_ratio: float,
    dormancy_activation: bool,
) -> Dict[str, Any]:
    """
    Compute a unified risk score using the trained inference engine.

    This function is kept for backward compatibility.
    Internally it delegates to InferenceEngine.predict_single() which
    uses the best trained model rather than hardcoded arithmetic.

    All parameters are passed as raw feature values mapped to the
    canonical feature schema:
      ensemble_prob       → F1692  (mule pattern score)
      anomaly_score       → F3894  (anomaly isolation index)
      behavioral_deviation→ F527   (velocity / transaction frequency)
      network_risk        → F321   (source concentration)
    """
    try:
        from ml.inference import get_engine
        engine = get_engine()

        features = {
            "F1692": float(ensemble_prob),
            "F3894": float(anomaly_score),
            "F527":  float(behavioral_deviation),
            "F321":  float(network_risk),
            # Reconstruct velocity and dormancy back to F115/F670
            "F115":  float(min(velocity_ratio / 4.0, 1.0)),  # reverse scale_pos_weight * 3.8
            "F670":  0.1 if dormancy_activation else 0.6,
            "F3043": float((ensemble_prob + anomaly_score) / 2.0),
        }

        result = engine.predict_single(features)
        return result["verdict"]

    except Exception as exc:
        logger.error("InferenceEngine unavailable (%s) – returning safe default", exc)
        return {
            "finalScore":     0.0,
            "baseScore":      0.0,
            "classification": "UNSCORED",
            "confidence":     0.0,
            "penalties":      {"velocitySpike": 0.0, "dormancyActivation": 0.0},
            "components":     {
                "lgbmContribution":       0.0,
                "anomalyContribution":    0.0,
                "behavioralContribution": 0.0,
                "networkContribution":    0.0,
            },
        }
