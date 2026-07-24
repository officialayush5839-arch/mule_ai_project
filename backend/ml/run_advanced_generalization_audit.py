import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from ml.research.simulator_override import ResearchOverlapSimulator
from ml.research.generalization_suite import AdvancedGeneralizationSuite

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s | %(message)s")
logger = logging.getLogger(__name__)

def run_advanced_audit():
    logger.info("Initializing Phase 0: Advanced Generalization & Scientific Validation Suite")
    artifact_dir = Path(r"C:\Users\ARYAN - AYUSH\.gemini\antigravity\brain\041528d9-3049-492b-ae1c-5aca37401dd0")
    
    suite = AdvancedGeneralizationSuite(artifact_dir=artifact_dir)
    
    # Run Cross-Seed Validation (includes its own generation)
    suite.run_cross_seed_validation()
    
    # Generate main evaluation dataset with overlap and unknown typologies
    logger.info("Generating master evaluation dataset (Overlap Mode + Unknown Typologies)...")
    sim = ResearchOverlapSimulator(n_samples=6000, fraud_rate=0.04, seed=42, temporal_days=365)
    master_df = sim.generate()
    
    # Execute the rest of the validations on the master_df
    suite.run_feature_removal_challenge(master_df)
    suite.run_ensemble_stability(master_df)
    suite.run_threshold_sensitivity_and_cost(master_df)
    suite.run_loto_and_unknown_fraud(master_df)
    
    suite.export_final_dashboard()
    
    logger.info("Advanced Generalization Suite Complete. Check artifacts for final verdict.")

if __name__ == "__main__":
    run_advanced_audit()
