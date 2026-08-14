import os
import sys
import glob
import argparse
import io
import json
import hashlib
import subprocess
from datetime import datetime, timezone

repo_root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from tokenizers import (
    Tokenizer,
    models,
    pre_tokenizers,
    decoders,
    trainers,
    processors,
)

from backend.tokenizer.config import TokenizerConfig


# ---------------------------------------------------------------------------
# Dataset reader
# Supports:
#   - Plain text files
#   - JSON / JSONL
#   - Markdown
#   - Source code
#   - Zstandard-compressed JSONL (.jsonl.zst / .json.zst)
# ---------------------------------------------------------------------------

SUPPORTED_PLAIN_EXTENSIONS = (
    ".txt",
    ".jsonl",
    ".json",
    ".md",
    ".py",
    ".ts",
    ".js",
    ".c",
    ".cpp",
    ".proxpl",
)

SUPPORTED_ZSTD_EXTENSIONS = (
    ".jsonl.zst",
    ".json.zst",
)


def _extract_text_from_json_line(line: str):
    """
    Extract usable text from one JSON/JSONL record.

    Preferred field:
        text

    Fallback:
        content

    Also supports a raw JSON string.
    """
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None

    if isinstance(obj, dict):
        text = obj.get("text")

        if text is None:
            text = obj.get("content")

        if text is None:
            return None

        return str(text).strip()

    if isinstance(obj, str):
        return obj.strip()

    return None


def _iter_plain_file(file_path: str):
    """
    Stream a normal text/source/JSONL file line-by-line.
    """
    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Parse JSONL/JSON records.
            if file_path.endswith((".jsonl", ".json")):
                text = _extract_text_from_json_line(line)

                if text:
                    yield text
            else:
                yield line


def _iter_zstd_jsonl(file_path: str):
    """
    Stream a Zstandard-compressed JSONL file without extracting it to disk.
    """
    try:
        import zstandard as zstd
    except ImportError as e:
        raise RuntimeError(
            "The 'zstandard' package is required to read .jsonl.zst files. "
            "Install it with: pip install zstandard"
        ) from e

    with open(file_path, "rb") as compressed_file:
        dctx = zstd.ZstdDecompressor()

        with dctx.stream_reader(compressed_file) as reader:
            text_stream = io.TextIOWrapper(
                reader,
                encoding="utf-8",
                errors="ignore",
            )

            try:
                for line in text_stream:
                    line = line.strip()

                    if not line:
                        continue

                    text = _extract_text_from_json_line(line)

                    if text:
                        yield text

            finally:
                text_stream.detach()


def get_text_iterator(dataset_path: str):
    """
    Return a streaming iterator over the training corpus.

    Supports either:
        - a single dataset file
        - a directory containing dataset shards

    Zstandard-compressed JSONL shards are streamed directly and are
    never fully decompressed into memory or written back to disk.
    """

    if os.path.isfile(dataset_path):
        files = [dataset_path]

    elif os.path.isdir(dataset_path):
        files = glob.glob(
            os.path.join(dataset_path, "**", "*"),
            recursive=True,
        )

        files = [
            file_path
            for file_path in files
            if os.path.isfile(file_path)
        ]

    else:
        raise ValueError(
            f"Dataset path '{dataset_path}' does not exist."
        )

    # Deterministic ordering.
    files.sort()

    supported_extensions = (
        SUPPORTED_PLAIN_EXTENSIONS
        + SUPPORTED_ZSTD_EXTENSIONS
    )

    processed_files = 0

    for file_path in files:
        if not file_path.endswith(supported_extensions):
            continue

        processed_files += 1

        try:
            print(
                f"[Tokenizer Trainer] Reading: {file_path}",
                flush=True,
            )

            if file_path.endswith(SUPPORTED_ZSTD_EXTENSIONS):
                yield from _iter_zstd_jsonl(file_path)
            else:
                yield from _iter_plain_file(file_path)

        except Exception as e:
            print(
                f"[Tokenizer Trainer] Warning: skipping file "
                f"{file_path}: {e}",
                flush=True,
            )

    if processed_files == 0:
        raise RuntimeError(
            "No supported dataset files were found in "
            f"'{dataset_path}'.\n"
            f"Supported plain extensions: {SUPPORTED_PLAIN_EXTENSIONS}\n"
            f"Supported compressed extensions: {SUPPORTED_ZSTD_EXTENSIONS}"
        )


