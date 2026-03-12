from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    manifest_path = Path("data/raw/manifest.json")
    if not manifest_path.exists():
        raise FileNotFoundError("data/raw/manifest.json not found")

    manifest = json.loads(manifest_path.read_text())
    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("manifest.sources must be a list")

    if not sources:
        raise ValueError("raw manifest has no registered sources")

    print(f"manifest version: {manifest.get('version')}")
    print(f"generated_at: {manifest.get('generated_at')}")
    print(f"num_sources: {len(sources)}")

    for rec in sources:
        required = ["source_name", "kind", "local_path", "size_bytes", "status"]
        for key in required:
            if key not in rec:
                raise ValueError(f"missing key in manifest record: {key}")

        p = Path(rec["local_path"])
        exists = p.exists()
        size_ok = exists and p.stat().st_size == rec["size_bytes"]

        print(
            f"- {rec['source_name']}: "
            f"exists={exists} size_match={size_ok} kind={rec['kind']}"
        )

        if not exists:
            raise FileNotFoundError(f"registered path missing: {p}")
        if not size_ok:
            raise ValueError(f"registered size mismatch for: {p}")

    print("raw manifest integrity: OK")


if __name__ == "__main__":
    main()
