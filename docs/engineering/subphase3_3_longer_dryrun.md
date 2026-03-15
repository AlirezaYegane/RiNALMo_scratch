# Subphase 3.3 — Longer Dry Run

## Goal
Prepare a longer dry run than 2.7 to validate real stability characteristics before any booked H200 execution.

## Frozen candidate command
PYTHONPATH=$PWD/src "/home/alirezay/micromamba/envs/rinalmo/bin/python" \
  scripts/train/pretrain.py \
  experiment=pretrain_dryrun \
  runtime=h200_single \
  data=pretrain_lmdb \
  train@_global_=pretrain_dryrun

## Scope
This subphase prepares the controlled longer dry-run execution path for:
- memory stability
- throughput sanity
- logging continuity
- checkpoint cadence
- loss behavior

## Expected artifacts
- console.log
- metrics.csv
- config_snapshot.yaml
- run_summary.json
- last.ckpt

## Pass criteria
- no OOM
- no NaN/Inf
- logs continue throughout the run
- checkpoints are written
- run_summary.json is written
- config_snapshot.yaml is written

## Policy
Execution is allowed only after:
1. data audit gate is acceptable
2. readiness rehearsal has passed
3. booking evidence exists

Until booking evidence is added, this document and script are prep-pack only.
