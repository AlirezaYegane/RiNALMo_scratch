# RiNALMo Hardening Decisions Log

## D-001 — Freeze upstream before refactor
Status: Accepted
Reason:
We need a stable and reviewable baseline before restructuring the repository.

## D-002 — Treat core transformer implementation as protected
Status: Accepted
Protected scope:
- rinalmo/model/attention.py
- rinalmo/model/model.py
- rinalmo/model/modules.py
- rinalmo/model/rope.py
Reason:
Phase 1 focuses on engineering hardening, not changing the scientific core.

## D-003 — Delay major refactor of downstream heads
Status: Accepted
Reason:
Downstream heads will remain untouched unless tests or audits later prove breakage.

## D-004 — Introduce engineering layers incrementally
Status: Accepted
Planned additions in later subphases:
- src/
- configs/
- tests/
- scripts/
- docs/engineering/

## D-005 — Home-folder-first development on server
Status: Accepted
Reason:
Per server rules, code, environments, checkpoints, and related non-dataset artifacts must remain under the home directory.

