from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, cast

import hydra
import lightning.pytorch as pl
import torch
import torch.nn.functional as F
from hydra.utils import to_absolute_path
from lightning.pytorch import seed_everything
from omegaconf import DictConfig, OmegaConf
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader, Dataset

from rinalmo.data.alphabet import Alphabet
from rinalmo.data.pretrain import (
    IGNORE_INDEX,
    MLMPretrainCollator,
    OnePerClusterPerEpochSampler,
    PretrainBatch,
)
from rinalmo.data.pretrain.dataset import JsonlPretrainDataset
from rinalmo.model.model import RiNALMo
from rinalmo.runtime.checkpointing import save_run_metadata
from rinalmo.training.base import build_trainer, resolve_ckpt_path_for_fit


class ListPretrainDataset(Dataset):
    def __init__(self, records: list[Any]) -> None:
        self.records = records

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> Any:
        return self.records[index]


def encode_sequence_body(seq: str, alphabet: Alphabet) -> list[int]:
    normalized = seq.upper().replace("U", "T")
    return [alphabet.get_idx(ch) for ch in normalized]


def lr_lambda(
    step: int,
    *,
    warmup_steps: int,
    max_steps: int,
    min_lr_ratio: float,
) -> float:
    if step < warmup_steps:
        return float(step + 1) / float(max(1, warmup_steps))

    progress = (step - warmup_steps) / float(max(1, max_steps - warmup_steps))
    progress = min(progress, 1.0)
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return min_lr_ratio + (1.0 - min_lr_ratio) * cosine


class PretrainWrapper(pl.LightningModule):
    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.model = RiNALMo(cfg)

        hparams = OmegaConf.to_container(cfg, resolve=True)
        self.save_hyperparameters(hparams)

    def on_train_epoch_start(self) -> None:
        train_loader = self.trainer.train_dataloader
        sampler = getattr(train_loader, "sampler", None)
        set_epoch = getattr(sampler, "set_epoch", None)
        if callable(set_epoch):
            set_epoch(int(self.current_epoch))

    def transfer_batch_to_device(
        self,
        batch: Any,
        device: torch.device,
        dataloader_idx: int,
    ) -> Any:
        if isinstance(batch, PretrainBatch):
            return PretrainBatch(
                input_ids=batch.input_ids.to(device),
                attention_mask=batch.attention_mask.to(device),
                labels=batch.labels.to(device),
                metadata=batch.metadata,
            )
        return super().transfer_batch_to_device(batch, device, dataloader_idx)

    def training_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        del batch_idx

        outputs = self.model(batch.input_ids)
        logits = cast(torch.Tensor, outputs["logits"])
        labels = batch.labels

        masked_positions = labels.ne(IGNORE_INDEX)
        masked_count = int(masked_positions.sum().item())

        if masked_count == 0:
            loss = logits.sum() * 0.0
            masked_acc = torch.tensor(0.0, device=logits.device)
        else:
            loss = F.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                labels.reshape(-1),
                ignore_index=IGNORE_INDEX,
            )
            predictions = logits.argmax(dim=-1)
            masked_acc = predictions[masked_positions].eq(labels[masked_positions]).float().mean()

        ppl = torch.exp(loss.detach().clamp(max=20.0))

        self.log(
            "train/loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            batch_size=batch.input_ids.size(0),
        )
        self.log(
            "train/masked_acc",
            masked_acc,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            batch_size=batch.input_ids.size(0),
        )
        self.log(
            "train/ppl",
            ppl,
            on_step=True,
            on_epoch=True,
            batch_size=batch.input_ids.size(0),
        )
        self.log(
            "train/masked_tokens",
            float(masked_count),
            on_step=True,
            on_epoch=False,
            batch_size=batch.input_ids.size(0),
        )

        return cast(torch.Tensor, loss)

    def configure_optimizers(self) -> Any:
        lr = float(self.cfg.optimization.lr)
        min_lr = float(self.cfg.optimization.min_lr)
        warmup_steps = int(self.cfg.optimization.warmup_steps)
        weight_decay = float(self.cfg.optimization.weight_decay)
        max_steps = int(self.cfg.trainer.max_steps)

        optimizer = AdamW(self.parameters(), lr=lr, weight_decay=weight_decay)

        min_lr_ratio = 0.0 if lr <= 0 else (min_lr / lr)
        scheduler = LambdaLR(
            optimizer,
            lr_lambda=lambda step: lr_lambda(
                step,
                warmup_steps=warmup_steps,
                max_steps=max_steps,
                min_lr_ratio=min_lr_ratio,
            ),
        )

        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "step",
                "frequency": 1,
            },
        }


