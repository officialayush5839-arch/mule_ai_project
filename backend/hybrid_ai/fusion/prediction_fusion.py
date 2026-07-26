import numpy as np
from typing import Dict

class PredictionFusion:
    """
    Implements multiple statistical fusion strategies for ensemble predictions.
    """
    @staticmethod
    def soft_voting(predictions: Dict[str, float]) -> float:
        """
        Simple average of probabilities.
        """
        if not predictions:
            return 0.0
        return sum(predictions.values()) / len(predictions)

    @staticmethod
    def hard_voting(predictions: Dict[str, float], threshold: float = 0.5) -> float:
        """
        Majority vote.
        """
        if not predictions:
            return 0.0
        votes = sum(1 for p in predictions.values() if p >= threshold)
        return 1.0 if votes > (len(predictions) / 2) else 0.0

    @staticmethod
    def weighted_average(predictions: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Averages probabilities based on predefined model weights.
        """
        if not predictions:
            return 0.0
        total_weight = sum(weights.get(m, 1.0) for m in predictions.keys())
        weighted_sum = sum(p * weights.get(m, 1.0) for m, p in predictions.items())
        return weighted_sum / total_weight if total_weight > 0 else 0.0
