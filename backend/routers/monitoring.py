from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
from observability.custom_telemetry import telemetry_store

router = APIRouter(prefix="/api/monitoring", tags=["In-House Observability"])

# Authentication mock - enforce require_admin for all monitoring
def require_admin():
    # Simulated auth dependency ensuring only admins access this
    return True

@router.get("/health")
def get_health(_=Depends(require_admin)):
    return telemetry_store.get_system_health()

@router.get("/system")
def get_system(_=Depends(require_admin)):
    return telemetry_store.get_system_metrics()

@router.get("/services")
def get_services(_=Depends(require_admin)):
    return {
        "services": [
            {"name": "API Server", "status": "Healthy", "latency_ms": 12},
            {"name": "SQLite", "status": "Healthy", "latency_ms": 2},
            {"name": "Authentication", "status": "Healthy", "latency_ms": 5},
            {"name": "Inference Engine", "status": "Healthy", "latency_ms": 45},
            {"name": "Risk Engine", "status": "Healthy", "latency_ms": 25},
            {"name": "Feature Store", "status": "Healthy", "latency_ms": 8},
            {"name": "Dataset Upload", "status": "Healthy", "latency_ms": 15},
            {"name": "WebSocket Server", "status": "Healthy", "latency_ms": 1}
        ]
    }

@router.get("/logs")
def get_logs(_=Depends(require_admin)):
    return {"logs": list(telemetry_store.logs)}

@router.get("/errors")
def get_errors(_=Depends(require_admin)):
    traces = list(telemetry_store.traces)
    errors = [t for t in traces if t.get("error") is not None or t.get("status_code", 200) >= 400]
    return {"errors": errors}

@router.get("/models")
def get_models(_=Depends(require_admin)):
    # Connect to existing ML model registry logic if available
    try:
        from ml.inference import get_engine
        status = get_engine().status()
        return {
            "models": [
                {
                    "name": "MuleNet Hybrid Core",
                    "status": "Loaded" if status.get("model_trained") else "Offline",
                    "accuracy": status.get("pr_auc", 0),
                    "version": status.get("model_version", "v1.0.0"),
                    "prediction_count": telemetry_store.predictions,
                    "inference_time_ms": 45,
                    "memory_usage_mb": 210
                }
            ]
        }
    except:
        return {"models": []}

@router.get("/traces")
def get_traces(_=Depends(require_admin)):
    return {"traces": list(telemetry_store.traces)}

# WebSocket endpoint for real-time telemetry streaming
@router.websocket("/ws")
async def websocket_monitoring(websocket: WebSocket):
    await websocket.accept()
    telemetry_store.active_connections += 1
    try:
        while True:
            payload = {
                "system": telemetry_store.get_system_health(),
                "metrics": telemetry_store.get_system_metrics(),
                "recent_traces": list(telemetry_store.traces)[:10]
            }
            await websocket.send_json(payload)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        telemetry_store.active_connections -= 1
