import os
import time
from typing import List, Dict, Any, Optional
from backend.tokenizer.tokenizer import ProXTokenizer

class TokenizerExperimentHarness:
    def __init__(self, tokenizers: Dict[str, ProXTokenizer]):
        self.tokenizers = tokenizers

    def evaluate_corpus(self, documents: List[str], corpus_name: str = "Evaluation Corpus") -> Dict[str, Any]:
        """Evaluates and compares compression ratio, token counts, and processing speed across tokenizer candidates."""
        total_bytes = sum(len(doc.encode("utf-8")) for doc in documents)
        results = {}

        for name, tok in self.tokenizers.items():
            start_t = time.time()
            total_tokens = 0
            doc_token_counts = []

            for doc in documents:
                tokens = tok.encode(doc)
                cnt = len(tokens)
                total_tokens += cnt
                doc_token_counts.append(cnt)

            elapsed = time.time() - start_t
            tok_per_sec = total_tokens / max(0.0001, elapsed)
            comp_ratio = total_bytes / max(1, total_tokens)
            avg_tok_per_doc = total_tokens / max(1, len(documents))

            results[name] = {
                "vocab_size": tok.vocab_size,
                "total_tokens": total_tokens,
                "total_bytes": total_bytes,
                "compression_ratio_bytes_per_token": round(comp_ratio, 4),
                "avg_tokens_per_doc": round(avg_tok_per_doc, 2),
                "throughput_tokens_sec": round(tok_per_sec, 2),
                "encode_duration_sec": round(elapsed, 4)
            }

        return {
            "corpus_name": corpus_name,
            "document_count": len(documents),
            "total_bytes": total_bytes,
            "tokenizer_comparisons": results
        }

    def print_report(self, eval_results: Dict[str, Any]):
        print("\n" + "="*70)
        print(f"PROX TOKENIZER CANDIDATE COMPARATIVE EVALUATION ({eval_results['corpus_name']})")
        print("="*70)
        print(f"Document Count: {eval_results['document_count']:,} | Total Bytes: {eval_results['total_bytes']:,}")
        print("-"*70)
        for name, res in eval_results["tokenizer_comparisons"].items():
            print(f"Tokenizer: {name:<20} | Vocab: {res['vocab_size']:<6} | Tokens: {res['total_tokens']:<8} | Ratio: {res['compression_ratio_bytes_per_token']:.4f} bytes/tok | Throughput: {res['throughput_tokens_sec']:.1f} tok/s")
        print("="*70 + "\n")
