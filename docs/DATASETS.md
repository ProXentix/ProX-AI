# ProX AI Dataset Pipeline

## Data Pipeline Architecture
The dataset pipeline (`backend/datasets/`) manages loading, preprocessing, sequence packing, and streaming.

## Supported Formats
- Plain Text (`.txt`)
- JSON Lines (`.jsonl`)
- Structured JSON (`.json`)
- Markdown (`.md`)
- Source Code (`.py`, `.ts`, `.js`, `.c`, `.cpp`, `.proxpl`)

## Pipeline Stages
1. **Loading:** `LocalDatasetLoader` reads local files without external internet dependencies.
2. **Deduplication:** Hash-based text deduplication (`deduplicate_texts`).
3. **Sequence Packing:** Concatenates token streams separated by `<eos>` and packs into sequence blocks of length $max\_seq\_len + 1$.
4. **Mixture Weighting:** `DatasetMixture` samples categories according to configured ratios (General Text: 40%, Programming: 25%, Reasoning: 15%, ProXPL: 15%, Documentation: 5%).
5. **Streaming:** `LocalDatasetStreamer` streams token blocks incrementally for zero-RAM memory footprint.
