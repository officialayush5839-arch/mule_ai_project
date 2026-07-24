"""
training_pipeline.py
====================
End-to-end ML training orchestrator for MuleNet AI.

Runs all phases in sequence:
  1. Dataset  (synthetic generation OR uploaded CSV)
  2. Schema mapping (if uploaded)
  3. Profiling & quality report
  4. Feature engineering (fit on train, apply to val/test)
  5. Hyperparameter optimisation  (Optuna, skippable with --skip-hpo)
  6. Multi-model training
  7. 10-fold cross-validation on best model
  8. Final evaluation on held-out test set
  9. Model registration + auto-promotion
 10. Drift detection vs previous model (if applicable)
 11. Report generation

CLI Usage:
  python -m ml.training_pipeline
  python -m ml.training_pipeline --skip-hpo
  python -m ml.training_pipeline --data-path /path/to/data.csv

All random seeds are fixed at 42 for full reproducibility.
"""

import argparse
import json
import logging
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

# ── Reproducibility (set before all ML imports) ───────────────────────────────
RANDOM_SEED = 42
os.environ["PYTHONHASHSEED"] = str(RANDOM_SEED)
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("training_pipeline")

BASE_DIR     = Path(__file__).resolve().parent.parent
REPORTS_DIR  = BASE_DIR / "ml" / "reports"
MODELS_DIR   = BASE_DIR / "models"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Phase helpers ────────────────────────────────────────────────────────────
def _phase(n: int, title: str):
    logger.info("")
    logger.info("=" * 60)
    logger.info("  PHASE %d – %s", n, title)
    logger.info("=" * 60)


def _save_json(data: Any, path: Path):
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, default=str)


