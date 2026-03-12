from __future__ import annotations

import argparse

from rinalmo.data.pretrain.dataset import JsonlPretrainDataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=str)
    parser.add_argument("--limit", type=int, default=1000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = JsonlPretrainDataset(args.manifest)

    checked = 0
    for _record in dataset.iter_records():
        checked += 1
        if checked >= args.limit:
            break

    print(f"manifest ok: checked={checked}, declared_total={len(dataset)}")


if __name__ == "__main__":
    main()
