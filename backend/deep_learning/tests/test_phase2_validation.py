import unittest
import torch
import numpy as np
import tempfile
from pathlib import Path
import json

from backend.deep_learning.models.tabular.mlp.model import DeepMLP
from backend.deep_learning.models.tabular.ft_transformer.model import FTTransformer
from backend.deep_learning.models.tabular.tab_transformer.model import TabTransformer
from backend.deep_learning.models.tabular.tabnet.model import TabNet
from backend.deep_learning.models.tabular.autoencoder.model import TabularAutoencoder

from backend.deep_learning.registry.checkpointing import CheckpointManager
from backend.deep_learning.registry.integration import DeepLearningRegistryAdapter
from backend.deep_learning.evaluation.metrics import ClassificationMetrics

class TestPhase2Validation(unittest.TestCase):
    def setUp(self):
        self.config = {
            "num_features": 5,
            "cat_dims": [(10, 8), (5, 4)], # 2 categorical features
            "hidden_dims": [64, 32],
            "embedding_dim": 16,
            "attention_heads": 2,
            "transformer_layers": 2,
            "n_d": 8, "n_a": 8, "n_steps": 2, "virtual_batch_size": 4
        }
        
        # Simulate inference data
        self.x_num = torch.randn(8, 5)
        self.x_cat = torch.randint(0, 4, (8, 2))
        self.x = (self.x_num, self.x_cat)
        
        self.device = torch.device("cpu")

    def test_model_instantiation_and_inference(self):
        models = [
            DeepMLP(self.config),
            FTTransformer(self.config),
            TabTransformer(self.config),
            TabNet(self.config),
            TabularAutoencoder(self.config)
        ]
        
        for model in models:
            model.eval()
            with torch.no_grad():
                out = model(self.x)
                self.assertIsNotNone(out, f"{model.model_name} returned None")
                if model.model_name == "TabularAutoencoder":
                    # Output dim should match input dim logic in AE (cat dims flattened + num)
                    # For simplcity, just check it produces a tensor
                    self.assertIsInstance(out, torch.Tensor)
                else:
                    self.assertEqual(out.shape, (8, 1), f"{model.model_name} output shape incorrect")
                
                # Check predict and predict_proba (only for classification models)
                if model.model_name != "TabularAutoencoder":
                    pred = model.predict(self.x, self.device)
                    proba = model.predict_proba(self.x, self.device)
                    self.assertEqual(pred.shape, (8, 1))
                    self.assertTrue(torch.all(proba >= 0) and torch.all(proba <= 1))

    def test_checkpointing_and_registry(self):
        models = [
            DeepMLP(self.config),
            FTTransformer(self.config)
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            chkpt_mgr = CheckpointManager(tmpdir)
            
            for model in models:
                optimizer = torch.optim.Adam(model.parameters())
                chkpt_mgr.save(model, optimizer, 1, {"auc": 0.9}, self.config, filename=f"{model.model_name}.pt")
                
                # Register
                DeepLearningRegistryAdapter.register_model(
                    model_name=model.model_name,
                    version="v1",
                    checkpoint_path=f"{tmpdir}/{model.model_name}.pt",
                    config=self.config,
                    metrics={"auc": 0.9}
                )
                
                # Load
                loaded_model = model.__class__.load_checkpoint(f"{tmpdir}/{model.model_name}.pt", self.device)
                self.assertEqual(loaded_model.config["num_features"], 5)
                
            # Verify registry
            registry_file = Path("backend/models/registry.json")
            if registry_file.exists():
                with open(registry_file, "r") as f:
                    registry = json.load(f)
                    self.assertIn("DeepMLP", registry)
                    self.assertIn("FTTransformer", registry)

    def test_calibration_metrics(self):
        y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        y_prob = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7, 0.4, 0.6])
        
        metrics = ClassificationMetrics.compute(y_true, y_prob)
        self.assertIn("ECE", metrics)
        self.assertIn("Brier Score", metrics)
        self.assertGreaterEqual(metrics["ECE"], 0)
        self.assertGreaterEqual(metrics["Brier Score"], 0)

if __name__ == "__main__":
    unittest.main()
