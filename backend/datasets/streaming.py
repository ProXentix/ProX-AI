import os
import json
from typing import Generator, List
from backend.tokenizer.tokenizer import ProXTokenizer

class LocalDatasetStreamer:
    """Stream text tokens incrementally from local JSONL/TXT corpora for zero-RAM overhead."""
    def __init__(self, data_path: str, tokenizer: ProXTokenizer, max_seq_len: int = 2048):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len

    def stream_token_chunks(self) -> Generator[List[int], None, None]:
        buffer = []
        if os.path.isfile(self.data_path):
            with open(self.data_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    text = line
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            obj = json.loads(line)
                            text = obj.get("text", line)
                        except Exception:
                            pass
                    tokens = self.tokenizer.encode(text) + [self.tokenizer.eos_token_id]
                    buffer.extend(tokens)
                    while len(buffer) >= self.max_seq_len + 1:
                        chunk = buffer[: self.max_seq_len + 1]
                        buffer = buffer[self.max_seq_len + 1 :]
                        yield chunk
