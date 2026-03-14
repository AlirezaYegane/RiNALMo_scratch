# Subphase 2.1B Blocker

## Summary
Raw pretraining source files were not found on the current host in the checked paths.

## Paper-intended raw sources
- RNAcentral
- nt
- Rfam
- Ensembl

## Current decision
- Do NOT download the 1TB-scale dataset bundle on this host.
- Respect server storage / policy constraints.
- Keep 2.1A as DONE (registry/config/tooling).
- Keep 2.1B as PENDING/BLOCKED until approved raw-source paths are mounted or provided.

## Impact
- Phase 2 remains valid as an engineering closeout for the subset-backed pipeline.
- Phase 3 may proceed only as a controlled H200 candidate launch on the validated subset/LMDB path.
- Full paper-scale launch remains blocked until raw-source availability is resolved.

## Rationale
The project already established fixture/subset/data-contract validation paths that do not require the 1TB-scale bundle.
