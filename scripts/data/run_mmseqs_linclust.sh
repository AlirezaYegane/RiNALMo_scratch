#!/usr/bin/env bash
set -euo pipefail

in_fasta="${1:?usage: run_mmseqs_linclust.sh <input.fa> <out_dir> [tmp_dir] [threads]}"
out_dir="${2:?usage: run_mmseqs_linclust.sh <input.fa> <out_dir> [tmp_dir] [threads]}"
tmp_dir="${3:-$out_dir/tmp}"
threads="${4:-32}"

mkdir -p "$out_dir" "$tmp_dir"

if [ ! -s "$in_fasta" ]; then
  echo "ERROR: input fasta is missing or empty: $in_fasta"
  exit 1
fi

prefix="$out_dir/linclust"

mmseqs easy-linclust \
  "$in_fasta" \
  "$prefix" \
  "$tmp_dir" \
  --min-seq-id 0.7 \
  -c 0.8 \
  --threads "$threads"

cluster_tsv="$(find "$out_dir" -maxdepth 1 -type f -name 'linclust*_cluster.tsv' | head -n 1 || true)"
if [ -z "$cluster_tsv" ]; then
  echo "ERROR: cluster TSV not found under $out_dir"
  find "$out_dir" -maxdepth 1 -type f | sort
  exit 1
fi

printf '%s\n' "$cluster_tsv" > "$out_dir/cluster_tsv.path"
echo "cluster TSV: $cluster_tsv"
