import torch
import logging

logger = logging.getLogger(__name__)

def get_device() -> torch.device:
    """
    Automatically detects the best available hardware for execution.
    Prioritizes CUDA, falls back to CPU.
    Future: MPS (Apple Silicon), ROCm.
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Device set to CUDA: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("CUDA not available. Device set to CPU.")
    
    return device
