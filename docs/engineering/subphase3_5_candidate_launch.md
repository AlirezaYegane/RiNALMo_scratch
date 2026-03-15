# Subphase 3.5 — Controlled H200 Candidate Launch

## Goal
Prepare a controlled pretraining launch on the current LMDB/subset setup under server policy constraints.

## Frozen candidate command
PYTHONPATH=$PWD/src "/home/alirezay/micromamba/envs/rinalmo/bin/python" \
  scripts/train/pretrain.py \
  experiment=pretrain_subset \
  runtime=h200_single \
  data=pretrain_lmdb \
  train@_global_=pretrain_subset

## Storage policy
- datasets remain under /Datasets
- code, env, logs, checkpoints, and outputs remain under home/repo space
- no uncontrolled writes outside the project output tree

## Expected artifacts
- console.log
- metrics.csv
- config_snapshot.yaml
- run_summary.json
- last.ckpt
- best.ckpt
- epoch checkpoints

## Launch gates
- prebooking gate report exists
- readiness rehearsal passed
- booking evidence exists
- current branch is clean enough for launch

## Retention policy
- keep latest candidate launch output
- keep last.ckpt and best.ckpt
- older candidate launch directories may be archived or deleted manually after review

## Scope boundary
This is not the full paper-scale launch.
It is the policy-safe controlled candidate launch on the currently prepared LMDB/subset path.
