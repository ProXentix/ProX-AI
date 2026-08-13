# PROX TRAINING CORPUS v0.1 — Dataset Source Audit Report

**Date:** 2026-08-13 09:24 UTC  
**Hugging Face Authentication Status:** **HF authentication: NOT AVAILABLE**  
**Pipeline Version:** v0.1  

---

## 1. Executive Summary & Accessibility Audit

This audit evaluates all candidate data sources for pre-training preflight accessibility, authentication requirements, category mapping, and explicit fallback options.

- **Total Data Sources Evaluated:** 12
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

---

## 3. Audited Preflight Assessment

- **General Natural Language:** `FineWeb-Edu` (Accessible) with `Wikipedia` fallback.
- **Programming Languages:** Multi-language streaming across `Python, C, C++, JavaScript, TypeScript, Rust, Go, Java` with `CodeParrot Clean / StarCoderData` fallbacks.
- **Technical Documentation:** `CodeXGlue` & `AG News Sci/Tech` (Accessible).
- **ProXPL Status:** ProXPL was removed from PROX TRAINING CORPUS v0.1 and is not included in the v0.1 training corpus.
- **Mathematics & Reasoning:** `OpenWebMath` (Accessible).
