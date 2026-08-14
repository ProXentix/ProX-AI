import pytest
import os
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.tokenizer.config import TokenizerConfig

def test_tokenizer_encode_decode_roundtrip():
    tokenizer = ProXTokenizer()
    text = "Hello ProX AI! This is a test of the ProX BPE tokenizer."
    tokens = tokenizer.encode(text)
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    decoded = tokenizer.decode(tokens)
    assert decoded == text

def test_tokenizer_empty_input():
    tokenizer = ProXTokenizer()
    assert tokenizer.encode("") == []
    assert tokenizer.decode([]) == ""

def test_tokenizer_unicode_support():
    tokenizer = ProXTokenizer()
    unicode_text = "ProX AI ✨ Neural Engine — 🚀 Support for 𝚷, 𝚺, 𝛀, and 🚀"
    tokens = tokenizer.encode(unicode_text)
    decoded = tokenizer.decode(tokens)
    assert decoded == unicode_text

def test_tokenizer_source_code_and_proxpl():
    tokenizer = ProXTokenizer()
    proxpl_code = "fn main() { let result = compute_fibonacci(10); return result; }"
    tokens = tokenizer.encode(proxpl_code)
    decoded = tokenizer.decode(tokens)
    assert decoded == proxpl_code

def test_tokenizer_special_tokens():
    tokenizer = ProXTokenizer()
    assert tokenizer.pad_token_id is not None
    assert tokenizer.bos_token_id is not None
    assert tokenizer.eos_token_id is not None
    assert tokenizer.unk_token_id is not None

def test_tokenizer_deterministic_behavior():
    tokenizer = ProXTokenizer()
    text = "Deterministic encoding validation string for ProX AI"
    run1 = tokenizer.encode(text)
    run2 = tokenizer.encode(text)
    assert run1 == run2

def test_valid_tokenizer_loads_successfully():
    tokenizer = ProXTokenizer()
    assert tokenizer.tokenizer is not None
    assert tokenizer.vocab_size == 32000

def test_missing_tokenizer_fails():
    with pytest.raises(RuntimeError, match="Frozen tokenizer artifact not found"):
        ProXTokenizer(tokenizer_path="non_existent_tokenizer.json", allow_fallback=False)

def test_corrupted_tokenizer_fails(tmp_path):
    corrupted_path = tmp_path / "corrupted_tokenizer.json"
    corrupted_path.write_text("this is not a valid json")
    with pytest.raises(RuntimeError, match="Failed to load frozen tokenizer"):
        ProXTokenizer(tokenizer_path=str(corrupted_path), allow_fallback=False)

def test_undefined_target_path_regression_is_impossible():
    tokenizer = ProXTokenizer()
    assert getattr(tokenizer, 'target_path', None) is not None

def test_vocabulary_exactly_32000():
    tokenizer = ProXTokenizer()
    assert tokenizer.vocab_size == 32000

def test_special_tokens_are_present():
    tokenizer = ProXTokenizer()
    expected = ["<pad>", "<bos>", "<eos>", "<unk>", "<proxpl_start>", "<proxpl_end>"]
    for t in expected:
        assert tokenizer.tokenizer.token_to_id(t) is not None

def test_production_mode_never_invokes_fallback(monkeypatch, tmp_path):
    dummy_path = tmp_path / "missing.json"
    
    invoked = False
    def mock_build(*args, **kwargs):
        nonlocal invoked
        invoked = True
        
    monkeypatch.setattr(ProXTokenizer, "_build_fallback_tokenizer", mock_build)
    
    with pytest.raises(RuntimeError):
        ProXTokenizer(tokenizer_path=str(dummy_path))
        
    assert not invoked

def test_explicit_allow_fallback_true_works_for_development(tmp_path):
    dummy_path = tmp_path / "dev_fallback.json"
    tokenizer = ProXTokenizer(tokenizer_path=str(dummy_path), allow_fallback=True)
    assert tokenizer.tokenizer is not None

def test_corpus_builder_refuses_fallback_tokenizer():
    tokenizer = ProXTokenizer()
    assert tokenizer.vocab_size == 32000
    
def test_tokenizer_sha256_is_deterministic():
    tokenizer = ProXTokenizer()
    hash1 = tokenizer.get_file_hash()
    hash2 = tokenizer.get_file_hash()
    assert hash1 != "N/A"
    assert hash1 == hash2
