import os
import torch
import tempfile
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer
from backend.training.checkpoint import save_checkpoint, load_checkpoint, inspect_checkpoint

def test_checkpoint_save_and_load_roundtrip():
    config = get_config("neurix-tiny")
    model_orig = NeurixTransformer(config)
    optimizer_orig = torch.optim.AdamW(model_orig.parameters(), lr=1e-3)

    with tempfile.TemporaryDirectory() as tmp_dir:
        save_path = save_checkpoint(
            output_dir=tmp_dir,
            step=10,
            epoch=1,
            model=model_orig,
            optimizer=optimizer_orig,
            scheduler=None,
            model_config=config,
            training_config={},
            metrics={"val_loss": 2.5}
        )

        assert os.path.exists(save_path)

        # Create new instance and load state
        model_loaded = NeurixTransformer(config)
        optimizer_loaded = torch.optim.AdamW(model_loaded.parameters(), lr=1e-3)
        chk = load_checkpoint(save_path, model_loaded, optimizer_loaded)

        assert chk["step"] == 10
        assert chk["epoch"] == 1
        assert chk["metrics"]["val_loss"] == 2.5

        # Verify weights match
        for p1, p2 in zip(model_orig.parameters(), model_loaded.parameters()):
            torch.testing.assert_close(p1, p2)

        info = inspect_checkpoint(save_path)
        assert info["step"] == 10
