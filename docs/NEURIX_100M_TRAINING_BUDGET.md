# Neurix-100M — Pretraining Compute Budget & Scale Analysis

**Date:** August 11, 2026  
**Model:** Neurix-100M (100,461,312 parameters)  
**Empirical CPU Throughput Baseline:** 72.5 tokens / second (Effective batch = 16, Seq len = 2048, FP32)  

---

## 1. Token-Based Empirical CPU Baselines

The following timelines are derived using the observed dry-run baseline of **72.5 tokens/sec**.

> [!NOTE]
> **LABEL: ROUGH CPU ESTIMATE**  
> These numbers serve strictly as an empirical baseline for planning. Actual CPU throughput may fluctuate during long runs due to OS scheduling, background processes, thermal throttling, and memory bandwidth contention.

| Target Token Count | Derived Global Steps (ceil) | Effective Tokens | CPU Estimated Duration (Hours) | CPU Estimated Duration (Days) |
| :--- | :--- | :--- | :--- | :--- |
| **1 Million Tokens** | 31 steps | 1,015,808 tokens | 3.89 hours | 0.16 days |
| **10 Million Tokens** | 306 steps | 10,027,008 tokens | 38.42 hours | 1.60 days |
| **100 Million Tokens** | 3,052 steps | 100,007,936 tokens | 383.17 hours | 15.97 days |
| **1 Billion Tokens** | 30,518 steps | 1,000,005,632 tokens | 3,831.44 hours | 159.64 days |
| **2 Billion Tokens (Chinchilla)** | 61,036 steps | 2,000,027,648 tokens | 7,662.94 hours | 319.29 days |

*Rounding Semantics:* Steps are calculated as $\lceil \text{target\_tokens} / \text{tokens\_per\_step} \rceil$ where $\text{tokens\_per\_step} = 1 \times 16 \times 2048 = 32,768$. Remainder tokens are padded to the step boundary.

---

## 2. Hardware Tier Comparison & Projections

> [!NOTE]
> **LABEL: MODEL-BASED ESTIMATE**  
> GPU timelines are mathematical projections based on theoretical FLOPS capacity and assumed Model FLOPs Utilization (MFU) efficiency factors. They are **NOT** benchmark results from physical GPU hardware.

### Compute Formula
- **FLOPs per step:** $6 \times N \times \text{tokens\_per\_step} = 6 \times 100,461,312 \times 32,768 = 1.975 \times 10^{13}\text{ FLOPs/step}$.
- **Chinchilla Scale (2B Tokens / 61,036 steps):** Total compute required is $\approx 1.205 \times 10^{18}\text{ total FLOPs}$.

| Hardware Tier | Rated Precision FLOPS | Assumed MFU Efficiency | Effective Compute Throughput | Projected Duration (2B Tokens) | Estimation Category |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development CPU (4-Core)** | N/A (Empirical) | N/A | **72.5 tok/s** | **319.29 days** | `ROUGH CPU ESTIMATE` |
| **Single RTX 4090 24GB** | 150 TFLOPS (FP16 Tensor) | 40% MFU | 60 TFLOPS | **5.58 hours** | `MODEL-BASED ESTIMATE` |
| **Single A100 80GB SXM** | 312 TFLOPS (FP16 Tensor) | 45% MFU | 140.4 TFLOPS | **2.39 hours** | `MODEL-BASED ESTIMATE` |
| **8x H100 GPU Cluster** | $8 \times 1,979\text{ TFLOPS}$ | 50% MFU | 7,916 TFLOPS | **0.04 hours (2.5 mins)** | `MODEL-BASED ESTIMATE` |

---

## 3. Checkpoint Storage Budget (2B Tokens / 61,036 Steps)

- **Checkpoint Frequency:** Every 1,000 steps
- **Checkpoint Count:** 61 checkpoints
- **Single Checkpoint Size:** $1,532.92\text{ MB}$ ($1.50\text{ GB}$) — Includes FP32 model weights ($383.23\text{ MB}$) and AdamW optimizer states ($1,149.69\text{ MB}$).
- **Total Storage Requirement:** **91.32 GB**

---

## 4. Pretraining Authorization Summary

- **CPU Status:** Fully functional for code verification, unit tests, and short dry runs. **STRICTLY NOT AUTHORIZED FOR FULL PRETRAINING** (319 days required).
- **Production Pretraining Requirement:** Production training of Neurix-100M requires an NVIDIA GPU instance with PyTorch CUDA support.
