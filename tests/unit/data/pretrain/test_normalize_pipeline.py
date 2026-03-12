from __future__ import annotations

import json
from pathlib import Path

from rinalmo.data.pretrain.normalize import (
    CanonicalizationResult,
    canonicalize_sequence,
    classify_length,
    get_invalid_characters,
    normalize_sequence,
)
from scripts.data.filter_lengths import main as filter_main
from scripts.data.normalize_sequences import main as normalize_main


def _read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_canonicalize_sequence_uppercases_strips_ws_and_replaces_u() -> None:
    assert canonicalize_sequence("a u\ng\tcU") == "ATGCT"


def test_invalid_characters_detected_after_canonicalization() -> None:
    assert get_invalid_characters("ACTGN-XZJ") == ("J", "X", "Z")


def test_normalize_sequence_returns_expected_result() -> None:
    result = normalize_sequence("augc augc")
    assert result == CanonicalizationResult(
        sequence="ATGCATGC",
        length=8,
        invalid_characters=(),
    )


def test_classify_length_respects_paper_bounds() -> None:
    assert classify_length(15) == "too_short"
    assert classify_length(16) == "ok"
    assert classify_length(8192) == "ok"
    assert classify_length(8193) == "too_long"


def test_normalize_script_end_to_end(tmp_path: Path) -> None:
    input_path = Path("tests/fixtures/pretrain/raw_sequences.jsonl")
    output_path = tmp_path / "normalized.jsonl"
    rejected_path = tmp_path / "rejected.jsonl"
    stats_path = tmp_path / "normalize_stats.json"

    import sys

    argv_backup = sys.argv
    sys.argv = [
        "normalize_sequences.py",
        str(input_path),
        str(output_path),
        "--rejected",
        str(rejected_path),
        "--stats",
        str(stats_path),
    ]
    try:
        normalize_main()
    finally:
        sys.argv = argv_backup

    normalized = _read_jsonl(output_path)
    rejected = _read_jsonl(rejected_path)
    stats = json.loads(stats_path.read_text(encoding="utf-8"))

    assert [row["sequence_id"] for row in normalized] == [
        "ok_u_lower",
        "short_valid",
        "ok_ambiguous",
    ]
    assert normalized[0]["sequence"] == "ATGCATGCATGCATGC"
    assert normalized[0]["length"] == 16
    assert normalized[1]["sequence"] == "ATGC"

    rejected_reasons = {row["reason"] for row in rejected}
    assert rejected_reasons == {"empty_sequence", "invalid_alphabet"}

    assert stats["normalized_records"] == 3
    assert stats["rejected_empty_sequence"] == 1
    assert stats["rejected_invalid_alphabet"] == 1


def test_filter_script_end_to_end(tmp_path: Path) -> None:
    raw_input = Path("tests/fixtures/pretrain/raw_sequences.jsonl")
    normalized_path = tmp_path / "normalized.jsonl"
    normalize_rejected_path = tmp_path / "normalize_rejected.jsonl"
    normalize_stats_path = tmp_path / "normalize_stats.json"

    import sys

    argv_backup = sys.argv
    sys.argv = [
        "normalize_sequences.py",
        str(raw_input),
        str(normalized_path),
        "--rejected",
        str(normalize_rejected_path),
        "--stats",
        str(normalize_stats_path),
    ]
    try:
        normalize_main()
    finally:
        sys.argv = argv_backup

    filtered_path = tmp_path / "filtered.jsonl"
    filter_rejected_path = tmp_path / "filter_rejected.jsonl"
    filter_stats_path = tmp_path / "filter_stats.json"

    argv_backup = sys.argv
    sys.argv = [
        "filter_lengths.py",
        str(normalized_path),
        str(filtered_path),
        "--rejected",
        str(filter_rejected_path),
        "--stats",
        str(filter_stats_path),
    ]
    try:
        filter_main()
    finally:
        sys.argv = argv_backup

    filtered = _read_jsonl(filtered_path)
    rejected = _read_jsonl(filter_rejected_path)
    stats = json.loads(filter_stats_path.read_text(encoding="utf-8"))

    assert [row["sequence_id"] for row in filtered] == ["ok_u_lower", "ok_ambiguous"]
    assert [row["reason"] for row in rejected] == ["too_short"]
    assert rejected[0]["length"] == 4

    assert stats["kept_records"] == 2
    assert stats["rejected_too_short"] == 1
    assert stats["rejected_too_long"] == 0


def test_filter_script_rejects_too_long_records(tmp_path: Path) -> None:
    long_input = tmp_path / "long_normalized.jsonl"
    long_output = tmp_path / "long_filtered.jsonl"
    rejected_path = tmp_path / "long_rejected.jsonl"
    stats_path = tmp_path / "long_stats.json"

    long_sequence = "A" * 8193
    long_input.write_text(
        json.dumps(
            {
                "sequence_id": "too_long",
                "source": "fixture",
                "sequence": long_sequence,
                "length": len(long_sequence),
            }
        )
        + "\n",
        encoding="utf-8",
    )

    import sys

    argv_backup = sys.argv
    sys.argv = [
        "filter_lengths.py",
        str(long_input),
        str(long_output),
        "--rejected",
        str(rejected_path),
        "--stats",
        str(stats_path),
    ]
    try:
        filter_main()
    finally:
        sys.argv = argv_backup

    filtered = _read_jsonl(long_output)
    rejected = _read_jsonl(rejected_path)
    stats = json.loads(stats_path.read_text(encoding="utf-8"))

    assert filtered == []
    assert rejected[0]["reason"] == "too_long"
    assert stats["rejected_too_long"] == 1
