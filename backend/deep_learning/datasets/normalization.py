import torch
import numpy as np
import logging

logger = logging.getLogger(__name__)

class NumericalScaler:
    """
    Handles numerical feature scaling. Fits on training data and transforms validation/test.
    Supports StandardScaler, MinMaxScaler, and RobustScaler logic.
    """
    def __init__(self, method: str = "standard"):
        self.method = method.lower()
        self.fitted = False
        self.params = {}
        
    def fit(self, X: torch.Tensor):
        if X.dim() != 2:
            raise ValueError("X must be a 2D tensor (batch_size, num_features)")
            
        if self.method == "standard":
            self.params["mean"] = X.mean(dim=0)
            self.params["std"] = X.std(dim=0, unbiased=False)
            self.params["std"][self.params["std"] == 0] = 1e-6 # prevent div by zero
        elif self.method == "minmax":
            self.params["min"] = X.min(dim=0)[0]
            self.params["max"] = X.max(dim=0)[0]
            self.params["range"] = self.params["max"] - self.params["min"]
            self.params["range"][self.params["range"] == 0] = 1e-6
        elif self.method == "robust":
            # Quantiles calculation (25th and 75th percentiles)
            q25 = torch.quantile(X, 0.25, dim=0)
            q75 = torch.quantile(X, 0.75, dim=0)
            self.params["median"] = torch.median(X, dim=0).values
            self.params["iqr"] = q75 - q25
            self.params["iqr"][self.params["iqr"] == 0] = 1e-6
        else:
            raise ValueError(f"Unknown scaling method: {self.method}")
            
        self.fitted = True
        logger.info(f"Fitted NumericalScaler using '{self.method}' strategy.")
        
    def transform(self, X: torch.Tensor) -> torch.Tensor:
        if not self.fitted:
            raise RuntimeError("Scaler must be fitted before calling transform()")
            
        if self.method == "standard":
            return (X - self.params["mean"]) / self.params["std"]
        elif self.method == "minmax":
            return (X - self.params["min"]) / self.params["range"]
        elif self.method == "robust":
            return (X - self.params["median"]) / self.params["iqr"]
            
    def fit_transform(self, X: torch.Tensor) -> torch.Tensor:
        self.fit(X)
        return self.transform(X)
