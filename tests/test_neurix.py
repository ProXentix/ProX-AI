import torch
import pytest
from backend.models.neurix import build_neurix_100m, NeurixTransformer
from backend.models.config import get_config, ModelConfig

def test_neurix_100m_exact_parameter_count():
    model = build_neurix_100m()
    params = model.num_parameters()
    # Exact mathematical formula count: 100,461,312 parameters
    assert params == 100_461_312, f"Expected exactly 100,461,312 parameters, got {params}"

def test_neurix_invalid_config_raises():
    with pytest.raises(ValueError):
        ModelConfig(d_model=768, n_heads=7)  # 768 % 7 != 0

def test_neurix_forward_pass_shape():
    model = build_neurix_100m()
    model.eval()
    input_ids = torch.tensor([[1, 25, 400, 1024]], dtype=torch.long)
    with torch.no_grad():
        logits = model(input_ids)
    assert logits.shape == (1, 4, 32000)

def test_neurix_causal_attention_masking():
    config = get_config("neurix-tiny")
    model = NeurixTransformer(config)
    model.eval()
    
    # Input sequences sharing the same prefix
    seq_a = torch.tensor([[1, 5, 10, 15]], dtype=torch.long)
    seq_b = torch.tensor([[1, 5, 10, 99]], dtype=torch.long)
    
    with torch.no_grad():
        logits_a = model(seq_a)
        logits_b = model(seq_b)

    # Prefix logits up to index 2 must match exactly due to causal masking
    torch.testing.assert_close(logits_a[:, :3, :], logits_b[:, :3, :])
