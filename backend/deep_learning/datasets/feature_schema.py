import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class FeatureSchema:
    """
    Strict Feature Schema management to ensure Tabular DL models receive
    features in the exact same order during training and inference.
    """
    def __init__(self, numerical_features: List[str], categorical_features: List[str], target: Optional[str] = None):
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.target = target
        
        # Verify no overlap
        overlap = set(self.numerical_features) & set(self.categorical_features)
        if overlap:
            raise ValueError(f"Features cannot be both numerical and categorical: {overlap}")
            
    def get_all_features(self) -> List[str]:
        return self.numerical_features + self.categorical_features

    def to_dict(self) -> Dict[str, Any]:
        return {
            "numerical_features": self.numerical_features,
            "categorical_features": self.categorical_features,
            "target": self.target
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureSchema':
        return cls(
            numerical_features=data.get("numerical_features", []),
            categorical_features=data.get("categorical_features", []),
            target=data.get("target")
        )

    def save(self, filepath: str | Path):
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
        logger.info(f"Feature schema saved to {filepath}")

    @classmethod
    def load(cls, filepath: str | Path) -> 'FeatureSchema':
        with open(filepath, "r") as f:
            data = json.load(f)
        logger.info(f"Feature schema loaded from {filepath}")
        return cls.from_dict(data)
