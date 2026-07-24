"""
model_registry.py
=================
Versioned model persistence layer for MuleNet AI.

Every training run produces its own versioned directory under backend/models/.
The registry tracks all versions, stores rich metadata, and supports rollback.
MLflow experiment tracking is included (local tracking URI, no server required).
"""

import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib

logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_FILE = MODELS_DIR / "registry.json"
BEST_POINTER  = MODELS_DIR / "best_version.txt"


# ─── Registry JSON helpers ───────────────────────────────────────────────────
def _load_registry() -> Dict[str, Any]:
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as fh:
            return json.load(fh)
    return {"versions": [], "best_version": None}


def _save_registry(reg: Dict[str, Any]) -> None:
    with open(REGISTRY_FILE, "w") as fh:
        json.dump(reg, fh, indent=2)


# ─── MLflow (optional) ────────────────────────────────────────────────────────
def _try_mlflow_log(
    run_name: str,
    metrics: Dict[str, float],
    params: Dict[str, Any],
    tags: Dict[str, str],
) -> None:
    """Attempt to log to MLflow; silently skip if not installed."""
    try:
        import mlflow
        mlflow_dir = BASE_DIR / "logs" / "mlruns"
        mlflow.set_tracking_uri(f"file:{mlflow_dir}")
        mlflow.set_experiment("MuleNet_AI")
        with mlflow.start_run(run_name=run_name):
            mlflow.log_metrics({k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))})
            mlflow.log_params({k: str(v) for k, v in params.items()})
            mlflow.set_tags(tags)
        logger.info("MLflow run logged: %s", run_name)
    except ImportError:
        logger.debug("MLflow not installed – skipping experiment tracking")
    except Exception as exc:
        logger.warning("MLflow logging failed (non-fatal): %s", exc)


# ─── Save ────────────────────────────────────────────────────────────────────
def save_model(
    model,
    feature_pipeline,
    metadata: Dict[str, Any],
    version: str,
    set_as_best: bool = False,
) -> Path:
    """
    Persist model + feature pipeline + metadata for a given version.

    Parameters
    ----------
    model            : fitted sklearn-compatible model (must have predict_proba)
    feature_pipeline : fitted FeatureEngineeringPipeline instance
    metadata         : dict with training stats, metrics, hyperparameters, etc.
    version          : version string, e.g. "v3_20260724_120000"
    set_as_best      : if True, write this version as the production pointer
    """
    vdir = MODELS_DIR / version
    vdir.mkdir(parents=True, exist_ok=True)

    # Save model
    model_path = vdir / "model.joblib"
    joblib.dump(model, model_path)
    logger.info("Saved model to %s", model_path)

    # Save feature pipeline
    fp_path = vdir / "feature_pipeline.joblib"
    joblib.dump(feature_pipeline, fp_path)

    # Save metadata
    meta = {
        **metadata,
        "version": version,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(vdir / "metadata.json", "w") as fh:
        json.dump(meta, fh, indent=2)

    # Update registry
    reg = _load_registry()
    existing_versions = [v["version"] for v in reg["versions"]]
    if version not in existing_versions:
        reg["versions"].append({
            "version":   version,
            "saved_at":  meta["saved_at"],
            "pr_auc":    metadata.get("pr_auc",  0.0),
            "roc_auc":   metadata.get("roc_auc", 0.0),
            "f1":        metadata.get("f1",       0.0),
            "source":    metadata.get("dataset_source", "unknown"),
        })

    if set_as_best:
        reg["best_version"] = version
        with open(BEST_POINTER, "w") as fh:
            fh.write(version)

    _save_registry(reg)

    # MLflow logging
    _try_mlflow_log(
        run_name=version,
        metrics={
            k: float(metadata[k])
            for k in ("pr_auc", "roc_auc", "f1", "mcc", "recall")
            if k in metadata
        },
        params=metadata.get("hyperparameters", {}),
        tags={"source": metadata.get("dataset_source", "unknown"), "version": version},
    )

    logger.info("Model registry updated. Version: %s  Best: %s", version, reg["best_version"])
    return vdir


# ─── Load ────────────────────────────────────────────────────────────────────
def load_model(version: Optional[str] = None):
    """
    Load a model + feature pipeline from the registry.

    If version is None, loads the current best version.
    Returns (model, feature_pipeline, metadata).
    """
    if version is None:
        if BEST_POINTER.exists():
            version = BEST_POINTER.read_text().strip()
        else:
            reg = _load_registry()
            version = reg.get("best_version")

    if not version:
        raise FileNotFoundError(
            "No trained model found. Run training_pipeline.py first."
        )

    vdir = MODELS_DIR / version
    if not vdir.exists():
        raise FileNotFoundError(f"Model version '{version}' not found at {vdir}")

    model            = joblib.load(vdir / "model.joblib")
    feature_pipeline = joblib.load(vdir / "feature_pipeline.joblib")
    with open(vdir / "metadata.json") as fh:
        metadata = json.load(fh)

    logger.info("Loaded model version: %s", version)
    return model, feature_pipeline, metadata


# ─── Registry Inspection ─────────────────────────────────────────────────────
def list_versions() -> List[Dict[str, Any]]:
    """Return all registered model versions, sorted newest first."""
    reg = _load_registry()
    return sorted(reg["versions"], key=lambda v: v.get("saved_at", ""), reverse=True)


def get_best_version() -> Optional[str]:
    """Return the current production model version string."""
    if BEST_POINTER.exists():
        return BEST_POINTER.read_text().strip()
    reg = _load_registry()
    return reg.get("best_version")


def get_version_metadata(version: str) -> Dict[str, Any]:
    meta_path = MODELS_DIR / version / "metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata not found for version: {version}")
    with open(meta_path) as fh:
        return json.load(fh)


# ─── Rollback ─────────────────────────────────────────────────────────────────
def rollback_to(version: str) -> None:
    """Set a previous model version as the active production model."""
    vdir = MODELS_DIR / version
    if not vdir.exists():
        raise FileNotFoundError(f"Version '{version}' not found in registry")
    with open(BEST_POINTER, "w") as fh:
        fh.write(version)
    reg = _load_registry()
    reg["best_version"] = version
    _save_registry(reg)
    logger.info("Rolled back production model to version: %s", version)


# ─── Compare & Auto-promote ───────────────────────────────────────────────────
def promote_if_better(
    candidate_version: str,
    metric: str = "pr_auc",
) -> bool:
    """
    Compare candidate model against the current best on `metric`.
    If candidate is better, promote it as the new production model.

    Returns True if promotion occurred.
    """
    reg = _load_registry()
    current_best = reg.get("best_version")

    if not current_best:
        # No existing model – always promote
        rollback_to(candidate_version)
        reg["best_version"] = candidate_version
        _save_registry(reg)
        logger.info("No previous model – promoting %s as best", candidate_version)
        return True

    # Get metrics from registry entries
    versions_map = {v["version"]: v for v in reg["versions"]}
    curr_val = versions_map.get(current_best, {}).get(metric, 0.0)
    cand_val = versions_map.get(candidate_version, {}).get(metric, 0.0)

    if cand_val > curr_val:
        rollback_to(candidate_version)
        reg["best_version"] = candidate_version
        _save_registry(reg)
        logger.info(
            "Promoted %s over %s (%s: %.4f > %.4f)",
            candidate_version, current_best, metric, cand_val, curr_val,
        )
        return True

    logger.info(
        "Kept %s as best (%s: %.4f vs %.4f for %s)",
        current_best, metric, curr_val, cand_val, candidate_version,
    )
    return False
