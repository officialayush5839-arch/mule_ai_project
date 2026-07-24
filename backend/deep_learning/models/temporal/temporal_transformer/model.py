import torch
import torch.nn as nn
import math
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, SeqLen, EmbeddingDim)
        """
        return x + self.pe[:, :x.size(1), :]

class TemporalTransformer(EnterpriseBaseModel):
    """
    Multi-head Sequence Transformer with Positional Encodings.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TemporalTransformer"
        
        self.input_dim = config.get("num_features", 10)
        self.d_model = config.get("d_model", 128)
        self.n_heads = config.get("attention_heads", 8)
        self.n_layers = config.get("transformer_layers", 4)
        self.dropout = config.get("dropout", 0.1)
        
        # Project raw features to d_model
        self.feature_embedding = nn.Linear(self.input_dim, self.d_model)
        self.pos_encoder = PositionalEncoding(self.d_model)
        
        # [CLS] Token for sequence aggregation
        self.cls_token = nn.Parameter(torch.zeros(1, 1, self.d_model))
        nn.init.kaiming_uniform_(self.cls_token, a=math.sqrt(5))
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=self.n_heads,
            dim_feedforward=self.d_model * 4,
            dropout=self.dropout,
            activation="gelu",
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=self.n_layers)
        
        self.head = nn.Sequential(
            nn.LayerNorm(self.d_model),
            nn.Linear(self.d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x: tuple) -> torch.Tensor:
        seq, mask = x # seq: (Batch, SeqLen, Features), mask: (Batch, SeqLen)
        batch_size = seq.size(0)
        
        # Embed features and add positional encoding
        seq_emb = self.feature_embedding(seq)
        seq_emb = self.pos_encoder(seq_emb)
        
        # Expand CLS token
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        
        # Concat CLS token at the beginning
        seq_emb = torch.cat((cls_tokens, seq_emb), dim=1)
        
        # Adjust mask for CLS token (1 means unmasked/attend, 0 means masked/ignore)
        cls_mask = torch.ones((batch_size, 1), device=mask.device)
        full_mask = torch.cat((cls_mask, mask), dim=1)
        
        # nn.Transformer expects src_key_padding_mask where True means "ignore this position"
        key_padding_mask = (full_mask == 0)
        
        # Transformer pass
        out = self.transformer(seq_emb, src_key_padding_mask=key_padding_mask)
        
        # Extract [CLS]
        cls_out = out[:, 0, :]
        
        return self.head(cls_out)
