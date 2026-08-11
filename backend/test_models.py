import torch
import pytest
from backend.models.neurix import build_neurix_100m
from backend.models.logix import build_logix_model
from backend.models.optix import build_optix_model
from backend.models.registry import ModelRegistry

def test_neurix_100m_parameter_count():
    model = build_neurix_100m()
    params = model.num_parameters()
    print(f"Neurix 100M total parameters: {params:,}")
    # Verify parameter count is approximately 100 million (between 95M and 105M)
    assert 95_000_000 <= params <= 105_000_000, f"Expected ~100M params, got {params}"

def test_neurix_forward_pass():
    model = build_neurix_100m()
    model.eval()
    input_ids = torch.tensor([[1, 25, 400, 1024]], dtype=torch.long)
    with torch.no_grad():
        logits = model(input_ids)
    assert logits.shape == (1, 4, 32000)

def test_logix_forward_pass():
    model = build_logix_model()
    model.eval()
    input_ids = torch.tensor([[10, 20, 30]], dtype=torch.long)
    with torch.no_grad():
        logits = model(input_ids)
    assert logits.shape == (1, 3, 32000)

def test_optix_forward_pass():
    model = build_optix_model()
    model.eval()
    input_ids = torch.tensor([[5, 15, 25]], dtype=torch.long)
    with torch.no_grad():
        logits = model(input_ids)
    assert logits.shape == (1, 3, 32000)

def test_registry_initialization():
    registry = ModelRegistry()
    models = registry.get_model_info_list()
    assert len(models) == 3
    ids = [m["id"] for m in models]
    assert "neurix" in ids
    assert "logix" in ids
    assert "optix" in ids
