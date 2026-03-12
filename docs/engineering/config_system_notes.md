# Subphase 4 - Unified Config System Notes

## Goal
Introduce a Hydra-based central config system without changing scientific model logic.

## Scope
This subphase intentionally migrates only one task first:
- splice-site prediction

## Design
- Hydra composes configs from `configs/`
- a lightweight bridge converts resolved config into legacy CLI argv
- legacy task entrypoints remain intact
- relative paths are preserved by setting `hydra.job.chdir=false`

## Why this approach
This gives us central config management now, while avoiding risky rewrites of training internals too early.

## Deferred
- migrating all remaining downstream task entrypoints
- replacing legacy argparse inside task scripts
- base trainer abstraction
- checkpoint/resume hardening
