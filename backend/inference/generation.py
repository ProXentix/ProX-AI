import time
import torch
from typing import List, Generator, Dict, Any, Optional
from backend.models.neurix import NeurixTransformer
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.inference.kv_cache import build_kv_caches
from backend.inference.sampling import sample_next_token

class GenerationEngine:
    def __init__(self, model: NeurixTransformer, tokenizer: ProXTokenizer, device: str = "cpu"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        use_kv_cache: bool = True,
        stop_sequences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        prompt_tokens = self.tokenizer.encode(prompt)
        if not prompt_tokens:
            prompt_tokens = [self.tokenizer.bos_token_id]

        input_tensor = torch.tensor([prompt_tokens], dtype=torch.long, device=self.device)
        seq_len = input_tensor.shape[1]

        kv_caches = None
        if use_kv_cache:
            kv_caches = build_kv_caches(
                n_layers=self.model.n_layers,
                max_batch_size=1,
                max_seq_len=seq_len + max_new_tokens + 16,
                n_heads=self.model.config.n_heads,
                head_dim=self.model.config.head_dim,
                device=str(self.device)
            )

        start_time = time.time()
        generated_tokens = []

        with torch.no_grad():
            if use_kv_cache:
                # 1. PREFILL PHASE
                logits = self.model(input_tensor, kv_caches=kv_caches, start_pos=0)
                next_token_logits = logits[0, -1, :]
                next_token = sample_next_token(
                    next_token_logits.unsqueeze(0),
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                    generated_tokens=generated_tokens
                )
                generated_tokens.append(next_token)

                # 2. DECODE PHASE
                start_pos = seq_len
                curr_input = torch.tensor([[next_token]], dtype=torch.long, device=self.device)

                for _ in range(max_new_tokens - 1):
                    if next_token == self.tokenizer.eos_token_id:
                        break

                    logits = self.model(curr_input, kv_caches=kv_caches, start_pos=start_pos)
                    next_token_logits = logits[0, -1, :]
                    next_token = sample_next_token(
                        next_token_logits.unsqueeze(0),
                        temperature=temperature,
                        top_k=top_k,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty,
                        generated_tokens=generated_tokens
                    )
                    generated_tokens.append(next_token)
                    start_pos += 1
                    curr_input = torch.tensor([[next_token]], dtype=torch.long, device=self.device)
            else:
                # Standard generation without KV cache (recomputes full sequence per step)
                curr_tensor = input_tensor
                for _ in range(max_new_tokens):
                    logits = self.model(curr_tensor)
                    next_token_logits = logits[0, -1, :]
                    next_token = sample_next_token(
                        next_token_logits.unsqueeze(0),
                        temperature=temperature,
                        top_k=top_k,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty,
                        generated_tokens=generated_tokens
                    )
                    if next_token == self.tokenizer.eos_token_id:
                        break
                    generated_tokens.append(next_token)
                    next_tensor = torch.tensor([[next_token]], dtype=torch.long, device=self.device)
                    curr_tensor = torch.cat([curr_tensor, next_tensor], dim=1)

        elapsed = time.time() - start_time
        decoded_text = self.tokenizer.decode(generated_tokens)

        # Check stop sequences
        if stop_sequences:
            for stop in stop_sequences:
                if stop in decoded_text:
                    decoded_text = decoded_text.split(stop)[0]

        tok_per_sec = len(generated_tokens) / max(0.001, elapsed)

        return {
            "text": decoded_text,
            "prompt_tokens": len(prompt_tokens),
            "generated_tokens": len(generated_tokens),
            "total_tokens": len(prompt_tokens) + len(generated_tokens),
            "latency_seconds": elapsed,
            "tokens_per_second": tok_per_sec,
            "used_kv_cache": use_kv_cache
        }

    def generate_stream(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1
    ) -> Generator[str, None, None]:
        prompt_tokens = self.tokenizer.encode(prompt)
        if not prompt_tokens:
            prompt_tokens = [self.tokenizer.bos_token_id]

        input_tensor = torch.tensor([prompt_tokens], dtype=torch.long, device=self.device)
        seq_len = input_tensor.shape[1]

        kv_caches = build_kv_caches(
            n_layers=self.model.n_layers,
            max_batch_size=1,
            max_seq_len=seq_len + max_new_tokens + 16,
            n_heads=self.model.config.n_heads,
            head_dim=self.model.config.head_dim,
            device=str(self.device)
        )

        generated_tokens = []

        with torch.no_grad():
            logits = self.model(input_tensor, kv_caches=kv_caches, start_pos=0)
            next_token_logits = logits[0, -1, :]
            next_token = sample_next_token(
                next_token_logits.unsqueeze(0),
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                generated_tokens=generated_tokens
            )
            generated_tokens.append(next_token)
            yield self.tokenizer.decode([next_token])

            start_pos = seq_len
            curr_input = torch.tensor([[next_token]], dtype=torch.long, device=self.device)

            for _ in range(max_new_tokens - 1):
                if next_token == self.tokenizer.eos_token_id:
                    break

                logits = self.model(curr_input, kv_caches=kv_caches, start_pos=start_pos)
                next_token_logits = logits[0, -1, :]
                next_token = sample_next_token(
                    next_token_logits.unsqueeze(0),
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                    generated_tokens=generated_tokens
                )
                generated_tokens.append(next_token)
                yield self.tokenizer.decode([next_token])

                start_pos += 1
                curr_input = torch.tensor([[next_token]], dtype=torch.long, device=self.device)
