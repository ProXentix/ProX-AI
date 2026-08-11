import torch
import pytest
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.inference.generation import GenerationEngine

def test_kv_cache_deterministic_equivalence():
    config = get_config("neurix-tiny")
    model = NeurixTransformer(config)
    tokenizer = ProXTokenizer()

    engine = GenerationEngine(model, tokenizer, device="cpu")
    prompt = "ProX AI KV Cache Deterministic Test String"

    # Deterministic greedy generation (temperature=0.0)
    res_with_cache = engine.generate(prompt, max_new_tokens=20, temperature=0.0, use_kv_cache=True)
    res_without_cache = engine.generate(prompt, max_new_tokens=20, temperature=0.0, use_kv_cache=False)

    assert res_with_cache["text"] == res_without_cache["text"], (
        f"KV cache output mismatched non-cached output:\n"
        f"  With Cache:    {res_with_cache['text']}\n"
        f"  Without Cache: {res_without_cache['text']}"
    )
