# Kaggle 1B Production Workflow

This document defines the strict, unidirectional workflow for the final ProX-AI 1B production run.

## Architecture & Boundaries

1. **GitHub (Source of Truth)**: ALL code, configurations, tests, and documentation live here.
2. **Kaggle (Disposable Compute)**: Executes the exact code from GitHub. **NEVER** edit code on Kaggle.
3. **Hugging Face (Persistent Storage)**:
   - **HF Dataset**: Stores the generated 1B corpus.
   - **HF Model**: Stores checkpoints and the final inference model.

## The Production Workflow

### 1. Local Development (Pre-requisite)
- All development happens locally.
- Run `pytest -v` locally and ensure 100% pass rate.
- **Commit & Push** all changes to GitHub.

### 2. Kaggle Environment Initialization
- Open a fresh Kaggle Notebook with a P100/T4x2/A100 GPU.
- Add your Hugging Face API token as a Kaggle Secret (`HF_TOKEN`).
- **Clone** the repository from GitHub:
  ```bash
  git clone https://github.com/ProXentix/ProX-AI.git
  cd ProX-AI
  git checkout <exact_commit_hash>
  pip install -r requirements.txt
  ```

### 3. Corpus Generation (Phase A)
- Generate the corpus targeting 1B tokens:
  ```bash
  python scripts/build_prox_corpus.py
  ```
- This step streams data, deduplicates, filters quality, and generates:
  - `train` shards (~900M)
  - `validation` shards (~50M)
  - `test` shards (~50M)
  - A strict JSON manifest recording Hindi percentages, duplicates, and rejection counts.
- Upload to HF Dataset:
  ```bash
  python scripts/upload_corpus_to_hf.py --repo_id "ProXentix/prox-corpus"
  ```
- Wait for remote verification, then you may delete local shards to free disk space.

### 4. Strict Preflight
- The training script runs `backend/training/preflight.py` automatically.
- **Failures will trigger if:**
  - The working directory is dirty (uncommitted Kaggle changes).
  - The parameter count is exactly 0.
  - Estimated memory exceeds available VRAM.
  - The corpus manifest is missing or shows 0 train tokens.
  - The tokenizer fails the Hindi/English/Code sanity benchmark.

### 5. Training & Resuming
- Execute training, passing the HF Model repo for final export:
  ```bash
  python backend/training/train.py --model neurix-1b --dataset prox_training_corpus --hf-repo "ProXentix/prox-neurix-1b"
  ```
- `backend/training/resume.py` will query your private HF Model repo. If a previous checkpoint exists (e.g. Kaggle rebooted), it will auto-resume.
- `CheckpointManager` monitors disk space. It guarantees that only the **latest 2** local checkpoints are kept on Kaggle disk.
- It safely uploads new checkpoints to HF, verifies the upload via SHA-256, and deletes the oldest local checkpoint.

### 6. Final Inference Export
- Once training completes, the pipeline automatically strips optimizer and scheduler states.
- It exports `inference_model.pt` containing only weights, model config, and tokenizer metadata.
- This final artifact is automatically uploaded to the Hugging Face Model repository.

## Important Directives
- **NEVER** push code from Kaggle back to GitHub.
- If Kaggle crashes, simply restart the notebook and run the training command again. The resume architecture handles the rest.
- Do not manually adjust `TARGET_CONFIG` to fake the 1B tokens; let the pipeline stream and count them.
