# Neurix-100M — Parameter & Hardware Memory Analysis Report

**Date:** August 11, 2026  
**Model Architecture:** Neurix-100M (Transformer Decoder)  
**Parameter Count:** 100,461,312 parameters  
**Target Environment:** Windows 11 AMD64, PyTorch 2.13.0+cpu, 7.4 GB System RAM  

---

## 1. Executive Summary

This report presents a rigorous breakdown of memory requirements for training the **Neurix-100M** parameter model. Memory is strictly differentiated between **Model Weights** (static parameter storage), **Total Estimated Training Memory** (weights, gradients, optimizer states, sequence activation graphs, and framework buffers), and **Observed Process RSS Memory**.

**Verdict on 7.4 GB System RAM (FP32, batch=1, seq=2048):**
**`LIMITED MARGIN / SHORT RUNS ONLY`** (Peak estimated memory is **4,924.92 MB** [~4.81 GB], leaving a **2.59 GB** safety margin on a 7.4 GB machine).

> [!IMPORTANT]
> **CLASSIFICATION NOTICE**  
> Do **NOT** classify this configuration as "comfortably safe". While the current configuration fits within available RAM without triggering System OOM during short dry runs, the remaining memory margin is limited (2.59 GB). Furthermore, CPU compute throughput (~72.5 tokens/sec) makes large-scale pretraining impractically slow.

---

## 2. Model Weight Storage Requirements

*Note on Units:* All megabyte values in this specification represent binary megabytes (MiB, $1024^2$ bytes). $100,461,312 \times 4\text{ bytes} = 401,845,248\text{ bytes} = 383.23\text{ MiB}$.

| Precision / Dtype | Bytes per Parameter | Parameter Memory (MiB) | Parameter Memory (GB) |
| :--- | :--- | :--- | :--- |
| **FP32 (Single Precision)** | 4 bytes | 383.23 MiB | 0.374 GB |
| **FP16 (Half Precision)** | 2 bytes | 191.61 MiB | 0.187 GB |
| **BF16 (Bfloat16)** | 2 bytes | 191.61 MiB | 0.187 GB |

---

## 3. Detailed Training Graph Memory Breakdown

For FP32 training at batch size = 1 and maximum sequence length = 2048:

| Component | Calculation Basis | Theoretical Memory (MB) | Approx Memory (GB) |
| :--- | :--- | :--- | :--- |
| **Model Weights (FP32)** | $100,461,312 \times 4\text{ bytes}$ | 383.23 MB | 0.374 GB |
| **Gradients (FP32)** | 1 FP32 gradient tensor per parameter ($100,461,312 \times 4$) | 383.23 MB | 0.374 GB |
| **AdamW Optimizer States** | 2 FP32 tensors per parameter ($m$ & $v$) ($2 \times 100,461,312 \times 4$) | 766.46 MB | 0.748 GB |
| **Activations (batch=1, seq=2048)** | 12 layers, 768 hidden, attention matrices, MLP intermediate | 2,592.00 MB | 2.531 GB |
| **PyTorch / Framework Overhead** | Engineering estimate / C++ runtime reserve (unmeasured buffer reserve) | 800.00 MB | 0.781 GB |
| **TOTAL ESTIMATED PEAK RAM** | **Sum of all training components** | **4,924.92 MB** | **4.81 GB** |

---

## 4. Empirical Peak Memory Measurement (Process RSS on CPU)

During single-step dry runs of Neurix-100M on the Windows CPU environment, process Working-Set / Resident Set Size (RSS) memory was recorded at each phase:

| Phase | Observed Process RSS (MB) | Stage Delta (MB) | Cumulative Delta (MB) |
| :--- | :--- | :--- | :--- |
| **1. Baseline (Python / PyTorch load)** | 200.82 MB | Baseline | Baseline |
| **2. Post-Model Initialization** | 694.99 MB | +494.17 MB | +494.17 MB |
| **3. Post-Optimizer Creation** | 775.15 MB | +80.16 MB | +574.33 MB |
| **4. During Forward Pass** | **2,571.99 MB** | +1,796.84 MB | **+2,371.18 MB** |
| **5. During Backward Pass** | 2,027.21 MB | -544.78 MB | +1,826.40 MB |
| **6. Post-Optimizer Step (`optimizer.step()`)** | 2,455.21 MB | +428.00 MB | +2,254.40 MB |

### Analysis: Theoretical Estimate vs. Observed Peak Memory
- **Theoretical Peak Estimate:** 4,924.92 MB (~4.81 GB)
- **Observed Peak Process RSS:** **2,571.99 MB** (~2.51 GB)

*Explanation of Variance:*
1. **Lazy AdamW Allocation:** PyTorch's `torch.optim.AdamW` initializes state tensors ($m$ and $v$) lazily per parameter group upon the first parameter update.
2. **Intermediate Activation Cleanup:** During CPU execution, PyTorch's autograd engine frees activation graphs progressively layer-by-layer during the backward pass (evidenced by RSS dropping from 2,571.99 MB to 2,027.21 MB).
3. **Framework Overhead Buffer:** The 800 MB PyTorch overhead is an engineering safety buffer for worst-case peak allocations rather than a static resident baseline.

---

## 5. Hardware Safety & Margin Analysis

- **System Installed RAM:** 7.40 GB
- **Estimated Training Graph Peak Memory:** 4.81 GB
- **Calculated Safety Margin:** **2.59 GB**

> [!WARNING]
> **SAFETY RATING: LIMITED MARGIN / SHORT RUNS ONLY**  
> Execution of `neurix-100m` (batch=1, max_seq_len=2048, FP32) is technically functional without system OOM, but the remaining 2.59 GB RAM margin leaves limited headroom for background processes.

---

## 6. Context Length & Sequence Scaling Analysis

| Sequence Length | Activation Memory (MB) | Total Peak RAM (GB) | RAM Margin on 7.4 GB | Safety Rating |
| :--- | :--- | :--- | :--- | :--- |
| **128 tokens** | ~162 MB | ~2.45 GB | 4.95 GB | SAFE |
| **512 tokens** | ~648 MB | ~2.93 GB | 4.47 GB | SAFE |
| **1024 tokens** | ~1,296 MB | ~3.57 GB | 3.83 GB | SAFE |
| **2048 tokens (Canonical)** | ~2,592 MB | ~4.81 GB | 2.59 GB | LIMITED MARGIN |
