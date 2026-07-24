import torch
import torch.nn as nn
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class TabTransformer(EnterpriseBaseModel):
    """
    TabTransformer Architecture.
    Passes categorical features through Transformer encoder blocks.
    Numerical features are concatenated with contextualized embeddings via LayerNorm.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TabTransformer"
        
        self.num_dim = config.get("num_features", 0)
        self.cat_dims = config.get("cat_dims", [])
        
        self.d_token = config.get("embedding_dim", 32)
        n_heads = config.get("attention_heads", 8)
        n_layers = config.get("transformer_layers", 6)
        dropout = config.get("dropout", 0.1)
        
        # Categorical Embeddings
        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(cardinality, self.d_token) 
            for cardinality, _ in self.cat_dims
        ])
        
        # Transformer for Categoricals
        if self.cat_dims:
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=self.d_token,
                nhead=n_heads,
                dim_feedforward=self.d_token * 4,
                dropout=dropout,
                activation="relu",
                batch_first=True
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
            
        # Numerical processing
        self.num_norm = nn.LayerNorm(self.num_dim) if self.num_dim > 0 else None
        
        # MLP Head
        mlp_input_dim = (len(self.cat_dims) * self.d_token) + self.num_dim
        self.mlp = nn.Sequential(
            nn.Linear(mlp_input_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x: tuple) -> torch.Tensor:
        x_num, x_cat = x
        
        # Contextualize Categoricals
        if self.cat_dims and x_cat is not None:
            cat_tokens = [emb(x_cat[:, i]).unsqueeze(1) for i, emb in enumerate(self.cat_embeddings)]
            x_cat_seq = torch.cat(cat_tokens, dim=1) # (batch, num_cats, d_token)
            x_cat_context = self.transformer(x_cat_seq)
            # Flatten contextualized categorical embeddings
            x_cat_flat = x_cat_context.view(x_cat_context.size(0), -1)
        else:
            x_cat_flat = torch.empty((x_num.size(0), 0), device=x_num.device)
            
        # Normalize Numericals
        if self.num_dim > 0 and x_num is not None:
            x_num_norm = self.num_norm(x_num)
        else:
            x_num_norm = torch.empty((x_cat.size(0), 0), device=x_cat.device)
            
        # Feature Fusion
        x_fused = torch.cat([x_cat_flat, x_num_norm], dim=1)
        
        # MLP Head
        return self.mlp(x_fused)
