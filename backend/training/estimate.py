import argparse
import math
from typing import Optional
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer

def estimate_training_budget(
    model_name: str = "neurix-100m",
    target_steps: Optional[int] = None,
    target_tokens: Optional[int] = None,
    batch_size: int = 1,
    grad_accum: int = 16,
    seq_len: int = 2048,
    save_every: int = 1000,
    measured_cpu_tok_s: float = 72.5
):
    config = get_config(model_name)
    model = NeurixTransformer(config)
    num_params = model.num_parameters()

    effective_batch_size = batch_size * grad_accum
    tokens_per_step = effective_batch_size * seq_len

    remainder_tokens = 0
    effective_tokens = 0

    if target_tokens is not None and target_tokens > 0:
        steps = math.ceil(target_tokens / tokens_per_step)
        effective_tokens = steps * tokens_per_step
        remainder_tokens = effective_tokens - target_tokens
    elif target_steps is not None and target_steps > 0:
        steps = target_steps
        effective_tokens = steps * tokens_per_step
    else:
        steps = 50000
        effective_tokens = steps * tokens_per_step

    # Estimate FLOPs per step: 6 * N * tokens_per_step (forward + backward)
    flops_per_step = 6 * num_params * tokens_per_step
    total_flops = flops_per_step * steps

    num_checkpoints = steps // save_every if save_every > 0 else 0
    checkpoint_size_mb = (num_params * 4 + num_params * 4 * 3) / (1024**2)  # params + optimizer states
    total_storage_gb = (num_checkpoints * checkpoint_size_mb) / 1024

    # Estimated durations
    cpu_duration_sec = effective_tokens / measured_cpu_tok_s
    cpu_duration_hours = cpu_duration_sec / 3600
    cpu_duration_days = cpu_duration_hours / 24

    rtx_4090_hours = total_flops / (150e12 * 0.40 * 3600)
    a100_hours = total_flops / (312e12 * 0.45 * 3600)
    h100_cluster_hours = total_flops / (8 * 1979e12 * 0.50 * 3600)

    print("\n" + "="*70)
    print("PROX AI — NEURIX REALISTIC TRAINING ESTIMATOR")
    print("="*70)
    print(f"Model Architecture:           {model_name} ({num_params:,} parameters)")
    print(f"Sequence Length:              {seq_len} tokens")
    print(f"Micro Batch Size:             {batch_size}")
    print(f"Gradient Accumulation Steps:  {grad_accum}")
    print(f"Effective Batch Size:         {effective_batch_size}")
    print(f"Tokens Per Step:              {tokens_per_step:,}")
    print(f"Total Target Steps:           {steps:,}")
    if target_tokens is not None:
        print(f"Target Requested Tokens:      {target_tokens:,}")
        print(f"Derived Effective Tokens:     {effective_tokens:,} ({effective_tokens / 1e9:.4f} Billion Tokens)")
        print(f"Ceil Rounding Step Padding:   +{remainder_tokens:,} extra tokens (ceil to step boundary)")
    else:
        print(f"Total Pretraining Tokens:     {effective_tokens:,} ({effective_tokens / 1e9:.4f} Billion Tokens)")
    print(f"Estimated FLOPs Per Step:     {flops_per_step:.2e}")
    print(f"Estimated Total Compute FLOPs:{total_flops:.2e}")
    print(f"Checkpoint Interval:          Every {save_every:,} steps")
    print(f"Estimated Checkpoint Count:   {num_checkpoints}")
    print(f"Single Checkpoint Size:       {checkpoint_size_mb:.2f} MB")
    print(f"Total Checkpoint Storage:     {total_storage_gb:.2f} GB")
    print("-"*70)
    print("ESTIMATED TRAINING TIMELINES:")
    print(f"  [ROUGH CPU ESTIMATE] Baseline (~{measured_cpu_tok_s:.1f} tok/s): {cpu_duration_hours:.2f} hours ({cpu_duration_days:.2f} days)")
    print(f"  [MODEL-BASED ESTIMATE] Single RTX 4090 (150 TFLOPS FP16):  ~{rtx_4090_hours:.2f} hours")
    print(f"  [MODEL-BASED ESTIMATE] Single A100 80GB (312 TFLOPS FP16): ~{a100_hours:.2f} hours")
    print(f"  [MODEL-BASED ESTIMATE] 8x H100 GPU Cluster (8x 1979 TFLOPS):~{h100_cluster_hours:.2f} hours")
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Estimate Neurix Pretraining Compute & Memory Budget")
    parser.add_argument("--model", type=str, default="neurix-100m")
    parser.add_argument("--steps", type=int, default=None, help="Target steps")
    parser.add_argument("--tokens", "--target-tokens", type=int, default=None, help="Target total tokens (accepts --tokens or --target-tokens)")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=16)
    parser.add_argument("--seq-len", type=int, default=2048)
    parser.add_argument("--save-every", type=int, default=1000)

    args = parser.parse_args()
    estimate_training_budget(
        model_name=args.model,
        target_steps=args.steps,
        target_tokens=args.tokens,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        seq_len=args.seq_len,
        save_every=args.save_every
    )

if __name__ == "__main__":
    main()
