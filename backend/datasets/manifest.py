import os
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.datasets.categories import classify_document, get_category_availability, CANONICAL_CATEGORIES
from backend.datasets.quality import DatasetQualityPipeline
from backend.datasets.leakage import DataLeakageChecker
from backend.tokenizer.tokenizer import ProXTokenizer

def compute_dataset_hash(documents: List[str]) -> str:
    h = hashlib.sha256()
    for doc in sorted(documents):
        h.update(doc.strip().encode("utf-8"))
    return h.hexdigest()

class DatasetManifestGenerator:
    def __init__(self, dataset_name: str = "ProX-Corpus-DEV", dataset_version: str = "v0.1"):
        self.dataset_name = dataset_name
        self.dataset_version = dataset_version

    def build_manifest(
        self,
        documents: List[Dict[str, Any]],
        tokenizer: Optional[ProXTokenizer] = None,
        val_ratio: float = 0.1,
        source_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Builds a comprehensive dataset manifest with category stats, token counts, quality filtering, and leakage verification."""
        tokenizer = tokenizer or ProXTokenizer()

        # Quality filtering & deduplication
        quality_pipe = DatasetQualityPipeline()
        filter_res = quality_pipe.filter_and_clean_documents(documents)
        clean_docs = filter_res["clean_documents"]
        doc_records = filter_res["document_records"]

        # Category distribution & token statistics
        cat_docs: Dict[str, List[str]] = {cat: [] for cat in CANONICAL_CATEGORIES}
        cat_tokens: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
        lang_distribution: Dict[str, int] = {}

        for rec in doc_records:
            text = rec["text"]
            cat = rec.get("category") or classify_document(text).value
            lang = rec.get("format", "txt")

            if cat not in cat_docs:
                cat_docs[cat] = []
            cat_docs[cat].append(text)
            tok_count = len(tokenizer.encode(text))
            cat_tokens[cat] = cat_tokens.get(cat, 0) + tok_count
            lang_distribution[lang] = lang_distribution.get(lang, 0) + 1

        category_availability = get_category_availability(cat_docs)
        category_distribution = {}
        for cat in CANONICAL_CATEGORIES:
            category_distribution[cat] = {
                "status": category_availability[cat],
                "document_count": len(cat_docs.get(cat, [])),
                "estimated_tokens": cat_tokens.get(cat, 0),
            }

        # Train / Val Split & Leakage Check
        split_idx = max(1, int(len(clean_docs) * (1 - val_ratio)))
        train_docs = clean_docs[:split_idx]
        val_docs = clean_docs[split_idx:] if split_idx < len(clean_docs) else train_docs

        leakage_checker = DataLeakageChecker()
        leakage_report = leakage_checker.check_leakage(train_docs, val_docs)

        total_tokens = sum(cat_tokens.values())
        ds_hash = compute_dataset_hash(clean_docs)

        manifest = {
            "dataset_name": self.dataset_name,
            "dataset_version": self.dataset_version,
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "dataset_hash": ds_hash,
            "source_identifiers": source_paths or [],
            "summary_statistics": {
                "input_document_count": filter_res["stats"]["input_documents"],
                "clean_document_count": len(clean_docs),
                "total_estimated_tokens": total_tokens,
                "total_byte_size": sum(r["bytes"] for r in doc_records),
                "train_document_count": len(train_docs),
                "val_document_count": len(val_docs),
            },
            "category_distribution": category_distribution,
            "language_distribution": lang_distribution,
            "quality_filtering_statistics": filter_res["stats"],
            "leakage_verification_report": leakage_report,
            "tokenizer_metadata": {
                "tokenizer_identifier": "ProX Tokenizer DEV",
                "tokenizer_hash": "ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1",
                "vocab_size": tokenizer.vocab_size
            }
        }
        return manifest

    def save_manifest(self, manifest: Dict[str, Any], output_path: str = "./dataset_manifest.json") -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"[Dataset Manifest] Manifest saved to {output_path} (Hash: {manifest['dataset_hash'][:16]}...)")
        return output_path
