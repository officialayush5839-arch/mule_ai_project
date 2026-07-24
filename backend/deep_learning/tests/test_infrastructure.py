import unittest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import tempfile
from pathlib import Path

from backend.deep_learning.utils.random import seed_everything
from backend.deep_learning.utils.device import get_device
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel
from backend.deep_learning.training.engine import EnterpriseTrainer
from backend.deep_learning.training.callbacks import EarlyStopping, ModelCheckpoint

class DummyModel(EnterpriseBaseModel):
    def __init__(self, config):
        super().__init__(config)
        self.fc = nn.Linear(10, 1)
        
    def forward(self, x):
        return self.fc(x)

class TestDeepLearningInfrastructure(unittest.TestCase):
    
    def test_seed_determinism(self):
        seed_everything(42)
        a = torch.rand(5)
        seed_everything(42)
        b = torch.rand(5)
        self.assertTrue(torch.allclose(a, b), "Random seeds are not deterministic.")

    def test_device_detection(self):
        device = get_device()
        self.assertIsInstance(device, torch.device)

    def test_checkpointing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            model = DummyModel({"hidden_dim": 64})
            path = Path(tmpdir) / "test.pt"
            
            model.save_checkpoint(str(path))
            self.assertTrue(path.exists())
            
            loaded_model = DummyModel.load_checkpoint(str(path), torch.device("cpu"))
            self.assertEqual(loaded_model.config["hidden_dim"], 64)

    def test_training_engine(self):
        model = DummyModel({})
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        criterion = nn.BCEWithLogitsLoss()
        device = torch.device("cpu")
        
        # Create dummy data
        X = torch.randn(100, 10)
        y = torch.randint(0, 2, (100, 1)).float()
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=10)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            callbacks = [
                EarlyStopping(patience=2, min_delta=0.0),
                ModelCheckpoint(save_dir=tmpdir, save_best_only=True)
            ]
            
            trainer = EnterpriseTrainer(
                model=model,
                optimizer=optimizer,
                criterion=criterion,
                device=device,
                callbacks=callbacks
            )
            
            trainer.fit(train_loader=loader, val_loader=loader, epochs=2)
            
            self.assertTrue((Path(tmpdir) / "best_model.pt").exists(), "ModelCheckpoint did not save the best model.")

if __name__ == "__main__":
    unittest.main()
