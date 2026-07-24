import torch
import logging
from typing import Optional, Dict, Any, List
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)

class EnterpriseTrainer:
    """
    Robust PyTorch training engine supporting Mixed Precision (AMP), Gradient Clipping, and Callbacks.
    """
    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        criterion: torch.nn.Module,
        device: torch.device,
        scaler: Optional[torch.amp.GradScaler] = None,
        callbacks: Optional[List[Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.scaler = scaler if scaler else torch.amp.GradScaler(enabled=False)
        self.callbacks = callbacks or []
        self.config = config or {}
        
        self.current_epoch = 0
        self.best_val_loss = float('inf')

    def train_epoch(self, train_loader: DataLoader) -> float:
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, batch in enumerate(train_loader):
            # Assumes dataloader returns (features, labels)
            features, labels = batch[0].to(self.device), batch[1].to(self.device)
            
            self.optimizer.zero_grad(set_to_none=True)
            
            # AMP Context
            with torch.amp.autocast(device_type=self.device.type, enabled=self.scaler.is_enabled()):
                outputs = self.model(features)
                loss = self.criterion(outputs, labels)
                
            self.scaler.scale(loss).backward()
            
            # Gradient clipping support via config
            if "grad_clip_val" in self.config:
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config["grad_clip_val"])
                
            self.scaler.step(self.optimizer)
            self.scaler.update()
            
            total_loss += loss.item()
            
        return total_loss / len(train_loader)

    def validate_epoch(self, val_loader: DataLoader) -> float:
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for batch in val_loader:
                features, labels = batch[0].to(self.device), batch[1].to(self.device)
                
                with torch.amp.autocast(device_type=self.device.type, enabled=self.scaler.is_enabled()):
                    outputs = self.model(features)
                    loss = self.criterion(outputs, labels)
                    
                total_loss += loss.item()
                
        return total_loss / len(val_loader)

    def fit(self, train_loader: DataLoader, val_loader: DataLoader, epochs: int):
        logger.info(f"Starting training for {epochs} epochs on {self.device}")
        
        for epoch in range(epochs):
            self.current_epoch = epoch
            
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate_epoch(val_loader)
            
            logger.info(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
            
            # Trigger Callbacks
            stop_training = False
            for cb in self.callbacks:
                cb.on_epoch_end(self, epoch, val_loss)
                if getattr(cb, "stop_training", False):
                    stop_training = True
                    
            if stop_training:
                logger.info(f"Early stopping triggered at epoch {epoch+1}")
                break
