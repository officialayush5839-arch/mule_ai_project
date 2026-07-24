import torch
from torch.utils.data import Dataset
import pandas as pd
from typing import Optional, Tuple
from backend.deep_learning.datasets.feature_schema import FeatureSchema
from backend.deep_learning.datasets.normalization import NumericalScaler
from backend.deep_learning.datasets.feature_encoder import CategoricalEncoder

class EnterpriseTabularDataset(Dataset):
    """
    Advanced tabular dataset handling both numerical tensors and categorical indices.
    """
    def __init__(
        self, 
        df: pd.DataFrame, 
        schema: FeatureSchema, 
        num_scaler: NumericalScaler, 
        cat_encoder: CategoricalEncoder,
        is_train: bool = False
    ):
        self.schema = schema
        
        # Fit or Transform Categoricals
        if is_train:
            self.x_cat = cat_encoder.fit_transform(df)
        else:
            self.x_cat = cat_encoder.transform(df)
            
        # Fit or Transform Numericals (Handle NaNs)
        x_num_raw = df[schema.numerical_features].fillna(0.0).values
        x_num_tensor = torch.tensor(x_num_raw, dtype=torch.float32)
        
        if is_train:
            self.x_num = num_scaler.fit_transform(x_num_tensor)
        else:
            self.x_num = num_scaler.transform(x_num_tensor)
            
        # Target
        if schema.target and schema.target in df.columns:
            self.y = torch.tensor(df[schema.target].values, dtype=torch.float32).unsqueeze(1)
        else:
            self.y = None

    def __len__(self) -> int:
        return len(self.x_num)

    def __getitem__(self, idx: int) -> Tuple[Tuple[torch.Tensor, torch.Tensor], Optional[torch.Tensor]]:
        x = (self.x_num[idx], self.x_cat[idx])
        y = self.y[idx] if self.y is not None else None
        return x, y
