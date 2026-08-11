import pytest
from backend.tokenizer.tokenizer import ProXTokenizer

def test_tokenizer_dev_versioning_and_fallback_enforcement():
    # Loading default tokenizer artifact
    tok = ProXTokenizer(allow_fallback=True)
    assert tok.vocab_size > 0

    # Non-existent tokenizer with allow_fallback=False must raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        ProXTokenizer(tokenizer_path="./non_existent_dir/tokenizer.json", allow_fallback=False)
