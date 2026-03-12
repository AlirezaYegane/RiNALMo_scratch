from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_KEYS = {"sequence_id", "sequence", "source", "length"}
MANIFEST_KEYS = {"shard_path", "num_records"}

SKIP_SUFFIXES = (
    ".rejected.jsonl",
    ".rejects.jsonl",
    ".errors.jsonl",
    ".stats.jsonl",
)


def iter_jsonl_files(path: Path) -> list[Path]:
    if path.is_dir():
        files = []
        for p in sorted(path.glob("*.jsonl")):
            if not p.is_file():
                continue
            if p.name == "manifest.jsonl":
                files.append(p)
                continue
            if p.name.endswith(SKIP_SUFFIXES):
                continue
            files.append(p)
        return files
    return [path]


def is_manifest_like(obj: dict[str, object]) -> bool:
    keys = set(obj.keys())
    return MANIFEST_KEYS.issubset(keys) and "sequence" not in keys


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
    skipped_manifest = 0

    with out_path.open("w", encoding="utf-8") as out:
        for file in files:
            with file.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"invalid json in {file}:{line_no}: {exc.msg}"
                        ) from exc

                    if not isinstance(obj, dict):
                        raise ValueError(
                            f"expected JSON object in {file}:{line_no}, got {type(obj).__name__}"
                        )

                    if is_manifest_like(obj):
                        skipped_manifest += 1
                        continue

                    keys = set(obj.keys())
                    missing = REQUIRED_KEYS - keys
                    if missing:
                        raise ValueError(
                            f"unexpected filtered record schema in {file}:{line_no}; "
                            f"missing={sorted(missing)} keys={sorted(keys)}"
                        )

                    seq_id = str(obj["sequence_id"]).strip()
                    seq = str(obj["sequence"]).strip().upper()

                    if not seq_id:
                        raise ValueError(f"empty sequence_id in {file}:{line_no}")
                    if not seq:
                        raise ValueError(f"empty sequence in {file}:{line_no}")
                    if seq_id in seen_ids:
                        raise ValueError(
                            f"duplicate sequence_id while exporting fasta: {seq_id}"
                        )

                    seen_ids.add(seq_id)
                    out.write(f">{seq_id}\n{seq}\n")
                    count += 1

    print(
        f"wrote {count} FASTA records to {out_path} "
        f"(skipped_manifest_lines={skipped_manifest})"
    )


if __name__ == "__main__":
    main()
