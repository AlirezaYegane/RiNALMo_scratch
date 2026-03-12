from __future__ import annotations

from dataclasses import dataclass


class ValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PretrainRecord:
    sequence: str
    sequence_id: str
    source: str
    length: int
    cluster_id: str | None = None
