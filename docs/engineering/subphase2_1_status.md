# Subphase 2.1 Status

## Implemented
- source registry configs for RNAcentral, nt, Rfam, Ensembl
- raw source registration utility
- raw manifest integrity checker
- local-path validation hardening for registration

## Current blocker
As of the current H200 host session, raw pretraining source files were not found in:
- home directory scope
- common storage roots checked: /mnt, /srv, /opt

Therefore, real source registration into `data/raw/manifest.json` has not yet been completed on this host.

## Status
- 2.1A (registry/contracts/tooling): DONE
- 2.1B (real raw-source registration on actual data host): PENDING

## Next step
Proceed with Subphase 2.2 implementation on fixtures and wire it to real raw sources once the dataset mount/path is available.
