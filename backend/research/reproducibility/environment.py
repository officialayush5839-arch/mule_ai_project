import platform
import sys
import torch
import subprocess
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EnvironmentTracker:
    """
    Captures complete hardware, software, and configuration metadata 
    to ensure 100% reproducibility of research results.
    """
    @staticmethod
    def get_git_commit() -> str:
        try:
            return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        except Exception:
            return "unknown"

    @staticmethod
    def capture_environment(seed: int, dataset_version: str, config_hash: str) -> Dict[str, Any]:
        logger.info("Capturing research environment for reproducibility...")
        
        env_meta = {
            "os": platform.system() + " " + platform.release(),
            "python_version": sys.version.split('\n')[0],
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "git_commit": EnvironmentTracker.get_git_commit(),
            "random_seed": seed,
            "dataset_version": dataset_version,
            "experiment_config_hash": config_hash
        }
        
        if env_meta["cuda_available"]:
            env_meta["cuda_version"] = torch.version.cuda
            env_meta["cudnn_version"] = torch.backends.cudnn.version()
            env_meta["gpu_name"] = torch.cuda.get_device_name(0)
            
        return env_meta
