# Subphase 2.5 — Collator and Pretraining Data Pipeline

## Scope
This subphase adds the paper-aligned masking/crop/sampling layer needed before a true pretraining entrypoint.

## Implemented
- MLM collator
- 15% masking policy
- 80/10/10 corruption rule
- crop-to-1024 behavior
- [CLS]/[EOS]/[PAD] handling
- one-sample-per-cluster-per-epoch sampler
- unit tests for masking, crop behavior, and cluster-aware sampling

## Important note
Paper-faithful behavior requires real `cluster_id` values to be exposed by the packaged pretraining dataset.
If `cluster_id` is missing, sampler falls back to singleton sampling only as a temporary safety fallback.

## Deferred to 2.6
- actual pretraining entrypoint
- optimizer/scheduler parity
- runtime logging/checkpoint integration
