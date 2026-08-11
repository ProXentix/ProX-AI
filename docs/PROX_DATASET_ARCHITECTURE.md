# ProX AI — Production Dataset Architecture Specification

**Date:** August 11, 2026  
**Status:** IMPLEMENTED & VERIFIED  
**Module Location:** `backend/datasets/`  

---

## 1. Architectural Overview

The **ProX AI Dataset Architecture** is an end-to-end data processing and validation engine designed to load, normalize, categorize, quality-filter, deduplicate, and split pretraining datasets while enforcing strict zero-leakage boundaries and producing reproducible dataset manifests (`dataset_manifest.json`).

```text
Local Text / Code / JSONL / ProXPL Files
                   │
                   ▼
  LocalDatasetLoader (loader.py)
                   │
                   ▼
 Category Classifier (categories.py)
                   │
                   ▼
 DatasetQualityPipeline (quality.py) ──► Syntax Validation (ast.parse)
                   │
                   ▼
 DatasetDeduplicator (deduplication.py) ──► Exact SHA-256 + Near-Dup Jaccard
                   │
                   ▼
 DataLeakageChecker (leakage.py) ──► Train/Val Overlap Verification
                   │
                   ▼
 DatasetManifestGenerator (manifest.py) ──► `dataset_manifest.json`
```

---

## 2. Canonical Data Categories

Data is partitioned into 6 explicit canonical categories:

| Category Key | Description & Target Material | Current Corpus Status |
| :--- | :--- | :--- |
| `general_natural_language` | General domain natural language text (`.txt`) | **AVAILABLE** (`data/smoke_test.jsonl`) |
| `programming_languages` | Python, JavaScript, TypeScript, C, C++, Rust, Go (`.py`, `.ts`, `.js`, `.c`, `.cpp`) | **AVAILABLE** (`data/smoke_test.jsonl`) |
| `technical_documentation` | Architecture docs, APIs, Markdown specs (`.md`, `.rst`) | **AVAILABLE** (`docs/*.md`) |
| `proxpl` | Native ProXPL source code, specs, compiler tests (`.proxpl`) | **AVAILABLE** (`data/smoke_test.jsonl`) |
| `mathematics_reasoning` | Formal proofs, LaTeX equations, reasoning benchmarks (`.tex`) | **NOT AVAILABLE** |
| `structured_technical_text` | JSON, YAML, XML schemas, config data (`.json`, `.yaml`) | **AVAILABLE** (`data/smoke_test.jsonl`) |

*Data Availability Protocol:* Any category without an active, verified dataset corpus is explicitly reported as **`NOT AVAILABLE`** in manifests and reports rather than generating simulated statistics.

---

## 3. Supported File Formats & Ingestion (`loader.py`)

The loader recursively scans and ingests:
- **Plain Text (`.txt`)**
- **Markdown (`.md`, `.rst`)**
- **Structured JSON & JSONL (`.json`, `.jsonl`)**
- **Source Code (`.py`, `.ts`, `.js`, `.c`, `.cpp`, `.rs`, `.go`)**
- **ProXPL Source (`.proxpl`)**

Output records include document text, source file path, assigned category, format extension, and byte size.

---

## 4. Measurable Quality Filtering Pipeline (`quality.py`)

1. **Unicode Normalization:** Applies NFC Unicode normalization and strips invalid characters.
2. **Length Boundary Filter:** Rejects documents with length $< 10$ characters or $> 100,000$ characters.
3. **Repetition Filter:** Measures $10$-gram repetition ratio and discards documents exceeding $50\%$ repeated $10$-grams.
4. **Syntax Validation:** Executes `ast.parse` for Python source code and delimiter balance heuristics for C/JS/ProXPL.

---

## 5. Deduplication Strategy (`deduplication.py`)

- **Exact Deduplication:** Identifies and strips bitwise identical documents using SHA-256 hashes.
- **Near-Duplicate Detection:** Computes character $5$-gram Jaccard similarity across documents ($\text{threshold} \ge 0.85$) to eliminate near-identical duplicates.

---

## 6. Train/Val Leakage Guard (`leakage.py`)

Before dataset finalization, the dataset generator computes exact SHA-256 hashes and $5$-gram Jaccard overlaps across train and validation splits. If any validation document overlaps with training data, a leakage error is flagged and recorded in `leakage_verification_report`.

---

## 7. Dataset Manifest Schema (`dataset_manifest.json`)

Every dataset version outputs a reproducible `dataset_manifest.json`:
```json
{
  "dataset_name": "ProX-Corpus-DEV",
  "dataset_version": "v0.1",
  "creation_timestamp": "2026-08-11T12:21:07Z",
  "dataset_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "source_identifiers": ["data/smoke_test.jsonl"],
  "summary_statistics": {
    "input_document_count": 5,
    "clean_document_count": 5,
    "total_estimated_tokens": 120,
    "total_byte_size": 438,
    "train_document_count": 4,
    "val_document_count": 1
  },
  "category_distribution": {
    "general_natural_language": { "status": "AVAILABLE", "document_count": 1, "estimated_tokens": 20 },
    "programming_languages": { "status": "AVAILABLE", "document_count": 1, "estimated_tokens": 30 },
    "technical_documentation": { "status": "NOT AVAILABLE", "document_count": 0, "estimated_tokens": 0 },
    "proxpl": { "status": "AVAILABLE", "document_count": 2, "estimated_tokens": 45 },
    "mathematics_reasoning": { "status": "NOT AVAILABLE", "document_count": 0, "estimated_tokens": 0 },
    "structured_technical_text": { "status": "AVAILABLE", "document_count": 1, "estimated_tokens": 25 }
  },
  "quality_filtering_statistics": { ... },
  "leakage_verification_report": { "is_clean": true, "exact_leak_count": 0 },
  "tokenizer_metadata": {
    "tokenizer_identifier": "ProX Tokenizer DEV",
    "tokenizer_hash": "ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1"
  }
}
```
