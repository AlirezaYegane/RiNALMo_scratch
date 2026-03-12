from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def sha256sum(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "generated_at": None, "sources": []}
    return json.loads(path.read_text())


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    manifest["generated_at"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def upsert_source(manifest: dict[str, Any], record: dict[str, Any]) -> None:
    sources = manifest.setdefault("sources", [])
    for idx, existing in enumerate(sources):
        if existing["source_name"] == record["source_name"]:
            sources[idx] = record
            return
    sources.append(record)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="e.g. rnacentral")
    parser.add_argument("--path", required=True, help="local file path")
    parser.add_argument("--kind", required=True, help="e.g. fasta_gz")
    parser.add_argument("--url", default="", help="upstream URL")
    parser.add_argument("--checksum", action="store_true", help="compute sha256")
    parser.add_argument(
        "--manifest",
        default="data/raw/manifest.json",
        help="manifest output path",
    )
    args = parser.parse_args()

    raw_path = str(args.path).strip()
    if not raw_path:
        raise ValueError("--path cannot be empty")

    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"raw source file not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"--path must point to a file, not a directory: {path}")

    stat = path.stat()
    record = {
        "source_name": args.source,
        "kind": args.kind,
        "local_path": str(path),
        "url": args.url,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
        "checksum_sha256": sha256sum(path) if args.checksum else "",
        "status": "registered",
    }

    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    upsert_source(manifest, record)
    save_manifest(manifest_path, manifest)

    print(f"registered source={args.source}")
    print(f"path={path}")
    print(f"size_bytes={stat.st_size}")
    if record["checksum_sha256"]:
        print(f"sha256={record['checksum_sha256']}")


if __name__ == "__main__":
    main()
