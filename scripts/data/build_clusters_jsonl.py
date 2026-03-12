from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def read_fasta_ids(path: Path) -> list[str]:
    ids: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(">"):
                ids.append(line[1:].strip().split()[0])
    return ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unique-fasta", required=True)
    ap.add_argument("--cluster-tsv", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--stats", required=True)
    args = ap.parse_args()

    unique_fasta = Path(args.unique_fasta)
    cluster_tsv = Path(args.cluster_tsv)
    output = Path(args.output)
    stats_path = Path(args.stats)

    all_ids = read_fasta_ids(unique_fasta)

    members_by_rep: dict[str, list[str]] = defaultdict(list)
    clustered_members: set[str] = set()

    with cluster_tsv.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                raise ValueError(f"invalid cluster tsv line at {cluster_tsv}:{line_no}")
            rep, member = parts[0], parts[1]
            members_by_rep[rep].append(member)
            clustered_members.add(member)

    for seq_id in all_ids:
        if seq_id not in clustered_members:
            members_by_rep[seq_id].append(seq_id)

    output.parent.mkdir(parents=True, exist_ok=True)
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    cluster_sizes: list[int] = []
    seq_count = 0

    with output.open("w", encoding="utf-8") as out:
        for idx, rep in enumerate(sorted(members_by_rep), start=1):
            cluster_id = f"clu_{idx:09d}"
            members = sorted(set(members_by_rep[rep]))
            cluster_sizes.append(len(members))
            for member in members:
                out.write(
                    json.dumps(
                        {
                            "sequence_id": member,
                            "cluster_id": cluster_id,
                            "representative_id": rep,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                seq_count += 1

    stats = {
        "num_sequences": seq_count,
        "num_clusters": len(cluster_sizes),
        "max_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
        "min_cluster_size": min(cluster_sizes) if cluster_sizes else 0,
    }
    stats_path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    print(f"wrote clusters jsonl: {output}")
    print(f"wrote stats: {stats_path}")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
