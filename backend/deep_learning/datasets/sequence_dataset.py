import torch
from torch.utils.data import Dataset
import numpy as np

class EnterpriseSequenceDataset(Dataset):
    """
    Dataset wrapper for 3D Sequence Tensors (Batch, Sequence, Features).
    Generates attention masks for padded timestamps.
    """
    def __init__(self, sequences: np.ndarray, labels: np.ndarray):
        """
        sequences: (N, seq_len, features)
        labels: (N,)
        """
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int):
        seq = self.sequences[idx]
        label = self.labels[idx]
        
        # Mask where the sequence is entirely zero (padded timestamps)
        # 1 means unmasked, 0 means masked
        mask = (seq.abs().sum(dim=-1) > 0).float()
        
        # Return tuple (seq, mask) for x
        return (seq, mask), label
