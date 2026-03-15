from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
from typing import Any

REPO_ROOT = Path.cwd()
OUT_DIR = REPO_ROOT / "outputs" / "readiness"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_AUDIT_DOC = REPO_ROOT / "docs" / "engineering" / "prebooking_data_audit.md"
CANONICAL_SUMMARY = REPO_ROOT / "outputs" / "data_audit" / "canonical_raw_summary.json"
READINESS_REPORT = REPO_ROOT / "outputs" / "readiness" / "h200_readiness_report.json"
BOOKING_EVIDENCE = REPO_ROOT / "outputs" / "readiness" / "booking_evidence.txt"

SEARCH_ROOTS = [
    Path("/Datasets"),
    Path("/mnt"),
    Path("/srv"),
    Path("/opt"),
    Path.home() / "downloads",
    REPO_ROOT / "downloads",
]

def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def precise_find(max_depth: int = 8) -> dict[str, list[str]]:
    matches = {"nt": [], "ensembl": []}
    nt_patterns = ["nt", "nt.*", "*blast*nt*"]
    ensembl_patterns = ["*ensembl*", "*release-109*", "*release109*"]

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        root_depth = len(root.parts)
        for cur_root, dirnames, filenames in os.walk(root):
            cur_path = Path(cur_root)
            if len(cur_path.parts) - root_depth >= max_depth:
                dirnames[:] = []
            for name in filenames:
                full = str(cur_path / name)
                lower = name.lower()
                if any(fnmatch.fnmatch(lower, p.lower()) for p in nt_patterns):
                    matches["nt"].append(full)
                if any(fnmatch.fnmatch(lower, p.lower()) for p in ensembl_patterns):
                    matches["ensembl"].append(full)

    matches["nt"] = sorted(set(matches["nt"]))[:200]
    matches["ensembl"] = sorted(set(matches["ensembl"]))[:200]
    return matches

canonical = load_json(CANONICAL_SUMMARY)
readiness = load_json(READINESS_REPORT)
matches = precise_find()

canonical_present = False
canonical_total = None
if canonical is not None:
    srcs = canonical.get("sources", {})
    canonical_present = bool(
        srcs.get("RNAcentral", {}).get("exists")
        and srcs.get("Rfam", {}).get("exists")
    )
    canonical_total = canonical.get("total_canonical_raw")

readiness_pass = bool(readiness and readiness.get("all_ok") is True)
booking_present = BOOKING_EVIDENCE.exists()

data_doc_present = DATA_AUDIT_DOC.exists()
nt_found = len(matches["nt"]) > 0
ensembl_found = len(matches["ensembl"]) > 0

data_gate_status = "PASS" if (
    canonical_present and nt_found and ensembl_found and data_doc_present
) else "PARTIAL/BLOCKED"
readiness_gate_status = "PASS" if readiness_pass else "BLOCKED"
booking_gate_status = "PASS" if booking_present else "BLOCKED"

overall_pass = (
    data_gate_status == "PASS"
    and readiness_gate_status == "PASS"
    and booking_gate_status == "PASS"
)

reasons: list[str] = []
if not data_doc_present:
    reasons.append("prebooking_data_audit.md missing")
if not canonical_present:
    reasons.append("canonical RNAcentral/Rfam raw sources not fully present")
if not nt_found:
    reasons.append("nt not found in precise inventory search")
if not ensembl_found:
    reasons.append("Ensembl release-109 ncRNA not found in precise inventory search")
if not readiness_pass:
    reasons.append("h200_readiness_report.json missing or all_ok != true")
if not booking_present:
    reasons.append("booking evidence file missing")

report = {
    "status": "PASS" if overall_pass else "BLOCKED",
    "data_gate": {
        "status": data_gate_status,
        "data_audit_doc_present": data_doc_present,
        "canonical_summary_present": canonical is not None,
        "canonical_raw_present": canonical_present,
        "canonical_raw_total": canonical_total,
        "nt_matches": matches["nt"],
        "ensembl_matches": matches["ensembl"],
    },
    "readiness_gate": {
        "status": readiness_gate_status,
        "readiness_report_present": readiness is not None,
        "all_ok": readiness.get("all_ok") if readiness else None,
    },
    "booking_gate": {
        "status": booking_gate_status,
        "booking_evidence_present": booking_present,
        "booking_evidence_path": str(BOOKING_EVIDENCE),
    },
    "reasons_blocked": reasons,
}

out_path = OUT_DIR / "prebooking_gate_report.json"
out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
