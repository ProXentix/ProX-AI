import torch
import torch.nn as nn
from backend.models.neurix import NeurixTransformer
from backend.models.config import ModelConfig, get_config

class LogixModel(nn.Module):
    """
    Logix Model: Specialized for verifiable step-by-step reasoning, mathematical logic,
    and ProXPL / TypeScript / Python code synthesis.
    """
    def __init__(self, config: ModelConfig = None):
        super().__init__()
        if config is None:
            config = get_config("logix")
        self.config = config
        self.backbone = NeurixTransformer(config)
        self.reasoning_head = nn.Linear(config.d_model, 2)  # Binary verification score (Valid / Invalid)

    def forward(self, input_ids: torch.Tensor, kv_caches=None, start_pos: int = 0):
        logits = self.backbone(input_ids, kv_caches=kv_caches, start_pos=start_pos)
        return logits

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

def build_logix_model() -> LogixModel:
    return LogixModel()