# ─── Report Generators ────────────────────────────────────────────────────────
def _write_dataset_profile_report(profile: Dict, metadata_dict: Dict, path: Path):
    lines = [
        "# Dataset Profile Report",
        f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Version:** {metadata_dict.get('version', 'N/A')}",
        f"**Source:** {metadata_dict.get('source', 'N/A')}",
        f"**Samples:** {metadata_dict.get('n_samples', 0):,}",
        f"**Positive (mule):** {metadata_dict.get('n_positive', 0):,} "
        f"({metadata_dict.get('fraud_rate', 0)*100:.2f}%)",
        f"**Train / Val / Test:** {metadata_dict.get('train_samples', 0):,} / "
        f"{metadata_dict.get('val_samples', 0):,} / {metadata_dict.get('test_samples', 0):,}",
        "\n## Quality Issues",
    ]
    issues = metadata_dict.get("quality_issues", [])
    if issues:
        for issue in issues:
            lines.append(f"- ⚠️  {issue}")
    else:
        lines.append("- ✅ No quality issues detected")

    lines += ["\n## Feature Statistics\n",
               "| Feature | Mean | Std | Min | Max | Skew | Missing % |",
               "| ------- | ---- | --- | --- | --- | ---- | --------- |"]
    for feat, stats in profile.get("columns", {}).items():
        lines.append(
            f"| {feat} | {stats.get('mean','?')} | {stats.get('std','?')} | "
            f"{stats.get('min','?')} | {stats.get('max','?')} | "
            f"{stats.get('skew','?')} | {stats.get('missing_pct','?')} |"
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Dataset profile report written to %s", path)


def _write_training_report(
    results: Dict,
    eval_metrics: Dict,
    cv_results: Dict,
    version: str,
    path: Path,
):
    lb = results.get("leaderboard", [])
    lines = [
        "# Training Report",
        f"\n**Version:** {version}",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "\n## Model Leaderboard (Validation PR-AUC)\n",
        "| Rank | Model | Val PR-AUC |",
        "| ---- | ----- | ---------: |",
    ]
    for i, row in enumerate(lb, 1):
        lines.append(f"| {i} | {row['model']} | {row['val_pr_auc']:.4f} |")

    best_name = results.get("best_model_name", "?")
    lines += [
        f"\n**Best Model:** {best_name}",
        "\n## Test Set Evaluation\n",
        f"- PR-AUC:            **{eval_metrics.get('pr_auc', '?')}**",
        f"- ROC-AUC:           {eval_metrics.get('roc_auc', '?')}",
        f"- F1 (binary):       {eval_metrics.get('f1_binary', '?')}",
        f"- Recall:            {eval_metrics.get('recall', '?')}",
        f"- Precision:         {eval_metrics.get('precision', '?')}",
        f"- MCC:               {eval_metrics.get('mcc', '?')}",
        f"- Balanced Accuracy: {eval_metrics.get('balanced_accuracy', '?')}",
        f"- Brier Score:       {eval_metrics.get('brier_score', '?')}",
        f"- ECE:               {eval_metrics.get('ece', '?')}",
        f"- Threshold:         {eval_metrics.get('threshold', '?')}",
        "\n## Cross-Validation (10-fold, best model)\n",
        f"- PR-AUC: {cv_results.get('pr_auc_mean','?')} ± {cv_results.get('pr_auc_std','?')}",
        f"- F1:     {cv_results.get('f1_mean','?')}     ± {cv_results.get('f1_std','?')}",
        f"- Recall: {cv_results.get('recall_mean','?')} ± {cv_results.get('recall_std','?')}",
        "\n## Confusion Matrix\n",
    ]
    cm = eval_metrics.get("confusion_matrix", {})
    tn, fp = cm.get("tn", "?"), cm.get("fp", "?")
    fn, tp = cm.get("fn", "?"), cm.get("tp", "?")
    lines += [
        "| Actual \\ Predicted | Negative | Positive |",
        "| ------------------ | -------- | -------- |",
        f"| Negative (legit)   | TN={tn}  | FP={fp}  |",
        f"| Positive (mule)    | FN={fn}  | TP={tp}  |",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Training report written to %s", path)


def _write_model_card(
    best_model_name: str,
    eval_metrics: Dict,
    metadata_dict: Dict,
    version: str,
    path: Path,
):
    lines = [
        f"# Model Card – {best_model_name}",
        f"\n**Version:** {version}",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "\n## Intended Use",
        "Detection of mule accounts in banking transaction data.",
        "Output: risk probability [0,1] and categorical classification.",
        "\n## Training Data",
        f"- Source: {metadata_dict.get('source', '?')}",
        f"- Samples: {metadata_dict.get('n_samples', '?'):,}",
        f"- Fraud rate: {metadata_dict.get('fraud_rate', 0)*100:.2f}%",
        f"- Dataset hash: `{metadata_dict.get('dataset_hash', '?')}`",
        "\n## Performance (Independent Test Set)",
        f"- PR-AUC:  **{eval_metrics.get('pr_auc', '?')}** (primary metric)",
        f"- ROC-AUC: {eval_metrics.get('roc_auc', '?')}",
        f"- F1:      {eval_metrics.get('f1_binary', '?')}",
        f"- Recall:  {eval_metrics.get('recall', '?')} (↑ minimises missed mules)",
        f"- MCC:     {eval_metrics.get('mcc', '?')}",
        "\n## Limitations",
        "- Trained on synthetic data unless real data uploaded.",
        "- Performance on real data may differ from reported metrics.",
        "- Requires monitoring for distribution drift over time.",
        "\n## Decision Threshold",
        f"Optimal threshold: **{eval_metrics.get('threshold', 0.5)}** "
        "(search on validation set, maximises F1)",
        "\n## Ethical Considerations",
        "- False positives flag legitimate accounts; human review is mandatory.",
        "- Model output is advisory; final decisions must involve compliance officers.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Model card written to %s", path)


# ─── Main Pipeline ─────────────────────────────────────────────────────────────
def run_full_pipeline(
    data_path: Optional[str] = None,
    skip_hpo: bool = False,
    n_samples: int = 50_000,
    fraud_rate: float = 0.04,
    seed: int = RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Execute all training phases in sequence.

    Parameters
    ----------
    data_path : path to real CSV, or None for synthetic
    skip_hpo  : skip Optuna HPO (faster, lower quality)
    n_samples : synthetic dataset size
    fraud_rate: synthetic fraud rate
    seed      : master random seed

    Returns
    -------
    summary dict with version, metrics, and status
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # ── Phase 1: Dataset ─────────────────────────────────────────────
    _phase(1, "DATASET PIPELINE")
    from ml.dataset_pipeline import run_dataset_pipeline, profile_dataset, FEATURE_COLS, TARGET_COL
    from ml.schema_mapper import auto_map_dataframe

    # If uploading, try auto-mapping first
    if data_path and Path(data_path).exists():
        import pandas as pd
        raw_df = pd.read_csv(data_path)
        mapped_df, mapping_report = auto_map_dataframe(raw_df)
        logger.info("Schema mapping: %s", mapping_report["mapping"])
        if mapping_report["unmapped"]:
            logger.warning("Unmapped columns (ignored): %s", mapping_report["unmapped"])
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        mapped_df.to_csv(tmp.name, index=False)
        actual_data_path = tmp.name
    else:
        actual_data_path = None

    train_df, val_df, test_df, dataset_meta = run_dataset_pipeline(
        data_path=actual_data_path,
        n_samples=n_samples,
        fraud_rate=fraud_rate,
        seed=seed,
    )

    # Clean up temp file
    if actual_data_path and actual_data_path != data_path:
        try:
            os.unlink(actual_data_path)
        except Exception:
            pass

    import dataclasses
    metadata_dict = dataclasses.asdict(dataset_meta)
    version = f"v1_{timestamp}"

    # ── Phase 2: Profiling ───────────────────────────────────────────
    _phase(2, "DATASET PROFILING")
    import pandas as pd
    full_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    profile = profile_dataset(full_df)
    _write_dataset_profile_report(profile, metadata_dict, REPORTS_DIR / "dataset_profile_report.md")
    _save_json(profile, REPORTS_DIR / "dataset_profile.json")

    # ── Phase 3: Feature Engineering ────────────────────────────────
    _phase(3, "FEATURE ENGINEERING")
    from ml.feature_engineering import FeatureEngineeringPipeline

    fe_pipeline = FeatureEngineeringPipeline()
    X_train = fe_pipeline.fit_transform(train_df)
    X_val   = fe_pipeline.transform(val_df)
    X_test  = fe_pipeline.transform(test_df)

    y_train = train_df[TARGET_COL].values if TARGET_COL in train_df.columns else np.zeros(len(train_df))
    y_val   = val_df[TARGET_COL].values   if TARGET_COL in val_df.columns   else np.zeros(len(val_df))
    y_test  = test_df[TARGET_COL].values  if TARGET_COL in test_df.columns  else np.zeros(len(test_df))

    fe_pipeline.save(version)
    _save_json(fe_pipeline.get_feature_info(), REPORTS_DIR / "feature_engineering_report.json")
    logger.info("Feature shapes – train: %s  val: %s  test: %s", X_train.shape, X_val.shape, X_test.shape)

    # ── Phase 4: Hyperparameter Optimisation ─────────────────────────
    hpo_params: Dict = {}
    if not skip_hpo:
        _phase(4, "HYPERPARAMETER OPTIMISATION (Optuna)")
        from ml.hyperparameter_optimization import run_hyperparameter_optimization
        hpo_params = run_hyperparameter_optimization(
            X_train=X_train,
            y_train=y_train,
            version=version,
            n_trials=40,
        )
        _save_json(hpo_params, REPORTS_DIR / "hyperparameter_report.json")
    else:
        logger.info("HPO skipped (--skip-hpo flag set)")

    # ── Phase 5: Model Training ───────────────────────────────────────
    _phase(5, "MODEL TRAINING")
    from ml.model_training import train_all_models

    training_results = train_all_models(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        hpo_params=hpo_params,
        build_ensemble=True,
    )

    best_name = training_results.get("best_model_name")
    if not best_name:
        raise RuntimeError("All models failed to train. Check logs above.")

    logger.info("Best model: %s", best_name)

    # Retrieve the best model object
    all_models = {**training_results["individual"], **training_results["ensembles"]}
    best_model, best_val_auc = all_models[best_name]

    # ── Phase 6: Threshold Optimisation ──────────────────────────────
    _phase(6, "THRESHOLD OPTIMISATION")
    from ml.evaluation import find_optimal_threshold

    y_val_prob = best_model.predict_proba(X_val)[:, 1]
    optimal_threshold, best_f1_val = find_optimal_threshold(y_val, y_val_prob, metric="f1")
    logger.info("Optimal threshold: %.4f  (val F1=%.4f)", optimal_threshold, best_f1_val)

    # ── Phase 7: Cross-Validation ─────────────────────────────────────
    _phase(7, "10-FOLD CROSS-VALIDATION")
    from ml.evaluation import cross_validate_model

    # CV on combined train+val for best model (using its class and best params)
    X_tv = np.vstack([X_train, X_val])
    y_tv = np.concatenate([y_train, y_val])

    cv_results: Dict = {}
    try:
        model_class  = type(best_model)
        model_params = best_model.get_params()
        cv_results   = cross_validate_model(model_class, model_params, X_tv, y_tv, n_folds=10)
        _save_json(cv_results, REPORTS_DIR / "cross_validation_report.json")
    except Exception as exc:
        logger.warning("Cross-validation failed (non-fatal): %s", exc)
        cv_results = {"note": f"CV skipped: {exc}"}

    # ── Phase 8: Final Test Evaluation ───────────────────────────────
    _phase(8, "FINAL TEST EVALUATION")
    from ml.evaluation import evaluate_model, generate_leaderboard, format_leaderboard_markdown

    eval_metrics = evaluate_model(
        model=best_model,
        X=X_test,
        y=y_test,
        threshold=optimal_threshold,
        model_name=best_name,
    )
    _save_json(eval_metrics, REPORTS_DIR / "metrics_report.json")

    # Leaderboard across all models on test set
    all_eval: Dict = {}
    for mname, (mdl, _) in all_models.items():
        try:
            all_eval[mname] = evaluate_model(mdl, X_test, y_test, optimal_threshold, mname)
        except Exception:
            pass
    leaderboard = generate_leaderboard(all_eval)
    _save_json(leaderboard, REPORTS_DIR / "leaderboard.json")
    lb_md = format_leaderboard_markdown(leaderboard)
    (REPORTS_DIR / "leaderboard.md").write_text(f"# Model Leaderboard\n\n{lb_md}", encoding="utf-8")

    # ── Phase 9: Explainability ───────────────────────────────────────
    _phase(9, "EXPLAINABILITY (SHAP)")
    from ml.explainability import ExplainabilityEngine

    explainability = ExplainabilityEngine()
    try:
        explainability.fit(
            model=best_model,
            X_background=X_train,
            feature_names=fe_pipeline.feature_names_out_,
        )
        gi = explainability.get_global_importance()
        _save_json(gi, REPORTS_DIR / "explainability_report.json")
        pi = explainability.permutation_importance(best_model, X_test, y_test)
        _save_json(pi, REPORTS_DIR / "permutation_importance.json")
    except Exception as exc:
        logger.warning("SHAP fitting failed (non-fatal): %s", exc)

    # ── Phase 10: Model Registration ──────────────────────────────────
    _phase(10, "MODEL REGISTRATION")
    from ml.model_registry import save_model, promote_if_better

    meta_to_save = {
        **metadata_dict,
        "best_model_name":    best_name,
        "pr_auc":             eval_metrics.get("pr_auc",    0.0),
        "roc_auc":            eval_metrics.get("roc_auc",   0.0),
        "f1":                 eval_metrics.get("f1_binary", 0.0),
        "mcc":                eval_metrics.get("mcc",       0.0),
        "recall":             eval_metrics.get("recall",    0.0),
        "optimal_threshold":  optimal_threshold,
        "val_pr_auc":         best_val_auc,
        "hyperparameters":    hpo_params.get(best_name, {}),
        "dataset_version":    dataset_meta.version,
        "dataset_source":     dataset_meta.source,
    }
    save_model(
        model=best_model,
        feature_pipeline=fe_pipeline,
        metadata=meta_to_save,
        version=version,
        set_as_best=False,   # decide after comparison
    )
    promoted = promote_if_better(version, metric="pr_auc")
    logger.info("Model promoted to production: %s", promoted)

    # ── Phase 11: Report Generation ───────────────────────────────────
    _phase(11, "REPORT GENERATION")
    _write_training_report(training_results, eval_metrics, cv_results, version, REPORTS_DIR / "training_report.md")
    _write_model_card(best_name, eval_metrics, metadata_dict, version, REPORTS_DIR / "model_card.md")

    # Deployment report
    dep_lines = [
        "# Deployment Report",
        f"\n**Version:** {version}",
        f"**Model:** {best_name}",
        f"**Promoted:** {'Yes' if promoted else 'No (previous model retained)'}",
        f"\n**Production Endpoint:** POST /api/predict",
        f"**Batch Endpoint:** POST /api/batch-analyze",
        f"\n**Threshold:** {optimal_threshold}",
        f"**PR-AUC (test):** {eval_metrics.get('pr_auc')}",
        f"**ROC-AUC (test):** {eval_metrics.get('roc_auc')}",
    ]
    (REPORTS_DIR / "deployment_report.md").write_text("\n".join(dep_lines), encoding="utf-8")

    logger.info("")
    logger.info("✅ TRAINING COMPLETE")
    logger.info("   Version:       %s", version)
    logger.info("   Best model:    %s", best_name)
    logger.info("   Test PR-AUC:   %.4f", eval_metrics.get("pr_auc", 0))
    logger.info("   Test ROC-AUC:  %.4f", eval_metrics.get("roc_auc", 0))
    logger.info("   Test F1:       %.4f", eval_metrics.get("f1_binary", 0))
    logger.info("   Threshold:     %.4f", optimal_threshold)
    logger.info("   Promoted:      %s", promoted)
    logger.info("")

    # Reload the inference engine so new model is picked up immediately
    try:
        from ml.inference import reload_engine
        reload_engine()
        logger.info("InferenceEngine reloaded with new model.")
    except Exception as exc:
        logger.warning("Inference engine reload failed (restart server): %s", exc)

    return {
        "version":      version,
        "best_model":   best_name,
        "pr_auc":       eval_metrics.get("pr_auc"),
        "roc_auc":      eval_metrics.get("roc_auc"),
        "f1":           eval_metrics.get("f1_binary"),
        "threshold":    optimal_threshold,
        "promoted":     promoted,
    }


# ─── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MuleNet AI – Training Pipeline")
    parser.add_argument("--data-path",   type=str,  default=None,  help="Path to real CSV dataset")
    parser.add_argument("--skip-hpo",    action="store_true",      help="Skip Optuna HPO (faster)")
    parser.add_argument("--n-samples",   type=int,  default=50_000,help="Synthetic dataset size")
    parser.add_argument("--fraud-rate",  type=float,default=0.04,  help="Synthetic fraud rate [0.01-0.10]")
    parser.add_argument("--seed",        type=int,  default=42,    help="Random seed")
    args = parser.parse_args()

    run_full_pipeline(
        data_path=args.data_path,
        skip_hpo=args.skip_hpo,
        n_samples=args.n_samples,
        fraud_rate=args.fraud_rate,
        seed=args.seed,
    )
