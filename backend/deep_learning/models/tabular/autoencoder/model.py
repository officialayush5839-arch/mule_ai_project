import torch
import torch.nn as nn
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class TabularAutoencoder(EnterpriseBaseModel):
    """
    Unsupervised Representation Learning for anomaly detection and latent embeddings.
    Only reconstructs numerical features for simplicity, or concatenated embeddings.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TabularAutoencoder"
        
        # Dimensions
        self.num_dim = config.get("num_features", 0)
        self.cat_dims = config.get("cat_dims", [])
        
        self.embeddings = nn.ModuleList([
            nn.Embedding(cardinality, emb_dim) 
            for cardinality, emb_dim in self.cat_dims
        ])
        
        total_emb_dim = sum(emb_dim for _, emb_dim in self.cat_dims)
        self.input_dim = self.num_dim + total_emb_dim
        self.latent_dim = config.get("latent_dim", 64)
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(self.input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, self.latent_dim)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(self.latent_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, self.input_dim)
        )

    def encode(self, x_num: torch.Tensor, x_cat: torch.Tensor) -> torch.Tensor:
        emb_outputs = []
        if self.embeddings:
            for i, emb_layer in enumerate(self.embeddings):
                emb_outputs.append(emb_layer(x_cat[:, i]))
                
        if emb_outputs:
            x_cat_emb = torch.cat(emb_outputs, dim=1)
            x_fused = torch.cat([x_num, x_cat_emb], dim=1)
        else:
            x_fused = x_num
            
        return self.encoder(x_fused), x_fused

    def forward(self, x: tuple) -> torch.Tensor:
        """
        Returns the reconstructed fused features.
        Target for MSE loss should be the `x_fused` tensor returned during encode.
        """
        x_num, x_cat = x
        latent, _ = self.encode(x_num, x_cat)
        reconstructed = self.decoder(latent)
        return reconstructed
