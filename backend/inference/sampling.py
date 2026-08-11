import torch
import torch.nn.functional as F
from typing import List, Optional

def apply_repetition_penalty(logits: torch.Tensor, generated_tokens: List[int], penalty: float = 1.1) -> torch.Tensor:
    if penalty == 1.0 or not generated_tokens:
        return logits
    for token in set(generated_tokens):
        if logits[0, token] < 0:
            logits[0, token] *= penalty
        else:
            logits[0, token] /= penalty
    return logits

def sample_next_token(
    logits: torch.Tensor,
    temperature: float = 0.7,
    top_k: int = 40,
    top_p: float = 0.9,
    repetition_penalty: float = 1.1,
    generated_tokens: Optional[List[int]] = None
) -> int:
    logits = logits.clone()
    
    if generated_tokens and repetition_penalty > 1.0:
        logits = apply_repetition_penalty(logits, generated_tokens, repetition_penalty)

    if temperature <= 0.0:
        return torch.argmax(logits, dim=-1).item()

    logits = logits / max(temperature, 1e-5)

    if top_k > 0:
        values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
        min_value = values[0, -1]
        logits[logits < min_value] = -float("Inf")

    if top_p < 1.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
        logits[indices_to_remove] = -float("Inf")

    probs = F.softmax(logits, dim=-1)
    next_token = torch.multinomial(probs, num_samples=1).item()
    return next_token
