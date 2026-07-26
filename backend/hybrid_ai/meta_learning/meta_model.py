import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict, List

class MetaLearner:
    """
    Trains a meta-model (Stacking) over the base models to learn optimal decision boundaries.
    """
    def __init__(self):
        self.model = LogisticRegression()
        self.is_trained = False
        self.model_features = []

    def fit(self, base_predictions: np.ndarray, y_true: np.ndarray, model_names: List[str]):
        """
        base_predictions: (num_samples, num_base_models)
        """
        self.model.fit(base_predictions, y_true)
        self.model_features = model_names
        self.is_trained = True

    def predict_proba(self, base_predictions: Dict[str, float]) -> float:
        """
        Takes a single row of base predictions and outputs the meta-probability.
        """
        if not self.is_trained:
            # Fallback to simple average if untrained
            return sum(base_predictions.values()) / max(1, len(base_predictions))
            
        # Ensure ordered correctly
        x = np.array([[base_predictions.get(m, 0.5) for m in self.model_features]])
        return self.model.predict_proba(x)[0][1]
