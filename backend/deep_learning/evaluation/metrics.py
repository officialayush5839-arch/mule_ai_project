import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_score, recall_score, accuracy_score, brier_score_loss
from typing import Dict

class ClassificationMetrics:
    @staticmethod
    def compute(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
        y_pred = (y_prob >= threshold).astype(int)
        
        return {
            "ROC-AUC": float(roc_auc_score(y_true, y_prob)),
            "PR-AUC": float(average_precision_score(y_true, y_prob)),
            "F1": float(f1_score(y_true, y_pred)),
            "Precision": float(precision_score(y_true, y_pred)),
            "Recall": float(recall_score(y_true, y_pred)),
            "Accuracy": float(accuracy_score(y_true, y_pred)),
            "Calibration Error (Brier)": float(brier_score_loss(y_true, y_prob))
        }

class ReconstructionMetrics:
    @staticmethod
    def compute(x_true: np.ndarray, x_pred: np.ndarray) -> Dict[str, float]:
        mse = np.mean((x_true - x_pred) ** 2)
        mae = np.mean(np.abs(x_true - x_pred))
        
        # 95th percentile error for anomaly detection thresholding
        errors = np.sum((x_true - x_pred) ** 2, axis=1)
        p95 = np.percentile(errors, 95)
        
        return {
            "MSE": float(mse),
            "MAE": float(mae),
            "95th Percentile Error": float(p95)
        }
