# Subphase 3.4 — Resume / Recovery Validation

## Goal
Validate that a stopped pretraining run can resume from last.ckpt without losing training continuity.

## Source checkpoint
The resume validation must consume last.ckpt from a successful 3.3 longer dry run.

## Resume scenario
1. run 3.3 and confirm last.ckpt exists
2. stop the job cleanly or use the final written last.ckpt
3. relaunch pretraining from that checkpoint into a fresh output directory
4. verify continuity in logs and metrics

## Expected evidence
- explicit restore log lines
- checkpoint path used
- resumed output directory
- metrics continuation after resume
- new config snapshot
- new run summary

## Pass criteria
- restore of global step
- restore of epoch
- restore of optimizer state
- restore of scheduler state
- restore of logger continuity
- no immediate crash after resume
- resumed run writes logs and checkpoints again

## Important note
The exact resume override key may differ depending on current pretrain.py CLI wiring.
This prep-pack keeps the resume key configurable at execution time.

## Policy
Execution is allowed only after:
1. successful 3.3 output with last.ckpt
2. readiness rehearsal already passed
3. booking evidence exists
