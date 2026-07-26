import json
import csv
from pathlib import Path
from typing import Dict, Any

class ReportGenerator:
    """
    Automates generation of 13 Markdown reports and LaTeX exports.
    """
    def __init__(self):
        self.output_dir = Path("backend/research/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_latex_table(self, benchmark_results: Dict[str, Dict[str, float]]):
        """
        Exports a LaTeX-ready table for academic papers.
        """
        latex = "\\begin{table}[h]\n\\centering\n\\begin{tabular}{lcccc}\n\\toprule\n"
        latex += "Model & ROC-AUC & PR-AUC & F1-Score & Latency (ms) \\\\\n\\midrule\n"
        
        for model, metrics in benchmark_results.items():
            latex += f"{model} & {metrics['roc_auc']:.3f} & {metrics['pr_auc']:.3f} & {metrics['f1']:.3f} & {metrics['latency_ms']:.1f} \\\\\n"
            
        latex += "\\bottomrule\n\\end{tabular}\n\\caption{Performance comparison across AI families.}\n\\label{tab:performance}\n\\end{table}"
        
        with open(self.output_dir / "performance_table.tex", "w") as f:
            f.write(latex)

    def generate_markdown_summary(self, benchmark_results: Dict[str, Dict[str, float]], env_meta: Dict[str, Any]):
        """
        Generates the Executive Summary.
        """
        with open(self.output_dir / "EXECUTIVE_SUMMARY.md", "w") as f:
            f.write("# Enterprise Research Evaluation: Executive Summary\n\n")
            f.write("## Reproducibility Context\n")
            f.write("```json\n" + json.dumps(env_meta, indent=2) + "\n```\n\n")
            
            f.write("## Benchmark Results\n")
            f.write("| Model | ROC-AUC | F1-Score | Latency (ms) |\n")
            f.write("|---|---|---|---|\n")
            for model, metrics in benchmark_results.items():
                f.write(f"| {model} | {metrics['roc_auc']:.3f} | {metrics['f1']:.3f} | {metrics['latency_ms']} |\n")

    def export_csv(self, benchmark_results: Dict[str, Dict[str, float]]):
        """
        Dumps raw CSV for downstream statistical tools.
        """
        with open(self.output_dir / "benchmark_metrics.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Model", "ROC_AUC", "PR_AUC", "F1", "Latency_ms"])
            for model, metrics in benchmark_results.items():
                writer.writerow([model, metrics['roc_auc'], metrics['pr_auc'], metrics['f1'], metrics['latency_ms']])
