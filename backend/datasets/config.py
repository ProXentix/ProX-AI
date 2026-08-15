import os
import json
from typing import Dict, Any, List, Tuple, Optional

PRODUCTION_MODE = os.environ.get("PROX_PRODUCTION_MODE", "0") == "1"

TARGET_CONFIG: Dict[str, Any] = {
    "target_total_tokens": 1_000_000_000,
    "category_targets": {
        "general_natural_language": 350_000_000,
        "programming_languages": 250_000_000,
        "technical_documentation": 150_000_000,
        "hindi": 150_000_000,
        "mathematics_reasoning": 75_000_000,
        "other_indic": 25_000_000,
    },
    "validation_ratio": 0.05,
    "test_ratio": 0.05,
}

# Per-language programming targets (percentage breakdown of 250M target)
PROGRAMMING_LANGUAGE_TARGETS: Dict[str, float] = {
    "python": 0.20,
    "c": 0.08,
    "cpp": 0.10,
    "javascript": 0.10,
    "typescript": 0.08,
    "rust": 0.08,
    "go": 0.06,
    "java": 0.10,
    "sql": 0.04,
    "csharp": 0.04,
    "kotlin": 0.03,
    "swift": 0.03,
    "shell": 0.03,
    "html_css": 0.02,
    "proxpl": 0.01,
}

# Canonical programming language directory mapping for Hugging Face datasets (e.g. bigcode/the-stack-smol)
PROGRAMMING_DATA_DIRS: Dict[str, str] = {
    "python": "data/python",
    "c": "data/c",
    "cpp": "data/c++",
    "javascript": "data/javascript",
    "typescript": "data/typescript",
    "rust": "data/rust",
    "go": "data/go",
    "java": "data/java",
    "sql": "data/sql",
    "csharp": "data/csharp",
    "kotlin": "data/kotlin",
    "swift": "data/swift",
    "shell": "data/shell",
    "html_css": "data/html",
    "proxpl": "data/proxpl",
}

DATASET_REGISTRY: List[Dict[str, Any]] = [
    {
        "dataset_name": "FineWeb-Edu",
        "dataset_id": "HuggingFaceFW/fineweb-edu",
        "subset": "sample-10BT",
        "category": "general_natural_language",
        "auth_required": False,
        "fallback": "wikimedia/wikipedia (20231101.en)",
        "license": "ODC-By 1.0"
    },
    {
        "dataset_name": "The Stack Smol (Python)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["python"],
        "category": "programming_languages",
        "language": "python",
        "auth_required": True,
        "fallback": "codeparrot/codeparrot-clean-train",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (C)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["c"],
        "category": "programming_languages",
        "language": "c",
        "auth_required": True,
        "fallback": "m-a-p/code_bagel (c_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (C++)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["cpp"],
        "category": "programming_languages",
        "language": "cpp",
        "auth_required": True,
        "fallback": "m-a-p/code_bagel (cpp_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (JavaScript)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["javascript"],
        "category": "programming_languages",
        "language": "js",
        "auth_required": True,
        "fallback": "bigcode/starcoderdata (js_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (TypeScript)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["typescript"],
        "category": "programming_languages",
        "language": "ts",
        "auth_required": True,
        "fallback": "bigcode/starcoderdata (ts_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (Rust)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["rust"],
        "category": "programming_languages",
        "language": "rust",
        "auth_required": True,
        "fallback": "bigcode/starcoderdata (rust_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (Go)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["go"],
        "category": "programming_languages",
        "language": "go",
        "auth_required": True,
        "fallback": "bigcode/starcoderdata (go_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "The Stack Smol (Java)",
        "dataset_id": "bigcode/the-stack-smol",
        "subset": PROGRAMMING_DATA_DIRS["java"],
        "category": "programming_languages",
        "language": "java",
        "auth_required": True,
        "fallback": "bigcode/starcoderdata (java_subset)",
        "license": "BigCode Terms / Apache-2.0"
    },
    {
        "dataset_name": "CodeXGlue NL/Code Search",
        "dataset_id": "google/code_x_glue_tc_nl_code_search_adv",
        "subset": "default",
        "category": "technical_documentation",
        "auth_required": False,
        "fallback": "None Required",
        "license": "Apache-2.0"
    },
    {
        "dataset_name": "AG News Sci/Tech",
        "dataset_id": "fancyzhx/ag_news",
        "subset": "default",
        "category": "technical_documentation",
        "auth_required": False,
        "fallback": "None Required",
        "license": "Academic / Public News"
    },
    {
        "dataset_name": "OpenWebMath",
        "dataset_id": "open-web-math/open-web-math",
        "subset": "default",
        "category": "mathematics_reasoning",
        "auth_required": False,
        "fallback": "None Required",
        "license": "ODC-By 1.0"
    },
    {
        "dataset_name": "Sangraha Verified (Hindi)",
        "dataset_id": "ai4bharat/sangraha",
        "subset": "verified/hin",
        "category": "hindi",
        "language": "hi",
        "auth_required": False,
        "fallback": "ai4bharat/sangraha (unverified/hin)",
        "license": "Indic Permissive"
    }
]

_INDIC_LANGS = {
    "ben": "bn", "guj": "gu", "kan": "kn", "mal": "ml",
    "mar": "mr", "ori": "or", "pan": "pa", "tam": "ta",
    "tel": "te", "urd": "ur"
}

