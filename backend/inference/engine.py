import os
import torch
from typing import Dict, Any, Optional
from backend.models.neurix import NeurixTransformer
from backend.models.config import ModelConfig, get_config
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.inference.generation import GenerationEngine
from backend.training.checkpoint import load_checkpoint

class ProXInferenceEngine:
    def __init__(self, model_name: str = "neurix-100m", checkpoint_path: Optional[str] = None):
        self.config = get_config(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = ProXTokenizer()
        self.model = NeurixTransformer(self.config)

        if checkpoint_path and os.path.exists(checkpoint_path):
            load_checkpoint(checkpoint_path, self.model, device=self.device)
            self.trained = True
        else:
            print(f"[Inference Engine] NO TRAINED CHECKPOINT FOUND for {model_name}. Model is initialized with raw weights.")
            self.trained = False

        self.engine = GenerationEngine(self.model, self.tokenizer, device=self.device)

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return self.engine.generate(prompt, **kwargs)

    def generate_stream(self, prompt: str, **kwargs):
        return self.engine.generate_stream(prompt, **kwargs)
