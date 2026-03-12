# Subphase 2.3 — Deduplication and Clustering

## Goal
Build a paper-faithful dedup + clustering stage after 2.2 filtering.

## Pipeline
1. export filtered JSONL to FASTA
2. remove exact duplicate sequences with seqkit rmdup
3. cluster unique sequences with mmseqs easy-linclust
4. build sequence_id -> cluster_id mapping

## Paper parameters
- seqkit rmdup for duplicate removal
- mmseqs easy-linclust
- --min-seq-id 0.7
- -c 0.8

## Outputs
- data/work/clustering/rmdup/unique.fa
- data/work/clustering/mmseqs/*
- data/work/clusters.jsonl
- data/work/clustering/cluster_stats.json

## Important note
Because subphase 2.2 emits filtered JSONL shards, this subphase adds a JSONL->FASTA bridge before seqkit/mmseqs.
