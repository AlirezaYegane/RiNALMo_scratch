from __future__ import annotations

from typing import Any

from .schema import PretrainRecord, ValidationError

RNA_ALPHABET = set("ACGUTN")
MIN_LEN = 16
MAX_LEN = 8192


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"field '{key}' must be a non-empty string")
    return value.strip()


def normalize_sequence(seq: str) -> str:
    seq = seq.strip().upper().replace(" ", "").replace("\n", "")
    seq = seq.replace("U", "T")
    return seq


def normalize_record(data: dict[str, Any]) -> PretrainRecord:
    sequence = normalize_sequence(_require_str(data, "sequence"))
    sequence_id = _require_str(data, "sequence_id")
    source = _require_str(data, "source")

    cluster_raw = data.get("cluster_id")
    if cluster_raw is not None and not isinstance(cluster_raw, str):
        raise ValidationError("field 'cluster_id' must be a string or null")
    cluster_id = cluster_raw.strip() if isinstance(cluster_raw, str) and cluster_raw.strip() else None

    length = data.get("length")
    if length is None:
        length = len(sequence)
    if not isinstance(length, int):
        raise ValidationError("field 'length' must be an integer")

    record = PretrainRecord(
        sequence=sequence,
        sequence_id=sequence_id,
        source=source,
        length=length,
        cluster_id=cluster_id,
    )
    validate_record(record)
    return record


def validate_record(record: PretrainRecord) -> None:
    if record.length != len(record.sequence):
        raise ValidationError(
            f"length mismatch for {record.sequence_id}: declared={record.length}, actual={len(record.sequence)}"
        )

    if not (MIN_LEN <= record.length <= MAX_LEN):
        raise ValidationError(
            f"sequence length out of range for {record.sequence_id}: {record.length} not in [{MIN_LEN}, {MAX_LEN}]"
        )

    invalid = sorted(set(record.sequence) - RNA_ALPHABET)
    if invalid:
        raise ValidationError(
            f"invalid alphabet for {record.sequence_id}: {''.join(invalid)}"
        )
