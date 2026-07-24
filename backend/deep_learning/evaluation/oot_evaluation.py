import numpy as np
from typing import Dict, List
import logging
from backend.deep_learning.evaluation.metrics import ClassificationMetrics

logger = logging.getLogger(__name__)

class OutOfTimeEvaluation:
    """
    Evaluates Temporal Models across time bounds to measure drift and degradation.
    """
    @staticmethod
    def evaluate_drift(
        y_true_val: np.ndarray, y_prob_val: np.ndarray,
        y_true_oot: np.ndarray, y_prob_oot: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculates performance degradation between Validation (In-Time) and Test (Out-Of-Time).
        """
        val_metrics = ClassificationMetrics.compute(y_true_val, y_prob_val)
        oot_metrics = ClassificationMetrics.compute(y_true_oot, y_prob_oot)
        
        degradation = {}
        for metric, val in val_metrics.items():
            if metric in oot_metrics:
                drop = val - oot_metrics[metric]
                degradation[f"{metric}_Degradation"] = drop
                
        logger.info(f"OOT Degradation: AUC Drop: {degradation.get('ROC-AUC_Degradation', 0):.4f}")
        
        return {
            "In_Time_Metrics": val_metrics,
            "Out_Of_Time_Metrics": oot_metrics,
            "Degradation": degradation
        }
