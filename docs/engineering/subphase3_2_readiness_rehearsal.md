# Subphase 3.2 — H200 Readiness Rehearsal

## Goal
Run a clean, non-heavy readiness rehearsal before any longer H200 launch.

## What this subphase verifies
- Hydra config composition resolves for the H200 candidate command
- required training entrypoints and config files exist
- pretraining manifest and LMDB paths exist and are readable
- output/report directory is writable
- GPU visibility and basic H200 environment sanity
- launch command candidate is recorded
- readiness report is written as a machine-readable artifact

## Out of scope
- long dry run stability testing
- resume/recovery interruption testing
- paper-scale full launch

## Pass criteria
- no missing required files
- config compose succeeds
- manifest parses
- LMDB path exists
- readiness JSON report written
- preflight shell checks do not fail

## Output artifacts
- outputs/readiness/h200_readiness_report.json
- outputs/readiness/resolved_pretrain_config.yaml
