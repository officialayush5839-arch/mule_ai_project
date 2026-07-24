import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

def sparsemax(z: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """Pure PyTorch Sparsemax implementation"""
    sorted_z, _ = torch.sort(z, dim=dim, descending=True)
    cumsum_z = torch.cumsum(sorted_z, dim=dim)
    k = torch.arange(1, z.size(dim) + 1, device=z.device).expand_as(z)
    is_gt = sorted_z > (cumsum_z - 1) / k
    k_max = is_gt.cumsum(dim).max(dim, keepdim=True)[0]
    tau = (cumsum_z.gather(dim, k_max - 1) - 1) / k_max
    return torch.clamp(z - tau, min=0.0)

class GhostBatchNorm(nn.Module):
    """Ghost Batch Normalization for TabNet"""
    def __init__(self, input_dim: int, virtual_batch_size: int = 128, momentum: float = 0.01):
        super().__init__()
        self.input_dim = input_dim
        self.virtual_batch_size = virtual_batch_size
        self.bn = nn.BatchNorm1d(input_dim, momentum=momentum)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training and x.size(0) > self.virtual_batch_size:
            chunks = x.chunk(int(torch.ceil(torch.tensor(x.size(0) / self.virtual_batch_size))), dim=0)
            res = [self.bn(x_) for x_ in chunks]
            return torch.cat(res, dim=0)
        return self.bn(x)

class FeatureTransformerBlock(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, vbs: int = 128):
        super().__init__()
        self.fc = nn.Linear(input_dim, output_dim, bias=False)
        self.bn = GhostBatchNorm(output_dim, virtual_batch_size=vbs)
        self.glu = nn.GLU(dim=1)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc(x)
        x = self.bn(x)
        # GLU halves the output dimension, so fc output_dim should be 2 * actual output_dim
        return self.glu(x)

class TabNet(EnterpriseBaseModel):
    """
    Pure PyTorch implementation of TabNet.
    Features: Sparse sequential attention, Feature masks, Ghost BN.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TabNet"
        
        self.num_dim = config.get("num_features", 0)
        self.cat_dims = config.get("cat_dims", [])
        
        self.embeddings = nn.ModuleList([
            nn.Embedding(cardinality, emb_dim) 
            for cardinality, emb_dim in self.cat_dims
        ])
        total_emb_dim = sum(emb_dim for _, emb_dim in self.cat_dims)
        self.input_dim = self.num_dim + total_emb_dim
        
        self.n_d = config.get("n_d", 8)
        self.n_a = config.get("n_a", 8)
        self.n_steps = config.get("n_steps", 3)
        self.gamma = config.get("gamma", 1.3)
        self.vbs = config.get("virtual_batch_size", 128)
        
        # Initial BN
        self.initial_bn = nn.BatchNorm1d(self.input_dim, momentum=0.01)
        
        # Feature Transformer (Shared & Dependent) - Simplified for brevity
        self.shared_ft = FeatureTransformerBlock(self.input_dim, (self.n_d + self.n_a) * 2, self.vbs)
        
        self.step_fts = nn.ModuleList([
            FeatureTransformerBlock(self.n_d + self.n_a, (self.n_d + self.n_a) * 2, self.vbs)
            for _ in range(self.n_steps)
        ])
        
        self.attentive_transformers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.n_a, self.input_dim, bias=False),
                GhostBatchNorm(self.input_dim, virtual_batch_size=self.vbs)
            ) for _ in range(self.n_steps)
        ])
        
        self.head = nn.Linear(self.n_d, 1, bias=False)

    def forward(self, x: tuple) -> torch.Tensor:
        out, _ = self.forward_masks(x)
        return out

    def forward_masks(self, x: tuple) -> Tuple[torch.Tensor, torch.Tensor]:
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
            
        x_fused = self.initial_bn(x_fused)
        
        batch_size = x_fused.size(0)
        out_accumulator = torch.zeros(batch_size, self.n_d, device=x_fused.device)
        prior_scales = torch.ones(batch_size, self.input_dim, device=x_fused.device)
        
        # Initial Step
        x_ft = self.shared_ft(x_fused)
        a = x_ft[:, self.n_d:]
        
        sparse_loss = torch.tensor(0.0, device=x_fused.device)
        masks = []
        
        for step in range(self.n_steps):
            # Attentive Transformer
            mask = self.attentive_transformers[step](a)
            mask = sparsemax(mask * prior_scales, dim=-1)
            prior_scales = prior_scales * (self.gamma - mask)
            
            sparse_loss += (mask * torch.log(mask + 1e-15)).mean()
            masks.append(mask)
            
            # Masked input
            masked_x = mask * x_fused
            x_ft = self.shared_ft(masked_x)
            x_step = self.step_fts[step](x_ft)
            
            d = x_step[:, :self.n_d]
            a = x_step[:, self.n_d:]
            
            out_accumulator += F.relu(d)
            
        # Prediction
        out = self.head(out_accumulator)
        return out, sparse_loss
