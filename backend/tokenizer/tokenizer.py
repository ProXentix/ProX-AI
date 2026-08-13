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
        allow_fallback: bool = True
    ):
        self.config = config
        self.tokenizer = None

        target_path = tokenizer_path or DEFAULT_TOKENIZER_PATH
        if os.path.exists(target_path):
            try:
                self.load(target_path)
            except Exception as e:
                if not allow_fallback:
                    raise RuntimeError(f"[ProX Tokenizer] Failed to load frozen tokenizer from {target_path}: {e}")
                print(f"[ProX Tokenizer] Failed to load from {target_path}: {e}. Building fallback tokenizer.")
                self._build_fallback_tokenizer(target_path)
        else:
            if not allow_fallback:
                raise FileNotFoundError(
                    f"[ProX Tokenizer] Frozen tokenizer artifact not found at '{target_path}'. "
                    f"Please run 'python -m backend.tokenizer.train_tokenizer --dataset <data> --output {target_path}' first."
                )
            self._build_fallback_tokenizer(target_path)

    def _build_fallback_tokenizer(self, save_path: Optional[str] = None):
        """Builds a Byte-Level BPE tokenizer preconfigured with ProX special tokens."""
        bpe = models.BPE(unk_token=self.config.unk_token)
        self.tokenizer = Tokenizer(bpe)
        self.tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        self.tokenizer.decoder = decoders.ByteLevel()
        self.tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)

        trainer = trainers.BpeTrainer(
            vocab_size=self.config.vocab_size,
            min_frequency=self.config.min_frequency,
            special_tokens=self.config.special_tokens,
            initial_alphabet=pre_tokenizers.ByteLevel.alphabet()
        )
        # Train on initial base alphabet & special tokens
        dummy_corpus = [
            "ProXPL fn main() { let x: int = 42; return x; }",
            "function calculateSum(a: number, b: number): number { return a + b; }",
            "def fibonacci(n: int) -> int:\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "#include <stdio.h>\nint main() { printf(\"Hello ProX\\n\"); return 0; }",
            "{\"status\": \"ok\", \"model\": \"neurix-100m\", \"value\": 100}"
        ]
        self.tokenizer.train_from_iterator(dummy_corpus, trainer=trainer)
        if save_path:
            try:
                self.save(save_path)
            except Exception:
                pass

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

tokenizer = ProXTokenizer()
