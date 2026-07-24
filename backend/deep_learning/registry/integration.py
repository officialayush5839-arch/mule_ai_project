import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
import torch

logger = logging.getLogger(__name__)

# Assumes the existing backend structure
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
REGISTRY_FILE = MODELS_DIR / "registry.json"

class DeepLearningRegistryAdapter:
    """
    Seamlessly integrates PyTorch models into the Classical ML model registry.
    Ensures that FastAPI endpoints reading registry.json do not crash.
    """
    @staticmethod
    def register_model(
        model_name: str,
        version: str,
        checkpoint_path: str,
        config: dict,
        metrics: dict
    ):
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry to append to it seamlessly
        registry = {}
        if REGISTRY_FILE.exists():
            try:
                with open(REGISTRY_FILE, "r") as f:
                    registry = json.load(f)
            except json.JSONDecodeError:
                pass

        if model_name not in registry:
            registry[model_name] = {"versions": {}}

        registry[model_name]["versions"][version] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model_type": "deep_learning_pytorch", # Distinguishes from joblib
            "artifact_path": str(checkpoint_path),
            "config": config,
            "metrics": metrics,
            "status": "staged"
        }

        # Automatically mark as best version if it's the first
        if "best_version" not in registry[model_name]:
            registry[model_name]["best_version"] = version

        # Save registry
        with open(REGISTRY_FILE, "w") as f:
            json.dump(registry, f, indent=4)
            
        logger.info(f"Registered Deep Learning model '{model_name}' version '{version}' into standard registry.")

    @staticmethod
    def promote_to_production(model_name: str, version: str):
        if not REGISTRY_FILE.exists():
            return
            
        with open(REGISTRY_FILE, "r") as f:
            registry = json.load(f)
            
        if model_name in registry and version in registry[model_name]["versions"]:
            registry[model_name]["best_version"] = version
            registry[model_name]["versions"][version]["status"] = "production"
            
            with open(REGISTRY_FILE, "w") as f:
                json.dump(registry, f, indent=4)
            
            logger.info(f"Promoted {model_name}:{version} to Production.")
