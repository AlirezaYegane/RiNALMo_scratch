from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ManifestEntry:
    shard_path: str
    num_records: int
    source: str


def load_manifest(path: str | Path) -> list[ManifestEntry]:
    manifest_path = Path(path)
    entries: list[ManifestEntry] = []

    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)
            entries.append(
                ManifestEntry(
                    shard_path=str(obj["shard_path"]),
                    num_records=int(obj["num_records"]),
                    source=str(obj["source"]),
                )
            )

    return entries
