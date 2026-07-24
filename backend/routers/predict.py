"""
routers/predict.py
==================
Prediction API router – API contract is UNCHANGED.

Endpoints:
  POST /api/predict        – single-account risk scoring
  POST /api/batch-analyze  – CSV batch analysis

Internally: delegates to InferenceEngine (replaces mock heuristics).
Response schemas are identical to the original implementation.
"""

import io
import logging

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ml.pipeline import calculate_feature_metrics
from ml.inference import get_engine

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Request Schema ───────────────────────────────────────────────────────────
class AccountFeatureInput(BaseModel):
    accountId:  str
    F115:  float = 0.5
    F321:  float = 0.3
    F527:  float = 0.4
    F670:  float = 0.5
    F1692: float = 0.2
    F3043: float = 0.3
    F3894: float = 0.1


# ─── Single Prediction ────────────────────────────────────────────────────────
@router.post("/predict")
def predict_single_account(payload: AccountFeatureInput):
    """
    Real-time risk scoring and SHAP explanation for a single account node.
    Uses the trained ML model via InferenceEngine.
    Response schema is backward-compatible with the original mock implementation.
    """
    features = payload.dict()
    account_id = features.pop("accountId", "UNKNOWN")

    try:
        engine = get_engine()
        result = engine.predict_single(features)

        return {
            "accountId":     account_id,
            "verdict":       result["verdict"],
            "shap":          result["shap"],
            "latency_ms":    result.get("latency_ms", 0.0),
            "model_trained": result.get("model_trained", False),
            "model_version": result.get("model_version", "none"),
        }

    except Exception as exc:
        logger.error("predict_single_account error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        )


# ─── Batch Analysis ───────────────────────────────────────────────────────────
@router.post("/batch-analyze")
async def analyze_batch_csv(file: UploadFile = File(...)):
    """
    Accepts corporate transaction CSV files, runs feature engineering,
    and returns detected mule anomalies.
    Response schema is backward-compatible with the original mock implementation.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV files are supported.",
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        if len(df) == 0:
            raise HTTPException(status_code=400, detail="CSV file is empty.")

        # ── Schema auto-mapping ───────────────────────────────────────
        try:
            from ml.schema_mapper import auto_map_dataframe
            df, mapping_report = auto_map_dataframe(df)
            if mapping_report.get("unmapped"):
                logger.info(
                    "Unmapped columns (ignored): %s", mapping_report["unmapped"]
                )
        except Exception as map_exc:
            logger.warning("Schema mapping failed (continuing with raw columns): %s", map_exc)

        # ── Account ID column ─────────────────────────────────────────
        id_col = next(
            (c for c in df.columns if "id" in c.lower() or "account" in c.lower()),
            None,
        )
        if not id_col:
            df["accountId"] = [f"ACC-UPLOAD-{i:04d}" for i in range(len(df))]
            id_col = "accountId"

        # ── Feature preparation (no random imputation) ────────────────
        pipeline_df = calculate_feature_metrics(df)

        # ── Batch inference via engine ────────────────────────────────
        engine  = get_engine()
        batch_results = engine.predict_batch(pipeline_df)

        # ── Collate response ──────────────────────────────────────────
        results = []
        anomalies_count      = 0
        critical_mules_count = 0
        total_risk           = 0.0

        for i, res in enumerate(batch_results):
            acc_id = str(pipeline_df.iloc[i][id_col]) if id_col in pipeline_df.columns else f"ROW-{i}"
            score  = res.get("riskScore", 0.0)
            cls    = res.get("classification", "SAFE")
            total_risk += score

            is_anomaly = score > 50
            if is_anomaly:
                anomalies_count += 1
                if score > 80:
                    critical_mules_count += 1
                results.append({
                    "id":             acc_id,
                    "riskScore":      score,
                    "classification": cls,
                    "confidence":     res.get("confidence", 0.0),
                    "reason":         f"ML model classification: {cls} (score={score})",
                })

        # ── Drift detection on uploaded data ──────────────────────────
        drift_report = {}
        try:
            from ml.dataset_pipeline import find_latest_version, load_splits, FEATURE_COLS
            from ml.drift_detection import detect_drift

            latest = find_latest_version()
            if latest:
                ref_train, _, _ = load_splits(latest)
                avail_cols = [c for c in FEATURE_COLS if c in pipeline_df.columns]
                if avail_cols:
                    drift_report = detect_drift(ref_train, pipeline_df, feature_cols=avail_cols)
                    summary = drift_report.get("summary", {})
                    if summary.get("recommend_retrain"):
                        logger.warning(
                            "Data drift detected on uploaded CSV. "
                            "Consider retraining via POST /api/model/train"
                        )
        except Exception as drift_exc:
            logger.debug("Drift detection skipped: %s", drift_exc)

        avg_risk = total_risk / max(len(df), 1)

        return {
            "totalUploaded":    len(df),
            "anomaliesDetected":anomalies_count,
            "avgRiskScore":     round(avg_risk, 1),
            "criticalMulesFound": critical_mules_count,
            "anomalousAccounts":  results[:15],   # limit list for UI
            "modelTrained":       engine.status().get("model_trained", False),
            "driftDetected":      drift_report.get("summary", {}).get("overall_drift", False),
            "driftSummary":       drift_report.get("summary", {}),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Batch analysis failed")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CSV file: {str(exc)}",
        )
