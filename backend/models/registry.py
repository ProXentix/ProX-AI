import os
import asyncio
import torch
import json
import logging
from backend.models.neurix import build_neurix_100m
from backend.models.logix import build_logix_model
from backend.models.optix import build_optix_model
from backend.tokenizer.tokenizer import tokenizer
from backend.inference.generation import GenerationEngine

logger = logging.getLogger(__name__)

WEIGHTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "weights")
os.makedirs(WEIGHTS_DIR, exist_ok=True)

NEURIX_CHECKPOINT_DIR = os.path.join(WEIGHTS_DIR, "neurix")
NEURIX_100M_LEGACY_PATH = os.path.join(WEIGHTS_DIR, "neurix_100m.pt")

SYSTEM_PROMPT = (
    "You are ProX AI, a general-purpose AI assistant powered by the ProX AI inference stack.\n"
    "Answer the user's actual question directly and naturally.\n"
    "Be concise for simple questions and detailed when complexity requires it.\n"
    "Do not use a fixed response template.\n"
    "Do not automatically produce numbered steps.\n"
    "Do not describe your internal reasoning or claim that you analyzed the user's objective unless that is genuinely relevant.\n"
    "Do not add generic consulting language.\n"
    "Use Markdown only when it improves readability.\n"
    "For greetings, respond naturally.\n"
    "For factual questions, answer directly.\n"
    "For coding questions, provide correct code and explanation when useful.\n"
    "For complex problems, organize the answer logically, but do not force a predefined structure.\n"
    "Never fabricate tool usage, web searches, model capabilities, citations, or actions."
)

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

    async def generate_stream(self, model_id: str, prompt: str, messages: list = None, max_new_tokens: int = 128):
        model_key = model_id.lower()
        if model_key == "logix":
            model = self.logix.backbone
        elif model_key == "optix":
            model = self.optix.decoder
        else:
            model = self.neurix_100m
            model_key = "neurix"

        checkpoint_path = self.checkpoints.get(model_key) or "Baseline (uninitialized weights)"
        backend_name = f"PyTorch ({self.device.type.upper()})"

        prompt_tokens = tokenizer.encode(prompt)
        prompt_token_count = len(prompt_tokens)

        print("\n[ProX Chat]")
        print("Request received")
        print(f"Model selected: {model_key}")
        print(f"Inference backend: {backend_name}")
        print(f"Checkpoint/model loaded: {checkpoint_path}")
        print(f"Prompt tokens: {prompt_token_count}")

        engine = GenerationEngine(model, tokenizer, device=str(self.device))
        generated_token_count = 0

        try:
            for token_text in engine.generate_stream(prompt, max_new_tokens=max_new_tokens):
                generated_token_count += 1
                data = json.dumps({"choices": [{"delta": {"content": token_text}}]})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.01)

            print(f"Generated tokens: {generated_token_count}")
            print("Generation completed\n")
            yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"[ProX Chat] Generation error: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

registry = ModelRegistry()