def build_train_loader(cfg: DictConfig, alphabet: Alphabet) -> tuple[DataLoader, dict[str, Any]]:
    if bool(cfg.data.use_lmdb):
        raise NotImplementedError(
            "LMDB pretrain dataset is not wired in subphase 2.6 smoke; set data.use_lmdb=false."
        )

    manifest_path = Path(to_absolute_path(str(cfg.data.manifest_path)))
    dataset = JsonlPretrainDataset(manifest_path)
    records = list(dataset.iter_records())

    if not records:
        raise ValueError(f"no pretrain records found in manifest: {manifest_path}")

    record_dataset = ListPretrainDataset(records)

    cluster_ids = [getattr(record, "cluster_id", None) for record in records]
    sampler = OnePerClusterPerEpochSampler(
        cluster_ids,
        shuffle=True,
        seed=int(cfg.seed),
    )

    random_token_ids = [alphabet.get_idx(token) for token in alphabet.standard_tkns]

    collator = MLMPretrainCollator(
        pad_token_id=alphabet.pad_idx,
        cls_token_id=alphabet.cls_idx,
        eos_token_id=alphabet.eos_idx,
        mask_token_id=alphabet.mask_idx,
        random_token_ids=random_token_ids,
        max_tokens=int(cfg.data.max_tokens),
        mask_prob=float(cfg.model.token_dropout.mask_ratio),
        seed=int(cfg.seed),
        encode_fn=lambda seq: encode_sequence_body(seq, alphabet),
        pad_to_batch_max=True,
    )

    loader = DataLoader(
        record_dataset,
        batch_size=int(cfg.data.batch_size),
        sampler=sampler,
        num_workers=int(cfg.data.num_workers),
        pin_memory=bool(cfg.data.pin_memory),
        persistent_workers=bool(cfg.data.persistent_workers) and int(cfg.data.num_workers) > 0,
        drop_last=bool(cfg.data.drop_last),
        collate_fn=collator,
    )

    summary = {
        "manifest_path": str(manifest_path),
        "num_records": len(records),
        "num_clusters": len(sampler),
        "batch_size": int(cfg.data.batch_size),
        "max_tokens": int(cfg.data.max_tokens),
    }
    return loader, summary


def patch_model_config_with_alphabet(cfg: DictConfig, alphabet: Alphabet) -> None:
    cfg.model.embedding.num_embeddings = len(alphabet)
    cfg.model.embedding.padding_idx = alphabet.pad_idx

    cfg.model.lm_mask_head.alphabet_size = len(alphabet)

    cfg.model.token_dropout.mask_tkn_idx = alphabet.mask_idx
    cfg.model.token_dropout.pad_tkn_idx = alphabet.pad_idx


def save_run_summary(output_dir: Path, summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "run_summary.json"
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


@hydra.main(version_base=None, config_path="../../configs", config_name="pretrain")
def main(cfg: DictConfig) -> None:
    seed_everything(int(cfg.seed), workers=True)

    cfg.paths.output_dir = to_absolute_path(str(cfg.paths.output_dir))

    alphabet = Alphabet()
    patch_model_config_with_alphabet(cfg, alphabet)

    train_loader, data_summary = build_train_loader(cfg, alphabet)

    model = PretrainWrapper(cfg)
    trainer = build_trainer(cfg)
    ckpt_path = resolve_ckpt_path_for_fit(cfg)

    trainer.fit(model, train_dataloaders=train_loader, ckpt_path=ckpt_path)

    summary = {
        "run_name": str(cfg.run.name),
        "output_dir": str(cfg.paths.output_dir),
        "vocab_size": len(alphabet),
        "pad_idx": alphabet.pad_idx,
        "mask_idx": alphabet.mask_idx,
        "optimizer": "AdamW",
        "lr": float(cfg.optimization.lr),
        "min_lr": float(cfg.optimization.min_lr),
        "warmup_steps": int(cfg.optimization.warmup_steps),
        "max_steps": int(cfg.trainer.max_steps),
        "model_embed_dim": int(cfg.model.embedding.embedding_dim),
        "model_num_blocks": int(cfg.model.transformer.num_blocks),
        **data_summary,
    }

    checkpoint_callback = getattr(trainer, "checkpoint_callback", None)
    if checkpoint_callback is not None:
        summary["best_model_path"] = str(checkpoint_callback.best_model_path)

    output_dir = Path(str(cfg.paths.output_dir))
    save_run_summary(output_dir, summary)
    save_run_metadata(output_dir, extra={"stage": "subphase2_6_pretrain"})


if __name__ == "__main__":
    main()
