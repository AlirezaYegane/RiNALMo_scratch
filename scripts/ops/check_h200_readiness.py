from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Ensure repo root is importable even when this file is executed directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts._bootstrap import bootstrap_repo

repo_root = Path(bootstrap_repo())

try:
    from hydra import compose, initialize_config_dir
    from omegaconf import OmegaConf
except Exception as exc:  # pragma: no cover
    print(f"[FATAL] hydra/omegaconf import failed: {exc}", file=sys.stderr)
    raise


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def run_cmd(cmd: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, f"command not found: {cmd[0]}"

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    detail = out if out else err
    return proc.returncode == 0, detail


def check_exists(path: Path, kind: str = "file") -> CheckResult:
    ok = path.exists()
    if kind == "dir":
        ok = ok and path.is_dir()
    elif kind == "file":
        ok = ok and path.is_file()

    try:
        label = str(path.relative_to(repo_root))
    except ValueError:
        label = str(path)

    return CheckResult(
        name=f"exists:{label}",
        ok=ok,
        detail="ok" if ok else f"missing {kind}: {path}",
    )


def check_writable_dir(path: Path) -> CheckResult:
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".write_probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        try:
            label = str(path.relative_to(repo_root))
        except ValueError:
            label = str(path)
        return CheckResult(
            name=f"writable:{label}",
            ok=True,
            detail="ok",
        )
    except Exception as exc:
        try:
            label = str(path.relative_to(repo_root))
        except ValueError:
            label = str(path)
        return CheckResult(
            name=f"writable:{label}",
            ok=False,
            detail=str(exc),
        )


def parse_manifest(manifest_path: Path) -> CheckResult:
    try:
        total_lines = 0
        total_records = 0
        first_entry: dict[str, Any] | None = None

        with manifest_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_lines += 1
                obj = json.loads(line)
                total_records += int(obj["num_records"])
                if first_entry is None:
                    first_entry = obj

        if total_lines == 0:
            return CheckResult("manifest:parse", False, "manifest is empty")

        return CheckResult(
            "manifest:parse",
            True,
            f"entries={total_lines}, total_records={total_records}, first={first_entry}",
        )
    except Exception as exc:
        return CheckResult("manifest:parse", False, str(exc))


def check_gpu() -> CheckResult:
    ok, detail = run_cmd(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"]
    )
    if not ok:
        return CheckResult("gpu:nvidia-smi", False, detail)

    names = [line.strip() for line in detail.splitlines() if line.strip()]
    has_h200 = any("H200" in line for line in names)
    return CheckResult(
        "gpu:h200_visible",
        has_h200,
        " | ".join(names) if names else "no GPUs listed",
    )


def check_disk(path: Path) -> CheckResult:
    usage = shutil.disk_usage(path)
    free_gb = usage.free / (1024 ** 3)
    ok = free_gb >= 50.0
    return CheckResult(
        "disk:repo_root_free_space",
        ok,
        f"free_gb={free_gb:.2f}",
    )


def compose_config(output_dir: Path) -> CheckResult:
    config_dir = repo_root / "configs"
    try:
        with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
            cfg = compose(
                config_name="pretrain",
                overrides=[
                    "experiment=pretrain_dryrun",
                    "runtime=h200_single",
                    "data=pretrain_lmdb",
                    "train@_global_=pretrain_dryrun",
                ],
            )

        resolved_path = output_dir / "resolved_pretrain_config.yaml"
        resolved_path.write_text(OmegaConf.to_yaml(cfg, resolve=True), encoding="utf-8")

        return CheckResult(
            "hydra:compose",
            True,
            f"resolved config written to {resolved_path}",
        )
    except Exception as exc:
        return CheckResult("hydra:compose", False, str(exc))


def build_launch_command() -> str:
    py = sys.executable
    return (
        f'PYTHONPATH=$PWD/src "{py}" scripts/train/pretrain.py '
        "experiment=pretrain_dryrun runtime=h200_single "
        "data=pretrain_lmdb train@_global_=pretrain_dryrun"
    )


def main() -> int:
    output_dir = repo_root / "outputs" / "readiness"
    output_dir.mkdir(parents=True, exist_ok=True)

    required_paths: list[tuple[Path, str]] = [
        (repo_root / "scripts" / "train" / "pretrain.py", "file"),
        (repo_root / "configs" / "pretrain.yaml", "file"),
        (repo_root / "configs" / "runtime" / "h200_single.yaml", "file"),
        (repo_root / "configs" / "data" / "pretrain_lmdb.yaml", "file"),
        (repo_root / "configs" / "experiment" / "pretrain_dryrun.yaml", "file"),
        (repo_root / "configs" / "train" / "pretrain_dryrun.yaml", "file"),
        (repo_root / "data" / "pretrain" / "manifest.jsonl", "file"),
        (repo_root / "data" / "pretrain" / "records.lmdb", "dir"),
        (repo_root / "scripts" / "ops" / "preflight_h200.sh", "file"),
    ]

    results: list[CheckResult] = []
    for path, kind in required_paths:
        results.append(check_exists(path, kind=kind))

    results.append(check_writable_dir(output_dir))
    results.append(check_disk(repo_root))
    results.append(check_gpu())

    manifest_path = repo_root / "data" / "pretrain" / "manifest.jsonl"
    if manifest_path.exists():
        results.append(parse_manifest(manifest_path))
    else:
        results.append(CheckResult("manifest:parse", False, f"missing file: {manifest_path}"))

    results.append(compose_config(output_dir))

    report = {
        "repo_root": str(repo_root),
        "python": sys.executable,
        "launch_command_candidate": build_launch_command(),
        "checks": [asdict(r) for r in results],
    }
    report["all_ok"] = all(r.ok for r in results)

    report_path = output_dir / "h200_readiness_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
