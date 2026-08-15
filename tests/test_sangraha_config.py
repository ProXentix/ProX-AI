import pytest
from backend.datasets.config import DATASET_REGISTRY, get_scaled_target_config
from backend.datasets.categories import DataCategory

def test_sangraha_verified_hin_source_construction():
    hindi_sources = [ds for ds in DATASET_REGISTRY if ds.get("category") == "hindi"]
    assert len(hindi_sources) == 1
    ds = hindi_sources[0]
    assert ds["dataset_name"] == "Sangraha Verified (Hindi)"
    assert ds["subset"] == "verified/hin"
    assert ds["language"] == "hi"
    assert "unverified/hin" in ds["fallback"]

def test_sangraha_language_specific_data_dir():
    indic_sources = [ds for ds in DATASET_REGISTRY if ds.get("category") == "other_indic"]
    assert len(indic_sources) == 10
    
    expected_langs = {"bn", "gu", "kn", "ml", "mr", "or", "pa", "ta", "te", "ur"}
    actual_langs = {ds["language"] for ds in indic_sources}
    assert expected_langs == actual_langs
    
    for ds in indic_sources:
        assert ds["subset"].startswith("verified/")
        assert "unverified/" in ds["fallback"]

def test_other_indic_multi_language_source_routing():
    # Verify that all target indic languages are routed properly to other_indic
    indic_sources = [ds for ds in DATASET_REGISTRY if ds.get("category") == "other_indic"]
    for ds in indic_sources:
        assert ds["category"] == DataCategory.OTHER_INDIC.value
        assert ds["dataset_id"] == "ai4bharat/sangraha"

def test_target_enforcement():
    config = get_scaled_target_config(1_000_000_000)
    assert config["category_targets"]["hindi"] == 150_000_000
    assert config["category_targets"]["other_indic"] == 25_000_000

