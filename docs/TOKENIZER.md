# ProX Tokenizer Documentation

## Overview
ProX AI uses a dedicated Byte-Level BPE Tokenizer (`backend/tokenizer/`) built on Hugging Face `tokenizers`.

## Features
- **Configurable Vocabulary Size:** Default 32,000.
- **Special Tokens:**
  - `<pad>` (ID: 0)
  - `<bos>` (ID: 1)
  - `<eos>` (ID: 2)
  - `<unk>` (ID: 3)
  - `<proxpl_start>` (ID: 4)
  - `<proxpl_end>` (ID: 5)
- **Multi-Domain Support:** Python, TypeScript, C/C++, JSON, Markdown, natural language, and ProXPL syntax.
- **Unicode Support:** Preserves multi-byte UTF-8 sequences.
- **Deterministic Identity:** $encode(decode(tokens)) = tokens$.

## Training CLI
Train a custom ProX vocabulary on domain corpora:
```bash
python -m backend.tokenizer.train_tokenizer \
    --dataset ./data/corpus \
    --vocab-size 32000 \
    --output ./weights/tokenizer/tokenizer.json
```
