import hashlib
from typing import List, Dict, Any, Set, Tuple

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

def extract_char_ngrams(text: str, n: int = 5) -> Set[str]:
    clean_text = "".join(text.split()).lower()
    if len(clean_text) < n:
        return {clean_text} if clean_text else set()
    return {clean_text[i:i+n] for i in range(len(clean_text) - n + 1)}

def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / float(union) if union > 0 else 0.0

class DatasetDeduplicator:
    def __init__(self, near_dup_threshold: float = 0.85, ngram_size: int = 5):
        self.near_dup_threshold = near_dup_threshold
        self.ngram_size = ngram_size

    def deduplicate_exact(self, documents: List[str]) -> Dict[str, Any]:
        """Performs exact SHA-256 deduplication."""
        seen = set()
        unique = []
        dup_count = 0

        for doc in documents:
            h = compute_sha256(doc)
            if h in seen:
                dup_count += 1
            else:
                seen.add(h)
                unique.append(doc)

        input_count = len(documents)
        dup_rate = (dup_count / max(1, input_count)) * 100.0

        return {
            "unique_documents": unique,
            "stats": {
                "input_documents": input_count,
                "duplicates_removed": dup_count,
                "remaining_documents": len(unique),
                "duplicate_rate_percent": round(dup_rate, 2),
            }
        }

    def deduplicate_near(self, documents: List[str]) -> Dict[str, Any]:
        """Performs exact SHA-256 followed by near-duplicate n-gram Jaccard filtering."""
        exact_res = self.deduplicate_exact(documents)
        candidate_docs = exact_res["unique_documents"]
        exact_dups = exact_res["stats"]["duplicates_removed"]

        ngram_sets: List[Set[str]] = [extract_char_ngrams(doc, self.ngram_size) for doc in candidate_docs]
        retained: List[str] = []
        retained_sets: List[Set[str]] = []
        retained_lens: List[int] = []
        index: Dict[int, List[int]] = {}
        near_dups_count = 0

        k_sample = 30  # Bottom-K min-hashes per document

        for doc, nset in zip(candidate_docs, ngram_sets):
            nlen = len(nset)
            if nlen == 0:
                retained.append(doc)
                retained_sets.append(nset)
                retained_lens.append(0)
                continue

            min_len = nlen * self.near_dup_threshold
            max_len = nlen / self.near_dup_threshold

            gram_hashes = sorted({hash(g) & 0xFFFFFFFF for g in nset})[:k_sample]

            candidates: Set[int] = set()
            for h in gram_hashes:
                if h in index:
                    for idx in index[h]:
                        if min_len <= retained_lens[idx] <= max_len:
                            candidates.add(idx)

            is_near_dup = False
            for c_idx in candidates:
                rset = retained_sets[c_idx]
                inter = len(nset & rset)
                union_len = nlen + retained_lens[c_idx] - inter
                if union_len > 0 and (inter / union_len) >= self.near_dup_threshold:
                    is_near_dup = True
                    break

            if is_near_dup:
                near_dups_count += 1
            else:
                new_idx = len(retained)
                retained.append(doc)
                retained_sets.append(nset)
                retained_lens.append(nlen)
                for h in gram_hashes:
                    if h not in index:
                        index[h] = []
                    index[h].append(new_idx)

        total_input = len(documents)
        total_removed = exact_dups + near_dups_count
        dup_rate = (total_removed / max(1, total_input)) * 100.0

        return {
            "unique_documents": retained,
            "stats": {
                "input_documents": total_input,
                "exact_duplicates_removed": exact_dups,
                "near_duplicates_removed": near_dups_count,
                "total_duplicates_removed": total_removed,
                "remaining_documents": len(retained),
                "duplicate_rate_percent": round(dup_rate, 2),
                "near_dup_threshold": self.near_dup_threshold
            }
        }
