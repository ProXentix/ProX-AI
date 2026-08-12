import os
import json
import tempfile
import pytest
from backend.datasets.config import TARGET_CONFIG, get_scaled_target_config, validate_target_config
from backend.datasets.stratified_split import assign_stratified_split
from backend.datasets.checkpoint import CorpusCheckpointManager
from backend.datasets.sharded_writer import ShardedCorpusWriter
from backend.datasets.proxpl_sources import load_approved_proxpl_corpus, verify_zero_repo_contamination
from backend.datasets.leakage import DataLeakageChecker, verify_no_leakage
from backend.tokenizer.tokenizer import ProXTokenizer

def test_target_config_validation():
    assert validate_target_config(TARGET_CONFIG) is True
    scaled = get_scaled_target_config(100_000)
    assert scaled["target_total_tokens"] == 100_000
    assert sum(scaled["category_targets"].values()) == 100_000

    invalid_config = {
        "target_total_tokens": 100,
        "category_targets": {"cat_a": 50, "cat_b": 40}  # sum 90 != 100
    }
    with pytest.raises(ValueError):
        validate_target_config(invalid_config)

def test_deterministic_stratified_split():
    record1 = {"sha256": "abc123sha", "category": "general_natural_language", "language": "en", "source": "src1"}
    record2 = {"sha256": "xyz789sha", "category": "programming_languages", "language": "python", "source": "src2"}

    split1 = assign_stratified_split(record1, val_ratio=0.10)
    split1_again = assign_stratified_split(record1, val_ratio=0.10)
    assert split1 in ["train", "validation"]
    assert split1 == split1_again, "Stratified split must be 100% deterministic"

def test_checkpoint_manager():
    with tempfile.TemporaryDirectory() as tmp_dir:
        chk_file = os.path.join(tmp_dir, "test_chk.json")
        mgr = CorpusCheckpointManager(checkpoint_path=chk_file)
        
        mgr.save_checkpoint(
            config_hash="hash123",
            category_tokens={"general_natural_language": 5000},
            category_docs={"general_natural_language": 10},
            language_tokens={"en": 5000},
            completed_datasets={"fineweb"}
        )
        
        mgr2 = CorpusCheckpointManager(checkpoint_path=chk_file)
        loaded = mgr2.load_checkpoint()
        assert loaded is True
        assert mgr2.get_category_tokens("general_natural_language") == 5000
        assert mgr2.is_category_complete("general_natural_language", 4000) is True
        assert mgr2.is_category_complete("general_natural_language", 10000) is False

def test_sharded_corpus_writer():
    with tempfile.TemporaryDirectory() as tmp_dir:
        writer = ShardedCorpusWriter(tmp_dir, prefix="test_shard", max_records_per_shard=2, use_compression=False)
        writer.write_record({"text": "rec1", "sha256": "h1"})
        writer.write_record({"text": "rec2", "sha256": "h2"})
        writer.write_record({"text": "rec3", "sha256": "h3"})
        writer.close()

        files = os.listdir(tmp_dir)
        assert len(files) == 2  # Shard 0 with 2 records, Shard 1 with 1 record

def test_zero_repository_contamination():
    clean_records = [
        {
            "source_id": "proxpl_approved_spec.md_0",
            "source_url": "https://prox.ai/docs/proxpl",
            "text": "fn main() {}"
        }
    ]
    assert verify_zero_repo_contamination(clean_records) is True

    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirty_records = [
        {
            "source_id": f"{repo_dir}/scripts/build_prox_corpus.py",
            "source_url": f"file://{repo_dir}/scripts/build_prox_corpus.py",
            "text": "import os"
        }
    ]
    with pytest.raises(ValueError):
        verify_zero_repo_contamination(dirty_records)

def test_approved_proxpl_corpus_loading():
    tokenizer = ProXTokenizer()
    records = load_approved_proxpl_corpus(tokenizer)
    assert len(records) > 0
    for r in records:
        assert r["category"] == "proxpl"
        assert r["language"] == "proxpl"
        assert "sha256" in r

def test_leakage_detection():
    train_docs = ["Sample document for training classification.", "Another distinct training sample."]
    val_docs_clean = ["Validation text that is completely non-overlapping."]
    val_docs_leaked = ["Sample document for training classification."]

    checker = DataLeakageChecker()
    clean_rep = checker.check_leakage(train_docs, val_docs_clean)
    assert clean_rep["is_clean"] is True
    assert verify_no_leakage(clean_rep, raise_on_leak=False) is True

    leaked_rep = checker.check_leakage(train_docs, val_docs_leaked)
    assert leaked_rep["is_clean"] is False
    with pytest.raises(RuntimeError):
        verify_no_leakage(leaked_rep, raise_on_leak=True)
