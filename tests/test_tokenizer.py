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
