# Kaggle Training Workflow

This document explicitly defines the strict unidirectional workflow for developing and training ProX-AI.

## Architecture

1. **GitHub (Source of Truth)**: ALL code, configurations, tests, and documentation live here.
2. **Kaggle (Disposable Compute)**: Executes the exact code from GitHub.
3. **Hugging Face (Persistent Storage)**:
   - **HF Dataset**: Stores the generated 1B corpus.
   - **HF Model**: Stores checkpoints and final weights.

## The Workflow

### 1. Local Development
- Write code, edit `backend/` files, update configs locally.
- Run `pytest -v` locally.
- **Commit & Push** to GitHub.

### 2. Kaggle Preparation
- Open a fresh Kaggle Notebook.
- Add GitHub credentials or public URL.
- **Clone/Pull** the repository from GitHub.
- **Checkout** the exact commit hash you want to train.
- Install dependencies (`pip install -r requirements.txt`).

### 3. Preflight & Integrity Checks
The system will run `backend/training/preflight.py`.
- **CRITICAL**: If the git working tree is dirty, preflight will abort. Kaggle notebooks MUST NOT have manually edited source code files in `/kaggle/working`.
- The git commit hash and clean status are injected into the training state and uploaded to Hugging Face.

### 4. Corpus Generation & Upload
- Run `python scripts/build_prox_corpus.py` on Kaggle.
- Run `python scripts/upload_corpus_to_hf.py --repo_id "ProXentix/prox-corpus"` to stream the corpus to a private Hugging Face Dataset repository.
- Wait for remote verification.
- **Cleanup**: Delete local `/kaggle/working/prox_training_corpus` to free disk space.

### 5. Training & Resuming
- Execute `train.py`.
- `backend/training/resume.py` will query your private HF Model repo. If a previous checkpoint exists, it will download it, verify the SHA256 checksum, and inject the weights and optimizer states into the run seamlessly.
- During training, `CheckpointManager` monitors disk space. It guarantees that only the **latest 2** local checkpoints are kept on Kaggle disk.
- It safely uploads new checkpoints to HF, verifies the upload, and deletes the oldest local checkpoint.

## Error Recovery
- **Network Failure**: If an upload fails, `CheckpointManager` will keep the local checkpoint and retry later.
- **Notebook Restart**: If Kaggle kills the notebook, just restart it. The resume logic will automatically find the latest verified HF checkpoint and continue exactly where it left off.
- **Storage Limit**: If Kaggle hits the 73GB limit, the checkpoint manager checks disk space before saving and aggressively prunes verified checkpoints.

**NEVER TREAT KAGGLE AS THE SOURCE OF TRUTH.** If there is a bug, fix it on your local machine, push to GitHub, and pull on Kaggle.
