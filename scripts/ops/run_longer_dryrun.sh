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
  echo "Run scripts/ops/check_prebooking_gate.py first."
  exit 1
fi

if [[ ! -f "$BOOKING_EVIDENCE" ]]; then
  echo "[BLOCKED] booking evidence missing: $BOOKING_EVIDENCE"
  echo "3.3 script is prepared, but execution remains blocked before booking."
  exit 2
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="outputs/pretrain_longer_dryrun/${STAMP}"
mkdir -p "$OUT_DIR"

echo "[INFO] output_dir=$OUT_DIR"

PYTHONPATH="$PWD/src" "$ENV_PY" scripts/train/pretrain.py \
  experiment=pretrain_dryrun \
  runtime=h200_single \
  data=pretrain_lmdb \
  train@_global_=pretrain_dryrun \
  hydra.run.dir="$OUT_DIR" \
  2>&1 | tee "$OUT_DIR/console.log"

echo "[INFO] longer dryrun finished"
