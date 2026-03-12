from __future__ import annotations

from omegaconf import OmegaConf

from rinalmo.training.base import resolve_ckpt_path_for_fit


def test_resolve_ckpt_none():
    cfg = OmegaConf.create(
        {
            "paths": {"output_dir": "./outputs/test"},
            "trainer": {"resume": None},
        }
    )
    assert resolve_ckpt_path_for_fit(cfg) is None
