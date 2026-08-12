# PROX TRAINING CORPUS v0.1 — Quality Filtering and Deduplication Report

**Date:** 2026-08-12 10:13 UTC  
**Corpus Version:** v0.1  
**Status:** **PASSED**  

---

## 1. Quality Filtering Pipeline Rules

1. **NFC Unicode Normalization:** Normalizes all text representations.
2. **Length Boundary Filter:** Drops documents $< 20$ characters or $> 100,000$ characters.
3. **N-Gram Repetition Filter:** Discards documents with > 45% repeated 10-grams.
4. **Syntax Validation:** Language-aware AST syntax check for Python source code.
5. **Format Validation:** Drops empty, malformed, or contaminated records.

---

## 2. Filtering Execution Statistics

- **Total Streamed Documents:** 31
- **Accepted Clean Documents:** 31
- **Total Rejected Documents:** 0

---

## 3. Deduplication Strategy & Results

- **Exact SHA-256 Deduplication:** 31 unique hashes tracked.
- **Cross-Session Resume Deduplication:** ACTIVE.
- **Repository Isolation:** 100% CLEAN.

---

## 4. Leakage Guard & Train/Val Partitioning

- **Partition Ratio:** 90% Training / 10% Validation.
- **Exact Leak Count:** 0
- **Near Leak Count:** 0
- **Leakage Status:** **0% LEAKAGE (CLEAN)**.
