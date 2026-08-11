from backend.tokenizer.tokenizer import ProXTokenizer
from backend.tokenizer.proxpl_eval import evaluate_proxpl_tokenization

def test_proxpl_tokenization_evaluation():
    tok = ProXTokenizer()
    eval_res = evaluate_proxpl_tokenization(tok)

    assert eval_res["tokenizer_vocab_size"] > 0
    assert eval_res["sample_count"] > 0
    assert eval_res["total_tokens"] > 0
    assert eval_res["avg_chars_per_token"] > 0.0
    assert len(eval_res["sample_evaluations"]) == eval_res["sample_count"]
