from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def checkpoint_dir(output_dir: str | Path) -> Path:
    return ensure_dir(Path(output_dir) / "checkpoints")


def resolve_resume_checkpoint(
    output_dir: str | Path,
    resume: str | None = None,
) -> str | None:
    """
    Rules:
    - resume=None / "" / "false" => no resume
    - resume="auto" / "last" => output_dir/checkpoints/last.ckpt if exists
    - otherwise treat resume as an explicit checkpoint path
    """
    if resume is None:
        return None

    resume_str = str(resume).strip()
    if resume_str == "" or resume_str.lower() in {"none", "false", "no"}:
        return None

    if resume_str.lower() in {"auto", "last"}:
        candidate = checkpoint_dir(output_dir) / "last.ckpt"
        return str(candidate) if candidate.exists() else None

    candidate = Path(resume_str).expanduser()
    if not candidate.exists():
        raise FileNotFoundError(f"Resume checkpoint not found: {candidate}")
    return str(candidate)


def save_config_snapshot(cfg: Any, output_dir: str | Path) -> Path:
    out_dir = ensure_dir(output_dir)
    path = out_dir / "config_snapshot.yaml"
    path.write_text(OmegaConf.to_yaml(cfg, resolve=True))
    return path


def _safe_git(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except Exception:
        return None


def collect_run_metadata(output_dir: str | Path) -> dict[str, Any]:
    out_dir = ensure_dir(output_dir)
    return {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "output_dir": str(out_dir.resolve()),
        "cwd": os.getcwd(),
        "git_commit": _safe_git(["git", "rev-parse", "HEAD"]),
        "git_branch": _safe_git(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "hostname": os.uname().nodename if hasattr(os, "uname") else None,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "wandb_disabled": os.environ.get("WANDB_DISABLED"),
    }


def save_run_metadata(output_dir: str | Path, extra: dict[str, Any] | None = None) -> Path:
    out_dir = ensure_dir(output_dir)
    payload = collect_run_metadata(out_dir)
    if extra:
        payload.update(extra)

    path = out_dir / "run_summary.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return path
