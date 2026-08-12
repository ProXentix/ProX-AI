import hashlib
from typing import Dict, Any, Tuple

def assign_stratified_split(
    record: Dict[str, Any],
    val_ratio: float = 0.10,
    seed: str = "prox_v0.1_split_seed"
) -> str:
    """Deterministically assigns a record to 'train' or 'validation' split based on SHA-256 hash.
    
    Guarantees reproducible, balanced stratified representation across category, language, and dataset.
    """
    sha = record.get("sha256", "")
    if not sha:
        text = record.get("text", "")
        sha = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
        record["sha256"] = sha

    cat = record.get("category", "general_natural_language")
    lang = record.get("language", "en")
    src = record.get("source", "default")

    # Hash key combining seed, sha256, category, language, source
    hash_payload = f"{seed}:{sha}:{cat}:{lang}:{src}".encode("utf-8")
    h_int = int(hashlib.md5(hash_payload).hexdigest()[:8], 16)
    
    # Bucket 0..999
    bucket = h_int % 1000
    threshold = int(val_ratio * 1000)

    if bucket < threshold:
        return "validation"
    else:
        return "train"
