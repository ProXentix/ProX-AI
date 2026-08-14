import os
import json
from typing import Optional
from backend.utils.hf_hub import list_model_files, download_from_hf_model, calculate_sha256

def discover_latest_remote_checkpoint(repo_id: str, local_dir: str, dry_run: bool = False) -> Optional[str]:
    """
    Scans the HF repo for the latest checkpoint.
    Downloads the manifest and the checkpoint.
    Verifies the checksum.
    Returns the local path to the downloaded checkpoint if verified.
    """
    files = list_model_files(repo_id)
    # Checkpoints are typically named checkpoints/checkpoint-step-000000.pt
    ckpts = [f for f in files if f.startswith("checkpoints/checkpoint-step-") and f.endswith(".pt")]
    if not ckpts:
        print("[Resume] No remote checkpoints found.")
        return None
        
    # Sort by step number
    ckpts.sort(key=lambda x: int(x.split("-step-")[1].split(".")[0]))
    latest_ckpt_remote = ckpts[-1]
    manifest_remote = f"{latest_ckpt_remote}.manifest.json"
    
    if manifest_remote not in files:
        print(f"[Resume] WARNING: Latest checkpoint {latest_ckpt_remote} has no manifest. It may be unverified or incomplete.")
        return None
        
    print(f"[Resume] Discovered latest remote checkpoint: {latest_ckpt_remote}")
    
    # Download manifest
    manifest_path = download_from_hf_model(repo_id, manifest_remote, local_dir=local_dir, dry_run=dry_run)
    if not manifest_path or dry_run:
        return None
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    expected_sha256 = manifest.get("sha256")
    
    # Download checkpoint
    ckpt_path = download_from_hf_model(repo_id, latest_ckpt_remote, local_dir=local_dir, dry_run=dry_run)
    if not ckpt_path:
        return None
        
    # Verify checksum
    print(f"[Resume] Validating checksum for {ckpt_path}...")
    actual_sha256 = calculate_sha256(ckpt_path)
    
    if actual_sha256 != expected_sha256:
        print(f"[Resume] ERROR: Checksum mismatch for {ckpt_path}.")
        print(f"  Expected: {expected_sha256}")
        print(f"  Actual:   {actual_sha256}")
        return None
        
    print("[Resume] Checksum verified successfully.")
    return ckpt_path
