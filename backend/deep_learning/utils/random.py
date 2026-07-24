import os
import random
import numpy as np
import torch
import logging

logger = logging.getLogger(__name__)

def seed_everything(seed: int = 42):
    """
    Forces absolute determinism across all libraries.
    """
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        
    # CuDNN settings for reproducibility
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    logger.info(f"Seed perfectly locked to {seed} across Python, Numpy, PyTorch, and CUDA.")
