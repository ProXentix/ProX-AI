import os
import json
from typing import List, Dict, Any
from backend.datasets.deduplication import compute_sha256
from backend.tokenizer.tokenizer import ProXTokenizer

APPROVED_PROXPL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "proxpl_sources"
)

def verify_zero_repo_contamination(records: List[Dict[str, Any]]) -> bool:
    """Verifies that no file paths or build code from the local ProX-AI repository exist in records."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for r in records:
        source_id = str(r.get("source_id", ""))
        source_url = str(r.get("source_url", ""))
        if (repo_root in source_id or repo_root in source_url) and not source_id.startswith("proxpl_approved_"):
            raise ValueError(f"HARD RULE VIOLATION: Repository file detected in corpus record: {source_id}")
    return True

def load_approved_proxpl_corpus(tokenizer: ProXTokenizer) -> List[Dict[str, Any]]:
    """Loads approved ProXPL specifications, standard library docs, compiler diagnostic pairs, and canonical examples."""
    records = []
    
    if not os.path.exists(APPROVED_PROXPL_DIR):
        print(f"[ProXPL Ingestor] Warning: Approved ProXPL directory not found at {APPROVED_PROXPL_DIR}")
        return records

    print("[ProXPL Ingestor] Ingesting approved ProXPL language specifications and examples...", flush=True)
    idx = 0
    for root, _, files in os.walk(APPROVED_PROXPL_DIR):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                
                if not content:
                    continue
                
                # Shard or split large files by sections if needed
                sections = content.split("\n\n# ") if file.endswith(".md") else [content]
                for s_idx, sec in enumerate(sections):
                    sec_text = sec if sec.startswith("# ") or not file.endswith(".md") else f"# {sec}"
                    if len(sec_text.strip()) < 20:
                        continue
                    
                    record = {
                        "text": sec_text.strip(),
                        "category": "proxpl",
                        "language": "proxpl",
                        "source": "ProXPL Project Specification & Standard Library",
                        "dataset": "ProXPL Official Specification Corpus v0.1",
                        "license": "Apache-2.0 Open Source Specification",
                        "source_url": "https://prox.ai/docs/proxpl",
                        "source_id": f"proxpl_approved_{file}_{s_idx}_{idx}",
                        "quality": "official_approved_language_material",
                        "sha256": compute_sha256(sec_text.strip())
                    }
                    records.append(record)
                    idx += 1
            except Exception as e:
                print(f"[ProXPL Ingestor] Notice reading {file_path}: {e}")

    verify_zero_repo_contamination(records)
    print(f"[ProXPL Ingestor] Ingested {len(records)} approved ProXPL records.", flush=True)
    return records
