from __future__ import annotations

from rinalmo.data.pretrain.sampler import OnePerClusterPerEpochSampler


def test_sampler_returns_one_index_per_cluster() -> None:
    sampler = OnePerClusterPerEpochSampler(
        ["a", "a", "b", "b", "c"],
        shuffle=False,
        seed=42,
    )

    indices = list(iter(sampler))
    assert len(indices) == 3

    chosen = set(indices)
    assert len(chosen & {0, 1}) == 1
    assert len(chosen & {2, 3}) == 1
    assert len(chosen & {4}) == 1


def test_sampler_changes_selection_across_epochs() -> None:
    sampler = OnePerClusterPerEpochSampler(
        ["a", "a", "b", "b", "c", "c"],
        shuffle=False,
        seed=123,
    )

    sampler.set_epoch(0)
    epoch0 = list(iter(sampler))

    sampler.set_epoch(1)
    epoch1 = list(iter(sampler))

    assert len(epoch0) == len(epoch1) == 3
    assert epoch0 != epoch1


def test_sampler_falls_back_to_singletons_when_cluster_id_missing() -> None:
    sampler = OnePerClusterPerEpochSampler(
        [None, None, "x"],
        shuffle=False,
        seed=42,
    )

    indices = list(iter(sampler))
    assert len(indices) == 3
    assert sorted(indices) == [0, 1, 2]
