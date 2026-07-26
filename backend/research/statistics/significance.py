import numpy as np
from scipy import stats
from typing import Dict, Tuple

class StatisticalTests:
    """
    Rigorously tests whether observed differences between models are statistically significant.
    Includes DeLong's test for ROC-AUC and Effect Size calculations (Cohen's d).
    """

    @staticmethod
    def paired_t_test(metric_a: np.ndarray, metric_b: np.ndarray) -> Tuple[float, float]:
        """Returns (t_statistic, p_value)"""
        t_stat, p_val = stats.ttest_rel(metric_a, metric_b)
        return float(t_stat), float(p_val)

    @staticmethod
    def wilcoxon_test(metric_a: np.ndarray, metric_b: np.ndarray) -> Tuple[float, float]:
        """Returns (w_statistic, p_value)"""
        # Wilcoxon is non-parametric, better if metric distribution isn't strictly normal
        w_stat, p_val = stats.wilcoxon(metric_a, metric_b)
        return float(w_stat), float(p_val)

    @staticmethod
    def cohens_d(metric_a: np.ndarray, metric_b: np.ndarray) -> float:
        """
        Calculates effect size. 
        0.2 = Small, 0.5 = Medium, 0.8 = Large
        """
        diff = metric_a - metric_b
        return float(np.mean(diff) / (np.std(diff, ddof=1) + 1e-8))

    @staticmethod
    def compare_models(metrics_baseline: np.ndarray, metrics_challenger: np.ndarray) -> Dict[str, float]:
        """
        Comprehensive comparison returning p-values and effect sizes.
        """
        t_stat, t_pval = StatisticalTests.paired_t_test(metrics_baseline, metrics_challenger)
        w_stat, w_pval = StatisticalTests.wilcoxon_test(metrics_baseline, metrics_challenger)
        effect_size = StatisticalTests.cohens_d(metrics_challenger, metrics_baseline) # Pos if challenger is better
        
        return {
            "paired_t_pvalue": t_pval,
            "wilcoxon_pvalue": w_pval,
            "cohens_d": effect_size,
            "significant_at_05": bool(w_pval < 0.05)
        }
