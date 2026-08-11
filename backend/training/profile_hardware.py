import sys
import os
import platform
import shutil
import torch
import psutil
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer

def profile_hardware():
    config = get_config("neurix-100m")
    model = NeurixTransformer(config)
    num_params = model.num_parameters()

    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU (No CUDA)"
    vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if cuda_available else 0.0
    cuda_version = torch.version.cuda if cuda_available else "N/A"

    total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 2)

    total_disk_gb, used_disk_gb, free_disk_gb = shutil.disk_usage(os.getcwd())
    free_disk_gb = round(free_disk_gb / (1024**3), 2)

    # Memory calculations
    fp32_weights_mb = (num_params * 4) / (1024**2)
    fp16_weights_mb = (num_params * 2) / (1024**2)
    bf16_weights_mb = (num_params * 2) / (1024**2)

    gradients_mb = fp32_weights_mb  # FP32 gradients
    optimizer_states_mb = fp32_weights_mb * 2  # AdamW m and v vectors (FP32)
    
    # Sequence activation memory estimate for batch_size=1, seq_len=2048, 12 layers, d_model=768
    # Layer activations ~ (batch * seq * hidden * layers * bytes) + attention matrices
    seq_len = config.max_seq_len
    batch_size = 1
    activations_mb = (batch_size * seq_len * config.d_model * config.n_layers * 4 * 4) / (1024**2) + (batch_size * config.n_heads * seq_len * seq_len * config.n_layers * 4) / (1024**2)
    
    framework_overhead_mb = 800.0  # PyTorch baseline context & temp buffers

    total_training_memory_mb = fp32_weights_mb + gradients_mb + optimizer_states_mb + activations_mb + framework_overhead_mb
    total_training_memory_gb = total_training_memory_mb / 1024

    safety_margin_gb = total_ram_gb - total_training_memory_gb

    print("\n" + "="*70)
    print("PROX AI — HARDWARE PROFILING & MEMORY ANALYSIS")
    print("="*70)
    print(f"OS Platform:            {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Version:         {platform.python_version()}")
    print(f"PyTorch Version:        {torch.__version__}")
    print(f"CUDA Available:         {cuda_available} (CUDA Version: {cuda_version})")
    print(f"Target Compute Device:  {device_name}")
    if cuda_available:
        print(f"GPU VRAM:               {vram_gb} GB")
    print(f"CPU Physical Cores:     {psutil.cpu_count(logical=False)} (Logical: {psutil.cpu_count(logical=True)})")
    print(f"System RAM:             {free_ram_gb} GB Free / {total_ram_gb} GB Total")
    print(f"Available Disk Space:   {free_disk_gb} GB")
    print(f"BF16 Supported:         {torch.cuda.is_bf16_supported() if cuda_available else False}")
    print("-"*70)
    print("WEIGHT STORAGE COMPARISON (MODEL WEIGHTS ONLY)")
    print(f"  • FP32 Model Weights:     {fp32_weights_mb:.2f} MB ({fp32_weights_mb/1024:.3f} GB)")
    print(f"  • FP16 Model Weights:     {fp16_weights_mb:.2f} MB ({fp16_weights_mb/1024:.3f} GB)")
    print(f"  • BF16 Model Weights:     {bf16_weights_mb:.2f} MB ({bf16_weights_mb/1024:.3f} GB)")
    print("-"*70)
    print("FULL TRAINING GRAPH MEMORY BREAKDOWN (FP32, batch=1, seq=2048)")
    print(f"  Component            | Approx Memory (MB) | Approx Memory (GB)")
    print(f"  ---------------------|--------------------|-------------------")
    print(f"  Model Weights (FP32) | {fp32_weights_mb:18.2f} | {fp32_weights_mb/1024:17.3f}")
    print(f"  Gradients (FP32)     | {gradients_mb:18.2f} | {gradients_mb/1024:17.3f}")
    print(f"  Optimizer (AdamW)    | {optimizer_states_mb:18.2f} | {optimizer_states_mb/1024:17.3f}")
    print(f"  Activations (seq=2048| {activations_mb:18.2f} | {activations_mb/1024:17.3f}")
    print(f"  PyTorch Overhead     | {framework_overhead_mb:18.2f} | {framework_overhead_mb/1024:17.3f}")
    print(f"  ---------------------|--------------------|-------------------")
    print(f"  TOTAL ESTIMATED RAM  | {total_training_memory_mb:18.2f} | {total_training_memory_gb:17.3f}")
    print("-"*70)
    print(f"System RAM:             {total_ram_gb:.2f} GB")
    print(f"Estimated Peak Memory:  {total_training_memory_gb:.2f} GB")
    print(f"Safety Margin:          {safety_margin_gb:.2f} GB")
    if safety_margin_gb > 2.0:
        print("CPU Memory Assessment:  SAFE (Sufficient headroom for batch=1, seq=2048)")
    elif safety_margin_gb > 0.5:
        print("CPU Memory Assessment:  MARGINAL (Execution possible, tight memory margin)")
    else:
        print("CPU Memory Assessment:  UNSAFE (High risk of Out-Of-Memory)")
    print("="*70 + "\n")

if __name__ == "__main__":
    profile_hardware()
