import os
import json
import time
import socket
from typing import Generator, List, Dict, Any, Callable

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

class RobustNetworkStreamer:
    """Handles transient Windows network socket errors ([WinError 10038]), timeouts, and HF stream reconnects."""
    def __init__(self, max_retries: int = 5, initial_backoff: float = 2.0):
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.retry_stats = {
            "NETWORK_RETRY_SUCCESS": 0,
            "NETWORK_RETRY_EXHAUSTED": 0,
            "SOURCE_FAILED": 0,
            "SOURCE_FALLBACK_USED": 0
        }

    def safe_stream(self, dataset_generator_builder: Callable[[], Generator[Dict[str, Any], None, None]], source_name: str) -> Generator[Dict[str, Any], None, None]:
        retries = 0
        backoff = self.initial_backoff
        
        while retries <= self.max_retries:
            ds_iter = None
            try:
                ds_iter = dataset_generator_builder()
                for item in ds_iter:
                    yield item
                # Completed successfully
                return
            except GeneratorExit:
                return
            except (OSError, socket.error, TimeoutError, ConnectionResetError, Exception) as e:
                err_str = str(e)
                retries += 1
                if retries > self.max_retries:
                    print(f"[{source_name}] NETWORK_RETRY_EXHAUSTED after {self.max_retries} attempts: {err_str}", flush=True)
                    self.retry_stats["NETWORK_RETRY_EXHAUSTED"] += 1
                    self.retry_stats["SOURCE_FAILED"] += 1
                    raise e
                
                print(
                    f"[{source_name}] Transient network/socket warning ({err_str[:60]}...). "
                    f"Re-initializing stream (Attempt {retries}/{self.max_retries} in {backoff:.1f}s)...",
                    flush=True
                )
                self.retry_stats["NETWORK_RETRY_SUCCESS"] += 1
                time.sleep(backoff)
                backoff *= 2.0
            finally:
                if ds_iter is not None:
                    if hasattr(ds_iter, "close") and callable(getattr(ds_iter, "close")):
                        try:
                            ds_iter.close()
                        except Exception:
                            pass
                    if hasattr(ds_iter, "_ex_iterable") and hasattr(ds_iter._ex_iterable, "close") and callable(getattr(ds_iter._ex_iterable, "close")):
                        try:
                            ds_iter._ex_iterable.close()
                        except Exception:
                            pass
