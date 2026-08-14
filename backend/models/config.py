from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    name: str = "neurix-100m"
    vocab_size: int = 32000
    d_model: int = 768
    n_layers: int = 12
    n_heads: int = 12
    d_ff: int = 1720
    max_seq_len: int = 2048
    tie_weights: bool = True
    status: str = "INITIALIZED"  # REGISTERED, INITIALIZED, CHECKPOINT_FOUND, LOADED, READY, FAILED

    def __post_init__(self):
        if self.d_model % self.n_heads != 0:
            raise ValueError(
                f"Invalid model config: d_model ({self.d_model}) must be divisible by n_heads ({self.n_heads})"
            )
        if self.head_dim <= 0:
            raise ValueError(f"Invalid head_dim calculated: {self.head_dim}")

    @property
    def head_dim(self) -> int:
        return self.d_model // self.n_heads

PRESET_CONFIGS = {
    "neurix-tiny": ModelConfig(
        name="neurix-tiny",
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=128,
        max_seq_len=128,
        tie_weights=True
    ),
    "neurix-small": ModelConfig(
        name="neurix-small",
        vocab_size=16000,
        d_model=384,
        n_layers=6,
        n_heads=6,
        d_ff=1024,
        max_seq_len=1024,
        tie_weights=True
    ),
    "neurix-100m": ModelConfig(
        name="neurix-100m",
        vocab_size=32000,
        d_model=768,
        n_layers=12,
        n_heads=12,
        d_ff=1720,
        max_seq_len=2048,
        tie_weights=True
    ),
    "logix": ModelConfig(
        name="logix",
        vocab_size=32000,
        d_model=768,
        n_layers=12,
        n_heads=12,
        d_ff=1720,
        max_seq_len=2048,
        tie_weights=True
    ),
    "neurix-1b": ModelConfig(
        name="neurix-1b",
        vocab_size=32000,
        d_model=1792,
        n_layers=24,
        n_heads=14,
        d_ff=4800,
        max_seq_len=4096,
        tie_weights=True
    ),
    "optix": ModelConfig(
        name="optix",
        vocab_size=32000,
        d_model=768,
        n_layers=8,
        n_heads=8,
        d_ff=2048,
        max_seq_len=1024,
        tie_weights=True,
        status="EXPERIMENTAL_NOT_TRAINED"
    ),
}

def get_config(name: str) -> ModelConfig:
    if name in PRESET_CONFIGS:
        return PRESET_CONFIGS[name]
    raise ValueError(f"Unknown model config: {name}. Available configs: {list(PRESET_CONFIGS.keys())}")
