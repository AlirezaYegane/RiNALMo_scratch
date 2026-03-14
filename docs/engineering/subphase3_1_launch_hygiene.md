# Subphase 3.1 — Repo Cleanup and Launch Hygiene

## Scope
This subphase prepares the repository for phase-3 launch operations.

## Includes
- keeping the working tree clean
- ignoring generated runtime artifacts
- adding preflight ops helpers
- standardizing launch hygiene checks before any H200-facing run

## Explicitly excluded
- longer dry run
- resume/recovery validation
- controlled candidate launch
- full paper-scale launch

## Current context
Phase 3 is launch-oriented, but this subphase is only the cleanup/hygiene gate before readiness rehearsal.

## Carry-forward blocker
Full paper-scale launch remains blocked until raw-source availability / real source registration is completed.

## Deliverables
- repo hygiene note
- artifact ignore policy
- preflight ops script
- clean git status before 3.2
