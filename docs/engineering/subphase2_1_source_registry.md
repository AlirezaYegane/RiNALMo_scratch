# Subphase 2.1 — Source Registry and Raw Data Ingestion

## Scope
This subphase formalizes raw pretraining data sources before canonicalization and filtering.

## Paper-aligned sources
- RNAcentral
- nt
- Rfam
- Ensembl

## Added in this subphase
- per-source YAML registry files
- raw manifest JSON
- raw source registration script
- raw manifest integrity checker

## Non-goals
- full download orchestration for all sources
- sequence normalization
- deduplication
- clustering
- LMDB packaging
- pretraining launch

## Output contracts
Each registered raw source record includes:
- source_name
- kind
- local_path
- url
- size_bytes
- modified_at
- checksum_sha256
- status
