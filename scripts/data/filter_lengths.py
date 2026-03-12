from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts._bootstrap import bootstrap_repo

bootstrap_repo()


def parse_args() -> argparse.Namespace:
    from rinalmo.data.pretrain.normalize import (
        MAX_SEQUENCE_LENGTH,
        MIN_SEQUENCE_LENGTH,
    )

    parser = argparse.ArgumentParser(
        description="Filter normalized sequence JSONL records by paper-faithful length bounds."
    )
    parser.add_argument("input", type=Path, help="Input normalized JSONL file")
    parser.add_argument("output", type=Path, help="Output filtered JSONL file")
    parser.add_argument(
        "--rejected",
        type=Path,
        required=True,
        help="Rejected-length JSONL output",
    )
    parser.add_argument(
        "--stats",
        type=Path,
        required=True,
        help="Path to write filtering stats JSON",
    )
    parser.add_argument("--min-len", type=int, default=MIN_SEQUENCE_LENGTH)
    parser.add_argument("--max-len", type=int, default=MAX_SEQUENCE_LENGTH)
    return parser.parse_args()


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    from rinalmo.data.pretrain.normalize import classify_length

    args = parse_args()

    kept_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []

    stats = {
        "total_lines": 0,
        "kept_records": 0,
        "rejected_invalid_json": 0,
        "rejected_non_object": 0,
        "rejected_missing_sequence": 0,
        "rejected_invalid_length": 0,
        "rejected_too_short": 0,
        "rejected_too_long": 0,
        "min_len": args.min_len,
        "max_len": args.max_len,
    }

    with args.input.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue

            stats["total_lines"] += 1

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "invalid_json",
                        "error": exc.msg,
                        "raw_line": raw_line.rstrip("\n"),
                    }
                )
                stats["rejected_invalid_json"] += 1
                continue

            if not isinstance(obj, dict):
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "non_object_record",
                        "raw_record": obj,
                    }
                )
                stats["rejected_non_object"] += 1
                continue

            sequence = obj.get("sequence")
            if not isinstance(sequence, str):
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "missing_sequence",
                        "raw_record": obj,
                    }
                )
                stats["rejected_missing_sequence"] += 1
                continue

            length_obj = obj.get("length", len(sequence))
            if not isinstance(length_obj, int):
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "invalid_length",
                        "raw_record": obj,
                    }
                )
                stats["rejected_invalid_length"] += 1
                continue

            verdict = classify_length(
                length_obj,
                min_len=args.min_len,
                max_len=args.max_len,
            )
            if verdict == "too_short":
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "too_short",
                        "length": length_obj,
                        "raw_record": obj,
                    }
                )
                stats["rejected_too_short"] += 1
                continue

            if verdict == "too_long":
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "too_long",
                        "length": length_obj,
                        "raw_record": obj,
                    }
                )
                stats["rejected_too_long"] += 1
                continue

            kept = dict(obj)
            kept["length"] = length_obj
            kept_records.append(kept)
            stats["kept_records"] += 1

    _write_jsonl(args.output, kept_records)
    _write_jsonl(args.rejected, rejected_records)

    args.stats.parent.mkdir(parents=True, exist_ok=True)
    args.stats.write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        f"kept={stats['kept_records']} "
        f"rejected={len(rejected_records)} "
        f"input={args.input}"
    )


if __name__ == "__main__":
    main()
