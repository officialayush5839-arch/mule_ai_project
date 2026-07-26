import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
from torch_geometric.nn import SAGEConv
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class GraphSAGE(EnterpriseBaseModel):
    """
    Enterprise GraphSAGE Model supporting multiple aggregators.
    Inherits from EnterpriseBaseModel for unified training.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "GraphSAGE"
        
        self.in_channels = config.get("num_features", 128)
        self.hidden_channels = config.get("hidden_channels", [256, 128])
        self.aggr = config.get("aggr", "mean") # mean, max, lstm
        self.dropout = config.get("dropout", 0.2)
        
        self.convs = nn.ModuleList()
        
        # Build layers
        dims = [self.in_channels] + self.hidden_channels
        for i in range(len(dims) - 1):
            self.convs.append(SAGEConv(dims[i], dims[i+1], aggr=self.aggr))
            
        self.dropout_layer = nn.Dropout(self.dropout)
        
        # Final classification head
        self.head = nn.Linear(dims[-1], 1)

    def forward(self, data_tuple: Tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
        """
        Receives tuple (x, edge_index) from the pipeline.
        x: [num_nodes, num_features]
        edge_index: [2, num_edges]
        """
        x, edge_index = data_tuple
        
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i < len(self.convs) - 1:
                x = x.relu()
                x = self.dropout_layer(x)
                
        return self.head(x)
