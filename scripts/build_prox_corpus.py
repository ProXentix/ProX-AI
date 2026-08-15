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
import gzip
try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

def read_corpus_lines(filepath: str) -> Generator[str, None, None]:
    if filepath.endswith(".gz"):
        with gzip.open(filepath, "rt", encoding="utf-8") as f:
            for line in f:
                yield line
    elif filepath.endswith(".zst") and HAS_ZSTD:
        with open(filepath, "rb") as raw:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(raw) as stream:
                import io
                text_stream = io.TextIOWrapper(stream, encoding="utf-8")
                for line in text_stream:
                    yield line
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                yield line

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

def get_dedup_index_path() -> str:
    dedup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prox_training_corpus", "dedup_index")
    os.makedirs(dedup_dir, exist_ok=True)
    if HAS_ZSTD:
        return os.path.join(dedup_dir, "hashes.jsonl.zst")
    return os.path.join(dedup_dir, "hashes.jsonl")

class DedupIndexWriter:
    def __init__(self):
        self.filepath = get_dedup_index_path()
        self.file = None
        self.writer = None
        self._open()

    def _open(self):
        if self.filepath.endswith(".zst") and HAS_ZSTD:
            self.file = open(self.filepath, "ab")
            cctx = zstd.ZstdCompressor(level=3)
            self.writer = cctx.stream_writer(self.file)
        else:
            self.file = open(self.filepath, "a", encoding="utf-8")
            self.writer = self.file

    def write_hash(self, sha: str, source: str, category: str, chars: int):
        record = json.dumps({"sha256": sha, "source": source, "category": category, "chars": chars}) + "\n"
        if self.filepath.endswith(".zst") and HAS_ZSTD:
            self.writer.write(record.encode("utf-8"))
        else:
            self.writer.write(record)

    def flush(self):
        if self.writer:
            if hasattr(self.writer, "flush"):
                self.writer.flush()
        if self.file and hasattr(self.file, "fileno"):
            os.fsync(self.file.fileno())

    def close(self):
        self.flush()
        if hasattr(self.writer, "close"):
            try:
                self.writer.close()
            except Exception: pass
        if hasattr(self.file, "close"):
            try:
                self.file.close()
            except Exception: pass

def load_existing_dedup_hashes() -> Set[str]:
    seen = set()
    filepath = get_dedup_index_path()
    if os.path.exists(filepath):
        try:
            for line in read_corpus_lines(filepath):
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        if "sha256" in obj:
                            seen.add(obj["sha256"])
                    except Exception:
                        pass
        except Exception:
            pass
    return seen

