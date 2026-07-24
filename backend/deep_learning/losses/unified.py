import torch
import torch.nn as nn
import torch.nn.functional as F

class UnifiedLoss(nn.Module):
    """
    Unified loss manager for different task objectives.
    """
    def __init__(self, task_type: str = "classification"):
        super().__init__()
        self.task_type = task_type
        
        if task_type == "classification":
            self.criterion = nn.BCEWithLogitsLoss()
        elif task_type == "regression":
            self.criterion = nn.MSELoss()
        elif task_type == "reconstruction":
            self.criterion = nn.MSELoss()
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def forward(self, preds: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return self.criterion(preds, targets)

class SparsityLoss(nn.Module):
    """
    Custom Sparsity loss for TabNet (penalizes dense attention masks).
    """
    def __init__(self, lambda_sparse: float = 1e-3):
        super().__init__()
        self.lambda_sparse = lambda_sparse

    def forward(self, sparse_loss: torch.Tensor) -> torch.Tensor:
        return self.lambda_sparse * sparse_loss
