import os
import tempfile
from backend.datasets.loader import LocalDatasetLoader
from backend.datasets.categories import classify_document, DataCategory

def test_dataset_loader_multi_format():
    with tempfile.TemporaryDirectory() as tmp_dir:
        txt_file = os.path.join(tmp_dir, "doc.txt")
        jsonl_file = os.path.join(tmp_dir, "data.jsonl")
        proxpl_file = os.path.join(tmp_dir, "main.proxpl")

        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("General text document content.")
        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write('{"text": "JSONL line 1"}\n{"text": "JSONL line 2"}\n')
        with open(proxpl_file, "w", encoding="utf-8") as f:
            f.write("fn main() { let x: int = 42; }")

        loader = LocalDatasetLoader(tmp_dir)
        docs = loader.load_documents()
        assert len(docs) == 4

        texts = [d["text"] for d in docs]
        assert "General text document content." in texts
        assert "JSONL line 1" in texts
        assert "fn main() { let x: int = 42; }" in texts

def test_dataset_category_classification():
    cat_py = classify_document("def add(a, b): return a + b", "script.py")
    assert cat_py == DataCategory.PROGRAMMING_LANGUAGES

    cat_md = classify_document("# Title\nDocumentation", "readme.md")
    assert cat_md == DataCategory.TECHNICAL_DOCUMENTATION

    cat_prox = classify_document("fn main() { println!(\"Hi\"); }", "app.proxpl")
    assert cat_prox == DataCategory.PROXPL
