# Neurix-1B Training Guide

## Pretraining Recipe
The 1B model will be trained on the ProX Training Corpus v0.2, consisting of ~1 Billion tokens.

### Configuration
- **Optimizer**: AdamW
- **Learning Rate**: 2.0e-4
- **Scheduler**: Cosine Annealing with Warmup (4000 steps)
- **Precision**: bfloat16
- **Global Batch Size**: 32 (1 micro-batch * 32 gradient accumulation steps)

### Target Corpus
- **1,000,000,000** tokens total.
- Strict anti-leakage boundaries applied to 50M val and 50M test sets.
