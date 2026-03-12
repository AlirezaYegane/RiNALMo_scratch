from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_manifest_validator_help() -> None:
    proc = _run(
        [sys.executable, "scripts/data/validate_pretrain_manifest.py", "--help"]
    )
    assert proc.returncode == 0, proc.stderr
    assert "manifest" in proc.stdout.lower()


def test_root_wrapper_help_smoke() -> None:
    proc = _run([sys.executable, "train_sec_struct_prediction.py", "--help"])
    assert proc.returncode == 0, proc.stderr
    assert "usage" in proc.stdout.lower() or "help" in proc.stdout.lower()
