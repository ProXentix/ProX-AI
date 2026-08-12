# PROX TRAINING CORPUS v0.1 — Quality Filtering and Deduplication Report

**Date:** 2026-08-12 07:46 UTC  
**Corpus Version:** v0.1  
**Status:** PROCESSED & DEDUPLICATED  

---

## 1. Quality Filtering Pipeline Rules

The data pipeline applies 5 measurable quality filters:

1. **NFC Unicode Normalization:** Applies `unicodedata.normalize("NFC", text)` to ensure canonical character representations.
2. **Length Boundary Filter:** Drops documents with length $< 20$ characters or $> 100,000$ characters.
3. **N-Gram Repetition Filter:** Discards documents with $> 45\%$ repeated $10$-grams.
4. **Syntax Validation:** Language-aware syntax validation (Python `ast.parse` for Python source code).
5. **Format Validation:** Drops empty, non-UTF8, or malformed records.

---

## 2. Filtering Execution Statistics

- **Input Documents:** 7,300
- **Clean Documents:** 6,430
- **Empty Filtered:** 0
- **Length Filtered:** 19
- **Repetition Filtered:** 818
- **Syntax Error Filtered:** 0

---

## 3. Deduplication Strategy & Results

- **Exact SHA-256 Deduplication:** 0 exact duplicate documents removed.
- **Near-Duplicate Detection (Jaccard 0.85):** 0 near-duplicate documents removed.
- **Total Duplicates Removed:** 0
- **Remaining Unique Documents:** 6,428

---

## 4. Leakage Guard & Train/Val Partitioning

- **Partition Ratio:** 90% Training (`train/train.jsonl`) / 10% Validation (`validation/val.jsonl`).
- **Leakage Check Result:** Exact SHA-256 and 5-gram Jaccard similarity across training and validation splits.
- **Exact Leaks:** 0
- **Near Leaks:** 0
- **Leakage Status:** **0% LEAKAGE (CLEAN)**.
