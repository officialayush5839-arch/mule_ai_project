import torch
import torch.nn as nn
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class NumericalFeatureTokenizer(nn.Module):
    """
    Transforms continuous numerical features into dense token embeddings.
    Allows Transformers to process numbers effectively.
    """
    def __init__(self, num_features: int, embedding_dim: int):
        super().__init__()
        # Learnable weights for numerical features to project them to embedding_dim
        self.weight = nn.Parameter(torch.Tensor(num_features, embedding_dim))
        self.bias = nn.Parameter(torch.Tensor(num_features, embedding_dim))
        nn.init.kaiming_uniform_(self.weight, a=torch.math.sqrt(5))
        nn.init.zeros_(self.bias)

    def forward(self, x_num: torch.Tensor) -> torch.Tensor:
        # x_num shape: (batch_size, num_features)
        # Output shape: (batch_size, num_features, embedding_dim)
        x_num = x_num.unsqueeze(-1)
        return x_num * self.weight.unsqueeze(0) + self.bias.unsqueeze(0)


class FTTransformer(EnterpriseBaseModel):
    """
    Feature Tokenizer + Transformer.
    Embeds both categorical and numerical features into a unified sequence.
    Appends a [CLS] token and applies Transformer Encoder layers.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "FTTransformer"
        
        self.num_dim = config.get("num_features", 0)
        self.cat_dims = config.get("cat_dims", [])
        
        # Hyperparameters
        self.d_token = config.get("embedding_dim", 128)
        n_heads = config.get("attention_heads", 8)
        n_layers = config.get("transformer_layers", 6)
        dropout = config.get("dropout", 0.2)
        
        # Tokenizers
        if self.num_dim > 0:
            self.num_tokenizer = NumericalFeatureTokenizer(self.num_dim, self.d_token)
            
        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(cardinality, self.d_token) 
            for cardinality, _ in self.cat_dims
        ])
        
        # [CLS] Token
        self.cls_token = nn.Parameter(torch.zeros(1, 1, self.d_token))
        nn.init.kaiming_uniform_(self.cls_token, a=torch.math.sqrt(5))
        
        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_token,
            nhead=n_heads,
            dim_feedforward=self.d_token * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # Prediction Head
        self.head = nn.Sequential(
            nn.LayerNorm(self.d_token),
            nn.Linear(self.d_token, self.d_token // 2),
            nn.ReLU(),
            nn.Linear(self.d_token // 2, 1)
        )

    def forward(self, x: tuple) -> torch.Tensor:
        x_num, x_cat = x
        batch_size = x_num.size(0) if x_num is not None else x_cat.size(0)
        
        tokens = []
        
        # Append [CLS]
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        tokens.append(cls_tokens)
        
        # Tokenize Categorical
        if self.cat_embeddings and x_cat is not None:
            cat_tokens = [emb(x_cat[:, i]).unsqueeze(1) for i, emb in enumerate(self.cat_embeddings)]
            tokens.extend(cat_tokens)
            
        # Tokenize Numerical
        if self.num_dim > 0 and x_num is not None:
            num_tokens = self.num_tokenizer(x_num)
            tokens.append(num_tokens)
            
        # Concatenate Sequence
        x_seq = torch.cat(tokens, dim=1) # Shape: (batch, seq_len, d_token)
        
        # Transformer Pass
        encoded = self.transformer(x_seq)
        
        # Extract [CLS] token representation (index 0)
        cls_representation = encoded[:, 0, :]
        
        return self.head(cls_representation)
