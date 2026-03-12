from __future__ import annotations

from runpy import run_module

from scripts._bootstrap import bootstrap_repo


def main() -> int:
    bootstrap_repo()
    run_module("scripts.train.train_splice_site_prediction", run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
