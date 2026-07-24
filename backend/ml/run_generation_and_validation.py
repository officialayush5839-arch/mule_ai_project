import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ml.dataset_pipeline import run_dataset_pipeline
from ml.dataset_validation import generate_validation_reports
from ml.training_pipeline import run_full_pipeline

def main():
    print("Generating Research-Grade Financial Crime Dataset...")
    train_df, val_df, test_df, meta = run_dataset_pipeline(n_samples=5000, fraud_rate=0.04)
    print("Dataset generation complete!")
    print(f"Shape: {train_df.shape}")
    
    print("Generating validation reports...")
    import os
    artifact_dir = Path(r"C:\Users\ARYAN - AYUSH\.gemini\antigravity\brain\041528d9-3049-492b-ae1c-5aca37401dd0")
    generate_validation_reports(train_df, artifact_dir)
    print("Reports generated.")
    
    print("Executing ML Training Pipeline to observe natural performance metrics...")
    # we skip HPO to make it fast
    run_full_pipeline(skip_hpo=True, n_samples=5000)

if __name__ == "__main__":
    main()
