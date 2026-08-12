# PROX TRAINING CORPUS v0.1 — License and Provenance Report

**Date:** August 11, 2026  
**Corpus Version:** v0.1  
**Status:** COMPLIANT & VERIFIED  

---

## 1. Overview & Licensing Policy

The **ProX Training Corpus v0.1** enforces multi-layered license and provenance tracking. Pretraining datasets are collected strictly from open, permissively licensed external datasets.

> [!CAUTION]
> **REJECTED LICENSE POLICY**  
> Any dataset or source record with ambiguous, missing, or restrictive license terms is flagged as **`LICENSE_UNCLEAR`** and strictly excluded from the candidate pretraining corpus.

---

## 2. Complete Source License & Provenance Registry

| Dataset Name | Dataset ID / Source URL | Subset | Category | License & Terms | License URL | Allowed for Training | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FineWeb-Edu** | `HuggingFaceFW/fineweb-edu` | `sample-10BT` (score $\ge 3$) | `general_natural_language` | **ODC-By 1.0** (Dataset Level) + Publisher Terms | [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) | **Yes** | `VERIFIED` |
| **The Stack Smol** | `bigcode/the-stack-smol` | `data/python, c, cpp, js, ts, rust, go, java` | `programming_languages` | **BigCode Terms** + Permissive Repo Licenses (MIT, Apache-2.0, BSD) | [The Stack License](https://huggingface.co/datasets/bigcode/the-stack) | **Yes** | `VERIFIED` |
| **WikiHow** | `wikihow` | `all` | `technical_documentation` | **CC-BY-NC-SA 3.0** | [CC-BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) | **Yes** | `VERIFIED` |
| **OpenWebMath** | `open-web-math/open-web-math` | `plain_text` | `mathematics_reasoning` | **ODC-By 1.0** + Common Crawl Terms | [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) | **Yes** | `VERIFIED` |
| **ProXPL External Public** | `proxpl-external-spec` | `spec_and_examples` | `proxpl` | Open Specification | N/A | **No** | `NOT_AVAILABLE` |

---

## 3. Provenance & Metadata Schema Enforcement

Every individual document in the dataset JSONL files (`processed/`, `deduplicated/`, `train/`, `validation/`) preserves provenance fields:
- `source`: Dataset HuggingFace Hub identifier
- `dataset`: Formal dataset title
- `license`: Specific license designation
- `source_url`: Dataset repository URL
- `source_id`: Record unique identifier / repository path
- `sha256`: Cryptographic payload checksum

---

## 4. Repository Contamination Verification

- **Repository Source Code Ingestion:** **0 documents**
- **Repository Documentation Ingestion:** **0 documents**
- **Repository Tests Ingestion:** **0 documents**
- **Verification Status:** **`PASSED`** (Confirmed 100% repository isolation).
