import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
from torch_geometric.nn import GATConv
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class GAT(EnterpriseBaseModel):
    """
    Graph Attention Network (multi-head attention).
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "GAT"
        
        self.in_channels = config.get("num_features", 128)
        self.hidden_channels = config.get("hidden_channels", [128, 64])
        self.heads = config.get("heads", 4)
        self.dropout = config.get("dropout", 0.2)
        
        self.convs = nn.ModuleList()
        
        dims = [self.in_channels] + self.hidden_channels
        for i in range(len(dims) - 1):
            is_last = i == (len(dims) - 2)
            heads = 1 if is_last else self.heads
            concat = not is_last # Average heads on last layer instead of concatenating
            
            in_dim = dims[i] * (self.heads if i > 0 else 1)
            self.convs.append(GATConv(in_dim, dims[i+1], heads=heads, concat=concat, dropout=self.dropout))
            
        self.head = nn.Linear(dims[-1], 1)

    def forward(self, data_tuple: Tuple[torch.Tensor, torch.Tensor], return_attention_weights=False) -> torch.Tensor:
        x, edge_index = data_tuple
        
        attns = []
        for i, conv in enumerate(self.convs):
            if return_attention_weights:
                x, attn = conv(x, edge_index, return_attention_weights=True)
                attns.append(attn)
            else:
                x = conv(x, edge_index)
                
            if i < len(self.convs) - 1:
                x = nn.ELU()(x)
                
        pred = self.head(x)
        if return_attention_weights:
            return pred, attns
        return pred
