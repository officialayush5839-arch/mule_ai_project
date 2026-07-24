import torch
import torch.nn as nn
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel
from backend.deep_learning.models.tabular.mlp.model import DeepMLP
from backend.deep_learning.models.temporal.lstm.model import TemporalLSTM

class TemporalFusion(EnterpriseBaseModel):
    """
    Fuses Static features (Profile) and Dynamic features (Transactions).
    Uses DeepMLP for static and TemporalLSTM for dynamic sequences.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TemporalFusion"
        
        # Split configurations
        static_config = config.get("static_config", {})
        dynamic_config = config.get("dynamic_config", {})
        
        # Base Encoders
        self.static_encoder = DeepMLP(static_config)
        self.dynamic_encoder = TemporalLSTM(dynamic_config)
        
        # Remove their classification heads to extract representations
        static_out_dim = static_config.get("hidden_dims", [128])[-1]
        dynamic_out_dim = dynamic_config.get("hidden_size", 256) * (2 if dynamic_config.get("bidirectional", True) else 1)
        
        self.static_encoder.network = self.static_encoder.network[:-1] # Remove head
        self.dynamic_encoder.head = nn.Identity() # Remove head
        
        fusion_dim = static_out_dim + dynamic_out_dim
        
        self.fusion_head = nn.Sequential(
            nn.Linear(fusion_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x: tuple) -> torch.Tensor:
        """
        x is a nested tuple: (static_features, dynamic_features)
        static_features: (x_num, x_cat)
        dynamic_features: (seq, mask)
        """
        static_features, dynamic_features = x
        
        static_rep = self.static_encoder(static_features)
        dynamic_rep = self.dynamic_encoder(dynamic_features)
        
        # Concatenate embeddings
        fused = torch.cat([static_rep, dynamic_rep], dim=1)
        
        return self.fusion_head(fused)
