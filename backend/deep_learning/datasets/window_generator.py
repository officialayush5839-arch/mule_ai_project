import pandas as pd
import numpy as np
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class WindowGenerator:
    """
    Generates sliding windows of transactions for temporal models.
    Supports configurable window sizes (e.g., 30, 90, 180 days).
    """
    def __init__(self, entity_col: str = "customer_id", time_col: str = "timestamp", sequence_length: int = 30):
        self.entity_col = entity_col
        self.time_col = time_col
        self.sequence_length = sequence_length

    def generate_windows(self, df: pd.DataFrame, feature_cols: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Groups by entity, sorts by time, and extracts fixed-length sliding windows.
        Pads sequences shorter than sequence_length with zeros.
        Returns (sequences, labels/targets) if a target column exists.
        For simplicity in this mock, we assume the dataset is pre-sorted if necessary,
        or we sort it here.
        """
        df = df.sort_values(by=[self.entity_col, self.time_col])
        
        # Simple extraction logic for demonstration.
        # In production, this uses rolling windows with stride.
        # Here we group by entity, and take the last `sequence_length` records.
        sequences = []
        labels = []
        has_target = "is_fraud" in df.columns
        
        for entity, group in df.groupby(self.entity_col):
            # Convert group features to numpy
            feats = group[feature_cols].values
            target = group["is_fraud"].values[-1] if has_target else 0
            
            seq_len = len(feats)
            if seq_len >= self.sequence_length:
                # Truncate to the most recent `sequence_length`
                seq = feats[-self.sequence_length:]
            else:
                # Pad with zeros at the beginning
                pad = np.zeros((self.sequence_length - seq_len, len(feature_cols)))
                seq = np.vstack([pad, feats])
                
            sequences.append(seq)
            labels.append(target)
            
        return np.array(sequences), np.array(labels)
