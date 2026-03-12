from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts._bootstrap import bootstrap_repo

bootstrap_repo()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Canonicalize sequence JSONL records for RiNALMo pretraining."
    )
    parser.add_argument("input", type=Path, help="Input JSONL file")
    parser.add_argument("output", type=Path, help="Output normalized JSONL file")
    parser.add_argument(
        "--rejected",
        type=Path,
        required=True,
        help="Rejected-record JSONL output",
    )
    parser.add_argument(
        "--stats",
        type=Path,
        required=True,
        help="Path to write normalization stats JSON",
    )
    return parser.parse_args()


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    from rinalmo.data.pretrain.normalize import normalize_sequence

    args = parse_args()

    normalized_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []

    stats = {
        "total_lines": 0,
        "normalized_records": 0,
        "rejected_invalid_json": 0,
        "rejected_non_object": 0,
        "rejected_missing_sequence": 0,
        "rejected_empty_sequence": 0,
        "rejected_invalid_alphabet": 0,
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

            raw_sequence = obj.get("sequence")
            if not isinstance(raw_sequence, str):
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "missing_sequence",
                        "raw_record": obj,
                    }
                )
                stats["rejected_missing_sequence"] += 1
                continue

            result = normalize_sequence(raw_sequence)

            if not result.sequence:
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "empty_sequence",
                        "raw_record": obj,
                    }
                )
                stats["rejected_empty_sequence"] += 1
                continue

            if result.invalid_characters:
                rejected_records.append(
                    {
                        "line_no": line_no,
                        "reason": "invalid_alphabet",
                        "invalid_characters": list(result.invalid_characters),
                        "raw_record": obj,
                        "canonicalized_sequence": result.sequence,
                    }
                )
                stats["rejected_invalid_alphabet"] += 1
                continue

            normalized = dict(obj)
            normalized["sequence"] = result.sequence
            normalized["length"] = result.length

            normalized_records.append(normalized)
            stats["normalized_records"] += 1

    _write_jsonl(args.output, normalized_records)
    _write_jsonl(args.rejected, rejected_records)

    args.stats.parent.mkdir(parents=True, exist_ok=True)
    args.stats.write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        f"normalized={stats['normalized_records']} "
        f"rejected={len(rejected_records)} "
        f"input={args.input}"
    )


if __name__ == "__main__":
    main()
