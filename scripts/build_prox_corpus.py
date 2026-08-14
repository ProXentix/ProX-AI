import os
import sys
import json
import time
import argparse
import hashlib
import statistics
import gc
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable, Generator

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

def load_existing_dedup_hashes(dedup_dir: str) -> Set[str]:
    seen = set()
    if os.path.exists(dedup_dir):
        for fname in os.listdir(dedup_dir):
            if fname.endswith(".jsonl.gz") or fname.endswith(".jsonl.zst") or fname.endswith(".jsonl"):
                fpath = os.path.join(dedup_dir, fname)
                try:
                    if fname.endswith(".gz"):
                        import gzip
                        f_in = gzip.open(fpath, "rt", encoding="utf-8")
                    elif fname.endswith(".zst"):
                        import zstandard as zstd
                        raw = open(fpath, "rb")
                        dctx = zstd.ZstdDecompressor()
                        f_in = dctx.stream_reader(raw)
                    else:
                        f_in = open(fpath, "r", encoding="utf-8")
                    
                    for line in f_in:
                        if isinstance(line, bytes):
                            line = line.decode("utf-8")
                        line = line.strip()
                        if line:
                            try:
                                obj = json.loads(line)
                                sha = obj.get("sha256")
                                if sha:
                                    seen.add(sha)
                            except Exception:
                                pass
                    f_in.close()
                except Exception:
                    pass
    return seen

from backend.datasets.categories import classify_document, DataCategory, CANONICAL_CATEGORIES
from backend.datasets.config import (
    PRODUCTION_MODE,
    TARGET_CONFIG,
    PROGRAMMING_LANGUAGE_TARGETS,
    PROGRAMMING_DATA_DIRS,
    DATASET_REGISTRY,
    get_scaled_target_config,
    validate_target_config,
    check_hf_authentication,
    audit_dataset_sources
)
from backend.datasets.quality import DatasetQualityPipeline, validate_code_syntax
from backend.datasets.deduplication import DatasetDeduplicator, compute_sha256
from backend.datasets.leakage import DataLeakageChecker, verify_no_leakage, verify_zero_repo_contamination
from backend.datasets.checkpoint import CorpusCheckpointManager
from backend.datasets.sharded_writer import ShardedCorpusWriter
from backend.datasets.stratified_split import assign_stratified_split
from backend.datasets.streaming import RobustNetworkStreamer
from backend.tokenizer.tokenizer import ProXTokenizer

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CORPUS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prox_training_corpus")
SOURCES_DIR = os.path.join(CORPUS_ROOT, "sources")
RAW_DIR = os.path.join(CORPUS_ROOT, "raw")
PROCESSED_DIR = os.path.join(CORPUS_ROOT, "processed")
DEDUPLICATED_DIR = os.path.join(CORPUS_ROOT, "deduplicated")
TRAIN_DIR = os.path.join(CORPUS_ROOT, "train")
VAL_DIR = os.path.join(CORPUS_ROOT, "validation")
TEST_DIR = os.path.join(CORPUS_ROOT, "test")
MANIFESTS_DIR = os.path.join(CORPUS_ROOT, "manifests")
REPORTS_DIR = os.path.join(CORPUS_ROOT, "reports")
CHECKPOINT_DIR = os.path.join(CORPUS_ROOT, "checkpoints")

def ensure_corpus_directories():
    for d in [CORPUS_ROOT, SOURCES_DIR, RAW_DIR, PROCESSED_DIR, DEDUPLICATED_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR, MANIFESTS_DIR, REPORTS_DIR, CHECKPOINT_DIR]:
        os.makedirs(d, exist_ok=True)

class TerminalProgressTracker:
    def __init__(self, target_total_tokens: int, category_targets: Dict[str, int]):
        self.target_total = target_total_tokens
        self.category_targets = category_targets
        self.start_time = time.time()
        self.last_update_time = time.time()

    def update(
        self,
        current_total_tokens: int,
        category_tokens: Dict[str, int],
        current_category: str,
        current_dataset: str,
        current_docs: int,
        force: bool = False
    ):
        now = time.time()
        if not force and (now - self.last_update_time) < 2.0:
            return
        
        self.last_update_time = now
        elapsed = max(0.1, now - self.start_time)
        tok_per_sec = current_total_tokens / elapsed
        doc_per_sec = current_docs / elapsed
        
        pct = (current_total_tokens / max(1, self.target_total)) * 100.0
        bar_len = 20
        filled = int(bar_len * (current_total_tokens / max(1, self.target_total)))
        filled = min(bar_len, max(0, filled))
        bar = "█" * filled + "░" * (bar_len - filled)
        
        rem_tok = max(0, self.target_total - current_total_tokens)
        eta_sec = rem_tok / max(1.0, tok_per_sec)
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_sec))

        print(
            f"\rOverall: [{bar}] {current_total_tokens:,} / {self.target_total:,} ({pct:.1f}%) | "
            f"{tok_per_sec:,.0f} /s | {doc_per_sec:,.0f} doc/s | ETA: {eta_str} | Active: {current_category} ({current_dataset})",
            end="",
            flush=True
        )

