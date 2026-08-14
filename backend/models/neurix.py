import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from backend.models.config import ModelConfig, get_config

class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        variance = x.pow(2).mean(-1, keepdim=True)
        return x * torch.rsqrt(variance + self.eps) * self.weight

class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, max_seq_len: int = 2048):
        super().__init__()
        inv_freq = 1.0 / (10000.0 ** (torch.arange(0, dim, 2).float() / dim))
        t = torch.arange(max_seq_len).float()
        freqs = torch.einsum("i,j->ij", t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos(), persistent=False)
        self.register_buffer("sin_cached", emb.sin(), persistent=False)

    def forward(self, x: torch.Tensor, seq_len: int):
        return self.cos_cached[:seq_len, :], self.sin_cached[:seq_len, :]

def rotate_half(x: torch.Tensor) -> torch.Tensor:
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)

def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor):
    cos = cos.unsqueeze(0).unsqueeze(2)  # [1, seq_len, 1, head_dim]
    sin = sin.unsqueeze(0).unsqueeze(2)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed

class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, max_seq_len: int = 2048):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)
        self.rotary_emb = RotaryEmbedding(self.head_dim, max_seq_len)

    def forward(self, x: torch.Tensor, kv_cache=None, start_pos: int = 0) -> torch.Tensor:
        b_size, seq_len, _ = x.shape
        q = self.q_proj(x).view(b_size, seq_len, self.n_heads, self.head_dim)
        k = self.k_proj(x).view(b_size, seq_len, self.n_heads, self.head_dim)
        v = self.v_proj(x).view(b_size, seq_len, self.n_heads, self.head_dim)

        cos, sin = self.rotary_emb(v, start_pos + seq_len)
        cos = cos[start_pos : start_pos + seq_len]
        sin = sin[start_pos : start_pos + seq_len]
        q, k = apply_rotary_pos_emb(q, k, cos, sin)

        if kv_cache is not None:
            k, v = kv_cache.update(k, v, start_pos)

        # Transpose for PyTorch Scaled Dot Product Attention [batch, heads, seq_len, head_dim]
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        is_causal = (seq_len > 1) and (kv_cache is None or start_pos == 0)
        out = F.scaled_dot_product_attention(q, k, v, is_causal=is_causal)
        out = out.transpose(1, 2).contiguous().view(b_size, seq_len, -1)
        return self.out_proj(out)

class SwiGLUFFN(nn.Module):
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff, bias=False)  # gate
        self.w2 = nn.Linear(d_ff, d_model, bias=False)  # down
        self.w3 = nn.Linear(d_model, d_ff, bias=False)  # up

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w2(F.silu(self.w1(x)) * self.w3(x))

class NeurixBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, d_ff: int, max_seq_len: int = 2048):
        super().__init__()
        self.attn_norm = RMSNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_heads, max_seq_len)
        self.ffn_norm = RMSNorm(d_model)
        self.ffn = SwiGLUFFN(d_model, d_ff)

    def forward(self, x: torch.Tensor, kv_cache=None, start_pos: int = 0) -> torch.Tensor:
        x = x + self.attn(self.attn_norm(x), kv_cache=kv_cache, start_pos=start_pos)
        x = x + self.ffn(self.ffn_norm(x))
        return x

class NeurixTransformer(nn.Module):
    """
    Neurix Decoder-Only Transformer Model.
    Architecture: RoPE, RMSNorm, SwiGLU, Scaled Dot-Product Attention, Optional KV Cache.
    """
    def __init__(self, config: ModelConfig = None, **kwargs):
        super().__init__()
        if config is None:
            if kwargs:
                config = ModelConfig(**kwargs)
            else:
                config = get_config("neurix-100m")

        self.config = config
        self.vocab_size = config.vocab_size
        self.d_model = config.d_model
        self.n_layers = config.n_layers
        self.max_seq_len = config.max_seq_len

        self.tok_embeddings = nn.Embedding(config.vocab_size, config.d_model)
        self.layers = nn.ModuleList([
            NeurixBlock(config.d_model, config.n_heads, config.d_ff, config.max_seq_len)
            for _ in range(config.n_layers)
        ])
        self.norm = RMSNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        if config.tie_weights:
            self.lm_head.weight = self.tok_embeddings.weight

        self.apply(self._init_module_weights)

    def _init_module_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, input_ids: torch.Tensor, kv_caches=None, start_pos: int = 0) -> torch.Tensor:
        x = self.tok_embeddings(input_ids)
        for i, layer in enumerate(self.layers):
            layer_cache = kv_caches[i] if kv_caches is not None else None
            x = layer(x, kv_cache=layer_cache, start_pos=start_pos)
        x = self.norm(x)
        logits = self.lm_head(x)
        return logits

    def num_parameters(self) -> int:
        params = {p for p in self.parameters() if p.requires_grad}
        return sum(p.numel() for p in params)

    def get_parameter_breakdown(self) -> dict:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        # Deduplicate exactly based on id(p) to handle tie_weights
        unique_params = {id(p): p for p in self.parameters()}
        unique = sum(p.numel() for p in unique_params.values())

        return {
            "total_parameters": total,
            "trainable_parameters": trainable,
            "unique_parameters": unique,
            "is_tied": self.config.tie_weights,
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
        }

def build_neurix_100m() -> NeurixTransformer:
    config = get_config("neurix-100m")
    return NeurixTransformer(config)
