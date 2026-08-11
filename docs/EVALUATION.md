# ProX AI Evaluation Framework

## Verified Metrics
1. **Validation Loss:** Cross-entropy loss on held-out validation set.
2. **Perplexity:** $PPL = \exp(Loss)$.
3. **Throughput:** Tokens generated per second (`tok/s`).
4. **Latency:** Total response time in seconds.
5. **KV Cache Speedup:** Deterministic token output equivalence check between cached and non-cached decoding.

## Output Directory
Evaluation artifacts and log outputs are saved under `reports/`.
