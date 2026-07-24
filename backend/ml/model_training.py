"""
model_training.py
=================
Multi-model training for MuleNet AI mule-account fraud detection.

Trains the following models and compares them on validation PR-AUC:
  Supervised:
    1. LightGBM           (primary candidate)
    2. XGBoost
    3. CatBoost           (optional, large install)
    4. Random Forest
    5. Extra Trees
    6. Logistic Regression  (baseline)

  Unsupervised (anomaly detection):
    7. Isolation Forest
    8. One-Class SVM

  Ensemble:
    9. Soft-Voting Ensemble weighted by validation PR-AUC
   10. Stacking Ensemble (LR meta-learner)

All supervised models handle class imbalance via:
  - is_unbalance / scale_pos_weight / class_weight
  - SMOTE oversampling (applied to training split only)

The best single model and the ensemble are both persisted.
"""

import logging
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.svm import OneClassSVM

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

RANDOM_SEED = 42


# ─── Optional heavy imports ───────────────────────────────────────────────────
def _import_lightgbm():
    try:
        import lightgbm as lgb
        return lgb
    except ImportError:
        logger.warning("LightGBM not installed – skipping")
        return None


def _import_xgboost():
    try:
        import xgboost as xgb
        return xgb
    except ImportError:
        logger.warning("XGBoost not installed – skipping")
        return None


def _import_catboost():
    try:
        from catboost import CatBoostClassifier
        return CatBoostClassifier
    except ImportError:
        logger.warning("CatBoost not installed – skipping (optional)")
        return None


def _import_smote():
    try:
        from imblearn.over_sampling import SMOTE
        return SMOTE
    except ImportError:
        logger.warning("imbalanced-learn not installed – SMOTE unavailable")
        return None


