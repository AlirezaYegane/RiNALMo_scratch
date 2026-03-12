# Subphase 2.2 — Canonicalization and Sequence Filtering

## Scope
This subphase implements paper-faithful canonicalization and length filtering for
pretraining sequence records without requiring the full raw dataset mount.

## Implemented
- sequence canonicalization utility
- whitespace stripping
- uppercase normalization
- U -> T conversion
- alphabet validation against RiNALMo tokenization alphabet
- rejection of empty / malformed / invalid-alphabet records
- paper-faithful sequence length filtering with bounds 16..8192
- fixture-based tests for normalization and filtering scripts

## Scripts
- scripts/data/normalize_sequences.py
- scripts/data/filter_lengths.py

## Outputs
- data/work/normalized/*.jsonl
- data/work/filtered/*.jsonl

## Notes
This implementation assumes JSONL sequence records as the processing contract for
this subphase. A FASTA/FA.GZ adapter can be added later without changing the
canonicalization core.
