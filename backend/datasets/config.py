import os
from typing import Dict, Any

TARGET_CONFIG: Dict[str, Any] = {
    "target_total_tokens": 100_000_000,
    "category_targets": {
        "general_natural_language": 45_000_000,
        "programming_languages": 30_000_000,
        "technical_documentation": 10_000_000,
        "proxpl": 10_000_000,
        "mathematics_reasoning": 5_000_000,
    },
    "validation_ratio": 0.10,
}

def get_scaled_target_config(target_tokens: int) -> Dict[str, Any]:
    """Scales category targets proportionally for smaller test builds (e.g. 100k, 1M)."""
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
        "validation_ratio": TARGET_CONFIG["validation_ratio"],
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
