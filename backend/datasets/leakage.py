from typing import List, Dict, Any, Set
from backend.datasets.deduplication import compute_sha256, extract_char_ngrams, jaccard_similarity

class DataLeakageChecker:
    def __init__(self, near_dup_threshold: float = 0.85):
        self.near_dup_threshold = near_dup_threshold

    def check_leakage(self, train_docs: List[str], val_docs: List[str]) -> Dict[str, Any]:
        """Checks for exact and near-duplicate document leakage between train and validation splits."""
        train_hashes: Set[str] = {compute_sha256(doc) for doc in train_docs}
        
        exact_leaks = 0
        leaked_hashes = []

        for doc in val_docs:
            h = compute_sha256(doc)
            if h in train_hashes:
                exact_leaks += 1
                leaked_hashes.append(h)

        # Near-duplicate leakage check
        train_ngrams = [extract_char_ngrams(d) for d in train_docs]
        near_leaks = 0

        for val_doc in val_docs:
            val_ngram = extract_char_ngrams(val_doc)
            for t_ngram in train_ngrams:
                sim = jaccard_similarity(val_ngram, t_ngram)
                if sim >= self.near_dup_threshold:
                    near_leaks += 1
                    break

        total_val = len(val_docs)
        leakage_rate = (exact_leaks / max(1, total_val)) * 100.0

        report = {
            "train_document_count": len(train_docs),
            "val_document_count": total_val,
            "exact_leak_count": exact_leaks,
            "near_leak_count": near_leaks,
            "total_leak_count": exact_leaks + near_leaks,
            "leakage_rate_percent": round(leakage_rate, 2),
            "leaked_document_hashes": leaked_hashes[:50],  # cap list for manifest
            "is_clean": (exact_leaks + near_leaks) == 0
        }

        return report
