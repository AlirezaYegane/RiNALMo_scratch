# Subphase 6 — Data Contracts and Dataset Validation

## Scope
This subphase adds a contract-driven validation layer for pretraining data.
It does not run full paper-faithful preprocessing and does not require the 1TB-scale dataset bundle.

## Added in this subphase
- JSONL manifest loader
- per-record schema normalization and validation
- alphabet and length checks
- duplicate sequence_id detection
- missing-shard detection
- invalid-JSON / corrupted-shard detection
- manifest record-count validation
- dry-run dataset iterator
- minimal collator contract
- unit tests for validation, manifest loading, dataset iteration, collator behavior, and shard integrity

## Required sample fields
- sequence
- sequence_id
- source
- length
- optional cluster_id

## Deferred to later phases
- full RNAcentral/nt/Rfam/Ensembl ingestion
- seqkit/mmseqs pipeline
- LMDB build
- cluster-aware distributed sampling
- masking objective finalization
- large-scale pretraining runs
