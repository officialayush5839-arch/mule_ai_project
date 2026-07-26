import numpy as np
from typing import Dict

class UncertaintyEstimator:
    """
    Measures ensemble disagreement and predictive uncertainty.
    """
    @staticmethod
    def calculate_variance(predictions: Dict[str, float]) -> float:
        """
        Variance across ensemble predictions. High variance = high disagreement (OOD).
        """
        if len(predictions) < 2:
            return 0.0
        return np.var(list(predictions.values()))

    @staticmethod
    def calculate_entropy(probability: float) -> float:
        """
        Shannon entropy of the final fused probability.
        Maximal at p=0.5 (highest uncertainty).
        """
        if probability <= 0 or probability >= 1:
            return 0.0
        return -(probability * np.log2(probability) + (1 - probability) * np.log2(1 - probability))
