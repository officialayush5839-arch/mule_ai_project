import torch
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CheckpointManager:
    """
    Enterprise Checkpoint Manager for deep learning models.
    """
    def __init__(self, save_dir: str):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def save(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        metrics: Dict[str, float],
        config: Dict[str, Any],
        is_best: bool = False,
        filename: str = "checkpoint.pt"
    ):
        state = {
            "epoch": epoch,
            "state_dict": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "metrics": metrics,
            "config": config
        }
        
        path = self.save_dir / filename
        torch.save(state, path)
        logger.info(f"Saved checkpoint to {path}")
        
        if is_best:
            best_path = self.save_dir / "best_model.pt"
            torch.save(state, best_path)
            logger.info(f"Saved best model to {best_path}")

    @staticmethod
    def load(path: str, model: torch.nn.Module, optimizer: torch.optim.Optimizer = None, device: torch.device = torch.device('cpu')):
        logger.info(f"Loading checkpoint from {path}")
        checkpoint = torch.load(path, map_location=device)
        
        model.load_state_dict(checkpoint["state_dict"])
        if optimizer and "optimizer" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer"])
            
        return checkpoint.get("epoch", 0), checkpoint.get("metrics", {}), checkpoint.get("config", {})
