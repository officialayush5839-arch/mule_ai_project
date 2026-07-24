import torch
import torch.nn as nn
from typing import Dict, Any, List
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class DeepMLP(EnterpriseBaseModel):
    """
    Standard Deep Neural Network with Xavier initialization, 
    configurable activations (ReLU/GELU/SiLU), Batch Normalization, and Dropout.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "DeepMLP"
        
        # Dimensions
        self.num_dim = config.get("num_features", 0)
        self.cat_dims = config.get("cat_dims", []) # List of (cardinality, embedding_dim)
        
        # Build Embeddings
        self.embeddings = nn.ModuleList([
            nn.Embedding(cardinality, emb_dim) 
            for cardinality, emb_dim in self.cat_dims
        ])
        
        total_emb_dim = sum(emb_dim for _, emb_dim in self.cat_dims)
        input_dim = self.num_dim + total_emb_dim
        
        # Build MLP Layers
        hidden_dims = config.get("hidden_dims", [512, 256, 128])
        dropout_rate = config.get("dropout", 0.2)
        activation_type = config.get("activation", "relu").lower()
        
        if activation_type == "relu":
            activation = nn.ReLU()
        elif activation_type == "gelu":
            activation = nn.GELU()
        elif activation_type == "silu":
            activation = nn.SiLU()
        else:
            activation = nn.ReLU()
            
        layers = []
        in_dim = input_dim
        
        for out_dim in hidden_dims:
            linear = nn.Linear(in_dim, out_dim)
            # Xavier Initialization
            nn.init.xavier_uniform_(linear.weight)
            nn.init.zeros_(linear.bias)
            
            layers.extend([
                linear,
                nn.BatchNorm1d(out_dim),
                activation,
                nn.Dropout(dropout_rate)
            ])
            in_dim = out_dim
            
        # Prediction Head
        head = nn.Linear(in_dim, 1)
        nn.init.xavier_uniform_(head.weight)
        nn.init.zeros_(head.bias)
        layers.append(head)
        
        self.network = nn.Sequential(*layers)

    def forward(self, x: tuple) -> torch.Tensor:
        """
        x is a tuple of (x_num, x_cat)
        """
        x_num, x_cat = x
        
        emb_outputs = []
        if self.embeddings:
            for i, emb_layer in enumerate(self.embeddings):
                emb_outputs.append(emb_layer(x_cat[:, i]))
                
        if emb_outputs:
            x_cat_emb = torch.cat(emb_outputs, dim=1)
            x_fused = torch.cat([x_num, x_cat_emb], dim=1)
        else:
            x_fused = x_num
            
        return self.network(x_fused)
