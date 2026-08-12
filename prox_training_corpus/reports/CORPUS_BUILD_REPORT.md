# PROX TRAINING CORPUS v0.1 — Build Report

**Date:** 2026-08-12 10:12 UTC  
**Corpus Version:** v0.1  
**Corpus Hash (SHA-256):** `12d8f46f622f9908680c8196d730c338ac0d65579fea35dc82866f36fb91b15a`  
**Build Status:** **PASSED**  
**100M BUILD STATUS:** **READY**  

---

## 1. Executive Summary & Status

- **Target Tokens:** **100,000**
- **Actual Usable Tokens:** **110,991**
- **Train Tokens:** **99,891** | **Validation Tokens:** **11,100**
- **Target Status:** TARGET REACHED
- **Leakage Verification:** CLEAN (0% Leakage)

---

## 2. Category Distribution & Token Breakdown

| Category Key | Status | Document Count | Tokens | Target Tokens | Actual % | Target % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `general_natural_language` | AVAILABLE | 14 | 57,600 | 50,000 | 51.9% | 50.0% |
| `programming_languages` | AVAILABLE | 5 | 30,860 | 30,000 | 27.8% | 30.0% |
| `technical_documentation` | AVAILABLE | 11 | 15,492 | 15,000 | 13.96% | 15.0% |
| `mathematics_reasoning` | AVAILABLE | 1 | 7,039 | 5,000 | 6.34% | 5.0% |

---

## 3. Programming Language Distribution

| Programming Language | Tokens Ingested | Target Share % | Status |
| :--- | :--- | :--- | :--- |
| `PYTHON` | 30,860 | 20.0% | VERIFIED |
| `C` | 0 | 13.0% | SOURCE_UNAVAILABLE |
| `CPP` | 0 | 13.0% | SOURCE_UNAVAILABLE |
| `JS` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `TS` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `RUST` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `GO` | 0 | 10.0% | SOURCE_UNAVAILABLE |
| `JAVA` | 0 | 11.0% | SOURCE_UNAVAILABLE |
| `EN` | 73,092 | 10.0% | VERIFIED |
| `MATH` | 7,039 | 10.0% | VERIFIED |

---

## 4. Quality & Network Robustness Statistics

- **Total Streamed Documents:** 31
- **Accepted Clean Documents:** 31
- **Rejected Documents:** 0
- **Network Retry Successes:** 0
- **Network Retry Exhausted:** 0

---

## 5. ProXPL Status & Pipeline Policy

ProXPL was removed from PROX TRAINING CORPUS v0.1 and is not included in the v0.1 training corpus.

---

## 6. 100M Build Readiness Assessment

**100M BUILD STATUS:** **READY**

**All mandatory targets and leakage checks satisfied.**