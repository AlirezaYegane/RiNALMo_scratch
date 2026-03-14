from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import lmdb

from .manifest import load_manifest
from .schema import PretrainRecord
from .validation import normalize_record


def _resolve_entry_path(manifest_path: Path, shard_path: str | Path) -> Path:
    raw = Path(shard_path)

    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append(raw)
        candidates.append(manifest_path.parent / raw)

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    if raw.is_absolute():
        return raw

    return (manifest_path.parent / raw).resolve()


class JsonlPretrainDataset:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)
        self.entries = load_manifest(self.manifest_path)

    def __len__(self) -> int:
        return sum(entry.num_records for entry in self.entries)

    def iter_records(self) -> Iterator[PretrainRecord]:
        seen_ids: set[str] = set()

        for entry in self.entries:
            shard = _resolve_entry_path(self.manifest_path, entry.shard_path)

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


class LmdbPretrainDataset:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)
        self.entries = load_manifest(self.manifest_path)

    def __len__(self) -> int:
        return sum(entry.num_records for entry in self.entries)

    def iter_records(self) -> Iterator[PretrainRecord]:
        seen_ids: set[str] = set()

        for entry in self.entries:
            lmdb_path = _resolve_entry_path(self.manifest_path, entry.shard_path)

            if not lmdb_path.exists():
                raise FileNotFoundError(f"manifest shard not found: {lmdb_path}")

            env = lmdb.open(
                str(lmdb_path),
                readonly=True,
                lock=False,
                readahead=False,
                max_readers=1,
                subdir=lmdb_path.is_dir(),
            )

            shard_count = 0
            try:
                with env.begin() as txn:
                    cursor = txn.cursor()
                    for key, value in cursor:
                        if key.startswith(b"__meta__/"):
                            continue

                        try:
                            text = value.decode("utf-8")
                        except UnicodeDecodeError as exc:
                            raise ValueError(
                                f"invalid utf-8 value in {lmdb_path} for key {key!r}"
                            ) from exc

                        try:
                            obj = json.loads(text)
                        except json.JSONDecodeError as exc:
                            raise ValueError(
                                f"invalid json in {lmdb_path} for key {key!r}: {exc.msg}"
                            ) from exc

                        record = normalize_record(obj)

                        if record.sequence_id in seen_ids:
                            raise ValueError(
                                f"duplicate sequence_id detected: {record.sequence_id} in {lmdb_path}"
                            )

                        seen_ids.add(record.sequence_id)
                        shard_count += 1
                        yield record
            finally:
                env.close()

            if shard_count != entry.num_records:
                raise ValueError(
                    f"record count mismatch for {lmdb_path}: manifest={entry.num_records}, actual={shard_count}"
                )
