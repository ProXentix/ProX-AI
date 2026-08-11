from dataclasses import dataclass
import yaml
import os

@dataclass
class TrainingConfig:
    batch_size: int = 1
    gradient_accumulation_steps: int = 16
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    warmup_steps: int = 500
    max_steps: int = 10000
    gradient_clip: float = 1.0
    precision: str = "auto"  # auto, float32, float16, bfloat16
    seed: int = 42

@dataclass
class CheckpointConfig:
    save_every: int = 500
    output_dir: str = "./weights/neurix"

def load_training_config_from_yaml(yaml_path: str):
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data
