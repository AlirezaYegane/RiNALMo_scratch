from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from .manifest import load_manifest
from .schema import PretrainRecord
from .validation import normalize_record


class JsonlPretrainDataset:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)
        self.entries = load_manifest(self.manifest_path)

    def __len__(self) -> int:
        return sum(entry.num_records for entry in self.entries)

    def iter_records(self) -> Iterator[PretrainRecord]:
        base_dir = self.manifest_path.parent
        seen_ids: set[str] = set()

        for entry in self.entries:
            shard = Path(entry.shard_path)
            if not shard.is_absolute():
                shard = base_dir / shard

            if not shard.exists():
                raise FileNotFoundError(f"manifest shard not found: {shard}")

            shard_count = 0

            with shard.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"invalid json in {shard}:{line_no}: {exc.msg}"
                        ) from exc

                    record = normalize_record(obj)

                    if record.sequence_id in seen_ids:
                        raise ValueError(
                            f"duplicate sequence_id detected: {record.sequence_id} in {shard}:{line_no}"
                        )

                    seen_ids.add(record.sequence_id)
                    shard_count += 1
                    yield record

            if shard_count != entry.num_records:
                raise ValueError(
                    f"record count mismatch for {shard}: manifest={entry.num_records}, actual={shard_count}"
                )
