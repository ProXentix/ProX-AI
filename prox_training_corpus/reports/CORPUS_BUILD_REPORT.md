# PROX TRAINING CORPUS v0.1 — Build Report

**Date:** 2026-08-12 08:22 UTC  
**Corpus Version:** v0.1  
**Corpus Hash (SHA-256):** `118b07b0da667cf79e9e6e9ab27c6bebb34e5887294c509f091e7af3372fc89e`  
**Build Status:** **PASSED WITH WARNINGS**  

---

## 1. Executive Summary & Status

- **Target Tokens:** **10,000,000**
- **Actual Usable Tokens:** **9,019,043**
- **Train Tokens:** **8,117,138** | **Validation Tokens:** **901,905**
- **Target Status:** PARTIAL BUILD (90.2% of target)
- **Leakage Verification:** CLEAN (0% Leakage)

---

## 2. Category Distribution & Token Breakdown

| Category Key | Status | Document Count | Tokens | Target Tokens | Actual % | Target % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `general_natural_language` | AVAILABLE | 1,003 | 4,508,314 | 4,500,000 | 49.99% | 45.0% |
| `programming_languages` | AVAILABLE | 423 | 3,003,284 | 3,000,000 | 33.3% | 30.0% |
| `technical_documentation` | AVAILABLE | 706 | 1,000,413 | 1,000,000 | 11.09% | 10.0% |
| `proxpl` | AVAILABLE | 3 | 5,008 | 1,000,000 | 0.06% | 10.0% |
| `mathematics_reasoning` | AVAILABLE | 75 | 502,024 | 500,000 | 5.57% | 5.0% |
| `structured_technical_text` | NOT AVAILABLE | 0 | 0 | 0 | 0.0% | 0.0% |

---

## 3. Language & Source Representation

- **Languages Represented:** en, python, proxpl, math
- **Sources Ingested:** `FineWeb-Edu`, `The Stack Smol / CodeParrot`, `CodeXGlue / AG News`, `OpenWebMath`, `ProXPL Approved Corpus`.
- **ProXPL Status:** 5,008 tokens ingested under strict zero repository contamination.
- **Repository Isolation Verification:** **STRICTLY ZERO** (Verified 100% repository isolation).

---

## 4. Quality & Deduplication Metrics

- **Total Streamed Documents:** 2,291
- **Accepted Clean Documents:** 2,210
- **Rejected Documents:** 81
- **Exact SHA-256 Duplicates Filtered:** 2,210 unique payload checksums tracked.

---

## 5. Final Assessment

**CORPUS BUILD STATUS:** **PASSED WITH WARNINGS**
