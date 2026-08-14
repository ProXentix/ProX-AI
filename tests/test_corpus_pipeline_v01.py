import os
import json
import tempfile
import pytest
from backend.datasets.config import (
    TARGET_CONFIG,
    PROGRAMMING_LANGUAGE_TARGETS,
    PROGRAMMING_DATA_DIRS,
    DATASET_REGISTRY,
    get_scaled_target_config,
    validate_target_config,
    check_hf_authentication,
    audit_dataset_sources
)
from backend.datasets.stratified_split import assign_stratified_split
from backend.datasets.checkpoint import CorpusCheckpointManager
from backend.datasets.sharded_writer import ShardedCorpusWriter
from backend.datasets.categories import CANONICAL_CATEGORIES
from backend.datasets.leakage import DataLeakageChecker, verify_no_leakage, verify_zero_repo_contamination
from backend.datasets.quality import validate_code_syntax
from backend.datasets.streaming import RobustNetworkStreamer
from backend.tokenizer.tokenizer import ProXTokenizer
from scripts.build_prox_corpus import generate_source_audit_report

def test_programming_data_dirs_mapping():
    assert PROGRAMMING_DATA_DIRS["cpp"] == "data/c++"
    cpp_entry = next((ds for ds in DATASET_REGISTRY if ds.get("language") == "cpp"), None)
    assert cpp_entry is not None
    assert cpp_entry["subset"] == "data/c++"

def test_target_config_validation():
    assert "proxpl" not in TARGET_CONFIG["category_targets"]
    assert "proxpl" not in CANONICAL_CATEGORIES
    assert validate_target_config(TARGET_CONFIG) is True
    scaled = get_scaled_target_config(100_000)
    assert scaled["target_total_tokens"] == 100_000
    assert sum(scaled["category_targets"].values()) == 100_000
    assert "proxpl" not in scaled["category_targets"]

    invalid_config = {
        "target_total_tokens": 100,
        "category_targets": {"cat_a": 50, "cat_b": 40}
    }
    with pytest.raises(ValueError):
        validate_target_config(invalid_config)

def test_hf_authentication_preflight_formatting():
    from backend.datasets.config import check_hf_authentication
    state = check_hf_authentication()
    assert isinstance(state, dict)
    assert "authenticated" in state
    assert "api_reachable" in state

def test_audit_dataset_sources():
    from backend.datasets.config import audit_dataset_sources
    state = {"authenticated": True, "api_reachable": True, "token_source": "TEST", "username": "testuser"}
    audit = audit_dataset_sources(state)
    assert isinstance(audit, list)
    for res in audit:
        assert res["accessible"] is True
        assert "dataset_name" in res

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
            config_hash="abc",
            category_chars={"general_natural_language": 500},
            category_docs={"general_natural_language": 1},
            language_chars={"en": 500},
            completed_datasets=set(),
            seen_sha256_count=1,
            documents_seen=1,
            documents_accepted=1,
            documents_rejected=0,
            duplicates=0,
            git_commit="test"
        )
        
        mgr2 = CorpusCheckpointManager(checkpoint_path=chk_file)
        loaded = mgr2.load_checkpoint(expected_config_hash="abc")
        assert loaded is True
        assert mgr2.state["category_chars"]["general_natural_language"] == 500
        assert mgr2.is_category_complete("general_natural_language", 400) is True
        assert mgr2.is_category_complete("general_natural_language", 1000) is False

def test_sharded_corpus_writer():
    with tempfile.TemporaryDirectory() as tmp_dir:
        writer = ShardedCorpusWriter(tmp_dir, prefix="test_shard", max_records_per_shard=2, use_compression=False)
        writer.write_record({"text": "rec1", "sha256": "h1"})
        writer.write_record({"text": "rec2", "sha256": "h2"})
        writer.write_record({"text": "rec3", "sha256": "h3"})
        writer.close()

        files = os.listdir(tmp_dir)
        assert len(files) == 2

def test_zero_repository_contamination():
    clean_records = [
        {
            "source_id": "external_clean_doc_0",
            "source_url": "https://example.com/doc",
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

def test_no_proxpl_in_pipeline_categories():
    assert "proxpl" not in CANONICAL_CATEGORIES
    assert "proxpl" not in TARGET_CONFIG["category_targets"]
    assert PROGRAMMING_DATA_DIRS["cpp"] == "data/c++"

def test_syntax_warning_isolation():
    # String literal with invalid backslash escape '\s'
    code_with_invalid_escape = "def foo():\n    s = '\\s\\w\\d'\n    return s"
    res = validate_code_syntax(code_with_invalid_escape, "python")
    assert res["valid"] is True

def test_robust_network_streamer():
    streamer = RobustNetworkStreamer(max_retries=1, initial_backoff=0.01)
    def dummy_gen():
        yield {"text": "hello"}

    items = list(streamer.safe_stream(dummy_gen, "DummySource"))
    assert len(items) == 1
    assert items[0]["text"] == "hello"

def test_source_audit_report_generation():
    from scripts.build_prox_corpus import generate_source_audit_report
    state = {"authenticated": True, "api_reachable": True, "token_source": "TEST", "username": "testuser"}
    audit = [{"dataset_name": "Test", "subset": "test", "category": "general", "status": "ACCESSIBLE", "accessible": True, "auth_required": False, "fallback": "N/A", "license": "MIT"}]
    report_path = generate_source_audit_report(audit, state)
    assert os.path.exists(report_path)
    assert os.path.exists(report_path)
