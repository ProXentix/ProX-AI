from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.inference.generation import GenerationEngine

def test_generation_output_structure():
    config = get_config("neurix-tiny")
    model = NeurixTransformer(config)
    tokenizer = ProXTokenizer()
    engine = GenerationEngine(model, tokenizer, device="cpu")

    res = engine.generate("Hello world", max_new_tokens=10, temperature=0.7)
    assert "text" in res
    assert "prompt_tokens" in res
    assert "generated_tokens" in res
    assert "latency_seconds" in res
    assert "tokens_per_second" in res
    assert res["generated_tokens"] > 0

def test_generation_stop_sequence():
    config = get_config("neurix-tiny")
    model = NeurixTransformer(config)
    tokenizer = ProXTokenizer()
    engine = GenerationEngine(model, tokenizer, device="cpu")

    res = engine.generate("Function definition:", max_new_tokens=20, stop_sequences=["\n"])
    assert "\n" not in res["text"]
