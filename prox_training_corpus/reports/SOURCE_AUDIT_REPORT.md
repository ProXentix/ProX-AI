# PROX TRAINING CORPUS v0.1 — Dataset Source Audit Report

**Date:** 2026-08-15 09:33 UTC  
**Hugging Face Authentication Status:** **HF authentication: NOT AVAILABLE**  
**Pipeline Version:** v0.1  

---

## 1. Executive Summary & Accessibility Audit

This audit evaluates all candidate data sources for pre-training preflight accessibility, authentication requirements, category mapping, and explicit fallback options.

- **Total Data Sources Evaluated:** 23
- **Hugging Face Token Status:** `NOT AVAILABLE` (Token value is never logged or stored)
- **Gated Datasets Access:** DISABLED (Permissive Fallbacks Active)

---

## 2. Source Accessibility & Provenance Registry

| Dataset Name | Subset / Path | Category | Language | Auth Req | Accessible | Fallback Source | License | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FineWeb-Edu` | `sample-10BT` | `general_natural_language` | `en` | NO | **YES** | `wikimedia/wikipedia (20231101.en)` | ODC-By 1.0 | `ACCESSIBLE` |
| `The Stack Smol (Python)` | `data/python` | `programming_languages` | `python` | YES | **NO** | `codeparrot/codeparrot-clean-train` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (C)` | `data/c` | `programming_languages` | `c` | YES | **NO** | `m-a-p/code_bagel (c_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (C++)` | `data/c++` | `programming_languages` | `cpp` | YES | **NO** | `m-a-p/code_bagel (cpp_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (JavaScript)` | `data/javascript` | `programming_languages` | `js` | YES | **NO** | `bigcode/starcoderdata (js_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (TypeScript)` | `data/typescript` | `programming_languages` | `ts` | YES | **NO** | `bigcode/starcoderdata (ts_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (Rust)` | `data/rust` | `programming_languages` | `rust` | YES | **NO** | `bigcode/starcoderdata (rust_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (Go)` | `data/go` | `programming_languages` | `go` | YES | **NO** | `bigcode/starcoderdata (go_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `The Stack Smol (Java)` | `data/java` | `programming_languages` | `java` | YES | **NO** | `bigcode/starcoderdata (java_subset)` | BigCode Terms / Apache-2.0 | `GATED_UNAUTHENTICATED (Fallback Active)` |
| `CodeXGlue NL/Code Search` | `default` | `technical_documentation` | `en` | NO | **YES** | `None Required` | Apache-2.0 | `ACCESSIBLE` |
| `AG News Sci/Tech` | `default` | `technical_documentation` | `en` | NO | **YES** | `None Required` | Academic / Public News | `ACCESSIBLE` |
| `OpenWebMath` | `default` | `mathematics_reasoning` | `en` | NO | **YES** | `None Required` | ODC-By 1.0 | `ACCESSIBLE` |
| `Sangraha Verified (Hindi)` | `verified/hin` | `hindi` | `hi` | NO | **YES** | `ai4bharat/sangraha (unverified/hin)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (ben)` | `verified/ben` | `other_indic` | `bn` | NO | **YES** | `ai4bharat/sangraha (unverified/ben)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (guj)` | `verified/guj` | `other_indic` | `gu` | NO | **YES** | `ai4bharat/sangraha (unverified/guj)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (kan)` | `verified/kan` | `other_indic` | `kn` | NO | **YES** | `ai4bharat/sangraha (unverified/kan)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (mal)` | `verified/mal` | `other_indic` | `ml` | NO | **YES** | `ai4bharat/sangraha (unverified/mal)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (mar)` | `verified/mar` | `other_indic` | `mr` | NO | **YES** | `ai4bharat/sangraha (unverified/mar)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (ori)` | `verified/ori` | `other_indic` | `or` | NO | **YES** | `ai4bharat/sangraha (unverified/ori)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (pan)` | `verified/pan` | `other_indic` | `pa` | NO | **YES** | `ai4bharat/sangraha (unverified/pan)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (tam)` | `verified/tam` | `other_indic` | `ta` | NO | **YES** | `ai4bharat/sangraha (unverified/tam)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (tel)` | `verified/tel` | `other_indic` | `te` | NO | **YES** | `ai4bharat/sangraha (unverified/tel)` | Indic Permissive | `ACCESSIBLE` |
| `Sangraha Verified (urd)` | `verified/urd` | `other_indic` | `ur` | NO | **YES** | `ai4bharat/sangraha (unverified/urd)` | Indic Permissive | `ACCESSIBLE` |

---

## 3. Audited Preflight Assessment

- **General Natural Language:** `FineWeb-Edu` (Accessible) with `Wikipedia` fallback.
- **Programming Languages:** Multi-language streaming across `Python, C, C++, JavaScript, TypeScript, Rust, Go, Java` with `CodeParrot Clean / StarCoderData` fallbacks.
- **Technical Documentation:** `CodeXGlue` & `AG News Sci/Tech` (Accessible).
- **ProXPL Status:** ProXPL was removed from PROX TRAINING CORPUS v0.1 and is not included in the v0.1 training corpus.
- **Mathematics & Reasoning:** `OpenWebMath` (Accessible).
