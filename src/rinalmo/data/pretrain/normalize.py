from __future__ import annotations

from dataclasses import dataclass
from typing import Final

MIN_SEQUENCE_LENGTH: Final[int] = 16
MAX_SEQUENCE_LENGTH: Final[int] = 8192
ALLOWED_SEQUENCE_ALPHABET: Final[frozenset[str]] = frozenset("ACGTIRYKMSWBDHVN-")


@dataclass(frozen=True)
class CanonicalizationResult:
    sequence: str
    length: int
    invalid_characters: tuple[str, ...]


def canonicalize_sequence(raw_sequence: str) -> str:
    """
    Canonicalize a raw RNA/DNA-like sequence for RiNALMo preprocessing.

    Rules:
    - strip all whitespace
    - uppercase
    - replace U with T
    """
    return "".join(raw_sequence.split()).upper().replace("U", "T")


def get_invalid_characters(sequence: str) -> tuple[str, ...]:
    invalid = {char for char in sequence if char not in ALLOWED_SEQUENCE_ALPHABET}
    return tuple(sorted(invalid))


def normalize_sequence(raw_sequence: str) -> CanonicalizationResult:
    sequence = canonicalize_sequence(raw_sequence)
    invalid_characters = get_invalid_characters(sequence)
    return CanonicalizationResult(
        sequence=sequence,
        length=len(sequence),
        invalid_characters=invalid_characters,
    )


def is_valid_length(
    length: int,
    *,
    min_len: int = MIN_SEQUENCE_LENGTH,
    max_len: int = MAX_SEQUENCE_LENGTH,
) -> bool:
    return min_len <= length <= max_len


def classify_length(
    length: int,
    *,
    min_len: int = MIN_SEQUENCE_LENGTH,
    max_len: int = MAX_SEQUENCE_LENGTH,
) -> str:
    if length < min_len:
        return "too_short"
    if length > max_len:
        return "too_long"
    return "ok"
