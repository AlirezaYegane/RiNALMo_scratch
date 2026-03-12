from __future__ import annotations

import pytest

from rinalmo.data.pretrain.dataset import JsonlPretrainDataset


def test_duplicate_sequence_id_across_shards_raises() -> None:
    ds = JsonlPretrainDataset("tests/fixtures/pretrain/manifest_dupe.jsonl")
    with pytest.raises(ValueError, match="duplicate sequence_id detected: dup_001"):
        list(ds.iter_records())


def test_invalid_json_raises_clear_error() -> None:
    ds = JsonlPretrainDataset("tests/fixtures/pretrain/manifest_bad_json.jsonl")
    with pytest.raises(ValueError, match="invalid json"):
        list(ds.iter_records())


def test_missing_shard_raises_clear_error() -> None:
    ds = JsonlPretrainDataset("tests/fixtures/pretrain/manifest_missing.jsonl")
    with pytest.raises(FileNotFoundError, match="manifest shard not found"):
        list(ds.iter_records())


def test_manifest_count_mismatch_raises() -> None:
    ds = JsonlPretrainDataset("tests/fixtures/pretrain/manifest_count_mismatch.jsonl")
    with pytest.raises(ValueError, match="record count mismatch"):
        list(ds.iter_records())
