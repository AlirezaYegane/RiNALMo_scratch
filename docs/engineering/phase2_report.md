# Phase 2 Closeout Report

## Scope
Phase 2 focused on building a paper-faithful pretraining pipeline up to validated tiny/subset/GPU dryrun execution.

## Status by subphase
- 2.1A source registry/contracts/tooling: DONE
- 2.1B real raw-source registration on actual data host: PENDING
- 2.2 canonicalization/filtering: DONE
- 2.3 dedup/clustering on working subset: DONE
- 2.4 LMDB packaging: DONE
- 2.5 collator and cluster-aware sampler: DONE
- 2.6 pretraining entrypoint and config parity: DONE
- 2.7 tiny/subset/GPU dryrun validation: DONE
- 2.8 phase closeout and launch pack: DONE

## Intended pretraining sources
- RNAcentral
- nt
- Rfam
- Ensembl

## Implemented paper-aligned behaviors
- source registry scaffold for the intended paper datasets
- sequence canonicalization path
- filtering path for valid training records
- dedup + clustering workflow
- LMDB packaging
- MLM masking path
- crop path for pretraining inputs
- one-per-cluster-per-epoch sampling path
- warmup + cosine schedule path
- gradient clipping path
- checkpointing and resume-safe runtime artifacts

## Phase 2 artifacts
- scripts/train/pretrain.py
- data/pretrain/manifest.jsonl
- data/pretrain/records.lmdb
- outputs/*/best.ckpt
- outputs/*/last.ckpt
- outputs/*/config_snapshot.yaml
- outputs/*/metrics.csv
- outputs/*/run_summary.json

## Current readiness statement
The engineering pipeline is ready for a controlled H200 launch candidate.
It is not yet a full paper-scale launch because full raw-source registration on the actual data host is still pending.

## Known limitations
- Full raw-source registration into data/raw/manifest.json is not complete on the current host.
- Current successful GPU dryrun should be treated as functional validation, not full-corpus validation.
- Final paper-scale Phase 3 launch should only begin after raw source availability is confirmed and a longer dryrun is completed on the intended H200 path.
- The 1TB-scale dataset bundle is intentionally not downloaded on this host due to storage/policy constraints.

## Go / No-Go
- GO: controlled H200 candidate launch on the currently validated subset-backed pipeline
- NO-GO: full paper-scale launch until 2.1B is closed
