from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import torch

IGNORE_INDEX = -100


def _get_field(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item.get(name, default)
    return getattr(item, name, default)


@dataclass(frozen=True)
class PretrainBatch:
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    labels: torch.Tensor
    metadata: list[dict[str, Any]]


class MLMPretrainCollator:
    """
    Paper-aligned pretraining collator for RiNALMo.

    Expected per-item fields:
      - token_ids: list[int]
        or
      - sequence: str (if encode_fn is provided)
      - sequence_id: str | optional
      - source: str | optional
      - cluster_id: str | int | optional
    """

    def __init__(
        self,
        *,
        pad_token_id: int,
        cls_token_id: int,
        eos_token_id: int,
        mask_token_id: int,
        random_token_ids: Sequence[int],
        max_tokens: int = 1024,
        mask_prob: float = 0.15,
        ignore_index: int = IGNORE_INDEX,
        seed: int = 42,
        encode_fn: Callable[[str], list[int]] | None = None,
        pad_to_batch_max: bool = True,
    ) -> None:
        if max_tokens < 4:
            raise ValueError("max_tokens must be >= 4")
        if not 0.0 <= mask_prob <= 1.0:
            raise ValueError("mask_prob must be between 0 and 1")
        if not random_token_ids:
            raise ValueError("random_token_ids must not be empty")

        self.pad_token_id = pad_token_id
        self.cls_token_id = cls_token_id
        self.eos_token_id = eos_token_id
        self.mask_token_id = mask_token_id
        self.random_token_ids = list(random_token_ids)
        self.max_tokens = max_tokens
        self.mask_prob = mask_prob
        self.ignore_index = ignore_index
        self.encode_fn = encode_fn
        self.pad_to_batch_max = pad_to_batch_max
        self._rng = random.Random(seed)

    def __call__(self, items: Sequence[Any]) -> PretrainBatch:
        if not items:
            raise ValueError("empty batch is not allowed")

        processed: list[tuple[list[int], list[int], dict[str, Any]]] = []

        for item in items:
            token_ids = self._extract_token_ids(item)
            cropped_ids, crop_start, crop_end = self._crop_body(token_ids)

            input_ids = self._add_boundary_tokens(
                body_ids=cropped_ids,
                original_length=len(token_ids),
                crop_start=crop_start,
                crop_end=crop_end,
            )
            masked_input_ids, labels = self._apply_mlm(input_ids)

            metadata = {
                "sequence_id": _get_field(item, "sequence_id"),
                "source": _get_field(item, "source"),
                "cluster_id": _get_field(item, "cluster_id"),
                "original_length": len(token_ids),
                "crop_start": crop_start,
                "crop_end": crop_end,
                "final_length": len(masked_input_ids),
            }
            processed.append((masked_input_ids, labels, metadata))

        target_len = (
            max(len(input_ids) for input_ids, _, _ in processed)
            if self.pad_to_batch_max
            else self.max_tokens
        )

        batch_input_ids: list[list[int]] = []
        batch_attention_mask: list[list[int]] = []
        batch_labels: list[list[int]] = []
        batch_metadata: list[dict[str, Any]] = []

        for input_ids, labels, metadata in processed:
            if len(input_ids) > target_len:
                raise ValueError("input_ids length exceeds target_len during padding")

            pad_len = target_len - len(input_ids)

            batch_input_ids.append(input_ids + [self.pad_token_id] * pad_len)
            batch_attention_mask.append([1] * len(input_ids) + [0] * pad_len)
            batch_labels.append(labels + [self.ignore_index] * pad_len)
            batch_metadata.append(metadata)

        return PretrainBatch(
            input_ids=torch.tensor(batch_input_ids, dtype=torch.long),
            attention_mask=torch.tensor(batch_attention_mask, dtype=torch.long),
            labels=torch.tensor(batch_labels, dtype=torch.long),
            metadata=batch_metadata,
        )

    def _extract_token_ids(self, item: Any) -> list[int]:
        token_ids = _get_field(item, "token_ids")
        if token_ids is not None:
            return [int(x) for x in token_ids]

        sequence = _get_field(item, "sequence")
        if sequence is None:
            raise ValueError("each item must provide token_ids or sequence")

        if self.encode_fn is None:
            raise ValueError("encode_fn is required when batching raw sequence strings")

        encoded = self.encode_fn(str(sequence))
        return [int(x) for x in encoded]

    def _crop_body(self, token_ids: list[int]) -> tuple[list[int], int, int]:
        max_body_len = self.max_tokens - 2
        n = len(token_ids)

        if n <= max_body_len:
            return token_ids, 0, n

        start = self._rng.randint(0, n - max_body_len)
        end = start + max_body_len
        return token_ids[start:end], start, end

    def _add_boundary_tokens(
        self,
        *,
        body_ids: list[int],
        original_length: int,
        crop_start: int,
        crop_end: int,
    ) -> list[int]:
        out = list(body_ids)

        if crop_start == 0:
            out = [self.cls_token_id] + out
        if crop_end == original_length:
            out = out + [self.eos_token_id]

        if len(out) > self.max_tokens:
            raise ValueError(
                f"constructed sequence exceeds max_tokens: {len(out)} > {self.max_tokens}"
            )
        return out

    def _apply_mlm(self, input_ids: list[int]) -> tuple[list[int], list[int]]:
        special_ids = {self.pad_token_id, self.cls_token_id, self.eos_token_id}
        candidate_positions = [
            i for i, token_id in enumerate(input_ids) if token_id not in special_ids
        ]

        labels = [self.ignore_index] * len(input_ids)
        output_ids = list(input_ids)

        for pos in candidate_positions:
            if self._rng.random() >= self.mask_prob:
                continue

            original = output_ids[pos]
            labels[pos] = original

            draw = self._rng.random()
            if draw < 0.8:
                output_ids[pos] = self.mask_token_id
            elif draw < 0.9:
                output_ids[pos] = self._rng.choice(self.random_token_ids)
            else:
                output_ids[pos] = original

        return output_ids, labels


PretrainCollator = MLMPretrainCollator