# ---------------------------------------------------------------------------
# Tokenizer training
# ---------------------------------------------------------------------------

def train_tokenizer(
    dataset_path: str,
    vocab_size: int,
    output_path: str,
):
    def _get_git_commit():
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, cwd=repo_root).decode("utf-8").strip()
        except Exception:
            return "unknown"

    def _get_file_hash(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    print(
        "[Tokenizer Trainer] Training ProX BPE Tokenizer...",
        flush=True,
    )

    print(
        f"  Dataset Path: {dataset_path}",
        flush=True,
    )

    print(
        f"  Vocab Size:   {vocab_size}",
        flush=True,
    )

    print(
        f"  Output Path:  {output_path}",
        flush=True,
    )

    config = TokenizerConfig(
        vocab_size=vocab_size
    )

    # -----------------------------------------------------------------------
    # BPE tokenizer
    # -----------------------------------------------------------------------

    bpe = models.BPE(
        unk_token=config.unk_token
    )

    tokenizer = Tokenizer(bpe)

    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(
        add_prefix_space=False
    )

    tokenizer.decoder = decoders.ByteLevel()

    tokenizer.post_processor = processors.ByteLevel(
        trim_offsets=False
    )

    # -----------------------------------------------------------------------
    # BPE trainer
    # -----------------------------------------------------------------------

    trainer = trainers.BpeTrainer(
        vocab_size=config.vocab_size,
        min_frequency=config.min_frequency,
        special_tokens=config.special_tokens,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    )

    # -----------------------------------------------------------------------
    # Train directly from streaming iterator.
    #
    # Important:
    # The corpus contains .jsonl.zst shards, so get_text_iterator()
    # transparently decompresses and streams those records.
    # -----------------------------------------------------------------------

    iterator = get_text_iterator(dataset_path)

    tokenizer.train_from_iterator(
        iterator,
        trainer=trainer,
    )

    # -----------------------------------------------------------------------
    # Save tokenizer
    # -----------------------------------------------------------------------

    output_path = os.path.abspath(output_path)

    output_dir = os.path.dirname(output_path)

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    tokenizer.save(output_path)

    actual_vocab_size = tokenizer.get_vocab_size()

    if actual_vocab_size != 32000:
        raise RuntimeError(f"Tokenizer training failed: actual vocab size {actual_vocab_size} does not exactly match 32000.")

    print(
        "[Tokenizer Trainer] Tokenizer trained and saved to "
        f"{output_path} "
        f"(vocab size: {actual_vocab_size})",
        flush=True,
    )

    sha256_hash = _get_file_hash(output_path)
    sha_path = output_path.replace(".json", ".sha256")
    with open(sha_path, "w") as f:
        f.write(sha256_hash)
        
    # Generate Manifest
    manifest_path = output_path.replace(".json", "_manifest.json")
    
    # Compute a quick hash for the training corpus
    corpus_h = hashlib.sha256()
    corpus_h.update(dataset_path.encode('utf-8'))
    if os.path.isdir(dataset_path):
        for root, _, files in sorted(os.walk(dataset_path)):
            for f in sorted(files):
                fpath = os.path.join(root, f)
                corpus_h.update(f.encode('utf-8'))
                try:
                    corpus_h.update(str(os.path.getsize(fpath)).encode('utf-8'))
                except Exception:
                    pass
                    
    manifest = {
        "tokenizer_version": "ProX-Tokenizer-DEV",
        "vocab_size": actual_vocab_size,
        "sha256": sha256_hash,
        "special_tokens": config.special_tokens,
        "training_corpus_hash": corpus_h.hexdigest(),
        "training_git_commit": _get_git_commit(),
        "creation_timestamp": datetime.now(timezone.utc).isoformat()
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Train ProX BPE Tokenizer"
    )

    parser.add_argument(
        "--dataset",
        "--data-dir",
        dest="dataset",
        type=str,
        required=True,
        help=(
            "Path to text/code dataset file or directory "
            "containing corpus shards"
        ),
    )

    parser.add_argument(
        "--vocab-size",
        type=int,
        default=32000,
        help="Target vocabulary size",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./weights/tokenizer/tokenizer.json",
        help="Output path for tokenizer.json",
    )

    args = parser.parse_args()

    train_tokenizer(
        dataset_path=args.dataset,
        vocab_size=args.vocab_size,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
