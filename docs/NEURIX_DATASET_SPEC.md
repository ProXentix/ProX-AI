# Neurix Dataset Architecture & Specification

## Overview
This document defines the production dataset mixture architecture for pretraining Neurix-100M-v1.

---

## 1. Domain Category Mixtures

| Category ID | Domain Name | Sampling Weight | Target Formats | Quality Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `cat_01` | **Natural Language & Knowledge** | **40%** | `.jsonl`, `.txt`, `.md` | High perplexity score filter, English & Indian language fluency |
| `cat_02` | **General Programming** | **25%** | `.py`, `.ts`, `.js`, `.c`, `.cpp` | Valid syntax, non-minified code, docstrings preserved |
| `cat_03` | **ProXPL Code & Specs** | **15%** | `.proxpl`, `.md` | Compiler-passable ProXPL programs, AST-validated examples |
| `cat_04` | **Technical Documentation** | **10%** | `.md`, `.txt`, `.json` | Markdown layout structure, API reference docs |
| `cat_05` | **Mathematical Reasoning** | **10%** | `.jsonl`, `.txt` | Step-by-step reasoning traces, equation verifications |

---

## 2. Ingestion & Quality Controls
1. **Deduplication:** SHA-256 exact document hashing and MinHash LSH near-deduplication.
2. **Filtering:** Length bounds ($16 \le tokens \le 32768$), boilerplate removal, PII scrubbing.
3. **Leakage Prevention:** Strict cross-contamination audit between training and held-out validation sets.
