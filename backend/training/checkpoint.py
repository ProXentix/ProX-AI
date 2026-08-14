import os
import torch
import random
from typing import Dict, Any, Optional

def save_checkpoint(
    output_dir: str,
    step: int,
    epoch: int,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Optional[Any],
    model_config: Any,
    training_config: Any,
    metrics: Dict[str, float],
    dataset_metadata: Optional[Dict[str, Any]] = None
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    checkpoint_name = f"checkpoint-step-{step:06d}.pt"
    checkpoint_path = os.path.join(output_dir, checkpoint_name)

    try:
        import subprocess
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        git_dirty = bool(subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8").strip())
    except Exception:
        git_commit = "unknown"
        git_dirty = True

    state = {
        "step": step,
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict() if optimizer else None,
        "scheduler_state": scheduler.state_dict() if scheduler else None,
        "model_config": model_config,
        "training_config": training_config,
        "dataset_metadata": dataset_metadata or {},
        "git_commit": git_commit,
        "git_dirty": git_dirty,
        "metrics": metrics,
        "rng_states": {
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            "python": random.getstate(),
        }
    }

    torch.save(state, checkpoint_path)
    latest_path = os.path.join(output_dir, "latest.pt")
    torch.save(state, latest_path)

    print(f"[Checkpoint System] Saved checkpoint to {checkpoint_path}")
    return checkpoint_path

def load_checkpoint(
    checkpoint_path: str,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[Any] = None,
    device: str = "cpu"
) -> Dict[str, Any]:
    if not os.path.exists(checkpoint_path):
        print("[Checkpoint System] NO TRAINED CHECKPOINT FOUND")
        raise FileNotFoundError(f"Checkpoint path not found: {checkpoint_path}")

    print(f"[Checkpoint System] Loading checkpoint from {checkpoint_path}...")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    model.load_state_dict(checkpoint["model_state"])

    if optimizer and checkpoint.get("optimizer_state"):
        optimizer.load_state_dict(checkpoint["optimizer_state"])

    if scheduler and checkpoint.get("scheduler_state"):
        scheduler.load_state_dict(checkpoint["scheduler_state"])

    if "rng_states" in checkpoint and checkpoint["rng_states"]:
        rng = checkpoint["rng_states"]
        if "torch" in rng and rng["torch"] is not None:
            torch.set_rng_state(rng["torch"])
        if "python" in rng and rng["python"] is not None:
            random.setstate(rng["python"])

    print(f"[Checkpoint System] Successfully restored state from step {checkpoint.get('step', 0)}")
    return checkpoint

def inspect_checkpoint(checkpoint_path: str) -> Dict[str, Any]:
    if not os.path.exists(checkpoint_path):
        print("[Checkpoint System] NO TRAINED CHECKPOINT FOUND")
        return {"status": "NO TRAINED CHECKPOINT FOUND"}

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    info = {
        "checkpoint_path": checkpoint_path,
        "step": checkpoint.get("step", "Unknown"),
        "epoch": checkpoint.get("epoch", "Unknown"),
        "model_config": checkpoint.get("model_config"),
        "training_config": checkpoint.get("training_config"),
        "dataset_metadata": checkpoint.get("dataset_metadata", {}),
        "git_commit": checkpoint.get("git_commit", "Unknown"),
        "git_dirty": checkpoint.get("git_dirty", True),
        "metrics": checkpoint.get("metrics", {}),
    }

    print("="*50)
    print("PROX-AI CHECKPOINT METADATA")
    print("="*50)
    print(f"Path:            {info['checkpoint_path']}")
    print(f"Global Step:     {info['step']}")
    print(f"Epoch:           {info['epoch']}")
    print(f"Git Commit:      {info['git_commit']}")
    print(f"Git Dirty:       {info['git_dirty']}")
    
    if info['dataset_metadata']:
        print(f"Corpus Version:  {info['dataset_metadata'].get('corpus_version', 'Unknown')}")
        print(f"Train Tokens:    {info['dataset_metadata'].get('train_tokens', 'Unknown')}")
        print(f"Hindi Tokens:    {info['dataset_metadata'].get('hindi_tokens', 'Unknown')}")
        
    if info['metrics']:
        print(f"Validation Loss: {info['metrics'].get('val_loss', 'N/A')}")
        print(f"Perplexity:      {info['metrics'].get('perplexity', 'N/A')}")
    print("="*50 + "\n")

    return info

def export_inference_model(
    output_dir: str,
    model: torch.nn.Module,
    model_config: Any,
    tokenizer_metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Exports a clean, inference-ready model without training states."""
    os.makedirs(output_dir, exist_ok=True)
    export_path = os.path.join(output_dir, "inference_model.pt")

    state = {
        "model_state": model.state_dict(),
        "model_config": model_config,
        "tokenizer_metadata": tokenizer_metadata or {}
    }

    torch.save(state, export_path)
    print(f"[Checkpoint System] Exported inference model to {export_path}")
    return export_path
