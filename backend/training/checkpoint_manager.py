import os
import json
import glob
from typing import List, Dict, Any, Optional
from backend.training.checkpoint import save_checkpoint
from backend.utils.hf_hub import upload_to_hf_model, calculate_sha256
from backend.utils.storage import check_disk_space

class CheckpointManager:
    def __init__(
        self,
        output_dir: str,
        hf_repo_id: Optional[str] = None,
        max_local_keep: int = 2,
        dry_run: bool = False
    ):
        self.output_dir = output_dir
        self.hf_repo_id = hf_repo_id
        self.max_local_keep = max_local_keep
        self.dry_run = dry_run
        os.makedirs(output_dir, exist_ok=True)
        
    def get_local_checkpoints(self) -> List[str]:
        # Returns paths sorted by creation time (oldest first)
        ckpts = glob.glob(os.path.join(self.output_dir, "checkpoint-step-*.pt"))
        return sorted(ckpts, key=os.path.getmtime)
        
    def save_and_manage(
        self,
        step: int,
        epoch: int,
        model: Any,
        optimizer: Any,
        scheduler: Any,
        model_config: Any,
        training_config: Any,
        metrics: Dict[str, float],
        dataset_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        
        # 1. Estimate space
        # A 1B model checkpoint in FP32 + Optimizer states could be ~12GB. Let's assume 15GB required.
        required_space = 15 * (1024**3)
        if not check_disk_space(required_space, self.output_dir):
            print("[CheckpointManager] Insufficient space for new checkpoint. Attempting to force cleanup.")
            self._cleanup_local(force=True)
            
        # 2. Save locally
        ckpt_path = save_checkpoint(
            output_dir=self.output_dir,
            step=step,
            epoch=epoch,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            model_config=model_config,
            training_config=training_config,
            metrics=metrics,
            dataset_metadata=dataset_metadata
        )
        
        # 3. Upload and verify if HF repo is configured
        if self.hf_repo_id:
            filename = os.path.basename(ckpt_path)
            sha256 = calculate_sha256(ckpt_path)
            
            manifest = {
                "step": step,
                "epoch": epoch,
                "filename": filename,
                "sha256": sha256
            }
            manifest_path = os.path.join(self.output_dir, f"{filename}.manifest.json")
            with open(manifest_path, "w") as f:
                json.dump(manifest, f)
                
            success = upload_to_hf_model(
                repo_id=self.hf_repo_id,
                local_path=ckpt_path,
                path_in_repo=f"checkpoints/{filename}",
                dry_run=self.dry_run
            )
            
            if success:
                upload_to_hf_model(
                    repo_id=self.hf_repo_id,
                    local_path=manifest_path,
                    path_in_repo=f"checkpoints/{filename}.manifest.json",
                    dry_run=self.dry_run
                )
                print(f"[CheckpointManager] Remote verification success for {filename}.")
                self._cleanup_local(force=False)
            else:
                print(f"[CheckpointManager] Upload failed for {filename}. Retaining local copy.")
        else:
            self._cleanup_local(force=False)
            
        return ckpt_path

    def _cleanup_local(self, force: bool = False):
        ckpts = self.get_local_checkpoints()
        keep = self.max_local_keep
        
        if force:
            keep = max(1, keep - 1)
            
        if len(ckpts) > keep:
            for old_ckpt in ckpts[:-keep]:
                try:
                    os.remove(old_ckpt)
                    print(f"[CheckpointManager] Deleted old local checkpoint: {old_ckpt}")
                    manifest = f"{old_ckpt}.manifest.json"
                    if os.path.exists(manifest):
                        os.remove(manifest)
                except Exception as e:
                    print(f"[CheckpointManager] Failed to delete {old_ckpt}: {e}")
