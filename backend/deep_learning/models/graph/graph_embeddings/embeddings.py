import torch
from torch_geometric.nn import Node2Vec
from typing import Dict, Any

class GraphEmbedder:
    """
    Random-walk based embedding extractors (Node2Vec, DeepWalk).
    """
    @staticmethod
    def create_node2vec(
        edge_index: torch.Tensor,
        embedding_dim: int = 128,
        walk_length: int = 20,
        context_size: int = 10,
        walks_per_node: int = 10,
        p: float = 1.0,
        q: float = 1.0,
        sparse: bool = True
    ) -> Node2Vec:
        """
        Standard Node2Vec.
        """
        return Node2Vec(
            edge_index,
            embedding_dim=embedding_dim,
            walk_length=walk_length,
            context_size=context_size,
            walks_per_node=walks_per_node,
            p=p,
            q=q,
            sparse=sparse
        )

    @staticmethod
    def create_deepwalk(
        edge_index: torch.Tensor,
        embedding_dim: int = 128,
        walk_length: int = 20,
        context_size: int = 10,
        walks_per_node: int = 10,
        sparse: bool = True
    ) -> Node2Vec:
        """
        DeepWalk is exactly Node2Vec with p=1.0 and q=1.0.
        """
        return Node2Vec(
            edge_index,
            embedding_dim=embedding_dim,
            walk_length=walk_length,
            context_size=context_size,
            walks_per_node=walks_per_node,
            p=1.0,
            q=1.0,
            sparse=sparse
        )