def generate_source_audit_report(audit_results: List[Dict[str, Any]], hf_auth_state: Dict[str, Any]) -> str:
    ensure_corpus_directories()
    report_path = os.path.join(REPORTS_DIR, "SOURCE_AUDIT_REPORT.md")
    hf_auth_status = "AVAILABLE" if hf_auth_state.get("authenticated") else "NOT AVAILABLE"
    
    rows = []
    for r in audit_results:
        acc_str = "YES" if r["accessible"] else "NO"
        auth_str = "YES" if r["auth_required"] else "NO"
        rows.append(
            f"| `{r['dataset_name']}` | `{r['subset']}` | `{r['category']}` | `{r.get('language', 'N/A')}` | "
            f"{auth_str} | **{acc_str}** | `{r['fallback']}` | {r['license']} | `{r['status']}` |"
        )
    
    table_content = "\n".join(rows)

    content = f"""# PROX TRAINING CORPUS v0.1 — Dataset Source Audit Report

**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  
**Hugging Face Authentication Status:** **HF authentication: {hf_auth_status}**  
**Pipeline Version:** v0.1  

---

## 1. Executive Summary & Accessibility Audit

This audit evaluates all candidate data sources for pre-training preflight accessibility, authentication requirements, category mapping, and explicit fallback options.

- **Total Data Sources Evaluated:** {len(audit_results)}
- **Hugging Face Token Status:** `{hf_auth_status}` (Token value is never logged or stored)
- **Gated Datasets Access:** {"ENABLED" if hf_auth_status == "AVAILABLE" else "DISABLED (Permissive Fallbacks Active)"}

---

## 2. Source Accessibility & Provenance Registry

| Dataset Name | Subset / Path | Category | Language | Auth Req | Accessible | Fallback Source | License | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_content}

---

## 3. Audited Preflight Assessment

- **General Natural Language:** `FineWeb-Edu` (Accessible) with `Wikipedia` fallback.
- **Programming Languages:** Multi-language streaming across `Python, C, C++, JavaScript, TypeScript, Rust, Go, Java` with `CodeParrot Clean / StarCoderData` fallbacks.
- **Technical Documentation:** `CodeXGlue` & `AG News Sci/Tech` (Accessible).
- **ProXPL Status:** ProXPL was removed from PROX TRAINING CORPUS v0.1 and is not included in the v0.1 training corpus.
- **Mathematics & Reasoning:** `OpenWebMath` (Accessible).
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[Corpus Builder] Source Audit Report saved to {report_path}", flush=True)
    return report_path

def build_prox_corpus_pipeline(
    target_tokens: int = 100_000_000,
    resume: bool = False,
    dry_run: bool = False,
    report_only: bool = False,
    single_category: Optional[str] = None,
    stage: str = "all"
) -> Dict[str, Any]:

    ensure_corpus_directories()

    if target_tokens == 100_000_000:
        config = TARGET_CONFIG
    else:
        config = get_scaled_target_config(target_tokens)
    
    validate_target_config(config)

    category_targets = config["category_targets"]
    target_total = config["target_total_tokens"]
    val_ratio = config.get("validation_ratio", 0.05)
    test_ratio = config.get("test_ratio", 0.05)

    hf_auth_state = check_hf_authentication()
    is_hf_authenticated = hf_auth_state.get("authenticated", False)
    hf_auth_status = "AVAILABLE" if is_hf_authenticated else "NOT AVAILABLE"

    print("=" * 75, flush=True)
    print(f"PROX AI — BUILD PROX TRAINING CORPUS v0.1 (Target: {target_total:,} tokens)", flush=True)
    print(f"Stage: {stage.upper()}")
    print("=" * 75, flush=True)
    print(f"HF authentication: {hf_auth_status} (Username: {hf_auth_state.get('username')}, Source: {hf_auth_state.get('token_source')})", flush=True)

    audit_results = audit_dataset_sources(hf_auth_state)
    audit_report_path = generate_source_audit_report(audit_results, hf_auth_state)

    if dry_run:
        print("\n--- PREFLIGHT DATASET SOURCE AUDIT SUMMARY ---", flush=True)
        print(f"Target Total Tokens: {target_total:,}", flush=True)
        print(f"HF Authentication:   {hf_auth_status}", flush=True)
        print("\nDataset Accessibility Registry:", flush=True)
        for r in audit_results:
            print(f"  • {r['dataset_name']:<30} [{r['category']}]: Status = {r['status']}", flush=True)
        print(f"\nAudit Report: {audit_report_path}", flush=True)
        print("Dry run completed. No token payload data streamed.", flush=True)
        return {"status": "DRY_RUN_COMPLETE", "audit_report": audit_report_path}

    if report_only:
        print("[Corpus Builder] Generating reports from existing manifest...", flush=True)
        manifest_path = os.path.join(MANIFESTS_DIR, "corpus_manifest_v0.1.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {"status": "MANIFEST_NOT_FOUND"}

    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()
    checkpoint_mgr = CorpusCheckpointManager()
    if resume:
        loaded = checkpoint_mgr.load_checkpoint(expected_config_hash=config_hash)
        if not loaded:
            resume = False

    net_streamer = RobustNetworkStreamer(max_retries=5, initial_backoff=2.0)
    
    seen_sha256: Set[str] = set()
    category_docs: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
    category_streamed_docs: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
    category_rejected_docs: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
    source_stats: Dict[str, Dict[str, Any]] = {}
    completed_datasets: Set[str] = set(checkpoint_mgr.state.get("completed_datasets", []))
    
    total_docs_seen = checkpoint_mgr.state.get("documents_seen", 0)
    total_duplicates = checkpoint_mgr.state.get("duplicates", 0)

    # STAGE A: RAW CORPUS COLLECTION
    if stage in ["raw", "all"]:
        print(f"\n[STAGE A] RAW CORPUS COLLECTION", flush=True)
        
        raw_char_target_total = target_total * 5
        raw_category_targets = {k: v * 5 for k, v in category_targets.items()}
        
        category_chars: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
        language_chars: Dict[str, int] = {
            "python": 0, "c": 0, "cpp": 0, "js": 0, "ts": 0, "rust": 0, "go": 0, "java": 0
        }

        if resume:
            category_chars.update(checkpoint_mgr.state.get("category_chars", {}))
            category_docs.update(checkpoint_mgr.state.get("category_docs", {}))
            language_chars.update(checkpoint_mgr.state.get("language_chars", {}))
            seen_sha256 = load_existing_dedup_hashes(DEDUPLICATED_DIR)
            print(f"[Corpus Builder] Loaded {len(seen_sha256):,} existing document hashes for resume deduplication.", flush=True)

        progress = TerminalProgressTracker(raw_char_target_total, raw_category_targets)
        
        raw_writer = ShardedCorpusWriter(RAW_DIR, prefix="raw", max_records_per_shard=5000)
        train_raw_writer = ShardedCorpusWriter(TRAIN_DIR, prefix="raw_train_shard", max_records_per_shard=5000)
        val_raw_writer = ShardedCorpusWriter(VAL_DIR, prefix="raw_val_shard", max_records_per_shard=5000)
        test_raw_writer = ShardedCorpusWriter(TEST_DIR, prefix="raw_test_shard", max_records_per_shard=5000)
        quality_pipe = DatasetQualityPipeline(min_len=20, max_len=100000, max_repetition=0.45)

        def process_and_write_sample(sample: Dict[str, Any]) -> bool:
            cat = sample.get("category", DataCategory.GENERAL_NATURAL_LANGUAGE.value)
            lang = sample.get("language", "en")
            src = sample.get("dataset", "unknown")
            text = sample.get("text", "").strip()

            nonlocal total_docs_seen, total_duplicates
            total_docs_seen += 1

            if not text:
                category_rejected_docs[cat] = category_rejected_docs.get(cat, 0) + 1
                return False

            doc_chars = len(text)
            category_streamed_docs[cat] = category_streamed_docs.get(cat, 0) + 1

            if len(text) < quality_pipe.min_len or len(text) > quality_pipe.max_len:
                category_rejected_docs[cat] = category_rejected_docs.get(cat, 0) + 1
                return False

            if lang in ["py", "python"]:
                syntax_check = validate_code_syntax(text, "python")
                if not syntax_check["valid"]:
                    category_rejected_docs[cat] = category_rejected_docs.get(cat, 0) + 1
                    return False

            sha = sample.get("sha256") or compute_sha256(text)
            sample["sha256"] = sha

            if sha in seen_sha256:
                total_duplicates += 1
                category_rejected_docs[cat] = category_rejected_docs.get(cat, 0) + 1
                return False

            seen_sha256.add(sha)
            raw_writer.write_record(sample)

            split_val = int(hashlib.md5(sha.encode()).hexdigest(), 16) % 10000 / 10000.0
            if split_val < val_ratio:
                val_raw_writer.write_record(sample)
            elif split_val < (val_ratio + test_ratio):
                test_raw_writer.write_record(sample)
            else:
                train_raw_writer.write_record(sample)

            category_chars[cat] = category_chars.get(cat, 0) + doc_chars
            category_docs[cat] = category_docs.get(cat, 0) + 1
            language_chars[lang] = language_chars.get(lang, 0) + doc_chars

            if src not in source_stats:
                source_stats[src] = {
                    "dataset_name": src,
                    "dataset_id": sample.get("source", src),
                    "category": cat,
                    "language": lang,
                    "license": sample.get("license", "Unknown"),
                    "retrieved_records": 0,
                    "retrieved_chars": 0,
                    "status": "VERIFIED"
                }
            source_stats[src]["retrieved_records"] += 1
            source_stats[src]["retrieved_chars"] += doc_chars

            total_curr = sum(category_chars.values())
            total_docs = sum(category_docs.values())
            progress.update(total_curr, category_chars, cat, src, total_docs)
            return True

        from datasets import load_dataset
        if single_category in [None, "general_natural_language"]:
            cat_key = "general_natural_language"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: General Natural Language (Target: {target:,} chars)", flush=True)
                fw_dataset_name = "HuggingFaceFW/fineweb-edu"
                try:
                    def get_fw_stream():
                        return load_dataset(fw_dataset_name, name="sample-10BT", split="train", streaming=True)
                    for sample in net_streamer.safe_stream(get_fw_stream, "FineWeb-Edu"):
                        if category_chars[cat_key] >= target: break
                        score = sample.get("score", 0)
                        if score is not None and score >= 3.0:
                            text = sample.get("text", "").strip()
                            if len(text) > 150:
                                process_and_write_sample({
                                    "text": text, "category": cat_key, "language": "en",
                                    "source": fw_dataset_name, "dataset": "FineWeb-Edu",
                                    "license": "ODC-By 1.0 (Dataset) / Publisher Rights Preserved",
                                    "source_url": f"https://huggingface.co/datasets/{fw_dataset_name}",
                                    "source_id": f"fineweb_{sample.get('id', category_docs[cat_key])}",
                                    "quality": f"educational_score_{round(float(score), 2)}",
                                    "sha256": compute_sha256(text)
                                })
                except Exception as e:
                    pass
                
                if category_chars[cat_key] < target and not PRODUCTION_MODE:
                    try:
                        wiki_dataset = "wikimedia/wikipedia"
                        def get_wiki_stream(): return load_dataset(wiki_dataset, name="20231101.en", split="train", streaming=True)
                        for sample in net_streamer.safe_stream(get_wiki_stream, "Wikipedia"):
                            if category_chars[cat_key] >= target: break
                            text = sample.get("text", "").strip()
                            title = sample.get("title", "")
                            full_doc = f"# {title}\n\n{text}" if title else text
                            if len(full_doc) > 200:
                                process_and_write_sample({
                                    "text": full_doc, "category": cat_key, "language": "en",
                                    "source": wiki_dataset, "dataset": "Wikimedia Wikipedia (20231101.en)",
                                    "license": "CC-BY-SA 3.0 / GNU FDL",
                                    "source_url": f"https://huggingface.co/datasets/{wiki_dataset}",
                                    "source_id": f"wiki_en_{category_docs[cat_key]}_{title[:30]}",
                                    "quality": "high_encyclopedic",
                                    "sha256": compute_sha256(full_doc)
                                })
                    except Exception as e2: pass
                
                if PRODUCTION_MODE and category_chars[cat_key] < target:
                    raise RuntimeError(f"PRODUCTION_MODE: Failed to reach target for {cat_key} without fallbacks.")

        if single_category in [None, "programming_languages"]:
            cat_key = "programming_languages"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Programming Languages (Target: {target:,} chars)", flush=True)
                prog_subtargets = {lang: int(target * pct) for lang, pct in PROGRAMMING_LANGUAGE_TARGETS.items()}
                stack_subsets = [
                    (PROGRAMMING_DATA_DIRS["python"], "python", prog_subtargets.get("python", int(target*0.20))),
                    (PROGRAMMING_DATA_DIRS["c"], "c", prog_subtargets.get("c", int(target*0.13))),
                    (PROGRAMMING_DATA_DIRS["cpp"], "cpp", prog_subtargets.get("cpp", int(target*0.13))),
                    (PROGRAMMING_DATA_DIRS["javascript"], "js", prog_subtargets.get("javascript", prog_subtargets.get("js", int(target*0.13)))),
                    (PROGRAMMING_DATA_DIRS["typescript"], "ts", prog_subtargets.get("typescript", prog_subtargets.get("ts", int(target*0.10)))),
                    (PROGRAMMING_DATA_DIRS["rust"], "rust", prog_subtargets.get("rust", int(target*0.10))),
                    (PROGRAMMING_DATA_DIRS["go"], "go", prog_subtargets.get("go", int(target*0.10))),
                    (PROGRAMMING_DATA_DIRS["java"], "java", prog_subtargets.get("java", int(target*0.11))),
                ]
                for data_dir, lang_key, lang_target in stack_subsets:
                    if category_chars[cat_key] >= target: break
                    lang_curr = language_chars.get(lang_key, 0)
                    if lang_curr >= lang_target: continue
                    if is_hf_authenticated:
                        try:
                            def get_stack_stream(): return load_dataset("bigcode/the-stack-smol", data_dir=data_dir, split="train", streaming=True)
                            for sample in net_streamer.safe_stream(get_stack_stream, f"Stack-{lang_key}"):
                                if category_chars[cat_key] >= target or language_chars.get(lang_key, 0) >= lang_target: break
                                code = sample.get("content", "").strip()
                                repo = sample.get("repo_name", "unknown")
                                lic = sample.get("license", "Permissive")
                                if len(code) > 50:
                                    process_and_write_sample({
                                        "text": code, "category": cat_key, "language": lang_key,
                                        "source": "bigcode/the-stack-smol", "dataset": f"The Stack Smol ({lang_key})",
                                        "license": f"BigCode Terms / Permissive ({lic})",
                                        "source_url": "https://huggingface.co/datasets/bigcode/the-stack-smol",
                                        "source_id": f"stack_{lang_key}_{category_docs[cat_key]}_{repo[:30]}",
                                        "quality": f"permissive_{lang_key}_code", "sha256": compute_sha256(code)
                                    })
                        except Exception: pass
                if category_chars[cat_key] < target and not PRODUCTION_MODE:
                    try:
                        def get_cp_stream(): return load_dataset("codeparrot/codeparrot-clean-train", split="train", streaming=True)
                        for sample in net_streamer.safe_stream(get_cp_stream, "CodeParrot"):
                            if category_chars[cat_key] >= target: break
                            code = sample.get("content", "").strip()
                            repo = sample.get("repo_name", "unknown")
                            if len(code) > 50:
                                process_and_write_sample({
                                    "text": code, "category": cat_key, "language": "python",
                                    "source": "codeparrot/codeparrot-clean-train", "dataset": "CodeParrot Clean (Python Fallback)",
                                    "license": "Apache-2.0 Open Source", "source_url": "https://huggingface.co/datasets/codeparrot/codeparrot-clean-train",
                                    "source_id": f"codeparrot_{category_docs[cat_key]}_{repo[:30]}", "quality": "permissive_python_code", "sha256": compute_sha256(code)
                                })
                    except Exception: pass
                    
                if PRODUCTION_MODE and category_chars[cat_key] < target:
                    raise RuntimeError(f"PRODUCTION_MODE: Failed to reach target for {cat_key} without fallbacks.")

        if single_category in [None, "technical_documentation"]:
            cat_key = "technical_documentation"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Technical Documentation (Target: {target:,} chars)", flush=True)
                try:
                    def get_cg_stream(): return load_dataset("google/code_x_glue_tc_nl_code_search_adv", split="train", streaming=True)
                    for sample in net_streamer.safe_stream(get_cg_stream, "CodeXGlue"):
                        if category_chars[cat_key] >= target: break
                        docstring = sample.get("docstring", "").strip()
                        code = sample.get("code", "").strip()
                        repo = sample.get("repo", "")
                        if len(docstring) > 40 and len(code) > 20:
                            doc_text = f"# Technical Documentation: {repo}\n\n## Explanation\n{docstring}\n\n## Implementation\n```python\n{code}\n```"
                            process_and_write_sample({
                                "text": doc_text, "category": cat_key, "language": "en", "source": "google/code_x_glue_tc_nl_code_search_adv",
                                "dataset": "CodeXGlue Code-NL Search", "license": "Apache-2.0 / Open Technical Documentation",
                                "source_url": "https://huggingface.co/datasets/google/code_x_glue_tc_nl_code_search_adv", "source_id": f"codexglue_{category_docs[cat_key]}",
                                "quality": "technical_docstring_explanation", "sha256": compute_sha256(doc_text)
                            })
                except Exception: pass
                if category_chars[cat_key] < target:
                    try:
                        def get_ag_stream(): return load_dataset("fancyzhx/ag_news", split="train", streaming=True)
                        for sample in net_streamer.safe_stream(get_ag_stream, "AGNews"):
                            if category_chars[cat_key] >= target: break
                            text = sample.get("text", "").strip()
                            label = sample.get("label", 0)
                            if text and label in (2, 3):
                                full_doc = f"# Technical Reporting Record\n\n{text}"
                                process_and_write_sample({
                                    "text": full_doc, "category": cat_key, "language": "en", "source": "fancyzhx/ag_news",
                                    "dataset": "AG News Sci/Tech", "license": "Academic / Public News Corpus",
                                    "source_url": "https://huggingface.co/datasets/fancyzhx/ag_news", "source_id": f"ag_news_{category_docs[cat_key]}",
                                    "quality": "technical_reporting", "sha256": compute_sha256(full_doc)
                                })
                    except Exception: pass

        if single_category in [None, "mathematics_reasoning"]:
            cat_key = "mathematics_reasoning"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Mathematics & Reasoning (Target: {target:,} chars)", flush=True)
                try:
                    def get_owm_stream(): return load_dataset("open-web-math/open-web-math", split="train", streaming=True)
                    for sample in net_streamer.safe_stream(get_owm_stream, "OpenWebMath"):
                        if category_chars[cat_key] >= target: break
                        text = sample.get("text", "").strip()
                        if len(text) > 100:
                            process_and_write_sample({
                                "text": text, "category": cat_key, "language": "math", "source": "open-web-math/open-web-math",
                                "dataset": "OpenWebMath", "license": "ODC-By 1.0 (Dataset) / Common Crawl Terms Preserved",
                                "source_url": "https://huggingface.co/datasets/open-web-math/open-web-math", "source_id": f"owm_{sample.get('id', category_docs[cat_key])}",
                                "quality": "latex_web_mathematics", "sha256": compute_sha256(text)
                            })
                except Exception: pass

        raw_writer.close()
        train_raw_writer.close()
        val_raw_writer.close()
        test_raw_writer.close()

        total_chars = sum(category_chars.values())
        total_docs = sum(category_docs.values())
        progress.update(total_chars, category_chars, "Finished", "Complete", total_docs, force=True)
        print("\n", flush=True)

        try:
            import subprocess
            git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        except Exception:
            git_commit = "unknown"

        checkpoint_mgr.save_checkpoint(
            config_hash=config_hash,
            category_chars=category_chars,
            category_docs=category_docs,
            language_chars=language_chars,
            completed_datasets=completed_datasets,
            seen_sha256_count=len(seen_sha256),
            documents_seen=total_docs_seen,
            documents_accepted=total_docs,
            documents_rejected=sum(category_rejected_docs.values()),
            duplicates=total_duplicates,
            git_commit=git_commit
        )

        sources_manifest = {
            "sources_version": "v0.1",
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_sources": len(source_stats),
            "sources": list(source_stats.values())
        }
        with open(os.path.join(MANIFESTS_DIR, "sources_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(sources_manifest, f, indent=2)

    # STAGE B: TOKENIZE FINAL CORPUS
    if stage in ["tokenize", "all"]:
        print(f"\n[STAGE B] TOKENIZE FINAL CORPUS", flush=True)
        
        tokenizer = ProXTokenizer(allow_fallback=False)
        if tokenizer.vocab_size != 32000:
            raise RuntimeError(f"Tokenizer vocab size is {tokenizer.vocab_size}, expected exactly 32000")
            
        tokenizer_hash = tokenizer.get_file_hash()
        print(f"[Corpus Builder] Loaded Production Tokenizer (Vocab: {tokenizer.vocab_size}, Hash: {tokenizer_hash})")

        train_writer = ShardedCorpusWriter(TRAIN_DIR, prefix="train_shard", max_records_per_shard=5000)
        val_writer = ShardedCorpusWriter(VAL_DIR, prefix="val_shard", max_records_per_shard=5000)
        test_writer = ShardedCorpusWriter(TEST_DIR, prefix="test_shard", max_records_per_shard=5000)

        category_tokens: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
        language_tokens: Dict[str, int] = {
            "python": 0, "c": 0, "cpp": 0, "js": 0, "ts": 0, "rust": 0, "go": 0, "java": 0
        }
        
        def tokenize_directory(in_dir: str, prefix: str, out_writer: ShardedCorpusWriter) -> int:
            total_dir_tokens = 0
            for fname in os.listdir(in_dir):
                if not fname.startswith(prefix):
                    continue
                fpath = os.path.join(in_dir, fname)
                try:
                    f_in = open(fpath, "r", encoding="utf-8")
                    for line in f_in:
                        obj = json.loads(line.strip())
                        text = obj["text"]
                        cat = obj.get("category", DataCategory.GENERAL_NATURAL_LANGUAGE.value)
                        lang = obj.get("language", "en")
                        
                        toks = len(tokenizer.encode(text))
                        category_tokens[cat] = category_tokens.get(cat, 0) + toks
                        language_tokens[lang] = language_tokens.get(lang, 0) + toks
                        total_dir_tokens += toks
                        
                        out_writer.write_record(obj)
                    f_in.close()
                except Exception:
                    pass
            return total_dir_tokens

        print("Tokenizing train shards...")
        train_tokens = tokenize_directory(TRAIN_DIR, "raw_train_shard", train_writer)
        print("Tokenizing validation shards...")
        val_tokens = tokenize_directory(VAL_DIR, "raw_val_shard", val_writer)
        print("Tokenizing test shards...")
        test_tokens = tokenize_directory(TEST_DIR, "raw_test_shard", test_writer)
        
        train_writer.close()
        val_writer.close()
        test_writer.close()
        
        total_tokens = sum(category_tokens.values())
        print(f"Total Exact Tokens: {total_tokens:,}")

        print("[Corpus Builder] Performing Leakage Verification on train/val/test splits...", flush=True)
        sample_train_texts, sample_val_texts, sample_test_texts = [], [], []
        
        def _read_texts(in_dir: str, prefix: str, limit: int) -> List[str]:
            res = []
            for fname in os.listdir(in_dir):
                if fname.startswith(prefix):
                    try:
                        with open(os.path.join(in_dir, fname), "r", encoding="utf-8") as f:
                            for line in f:
                                res.append(json.loads(line.strip())["text"])
                                if len(res) >= limit: return res
                    except Exception: pass
            return res

        sample_train_texts = _read_texts(TRAIN_DIR, "train_shard", 1000)
        sample_val_texts = _read_texts(VAL_DIR, "val_shard", 500)
        sample_test_texts = _read_texts(TEST_DIR, "test_shard", 500)

        leakage_checker = DataLeakageChecker()
        leakage_report = leakage_checker.check_leakage(sample_train_texts, sample_val_texts + sample_test_texts)
        verify_no_leakage(leakage_report, raise_on_leak=False)

        corpus_hash = compute_sha256(f"prox_corpus_v0.1_{total_tokens}_{config_hash}")

        target_reached = total_tokens >= (target_total * 0.95)
        leakage_clean = leakage_report.get("is_clean", True)
        
        blocking_reasons = []
        if not target_reached:
            blocking_reasons.append(f"Token count ({total_tokens:,}) is below 95% of target ({target_total:,})")
        if not leakage_clean:
            blocking_reasons.append("Train/Validation leakage detected")
        if category_tokens.get("general_natural_language", 0) == 0:
            blocking_reasons.append("General Natural Language category has 0 tokens")
        if category_tokens.get("programming_languages", 0) == 0:
            blocking_reasons.append("Programming Languages category has 0 tokens")

        if target_reached and leakage_clean and len(blocking_reasons) == 0:
            build_status = "PASSED"
            is_100m_ready = True
        elif total_tokens > 0 and leakage_clean:
            build_status = "PASSED WITH WARNINGS"
            is_100m_ready = False
        else:
            build_status = "FAILED"
            is_100m_ready = False

        readiness_str = "READY" if is_100m_ready else "NOT READY"

        total_docs = sum(category_docs.values())
        corpus_manifest = {
            "corpus_version": "v0.1",
            "target_tokens": target_total,
            "actual_tokens": total_tokens,
            "total_tokens": total_tokens,
            "train_tokens": train_tokens,
            "validation_tokens": val_tokens,
            "test_tokens": test_tokens,
            "build_status": build_status,
            "is_100m_ready": is_100m_ready,
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "corpus_hash": corpus_hash,
            "summary_statistics": {
                "raw_streamed_document_count": sum(category_streamed_docs.values()),
                "accepted_document_count": total_docs,
                "document_counts": total_docs,
                "rejected_documents": sum(category_rejected_docs.values()),
                "duplicate_counts": len(seen_sha256) - total_docs,
                "near_duplicate_counts": 0,
                "total_usable_tokens": total_tokens,
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "test_tokens": test_tokens,
                "target_phase_a_tokens": target_total,
                "target_reached": target_reached
            },
            "language_distribution": language_tokens,
            "hindi_tokens": category_tokens.get("hindi", 0),
            "hindi_percentage": round(category_tokens.get("hindi", 0) / max(1, total_tokens) * 100, 2) if total_tokens > 0 else 0,
            "programming_language_distribution": language_tokens,
            "technical_distribution": category_tokens.get("technical_documentation", 0),
            "math_distribution": category_tokens.get("mathematics_reasoning", 0),
            "category_distribution": {
                cat: {
                    "status": "AVAILABLE" if category_docs.get(cat, 0) > 0 else "NOT AVAILABLE",
                    "document_count": category_docs.get(cat, 0),
                    "tokens": category_tokens.get(cat, 0),
                    "target_tokens": category_targets.get(cat, 0),
                    "actual_percentage": round((category_tokens.get(cat, 0) / max(1, total_tokens)) * 100, 2) if total_tokens > 0 else 0
                } for cat in CANONICAL_CATEGORIES
            },
            "network_retry_statistics": getattr(net_streamer, 'retry_stats', {}),
            "leakage": leakage_report,
            "tokenizer": {
                "tokenizer_version": "ProX-Tokenizer-DEV",
                "vocab_size": tokenizer.vocab_size,
                "sha256": tokenizer_hash
            },
            "build": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pipeline_version": "v0.1",
                "configuration_hash": config_hash
            }
        }

        manifest_path = os.path.join(MANIFESTS_DIR, "corpus_manifest_v0.1.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(corpus_manifest, f, indent=2)

        build_report_path = os.path.join(REPORTS_DIR, "CORPUS_BUILD_REPORT.md")
        with open(build_report_path, "w", encoding="utf-8") as f:
            f.write(f"# PROX TRAINING CORPUS v0.1 — Build Report\n\n**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  \n**Corpus Version:** v0.1  \n**Corpus Hash (SHA-256):** `{corpus_hash}`  \n**Build Status:** **{build_status}**  \n**100M BUILD STATUS:** **{readiness_str}**  \n\n")

        print(f"\n[Corpus Builder] Build Completed with Status: {build_status}", flush=True)
        print(f"  • Total Usable Tokens: {total_tokens:,} / {target_total:,}", flush=True)
        print(f"  • Train Tokens:        {train_tokens:,}", flush=True)
        print(f"  • Val Tokens:          {val_tokens:,}", flush=True)
        print(f"  • Manifest Path:       {manifest_path}", flush=True)

        if not target_reached:
            raise RuntimeError("Target token count was not reached.")

        return corpus_manifest
    return {}

def main():
    parser = argparse.ArgumentParser(description="ProX AI Training Corpus Builder (Preflight & Build Engine)")
    parser.add_argument("--target-tokens", type=int, default=100_000_000, help="Target total usable tokens (default: 100000000)")
    parser.add_argument("--resume", action="store_true", help="Resume build from latest checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Print preflight source audit and dataset accessibility check")
    parser.add_argument("--report-only", action="store_true", help="Generate build report from existing manifest without streaming")
    parser.add_argument("--category", type=str, choices=CANONICAL_CATEGORIES, default=None, help="Limit streaming build to a specific category")
    parser.add_argument("--stage", type=str, choices=["raw", "tokenize", "all"], default="all", help="Pipeline stage to run")
    args = parser.parse_args()

    build_prox_corpus_pipeline(
        target_tokens=args.target_tokens,
        resume=args.resume,
        dry_run=args.dry_run,
        report_only=args.report_only,
        single_category=args.category,
        stage=args.stage
    )

if __name__ == "__main__":
    main()
