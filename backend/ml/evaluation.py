"""
evaluation.py
=============
Complete model evaluation suite for the MuleNet AI fraud detection system.

Fraud detection uses PR-AUC as the primary metric (not Accuracy), because
the positive class (mules) is rare and costly.

Computes:
  Accuracy, Precision, Recall, F1 (macro + weighted), ROC-AUC, PR-AUC,
  Balanced Accuracy, Matthews Correlation Coefficient, Cohen's Kappa,
  Confusion Matrix, Brier Score, ECE, 10-Fold Stratified Cross-Validation,
  Calibration Curve analysis.

Also implements:
  - Optimal decision threshold search (maximises F1 on validation set)
  - Model leaderboard generation (ranked by PR-AUC)
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold

logger = logging.getLogger(__name__)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]
TARGET_COL   = "label"
N_CV_FOLDS   = 10
RANDOM_SEED  = 42


# ─── Threshold Optimisation ───────────────────────────────────────────────────
def find_optimal_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    metric: str = "f1",
) -> Tuple[float, float]:
    """
    Search decision thresholds in [0.05, 0.95] and return the one that
    maximises the chosen metric on the provided ground truth.

    Returns (best_threshold, best_metric_value)
    """
    thresholds = np.linspace(0.05, 0.95, 181)
    best_thresh = 0.5
    best_val    = -1.0

    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        if metric == "f1":
            val = f1_score(y_true, y_pred, zero_division=0)
        elif metric == "mcc":
            val = matthews_corrcoef(y_true, y_pred)
        elif metric == "recall":
            val = recall_score(y_true, y_pred, zero_division=0)
        else:
            val = f1_score(y_true, y_pred, zero_division=0)

        if val > best_val:
            best_val    = val
            best_thresh = float(t)

    return best_thresh, best_val


# ─── Calibration Metrics ──────────────────────────────────────────────────────
def compute_ece(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """Expected Calibration Error (ECE)."""
    bins = np.linspace(0, 1, n_bins + 1)
    ece  = 0.0
    n    = len(y_true)
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() == 0:
            continue
        acc  = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += (mask.sum() / n) * abs(acc - conf)
    return round(float(ece), 5)


# ─── Core Evaluation ──────────────────────────────────────────────────────────
def evaluate_model(
    model,
    X: np.ndarray,
    y: np.ndarray,
    threshold: float = 0.5,
    model_name: str = "model",
) -> Dict[str, Any]:
    """
    Compute the full metrics suite for a binary classifier on the provided split.
    The model must implement predict_proba(X).
    """
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)

    # Core metrics
    pr_auc  = float(average_precision_score(y, y_prob))
    roc_auc = float(roc_auc_score(y, y_prob))
    f1_w    = float(f1_score(y, y_pred, average="weighted", zero_division=0))
    f1_m    = float(f1_score(y, y_pred, average="macro",    zero_division=0))
    f1_pos  = float(f1_score(y, y_pred, average="binary",   zero_division=0, pos_label=1))

    cm = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

    # Calibration
    fraction_of_positives, mean_predicted = calibration_curve(y, y_prob, n_bins=10)
    brier = float(brier_score_loss(y, y_prob))
    ece   = compute_ece(np.array(y), y_prob)

    metrics: Dict[str, Any] = {
        "model_name":         model_name,
        "threshold":          threshold,
        "n_samples":          int(len(y)),
        "n_positive":         int(y.sum()),
        # Classification metrics
        "accuracy":           round(float(accuracy_score(y, y_pred)),              4),
        "balanced_accuracy":  round(float(balanced_accuracy_score(y, y_pred)),     4),
        "precision":          round(float(precision_score(y, y_pred, zero_division=0)), 4),
        "recall":             round(float(recall_score(y, y_pred, zero_division=0)),   4),
        "f1_binary":          round(f1_pos, 4),
        "f1_macro":           round(f1_m,   4),
        "f1_weighted":        round(f1_w,   4),
        "mcc":                round(float(matthews_corrcoef(y, y_pred)), 4),
        "cohen_kappa":        round(float(cohen_kappa_score(y, y_pred)), 4),
        # Ranking metrics
        "roc_auc":            round(roc_auc,  4),
        "pr_auc":             round(pr_auc,   4),
        # Calibration
        "brier_score":        round(brier,    5),
        "ece":                round(ece,      5),
        # Confusion matrix
        "confusion_matrix": {
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        },
        # Curves (serialisable)
        "calibration_curve": {
            "fraction_of_positives": fraction_of_positives.tolist(),
            "mean_predicted_value":  mean_predicted.tolist(),
        },
    }

    logger.info(
        "[%s] PR-AUC=%.4f  ROC-AUC=%.4f  F1=%.4f  MCC=%.4f  Recall=%.4f",
        model_name, pr_auc, roc_auc, f1_pos,
        metrics["mcc"], metrics["recall"],
    )
    return metrics


# ─── Cross-Validation ─────────────────────────────────────────────────────────
def cross_validate_model(
    model_cls,
    model_params: Dict[str, Any],
    X: np.ndarray,
    y: np.ndarray,
    n_folds: int = N_CV_FOLDS,
    seed: int = RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Stratified K-Fold cross-validation.

    NOTE: Instantiates fresh models per fold to avoid leakage.
    Returns mean ± std for every metric.
    """
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)

    fold_metrics: List[Dict[str, float]] = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), start=1):
        X_tr, X_vl = X[train_idx], X[val_idx]
        y_tr, y_vl = y[train_idx], y[val_idx]

        mdl = model_cls(**model_params)
        mdl.fit(X_tr, y_tr)

        y_prob = mdl.predict_proba(X_vl)[:, 1]
        thresh, _ = find_optimal_threshold(y_vl, y_prob)
        y_pred = (y_prob >= thresh).astype(int)

        fold_metrics.append({
            "pr_auc":  float(average_precision_score(y_vl, y_prob)),
            "roc_auc": float(roc_auc_score(y_vl, y_prob)),
            "f1":      float(f1_score(y_vl, y_pred, zero_division=0)),
            "recall":  float(recall_score(y_vl, y_pred, zero_division=0)),
            "mcc":     float(matthews_corrcoef(y_vl, y_pred)),
        })
        logger.debug("Fold %d: PR-AUC=%.4f", fold, fold_metrics[-1]["pr_auc"])

    cv_result: Dict[str, Any] = {"n_folds": n_folds, "fold_details": fold_metrics}
    for metric_name in fold_metrics[0]:
        vals = [f[metric_name] for f in fold_metrics]
        cv_result[f"{metric_name}_mean"] = round(float(np.mean(vals)), 4)
        cv_result[f"{metric_name}_std"]  = round(float(np.std(vals)),  4)

    logger.info(
        "CV complete – PR-AUC=%.4f±%.4f  F1=%.4f±%.4f",
        cv_result["pr_auc_mean"], cv_result["pr_auc_std"],
        cv_result["f1_mean"],     cv_result["f1_std"],
    )
    return cv_result


