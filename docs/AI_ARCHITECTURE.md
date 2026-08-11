# ProX AI Architecture — Verified Production Architecture

## 1. System Overview
The ProX AI Platform implements a modular, configuration-driven ML pipeline for decoder-only transformer architectures (Neurix, Logix, Optix).

```
backend/
├── api/          # FastAPI routes, CORS, request validation, SSE streaming
├── models/       # NeurixTransformer, LogixModel, OptixModel, ModelConfig
├── tokenizer/    # ProX Byte-Level BPE Tokenizer, train_tokenizer CLI
├── datasets/     # Multi-format dataset loaders, preprocessing, packing, mixture
├── training/     # Causal LM Trainer, AdamW, Cosine LR scheduler, Checkpoint System
├── inference/    # Key-Value Cache (prefill + decode), sampling (top-k, top-p, temp)
├── utils/        # Resource detection (CUDA/CPU, RAM/VRAM), structured logging
└── weights/      # Checkpoint storage (checkpoint-step-XXXX.pt)
```

## 2. Model Architecture: Neurix-100M
- **Type:** Decoder-only Causal Transformer
- **Vocab Size:** 32,000
- **d_model:** 768
- **n_layers:** 12
- **n_heads:** 12 (`head_dim` = 64)
- **d_ff:** 1,720
- **max_seq_len:** 2048
- **Tied Weights:** True
- **Verified Parameters:** Exactly 100,461,312 parameters (~100.46M).

## 3. Key Subsystems

### 3.1 ProX BPE Tokenizer
Custom Byte-Level BPE tokenizer (`backend/tokenizer/`) supporting code (Python, TypeScript, C/C++, ProXPL), JSON, Markdown, and special tokens (`<pad>`, `<bos>`, `<eos>`, `<unk>`, `<proxpl_start>`, `<proxpl_end>`).

### 3.2 Key-Value (KV) Cache Engine
Autoregressive decoding uses Key-Value caching (`backend/inference/kv_cache.py`).
- **Prefill Phase:** Computes initial prompt self-attention ($\mathcal{O}(N^2 \cdot d_{model})$).
- **Decode Phase:** Retrieves cached K/V tensors for past tokens, reducing step attention complexity to $\mathcal{O}(N \cdot d_{model})$.

### 3.3 Checkpoint System
Checkpoints (`checkpoint-step-XXXX.pt`) store model weights, optimizer state, scheduler state, step count, epoch, model configuration, and validation metrics. Overwriting trained checkpoints with uninitialized weights is strictly prevented.

### 3.4 Model Lifecycle States
Models report honest states in Model Registry:
- `REGISTERED`
- `INITIALIZED`
- `CHECKPOINT_FOUND`
- `LOADED`
- `READY`
- `EXPERIMENTAL_NOT_TRAINED`
