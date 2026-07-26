import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GraphValidator:
    """
    Validates graph structures from CSVs before tensor construction to ensure integrity.
    """
    @staticmethod
    def validate(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs validations against the nodes and edges dataframes.
        Raises ValueError if critical violations occur (e.g. missing nodes).
        Returns a dictionary of graph statistics and warnings.
        """
        logger.info("Starting Graph Data Validation...")
        stats = {}
        
        # 1. Duplicate Nodes
        num_nodes = len(nodes_df)
        unique_nodes = nodes_df['node_id'].nunique()
        stats["num_nodes"] = num_nodes
        if unique_nodes < num_nodes:
            raise ValueError("CRITICAL: Duplicate node IDs detected in nodes.csv")
            
        # 2. Missing Endpoints (Orphan Edges)
        node_set = set(nodes_df['node_id'].unique())
        edge_src_set = set(edges_df['src_id'].unique())
        edge_dst_set = set(edges_df['dst_id'].unique())
        
        missing_src = edge_src_set - node_set
        missing_dst = edge_dst_set - node_set
        
        if missing_src or missing_dst:
            raise ValueError(f"CRITICAL: Edges reference non-existent nodes. Missing Srcs: {len(missing_src)}, Missing Dsts: {len(missing_dst)}")
            
        # 3. Self-loops warning
        self_loops = edges_df[edges_df['src_id'] == edges_df['dst_id']]
        stats["self_loops"] = len(self_loops)
        if len(self_loops) > 0:
            logger.warning(f"Graph contains {len(self_loops)} self-loops. These may bias GNN aggregations.")
            
        # 4. Duplicate Edges
        num_edges = len(edges_df)
        unique_edges = len(edges_df.drop_duplicates(subset=['src_id', 'dst_id', 'edge_type']))
        stats["num_edges"] = num_edges
        if unique_edges < num_edges:
            logger.warning(f"Detected {num_edges - unique_edges} duplicate edges.")
            
        # 5. Isolated Nodes
        connected_nodes = edge_src_set.union(edge_dst_set)
        isolated_nodes = node_set - connected_nodes
        stats["isolated_nodes"] = len(isolated_nodes)
        if stats["isolated_nodes"] > 0:
            logger.info(f"Found {stats['isolated_nodes']} isolated nodes.")
            
        logger.info(f"Graph Validation Passed: {stats}")
        return stats
