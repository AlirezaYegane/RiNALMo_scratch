from __future__ import annotations

import subprocess
import sys
from typing import Any

from omegaconf import DictConfig, OmegaConf


def _normalize(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def build_argv(cfg: DictConfig) -> list[str]:
    argv: list[str] = []

    for key in cfg.legacy.get("positional_order", []):
        value = OmegaConf.select(cfg, key)
        if value is None:
            continue
        argv.append(_normalize(value))

    for key in cfg.legacy.get("option_order", []):
        value = OmegaConf.select(cfg, key)
        if value is None:
            continue
        flag = f"--{key.split('.')[-1]}"
        argv.extend([flag, _normalize(value)])

    for key in cfg.legacy.get("flag_order", []):
        value = OmegaConf.select(cfg, key)
        if bool(value):
            argv.append(f"--{key.split('.')[-1]}")

    return argv


def entrypoint_module(path: str) -> str:
    module_name, _func_name = path.split(":")
    return module_name


def run_legacy_entrypoint(path: str, argv: list[str]) -> None:
    module_name = entrypoint_module(path)
    cmd = [sys.executable, "-m", module_name, *argv]
    print("legacy_cmd:", " ".join(cmd))
    subprocess.run(cmd, check=True)
