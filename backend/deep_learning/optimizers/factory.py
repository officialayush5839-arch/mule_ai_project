import torch
from typing import Dict, Any

class OptimizerFactory:
    @staticmethod
    def create(model: torch.nn.Module, config: Dict[str, Any]) -> torch.optim.Optimizer:
        opt_type = config.get("optimizer", "adamw").lower()
        lr = config.get("learning_rate", 1e-3)
        weight_decay = config.get("weight_decay", 1e-4)
        
        if opt_type == "adamw":
            return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif opt_type == "adam":
            return torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif opt_type == "sgd":
            momentum = config.get("momentum", 0.9)
            return torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unsupported optimizer: {opt_type}")