# ─── Model Leaderboard ────────────────────────────────────────────────────────
def generate_leaderboard(
    model_results: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Rank all evaluated models by PR-AUC (primary), then MCC (secondary).

    Parameters
    ----------
    model_results : {model_name → evaluate_model() output}

    Returns
    -------
    Ranked list of dicts (best model first).
    """
    rows = []
    for name, res in model_results.items():
        rows.append({
            "rank":             0,
            "model":            name,
            "pr_auc":           res.get("pr_auc",           0.0),
            "mcc":              res.get("mcc",              0.0),
            "f1":               res.get("f1_binary",        0.0),
            "recall":           res.get("recall",           0.0),
            "roc_auc":          res.get("roc_auc",          0.0),
            "balanced_accuracy":res.get("balanced_accuracy",0.0),
            "brier_score":      res.get("brier_score",      1.0),
            "threshold":        res.get("threshold",        0.5),
        })

    # Sort: PR-AUC descending, MCC descending as tiebreaker
    rows.sort(key=lambda r: (r["pr_auc"], r["mcc"]), reverse=True)
    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    return rows


def format_leaderboard_markdown(leaderboard: List[Dict[str, Any]]) -> str:
    """Format leaderboard as a markdown table."""
    header = (
        "| Rank | Model | PR-AUC | MCC | F1 | Recall | ROC-AUC |\n"
        "| ---- | ----- | -----: | --: | -: | -----: | ------: |\n"
    )
    rows = ""
    for r in leaderboard:
        rows += (
            f"| {r['rank']} | {r['model']} | {r['pr_auc']:.4f} | "
            f"{r['mcc']:.4f} | {r['f1']:.4f} | {r['recall']:.4f} | "
            f"{r['roc_auc']:.4f} |\n"
        )
    return header + rows
