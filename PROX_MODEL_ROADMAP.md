# ProX Model Roadmap

This document outlines the strategic training and development lifecycle for the ProX AI model families: **Neurix**, **Logix**, and **Optix**.

## 1. Neurix (General AI)
*Focus: General conversation, instruction following, multilingual tasks, summarization, and everyday productivity.*

### Development Stages
- **Stage 1 (Foundation):** Start with strong open-weight models, customize tokenizer, training data, and instruction tuning.
- **Stage 2 (ProX Models):** Train increasingly independent checkpoints from scratch.
  - *Progression:* `Neurix-Base` → `Neurix-Instruct` → `Neurix-Pro`

### Model Versions (Iterative Scaling)
- `Neurix 1B` (For local experimentation and pipeline validation)
- `Neurix 3B` (Small foundation model)
- `Neurix 7B` (Medium foundation model)
- `Neurix 14B+` (Production model)

### Dataset Requirements
- **Sources:** Web text, public domain books, instruction datasets, high-quality multilingual data (with strong focus on Indian languages).
- **Processing:** Rigorous PII filtering, toxicity screening, and language-specific tokenization optimization to prevent fragmentation.

### Evaluation
- **ProXBench Categories:** General knowledge, instruction following, writing quality, multilingual performance, context understanding.

### Infrastructure Requirements
- General-purpose distributed training clusters.
- Efficient tokenizer training pipeline.
- Streaming-optimized inference engines.

---

## 2. Logix (Coding + Reasoning)
*Focus: Complex logic, multi-step reasoning, programming, mathematical problem solving, and tool usage.*

### Development Stages
- **Stage 1 (Foundation):** Base model optimized for long-context and technical text.
- **Stage 2 (ProX Models):** Specialized SFT and RLHF for verifiable reasoning.
  - *Progression:* `Logix-Base` → `Logix-Code` → `Logix-Reason` → `Logix-Pro`

### Model Versions (Iterative Scaling)
- `Logix 3B` (Testing reasoning pipelines)
- `Logix 7B` (Code completion and debugging)
- `Logix 14B` (Advanced reasoning and repository tasks)
- `Logix 32B+` (Production model)

### Dataset Requirements
- **Sources:** Permissively licensed code repositories, mathematical datasets, logic puzzles, execution traces, ProXPL documentation and standard library.
- **Formats:** Highly structured conversational formats, synthetic reasoning chains, unit tests, and compiler outputs.

### Evaluation
- **ProXBench Categories:** Coding (pass@k), Mathematics, Reasoning (verifiable outcomes), Tool use, Repository understanding.
- **Mechanism:** Automatic evaluation via secure code execution sandboxes.

### Infrastructure Requirements
- Code execution sandboxes for automated evaluation during training.
- Long-context attention optimizations during pretraining and inference.

---

## 3. Optix (Vision + Image)
*Focus: Multimodal understanding, visual reasoning, OCR, and image generation.*

### Development Stages
- **Stage 1 (Foundation):** Implement decoupled vision encoders and image generation pipelines.
- **Stage 2 (ProX Models):** Fully integrated multimodal reasoning.
  - *Progression:* `Optix-Vision` (Encoder) → `Optix-Multimodal` (Text + Image understanding) → `Optix-Image` (Generation) → `Optix-Pro`

### Model Versions
- `Optix Vision`
- `Optix Image`
- `Optix Multimodal`

### Dataset Requirements
- **Sources:** High-quality image-text pairs, document scans, UI screenshots, diagrams with structured descriptions.
- **Processing:** Strict license and copyright verification for all visual assets.

### Evaluation
- **ProXBench Categories:** OCR accuracy, Visual QA, object understanding, image generation fidelity, prompt adherence.

### Infrastructure Requirements
- Modular deployment (separate hosting for Vision Encoder, LLM, and Image Generation models).
- GPU-heavy inference for low-latency image generation.

---

## Shared Milestones
- [ ] **Milestone 1:** Establish ProXBench evaluation suite and training dataset pipeline.
- [ ] **Milestone 2:** Train "Tiny" models for all three families to validate the pipeline end-to-end.
- [ ] **Milestone 3:** Deploy 1B/3B parameter checkpoints to a Staging environment connected to the UI.
- [ ] **Milestone 4:** Complete the first production-scale training run (e.g., 7B/14B).
- [ ] **Milestone 5:** Integrate models with ProX Agents, external tools, and memory systems.
