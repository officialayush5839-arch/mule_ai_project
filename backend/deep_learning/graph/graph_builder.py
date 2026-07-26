import pandas as pd
import torch
import numpy as np
from torch_geometric.data import Data
from backend.deep_learning.graph.graph_validator import GraphValidator

class GraphBuilder:
    """
    Parses node/edge dataframes and converts them into PyTorch Geometric Data objects.
    """
    @staticmethod
    def build_from_csv(
        nodes_path: str, 
        edges_path: str,
        feature_cols: list
    ) -> Data:
        """
        Builds a single homogeneous PyG graph for baseline tests.
        """
        nodes_df = pd.read_csv(nodes_path)
        edges_df = pd.read_csv(edges_path)
        
        # 1. Validate
        GraphValidator.validate(nodes_df, edges_df)
        
        # 2. Node Mapping
        # Map raw string IDs to contiguous integers for PyG edge_index
        unique_nodes = nodes_df['node_id'].unique()
        node_mapping = {old_id: new_id for new_id, old_id in enumerate(unique_nodes)}
        
        nodes_df['node_id'] = nodes_df['node_id'].map(node_mapping)
        edges_df['src_id'] = edges_df['src_id'].map(node_mapping)
        edges_df['dst_id'] = edges_df['dst_id'].map(node_mapping)
        
        # Sort nodes by index to ensure feature matrix aligns
        nodes_df = nodes_df.sort_values(by='node_id')
        
        # 3. Build edge_index tensor [2, num_edges]
        src = edges_df['src_id'].values
        dst = edges_df['dst_id'].values
        edge_index = torch.tensor(np.vstack((src, dst)), dtype=torch.long)
        
        # 4. Build node feature tensor (x)
        x = torch.tensor(nodes_df[feature_cols].values, dtype=torch.float)
        
        # 5. Build targets (y)
        if 'is_fraud' in nodes_df.columns:
            y = torch.tensor(nodes_df['is_fraud'].values, dtype=torch.long)
        else:
            y = None
            
        return Data(x=x, edge_index=edge_index, y=y)
