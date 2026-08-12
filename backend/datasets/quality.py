import ast
import hashlib
import warnings
import unicodedata
import statistics
from typing import List, Dict, Any, Union
from backend.datasets.deduplication import DatasetDeduplicator
from backend.tokenizer.tokenizer import ProXTokenizer

def validate_code_syntax(code: str, language: str = "python") -> Dict[str, Any]:
    """Validates source code syntax where practical (Python AST parse, JS/TS/ProXPL heuristics)."""
    if language in ["python", "py"]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"Python SyntaxError: {e.msg} at line {e.lineno}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    # JS / TS / C / CPP / ProXPL heuristics (unbalanced braces or quotes)
    open_braces = code.count("{") - code.count("}")
    open_parens = code.count("(") - code.count(")")
    if abs(open_braces) > 20 or abs(open_parens) > 20:
        return {"valid": False, "error": "Severely unbalanced syntax delimiters"}

    return {"valid": True, "error": None}

def check_repetition_ratio(text: str, ngram_size: int = 10) -> float:
    """Returns ratio of repeated n-grams in text (0.0 = unique, 1.0 = highly repetitive)."""
    if len(text) < ngram_size * 2:
        return 0.0
    ngrams = [text[i:i+ngram_size] for i in range(len(text) - ngram_size + 1)]
    if not ngrams:
        return 0.0
    unique_ngrams = set(ngrams)
    return 1.0 - (len(unique_ngrams) / float(len(ngrams)))

class DatasetQualityPipeline:
    def __init__(self, min_len: int = 10, max_len: int = 100000, max_repetition: float = 0.5):
        self.min_len = min_len
        self.max_len = max_len
        self.max_repetition = max_repetition
        self.deduplicator = DatasetDeduplicator()

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        # NFC Unicode Normalization & replacement of invalid characters
        text = unicodedata.normalize("NFC", text)
        return text.strip()

    def filter_and_clean_documents(self, documents: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Filters empty documents, invalid length, repetition, and applies exact/near-duplicate deduplication."""
        filtered_empty = 0
        filtered_length = 0
        filtered_repetition = 0
        filtered_syntax = 0

        clean_records = []
        raw_texts = []

        for item in documents:
            if isinstance(item, dict):
                text = item.get("text", "")
                lang = item.get("format", "txt")
            else:
                text = str(item)
                lang = "txt"

            doc_norm = self.normalize_text(text)
            doc_len = len(doc_norm)

            if doc_len == 0:
                filtered_empty += 1
                continue

            if doc_len < self.min_len or doc_len > self.max_len:
                filtered_length += 1
                continue

            rep_ratio = check_repetition_ratio(doc_norm)
            if rep_ratio > self.max_repetition:
                filtered_repetition += 1
                continue

            if lang in ["py", "python"]:
                syntax_res = validate_code_syntax(doc_norm, lang)
                if not syntax_res["valid"]:
                    filtered_syntax += 1
                    continue

            clean_records.append({
                "text": doc_norm,
                "format": lang,
                "bytes": len(doc_norm.encode("utf-8"))
            })
            raw_texts.append(doc_norm)

        # Deduplication step
        dedup_res = self.deduplicator.deduplicate_near(raw_texts)
        retained_texts = set(dedup_res["unique_documents"])

        final_docs = [r for r in clean_records if r["text"] in retained_texts]
        doc_lengths = [len(d["text"]) for d in final_docs] or [0]

        total_input = len(documents)
        return {
            "clean_documents": [d["text"] for d in final_docs],
            "document_records": final_docs,
            "stats": {
                "input_documents": total_input,
                "clean_documents": len(final_docs),
                "filtered_empty": filtered_empty,
                "filtered_length": filtered_length,
                "filtered_repetition": filtered_repetition,
                "filtered_syntax_error": filtered_syntax,
                "exact_duplicates_removed": dedup_res["stats"]["exact_duplicates_removed"],
                "near_duplicates_removed": dedup_res["stats"]["near_duplicates_removed"],
                "total_removed": total_input - len(final_docs),
                "avg_char_length": round(statistics.mean(doc_lengths), 2),
                "median_char_length": statistics.median(doc_lengths),
                "max_char_length": max(doc_lengths),
            }
        }

def analyze_corpus_quality(documents: List[Union[str, Dict[str, Any]]], tokenizer: ProXTokenizer) -> Dict[str, Any]:
    pipeline = DatasetQualityPipeline()
    result = pipeline.filter_and_clean_documents(documents)
    clean_docs = result["clean_documents"]

    total_tokens = sum(len(tokenizer.encode(d)) for d in clean_docs)
    result["stats"]["estimated_total_tokens"] = total_tokens

    print("\n" + "="*60)
    print("DATASET QUALITY & STATISTICAL ANALYSIS")
    print("="*60)
    print(f"Total Input Documents:    {result['stats']['input_documents']:,}")
    print(f"Clean Output Documents:   {result['stats']['clean_documents']:,}")
    print(f"Duplicates Removed:       {result['stats']['exact_duplicates_removed'] + result['stats']['near_duplicates_removed']:,}")
    print(f"Estimated Total Tokens:   {total_tokens:,}")
    print(f"Average Document Length:  {result['stats']['avg_char_length']} chars")
    print("="*60 + "\n")

    return result
