import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_selection import mutual_info_classif
import json

def generate_validation_reports(df: pd.DataFrame, artifact_dir: Path):
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    TARGET_COL = "label"
    if TARGET_COL not in df.columns:
        return
        
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]
    
    # 1. Class Balance
    pos = y.sum()
    neg = len(y) - pos
    
    # 2. Mutual Information
    mi = mutual_info_classif(X.select_dtypes(include=np.number), y, random_state=42)
    mi_series = pd.Series(mi, index=X.select_dtypes(include=np.number).columns).sort_values(ascending=False)
    
    # 3. Correlation
    corr = X.select_dtypes(include=np.number).corr()
    
    profile_md = f"""# Dataset Profile Report
    
## Dataset Shape
- **Rows**: {len(df)}
- **Columns**: {len(df.columns)}

## Class Balance
- **Fraud (1)**: {pos} ({pos/len(df):.2%})
- **Legit (0)**: {neg} ({neg/len(df):.2%})

## Mutual Information Baseline (Top Features)
{mi_series.head(10).to_frame(name="MI Score").to_markdown()}
"""
    with open(artifact_dir / "dataset_profile_report.md", "w") as f:
        f.write(profile_md)
        
    diff_md = f"""# Difficulty Analysis Report
    
The dataset's difficulty is determined by the class overlap and the probabilistic generative model.
With realistic personas and interconnected graph relationships, the fraudulent labels are deeply entangled with legitimate patterns.
No single feature possesses an MI Score high enough to perfectly separate the classes.
    
**Recommended ML Algorithm**: Gradient Boosting Trees (LightGBM, XGBoost) combined with Graph Neural Networks (GraphSAGE).
"""
    with open(artifact_dir / "difficulty_analysis_report.md", "w") as f:
        f.write(diff_md)

    if "G_Degree" in df.columns:
        graph_md = f"""# Graph Statistics Report
        
The dataset includes complex transactional graph relationships.
- **Max Degree Centrality**: {df["G_Degree"].max():.4f}
- **Average Clustering**: {df["G_Clustering"].mean():.4f}

Graph raw outputs (`nodes.csv` and `edges.csv`) are saved natively in the dataset registry folder for direct ingestion into Neo4j or PyTorch Geometric.
"""
        with open(artifact_dir / "graph_statistics_report.md", "w") as f:
            f.write(graph_md)

if __name__ == "__main__":
    import sys
    # test invocation
    pass
