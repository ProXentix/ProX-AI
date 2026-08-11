import argparse
import os
import yaml
from backend.models.config import ModelConfig, get_config
from backend.models.neurix import NeurixTransformer
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.datasets.loader import LocalDatasetLoader
from backend.datasets.preprocess import prepare_dataset_splits
from backend.training.config import TrainingConfig, CheckpointConfig
from backend.training.trainer import NeurixTrainer
from backend.training.checkpoint import inspect_checkpoint

def main():
    parser = argparse.ArgumentParser(description="ProX AI Neurix Training & Checkpoint CLI")
    parser.add_argument("--model", type=str, default="neurix-100m", help="Model config name (e.g. neurix-100m, neurix-tiny)")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config file")
    parser.add_argument("--dataset", type=str, default="./data/smoke_test.jsonl", help="Dataset file or directory path")
    parser.add_argument("--output", type=str, default=None, help="Checkpoint output directory")
    parser.add_argument("--steps", type=int, default=None, help="Absolute total target global training steps")
    parser.add_argument("--additional-steps", type=int, default=None, help="Additional steps to run relative to loaded checkpoint step")
    parser.add_argument("--tokenizer", type=str, default="./weights/tokenizer/tokenizer.json", help="Path to frozen tokenizer artifact")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint file to resume from")
    parser.add_argument("--inspect", type=str, default=None, help="Path to checkpoint file to inspect metadata")

    args = parser.parse_args()

    if args.inspect:
        inspect_checkpoint(args.inspect)
        return

    # Load configuration
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            yaml_raw = yaml.safe_load(f)
        m_dict = yaml_raw.get("model", {})
        t_dict = yaml_raw.get("training", {})
        c_dict = yaml_raw.get("checkpoint", {})

        model_config = ModelConfig(**m_dict)
        training_config = TrainingConfig(**t_dict)
        checkpoint_config = CheckpointConfig(**c_dict)
    else:
        model_config = get_config(args.model)
        training_config = TrainingConfig()
        checkpoint_config = CheckpointConfig(output_dir=f"./weights/{args.model}")

    if args.resume and os.path.exists(args.resume):
        try:
            import torch
            ckpt_data = torch.load(args.resume, map_location="cpu", weights_only=False)
            resumed_step = ckpt_data.get("step", 0)
            if args.additional_steps is not None:
                training_config.max_steps = resumed_step + args.additional_steps
            elif args.steps is not None:
                training_config.max_steps = args.steps
                if args.steps <= resumed_step:
                    print(f"[ProX Training] WARNING: Target --steps ({args.steps}) is <= resumed checkpoint step ({resumed_step}). No additional training steps will be executed.")
        except Exception:
            if args.steps is not None:
                training_config.max_steps = args.steps
    elif args.steps is not None:
        training_config.max_steps = args.steps

    if args.steps is not None or args.additional_steps is not None:
        checkpoint_config.save_every = min(checkpoint_config.save_every, training_config.max_steps)

    if args.output is not None:
        checkpoint_config.output_dir = args.output

    print(f"[ProX Training] Initializing Neurix Training Pipeline...")
    print(f"  Model:            {model_config.name}")
    print(f"  Dataset:          {args.dataset}")
    print(f"  Tokenizer Path:   {args.tokenizer}")
    print(f"  Target Max Steps: {training_config.max_steps}")
    print(f"  Output Dir:       {checkpoint_config.output_dir}")

    # Load frozen tokenizer artifact (disallow fallback dynamic training)
    tokenizer = ProXTokenizer(tokenizer_path=args.tokenizer, allow_fallback=False)

    loader = LocalDatasetLoader(args.dataset)
    raw_texts = loader.load_texts()

    if not raw_texts:
        raise ValueError(f"No texts found in dataset path: {args.dataset}")

    train_dataset, val_dataset = prepare_dataset_splits(
        raw_texts,
        tokenizer,
        max_seq_len=model_config.max_seq_len,
        val_ratio=0.1
    )

    model = NeurixTransformer(model_config)

    trainer = NeurixTrainer(
        model=model,
        model_config=model_config,
        training_config=training_config,
        checkpoint_config=checkpoint_config,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        tokenizer=tokenizer
    )

    trainer.train(resume_path=args.resume)

if __name__ == "__main__":
    main()
