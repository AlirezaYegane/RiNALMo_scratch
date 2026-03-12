from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_critical_files_exist() -> None:
    required = [
        "pyproject.toml",
        "configs/config.yaml",
        "src/rinalmo/training/base.py",
        "src/rinalmo/runtime/checkpointing.py",
        "src/rinalmo/runtime/guards.py",
        "scripts/train/pretrain.py",
        "scripts/data/validate_pretrain_manifest.py",
        "docs/engineering/subphase6_data_contracts.md",
    ]
    missing = [p for p in required if not (REPO_ROOT / p).exists()]
    assert not missing, f"missing critical files: {missing}"