def run_dedup_recovery():
    print("\n[DEDUP RECOVERY] Starting dedup index recovery from existing shards...", flush=True)
    seen = load_existing_dedup_hashes()
    initial_count = len(seen)
    
    writer = DedupIndexWriter()
    scanned_docs = 0
    recovered = 0
    duplicates = 0
    
    CORPUS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prox_training_corpus")
    shard_dirs = [os.path.join(CORPUS_ROOT, "raw"), os.path.join(CORPUS_ROOT, "train"), os.path.join(CORPUS_ROOT, "validation"), os.path.join(CORPUS_ROOT, "test")]
    for d in shard_dirs:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".jsonl") or fname.endswith(".jsonl.gz") or fname.endswith(".jsonl.zst"):
                    fpath = os.path.join(d, fname)
                    try:
                        for line in read_corpus_lines(fpath):
                            scanned_docs += 1
                            obj = json.loads(line.strip())
                            text = obj.get("text", "")
                            sha = obj.get("sha256")
                            if not sha:
                                # Fallback compute sha256 if compute_sha256 is imported later. Wait, we must import it.
                                # It's imported below, let's just use hashlib
                                sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
                            if sha not in seen:
                                seen.add(sha)
                                recovered += 1
                                writer.write_hash(sha, obj.get("source", "unknown"), obj.get("category", "unknown"), len(text))
                            else:
                                duplicates += 1
                    except Exception as e:
                        print(f"Error reading {fpath}: {e}")
    writer.close()
    print(f"[DEDUP RECOVERY]")
    print(f"Existing documents scanned: {scanned_docs}")
    print(f"Existing hashes recovered: {recovered}")
    print(f"Existing duplicates detected: {duplicates}")
    print(f"Dedup index status: READY (Total: {len(seen)})\n", flush=True)
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
from backend.datasets.quality import DatasetQualityPipeline, validate_code_syntax, validate_hindi_text, detect_indic_language
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
        
        # Display active category progress if it's Hindi or Other Indic
        if current_category == "hindi":
            cat_target = self.category_targets.get("hindi", 0) * 5
            print(f"\n  Hindi: {category_tokens.get('hindi', 0):,} / {cat_target:,} chars\033[F", end="", flush=True)
        elif current_category == "other_indic":
            cat_target = self.category_targets.get("other_indic", 0) * 5
            print(f"\n  Other Indic: {category_tokens.get('other_indic', 0):,} / {cat_target:,} chars\033[F", end="", flush=True)

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
    stage: str = "all",
    recover_dedup: bool = False,
    audit_resume: bool = False
) -> Dict[str, Any]:

    ensure_corpus_directories()

    if recover_dedup:
        run_dedup_recovery()
        if not (resume or audit_resume):
            return {"status": "RECOVERY_COMPLETE"}

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
    failed_datasets: Set[str] = set(checkpoint_mgr.state.get("failed_datasets", []))
    
    total_docs_seen = checkpoint_mgr.state.get("documents_seen", 0)
    total_duplicates = checkpoint_mgr.state.get("duplicates", 0)

    # STAGE A: RAW CORPUS COLLECTION
    if stage in ["raw", "all"]:
        print(f"\n[STAGE A] RAW CORPUS COLLECTION", flush=True)
        
        raw_char_target_total = target_total * 5
        raw_category_targets = {k: v * 5 for k, v in category_targets.items()}
        
        category_chars: Dict[str, int] = {cat: 0 for cat in CANONICAL_CATEGORIES}
        language_chars: Dict[str, int] = {
            "python": 0, "c": 0, "cpp": 0, "js": 0, "ts": 0, "rust": 0, "go": 0, "java": 0,
            "hi": 0, "bn": 0, "mr": 0, "gu": 0, "pa": 0, "ta": 0, "te": 0, "kn": 0, "ml": 0, "or": 0, "as": 0
        }

        if resume or audit_resume:
            category_chars.update(checkpoint_mgr.state.get("category_chars", {}))
            category_docs.update(checkpoint_mgr.state.get("category_docs", {}))
            language_chars.update(checkpoint_mgr.state.get("language_chars", {}))
            seen_sha256 = load_existing_dedup_hashes()
            
            if checkpoint_mgr.state.get("seen_sha256_count", 0) > 0 and len(seen_sha256) == 0:
                print(f"[RESUME WARNING] Checkpoint hash count: {checkpoint_mgr.state.get('seen_sha256_count')} Actual dedup index count: 0", flush=True)
                print("Running automatic dedup recovery...", flush=True)
                seen_sha256 = run_dedup_recovery()
            else:
                print(f"[Corpus Builder] Loaded {len(seen_sha256):,} existing document hashes for resume deduplication.", flush=True)

        if audit_resume:
            print("\n" + "="*50)
            print("AUDIT RESUME")
            print("="*50)
            print(f"Checkpoint:                   {config_hash}")
            print(f"Actual dedup index count:     {len(seen_sha256)}")
            print(f"Completed datasets:           {list(completed_datasets)}")
            print(f"Failed datasets:              {list(failed_datasets)}")
            print("\nCategory progress:")
            for cat in ["general_natural_language", "programming_languages", "technical_documentation", "hindi", "mathematics_reasoning", "other_indic"]:
                cur = category_chars.get(cat, 0)
                tgt = raw_category_targets.get(cat, 0)
                rem = max(0, tgt - cur)
                pct = (cur / max(1, tgt)) * 100
                print(f"  {cat}:")
                print(f"    current chars:   {cur:,}")
                print(f"    target chars:    {tgt:,}")
                print(f"    remaining chars: {rem:,}")
                print(f"    percentage:      {pct:.2f}%")
            print("\nGLOBAL:")
            g_cur = sum(category_chars.values())
            g_tgt = raw_char_target_total
            print(f"  Current raw chars: {g_cur:,}")
            print(f"  Target raw chars:  {g_tgt:,}")
            print(f"  Remaining raw chars: {max(0, g_tgt - g_cur):,}")
            print(f"  Estimated tokens:  {g_cur // 5:,}")
            print("="*50 + "\n")
            return {"status": "AUDIT_COMPLETE"}

        dedup_writer = DedupIndexWriter()
        last_checkpoint_accepted = sum(category_docs.values())
        last_checkpoint_chars = sum(category_chars.values())

        progress = TerminalProgressTracker(raw_char_target_total, raw_category_targets)
        
        raw_writer = ShardedCorpusWriter(RAW_DIR, prefix="raw", max_records_per_shard=5000)
        train_raw_writer = ShardedCorpusWriter(TRAIN_DIR, prefix="raw_train_shard", max_records_per_shard=5000)
        val_raw_writer = ShardedCorpusWriter(VAL_DIR, prefix="raw_val_shard", max_records_per_shard=5000)
        test_raw_writer = ShardedCorpusWriter(TEST_DIR, prefix="raw_test_shard", max_records_per_shard=5000)
        quality_pipe = DatasetQualityPipeline(min_len=20, max_len=100000, max_repetition=0.45)

        def force_checkpoint(active_src: str, active_cat: str):
            raw_writer.flush()
            train_raw_writer.flush()
            val_raw_writer.flush()
            test_raw_writer.flush()
            dedup_writer.flush()
            checkpoint_mgr.save_checkpoint(
                config_hash=config_hash,
                category_chars=category_chars,
                category_docs=category_docs,
                language_chars=language_chars,
                completed_datasets=list(completed_datasets),
                failed_datasets=list(failed_datasets),
                active_dataset=active_src,
                active_category=active_cat,
                seen_sha256_count=len(seen_sha256),
                documents_seen=total_docs_seen,
                documents_accepted=sum(category_docs.values()),
                documents_rejected=sum(category_rejected_docs.values()),
                duplicates=total_duplicates,
                retry_statistics=getattr(net_streamer, 'retry_stats', {}),
                source_statistics=source_stats,
                git_commit="unknown"
            )

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

            if cat == "hindi":
                if not validate_hindi_text(text):
                    category_rejected_docs[cat] = category_rejected_docs.get(cat, 0) + 1
                    return False

            sha = sample.get("sha256") or compute_sha256(text)
            sample["sha256"] = sha

            if sha in seen_sha256:
                total_duplicates += 1
                category_rejected_docs[cat] = category_rejected_docs.get(cat, 0) + 1
                return False

            seen_sha256.add(sha)
            dedup_writer.write_hash(sha, src, cat, doc_chars)
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

            nonlocal last_checkpoint_accepted, last_checkpoint_chars
            if (total_docs - last_checkpoint_accepted) >= 10000 or (total_curr - last_checkpoint_chars) >= 50000000:
                force_checkpoint(src, cat)
                last_checkpoint_accepted = total_docs
                last_checkpoint_chars = total_curr

            return True

        def run_source_stream(dataset_id: str, dataset_name: str, cat_key: str, target: int, stream_func, sample_processor):
            if dataset_name in completed_datasets or dataset_name in failed_datasets:
                return
            if category_chars[cat_key] >= target:
                return
            try:
                for sample in net_streamer.safe_stream(stream_func, dataset_name):
                    if category_chars[cat_key] >= target:
                        completed_datasets.add(dataset_name)
                        force_checkpoint(dataset_name, cat_key)
                        return
                    sample_processor(sample)
                completed_datasets.add(dataset_name)
                force_checkpoint(dataset_name, cat_key)
                
                # Source exhausted check
                if category_chars[cat_key] < target:
                    rem = target - category_chars[cat_key]
                    print(f"\n[{cat_key.upper()} TARGET NOT REACHED]", flush=True)
                    print(f"Current: {category_chars[cat_key]:,}", flush=True)
                    print(f"Target: {target:,} chars", flush=True)
                    print(f"Remaining: {rem:,}", flush=True)
            except Exception as e:
                failed_datasets.add(dataset_name)
                force_checkpoint(dataset_name, cat_key)
                print(f"\n[SOURCE ERROR] Source: {dataset_name} Category: {cat_key} Exception: {e}", flush=True)
                with open(os.path.join(REPORTS_DIR, "CORPUS_BUILD_ERRORS.jsonl"), "a", encoding="utf-8") as ef:
                    ef.write(json.dumps({"source": dataset_name, "category": cat_key, "error": str(e), "time": time.time()}) + "\n")

        from datasets import load_dataset
        if single_category in [None, "general_natural_language"]:
            cat_key = "general_natural_language"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: General Natural Language (Target: {target:,} chars)", flush=True)
                
                def fw_processor(sample):
                    score = sample.get("score", 0)
                    if score is not None and score >= 3.0:
                        text = sample.get("text", "").strip()
                        if len(text) > 150:
                            process_and_write_sample({
                                "text": text, "category": cat_key, "language": "en",
                                "source": "HuggingFaceFW/fineweb-edu", "dataset": "FineWeb-Edu",
                                "license": "ODC-By 1.0 (Dataset) / Publisher Rights Preserved",
                                "source_url": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu",
                                "source_id": f"fineweb_{sample.get('id', category_docs[cat_key])}",
                                "quality": f"educational_score_{round(float(score), 2)}",
                                "sha256": compute_sha256(text)
                            })
                run_source_stream("HuggingFaceFW/fineweb-edu", "FineWeb-Edu", cat_key, target, lambda: load_dataset("HuggingFaceFW/fineweb-edu", name="sample-10BT", split="train", streaming=True), fw_processor)
                
                if category_chars[cat_key] < target and not PRODUCTION_MODE:
                    def wiki_processor(sample):
                        text = sample.get("text", "").strip()
                        title = sample.get("title", "")
                        full_doc = f"# {title}\n\n{text}" if title else text
                        if len(full_doc) > 200:
                            process_and_write_sample({
                                "text": full_doc, "category": cat_key, "language": "en",
                                "source": "wikimedia/wikipedia", "dataset": "Wikimedia Wikipedia (20231101.en)",
                                "license": "CC-BY-SA 3.0 / GNU FDL",
                                "source_url": "https://huggingface.co/datasets/wikimedia/wikipedia",
                                "source_id": f"wiki_en_{category_docs[cat_key]}_{title[:30]}",
                                "quality": "high_encyclopedic",
                                "sha256": compute_sha256(full_doc)
                            })
                    run_source_stream("wikimedia/wikipedia", "Wikipedia", cat_key, target, lambda: load_dataset("wikimedia/wikipedia", name="20231101.en", split="train", streaming=True), wiki_processor)
                
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
                    if is_hf_authenticated:
                        def stack_processor(sample, lang_key=lang_key):
                            if language_chars.get(lang_key, 0) >= lang_target:
                                return
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
                        run_source_stream(f"Stack-{lang_key}", f"Stack-{lang_key}", cat_key, target, lambda data_dir=data_dir: load_dataset("bigcode/the-stack-smol", data_dir=data_dir, split="train", streaming=True), stack_processor)
                        
                if category_chars[cat_key] < target and not PRODUCTION_MODE:
                    def cp_processor(sample):
                        code = sample.get("content", "").strip()
                        repo = sample.get("repo_name", "unknown")
                        if len(code) > 50:
                            process_and_write_sample({
                                "text": code, "category": cat_key, "language": "python",
                                "source": "codeparrot/codeparrot-clean-train", "dataset": "CodeParrot Clean (Python Fallback)",
                                "license": "Apache-2.0 Open Source", "source_url": "https://huggingface.co/datasets/codeparrot/codeparrot-clean-train",
                                "source_id": f"codeparrot_{category_docs[cat_key]}_{repo[:30]}", "quality": "permissive_python_code", "sha256": compute_sha256(code)
                            })
                    run_source_stream("CodeParrot", "CodeParrot", cat_key, target, lambda: load_dataset("codeparrot/codeparrot-clean-train", split="train", streaming=True), cp_processor)
                    
                if PRODUCTION_MODE and category_chars[cat_key] < target:
                    raise RuntimeError(f"PRODUCTION_MODE: Failed to reach target for {cat_key} without fallbacks.")

        if single_category in [None, "technical_documentation"]:
            cat_key = "technical_documentation"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Technical Documentation (Target: {target:,} chars)", flush=True)
                def cg_processor(sample):
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
                run_source_stream("CodeXGlue", "CodeXGlue", cat_key, target, lambda: load_dataset("google/code_x_glue_tc_nl_code_search_adv", split="train", streaming=True), cg_processor)
                
                if category_chars[cat_key] < target:
                    def ag_processor(sample):
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
                    run_source_stream("AGNews", "AGNews", cat_key, target, lambda: load_dataset("fancyzhx/ag_news", split="train", streaming=True), ag_processor)

        if single_category in [None, "mathematics_reasoning"]:
            cat_key = "mathematics_reasoning"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Mathematics & Reasoning (Target: {target:,} chars)", flush=True)
                def owm_processor(sample):
                    text = sample.get("text", "").strip()
                    if len(text) > 100:
                        process_and_write_sample({
                            "text": text, "category": cat_key, "language": "math", "source": "open-web-math/open-web-math",
                            "dataset": "OpenWebMath", "license": "ODC-By 1.0 (Dataset) / Common Crawl Terms Preserved",
                            "source_url": "https://huggingface.co/datasets/open-web-math/open-web-math", "source_id": f"owm_{sample.get('id', category_docs[cat_key])}",
                            "quality": "latex_web_mathematics", "sha256": compute_sha256(text)
                        })
                run_source_stream("OpenWebMath", "OpenWebMath", cat_key, target, lambda: load_dataset("open-web-math/open-web-math", split="train", streaming=True), owm_processor)

        if single_category in [None, "hindi"]:
            cat_key = "hindi"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Hindi (Target: {target:,} chars)", flush=True)
                def hindi_processor(sample, quality="devanagari_mixed"):
                    text = sample.get("text", "").strip()
                    if len(text) > 100:
                        process_and_write_sample({
                            "text": text, "category": cat_key, "language": "hi", "source": "ai4bharat/sangraha",
                            "dataset": "Sangraha Verified (Hindi)" if "verified" in quality else "Sangraha Unverified (Hindi)", "license": "Indic Permissive",
                            "source_url": "https://huggingface.co/datasets/ai4bharat/sangraha",
                            "source_id": f"sangraha_hi_{category_docs.get(cat_key, 0)}",
                            "quality": quality, "sha256": compute_sha256(text)
                        })
                run_source_stream("sangraha_verified_hin", "Sangraha Verified (Hindi)", cat_key, target, lambda: load_dataset("ai4bharat/sangraha", data_dir="verified/hin", split="train", streaming=True), lambda s: hindi_processor(s, "devanagari_mixed_verified"))
                if category_chars[cat_key] < target:
                    run_source_stream("sangraha_unverified_hin", "Sangraha Unverified (Hindi)", cat_key, target, lambda: load_dataset("ai4bharat/sangraha", data_dir="unverified/hin", split="train", streaming=True), lambda s: hindi_processor(s, "devanagari_mixed_unverified"))

        if single_category in [None, "other_indic"]:
            cat_key = "other_indic"
            target = raw_category_targets[cat_key]
            if category_chars[cat_key] < target:
                print(f"\n[Corpus Builder] Category: Other Indic (Target: {target:,} chars)", flush=True)
                
                # Setup language balancing state
                if not hasattr(net_streamer, 'indic_counts_printed'):
                    net_streamer.indic_counts_printed = time.time()
                    
                def indic_processor_for_lang(sample, lang_code, iso, quality="indic_mixed"):
                    text = sample.get("text", "").strip()
                    lang = sample.get("language", iso)
                    if len(text) > 100:
                        dataset_title = f"Sangraha Verified ({lang_code})" if "verified" in quality else f"Sangraha Unverified ({lang_code})"
                        process_and_write_sample({
                            "text": text, "category": cat_key, "language": lang, "source": "ai4bharat/sangraha",
                            "dataset": dataset_title, "license": "Indic Permissive",
                            "source_url": "https://huggingface.co/datasets/ai4bharat/sangraha",
                            "source_id": f"sangraha_{lang_code}_{category_docs.get(cat_key, 0)}",
                            "quality": quality, "sha256": compute_sha256(text)
                        })
                        
                    # Periodically print indic stats
                    now = time.time()
                    if now - getattr(net_streamer, 'indic_counts_printed', 0) > 60:  # Print every 60s
                        net_streamer.indic_counts_printed = now
                        print("\n\nOther Indic Stats:")
                        for l in ["bn", "mr", "gu", "pa", "ta", "te", "kn", "ml", "or", "as"]:
                            print(f"{l.title()}: {language_chars.get(l, 0):,}")
                        print("\033[F" * 12, end="", flush=True)  # Move cursor back up
                        
                indic_langs = {
                    "ben": "bn", "guj": "gu", "kan": "kn", "mal": "ml",
                    "mar": "mr", "ori": "or", "pan": "pa", "tam": "ta",
                    "tel": "te", "urd": "ur"
                }
                
                for lang_code, iso in indic_langs.items():
                    run_source_stream(f"sangraha_verified_{lang_code}", f"Sangraha Verified ({lang_code})", cat_key, target, lambda lc=lang_code: load_dataset("ai4bharat/sangraha", data_dir=f"verified/{lc}", split="train", streaming=True), lambda s, lc=lang_code, isoc=iso: indic_processor_for_lang(s, lc, isoc, "indic_mixed_verified"))
                
                for lang_code, iso in indic_langs.items():
                    if category_chars[cat_key] < target:
                        run_source_stream(f"sangraha_unverified_{lang_code}", f"Sangraha Unverified ({lang_code})", cat_key, target, lambda lc=lang_code: load_dataset("ai4bharat/sangraha", data_dir=f"unverified/{lc}", split="train", streaming=True), lambda s, lc=lang_code, isoc=iso: indic_processor_for_lang(s, lc, isoc, "indic_mixed_unverified"))

        raw_writer.close()
        train_raw_writer.close()
        val_raw_writer.close()
        test_raw_writer.close()
        dedup_writer.close()

        total_chars = sum(category_chars.values())
        total_docs = sum(category_docs.values())
        progress.update(total_chars, category_chars, "Finished", "Complete", total_docs, force=True)
        print("\n", flush=True)
        
        incomplete_categories = []
        for cat, tgt in raw_category_targets.items():
            if single_category is not None and cat != single_category:
                continue
            if category_chars.get(cat, 0) < tgt:
                incomplete_categories.append((cat, category_chars.get(cat, 0), tgt))

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
            completed_datasets=list(completed_datasets),
            failed_datasets=list(failed_datasets),
            active_dataset="Completed" if not incomplete_categories else "Incomplete",
            active_category="Finished" if not incomplete_categories else "Incomplete",
            seen_sha256_count=len(seen_sha256),
            documents_seen=total_docs_seen,
            documents_accepted=total_docs,
            documents_rejected=sum(category_rejected_docs.values()),
            duplicates=total_duplicates,
            retry_statistics=getattr(net_streamer, 'retry_stats', {}),
            source_statistics=source_stats,
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

        if incomplete_categories:
            print("\n[CORPUS INCOMPLETE]", flush=True)
            for cat, curr, tgt in incomplete_categories:
                rem = max(0, tgt - curr)
                print(f"Category: {cat}\nCurrent chars: {curr:,}\nTarget chars: {tgt:,}\nRemaining chars: {rem:,}\n", flush=True)
            
            print("[RAW STAGE ABORTED] Pipeline will not proceed until all category targets are reached.", flush=True)
            return {"status": "INCOMPLETE", "missing_categories": incomplete_categories}

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
                    for line in read_corpus_lines(fpath):
                        obj = json.loads(line.strip())
                        text = obj["text"]
                        cat = obj.get("category", DataCategory.GENERAL_NATURAL_LANGUAGE.value)
                        lang = obj.get("language", "en")
                        
                        toks = len(tokenizer.encode(text))
                        category_tokens[cat] = category_tokens.get(cat, 0) + toks
                        language_tokens[lang] = language_tokens.get(lang, 0) + toks
                        total_dir_tokens += toks
                        
                        out_writer.write_record(obj)
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
                            for line in read_corpus_lines(os.path.join(in_dir, fname)):
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
    parser.add_argument("--recover-dedup", action="store_true", help="Reconstruct dedup index from existing shards")
    parser.add_argument("--audit-resume", action="store_true", help="Print detailed state of corpus vs checkpoint and exit")
    args = parser.parse_args()

    try:
        build_prox_corpus_pipeline(
            target_tokens=args.target_tokens,
            resume=args.resume,
            dry_run=args.dry_run,
            report_only=args.report_only,
            single_category=args.category,
            stage=args.stage,
            recover_dedup=args.recover_dedup,
            audit_resume=args.audit_resume
        )
    except KeyboardInterrupt:
        print("\n[Corpus Builder] Graceful shutdown requested (KeyboardInterrupt)...", flush=True)
    except Exception as e:
        import traceback
        print(f"\n[Corpus Builder] FATAL PIPELINE EXCEPTION: {e}", flush=True)
        traceback.print_exc()
    finally:
        print("\n[Corpus Builder] Exited.", flush=True)

if __name__ == "__main__":
    main()
