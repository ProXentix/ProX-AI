import os
import json
import glob
from typing import List, Dict, Any
from backend.datasets.categories import classify_document, DataCategory

class LocalDatasetLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.supported_exts = (".txt", ".jsonl", ".json", ".md", ".py", ".ts", ".js", ".c", ".cpp", ".proxpl", ".rs", ".go", ".rst")

    def _get_files(self) -> List[str]:
        if os.path.isfile(self.data_path):
            return [self.data_path]
        elif os.path.isdir(self.data_path):
            files = []
            for ext in self.supported_exts:
                files.extend(glob.glob(os.path.join(self.data_path, f"**/*{ext}"), recursive=True))
            return files
        else:
            raise FileNotFoundError(f"Dataset path {self.data_path} not found.")

    def load_documents(self) -> List[Dict[str, Any]]:
        """Loads files into structured document records with text, category, metadata, and byte counts."""
        files = self._get_files()
        documents = []
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            try:
                if file_path.endswith(".jsonl"):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                item = json.loads(line)
                                text = item.get("text", "") if isinstance(item, dict) else str(item)
                                if text:
                                    cat = classify_document(text, file_path)
                                    documents.append({
                                        "text": text,
                                        "file_path": file_path,
                                        "category": cat.value,
                                        "format": "jsonl",
                                        "bytes": len(text.encode("utf-8")),
                                    })
                elif file_path.endswith(".json"):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                        items = data if isinstance(data, list) else [data]
                        for item in items:
                            text = item.get("text", json.dumps(item)) if isinstance(item, dict) else str(item)
                            if text:
                                cat = classify_document(text, file_path)
                                documents.append({
                                    "text": text,
                                    "file_path": file_path,
                                    "category": cat.value,
                                    "format": "json",
                                    "bytes": len(text.encode("utf-8")),
                                })
                else:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                        if content:
                            cat = classify_document(content, file_path)
                            documents.append({
                                "text": content,
                                "file_path": file_path,
                                "category": cat.value,
                                "format": ext.lstrip("."),
                                "bytes": len(content.encode("utf-8")),
                            })
            except Exception as e:
                print(f"[DatasetLoader] Error loading {file_path}: {e}")
        return documents

    def load_texts(self) -> List[str]:
        """Convenience method returning raw text strings."""
        return [doc["text"] for doc in self.load_documents()]
