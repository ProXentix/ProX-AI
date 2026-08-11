import os
import random
import tempfile
import torch
import torch.nn.functional as F
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer
from backend.training.config import TrainingConfig
from backend.training.scheduler import get_cosine_schedule_with_warmup
from backend.training.checkpoint import save_checkpoint, load_checkpoint

def test_resume_optimizer_and_scheduler_determinism():
    config = get_config("neurix-tiny")
    t_config = TrainingConfig(batch_size=1, gradient_accumulation_steps=1, learning_rate=1e-3, warmup_steps=10, max_steps=50)

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Step 1: Initial training for 5 steps
        torch.manual_seed(42)
        random.seed(42)

        m1 = NeurixTransformer(config)
        opt1 = torch.optim.AdamW(m1.parameters(), lr=t_config.learning_rate)
        sch1 = get_cosine_schedule_with_warmup(opt1, num_warmup_steps=t_config.warmup_steps, num_training_steps=t_config.max_steps)

        for step in range(1, 6):
            opt1.zero_grad()
            x = torch.randint(0, config.vocab_size, (1, 64))
            y = torch.randint(0, config.vocab_size, (1, 64))
            logits = m1(x)
            loss = F.cross_entropy(logits.view(-1, config.vocab_size), y.view(-1))
            loss.backward()
            opt1.step()
            sch1.step()

        ckpt_path = save_checkpoint(
            output_dir=tmp_dir,
            step=5,
            epoch=1,
            model=m1,
            optimizer=opt1,
            scheduler=sch1,
            model_config=config,
            training_config=t_config,
            metrics={"val_loss": loss.item()}
        )

        # Step 2: Restore into two independent processes/instances
        m2 = NeurixTransformer(config)
        opt2 = torch.optim.AdamW(m2.parameters(), lr=t_config.learning_rate)
        sch2 = get_cosine_schedule_with_warmup(opt2, num_warmup_steps=t_config.warmup_steps, num_training_steps=t_config.max_steps)

        m3 = NeurixTransformer(config)
        opt3 = torch.optim.AdamW(m3.parameters(), lr=t_config.learning_rate)
        sch3 = get_cosine_schedule_with_warmup(opt3, num_warmup_steps=t_config.warmup_steps, num_training_steps=t_config.max_steps)

        chk2 = load_checkpoint(ckpt_path, m2, opt2, sch2)
        chk3 = load_checkpoint(ckpt_path, m3, opt3, sch3)

        assert chk2["step"] == 5
        assert chk3["step"] == 5

        # Verify optimizer state is NOT freshly initialized
        assert len(opt2.state) > 0, "Optimizer state dict must contain trained momentum/variance parameters"
        assert len(opt3.state) > 0, "Optimizer state dict must contain trained momentum/variance parameters"

        # Verify exact match between m2 and m3 states
        for p2, p3 in zip(m2.parameters(), m3.parameters()):
            torch.testing.assert_close(p2, p3)

        lr2 = opt2.param_groups[0]["lr"]
        lr3 = opt3.param_groups[0]["lr"]
        assert lr2 == lr3, f"Learning rates must match: {lr2} vs {lr3}"

        # Step 3: Run step 6 on both restored models with identical seed
        torch.manual_seed(999)
        x_next = torch.randint(0, config.vocab_size, (1, 64))
        y_next = torch.randint(0, config.vocab_size, (1, 64))

        opt2.zero_grad()
        loss2 = F.cross_entropy(m2(x_next).view(-1, config.vocab_size), y_next.view(-1))
        loss2.backward()
        opt2.step()
        sch2.step()

        opt3.zero_grad()
        loss3 = F.cross_entropy(m3(x_next).view(-1, config.vocab_size), y_next.view(-1))
        loss3.backward()
        opt3.step()
        sch3.step()

        # Strict deterministic assertion
        torch.testing.assert_close(loss2, loss3)
        for p2, p3 in zip(m2.parameters(), m3.parameters()):
            torch.testing.assert_close(p2, p3)