for _lang_code, _iso_code in _INDIC_LANGS.items():
    DATASET_REGISTRY.append({
        "dataset_name": f"Sangraha Verified ({_lang_code})",
        "dataset_id": "ai4bharat/sangraha",
        "subset": f"verified/{_lang_code}",
        "category": "other_indic",
        "language": _iso_code,
        "auth_required": False,
        "fallback": f"ai4bharat/sangraha (unverified/{_lang_code})",
        "license": "Indic Permissive"
    })

def check_hf_authentication() -> Dict[str, Any]:
    """Returns structured state about Hugging Face authentication."""
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    state = {
        "authenticated": False,
        "username": None,
        "token_source": "HF_TOKEN" if os.getenv("HF_TOKEN") else ("HUGGINGFACE_TOKEN" if os.getenv("HUGGINGFACE_TOKEN") else "NONE"),
        "api_reachable": False
    }

    if not token or len(token.strip()) < 5:
        try:
            from huggingface_hub import get_token
            token = get_token()
            if token:
                state["token_source"] = "huggingface_hub"
        except Exception:
            pass

    if not token or len(token.strip()) < 5:
        return state

    try:
        from huggingface_hub import HfApi
        api = HfApi()
        user_info = api.whoami(token=token.strip())
        state["api_reachable"] = True
        if user_info and "name" in user_info:
            state["authenticated"] = True
            state["username"] = user_info["name"]
    except Exception:
        import urllib.request
        try:
            urllib.request.urlopen("https://huggingface.co", timeout=3)
            state["api_reachable"] = True
        except Exception:
            state["api_reachable"] = False
            
    return state

def get_scaled_target_config(target_tokens: int) -> Dict[str, Any]:
    """Scales category targets proportionally for test builds (e.g. 100k, 1M, 10M)."""
    base_total = TARGET_CONFIG["target_total_tokens"]
    scale = target_tokens / float(base_total)
    
    scaled_categories = {}
    total_acc = 0
    cat_keys = list(TARGET_CONFIG["category_targets"].keys())
    
    for idx, key in enumerate(cat_keys):
        if idx == len(cat_keys) - 1:
            scaled_categories[key] = max(1, target_tokens - total_acc)
        else:
            cat_val = int(TARGET_CONFIG["category_targets"][key] * scale)
            scaled_categories[key] = cat_val
            total_acc += cat_val
            
    return {
        "target_total_tokens": target_tokens,
        "category_targets": scaled_categories,
        "validation_ratio": TARGET_CONFIG.get("validation_ratio", 0.05),
        "test_ratio": TARGET_CONFIG.get("test_ratio", 0.05),
    }

def validate_target_config(config: Dict[str, Any]) -> bool:
    """Validates that category targets sum exactly to the target_total_tokens and meet production requirements."""
    cat_targets = config.get("category_targets", {})
    total_target = config.get("target_total_tokens", 0)
    
    if total_target <= 0:
        raise ValueError(f"Configuration Error: target_total_tokens must be positive, got {total_target}")
        
    required_categories = {
        "general_natural_language", "programming_languages", 
        "technical_documentation", "hindi", "mathematics_reasoning", "other_indic"
    }
    
    missing_cats = required_categories - set(cat_targets.keys())
    if missing_cats:
        raise ValueError(f"Configuration Error: Missing required categories: {missing_cats}")
        
    for cat, target in cat_targets.items():
        if target < 0:
            raise ValueError(f"Configuration Error: Category {cat} has negative target ({target})")

    sum_cats = sum(cat_targets.values())
    if sum_cats != total_target:
        raise ValueError(
            f"Configuration Error: Sum of category targets ({sum_cats:,}) "
            f"does not equal total target tokens ({total_target:,})."
        )
        
    val_ratio = config.get("validation_ratio", 0.0)
    test_ratio = config.get("test_ratio", 0.0)
    if not (0.0 <= val_ratio <= 1.0) or not (0.0 <= test_ratio <= 1.0) or (val_ratio + test_ratio >= 1.0):
        raise ValueError(f"Configuration Error: Invalid split ratios (val={val_ratio}, test={test_ratio})")
        
    return True

def audit_dataset_sources(hf_token_status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Performs dry-run dataset accessibility audit without reading full dataset payloads."""
    audit_results = []
    is_authenticated = hf_token_status.get("authenticated", False)

    for ds in DATASET_REGISTRY:
        ds_id = ds["dataset_id"]
        auth_req = ds["auth_required"]

        if auth_req and not is_authenticated:
            accessible = False
            if PRODUCTION_MODE:
                status = "GATED_UNAUTHENTICATED (FATAL: Production mode requires auth)"
            else:
                status = "GATED_UNAUTHENTICATED (Fallback Active)"
        else:
            accessible = True
            status = "ACCESSIBLE"

        audit_results.append({
            "dataset_name": ds["dataset_name"],
            "dataset_id": ds_id,
            "subset": ds["subset"],
            "category": ds["category"],
            "language": ds.get("language", "en"),
            "auth_required": auth_req,
            "accessible": accessible,
            "status": status,
            "fallback": "DISABLED" if PRODUCTION_MODE else ds["fallback"],
            "license": ds["license"],
            "fallback_allowed": not PRODUCTION_MODE,
            "production_allowed": True
        })

    return audit_results
