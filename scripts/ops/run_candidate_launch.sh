#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/projects/RiNALMo}"
cd "$REPO_ROOT"

ENV_PY="${ENV_PY:-/home/alirezay/micromamba/envs/rinalmo/bin/python}"
if [[ ! -x "$ENV_PY" ]]; then
  ENV_PY=python3
fi

BOOKING_EVIDENCE="outputs/readiness/booking_evidence.txt"
GATE_REPORT="outputs/readiness/prebooking_gate_report.json"

if [[ ! -f "$GATE_REPORT" ]]; then
  echo "[ERROR] missing gate report: $GATE_REPORT"
  exit 1
fi

if [[ ! -f "$BOOKING_EVIDENCE" ]]; then
  echo "[BLOCKED] booking evidence missing: $BOOKING_EVIDENCE"
  exit 2
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="outputs/pretrain_candidate_launch/${STAMP}"
mkdir -p "$OUT_DIR"

git status --short > "$OUT_DIR/git_status.txt" || true
git rev-parse HEAD > "$OUT_DIR/git_commit.txt" || true

cat > "$OUT_DIR/launch_command.txt" <<CMD
PYTHONPATH=$PWD/src "$ENV_PY" scripts/train/pretrain.py experiment=pretrain_subset runtime=h200_single data=pretrain_lmdb train@_global_=pretrain_subset hydra.run.dir="$OUT_DIR"
CMD

echo "[INFO] output_dir=$OUT_DIR"

PYTHONPATH="$PWD/src" "$ENV_PY" scripts/train/pretrain.py \
  experiment=pretrain_subset \
  runtime=h200_single \
  data=pretrain_lmdb \
  train@_global_=pretrain_subset \
  hydra.run.dir="$OUT_DIR" \
  2>&1 | tee "$OUT_DIR/console.log"

echo "[INFO] candidate launch finished"
