#!/usr/bin/env bash
set -euo pipefail

in_fasta="${1:?usage: run_seqkit_rmdup.sh <input.fa> <out_dir>}"
out_dir="${2:?usage: run_seqkit_rmdup.sh <input.fa> <out_dir>}"

mkdir -p "$out_dir"

seqkit stat "$in_fasta" > "$out_dir/input.stat.txt"

seqkit rmdup \
  --by-seq \
  --ignore-case \
  -D "$out_dir/duplicates.detail.txt" \
  -o "$out_dir/unique.fa" \
  "$in_fasta"

seqkit stat "$out_dir/unique.fa" > "$out_dir/unique.stat.txt"

echo "unique fasta: $out_dir/unique.fa"
echo "duplicate detail: $out_dir/duplicates.detail.txt"
