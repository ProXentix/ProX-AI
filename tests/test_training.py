import torch
import torch.nn.functional as F
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer

def test_training_step_forward_backward_loss():
    config = get_config("neurix-tiny")
    model = NeurixTransformer(config)
    model.train()

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    x = torch.tensor([[1, 10, 20]], dtype=torch.long)
    y = torch.tensor([[10, 20, 30]], dtype=torch.long)

    logits = model(x)
    loss = F.cross_entropy(logits.view(-1, config.vocab_size), y.view(-1))
    
    optimizer.zero_grad()
    loss.backward()

    # Check gradients exist
    grad_norm = sum(p.grad.norm().item() for p in model.parameters() if p.grad is not None)
    assert grad_norm > 0

    optimizer.step()
    assert loss.item() > 0
