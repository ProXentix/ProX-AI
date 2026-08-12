import os
import json
import gzip
from typing import Dict, Any, Optional

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

class ShardedCorpusWriter:
    """Memory-efficient sharded corpus writer supporting jsonl, gz, and zst compression."""
    def __init__(
        self,
        output_dir: str,
        prefix: str = "shard",
        max_records_per_shard: int = 10000,
        use_compression: bool = True
    ):
        self.output_dir = output_dir
        self.prefix = prefix
        self.max_records_per_shard = max_records_per_shard
        self.use_compression = use_compression
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.shard_index = 0
        self.current_record_count = 0
        self.total_records_written = 0
        self.current_file = None

        if use_compression and HAS_ZSTD:
            self.extension = ".jsonl.zst"
        elif use_compression:
            self.extension = ".jsonl.gz"
        else:
            self.extension = ".jsonl"

        self.shard_index = self._detect_next_shard_index()
        self.current_record_count = 0
        self.total_records_written = 0
        self.current_file = None
        self._raw_file = None

    def _detect_next_shard_index(self) -> int:
        highest = -1
        if os.path.exists(self.output_dir):
            for fname in os.listdir(self.output_dir):
                if fname.startswith(f"{self.prefix}-") and (".jsonl" in fname):
                    parts = fname[len(self.prefix) + 1:].split(".")
                    if parts and parts[0].isdigit():
                        idx = int(parts[0])
                        if idx > highest:
                            highest = idx
        return highest + 1

    def _open_next_shard(self):
        self.close()

        filename = f"{self.prefix}-{self.shard_index:05d}{self.extension}"
        filepath = os.path.join(self.output_dir, filename)

        if self.extension == ".jsonl.zst" and HAS_ZSTD:
            cctx = zstd.ZstdCompressor(level=3)
            self._raw_file = open(filepath, "wb")
            self.current_file = cctx.stream_writer(self._raw_file)
        elif self.extension == ".jsonl.gz":
            self.current_file = gzip.open(filepath, "wt", encoding="utf-8")
        else:
            self.current_file = open(filepath, "w", encoding="utf-8")

        self.shard_index += 1
        self.current_record_count = 0

    def write_record(self, record: Dict[str, Any]):
        if self.current_file is None or self.current_record_count >= self.max_records_per_shard:
            self._open_next_shard()

        line = json.dumps(record, ensure_ascii=False) + "\n"
        if self.extension == ".jsonl.zst" and HAS_ZSTD:
            self.current_file.write(line.encode("utf-8"))
        else:
            self.current_file.write(line)

        self.current_record_count += 1
        self.total_records_written += 1

    def close(self):
        if self.current_file is not None:
            try:
                self.current_file.close()
            except Exception:
                pass
            self.current_file = None
        if self._raw_file is not None:
            try:
                self._raw_file.close()
            except Exception:
                pass
            self._raw_file = None
