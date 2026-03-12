from __future__ import annotations

import math
import shutil
from pathlib import Path

from lightning.pytorch.callbacks import Callback


class NaNLossGuard(Callback):
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if outputs is None:
            return

        loss = None
        if hasattr(outputs, "get"):
            loss = outputs.get("loss", None)
        elif hasattr(outputs, "loss"):
            loss = outputs.loss

        if loss is None:
            return

        try:
            value = float(loss.detach().float().cpu().item())
        except Exception:
            return

        if math.isnan(value) or math.isinf(value):
            raise RuntimeError(
                f"NaN/Inf loss detected at global_step={trainer.global_step}: {value}"
            )


class DiskSpaceGuard(Callback):
    def __init__(
        self,
        path: str,
        min_free_gb: float = 20.0,
        check_every_n_steps: int = 50,
    ):
        super().__init__()
        self.path = str(path)
        self.min_free_gb = float(min_free_gb)
        self.check_every_n_steps = int(check_every_n_steps)

    def _free_gb(self) -> float:
        usage = shutil.disk_usage(self.path)
        return usage.free / (1024 ** 3)

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if self.check_every_n_steps <= 0:
            return
        if trainer.global_step % self.check_every_n_steps != 0:
            return

        free_gb = self._free_gb()
        if free_gb < self.min_free_gb:
            raise RuntimeError(
                f"Low disk space at {self.path}: free={free_gb:.2f} GB < required={self.min_free_gb:.2f} GB"
            )


class EmergencyCheckpointOnException(Callback):
    def __init__(self, output_dir: str):
        super().__init__()
        self.output_dir = Path(output_dir)

    def on_exception(self, trainer, pl_module, exception):
        ckpt_dir = self.output_dir / "checkpoints"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        emergency_path = ckpt_dir / "emergency.ckpt"
        trainer.save_checkpoint(str(emergency_path))
