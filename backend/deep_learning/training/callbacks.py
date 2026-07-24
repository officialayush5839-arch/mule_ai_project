import logging
from typing import Any

logger = logging.getLogger(__name__)

class Callback:
    """Base callback interface."""
    def on_epoch_end(self, trainer: Any, epoch: int, val_loss: float):
        pass

class EarlyStopping(Callback):
    def __init__(self, patience: int = 5, min_delta: float = 0.0):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.counter = 0
        self.stop_training = False
        
    def on_epoch_end(self, trainer: Any, epoch: int, val_loss: float):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            logger.debug(f"EarlyStopping counter reset to 0.")
        else:
            self.counter += 1
            logger.debug(f"EarlyStopping counter: {self.counter} out of {self.patience}")
            if self.counter >= self.patience:
                self.stop_training = True

class ModelCheckpoint(Callback):
    def __init__(self, save_dir: str, save_best_only: bool = True):
        self.save_dir = save_dir
        self.save_best_only = save_best_only
        self.best_loss = float('inf')
        
    def on_epoch_end(self, trainer: Any, epoch: int, val_loss: float):
        if self.save_best_only:
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                trainer.model.save_checkpoint(f"{self.save_dir}/best_model.pt")
                logger.info(f"Saved new best model with val_loss: {val_loss:.4f}")
        else:
            trainer.model.save_checkpoint(f"{self.save_dir}/model_epoch_{epoch}.pt")
