#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_PY="${ENV_PY:-/home/alirezay/micromamba/envs/rinalmo/bin/python}"

cd "$REPO_ROOT"
export PYTHONPATH="$REPO_ROOT/src:$REPO_ROOT"
export MYPYPATH="$REPO_ROOT/src"

RUFF_TARGETS=(
  tests/integration/repro
  scripts/ops/check_h200_readiness.py
  scripts/data/validate_pretrain_manifest.py
  scripts/train/pretrain.py
  train_expression_level.py
  train_ribosome_loading.py
  train_sec_struct_prediction.py
  train_splice_site_prediction.py
  train_translation_efficiency.py
  src/rinalmo/runtime
  src/rinalmo/training
  src/rinalmo/hydra_bridge
  src/rinalmo/data/pretrain
)

MYPY_TARGETS=(
  src/rinalmo/runtime
  src/rinalmo/training
  src/rinalmo/hydra_bridge
  src/rinalmo/data/pretrain
)

echo "[1/5] import smoke"
"$ENV_PY" - <<'PY'
import importlib

mods = [
    "rinalmo",
    "scripts._bootstrap",
    "scripts.train.pretrain",
    "train_sec_struct_prediction",
]
for m in mods:
    importlib.import_module(m)
    print("OK:", m)
PY

echo "[2/5] ruff (scoped)"
"$ENV_PY" -m ruff check "${RUFF_TARGETS[@]}"

echo "[3/5] mypy (scoped)"
"$ENV_PY" -m mypy --explicit-package-bases "${MYPY_TARGETS[@]}"

echo "[4/5] pytest"
"$ENV_PY" -m pytest -q tests/unit tests/integration -rA

echo "[5/5] readiness"
"$ENV_PY" scripts/ops/check_h200_readiness.py

echo "phase7 quality gates: PASS"
