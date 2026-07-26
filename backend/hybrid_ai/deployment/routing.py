from typing import Dict, Any, List

class ContextAwareRouter:
    """
    Intelligently routes inference payloads to the most appropriate combination of models.
    Prevents crashing when modalities (like Graph or Sequence) are missing.
    """
    @staticmethod
    def select_models(payload: Dict[str, Any]) -> List[str]:
        """
        Evaluates available data and selects models.
        """
        selected_models = []
        
        # 1. Classical Models (Always available if static features exist)
        if "static_features" in payload:
            selected_models.extend(["LightGBM", "RandomForest"])
            
            # Tabular Deep Learning
            selected_models.extend(["FT-Transformer"])
            
        # 2. Temporal Models
        if "transaction_history" in payload and len(payload["transaction_history"]) > 3:
            selected_models.extend(["TemporalLSTM", "TemporalTransformer"])
            
        # 3. Graph Models
        if "neighborhood_edge_index" in payload and len(payload["neighborhood_edge_index"]) > 0:
            selected_models.extend(["GraphSAGE", "GAT"])
            
        return selected_models
