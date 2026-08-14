import os
import pytest
from backend.training.checkpoint_manager import CheckpointManager
from backend.utils.storage import check_disk_space

def test_check_disk_space_mocked(monkeypatch):
    import shutil
    from collections import namedtuple
    
    Usage = namedtuple("Usage", ["total", "used", "free"])
    
    def mock_usage(path):
        return Usage(100, 50, 50)
        
    monkeypatch.setattr(shutil, "disk_usage", mock_usage)
    
    # Needs 40, has 50. 40 * 1.1 = 44 < 50, so True
    assert check_disk_space(40, ".") is True
    
    # Needs 48. 48 * 1.1 = 52.8 > 50, so False
    assert check_disk_space(48, ".") is False

def test_checkpoint_manager_retention(tmp_path):
    mgr = CheckpointManager(output_dir=str(tmp_path), max_local_keep=2, dry_run=True)
    
    import time
    # Create fake checkpoints with slightly different mtimes
    for i in range(5):
        ckpt_name = f"checkpoint-step-{i:06d}.pt"
        ckpt_path = tmp_path / ckpt_name
        ckpt_path.write_text("fake data")
        time.sleep(0.01) # to ensure mtime ordering is correct
        
    ckpts = mgr.get_local_checkpoints()
    assert len(ckpts) == 5
    
    mgr._cleanup_local(force=False)
    
    ckpts_after = mgr.get_local_checkpoints()
    assert len(ckpts_after) == 2
    
    assert "step-000003" in ckpts_after[0]
    assert "step-000004" in ckpts_after[1]
    
    # Test force cleanup
    mgr._cleanup_local(force=True)
    ckpts_force = mgr.get_local_checkpoints()
    assert len(ckpts_force) == 1
    assert "step-000004" in ckpts_force[0]
