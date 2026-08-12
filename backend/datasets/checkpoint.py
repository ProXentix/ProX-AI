import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Set, Optional

CHECKPOINT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "prox_training_corpus",
    "checkpoints"
)
CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "checkpoint_state.json")

class CorpusCheckpointManager:
    """Manages pipeline state for resumable streaming corpus builds."""
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.checkpoint_path = checkpoint_path or CHECKPOINT_FILE
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
        self.state: Dict[str, Any] = {
            "pipeline_version": "v0.1",
            "configuration_hash": "",
            "last_updated": "",
            "category_tokens": {},
            "category_docs": {},
            "language_tokens": {},
            "completed_datasets": [],
            "seen_sha256_count": 0,
        }

    def load_checkpoint(self, expected_config_hash: Optional[str] = None) -> bool:
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                cat_tokens = data.get("category_tokens", {})
                if "proxpl" in cat_tokens:
                    print(f"[Checkpoint] Invalidating old checkpoint containing removed category 'proxpl': {self.checkpoint_path}")
                    return False
                
                if expected_config_hash and data.get("configuration_hash") != expected_config_hash:
                    print(f"[Checkpoint] Configuration hash mismatch (stored={data.get('configuration_hash')[:8]}, expected={expected_config_hash[:8]}). Invalidating checkpoint.")
                    return False
                
                self.state = data
                print(f"[Checkpoint] Loaded valid checkpoint from {self.checkpoint_path}")
                return True
            except Exception as e:
                print(f"[Checkpoint] Failed to load checkpoint: {e}")
        return False

    def save_checkpoint(
        self,
        config_hash: str,
        category_tokens: Dict[str, int],
        category_docs: Dict[str, int],
        language_tokens: Dict[str, int],
        completed_datasets: Set[str],
        seen_sha256_count: int = 0
    ):
        self.state["configuration_hash"] = config_hash
        self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.state["category_tokens"] = category_tokens
        self.state["category_docs"] = category_docs
        self.state["language_tokens"] = language_tokens
        self.state["completed_datasets"] = list(completed_datasets)
        self.state["seen_sha256_count"] = seen_sha256_count

        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def is_category_complete(self, category: str, target_tokens: int) -> bool:
        current = self.state.get("category_tokens", {}).get(category, 0)
        return current >= target_tokens

    def get_category_tokens(self, category: str) -> int:
        return self.state.get("category_tokens", {}).get(category, 0)
