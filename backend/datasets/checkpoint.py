import os
import json
import hashlib
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any, Set, Optional

CHECKPOINT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "prox_training_corpus",
    "checkpoints"
)
CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "checkpoint_latest.json")
PREVIOUS_CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "checkpoint_previous.json")

class CorpusCheckpointManager:
    """Manages pipeline state for resumable streaming corpus builds."""
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.checkpoint_path = checkpoint_path or CHECKPOINT_FILE
        self.previous_checkpoint_path = PREVIOUS_CHECKPOINT_FILE
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
        self.state: Dict[str, Any] = self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        return {
            "schema_version": "v1.0",
            "pipeline_version": "v0.1",
            "git_commit": "",
            "configuration_hash": "",
            "last_updated": "",
            "category_chars": {},
            "category_docs": {},
            "language_chars": {},
            "completed_datasets": [],
            "failed_datasets": [],
            "active_dataset": "",
            "active_category": "",
            "seen_sha256_count": 0,
            "documents_seen": 0,
            "documents_accepted": 0,
            "documents_rejected": 0,
            "duplicates": 0,
            "retry_statistics": {},
            "source_statistics": {}
        }

    def load_checkpoint(self, expected_config_hash: Optional[str] = None) -> bool:
        path_to_load = self.checkpoint_path
        if not os.path.exists(path_to_load):
            path_to_load = self.previous_checkpoint_path
            
        if os.path.exists(path_to_load):
            try:
                with open(path_to_load, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Validation
                if data.get("schema_version") not in ["v1.0"]:
                    print(f"[Checkpoint] Unrecognized schema version: {data.get('schema_version')}")
                    return False
                    
                if expected_config_hash and data.get("configuration_hash") != expected_config_hash:
                    print(f"[Checkpoint] Configuration hash mismatch. Expected {expected_config_hash}, got {data.get('configuration_hash')}")
                    return False
                
                self.state = data
                print(f"[Checkpoint] Loaded valid checkpoint from {path_to_load}")
                return True
            except Exception as e:
                print(f"[Checkpoint] Failed to load checkpoint {path_to_load}: {e}")
        return False

    def save_checkpoint(
        self,
        config_hash: str,
        category_chars: Dict[str, int],
        category_docs: Dict[str, int],
        language_chars: Dict[str, int],
        completed_datasets: list,
        failed_datasets: list = None,
        active_dataset: str = "",
        active_category: str = "",
        seen_sha256_count: int = 0,
        documents_seen: int = 0,
        documents_accepted: int = 0,
        documents_rejected: int = 0,
        duplicates: int = 0,
        retry_statistics: Dict[str, int] = None,
        source_statistics: Dict[str, Any] = None,
        git_commit: str = "unknown"
    ):
        self.state["configuration_hash"] = config_hash
        self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.state["category_chars"] = category_chars
        self.state["category_docs"] = category_docs
        self.state["language_chars"] = language_chars
        self.state["completed_datasets"] = completed_datasets
        self.state["failed_datasets"] = failed_datasets or []
        self.state["active_dataset"] = active_dataset
        self.state["active_category"] = active_category
        self.state["seen_sha256_count"] = seen_sha256_count
        self.state["documents_seen"] = documents_seen
        self.state["documents_accepted"] = documents_accepted
        self.state["documents_rejected"] = documents_rejected
        self.state["duplicates"] = duplicates
        self.state["retry_statistics"] = retry_statistics or {}
        self.state["source_statistics"] = source_statistics or {}
        self.state["git_commit"] = git_commit

        try:
            temp_path = self.checkpoint_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            if os.path.exists(self.checkpoint_path):
                os.replace(self.checkpoint_path, self.previous_checkpoint_path)
                
            os.replace(temp_path, self.checkpoint_path)
        except Exception as e:
            print(f"[Checkpoint] WARNING: Atomic write failed: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def is_category_complete(self, category: str, target_chars: int) -> bool:
        current = self.state.get("category_chars", {}).get(category, 0)
        return current >= target_chars

    def get_category_chars(self, category: str) -> int:
        return self.state.get("category_chars", {}).get(category, 0)
