from __future__ import annotations

import importlib

MODULES = [
    "scripts._bootstrap",
    "scripts.train.pretrain",
    "scripts.train.train_sec_struct_prediction",
    "scripts.train.train_splice_site_prediction",
    "scripts.train.train_ribosome_loading",
    "scripts.train.train_translation_efficiency",
    "scripts.train.train_expression_level",
    "train_sec_struct_prediction",
    "train_splice_site_prediction",
    "train_ribosome_loading",
    "train_translation_efficiency",
    "train_expression_level",
]


def test_entrypoint_modules_import() -> None:
    for name in MODULES:
        mod = importlib.import_module(name)
        assert mod is not None, f"failed importing {name}"
