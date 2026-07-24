import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from ml.dataset_pipeline import run_dataset_pipeline
from ml.research.research_suite import ResearchSuite

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s | %(message)s")
logger = logging.getLogger(__name__)

def run_suite():
    logger.info("Initializing Research Evaluation Suite...")
    artifact_dir = Path(r"C:\Users\ARYAN - AYUSH\.gemini\antigravity\brain\041528d9-3049-492b-ae1c-5aca37401dd0")
    
    # 1. Standard Simulation for Base Metrics
    logger.info("Generating standard evaluation dataset...")
    train_df, val_df, test_df, meta = run_dataset_pipeline(n_samples=8000, fraud_rate=0.04, oot_split=False)
    
    import pandas as pd
    vdir = Path(r"C:\Users\ARYAN - AYUSH\Downloads\mule_ai_project\backend\data") / meta.version
    full_df = pd.read_csv(vdir / "full_dataset.csv")
    
    suite = ResearchSuite(
        df=full_df, 
        artifact_dir=artifact_dir, 
        labels=full_df["label"].values, 
        train_df=train_df, 
        val_df=val_df, 
        test_df=test_df
    )
    
    suite.run_all()
    
    # 2. Out-Of-Time (OOT) Validation
    logger.info("Generating Temporal OOT dataset...")
    train_oot, val_oot, test_oot, meta_oot = run_dataset_pipeline(n_samples=5000, fraud_rate=0.04, oot_split=True)
    
    from lightgbm import LGBMClassifier
    from sklearn.metrics import average_precision_score
    clf = LGBMClassifier(random_state=42, n_estimators=100, verbose=-1)
    feats = [c for c in train_oot.columns if c.startswith(("F", "G", "T", "P")) and c not in ("Ground_Truth_Scenario", "Transaction_Timestamp", "Account_Creation_Date")]
    clf.fit(train_oot[feats], train_oot["label"])
    
    oot_pr = average_precision_score(test_oot["label"], clf.predict_proba(test_oot[feats])[:, 1])
    standard_pr = average_precision_score(test_df["label"], clf.predict_proba(test_df[feats])[:, 1])
    
    with open(artifact_dir / "TEMPORAL_VALIDATION_REPORT.md", "w") as f:
        f.write("# Temporal Validation Report\n\n")
        f.write(f"The model was trained on data from earlier periods and tested exclusively on future, unseen Out-Of-Time (OOT) data.\n\n")
        f.write(f"- **Standard Validation (Random Split) PR-AUC**: {standard_pr:.4f}\n")
        f.write(f"- **Out-Of-Time (Temporal Split) PR-AUC**: {oot_pr:.4f}\n\n")
        f.write(f"Degradation: {(standard_pr - oot_pr):.4f}\n")
        
    # Append to Master Report
    with open(artifact_dir / "RESEARCH_EVALUATION_REPORT.md", "a") as f:
        f.write("- [Temporal Validation Report](TEMPORAL_VALIDATION_REPORT.md)\n")
        
    logger.info("Research Suite Complete! Check the artifact directory for the Executive Dashboard.")

if __name__ == "__main__":
    run_suite()
