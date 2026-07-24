import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EnterpriseBaseModel(nn.Module):
    """
    Abstract Enterprise Deep Learning Base Model.
    All future PyTorch models (FT-Transformer, GNNs) must inherit from this.
    No specific algorithm or business logic should exist here.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.model_name = self.config.get("model_name", "EnterpriseBaseModel")
        
    def forward(self, x: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        Pure PyTorch forward pass. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement forward()")

    def predict(self, x: Any, device: torch.device) -> torch.Tensor:
        """
        Inference wrapper that handles evaluation mode and detached gradients.
        """
        self.eval()
        self.to(device)
        with torch.no_grad():
            if isinstance(x, tuple):
                x = tuple(t.to(device) if t is not None else None for t in x)
            else:
                x = x.to(device)
            return self.forward(x)

    def predict_proba(self, x: Any, device: torch.device) -> torch.Tensor:
        """
        Returns probabilities assuming binary classification.
        Applies sigmoid to logits.
        """
        logits = self.predict(x, device)
        return torch.sigmoid(logits)

    def save_checkpoint(self, path: str):
        """
        Serializes model weights and configuration.
        """
        checkpoint = {
            "state_dict": self.state_dict(),
            "config": self.config
        }
        torch.save(checkpoint, path)
        logger.info(f"Model checkpoint saved to {path}")

    @classmethod
    def load_checkpoint(cls, path: str, device: torch.device) -> 'EnterpriseBaseModel':
        """
        Loads a checkpoint into the model instance.
        """
        checkpoint = torch.load(path, map_location=device)
        config = checkpoint.get("config", {})
        
        # Instantiate the subclass dynamically
        model = cls(config)
        model.load_state_dict(checkpoint["state_dict"])
        model.to(device)
        model.eval()
        logger.info(f"Model checkpoint loaded from {path}")
        return model

    def summary(self):
        """
        Returns basic architecture and parameter counts.
        """
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        logger.info(f"Model Summary: {self.model_name}")
        logger.info(f"Total Parameters: {total_params:,}")
        logger.info(f"Trainable Parameters: {trainable_params:,}")
        return {"total": total_params, "trainable": trainable_params}
