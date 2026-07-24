import torch
from torch.utils.data import DataLoader, Dataset
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class TabularDataset(Dataset):
    """
    Standard PyTorch Dataset for Tabular features.
    """
    def __init__(self, features: torch.Tensor, labels: torch.Tensor):
        self.features = features
        self.labels = labels

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.labels[idx]

def create_dataloader(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = False
) -> DataLoader:
    """
    Factory function for enterprise dataloaders.
    """
    logger.debug(f"Creating DataLoader: batch_size={batch_size}, shuffle={shuffle}, workers={num_workers}")
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory
    )
