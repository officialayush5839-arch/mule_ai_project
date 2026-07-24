"""
hyperparameter_optimization.py
===============================
Optuna-based hyperparameter optimisation for MuleNet AI.

Objective metric: Validation PR-AUC (superior to Accuracy for imbalanced fraud).
Sampler:          TPE (Tree-structured Parzen Estimator) – Bayesian optimization.
Pruner:           Median pruner to kill unpromising trials early.

Models optimised: LightGBM, XGBoost, Random Forest, Extra Trees.
CatBoost skipped from HPO (uses its own internal tuning).

Results saved to: backend/models/{version}/best_parameters.json
"""

import json
import logging
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED  = 42
N_TRIALS     = 40    # practical for local machine; increase to 100 for better tuning
N_CV_FOLDS   = 3     # inner CV folds inside HPO (fast)
TIMEOUT_SECS = 600   # 10 minutes max per model


def _import_optuna():
    try:
        import optuna
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        return optuna
    except ImportError:
        logger.warning("Optuna not installed – HPO will be skipped")
        return None


# ─── Objective Functions ──────────────────────────────────────────────────────
def _lgbm_objective(trial, X: np.ndarray, y: np.ndarray) -> float:
    import lightgbm as lgb
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos

    params = {
        "n_estimators":      trial.suggest_int("n_estimators",    100, 800),
        "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "max_depth":         trial.suggest_int("max_depth",        3,  10),
        "num_leaves":        trial.suggest_int("num_leaves",       8,  64),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
        "subsample":         trial.suggest_float("subsample",      0.5, 1.0),
        "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha":         trial.suggest_float("reg_alpha",     1e-4, 10.0, log=True),
        "reg_lambda":        trial.suggest_float("reg_lambda",    1e-4, 10.0, log=True),
        "scale_pos_weight":  max(1, n_neg // max(n_pos, 1)),
        "random_state":      RANDOM_SEED,
        "n_jobs":            -1,
        "verbose":           -1,
    }
    model = lgb.LGBMClassifier(**params)
    return _cv_score(model, X, y)


def _xgb_objective(trial, X: np.ndarray, y: np.ndarray) -> float:
    import xgboost as xgb
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos

    params = {
        "n_estimators":    trial.suggest_int("n_estimators",   100, 800),
        "learning_rate":   trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "max_depth":       trial.suggest_int("max_depth",       3,  10),
        "min_child_weight":trial.suggest_int("min_child_weight", 1, 20),
        "subsample":       trial.suggest_float("subsample",     0.5, 1.0),
        "colsample_bytree":trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha":       trial.suggest_float("reg_alpha",    1e-4, 10.0, log=True),
        "reg_lambda":      trial.suggest_float("reg_lambda",   1e-4, 10.0, log=True),
        "scale_pos_weight":max(1, n_neg // max(n_pos, 1)),
        "eval_metric":     "aucpr",
        "random_state":    RANDOM_SEED,
        "n_jobs":          -1,
        "verbosity":       0,
    }
    try:
        model = xgb.XGBClassifier(**params)
    except Exception:
        params.pop("use_label_encoder", None)
        model = xgb.XGBClassifier(**params)
    return _cv_score(model, X, y)


def _rf_objective(trial, X: np.ndarray, y: np.ndarray) -> float:
    from sklearn.ensemble import RandomForestClassifier
    params = {
        "n_estimators":   trial.suggest_int("n_estimators",  50, 500),
        "max_depth":      trial.suggest_int("max_depth",      3,  20),
        "min_samples_leaf":trial.suggest_int("min_samples_leaf", 1, 20),
        "max_features":   trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
        "class_weight":   "balanced",
        "random_state":   RANDOM_SEED,
        "n_jobs":         -1,
    }
    model = RandomForestClassifier(**params)
    return _cv_score(model, X, y)


def _et_objective(trial, X: np.ndarray, y: np.ndarray) -> float:
    from sklearn.ensemble import ExtraTreesClassifier
    params = {
        "n_estimators":    trial.suggest_int("n_estimators",   50, 500),
        "max_depth":       trial.suggest_int("max_depth",       3,  20),
        "min_samples_leaf":trial.suggest_int("min_samples_leaf", 1, 20),
        "max_features":    trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
        "class_weight":    "balanced",
        "random_state":    RANDOM_SEED,
        "n_jobs":          -1,
    }
    model = ExtraTreesClassifier(**params)
    return _cv_score(model, X, y)


# ─── Inner CV Scorer ──────────────────────────────────────────────────────────
def _cv_score(model, X: np.ndarray, y: np.ndarray) -> float:
    """3-fold stratified CV, returns mean PR-AUC."""
    skf = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    scores = []
    for tr_idx, vl_idx in skf.split(X, y):
        mdl_clone = type(model)(**model.get_params())
        try:
            mdl_clone.fit(X[tr_idx], y[tr_idx])
            y_prob = mdl_clone.predict_proba(X[vl_idx])[:, 1]
            scores.append(average_precision_score(y[vl_idx], y_prob))
        except Exception:
            scores.append(0.0)
    return float(np.mean(scores)) if scores else 0.0


# ─── Per-model HPO ────────────────────────────────────────────────────────────
def _run_study(
    model_name: str,
    objective_fn,
    X: np.ndarray,
    y: np.ndarray,
    n_trials: int,
    timeout: int,
):
    optuna = _import_optuna()
    if optuna is None:
        return {}

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=5),
    )

    def wrapped(trial):
        return objective_fn(trial, X, y)

    study.optimize(wrapped, n_trials=n_trials, timeout=timeout, n_jobs=1, show_progress_bar=False)

    best = study.best_params
    logger.info(
        "[HPO:%s] Best PR-AUC=%.4f  params=%s",
        model_name, study.best_value, best,
    )
    return best


