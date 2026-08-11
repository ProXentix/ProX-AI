# ProX AI — Dataset, Tokenizer, and Model Versioning Scheme

**Date:** August 11, 2026  
**Status:** STANDARD & SPECIFICATION PERSISTED  

---

## 1. Overview

To ensure complete experimental reproducibility and auditability, ProX AI enforces a strict three-tier versioning hierarchy across **Datasets**, **Tokenizers**, and **Models**.

```text
Dataset Version (v0.x / v1.0) ──► Tokenizer Version (DEV / V1) ──► Model Version (Neurix-100M-v0 / v1)
```

Every training run manifest (`run_manifest.json`) and checkpoint header MUST record exact versions and cryptographic SHA-256 hashes for all three tiers.

---

## 2. Versioning Matrix & Naming Standards

### Tier 1: Dataset Versions
- **`Dataset v0.x` (Development / Smoke Testing):** Pre-production corpora derived from development samples (e.g. `data/smoke_test.jsonl`).
- **`Dataset v1.0` (Production Pretraining Corpus):** Frozen, representative production corpus containing natural language, source code, technical documentation, ProXPL, mathematics, and structured text.

### Tier 2: Tokenizer Versions
- **`ProX Tokenizer DEV`:** Development artifact trained on `smoke_test.jsonl` (SHA256: `ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1`).
- **`ProX Tokenizer V1`:** Immutable production tokenizer trained on `Dataset v1.0` (Target vocabulary size: 32,000).

### Tier 3: Model Architecture & Run Versions
- **`Neurix-100M-v0`:** Development dry-run / verification models.
- **`Neurix-100M-v1`:** Production pretrained model weight releases.

---

## 3. Cryptographic Hashing Protocol

1. **Dataset Hash:** SHA-256 hash of all concatenated sorted document strings in the cleaned dataset (`compute_dataset_hash`).
2. **Tokenizer Hash:** SHA-256 hash of `tokenizer.json` (`get_file_sha256`).
3. **Run Manifest:** Stored in `./weights/<model_dir>/run_manifest.json` on training launch.

---

## 4. Reproducibility Mandate

A model output or benchmark result is considered valid ONLY if it links directly to a `run_manifest.json` containing matching dataset, tokenizer, and model SHA-256 hashes.
