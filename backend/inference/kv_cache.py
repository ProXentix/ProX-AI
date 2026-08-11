import torch
import torch.nn as nn
from typing import Tuple, Optional

class KVCache:
    """
    Key-Value Cache container for Neurix Transformer autoregressive decoder inference.
    
    COMPLEXITY DOCUMENTATION:
    1. PREFILL PHASE:
       The initial prompt of length N is processed in a single forward pass.
       Self-attention compute complexity for prompt prefill is O(N^2 * d_model).
    
    2. DECODE PHASE:
       For each subsequent token step, KV projection tensors for past sequence keys/values
       are retrieved from this cache rather than being recomputed from position 0.
       Self-attention compute complexity per decode step becomes O(N * d_model) instead of O(N^2 * d_model).
    """
    def __init__(self, max_batch_size: int, max_seq_len: int, n_heads: int, head_dim: int, device: str = "cpu", dtype: torch.dtype = torch.float32):
        self.max_batch_size = max_batch_size
        self.max_seq_len = max_seq_len
        self.n_heads = n_heads
        self.head_dim = head_dim
        self.device = device
        self.dtype = dtype

        self.k_cache = torch.zeros((max_batch_size, max_seq_len, n_heads, head_dim), device=device, dtype=dtype)
        self.v_cache = torch.zeros((max_batch_size, max_seq_len, n_heads, head_dim), device=device, dtype=dtype)
        self.current_length = 0

    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, start_pos: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        key_states, value_states shape: [batch_size, seq_len, n_heads, head_dim]
        """
        b_size, seq_len, _, _ = key_states.shape
        end_pos = start_pos + seq_len

        self.k_cache[:b_size, start_pos:end_pos] = key_states
        self.v_cache[:b_size, start_pos:end_pos] = value_states
        self.current_length = end_pos

        return self.k_cache[:b_size, :end_pos], self.v_cache[:b_size, :end_pos]

    def reset(self):
        self.k_cache.zero_()
        self.v_cache.zero_()
        self.current_length = 0

def build_kv_caches(n_layers: int, max_batch_size: int, max_seq_len: int, n_heads: int, head_dim: int, device: str = "cpu"):
    return [
        KVCache(max_batch_size, max_seq_len, n_heads, head_dim, device=device)
        for _ in range(n_layers)
    ]
