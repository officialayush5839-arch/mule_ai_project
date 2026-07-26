from typing import Dict, List

class ContributionAnalyzer:
    """
    Analyzes which model family contributed the most to the final hybrid prediction.
    """
    @staticmethod
    def analyze_contributions(raw_predictions: Dict[str, float], final_prob: float) -> Dict[str, float]:
        """
        Calculates percentage contribution based on distance to the final probability.
        Models closer to the final probability get higher contribution scores.
        """
        contributions = {
            "Classical": 0.0,
            "Tabular_DL": 0.0,
            "Temporal_DL": 0.0,
            "Graph_DL": 0.0
        }
        
        # Calculate inverse distance (closer = higher score)
        raw_scores = {}
        for model, prob in raw_predictions.items():
            dist = abs(prob - final_prob)
            score = 1.0 / (dist + 1e-5)
            
            if model in ["LightGBM", "RandomForest"]:
                contributions["Classical"] += score
            elif "Tab" in model or "MLP" in model:
                contributions["Tabular_DL"] += score
            elif "Temporal" in model or "LSTM" in model or "GRU" in model:
                contributions["Temporal_DL"] += score
            elif "Graph" in model or "GAT" in model or "GCN" in model:
                contributions["Graph_DL"] += score
                
        # Normalize to percentages
        total_score = sum(contributions.values())
        if total_score > 0:
            for k in contributions.keys():
                contributions[k] = round((contributions[k] / total_score) * 100, 2)
                
        return contributions
