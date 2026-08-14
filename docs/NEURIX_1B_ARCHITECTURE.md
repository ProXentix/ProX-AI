# Neurix-1B Architecture

## Specifications
- **Vocab Size**: 32,000 (Byte-Level BPE)
- **d_model**: 1792
- **n_layers**: 24
- **n_heads**: 14 (head_dim = 128)
- **d_ff**: 4800 (SwiGLU)
- **max_seq_len**: 4096
- **Parameters**: ~1.05B

## Architectural Decisions
- Decoder-only Transformer.
- RoPE (Rotary Position Embeddings) scaled for 4096 context.
- RMSNorm applied pre-attention and pre-FFN.
- Tied embeddings (token embedding weights are shared with the LM head).
