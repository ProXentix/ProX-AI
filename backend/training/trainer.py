import math
import time
import os
import json
import hashlib
import platform
import subprocess
from datetime import datetime, timezone
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from backend.models.neurix import NeurixTransformer
from backend.models.config import ModelConfig
from backend.training.config import TrainingConfig, CheckpointConfig
from backend.training.scheduler import get_cosine_schedule_with_warmup
from backend.training.checkpoint import save_checkpoint, load_checkpoint
from backend.utils.device import get_device_info, print_resource_summary
from backend.tokenizer.tokenizer import ProXTokenizer

def get_git_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except Exception:
        return "N/A"

def get_file_sha256(file_path: str) -> str:
    if not os.path.exists(file_path):
        return "N/A"
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "N/A"

class NeurixTrainer:
    def __init__(
        self,
        model: NeurixTransformer,
        model_config: ModelConfig,
        training_config: TrainingConfig,
        checkpoint_config: CheckpointConfig,
        train_dataset,
        val_dataset,
        tokenizer: ProXTokenizer,
        dataset_path: str = "./data/smoke_test.jsonl"
    ):
        self.model = model
        self.model_config = model_config
        self.t_config = training_config
        self.c_config = checkpoint_config
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.tokenizer = tokenizer
        self.dataset_path = dataset_path

        device_info = get_device_info()
        self.device = torch.device(device_info["device"])
        self.model.to(self.device)

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.t_config.learning_rate,
            weight_decay=self.t_config.weight_decay
        )

        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.t_config.batch_size,
            shuffle=True
        )
        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.t_config.batch_size,
            shuffle=False
        )

        num_total_steps = self.t_config.max_steps
        self.scheduler = get_cosine_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.t_config.warmup_steps,
            num_training_steps=num_total_steps
        )

        self.use_amp = (self.device.type == "cuda" and self.t_config.precision in ["auto", "float16"])
        if hasattr(torch.amp, "GradScaler"):
            self.scaler = torch.amp.GradScaler("cuda", enabled=self.use_amp)
        else:
            self.scaler = torch.cuda.amp.GradScaler(enabled=self.use_amp)

        self.global_step = 0
        self.epoch = 0

        self.save_run_manifest()

    def save_run_manifest(self):
        os.makedirs(self.c_config.output_dir, exist_ok=True)
        manifest_path = os.path.join(self.c_config.output_dir, "run_manifest.json")

        manifest = {
            "model_version": self.model_config.name,
            "model_config": {
                "vocab_size": self.model_config.vocab_size,
                "d_model": self.model_config.d_model,
                "n_layers": self.model_config.n_layers,
                "n_heads": self.model_config.n_heads,
                "d_ff": self.model_config.d_ff,
                "max_seq_len": self.model_config.max_seq_len,
                "tie_weights": self.model_config.tie_weights,
                "parameters": self.model.num_parameters()
            },
            "tokenizer_version": "ProX-Tokenizer-DEV",
            "dataset_path": self.dataset_path,
            "dataset_hash": get_file_sha256(self.dataset_path),
            "git_commit": get_git_commit_hash(),
            "python_version": platform.python_version(),
            "pytorch_version": torch.__version__,
            "device": str(self.device),
            "dtype": "FP16 (AMP)" if self.use_amp else "FP32",
            "batch_size": self.t_config.batch_size,
            "gradient_accumulation_steps": self.t_config.gradient_accumulation_steps,
            "effective_batch_size": self.t_config.batch_size * self.t_config.gradient_accumulation_steps,
            "sequence_length": self.model_config.max_seq_len,
            "learning_rate": self.t_config.learning_rate,
            "scheduler": "CosineAnnealingWithWarmup",
            "optimizer": "AdamW",
            "seed": self.t_config.seed,
            "start_timestamp": datetime.now(timezone.utc).isoformat()
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print(f"[Trainer] Saved training run manifest to {manifest_path}")

    def evaluate(self) -> float:
        self.model.eval()
        total_loss = 0.0
        total_batches = 0
        with torch.no_grad():
            for x, y in self.val_loader:
                x = x.to(self.device)
                y = y.to(self.device)
                logits = self.model(x)
                loss = F.cross_entropy(logits.view(-1, self.model_config.vocab_size), y.view(-1))
                total_loss += loss.item()
                total_batches += 1
                if total_batches >= 20:
                    break
        self.model.train()
        avg_loss = total_loss / max(1, total_batches)
        return avg_loss

    def train(self, resume_path: str = None):
        if resume_path:
            chk = load_checkpoint(resume_path, self.model, self.optimizer, self.scheduler, self.device)
            self.global_step = chk.get("step", 0)
            self.epoch = chk.get("epoch", 0)

        print_resource_summary(
            model_name=self.model_config.name,
            num_params=self.model.num_parameters(),
            batch_size=self.t_config.batch_size,
            grad_accum=self.t_config.gradient_accumulation_steps,
            seq_len=self.model_config.max_seq_len,
            precision="AMP (FP16)" if self.use_amp else "FP32"
        )

        self.model.train()
        self.optimizer.zero_grad()
        start_time = time.time()

        while self.global_step < self.t_config.max_steps:
            self.epoch += 1
            for x, y in self.train_loader:
                x = x.to(self.device)
                y = y.to(self.device)

                if self.use_amp:
                    with torch.amp.autocast("cuda", enabled=True):
                        logits = self.model(x)
                        loss = F.cross_entropy(logits.view(-1, self.model_config.vocab_size), y.view(-1))
                        scaled_loss = loss / self.t_config.gradient_accumulation_steps
                else:
                    logits = self.model(x)
                    loss = F.cross_entropy(logits.view(-1, self.model_config.vocab_size), y.view(-1))
                    scaled_loss = loss / self.t_config.gradient_accumulation_steps

                if self.use_amp:
                    self.scaler.scale(scaled_loss).backward()
                else:
                    scaled_loss.backward()

                if (self.global_step + 1) % self.t_config.gradient_accumulation_steps == 0:
                    if self.use_amp:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.t_config.gradient_clip)
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.t_config.gradient_clip)
                        self.optimizer.step()

                    self.scheduler.step()
                    self.optimizer.zero_grad()

                self.global_step += 1

                if self.global_step % 10 == 0 or self.global_step == self.t_config.max_steps:
                    lr = self.optimizer.param_groups[0]["lr"]
                    elapsed = time.time() - start_time
                    tok_per_sec = (x.numel() * 10) / max(0.001, elapsed)
                    start_time = time.time()
                    print(f"Step {self.global_step:06d}/{self.t_config.max_steps} | Loss: {loss.item():.4f} | LR: {lr:.6e} | Throughput: {tok_per_sec:.1f} tok/s")

                if self.global_step % self.c_config.save_every == 0 or self.global_step == self.t_config.max_steps:
                    val_loss = self.evaluate()
                    ppl = math.exp(min(20, val_loss))
                    print(f"--> Validation Step {self.global_step} | Val Loss: {val_loss:.4f} | Perplexity: {ppl:.2f}")

                    save_checkpoint(
                        output_dir=self.c_config.output_dir,
                        step=self.global_step,
                        epoch=self.epoch,
                        model=self.model,
                        optimizer=self.optimizer,
                        scheduler=self.scheduler,
                        model_config=self.model_config,
                        training_config=self.t_config,
                        metrics={"val_loss": val_loss, "perplexity": ppl}
                    )

                if self.global_step >= self.t_config.max_steps:
                    break

        print("[Neurix Trainer] Training loop completed successfully.")


if __name__ == "__main__":
    from backend.training.train import main
    main()

