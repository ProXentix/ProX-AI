# Neurix-100M Pretraining Readiness & Architecture Report

**Date:** August 11, 2026  
**Target Environment:** Windows 11 AMD64, PyTorch 2.13.0+cpu, 7.4 GB System RAM  
**Model Architecture:** Neurix-100M (100,461,312 parameters)  

---

## 1. Categorized Final Readiness Verdict

To provide an unambiguous readiness evaluation, four distinct readiness criteria are evaluated individually:

### Q1: Is the software pipeline technically functional?
> **`YES`**  
> Model architecture initialization, forward/backward passes, autograd, loss evaluation, checkpoint saving, checkpoint loading, optimizer state restoration, scheduler stepping, gradient accumulation (effective batch size 16), and deterministic step execution are verified. The test suite passes 28 / 28 tests (`python -m pytest -q`).

### Q2: Can the current machine execute the exact 100M architecture?
> **`YES, FOR SHORT DRY RUNS`**  
> The machine executes FP32 training at batch size = 1 and max sequence length = 2048. Peak estimated memory is **4,924.92 MB (4.81 GB)**, which fits within 7.4 GB System RAM leaving a **2.59 GB** RAM margin. Peak empirical process RSS during forward pass is **2,571.99 MB (2.51 GB)**. However, because the RAM margin is 2.59 GB, the environment is classified as **LIMITED MARGIN / SHORT RUNS ONLY** (not "comfortably safe").

### Q3: Is the current machine practical for large-scale 100M pretraining?
> **`NO`**  
> Development CPU execution achieves an empirical baseline throughput of **72.5 tokens/sec**. Executing Chinchilla-optimal pretraining (~2.0 Billion tokens / 61,036 steps) would require approximately **7,662.94 hours (319.29 days)**. Practical pretraining requires an NVIDIA GPU (e.g. RTX 4090 or cloud A100/H100 instance).

### Q4: Is the dataset/tokenizer ready for production pretraining?
> **`NOT YET`**  
> The current dataset artifact (`data/smoke_test.jsonl`) and tokenizer (`weights/tokenizer/tokenizer.json`) are development artifacts. The tokenizer is designated as **ProX Tokenizer DEV** (SHA256: `ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1`). **ProX Tokenizer V1** remains reserved for the future representative production pretraining corpus.

---

## 2. Learning Rate Schedule Investigation Findings

- **Reported LR in Dry Runs:** `LR: 0.000000e+00`
- **Scheduler Type:** Cosine Annealing with Warmup (`LambdaLR`)
- **Configured Parameters:** `learning_rate = 3.0e-4`, `warmup_steps = 500`, `max_steps = 10000`, `gradient_accumulation_steps = 16`.
- **Exact Floating-Point Values at Micro-Steps (Grad Accum = 16):**
  - `step 0`: `lr = 0.0` (`0.000000000000e+00`)
  - `step 1`: `lr = 0.0` (`0.000000000000e+00`)
  - `step 2`: `lr = 0.0` (`0.000000000000e+00`)
  - `step 5`: `lr = 0.0` (`0.000000000000e+00`)
  - `step 10`: `lr = 0.0` (`0.000000000000e+00`)
  - `step 11`: `lr = 0.0` (`0.000000000000e+00`)

### Cause Analysis
1. **Mathematical Warmup Initial State:** At step 0 of linear warmup, $\text{lr\_lambda}(0) = 0 / \text{warmup\_steps} = 0.0$.
2. **Gradient Accumulation Boundary:** In `NeurixTrainer`, `self.optimizer.step()` and `self.scheduler.step()` are executed only on accumulation boundaries (`(global_step + 1) % 16 == 0`).
3. **Dry-Run Horizon:** During a 10-step or 11-step dry run, `global_step` reaches 10 or 11 micro-steps ($< 16$). Consequently, zero optimizer steps and zero scheduler steps occurred, keeping `current_step` in `LambdaLR` at 0.
4. **Step Order:** `self.scheduler.step()` is positioned **after** `self.optimizer.step()` as per PyTorch standard practice.

---

## 3. Checkpoint Resume & Determinism Verification

- **Checkpoint Path:** `./weights/neurix_100m_dry_run/checkpoint-step-000010.pt`
- **Step 10 Loss:** 10.6797
- **Resume Command:** `python -m backend.training.train --steps 11 --resume ...`
- **Step 11 Loss:** 10.6209
- **Restored State Verification:**
  - `model_state`: Restored
  - `optimizer_state`: Restored (`exp_avg`, `exp_avg_sq` confirmed intact, not freshly initialized)
  - `scheduler_state`: Restored
  - `rng_states`: Restored (`torch`, `python`)
- **Determinism Test:** Executing 1 step from checkpoint in two independent model/optimizer instances produced exact bitwise equality:
  - `Loss Diff: 0.000000000000e+00`
  - `Max Parameter Diff: 0.000000000000e+00`

---

## 4. Hardware Memory & Peak RSS Profile

- **Exact Parameter Count:** 100,461,312 parameters
- **FP32 Weights (383.23 MiB):** $100,461,312 \times 4\text{ bytes} = 401,845,248\text{ bytes}$
- **FP32 Gradients (383.23 MiB):** $100,461,312 \times 4\text{ bytes}$
- **AdamW Optimizer Memory (766.46 MiB):** $2 \times 100,461,312 \times 4\text{ bytes}$
- **Activations (batch=1, seq=2048):** 2,592 MB
- **PyTorch Framework Reserve:** 800 MB (Engineering Estimate)
- **Total Theoretical Peak Memory:** **4,924.92 MB (4.81 GB)**
- **System Installed RAM:** 7.4 GB
- **Calculated Margin:** **2.59 GB**
- **Safety Classification:** **`LIMITED MARGIN / SHORT RUNS ONLY`**

### Empirical RSS Profile (CPU)
- Baseline: **200.82 MB**
- Post-Model Init: **694.99 MB**
- Post-Optimizer Init: **775.15 MB**
- Peak Forward Pass RSS: **2,571.99 MB**
- Post-Optimizer Step RSS: **2,455.21 MB**

---

## 5. Tokenizer Lifecycle & Versioning Status

- **Tokenizer Lifecycle:** Model training strictly loads the pre-trained frozen tokenizer artifact (`weights/tokenizer/tokenizer.json`). Dynamic BPE training during model initialization is disabled (`allow_fallback=False`).
- **Tokenizer Version:** `ProX Tokenizer DEV`
- **Development Artifact Path:** `weights/tokenizer/tokenizer.json`
- **Artifact SHA-256:** `ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1`
- **Production Status:** `ProX Tokenizer V1` name and specification remain reserved for the future representative production dataset.

---

## 6. Pretraining Authorization Status

> [!CAUTION]
> **LONG PRETRAINING IS STRICTLY NOT AUTHORIZED**  
> Execution of training runs beyond short verification dry-runs is strictly prohibited in the current phase.
