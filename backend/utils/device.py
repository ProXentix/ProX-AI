import torch
import logging

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

def get_device_info():
    tpu_available = False
    device_str = "cpu"
    tpu_name = None

    try:
        import torch_xla.core.xla_model as xm
        xla_dev = xm.xla_device()
        device_str = str(xla_dev)
        tpu_available = True
        tpu_name = f"Kaggle / Google TPU ({xla_dev})"
    except Exception:
        tpu_available = False

    if not tpu_available:
        cuda_available = torch.cuda.is_available()
        device_str = "cuda" if cuda_available else "cpu"
    else:
        cuda_available = False

    system_ram = round(psutil.virtual_memory().total / (1024 ** 3), 2) if HAS_PSUTIL else "N/A"

    info = {
        "device": device_str,
        "cuda_available": cuda_available,
        "tpu_available": tpu_available,
        "gpu_name": tpu_name if tpu_available else (torch.cuda.get_device_name(0) if cuda_available else None),
        "gpu_vram_gb": round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2) if cuda_available else 0.0,
        "system_ram_gb": system_ram,
        "pytorch_version": torch.__version__,
    }

    return info

def print_resource_summary(model_name: str, num_params: int, batch_size: int, grad_accum: int, seq_len: int, precision: str):
    info = get_device_info()
    effective_batch = batch_size * grad_accum
    
    print("\n" + "="*60)
    print("PROX AI RESOURCE & TRAINING SUMMARY")
    print("="*60)
    print(f"Model Name:              {model_name}")
    print(f"Total Parameters:        {num_params:,}")
    print(f"PyTorch Version:         {info['pytorch_version']}")
    print(f"Target Device:           {info['device']}")
    if info['cuda_available']:
        print(f"GPU Model:               {info['gpu_name']}")
        print(f"VRAM Available:          {info['gpu_vram_gb']} GB")
    print(f"System RAM:              {info['system_ram_gb']} GB")
    print(f"Micro Batch Size:        {batch_size}")
    print(f"Gradient Accumulation:   {grad_accum}")
    print(f"Effective Batch Size:    {effective_batch}")
    print(f"Max Sequence Length:     {seq_len}")
    print(f"Target Precision:        {precision}")
    print("="*60 + "\n")

    if not info['cuda_available'] and num_params > 50_000_000 and batch_size * seq_len > 4096:
        print("[WARNING] High parameter count & context length on CPU. Training may be slow; consider using smaller batch sizes or development configs.")
