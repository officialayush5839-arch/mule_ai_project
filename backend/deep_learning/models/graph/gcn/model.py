import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
from torch_geometric.nn import GCNConv
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class GCN(EnterpriseBaseModel):
    """
    Graph Convolutional Network with spectral normalization.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "GCN"
        
        self.in_channels = config.get("num_features", 128)
        self.hidden_channels = config.get("hidden_channels", [256, 128])
        self.dropout = config.get("dropout", 0.2)
        
        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        
        dims = [self.in_channels] + self.hidden_channels
        for i in range(len(dims) - 1):
            self.convs.append(GCNConv(dims[i], dims[i+1]))
            self.bns.append(nn.BatchNorm1d(dims[i+1]))
            
        self.dropout_layer = nn.Dropout(self.dropout)
        self.head = nn.Linear(dims[-1], 1)

    def forward(self, data_tuple: Tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
        x, edge_index = data_tuple
        
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            x = self.bns[i](x)
            if i < len(self.convs) - 1:
                x = x.relu()
                x = self.dropout_layer(x)
                
        return self.head(x)
