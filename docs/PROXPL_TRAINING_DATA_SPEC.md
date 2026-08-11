# ProXPL Training Data Specification & Compiler Integration

**Date:** August 11, 2026  
**Status:** SPECIFICATION & PIPELINE READY  
**Language Target:** ProXPL (Native ProX AI Systems Language)  

---

## 1. Overview

ProXPL is the native high-performance programming language designed for the ProX AI platform. Pretraining data for ProXPL must adhere to rigorous correctness standards. Fake or synthetically hallucinatory code generated merely to inflate dataset byte size is strictly prohibited.

---

## 2. Collection Priorities & Categories

ProXPL training material is organized into 10 prioritized sub-categories:

1. **Language Specification:** Formal EBNF grammar, token rules, type system definitions (`.proxpl`, `.md`).
2. **Compiler Documentation:** Diagnostic descriptions, AST node specifications, compiler CLI flags.
3. **Syntax & Idiom Examples:** Small canonical code patterns, control flow, pattern matching, async primitives.
4. **Standard Library Source:** Built-in module implementations (tensor ops, memory allocators, network primitives).
5. **Validated Source Programs:** Complete, compilable `.proxpl` programs verified by the ProXPL toolchain.
6. **Compiler Unit Tests:** Regression tests, parser test fixtures, type checker tests.
7. **Diagnostic & Error Correction Pairs:** Paired tuples of `(Broken Source, Compiler Error Diagnostic) -> Corrected Source`.
8. **Code Completion Examples:** Partial code snippets paired with target completions.
9. **API Reference Documentation:** Module-level and function-level docstrings with signature annotations.
10. **Real Application Code:** Full application modules and benchmark implementations.

---

## 3. Compiler-in-the-Loop Validation Pipeline

All candidate ProXPL training samples pass through the native compiler validation loop:

```text
ProXPL Source Code Candidate (.proxpl)
                 │
                 ▼
ProXPL Toolchain Syntax Parsing (`proxpl check`)
                 │
   ┌─────────────┴─────────────┐
   ▼                           ▼
[PASS]                      [FAIL]
   │                           │
Execute Test Suite          Capture Compiler Error Code & Line
   │                           │
Record Pass Rate &           Construct Diagnostic Bug-Fix Pair:
Metadata (valid = true)     (Broken Source, Error) -> Fixed
```

---

## 4. Current Availability Status

- **Smoke-Test Samples:** **AVAILABLE** (basic syntax samples in `data/smoke_test.jsonl`).
- **Compiler-Validated Full Corpus:** **PLANNED** (awaiting full ProXPL toolchain deployment).
