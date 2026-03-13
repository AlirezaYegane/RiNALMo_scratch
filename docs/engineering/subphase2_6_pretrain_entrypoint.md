# Subphase 2.6 — Pretraining Entrypoint and Config Parity

## Goal
Add a real from-scratch pretraining entrypoint that wires the already-built
dataset, collator, sampler, runtime hardening, and checkpointing together.

## Must-match paper behavior
- MLM pretraining
- 15% token selection
- input length up to 1024
- linear warmup
- cosine annealing
- min LR floor
- gradient clipping = 1.0

## Outputs of this subphase
- standard pretrain command
- config snapshot
- run summary
- smoke entrypoint ready for 2.7 tiny run
