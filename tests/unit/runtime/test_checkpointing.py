from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf

from rinalmo.runtime.checkpointing import (
    resolve_resume_checkpoint,
    save_config_snapshot,
    save_run_metadata,
)


def test_resolve_resume_checkpoint_auto(tmp_path: Path):
    ckpt_dir = tmp_path / "checkpoints"
    ckpt_dir.mkdir(parents=True)
    ckpt = ckpt_dir / "last.ckpt"
    ckpt.write_text("dummy")

    resolved = resolve_resume_checkpoint(tmp_path, "auto")
    assert resolved == str(ckpt)


def test_save_config_and_run_metadata(tmp_path: Path):
    cfg = OmegaConf.create(
        {
            "paths": {"output_dir": str(tmp_path)},
            "run": {"name": "unit-test"},
            "seed": 42,
        }
    )

    config_path = save_config_snapshot(cfg, tmp_path)
    summary_path = save_run_metadata(tmp_path, extra={"seed": 42})

    assert config_path.exists()
    assert summary_path.exists()
