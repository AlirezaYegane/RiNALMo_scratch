# Packaging Notes

## Scope of Subphase 3
This subphase aligns packaging with the new src-layout and makes installation deterministic.

## Main changes
- switched package discovery to `src/`
- standardized license metadata to Apache-2.0
- added optional dependency groups:
  - train
  - dev
  - flash
  - wandb
  - bio-tools
- added tool configuration for:
  - pytest
  - ruff
  - mypy
  - coverage
- added MANIFEST.in for package resources

## Important note
PyTorch and CUDA-specific stack are intentionally not pinned in pyproject extras.
They remain environment-managed to avoid destabilizing the working server setup.
