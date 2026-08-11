from dataclasses import dataclass, field
from typing import List

@dataclass
class TokenizerConfig:
    vocab_size: int = 32000
    min_frequency: int = 2
    special_tokens: List[str] = field(default_factory=lambda: [
        "<pad>",
        "<bos>",
        "<eos>",
        "<unk>",
        "<proxpl_start>",
        "<proxpl_end>",
    ])
    unk_token: str = "<unk>"
    pad_token: str = "<pad>"
    bos_token: str = "<bos>"
    eos_token: str = "<eos>"

DEFAULT_TOKENIZER_CONFIG = TokenizerConfig()
