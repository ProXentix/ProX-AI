import hashlib
import random
from typing import List, Tuple
import torch
from torch.utils.data import Dataset
from backend.tokenizer.tokenizer import ProXTokenizer

def deduplicate_texts(texts: List[str]) -> List[str]:
    seen = set()
    unique = []
    for text in texts:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(text)
    return unique

def pack_sequences(token_ids: List[int], max_seq_len: int = 2048) -> List[List[int]]:
    chunks = []
    for i in range(0, len(token_ids), max_seq_len):
        chunk = token_ids[i : i + max_seq_len]
        if len(chunk) == max_seq_len:
            chunks.append(chunk)
    return chunks

class CausalLMDataset(Dataset):
    def __init__(self, token_chunks: List[List[int]]):
        self.samples = [torch.tensor(chunk, dtype=torch.long) for chunk in token_chunks]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        chunk = self.samples[idx]
        x = chunk[:-1]
        y = chunk[1:]
        return x, y

def prepare_dataset_splits(
    texts: List[str],
    tokenizer: ProXTokenizer,
    max_seq_len: int = 2048,
    val_ratio: float = 0.1,
    seed: int = 42
) -> Tuple[CausalLMDataset, CausalLMDataset]:
    random.seed(seed)
    unique_texts = deduplicate_texts(texts)
    random.shuffle(unique_texts)

    all_tokens = []
    for text in unique_texts:
        tokens = tokenizer.encode(text)
        if tokens:
            all_tokens.extend(tokens)
            all_tokens.append(tokenizer.eos_token_id)

    # Pack into (max_seq_len + 1) blocks so x is max_seq_len and y is max_seq_len
    block_size = max_seq_len + 1
    chunks = pack_sequences(all_tokens, block_size)

    if not chunks:
        # Fallback if text is small: pad or repeat
        padded = all_tokens[:block_size]
        while len(padded) < block_size:
            padded.append(tokenizer.pad_token_id)
        chunks = [padded]

    split_idx = max(1, int(len(chunks) * (1 - val_ratio)))
    train_chunks = chunks[:split_idx]
    val_chunks = chunks[split_idx:] if split_idx < len(chunks) else train_chunks

    return CausalLMDataset(train_chunks), CausalLMDataset(val_chunks)
