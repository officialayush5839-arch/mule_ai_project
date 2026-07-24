import torch
import torch.nn as nn
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class TemporalGRU(EnterpriseBaseModel):
    """
    Stacked GRU with Attention for faster sequence inference.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TemporalGRU"
        
        self.input_dim = config.get("num_features", 10)
        self.hidden_size = config.get("hidden_size", 256)
        self.num_layers = config.get("layers", 3)
        self.dropout = config.get("dropout", 0.2)
        
        self.gru = nn.GRU(
            input_size=self.input_dim,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=True,
            dropout=self.dropout if self.num_layers > 1 else 0
        )
        
        # Self-Attention pooling over time
        self.attention = nn.Sequential(
            nn.Linear(self.hidden_size, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
            nn.Softmax(dim=1)
        )
        
        self.head = nn.Sequential(
            nn.Linear(self.hidden_size, 128),
            nn.ReLU(),
            nn.Dropout(self.dropout),
            nn.Linear(128, 1)
        )

    def forward(self, x: tuple) -> torch.Tensor:
        seq, mask = x
        
        gru_out, _ = self.gru(seq)
        
        attn_weights = self.attention(gru_out)
        attn_weights = attn_weights * mask.unsqueeze(-1)
        attn_weights = attn_weights / (attn_weights.sum(dim=1, keepdim=True) + 1e-8)
        
        context = torch.sum(attn_weights * gru_out, dim=1)
        
        return self.head(context)
