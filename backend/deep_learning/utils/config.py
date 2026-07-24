import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    """
    Hierarchical Configuration System for Deep Learning experiments.
    """
    @staticmethod
    def load_yaml(filepath: str | Path) -> Dict[str, Any]:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
            
    @staticmethod
    def save_yaml(config: Dict[str, Any], filepath: str | Path):
        with open(filepath, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
