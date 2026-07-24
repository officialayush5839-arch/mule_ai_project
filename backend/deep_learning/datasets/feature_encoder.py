import torch
import logging
from typing import Dict, List, Any
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class CategoricalEncoder:
    """
    Learns vocabularies from categorical columns and transforms strings to integer indices.
    Reserves index 0 for <UNK>/Missing values.
    """
    def __init__(self, cat_features: List[str]):
        self.cat_features = cat_features
        self.vocabularies: Dict[str, Dict[str, int]] = {feat: {"<UNK>": 0} for feat in cat_features}
        self.cardinalities: Dict[str, int] = {}
        self.fitted = False

    def fit(self, df: pd.DataFrame):
        for feat in self.cat_features:
            if feat not in df.columns:
                raise ValueError(f"Categorical feature '{feat}' not found in dataframe.")
                
            unique_vals = df[feat].dropna().unique()
            for idx, val in enumerate(unique_vals, start=1):
                self.vocabularies[feat][str(val)] = idx
                
            self.cardinalities[feat] = len(self.vocabularies[feat])
            
        self.fitted = True
        logger.info("Categorical vocabularies built.")

    def transform(self, df: pd.DataFrame) -> torch.Tensor:
        if not self.fitted:
            raise RuntimeError("CategoricalEncoder must be fitted before transform.")
            
        encoded = np.zeros((len(df), len(self.cat_features)), dtype=np.int64)
        for i, feat in enumerate(self.cat_features):
            vocab = self.vocabularies[feat]
            # Map strings to int, defaulting to 0 (<UNK>)
            encoded[:, i] = df[feat].astype(str).map(vocab).fillna(0).astype(np.int64)
            
        return torch.tensor(encoded, dtype=torch.long)

    def fit_transform(self, df: pd.DataFrame) -> torch.Tensor:
        self.fit(df)
        return self.transform(df)

    def get_embedding_dims(self, max_dim: int = 64) -> List[int]:
        """
        Rule of thumb for embedding dimension: min(50, cardinality // 2)
        """
        dims = []
        for feat in self.cat_features:
            cardinality = self.cardinalities[feat]
            dim = min(max_dim, max(4, int(cardinality ** 0.25) * 10)) # Heuristic
            dims.append((cardinality, dim))
        return dims
