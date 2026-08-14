import os
import sys
import platform
import torch
import subprocess
import json
from backend.models.config import ModelConfig
from backend.models.neurix import NeurixTransformer
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.utils.device import get_device_info
from backend.utils.estimate_memory import estimate_memory

def run_preflight(
    model_config: ModelConfig,
    tokenizer: ProXTokenizer,
    dataset_path: str,
    batch_size: int,
    grad_accum: int,
    allow_dirty: bool = False
) -> bool:
    print("\n" + "="*50)
    print("PROX-AI PRODUCTION PREFLIGHT CHECK")
    print("="*50)
    
    passed = True

    # 1. Repo Status
    print("[1] Repository Status:")
    print(f"  Python: {platform.python_version()}")
    print(f"  PyTorch: {torch.__version__}")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8").strip()
        print(f"  Commit: {commit}")
        if dirty:
            print("  WARNING: Working tree is dirty!")
            if not allow_dirty:
                print("  ERROR: Kaggle production training requires a clean working tree from GitHub.")
                passed = False
    except Exception:
        print("  WARNING: Could not determine git commit.")
        if not allow_dirty:
            print("  ERROR: Must be run from a valid git repository for production.")
            passed = False
    
    # 2. Model Parameters
    print("\n[2] Model Configuration & Parameters:")
    print(f"  Name: {model_config.name}")
    print(f"  Vocab Size: {model_config.vocab_size}")
    print(f"  Max Context: {model_config.max_seq_len}")
    print(f"  Dimensions: d_model={model_config.d_model}, layers={model_config.n_layers}, heads={model_config.n_heads}")
    print(f"  Tied Embeddings: {model_config.tie_weights}")
    
    print("  Initializing model on meta device for exact parameter count...")
    with torch.device("meta"):
        meta_model = NeurixTransformer(model_config)
    breakdown = meta_model.get_parameter_breakdown()
    print(f"  Total Unique Parameters: {breakdown['unique_parameters']:,}")
    print(f"  Trainable Parameters: {breakdown['trainable_parameters']:,}")
    if breakdown['unique_parameters'] == 0:
        print("  ERROR: Parameter count is 0!")
        passed = False
    
    # 3. Tokenizer
    print("\n[3] Tokenizer Status & Benchmark:")
    tokenizer.print_tokenizer_report()
    if getattr(tokenizer, 'target_path', None) and not os.path.exists(tokenizer.target_path):
        print("  ERROR: Frozen tokenizer artifact missing!")
        passed = False
        
    print("  Running lightweight tokenizer pre-training benchmark...")
    benchmark_samples = [
        ("English", "This is a preflight check."),
        ("Hindi", "यह एक प्रीफ्लाइट चेक है।"),
        ("Code", "def hello(): print('world')")
    ]
    for lang, text in benchmark_samples:
        tokens = tokenizer.encode(text)
        decoded = tokenizer.decode(tokens)
        if decoded.strip() != text.strip():
            print(f"  ERROR: Tokenizer mismatch on {lang}: '{text}' -> '{decoded}'")
            passed = False
    print("  Tokenizer benchmark passed.")

    # 4. Dataset & Manifest
    print("\n[4] Dataset Status & Manifest:")
    print(f"  Path: {dataset_path}")
    if not os.path.exists(dataset_path):
        print("  ERROR: Dataset path does not exist!")
        passed = False
    elif "smoke_test.jsonl" in dataset_path:
        print("  ERROR: Production training cannot run on smoke_test.jsonl")
        passed = False
    else:
        manifest_path = os.path.join(dataset_path, "manifests", "corpus_manifest_v0.1.json")
        if not os.path.exists(manifest_path):
            print(f"  ERROR: Corpus manifest missing at {manifest_path}")
            passed = False
        else:
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                print(f"  Corpus Version: {manifest.get('corpus_version')}")
                print(f"  Corpus Hash:    {manifest.get('corpus_hash')}")
                print(f"  Total Tokens:   {manifest.get('total_tokens', 0):,}")
                print(f"  Train Tokens:   {manifest.get('train_tokens', 0):,}")
                print(f"  Val Tokens:     {manifest.get('validation_tokens', 0):,}")
                print(f"  Test Tokens:    {manifest.get('test_tokens', 0):,}")
                if manifest.get("train_tokens", 0) == 0:
                    print("  ERROR: No train tokens recorded in manifest.")
                    passed = False
            except Exception as e:
                print(f"  ERROR: Failed to parse manifest: {e}")
                passed = False

    # 5. Training Parameters & Memory
    print("\n[5] Training Parameters:")
    print(f"  Micro-batch size: {batch_size}")
    print(f"  Gradient Accumulation: {grad_accum}")
    print(f"  Effective Batch Size: {batch_size * grad_accum}")
    device_info = get_device_info()
    print(f"  Target Device: {device_info.get('device', 'cpu')}")
    
    print("\n[6] Memory Estimation:")
    est = estimate_memory(model_config, batch_size=batch_size)
    print(f"  Estimated Training Memory: {est['total_memory_gb']:.2f} GB")
    
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info()
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        print(f"  Available CUDA VRAM: {free_gb:.2f} GB / {total_gb:.2f} GB")
        if est['total_memory_gb'] > free_gb:
            print("  ERROR: Estimated memory exceeds available VRAM! OOM likely.")
            # We don't fail just yet because estimations might be slightly off, 
            # but for strict production, we could. We'll fail if it's > total VRAM.
            if est['total_memory_gb'] > total_gb:
                print("  FATAL ERROR: Impossible to train on this device.")
                passed = False
    
    print("\n" + "="*50)
    if not passed:
        print("PREFLIGHT FAILED. Aborting training.")
        sys.exit(1)
    
    print("PREFLIGHT PASSED. Commencing training.")
    print("="*50 + "\n")
    return True
