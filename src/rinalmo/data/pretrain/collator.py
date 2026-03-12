from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .schema import PretrainRecord


@dataclass(slots=True)
class PretrainCollator:
    max_length: int = 1024
    pad_token_id: int = 0

    def __call__(self, batch: Iterable[PretrainRecord]) -> dict[str, list[str] | list[int]]:
        records = list(batch)
        sequences = [r.sequence[: self.max_length] for r in records]
        lengths = [len(s) for s in sequences]

        return {
            "sequence_id": [r.sequence_id for r in records],
            "sequence": sequences,
            "length": lengths,
            "source": [r.source for r in records],
            "cluster_id": [r.cluster_id or "" for r in records],
        }
