import os
import tempfile
from backend.datasets.manifest import DatasetManifestGenerator

def test_dataset_manifest_generation():
    documents = [
        {"text": "Natural language document.", "format": "txt"},
        {"text": "# Technical Documentation\nStep 1: Install system.", "format": "md"},
        {"text": "def calculate(a, b):\n    return a + b", "format": "py"},
    ]

    generator = DatasetManifestGenerator(dataset_name="TestCorpus", dataset_version="v0.1")
    manifest = generator.build_manifest(documents)

    assert manifest["dataset_name"] == "TestCorpus"
    assert manifest["dataset_version"] == "v0.1"
    assert manifest["summary_statistics"]["clean_document_count"] == 3
    assert len(manifest["dataset_hash"]) == 64
    assert "category_distribution" in manifest
    assert "proxpl" not in manifest["category_distribution"]
    assert "general_natural_language" in manifest["category_distribution"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "dataset_manifest.json")
        saved_path = generator.save_manifest(manifest, out_path)
        assert os.path.exists(saved_path)
