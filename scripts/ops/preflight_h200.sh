#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "=== repo root ==="
pwd

echo
echo "=== current branch ==="
git branch --show-current

echo
echo "=== git status (should be clean except ignored runtime dirs) ==="
git status --short

echo
echo "=== required config files ==="
required=(
  "configs/pretrain.yaml"
  "configs/runtime/h200_single.yaml"
  "configs/data/pretrain_lmdb.yaml"
  "configs/experiment/pretrain_dryrun.yaml"
)
for f in "${required[@]}"; do
  if [[ -f "$f" ]]; then
    echo "[OK] $f"
  else
    echo "[MISSING] $f"
    exit 1
  fi
done

echo
echo "=== python env ==="
if command -v python >/dev/null 2>&1; then
  python --version
  which python
elif command -v python3 >/dev/null 2>&1; then
  python3 --version
  which python3
else
  echo "[WARN] neither python nor python3 found on PATH"
fi

echo
echo "=== gpu check ==="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader
else
  echo "[WARN] nvidia-smi not found"
fi

echo
echo "=== disk check ==="
df -h .
[[ -d /mnt ]] && df -h /mnt || true

echo
echo "=== output roots ==="
mkdir -p outputs
echo "[OK] outputs/ ready"

echo
echo "preflight skeleton passed"