# ─── Imbalance handling ───────────────────────────────────────────────────────
def apply_smote(
    X_train: np.ndarray,
    y_train: np.ndarray,
    fraud_rate: float,
    seed: int = RANDOM_SEED,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply SMOTE to oversample the minority class on the training set ONLY.
    Only applies if fraud_rate < 10% to avoid over-inflating majority data.
    """
    SMOTE = _import_smote()
    if SMOTE is None or fraud_rate >= 0.10:
        return X_train, y_train

    pos_count = int(y_train.sum())
    if pos_count < 6:
        logger.warning("Too few positive samples for SMOTE (%d). Skipping.", pos_count)
        return X_train, y_train

    k_neighbors = min(5, pos_count - 1)
    sm = SMOTE(random_state=seed, k_neighbors=k_neighbors)
    X_res, y_res = sm.fit_resample(X_train, y_train)
    logger.info(
        "SMOTE: %d → %d samples (positive: %d → %d)",
        len(y_train), len(y_res),
        int(y_train.sum()), int(y_res.sum()),
    )
    return X_res, y_res


# ─── Individual Model Builders ─────────────────────────────────────────────────
def build_lightgbm(n_pos: int, n_neg: int, params: Dict = None) -> Optional[Any]:
    lgb = _import_lightgbm()
    if lgb is None:
        return None
    scale = max(1, n_neg // max(n_pos, 1))
    default = dict(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=scale,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbose=-1,
    )
    if params:
        default.update(params)
    return lgb.LGBMClassifier(**default)


def build_xgboost(n_pos: int, n_neg: int, params: Dict = None) -> Optional[Any]:
    xgb = _import_xgboost()
    if xgb is None:
        return None
    scale = max(1, n_neg // max(n_pos, 1))
    default = dict(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=scale,
        eval_metric="aucpr",
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbosity=0,
        use_label_encoder=False,
    )
    if params:
        default.update(params)
    try:
        return xgb.XGBClassifier(**default)
    except TypeError:
        default.pop("use_label_encoder", None)
        return xgb.XGBClassifier(**default)


def build_catboost(n_pos: int, n_neg: int, params: Dict = None) -> Optional[Any]:
    CatBoostClassifier = _import_catboost()
    if CatBoostClassifier is None:
        return None
    default = dict(
        iterations=500,
        learning_rate=0.05,
        depth=6,
        auto_class_weights="Balanced",
        random_seed=RANDOM_SEED,
        verbose=0,
        allow_writing_files=False,
    )
    if params:
        default.update(params)
    return CatBoostClassifier(**default)


def build_random_forest(n_pos: int, n_neg: int, params: Dict = None) -> Any:
    default = dict(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    if params:
        default.update(params)
    return RandomForestClassifier(**default)


def build_extra_trees(n_pos: int, n_neg: int, params: Dict = None) -> Any:
    default = dict(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    if params:
        default.update(params)
    return ExtraTreesClassifier(**default)


def build_logistic_regression() -> Any:
    return LogisticRegression(
        C=0.1,
        class_weight="balanced",
        solver="lbfgs",
        max_iter=1000,
        random_state=RANDOM_SEED,
    )


def build_isolation_forest(contamination: float = 0.04) -> Any:
    from sklearn.ensemble import IsolationForest
    return IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )


def build_one_class_svm(nu: float = 0.04) -> Any:
    return OneClassSVM(nu=nu, kernel="rbf", gamma="scale")


# ─── Anomaly Model Wrapper ────────────────────────────────────────────────────
class AnomalyModelWrapper:
    """
    Wraps IsolationForest / OneClassSVM to expose predict_proba for
    consistent evaluation.  Scores are normalised to [0, 1].
    """
    def __init__(self, base_model):
        self.base_model = base_model
        self._score_min = 0.0
        self._score_max = 1.0

    def fit(self, X, y=None):
        # Train only on majority (non-fraud) class to model normal behaviour
        if y is not None:
            X_normal = X[y == 0]
        else:
            X_normal = X
        self.base_model.fit(X_normal)
        raw = self.base_model.score_samples(X_normal)
        self._score_min = float(raw.min())
        self._score_max = float(raw.max())
        return self

    def predict_proba(self, X):
        raw = self.base_model.score_samples(X)
        # Anomaly = low score → high fraud probability
        rng = max(self._score_max - self._score_min, 1e-8)
        normalised = (raw - self._score_min) / rng
        anomaly_prob = 1.0 - normalised.clip(0.0, 1.0)
        return np.column_stack([1.0 - anomaly_prob, anomaly_prob])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


# ─── Core Training Routine ────────────────────────────────────────────────────
def train_model(
    name: str,
    model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> Tuple[Any, float]:
    """
    Fit a single model and return (fitted_model, val_pr_auc).
    Handles LightGBM's early stopping transparently.
    """
    try:
        if "lightgbm" in type(model).__module__.lower():
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                callbacks=[
                    __import__("lightgbm").early_stopping(50, verbose=False),
                    __import__("lightgbm").log_evaluation(period=-1),
                ],
            )
        elif "xgboost" in type(model).__module__.lower():
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
        elif "catboost" in type(model).__module__.lower():
            model.fit(
                X_train, y_train,
                eval_set=(X_val, y_val),
                verbose=False,
            )
        else:
            model.fit(X_train, y_train)

        y_prob  = model.predict_proba(X_val)[:, 1]
        pr_auc  = float(average_precision_score(y_val, y_prob))
        logger.info("[%s] val PR-AUC = %.4f", name, pr_auc)
        return model, pr_auc

    except Exception as exc:
        logger.error("[%s] Training failed: %s", name, exc)
        return None, 0.0


# ─── Ensemble Building ────────────────────────────────────────────────────────
def build_soft_voting_ensemble(
    trained_models: Dict[str, Tuple[Any, float]],
    min_pr_auc: float = 0.0,
) -> VotingClassifier:
    """
    Soft-voting ensemble weighted by validation PR-AUC.
    Only models above min_pr_auc are included.
    """
    estimators = []
    weights    = []

    for name, (mdl, pr_auc) in trained_models.items():
        if mdl is None or pr_auc < min_pr_auc:
            continue
        estimators.append((name, mdl))
        weights.append(max(pr_auc, 0.01))

    if not estimators:
        raise ValueError("No valid models available for ensemble.")

    vc = VotingClassifier(
        estimators=estimators,
        voting="soft",
        weights=weights,
        n_jobs=-1,
    )
    # VotingClassifier needs to refit; inject pre-fitted estimators
    vc.estimators_ = [mdl for _, mdl in estimators]
    vc.le_         = __import__("sklearn.preprocessing", fromlist=["LabelEncoder"]).LabelEncoder()
    vc.le_.fit([0, 1])
    vc.classes_    = vc.le_.classes_
    vc.named_estimators_ = {n: m for n, m in estimators}
    return vc


def build_stacking_ensemble(
    trained_models: Dict[str, Tuple[Any, float]],
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> StackingClassifier:
    """
    Stacking ensemble with a calibrated Logistic Regression meta-learner.
    """
    estimators = [
        (name, mdl)
        for name, (mdl, pr_auc) in trained_models.items()
        if mdl is not None and pr_auc > 0.5
    ]
    if len(estimators) < 2:
        raise ValueError("Need at least 2 base models for stacking.")

    meta = CalibratedClassifierCV(
        LogisticRegression(C=1.0, random_state=RANDOM_SEED, max_iter=500),
        method="isotonic",
        cv=3,
    )
    stack = StackingClassifier(
        estimators=estimators,
        final_estimator=meta,
        cv=3,
        n_jobs=-1,
        passthrough=False,
    )
    stack.fit(X_train, y_train)
    return stack


# ─── Main Training Routine ────────────────────────────────────────────────────
def train_all_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    hpo_params: Optional[Dict[str, Dict]] = None,
    build_ensemble: bool = True,
) -> Dict[str, Any]:
    """
    Train all candidate models and optionally build ensembles.

    Parameters
    ----------
    X_train, y_train : training features and labels
    X_val,   y_val   : validation features and labels
    hpo_params       : {model_name → hyperparameter dict} from HPO phase
    build_ensemble   : whether to build voting + stacking ensembles

    Returns
    -------
    {
        "individual": {name: (model, pr_auc)},
        "ensemble": {name: (model, pr_auc)},    # if build_ensemble
        "leaderboard": [...],
    }
    """
    if hpo_params is None:
        hpo_params = {}

    n_pos = int(y_train.sum())
    n_neg = int((y_train == 0).sum())
    fraud_rate = n_pos / max(len(y_train), 1)

    logger.info(
        "Training on %d samples (fraud: %d / %.1f%%  legit: %d)",
        len(y_train), n_pos, fraud_rate * 100, n_neg,
    )

    # SMOTE on training data only
    X_tr_sm, y_tr_sm = apply_smote(X_train, y_train, fraud_rate)

    # ── Build model catalogue ─────────────────────────────────────────
    catalogue = {
        "LightGBM":           build_lightgbm(n_pos, n_neg, hpo_params.get("LightGBM")),
        "XGBoost":            build_xgboost(n_pos, n_neg, hpo_params.get("XGBoost")),
        "CatBoost":           build_catboost(n_pos, n_neg, hpo_params.get("CatBoost")),
        "RandomForest":       build_random_forest(n_pos, n_neg, hpo_params.get("RandomForest")),
        "ExtraTrees":         build_extra_trees(n_pos, n_neg, hpo_params.get("ExtraTrees")),
        "LogisticRegression": build_logistic_regression(),
    }

    # ── Train supervised models ───────────────────────────────────────
    trained: Dict[str, Tuple[Any, float]] = {}
    for name, model in catalogue.items():
        if model is None:
            continue
        fitted, pr_auc = train_model(name, model, X_tr_sm, y_tr_sm, X_val, y_val)
        if fitted is not None:
            trained[name] = (fitted, pr_auc)

    # ── Train anomaly models (on X_train only, no SMOTE) ─────────────
    for name, base_mdl in [
        ("IsolationForest", build_isolation_forest(contamination=fraud_rate)),
        ("OneClassSVM",     build_one_class_svm(nu=min(fraud_rate * 1.5, 0.5))),
    ]:
        wrapper = AnomalyModelWrapper(base_mdl)
        try:
            wrapper.fit(X_train, y_train)
            y_prob  = wrapper.predict_proba(X_val)[:, 1]
            pr_auc  = float(average_precision_score(y_val, y_prob))
            trained[name] = (wrapper, pr_auc)
            logger.info("[%s] val PR-AUC = %.4f", name, pr_auc)
        except Exception as exc:
            logger.error("[%s] failed: %s", name, exc)

    # ── Ensembles ─────────────────────────────────────────────────────
    ensembles: Dict[str, Tuple[Any, float]] = {}
    if build_ensemble and len(trained) >= 2:
        supervised_trained = {
            k: v for k, v in trained.items()
            if k not in ("IsolationForest", "OneClassSVM")
        }

        try:
            vc = build_soft_voting_ensemble(supervised_trained, min_pr_auc=0.5)
            y_prob = vc.predict_proba(X_val)[:, 1]
            vc_auc = float(average_precision_score(y_val, y_prob))
            ensembles["SoftVotingEnsemble"] = (vc, vc_auc)
            logger.info("[SoftVotingEnsemble] val PR-AUC = %.4f", vc_auc)
        except Exception as exc:
            logger.warning("SoftVotingEnsemble failed: %s", exc)

        try:
            stack = build_stacking_ensemble(supervised_trained, X_tr_sm, y_tr_sm)
            y_prob = stack.predict_proba(X_val)[:, 1]
            st_auc = float(average_precision_score(y_val, y_prob))
            ensembles["StackingEnsemble"] = (stack, st_auc)
            logger.info("[StackingEnsemble] val PR-AUC = %.4f", st_auc)
        except Exception as exc:
            logger.warning("StackingEnsemble failed: %s", exc)

    # ── Leaderboard ───────────────────────────────────────────────────
    all_models = {**trained, **ensembles}
    leaderboard = sorted(
        [{"model": k, "val_pr_auc": v[1]} for k, v in all_models.items()],
        key=lambda x: x["val_pr_auc"],
        reverse=True,
    )
    if leaderboard:
        logger.info("Best model: %s (PR-AUC=%.4f)", leaderboard[0]["model"], leaderboard[0]["val_pr_auc"])

    return {
        "individual":  trained,
        "ensembles":   ensembles,
        "leaderboard": leaderboard,
        "best_model_name": leaderboard[0]["model"] if leaderboard else None,
    }
