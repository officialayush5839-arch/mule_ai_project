import asyncio
from typing import Dict, Any
from backend.hybrid_ai.deployment.routing import ContextAwareRouter
from backend.hybrid_ai.fusion.uncertainty import UncertaintyEstimator
from backend.hybrid_ai.meta_learning.meta_model import MetaLearner
from backend.hybrid_ai.calibration.platt_scaling import PlattScaler
from backend.hybrid_ai.explainability.contribution_analysis import ContributionAnalyzer

class HybridInferenceEngine:
    """
    Asynchronously orchestrates multiple AI model families to meet strict latency budgets.
    """
    def __init__(self, fusion_strategy: str = "meta_learner"):
        self.router = ContextAwareRouter()
        self.meta_learner = MetaLearner()
        self.scaler = PlattScaler()
        self.scaler.fit([], []) # Mock fit
        self.fusion_strategy = fusion_strategy

    async def _run_model(self, model_name: str, payload: Dict[str, Any]) -> float:
        """
        Simulates running a single model.
        """
        await asyncio.sleep(0.01) 
        
        if "Graph" in model_name:
            return 0.85
        if "Temporal" in model_name:
            return 0.75
        if "LightGBM" in model_name:
            return 0.60
        return 0.65

    async def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Hybrid Inference API.
        """
        # 1. Route
        selected_models = self.router.select_models(payload)
        
        # 2. Execute Async Parallel Inference
        tasks = [self._run_model(model, payload) for model in selected_models]
        results = await asyncio.gather(*tasks)
        
        raw_predictions = dict(zip(selected_models, results))
        
        # 3. Fuse
        if self.fusion_strategy == "meta_learner":
            fused_prob = self.meta_learner.predict_proba(raw_predictions)
        else:
            fused_prob = sum(results) / len(results) if results else 0.0
            
        # 4. Calibrate
        calibrated_prob = self.scaler.calibrate(fused_prob)
        
        # 5. Uncertainty
        variance = UncertaintyEstimator.calculate_variance(raw_predictions)
        entropy = UncertaintyEstimator.calculate_entropy(calibrated_prob)
        
        # 6. Explainability
        contributions = ContributionAnalyzer.analyze_contributions(raw_predictions, calibrated_prob)
        
        return {
            "prediction": int(calibrated_prob > 0.5),
            "probability": calibrated_prob,
            "uncertainty": {
                "variance": variance,
                "entropy": entropy
            },
            "selected_models": selected_models,
            "model_contributions": contributions,
            "raw_predictions": raw_predictions
        }
