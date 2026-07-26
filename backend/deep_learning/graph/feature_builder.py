from dataclasses import dataclass
import torch
from typing import Optional

@dataclass
class GraphNodeFeatures:
    """
    Formalizes the fusion of multiple feature spaces into a single graph node representation.
    Designed for Enterprise Hybrid AI.
    """
    static_features: torch.Tensor       # Raw profile / tabular data
    tabular_embedding: Optional[torch.Tensor] = None   # From Phase 2 (e.g. FT-Transformer)
    temporal_embedding: Optional[torch.Tensor] = None  # From Phase 3 (e.g. LSTM/Transformer)

    def get_fused_features(self) -> torch.Tensor:
        """
        Concatenates available feature spaces into a unified dense tensor.
        """
        tensors = [self.static_features]
        if self.tabular_embedding is not None:
            tensors.append(self.tabular_embedding)
        if self.temporal_embedding is not None:
            tensors.append(self.temporal_embedding)
            
        return torch.cat(tensors, dim=-1)

class FeatureBuilder:
    """
    Utility class to construct GraphNodeFeatures from raw components.
    """
    @staticmethod
    def build_features(
        static: torch.Tensor, 
        tabular_emb: Optional[torch.Tensor] = None, 
        temporal_emb: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Returns the flattened representation ready for PyTorch Geometric (x).
        """
        gnf = GraphNodeFeatures(
            static_features=static, 
            tabular_embedding=tabular_emb, 
            temporal_embedding=temporal_emb
        )
        return gnf.get_fused_features()
