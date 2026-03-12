from __future__ import annotations

from pathlib import Path
from typing import Any

import lightning.pytorch as pl
from lightning.pytorch.callbacks import LearningRateMonitor, ModelCheckpoint
from lightning.pytorch.loggers import CSVLogger, WandbLogger
from omegaconf import OmegaConf

from rinalmo.runtime.checkpointing import (
    checkpoint_dir,
    resolve_resume_checkpoint,
    save_config_snapshot,
    save_run_metadata,
)
from rinalmo.runtime.guards import DiskSpaceGuard, EmergencyCheckpointOnException, NaNLossGuard


def _cfg_get(cfg: Any, key: str, default: Any) -> Any:
    value = OmegaConf.select(cfg, key)
    return default if value is None else value


def build_callbacks(cfg: Any) -> list[Any]:
    output_dir = Path(_cfg_get(cfg, "paths.output_dir", "./outputs/default"))
    ckpt_dir = checkpoint_dir(output_dir)

    monitor = _cfg_get(cfg, "callbacks.checkpoint.monitor", "val_loss")
    mode = _cfg_get(cfg, "callbacks.checkpoint.mode", "min")
    save_top_k = int(_cfg_get(cfg, "callbacks.checkpoint.save_top_k", 1))
    every_n_epochs = int(_cfg_get(cfg, "callbacks.checkpoint.every_n_epochs", 1))
    save_last = bool(_cfg_get(cfg, "callbacks.checkpoint.save_last", True))

    min_free_gb = float(_cfg_get(cfg, "callbacks.disk_guard.min_free_gb", 20.0))
    check_every_n_steps = int(_cfg_get(cfg, "callbacks.disk_guard.check_every_n_steps", 50))

    callbacks: list[Any] = [
        ModelCheckpoint(
            dirpath=str(ckpt_dir),
            filename="best",
            monitor=monitor,
            mode=mode,
            save_top_k=save_top_k,
            save_last=save_last,
            auto_insert_metric_name=False,
        ),
        ModelCheckpoint(
            dirpath=str(ckpt_dir),
            filename="epoch_{epoch:03d}",
            every_n_epochs=every_n_epochs,
            save_top_k=-1,
            auto_insert_metric_name=False,
        ),
        LearningRateMonitor(logging_interval="step"),
        NaNLossGuard(),
        DiskSpaceGuard(
            path=str(output_dir),
            min_free_gb=min_free_gb,
            check_every_n_steps=check_every_n_steps,
        ),
        EmergencyCheckpointOnException(str(output_dir)),
    ]
    return callbacks


def build_loggers(cfg: Any) -> list[Any]:
    output_dir = Path(_cfg_get(cfg, "paths.output_dir", "./outputs/default"))
    run_name = str(_cfg_get(cfg, "run.name", output_dir.name))
    csv_logger = CSVLogger(save_dir=str(output_dir), name="csv_logs")

    loggers: list[Any] = [csv_logger]

    use_wandb = bool(_cfg_get(cfg, "logging.wandb.enabled", False))
    if use_wandb:
        project = str(_cfg_get(cfg, "logging.wandb.project", "rinalmo"))
        wandb_logger = WandbLogger(
            project=project,
            name=run_name,
            save_dir=str(output_dir),
        )
        loggers.append(wandb_logger)

    return loggers


def prepare_run_artifacts(cfg: Any) -> None:
    output_dir = Path(_cfg_get(cfg, "paths.output_dir", "./outputs/default"))
    output_dir.mkdir(parents=True, exist_ok=True)

    save_config_snapshot(cfg, output_dir)
    save_run_metadata(
        output_dir,
        extra={
            "run_name": str(_cfg_get(cfg, "run.name", output_dir.name)),
            "seed": _cfg_get(cfg, "seed", None),
        },
    )


def build_trainer(cfg: Any) -> pl.Trainer:
    prepare_run_artifacts(cfg)

    trainer_kwargs = {
        "default_root_dir": str(_cfg_get(cfg, "paths.output_dir", "./outputs/default")),
        "max_epochs": int(_cfg_get(cfg, "trainer.max_epochs", 1)),
        "max_steps": int(_cfg_get(cfg, "trainer.max_steps", -1)),
        "accelerator": _cfg_get(cfg, "trainer.accelerator", "auto"),
        "devices": _cfg_get(cfg, "trainer.devices", 1),
        "precision": _cfg_get(cfg, "trainer.precision", "32-true"),
        "gradient_clip_val": float(_cfg_get(cfg, "trainer.gradient_clip_val", 1.0)),
        "log_every_n_steps": int(_cfg_get(cfg, "trainer.log_every_n_steps", 10)),
        "accumulate_grad_batches": int(_cfg_get(cfg, "trainer.accumulate_grad_batches", 1)),
        "callbacks": build_callbacks(cfg),
        "logger": build_loggers(cfg),
    }

    return pl.Trainer(**trainer_kwargs)


def resolve_ckpt_path_for_fit(cfg: Any) -> str | None:
    output_dir = Path(_cfg_get(cfg, "paths.output_dir", "./outputs/default"))
    resume = _cfg_get(cfg, "trainer.resume", None)
    return resolve_resume_checkpoint(output_dir=output_dir, resume=resume)
