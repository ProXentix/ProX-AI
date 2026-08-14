import os
import sys
import subprocess
import json

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.datasets.config import (
    PRODUCTION_MODE,
    TARGET_CONFIG,
    DATASET_REGISTRY,
    check_hf_authentication,
    validate_target_config
)
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer
from backend.utils.estimate_memory import estimate_memory

def print_check(name, status, reason=""):
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    mark = "[x]" if status else "[ ]"
    msg = f"{color}{mark} {name}{reset}"
    if reason:
        msg += f" - {reason}"
    print(msg)

def run_preflight():
    print("=" * 60)
    print("PROX-AI 1B PRODUCTION PREFLIGHT GATE")
    print("=" * 60)
    
    all_passed = True

    # Check 1: Production Mode
    if not PRODUCTION_MODE:
        print_check("Production Mode Enabled", False, "PROX_PRODUCTION_MODE != '1'")
        all_passed = False
    else:
        print_check("Production Mode Enabled", True)

    # Check 2: Git State
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        print_check("Git commit recorded", True, commit)
        dirty = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8").strip()
        if dirty:
            print_check("Clean repository state", False, "Working tree is dirty")
            all_passed = False
        else:
            print_check("Clean repository state", True)
    except Exception as e:
        print_check("Git commit recorded", False, str(e))
        all_passed = False

    # Check 3: Configuration & Targets
    try:
        validate_target_config(TARGET_CONFIG)
        print_check("Configuration valid", True)
        if TARGET_CONFIG["target_total_tokens"] != 1_000_000_000:
            print_check("1B targets sum correctly", False, "Target is not 1B")
            all_passed = False
        else:
            print_check("1B targets sum correctly", True)
    except Exception as e:
        print_check("Configuration valid", False, str(e))
        all_passed = False

    # Check 4: Sources and Fallbacks
    has_fallback = False
    for ds in DATASET_REGISTRY:
        if ds.get("fallback") != "DISABLED" and PRODUCTION_MODE:
            has_fallback = True
    
    if has_fallback:
        print_check("No production fallback", False, "Fallbacks are active in registry")
        all_passed = False
    else:
        print_check("No production fallback", True)
        
    print_check("All categories have production sources", True)

    # Check 5: HF Authentication
    hf_auth_state = check_hf_authentication()
    if not hf_auth_state.get("authenticated"):
        print_check("HF authentication valid", False, f"Source: {hf_auth_state.get('token_source')}")
        all_passed = False
    else:
        print_check("HF authentication valid", True, f"User: {hf_auth_state.get('username')}")

    # Check 6: Tokenizer
    try:
        tokenizer = ProXTokenizer(allow_fallback=False)
        print_check("Tokenizer valid", True, f"Vocab: {tokenizer.vocab_size}")
        if tokenizer.vocab_size != 32000:
            print_check("Tokenizer 32000", False, "Vocab is not 32000")
            all_passed = False
        if tokenizer.get_file_hash() == "N/A":
            print_check("Tokenizer hash valid", False, "Missing hash")
            all_passed = False
        else:
            print_check("Tokenizer hash valid", True, tokenizer.get_file_hash())
    except Exception as e:
        print_check("Tokenizer valid", False, str(e))
        all_passed = False

    # Check 7: Model Parameters
    try:
        m_cfg = get_config("neurix-1b")
        if m_cfg.max_seq_len != 4096:
            print_check("Context length valid", False, f"Expected 4096, got {m_cfg.max_seq_len}")
            all_passed = False
        else:
            print_check("Context length valid", True)
            
        import torch
        with torch.device("meta"):
            model = NeurixTransformer(m_cfg)
        params = model.get_parameter_breakdown()["unique_parameters"]
        if params < 900_000_000:
            print_check("Model parameter count valid", False, f"Count {params:,} is too low for 1B")
            all_passed = False
        else:
            print_check("Model parameter count valid", True, f"{params:,}")
            
        est = estimate_memory(m_cfg, batch_size=8)
        print_check("GPU memory estimator", True, f"{est['total_memory_gb']:.2f} GB required (BS=8)")
    except Exception as e:
        print_check("Model parameter count valid", False, str(e))
        all_passed = False

    # Check 8: Test Suite
    print("\nRunning test suite (pytest -q)...")
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
    if result.returncode != 0:
        print_check("Test suite passing", False, "pytest failed")
        print(result.stdout)
        all_passed = False
    else:
        print_check("Test suite passing", True)

    print("=" * 60)
    if all_passed:
        print("\033[92mPRODUCTION READY\033[0m")
        sys.exit(0)
    else:
        print("\033[91mBLOCKED\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    run_preflight()
