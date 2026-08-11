import os
import asyncio
import torch
import json
import logging
from backend.models.neurix import build_neurix_100m
from backend.models.logix import build_logix_model
from backend.models.optix import build_optix_model
from backend.tokenizer.tokenizer import tokenizer

logger = logging.getLogger(__name__)

WEIGHTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "weights")
os.makedirs(WEIGHTS_DIR, exist_ok=True)

NEURIX_CHECKPOINT_DIR = os.path.join(WEIGHTS_DIR, "neurix")
NEURIX_100M_LEGACY_PATH = os.path.join(WEIGHTS_DIR, "neurix_100m.pt")

class ModelLifecycleState:
    REGISTERED = "REGISTERED"
    INITIALIZED = "INITIALIZED"
    CHECKPOINT_FOUND = "CHECKPOINT_FOUND"
    LOADED = "LOADED"
    READY = "READY"
    FAILED = "FAILED"

class ModelRegistry:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Lazy model instances
        self._neurix_100m = None
        self._logix = None
        self._optix = None

        self.statuses = {
            "neurix": ModelLifecycleState.INITIALIZED,
            "logix": ModelLifecycleState.INITIALIZED,
            "optix": "EXPERIMENTAL_NOT_TRAINED",
        }
        self.checkpoints = {
            "neurix": None,
            "logix": None,
            "optix": None,
        }

        if os.path.exists(NEURIX_100M_LEGACY_PATH):
            self.checkpoints["neurix"] = NEURIX_100M_LEGACY_PATH

    @property
    def neurix_100m(self):
        if self._neurix_100m is None:
            self._neurix_100m = build_neurix_100m().to(self.device)
            if os.path.exists(NEURIX_100M_LEGACY_PATH):
                try:
                    state_dict = torch.load(NEURIX_100M_LEGACY_PATH, map_location=self.device, weights_only=True)
                    self._neurix_100m.load_state_dict(state_dict)
                    self.statuses["neurix"] = ModelLifecycleState.READY
                except Exception as e:
                    print(f"[ProX Engine] Warning: Failed to load legacy checkpoint: {e}")
        return self._neurix_100m

    @property
    def logix(self):
        if self._logix is None:
            self._logix = build_logix_model().to(self.device)
        return self._logix

    @property
    def optix(self):
        if self._optix is None:
            self._optix = build_optix_model().to(self.device)
        return self._optix

    def get_model_info_list(self):
        return [
            {
                "id": "neurix",
                "name": "Neurix 100M",
                "provider": "ProX AI",
                "description": "Decoder-Only Transformer (100.46M parameters, PyTorch). General language modeling.",
                "badge": "100M Params",
                "icon": "Sparkles",
                "parameters": "100.5M",
                "status": self.statuses["neurix"],
                "trained": self.checkpoints["neurix"] is not None,
                "checkpoint": self.checkpoints["neurix"],
                "capabilities": {
                    "vision": False,
                    "webSearch": False,
                    "codeExecution": False,
                    "reasoning": False,
                    "contextWindow": "2048"
                }
            },
            {
                "id": "logix",
                "name": "Logix",
                "provider": "ProX AI",
                "description": "Coding and step-by-step logic model architecture.",
                "badge": "Coding & Logic",
                "icon": "BrainCircuit",
                "parameters": "100.5M",
                "status": self.statuses["logix"],
                "trained": False,
                "checkpoint": None,
                "capabilities": {
                    "vision": False,
                    "webSearch": False,
                    "codeExecution": False,
                    "reasoning": False,
                    "contextWindow": "2048"
                }
            },
            {
                "id": "optix",
                "name": "Optix Vision",
                "provider": "ProX AI",
                "description": "Multimodal Vision Transformer architecture (Experimental, Untrained).",
                "badge": "Vision (Experimental)",
                "icon": "Cpu",
                "parameters": "65M",
                "status": self.statuses["optix"],
                "trained": False,
                "checkpoint": None,
                "capabilities": {
                    "vision": True,
                    "webSearch": False,
                    "codeExecution": False,
                    "reasoning": False,
                    "contextWindow": "1024"
                }
            }
        ]

    async def generate_stream(self, model_id: str, prompt: str, max_new_tokens: int = 80):
        if model_id == "logix":
            model = self.logix.backbone
        elif model_id == "optix":
            model = self.optix.decoder
        else:
            model = self.neurix_100m

        model.eval()
        input_ids = tokenizer.encode(prompt)
        if not input_ids:
            input_ids = [0]

        input_tensor = torch.tensor([input_ids], dtype=torch.long, device=self.device)

        with torch.no_grad():
            curr_tensor = input_tensor
            for _ in range(max_new_tokens):
                if curr_tensor.shape[1] > 1024:
                    curr_tensor = curr_tensor[:, -1024:]

                logits = model(curr_tensor)
                next_token_logits = logits[0, -1, :]
                probs = torch.softmax(next_token_logits / 0.8, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1).item()

                token_text = tokenizer.decode([next_token])
                data = json.dumps({"choices": [{"delta": {"content": token_text}}]})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.02)

                next_tensor = torch.tensor([[next_token]], dtype=torch.long, device=self.device)
                curr_tensor = torch.cat([curr_tensor, next_tensor], dim=1)

        yield "data: [DONE]\n\n"

registry = ModelRegistry()
