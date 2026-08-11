from typing import Dict, Any, List
from backend.tokenizer.tokenizer import ProXTokenizer

PROXPL_SYNTAX_SAMPLES = [
    "fn main() { let x: int = 42; println!(\"ProXPL Result: {}\", x); }",
    "pub struct Tensor<T> { data: Vec<T>, shape: Vec<usize> }",
    "impl<T> Tensor<T> { pub fn new(shape: &[usize]) -> Self { Tensor { data: vec![], shape: shape.to_vec() } } }",
    "match result { Ok(val) => val, Err(err) => panic!(\"Error: {}\", err) }",
    "error[E0308]: mismatched types expected `int`, found `string` at line 14:22"
]

def evaluate_proxpl_tokenization(tokenizer: ProXTokenizer) -> Dict[str, Any]:
    """Measures tokenization efficiency and breakdown for ProXPL syntax constructs."""
    results = []
    total_chars = 0
    total_tokens = 0

    for sample in PROXPL_SYNTAX_SAMPLES:
        tokens = tokenizer.encode(sample)
        decoded = [tokenizer.decode([t]) for t in tokens]
        char_count = len(sample)
        tok_count = len(tokens)
        total_chars += char_count
        total_tokens += tok_count

        results.append({
            "sample_snippet": sample,
            "char_count": char_count,
            "token_count": tok_count,
            "chars_per_token": round(char_count / max(1, tok_count), 2),
            "tokens_list": tokens[:10],
            "decoded_tokens_preview": decoded[:10]
        })

    avg_chars_per_tok = total_chars / max(1, total_tokens)

    return {
        "tokenizer_vocab_size": tokenizer.vocab_size,
        "sample_count": len(PROXPL_SYNTAX_SAMPLES),
        "total_chars": total_chars,
        "total_tokens": total_tokens,
        "avg_chars_per_token": round(avg_chars_per_tok, 2),
        "sample_evaluations": results
    }
