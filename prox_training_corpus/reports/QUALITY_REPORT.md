# PROX TRAINING CORPUS v0.1 — Quality Filtering and Deduplication Report

**Date:** August 11, 2026  
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

## 2. Deduplication Strategy

- **Exact SHA-256 Deduplication:** Identifies and strips bitwise identical documents within and across sources.
- **Near-Duplicate Detection:** Computes character $5$-gram Jaccard similarity across documents ($\text{threshold} \ge 0.85$) to eliminate near-identical copies across different dataset sources.

---

## 3. Leakage Guard & Train/Val Partitioning

- **Partition Ratio:** 90% Training (`train/train.jsonl`) / 10% Validation (`validation/val.jsonl`).
- **Leakage Check Result:** Calculated exact SHA-256 and $5$-gram Jaccard similarity across training and validation splits after deduplication.
- **Leakage Status:** **`0% LEAKAGE (CLEAN)`**. Zero overlapping documents detected between splits.
