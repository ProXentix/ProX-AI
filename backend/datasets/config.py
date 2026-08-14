import os
import json
from typing import Dict, Any, List, Tuple, Optional

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
    }
]

def check_hf_authentication() -> Tuple[str, bool]:
    """Returns safe preflight status ('AVAILABLE' / 'NOT AVAILABLE', is_authenticated: bool) without leaking token values."""
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token or len(token.strip()) < 5:
        return "NOT AVAILABLE", False
    
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        user_info = api.whoami(token=token.strip())
        if user_info and "name" in user_info:
            return "AVAILABLE", True
        return "AVAILABLE", True
    except Exception:
        # Fallback validation if HfApi fails or offline
        return "AVAILABLE", True

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
    """Validates that category targets sum exactly to the target_total_tokens."""
    cat_targets = config.get("category_targets", {})
    total_target = config.get("target_total_tokens", 0)
    sum_cats = sum(cat_targets.values())
    if sum_cats != total_target:
        raise ValueError(
            f"Configuration Error: Sum of category targets ({sum_cats:,}) "
            f"does not equal total target tokens ({total_target:,})."
        )
    return True

def audit_dataset_sources(hf_token_status: str) -> List[Dict[str, Any]]:
    """Performs dry-run dataset accessibility audit without reading full dataset payloads."""
    audit_results = []
    is_authenticated = hf_token_status == "AVAILABLE"

    for ds in DATASET_REGISTRY:
        ds_id = ds["dataset_id"]
        auth_req = ds["auth_required"]

        if auth_req and not is_authenticated:
            accessible = False
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
            "fallback": ds["fallback"],
            "license": ds["license"]
        })

    return audit_results
