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
        k_sample = 30
        train_ngrams = [extract_char_ngrams(d) for d in train_docs]
        train_lens = [len(s) for s in train_ngrams]
        index: Dict[int, List[int]] = {}
        for t_idx, t_set in enumerate(train_ngrams):
            gram_hashes = sorted({hash(g) & 0xFFFFFFFF for g in t_set})[:k_sample]
            for h in gram_hashes:
                if h not in index:
                    index[h] = []
                index[h].append(t_idx)

        near_leaks = 0
        for val_doc in val_docs:
            val_ngram = extract_char_ngrams(val_doc)
            vlen = len(val_ngram)
            if vlen == 0:
                continue

            min_len = vlen * self.near_dup_threshold
            max_len = vlen / self.near_dup_threshold

            gram_hashes = sorted({hash(g) & 0xFFFFFFFF for g in val_ngram})[:k_sample]

            candidates: Set[int] = set()
            for h in gram_hashes:
                if h in index:
                    for idx in index[h]:
                        if min_len <= train_lens[idx] <= max_len:
                            candidates.add(idx)

            for c_idx in candidates:
                t_set = train_ngrams[c_idx]
                inter = len(val_ngram & t_set)
                union_len = vlen + train_lens[c_idx] - inter
                if union_len > 0 and (inter / union_len) >= self.near_dup_threshold:
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

def verify_no_leakage(leakage_report: Dict[str, Any], raise_on_leak: bool = True) -> bool:
    """Verifies that no leakage occurred between train and validation splits."""
    if not leakage_report.get("is_clean", True):
        msg = (
            f"DATA LEAKAGE DETECTED: {leakage_report.get('exact_leak_count', 0)} exact leaks and "
            f"{leakage_report.get('near_leak_count', 0)} near-duplicate leaks between train and validation."
        )
        if raise_on_leak:
            raise RuntimeError(msg)
        print(f"[Leakage Checker] WARNING: {msg}")
        return False
    return True

