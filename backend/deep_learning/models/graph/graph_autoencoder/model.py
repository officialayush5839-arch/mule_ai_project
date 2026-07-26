import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
from torch_geometric.nn import GAE, GCNConv
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class GCNEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels * 2)
        self.conv2 = GCNConv(hidden_channels * 2, hidden_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        return self.conv2(x, edge_index)

class GraphAutoencoder(EnterpriseBaseModel):
    """
    Unsupervised Link Prediction and Embedding Extractor.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "GraphAutoencoder"
        
        self.in_channels = config.get("num_features", 128)
        self.hidden_channels = config.get("hidden_channels", 64)
        
        encoder = GCNEncoder(self.in_channels, self.hidden_channels)
        self.gae = GAE(encoder)

    def encode(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        return self.gae.encode(x, edge_index)
        
    def decode(self, z: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        return self.gae.decode(z, edge_index)

    def forward(self, data_tuple: Tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
        """
        Returns reconstructed edge probabilities (link prediction).
        """
        x, edge_index = data_tuple
        z = self.encode(x, edge_index)
        return self.decode(z, edge_index)
