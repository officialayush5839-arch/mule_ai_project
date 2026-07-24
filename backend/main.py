import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import predict, analytics, alerts, copilot
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Pre-loads the InferenceEngine at startup so the first prediction
    request is not slow due to cold-start model loading.
    """
    logger.info("MuleNet AI – starting up. Loading inference engine...")
    try:
        from ml.inference import get_engine
        engine = get_engine()
        status = engine.status()
        if status["model_trained"]:
            logger.info(
                "✅ Inference engine ready | version=%s | PR-AUC=%.4f | threshold=%.3f",
                status.get("model_version", "?"),
                status.get("pr_auc") or 0.0,
                status.get("threshold", 0.5),
            )
        else:
            logger.warning(
                "⚠️  No trained model found. "
                "Run: cd backend && python -m ml.training_pipeline"
            )
    except Exception as exc:
        logger.error("Inference engine startup failed (server still running): %s", exc)

    yield  # Application runs here

    logger.info("MuleNet AI – shutting down.")


app = FastAPI(
    title="MuleNet AI Backend",
    description="Financial Crime Intelligence Platform – Production ML Pipeline & API",
    version="3.0.0",
    lifespan=lifespan,
)

# Configure CORS for local development with the Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(predict.router,    prefix="/api", tags=["Predictive Analytics"])
app.include_router(analytics.router,  prefix="/api", tags=["Data Intelligence"])
app.include_router(alerts.router,     prefix="/api", tags=["Alert Systems"])
app.include_router(copilot.router,    prefix="/api", tags=["AI Copilot Interface"])


@app.get("/")
def read_root():
    from ml.inference import get_engine
    try:
        status = get_engine().status()
    except Exception:
        status = {"model_trained": False}
    return {
        "status":         "HEALTHY",
        "service":        "MuleNet AI Central Engine",
        "version":        "3.0.0",
        "model_trained":  status.get("model_trained", False),
        "model_version":  status.get("model_version"),
        "message":        "IIT Hyderabad Cybersecurity Hackathon Node Active",
    }


@app.get("/api/model/status")
def model_status():
    """Returns the current ML model status and version metadata."""
    from ml.inference import get_engine
    return get_engine().status()


@app.get("/api/model/versions")
def model_versions():
    """Returns all registered model versions."""
    from ml.model_registry import list_versions
    return list_versions()


@app.post("/api/model/train")
async def trigger_training(skip_hpo: bool = True):
    """
    Trigger a new training run using the latest uploaded dataset
    (or synthetic if no dataset has been uploaded).
    Runs with --skip-hpo by default for speed; set skip_hpo=false for full HPO.
    """
    import asyncio, concurrent.futures
    from ml.training_pipeline import run_full_pipeline

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, lambda: run_full_pipeline(skip_hpo=skip_hpo)
        )
    return {"success": True, "result": result}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
