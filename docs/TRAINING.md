# ProX AI Training Pipeline

## Overview
ProX AI features a configuration-driven Causal Language Model training engine (`backend/training/`).

## Training Features
- **Loss:** Cross-entropy next-token prediction with teacher forcing.
- **Optimizer:** AdamW (`weight_decay=0.1`).
- **Scheduler:** Cosine annealing with linear warmup (`backend/training/scheduler.py`).
- **Mixed Precision:** Automatic FP16 mixed precision (`torch.cuda.amp.autocast`) on CUDA.
- **Gradient Accumulation & Clipping:** Micro-batch accumulation with gradient norm clipping (`clip_grad_norm_ = 1.0`).
- **Reproducibility:** Global PyTorch, CUDA, and Python seed control.

## Running Training
Execute training via CLI:
```bash
python -m backend.training.train \
    --model neurix-100m \
    --config ./configs/neurix-100m.yaml \
    --dataset ./data/train.jsonl \
    --output ./weights/neurix \
    --steps 10000
```

## Checkpoint Inspection
Inspect checkpoint step, loss, epoch, and config:
```bash
python -m backend.training.train --inspect ./weights/neurix/latest.pt
```
