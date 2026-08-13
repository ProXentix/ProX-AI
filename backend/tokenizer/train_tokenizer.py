import os
import sys
import glob
import argparse

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers, processors
from backend.tokenizer.config import TokenizerConfig

def get_text_iterator(dataset_path: str):
    if os.path.isfile(dataset_path):
        files = [dataset_path]
    elif os.path.isdir(dataset_path):
        files = glob.glob(os.path.join(dataset_path, "**", "*.*"), recursive=True)
    else:
        raise ValueError(f"Dataset path {dataset_path} does not exist.")

    for file_path in files:
        if file_path.endswith((".txt", ".jsonl", ".json", ".md", ".py", ".ts", ".js", ".c", ".cpp", ".proxpl")):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            yield line
            except Exception as e:
                print(f"[Tokenizer Trainer] Warning skipping file {file_path}: {e}")

def train_tokenizer(dataset_path: str, vocab_size: int, output_path: str):
    print(f"[Tokenizer Trainer] Training ProX BPE Tokenizer...")
    print(f"  Dataset Path: {dataset_path}")
    print(f"  Vocab Size:   {vocab_size}")
    print(f"  Output Path:  {output_path}")

    config = TokenizerConfig(vocab_size=vocab_size)

    bpe = models.BPE(unk_token=config.unk_token)
    tokenizer = Tokenizer(bpe)
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)

    trainer = trainers.BpeTrainer(
        vocab_size=config.vocab_size,
        min_frequency=config.min_frequency,
        special_tokens=config.special_tokens,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet()
    )

    iterator = get_text_iterator(dataset_path)
    tokenizer.train_from_iterator(iterator, trainer=trainer)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    tokenizer.save(output_path)
    print(f"[Tokenizer Trainer] Tokenizer trained and saved to {output_path} (vocab size: {tokenizer.get_vocab_size()})")

def main():
    parser = argparse.ArgumentParser(description="Train ProX BPE Tokenizer")
    parser.add_argument("--dataset", "--data-dir", dest="dataset", type=str, required=True, help="Path to text/code dataset file or directory")
    parser.add_argument("--vocab-size", type=int, default=32000, help="Target vocabulary size")
    parser.add_argument("--output", type=str, default="./weights/tokenizer/tokenizer.json", help="Output path for tokenizer.json")

    args = parser.parse_args()
    train_tokenizer(args.dataset, args.vocab_size, args.output)

if __name__ == "__main__":
    main()