# ─── Public Entry Point ───────────────────────────────────────────────────────
def run_hyperparameter_optimization(
    X_train: np.ndarray,
    y_train: np.ndarray,
    version: str,
    n_trials: int = N_TRIALS,
    models_to_tune: Optional[list] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Run Optuna HPO for all supported models.

    Parameters
    ----------
    X_train, y_train : training features and labels
    version          : model version string (for saving results)
    n_trials         : number of Optuna trials per model
    models_to_tune   : subset of models to tune; None = tune all

    Returns
    -------
    {model_name → best_params_dict}
    """
    optuna = _import_optuna()
    if optuna is None:
        logger.warning("HPO skipped – Optuna not available.")
        return {}

    if models_to_tune is None:
        models_to_tune = ["LightGBM", "XGBoost", "RandomForest", "ExtraTrees"]

    objective_map = {
        "LightGBM":    _lgbm_objective,
        "XGBoost":     _xgb_objective,
        "RandomForest":_rf_objective,
        "ExtraTrees":  _et_objective,
    }

    best_params: Dict[str, Dict[str, Any]] = {}

    for model_name in models_to_tune:
        if model_name not in objective_map:
            continue

        # Check if the library is actually installed
        if model_name == "LightGBM":
            try:
                import lightgbm
            except ImportError:
                logger.warning("LightGBM not installed – skipping HPO for it")
                continue
        if model_name == "XGBoost":
            try:
                import xgboost
            except ImportError:
                logger.warning("XGBoost not installed – skipping HPO for it")
                continue

        logger.info("[HPO:%s] Starting %d trials...", model_name, n_trials)
        best = _run_study(
            model_name=model_name,
            objective_fn=objective_map[model_name],
            X=X_train,
            y=y_train,
            n_trials=n_trials,
            timeout=TIMEOUT_SECS,
        )
        if best:
            best_params[model_name] = best

    # ── Save results ──────────────────────────────────────────────────
    if best_params:
        vdir = MODELS_DIR / version
        vdir.mkdir(parents=True, exist_ok=True)
        out_path = vdir / "best_parameters.json"
        with open(out_path, "w") as fh:
            json.dump(best_params, fh, indent=2)
        logger.info("Best parameters saved to %s", out_path)

    return best_params


def load_best_parameters(version: str) -> Dict[str, Dict[str, Any]]:
    """Load previously saved HPO results for a given model version."""
    path = MODELS_DIR / version / "best_parameters.json"
    if not path.exists():
        return {}
    with open(path) as fh:
        return json.load(fh)
