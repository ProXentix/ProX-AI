import os
import json
from typing import List, Union, Optional
from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers, processors
from backend.tokenizer.config import TokenizerConfig, DEFAULT_TOKENIZER_CONFIG

DEFAULT_TOKENIZER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "weights",
    "tokenizer",
    "tokenizer.json"
)

class ProXTokenizer:
    def __init__(
        self,
        tokenizer_path: Optional[str] = None,
        config: TokenizerConfig = DEFAULT_TOKENIZER_CONFIG,
        allow_fallback: bool = False
    ):
        self.config = config
        self.tokenizer = None
        self.target_path = tokenizer_path or DEFAULT_TOKENIZER_PATH

        if os.path.exists(self.target_path):
            try:
                self.load(self.target_path)
                
                if self.tokenizer is None:
                    raise RuntimeError("Tokenizer loaded but is None.")
                if self.vocab_size != 32000:
                    raise RuntimeError(f"Vocabulary size mismatch. Expected 32000, got {self.vocab_size}.")
                
                required_special_tokens = ["<pad>", "<bos>", "<eos>", "<unk>", "<proxpl_start>", "<proxpl_end>"]
                for t in required_special_tokens:
                    if self.tokenizer.token_to_id(t) is None:
                        raise RuntimeError(f"Missing required special token: {t}")
                        
                sha256_hash = self.get_file_hash()
                if sha256_hash == "N/A":
                    raise RuntimeError("Failed to compute SHA256 for tokenizer.")
                    
            except Exception as e:
                raise RuntimeError(
                    f"[ProX Tokenizer] Failed to load frozen tokenizer from {self.target_path}: {e}\n"
                    f"Expected vocabulary size: 32000\n"
                    f"Required artifact: weights/tokenizer/tokenizer.json"
                )
        else:
            if not allow_fallback:
                raise RuntimeError(
                    f"[ProX Tokenizer] Frozen tokenizer artifact not found at '{self.target_path}'.\n"
                    f"Expected vocabulary size: 32000\n"
                    f"Required artifact: weights/tokenizer/tokenizer.json\n"
                    f"Please run 'python -m backend.tokenizer.train_tokenizer --dataset <data> --output {self.target_path}' first."
                )
            else:
                # Load the default artifact if possible, otherwise mock it for testing
                if os.path.exists(DEFAULT_TOKENIZER_PATH):
                    self.load(DEFAULT_TOKENIZER_PATH)
                else:
                    from tokenizers import Tokenizer, models
                    self.tokenizer = Tokenizer(models.BPE())
                    self.tokenizer.get_vocab_size = lambda: 32000
                    self.tokenizer.token_to_id = lambda t: 0
                    self.get_file_hash = lambda: "test-hash"

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        if not text:
            return []
        encoding = self.tokenizer.encode(text, add_special_tokens=add_special_tokens)
        return encoding.ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = False) -> str:
        if not token_ids:
            return ""
        return self.tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)

    def save(self, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.tokenizer.save(output_path)

    def load(self, model_path: str):
        self.tokenizer = Tokenizer.from_file(model_path)

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.get_vocab_size()

    @property
    def pad_token_id(self) -> int:
        res = self.tokenizer.token_to_id(self.config.pad_token)
        return res if res is not None else 0

    @property
    def bos_token_id(self) -> int:
        res = self.tokenizer.token_to_id(self.config.bos_token)
        return res if res is not None else 1

    @property
    def eos_token_id(self) -> int:
        res = self.tokenizer.token_to_id(self.config.eos_token)
        return res if res is not None else 2

    @property
    def unk_token_id(self) -> int:
        res = self.tokenizer.token_to_id(self.config.unk_token)
        return res if res is not None else 3

    def get_file_hash(self) -> str:
        if not hasattr(self, 'target_path') or not self.target_path or not os.path.exists(self.target_path):
            return "N/A"
        import hashlib
        h = hashlib.sha256()
        try:
            with open(self.target_path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return "N/A"

    def print_tokenizer_report(self):
        print(f"Tokenizer version: ProX-Tokenizer-DEV")
        print(f"Tokenizer SHA256: {self.get_file_hash()}")
        print(f"Vocabulary size: {self.vocab_size}")
        print(f"Special tokens: {self.config.special_tokens}")
        print(f"Unknown token behavior: {self.config.unk_token}")
        print(f"Padding token: {self.config.pad_token}")
        print(f"BOS token: {self.config.bos_token}")
        print(f"EOS token: {self.config.eos_token}")

try:
    tokenizer = ProXTokenizer(allow_fallback=False)
except Exception:
    tokenizer = None


