from __future__ import annotations

from rinalmo.data.pretrain.collator import IGNORE_INDEX, MLMPretrainCollator


def test_masking_skips_special_tokens_and_masks_about_15_percent() -> None:
    collator = MLMPretrainCollator(
        pad_token_id=0,
        cls_token_id=101,
        eos_token_id=102,
        mask_token_id=103,
        random_token_ids=[10, 11, 12, 13],
        max_tokens=2000,
        mask_prob=0.15,
        seed=7,
    )

    batch = collator(
        [
            {
                "token_ids": [10] * 1000,
                "sequence_id": "seq_001",
                "source": "fixture",
                "cluster_id": "c1",
            }
        ]
    )

    input_ids = batch.input_ids[0].tolist()
    labels = batch.labels[0].tolist()

    assert input_ids[0] == 101
    assert input_ids[-1] == 102
    assert labels[0] == IGNORE_INDEX
    assert labels[-1] == IGNORE_INDEX

    num_masked = sum(1 for x in labels if x != IGNORE_INDEX)
    assert 120 <= num_masked <= 180


def test_middle_crop_omits_missing_side_special_tokens() -> None:
    collator = MLMPretrainCollator(
        pad_token_id=0,
        cls_token_id=101,
        eos_token_id=102,
        mask_token_id=103,
        random_token_ids=[10, 11, 12, 13],
        max_tokens=1024,
        mask_prob=0.0,
        seed=42,
    )

    batch = collator(
        [
            {
                "token_ids": list(range(2000, 4000)),
                "sequence_id": "long_seq",
                "source": "fixture",
                "cluster_id": "c2",
            }
        ]
    )

    meta = batch.metadata[0]
    assert meta["crop_start"] > 0
    assert meta["crop_end"] < meta["original_length"]

    ids = batch.input_ids[0].tolist()
    # single-item batch -> no extra pad expected here
    assert len(ids) == 1022
    assert ids[0] != 101
    assert ids[-1] != 102


def test_full_short_sequence_gets_cls_and_eos() -> None:
    collator = MLMPretrainCollator(
        pad_token_id=0,
        cls_token_id=101,
        eos_token_id=102,
        mask_token_id=103,
        random_token_ids=[10, 11, 12, 13],
        max_tokens=1024,
        mask_prob=0.0,
        seed=1,
    )

    batch = collator(
        [
            {
                "token_ids": [10, 11, 12, 13],
                "sequence_id": "short_seq",
                "source": "fixture",
                "cluster_id": "c3",
            }
        ]
    )

    ids = batch.input_ids[0].tolist()
    assert ids == [101, 10, 11, 12, 13, 102]
