import argparse
from backend.models.config import get_config, ModelConfig

def estimate_memory(config: ModelConfig, batch_size: int = 1):
    vocab_size = config.vocab_size
    d_model = config.d_model
    n_layers = config.n_layers
    n_heads = config.n_heads
    d_ff = config.d_ff
    max_seq_len = config.max_seq_len
    
    # 1. Parameter calculation
    embed_params = vocab_size * d_model
    ln_params = (2 * d_model * n_layers) + d_model
    attn_params = 4 * d_model * d_model * n_layers
    ffn_params = 3 * d_model * d_ff * n_layers
    lm_head_params = 0 if config.tie_weights else vocab_size * d_model
    
    total_params = embed_params + ln_params + attn_params + ffn_params + lm_head_params
    
    # 2. Inference Memory
    fp32_bytes = 4
    fp16_bytes = 2
    
    inference_fp32 = total_params * fp32_bytes
    inference_fp16 = total_params * fp16_bytes
    inference_bf16 = total_params * fp16_bytes
    
    # KV Cache memory (batch_size=1)
    kv_cache_fp16 = 2 * n_layers * max_seq_len * 1 * d_model * fp16_bytes
    
    # 3. Training Memory (Mixed Precision AdamW)
    # Weights (FP16) = 2 bytes
    # Gradients (FP16) = 2 bytes
    # Master Weights (FP32) = 4 bytes
    # Momentum 1 (FP32) = 4 bytes
    # Momentum 2 (FP32) = 4 bytes
    # Total per parameter = 16 bytes
    optimizer_state = total_params * 16
    
    # Activations (approximate rule of thumb: 34 * b * s * h * L bytes for selective recomputation, or ~ 10-15x more without)
    # Let's give a basic estimation for full activations without checkpointing:
    # ~ (12 * b * s * d_model * L) in bytes for standard transformer blocks
    activation_memory = 12 * batch_size * max_seq_len * d_model * n_layers * fp16_bytes
    
    total_training_memory = optimizer_state + activation_memory
    
    def format_gb(bytes_val):
        return f"{bytes_val / (1024**3):.2f} GB"
        
    print("\n" + "="*50)
    print(f"MEMORY ESTIMATION REPORT: {config.name.upper()}")
    print("="*50)
    print(f"Total Parameters:    {total_params / 1e9:.3f} Billion")
    print(f"Context Length:      {max_seq_len} tokens")
    print("-" * 50)
    print(f"INFERENCE MEMORY:")
    print(f"  Weights (FP32):    {format_gb(inference_fp32)}")
    print(f"  Weights (FP16):    {format_gb(inference_fp16)}")
    print(f"  Weights (BF16):    {format_gb(inference_bf16)}")
    print(f"  KV Cache (seq={max_seq_len}, b=1, FP16): {format_gb(kv_cache_fp16)}")
    print("-" * 50)
    print(f"TRAINING MEMORY (Batch={batch_size}, seq={max_seq_len}, Mixed Precision AdamW):")
    print(f"  Weights/Opt/Grads: {format_gb(optimizer_state)}")
    print(f"  Activations (est): {format_gb(activation_memory)}")
    print(f"  Total Training:    {format_gb(total_training_memory)}")
    print("="*50 + "\n")
    
    return {
        "total_parameters": total_params,
        "total_memory_gb": total_training_memory / (1024**3),
        "inference_memory_gb": inference_bf16 / (1024**3),
        "kv_cache_gb": kv_cache_fp16 / (1024**3)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimate memory for Neurix models")
    parser.add_argument("--model", type=str, default="neurix-1b", help="Model config name")
    parser.add_argument("--batch_size", type=int, default=1, help="Training micro-batch size")
    args = parser.parse_args()
    
    config = get_config(args.model)
    estimate_memory(config, batch_size=args.batch_size)
