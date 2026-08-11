# ProX AI Inference Engine & KV Cache

## Architecture
The inference engine (`backend/inference/`) provides autoregressive token generation for Neurix transformers.

## Key-Value (KV) Cache Specification
- **Prefill Phase:** Computes self-attention over prompt prefix ($\mathcal{O}(N^2 \cdot d_{model})$).
- **Decode Phase:** Retrieves cached K/V tensors for past sequence steps, avoiding recomputation ($\mathcal{O}(N \cdot d_{model})$ per step).

## Sampling Options
- `temperature`: Softmax logit temperature scaling.
- `top_k`: Top-K logit filtering.
- `top_p`: Nucleus top-P cumulative probability filtering.
- `repetition_penalty`: Multiplicative penalty on previously generated tokens.
- `stop_sequences`: Truncates output when matching stop sub-strings.

## Stream Format
Exposes pure SSE standard format (`data: {"choices": [{"delta": {"content": "token"}}]}\n\n`) without artificial markdown headers.
