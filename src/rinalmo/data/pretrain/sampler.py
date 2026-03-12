from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Hashable, Iterator, Sequence

from torch.utils.data import Sampler


class OnePerClusterPerEpochSampler(Sampler[int]):
    """
    Samples exactly one example per cluster in each epoch.
    If cluster_id is missing, falls back to singleton clusters per index.
    """

    def __init__(
        self,
        cluster_ids: Sequence[Hashable | None],
        *,
        shuffle: bool = True,
        seed: int = 42,
    ) -> None:
        self.shuffle = shuffle
        self.seed = seed
        self.epoch = 0

        groups: dict[str, list[int]] = defaultdict(list)
        for idx, cluster_id in enumerate(cluster_ids):
            key = f"singleton::{idx}" if cluster_id is None else str(cluster_id)
            groups[key].append(idx)

        self._groups = {k: tuple(v) for k, v in groups.items()}
        self._cluster_keys = tuple(sorted(self._groups.keys()))

        if not self._cluster_keys:
            raise ValueError("cluster_ids must not be empty")

    def set_epoch(self, epoch: int) -> None:
        self.epoch = int(epoch)

    def __len__(self) -> int:
        return len(self._cluster_keys)

    def __iter__(self) -> Iterator[int]:
        rng = random.Random(self.seed + self.epoch)

        cluster_keys = list(self._cluster_keys)
        if self.shuffle:
            rng.shuffle(cluster_keys)

        selected: list[int] = []
        for key in cluster_keys:
            members = self._groups[key]
            selected.append(members[rng.randrange(len(members))])

        return iter(selected)
