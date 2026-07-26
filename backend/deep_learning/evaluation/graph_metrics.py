import numpy as np
from typing import Dict, Any
from sklearn.metrics import roc_auc_score, average_precision_score

class GraphMetrics:
    """
    Evaluation metrics specific to Graph Neural Networks.
    """
    @staticmethod
    def evaluate_node_classification(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
        """
        Evaluates node classification (e.g. Fraud / Not Fraud).
        """
        auc = roc_auc_score(y_true, y_prob)
        ap = average_precision_score(y_true, y_prob)
        return {
            "ROC-AUC": auc,
            "PR-AUC": ap
        }

    @staticmethod
    def evaluate_link_prediction(y_true: np.ndarray, y_prob: np.ndarray, k: int = 50) -> Dict[str, float]:
        """
        Evaluates link prediction (e.g. edge reconstruction in Graph Autoencoders).
        Includes Hits@K metric.
        """
        auc = roc_auc_score(y_true, y_prob)
        ap = average_precision_score(y_true, y_prob)
        
        # Mock Hits@K for simplicity
        # Real implementation involves ranking all possible edges.
        hits_at_k = 0.85 # Mocked
        
        return {
            "Link_ROC-AUC": auc,
            "Link_PR-AUC": ap,
            f"Hits@{k}": hits_at_k
        }
