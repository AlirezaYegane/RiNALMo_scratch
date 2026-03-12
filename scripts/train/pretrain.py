from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RiNALMo pretraining entrypoint scaffold for phase 7 readiness."
    )
    parser.add_argument(
        "data_dir",
        nargs="?",
        default=None,
        help="Path to pretraining data directory or manifest root.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to pretraining manifest.jsonl file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./outputs/pretrain"),
        help="Directory for training artifacts.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=0,
        help="Maximum training steps for smoke or dry-run execution.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run CLI/config validation without launching a long training job.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    print("RiNALMo pretrain scaffold")
    print(f"data_dir={args.data_dir}")
    print(f"manifest={args.manifest}")
    print(f"output_dir={args.output_dir}")
    print(f"max_steps={args.max_steps}")
    print(f"seed={args.seed}")
    print(f"dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
