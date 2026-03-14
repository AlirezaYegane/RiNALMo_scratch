#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

ENV_PY=${ENV_PY:-/home/alirezay/micromamba/envs/rinalmo/bin/python}
export PYTHONPATH=$PWD/src
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}

echo "repo: $PWD"
echo "python: $ENV_PY"
echo "cuda_visible_devices: $CUDA_VISIBLE_DEVICES"

"$ENV_PY" scripts/train/pretrain.py \
  experiment=pretrain_dryrun \
  runtime=h200_single \
  data=pretrain_lmdb \
  train=pretrain_dryrun
