# PROX TRAINING CORPUS v0.1 — Build Report

**Date:** 2026-08-12 08:30 UTC  
**Corpus Version:** v0.1  
**Corpus Hash (SHA-256):** `5f99393ad3520e71c501e1eaa784641c9bb53a6b92c4f6064db5fceab2493600`  
**Build Status:** **PASSED WITH WARNINGS**  
**100M BUILD STATUS:** **NOT READY**  

---

## 1. Executive Summary & Status

- **Target Tokens:** **10,000,000**
- **Actual Usable Tokens:** **9,024,933**
- **Train Tokens:** **8,122,439** | **Validation Tokens:** **902,494**
- **Target Status:** PARTIAL BUILD (90.2% of target)
- **Leakage Verification:** CLEAN (0% Leakage)

---

## 2. Category Distribution & Token Breakdown

| Category Key | Status | Document Count | Tokens | Target Tokens | Actual % | Target % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `general_natural_language` | AVAILABLE | 1,003 | 4,508,314 | 4,500,000 | 49.95% | 45.0% |
| `programming_languages` | AVAILABLE | 423 | 3,003,284 | 3,000,000 | 33.28% | 30.0% |
| `technical_documentation` | AVAILABLE | 706 | 1,000,413 | 1,000,000 | 11.08% | 10.0% |
| `proxpl` | AVAILABLE | 10 | 10,898 | 1,000,000 | 0.12% | 10.0% |
| `mathematics_reasoning` | AVAILABLE | 75 | 502,024 | 500,000 | 5.56% | 5.0% |
| `structured_technical_text` | NOT AVAILABLE | 0 | 0 | 0 | 0.0% | 0.0% |

---

## 3. Programming Language Distribution

| Programming Language | Tokens Ingested | Target Share % | Status |
| :--- | :--- | :--- | :--- |
| `PYTHON` | 3,003,284 | 20.0% | VERIFIED |
| `C` | 0 | 13.0% | SOURCE_UNAVAILABLE |
| `CPP` | 0 | 13.0% | SOURCE_UNAVAILABLE |
| `JS` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `TS` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `RUST` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `GO` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `JAVA` | 0 | 11.0% | SOURCE_UNAVAILABLE |
| `EN` | 5,508,727 | 10.0% | VERIFIED |
| `PROXPL` | 10,898 | 10.0% | VERIFIED |
| `MATH` | 502,024 | 10.0% | VERIFIED |

---

## 4. Quality & Network Robustness Statistics

- **Total Streamed Documents:** 2,298
- **Accepted Clean Documents:** 2,217
- **Rejected Documents:** 81
- **Network Retry Successes:** 0
- **Network Retry Exhausted:** 0

---

## 5. 100M Build Readiness Assessment

**100M BUILD STATUS:** **NOT READY**

**Blocking Reasons:**
- Token count (9,024,933) is below 95% of target (10,000,000)