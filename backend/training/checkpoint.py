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
    metrics: Dict[str, float]
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    checkpoint_name = f"checkpoint-step-{step:06d}.pt"
    checkpoint_path = os.path.join(output_dir, checkpoint_name)

    state = {
        "step": step,
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict() if optimizer else None,
        "scheduler_state": scheduler.state_dict() if scheduler else None,
        "model_config": model_config,
        "training_config": training_config,
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
        "metrics": checkpoint.get("metrics", {}),
    }

    print("\n" + "="*50)
    print("CHECKPOINT METADATA INSPECTION")
    print("="*50)
    print(f"Path:            {info['checkpoint_path']}")
    print(f"Global Step:     {info['step']}")
    print(f"Epoch:           {info['epoch']}")
    if info['metrics']:
        print(f"Validation Loss: {info['metrics'].get('val_loss', 'N/A')}")
        print(f"Perplexity:      {info['metrics'].get('perplexity', 'N/A')}")
    print("="*50 + "\n")

    return info
