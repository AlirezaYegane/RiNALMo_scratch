from __future__ import annotations

import argparse
import json
from pathlib import Path


def iter_jsonl_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(p for p in path.glob("*.jsonl") if p.is_file())
    return [path]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="filtered jsonl file or directory")
    ap.add_argument("--output", required=True, help="output fasta path")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    files = iter_jsonl_files(in_path)
    if not files:
        raise SystemExit(f"no jsonl files found under: {in_path}")

    seen_ids: set[str] = set()
    count = 0

    with out_path.open("w", encoding="utf-8") as out:
        for file in files:
            with file.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)

                    seq_id = str(obj["sequence_id"]).strip()
                    seq = str(obj["sequence"]).strip().upper()

                    if not seq_id:
                        raise ValueError(f"empty sequence_id in {file}:{line_no}")
                    if not seq:
                        raise ValueError(f"empty sequence in {file}:{line_no}")
                    if seq_id in seen_ids:
                        raise ValueError(f"duplicate sequence_id while exporting fasta: {seq_id}")

                    seen_ids.add(seq_id)
                    out.write(f">{seq_id}\n{seq}\n")
                    count += 1

    print(f"wrote {count} FASTA records to {out_path}")


if __name__ == "__main__":
    main()
