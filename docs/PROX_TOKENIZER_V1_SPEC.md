# ProX Tokenizer Specification — Development Artifact vs Production V1 Spec

**Date:** August 11, 2026  
**Development Artifact Identifier:** `ProX Tokenizer DEV`  
**Development Artifact Path:** `weights/tokenizer/tokenizer.json`  
**Development Artifact SHA-256:** `ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1`  

---

## 1. Versioning Designation Protocol

> [!IMPORTANT]
> **DEVELOPMENT VS. PRODUCTION VERSIONING SEPARATION**  
> The current tokenizer artifact stored at `weights/tokenizer/tokenizer.json` (SHA256: `ae03bfc8edfde3fab00b13a6cd65312a30bcf470ff9182fd7d405ad49103e0a1`) was trained on the development smoke test corpus (`data/smoke_test.jsonl`). It is explicitly designated as **`ProX Tokenizer DEV`**.
>
> The identifier **`ProX Tokenizer V1`** is strictly reserved for the future production tokenizer trained on a representative, full-scale pretraining corpus.

---

## 2. Core Tokenizer Architecture Standards (DEV & V1)

- **Algorithm:** Byte-Level Byte Pair Encoding (BPE)
- **Target Vocabulary Size:** Exactly **32,000** (Strictly compatible with Neurix-100M `vocab_size = 32000`)
- **Character Coverage:** 100% (Byte-Level fallback guarantees zero UNK byte loss)
- **Normalization:** NFC Unicode Normalization
- **Pre-tokenizer:** ByteLevel (`add_prefix_space=False`)
- **Decoder:** ByteLevel
- **Post-processor:** ByteLevel
- **Serialization Format:** HuggingFace `tokenizers` JSON (`tokenizer.json`)

---

## 3. Frozen Special Token Assignments

| Special Token | Token ID | Semantics / Purpose |
| :--- | :--- | :--- |
| `<pad>` | `0` | Sequence padding token |
| `<bos>` | `1` | Beginning of sequence marker |
| `<eos>` | `2` | End of sequence marker |
| `<unk>` | `3` | Unknown token fallback |
| `<proxpl_start>` | `4` | ProXPL code block start boundary |
| `<proxpl_end>` | `5` | ProXPL code block end boundary |

---

## 4. Controlled Tokenizer Experiments Protocol (`experiment.py`)

Before freezing `ProX Tokenizer V1`, candidate tokenizers (e.g. `DEV`, `Candidate A`, `Candidate B`) must be evaluated using the benchmarking harness (`backend/tokenizer/experiment.py`):

### Comparison Criteria
1. **Compression Ratio:** Measured in bytes per token ($\text{bytes}/\text{tokens}$).
2. **Average Tokens per Document:** Token length across category samples.
3. **Code Tokenization Efficiency:** Indentation and token splitting on `.py`, `.ts`, `.c`.
4. **ProXPL Syntax Efficiency:** Tokenization of ProXPL keywords (`fn`, `let`, `mut`, `struct`, `impl`, `pub`, `->`, `=>`).
5. **Unicode & Byte Fallback Behavior:** Handling of non-ASCII characters without bloat.
6. **Throughput:** Encoding throughput ($\text{tokens/sec}$).

---

## 5. ProXPL Tokenization Evaluation (`proxpl_eval.py`)

ProXPL tokenization behavior is measured against representative syntax constructs:
- Function declarations (`fn main()`, generics `<T>`)
- Keywords & control flow (`let`, `mut`, `match`, `pub`, `impl`)
- Punctuation & operators (`->`, `=>`, `::`, `!`)
- Compiler error diagnostics (`error[E0308]: mismatched types`)

---

## 6. Tokenizer Freeze Protocol

> [!CAUTION]
> **IMMUTABILITY FREEZE PROTOCOL**  
> Once `ProX Tokenizer V1` is trained on the production corpus and frozen, token mappings, vocabulary size, and special token IDs are strictly immutable. Any modification to token mappings after pretraining begins will corrupt embedding projections.
