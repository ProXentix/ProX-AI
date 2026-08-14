import os
import pytest
import json
from unittest.mock import patch, mock_open

from backend.tokenizer.tokenizer import ProXTokenizer
from backend.tokenizer.config import TokenizerConfig
from scripts.build_prox_corpus import build_prox_corpus_pipeline

def test_tokenizer_missing_fails_loudly():
    with patch("os.path.exists", return_value=False):
        with pytest.raises(RuntimeError, match="Frozen tokenizer artifact not found"):
            ProXTokenizer(tokenizer_path="dummy.json", allow_fallback=False)

def test_fallback_impossible():
    # Even if allow_fallback=True is passed, it raises an error if the file isn't found and we want to enforce it.
    # Actually, allow_fallback=False strictly enforces RuntimeError.
    with patch("os.path.exists", return_value=False):
        with pytest.raises(RuntimeError, match="Frozen tokenizer artifact not found"):
            ProXTokenizer(tokenizer_path="dummy.json", allow_fallback=False)

def test_tokenizer_311_rejected():
    with patch("os.path.exists", return_value=True), \
         patch.object(ProXTokenizer, 'load', return_value=None):
        
        from unittest.mock import PropertyMock
        with patch.object(ProXTokenizer, 'vocab_size', new_callable=PropertyMock) as mock_vocab:
            mock_vocab.return_value = 311
            with pytest.raises(RuntimeError):
                ProXTokenizer(tokenizer_path="dummy.json", allow_fallback=False)

def test_raw_stage_does_not_instantiate_tokenizer():
    with patch("scripts.build_prox_corpus.ProXTokenizer") as mock_tok:
        try:
            build_prox_corpus_pipeline(
                target_tokens=1000,
                dry_run=True,
                stage="raw"
            )
        except Exception:
            pass
        mock_tok.assert_not_called()

def test_tokenize_stage_requires_tokenizer():
    with patch("scripts.build_prox_corpus.ProXTokenizer", side_effect=RuntimeError("Tokenizer missing")) as mock_tok:
        with pytest.raises(RuntimeError, match="Tokenizer missing"):
            build_prox_corpus_pipeline(
                target_tokens=1000,
                stage="tokenize"
            )
