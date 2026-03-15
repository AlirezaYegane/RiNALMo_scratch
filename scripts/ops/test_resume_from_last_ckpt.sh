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

LATEST_RUN="$(find outputs/pretrain_longer_dryrun -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1 || true)"
if [[ -z "${LATEST_RUN:-}" ]]; then
  echo "[ERROR] no 3.3 run directory found under outputs/pretrain_longer_dryrun"
  exit 3
fi

LAST_CKPT="$LATEST_RUN/last.ckpt"
if [[ ! -f "$LAST_CKPT" ]]; then
  echo "[ERROR] missing checkpoint: $LAST_CKPT"
  exit 4
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="outputs/pretrain_resume_validation/${STAMP}"
mkdir -p "$OUT_DIR"

RESUME_KV="${RESUME_KV:-ckpt_path}"

echo "[INFO] latest_run=$LATEST_RUN"
echo "[INFO] last_ckpt=$LAST_CKPT"
echo "[INFO] resume_override_key=$RESUME_KV"
echo "[INFO] output_dir=$OUT_DIR"

cat > "$OUT_DIR/resume_plan.txt" <<PLAN
source_run=$LATEST_RUN
checkpoint=$LAST_CKPT
resume_override_key=$RESUME_KV
command=PYTHONPATH=$PWD/src $ENV_PY scripts/train/pretrain.py experiment=pretrain_dryrun runtime=h200_single data=pretrain_lmdb train@_global_=pretrain_dryrun ${RESUME_KV}=$LAST_CKPT hydra.run.dir=$OUT_DIR
PLAN

PYTHONPATH="$PWD/src" "$ENV_PY" scripts/train/pretrain.py \
  experiment=pretrain_dryrun \
  runtime=h200_single \
  data=pretrain_lmdb \
  train@_global_=pretrain_dryrun \
  "${RESUME_KV}=$LAST_CKPT" \
  hydra.run.dir="$OUT_DIR" \
  2>&1 | tee "$OUT_DIR/console.log"

echo "[INFO] resume validation finished"
