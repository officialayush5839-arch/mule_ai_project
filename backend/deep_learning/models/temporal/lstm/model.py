import torch
import torch.nn as nn
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class TemporalLSTM(EnterpriseBaseModel):
    """
    Multi-layer Bidirectional LSTM with Attention Pooling.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TemporalLSTM"
        
        self.input_dim = config.get("num_features", 10)
        self.hidden_size = config.get("hidden_size", 256)
        self.num_layers = config.get("layers", 3)
        self.bidirectional = config.get("bidirectional", True)
        self.dropout = config.get("dropout", 0.2)
        
        self.lstm = nn.LSTM(
            input_size=self.input_dim,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=True,
            dropout=self.dropout if self.num_layers > 1 else 0,
            bidirectional=self.bidirectional
        )
        
        lstm_out_dim = self.hidden_size * 2 if self.bidirectional else self.hidden_size
        
        # Self-Attention pooling over time
        self.attention = nn.Sequential(
            nn.Linear(lstm_out_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
            nn.Softmax(dim=1)
        )
        
        self.head = nn.Sequential(
            nn.Linear(lstm_out_dim, 128),
            nn.ReLU(),
            nn.Dropout(self.dropout),
            nn.Linear(128, 1)
        )

    def forward(self, x: tuple) -> torch.Tensor:
        seq, mask = x # seq: (Batch, SeqLen, Features), mask: (Batch, SeqLen)
        
        lstm_out, _ = self.lstm(seq)
        
        # Apply mask to attention
        attn_weights = self.attention(lstm_out) # (B, S, 1)
        attn_weights = attn_weights * mask.unsqueeze(-1)
        
        # Re-normalize weights after masking
        attn_weights = attn_weights / (attn_weights.sum(dim=1, keepdim=True) + 1e-8)
        
        # Context vector
        context = torch.sum(attn_weights * lstm_out, dim=1) # (B, OutDim)
        
        return self.head(context)
