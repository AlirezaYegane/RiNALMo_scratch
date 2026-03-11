# Repository Restructure Notes

## Scope of Subphase 2
This subphase performs safe structural cleanup without changing scientific logic.

## Completed structural moves
- moved Python package from `rinalmo/` to `src/rinalmo/`
- moved top-level training scripts to `scripts/train/`
- added compatibility bootstrap under `scripts/_bootstrap.py`
- preserved top-level command compatibility with thin wrapper scripts

## Deferred moves
The following internal refactors are intentionally deferred to avoid breaking imports too early:
- splitting `utils/` into `training/`, `runtime/`, and data-specific modules
- rewriting task wrappers into `src/rinalmo/training/tasks/`
- final packaging cleanup in `pyproject.toml`
