import torch
from typing import Dict, Any

class GraphAttentionExplainer:
    """
    Interface for extracting attention weights from GAT / GATv2.
    Prepares data for PyG Explainer / Captum visualization.
    """
    @staticmethod
    def extract_attention(edge_index: torch.Tensor, attention_weights: torch.Tensor) -> Dict[str, Any]:
        """
        Takes raw PyG attention weights and maps them back to source/destination nodes.
        attention_weights: [num_edges, num_heads]
        """
        src = edge_index[0].tolist()
        dst = edge_index[1].tolist()
        
        # Average across heads
        avg_attn = attention_weights.mean(dim=1).tolist()
        
        explanations = []
        for s, d, w in zip(src, dst, avg_attn):
            explanations.append({
                "source": s,
                "target": d,
                "attention_score": w
            })
            
        return {"attention_edges": explanations}
