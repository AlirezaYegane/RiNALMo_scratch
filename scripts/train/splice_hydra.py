from __future__ import annotations

import shlex

from scripts._bootstrap import bootstrap_repo

bootstrap_repo()

import hydra
from omegaconf import DictConfig, OmegaConf

from rinalmo.hydra_bridge.legacy_cli import build_argv, run_legacy_entrypoint


@hydra.main(version_base=None, config_path="../../configs", config_name="config")
def main(cfg: DictConfig) -> None:
    if cfg.name != "splice":
        raise ValueError(f"Expected task=splice, got: {cfg.name}")

    argv = build_argv(cfg)

    print("entrypoint:", cfg.legacy.entrypoint)
    print("argv:", " ".join(shlex.quote(x) for x in argv))
    print("dry_run:", cfg.dry_run)
    print("resolved_config:")
    print(OmegaConf.to_yaml(cfg, resolve=True))

    if cfg.dry_run:
        return

    run_legacy_entrypoint(cfg.legacy.entrypoint, argv)


if __name__ == "__main__":
    main()
