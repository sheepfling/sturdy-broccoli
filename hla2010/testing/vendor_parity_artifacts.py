"""Vendor parity artifact manifest writer."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class VendorParityArtifactPaths:
    output_dir: Path
    summary_json: Path
    artifact_manifest_csv: Path
    report_markdown: Path


@dataclass(frozen=True)
class VendorParityArtifactRow:
    vendor_family: str
    profile: str
    artifact_kind: str
    role: str
    path: str
    required: bool
    exists: bool
    note: str


_ARTIFACT_SPECS: tuple[dict[str, Any], ...] = (
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "runtime smoke entrypoint",
        "path": "scripts/ci/vendor_runtime_smoke.sh",
        "required": True,
        "note": "Main real-runtime smoke/profile runner for CERTI and Pitch.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "edge matrix entrypoint",
        "path": "scripts/ci/vendor_edge_matrix.sh",
        "required": True,
        "note": "Highest-value vendor edge slice wrapper.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "test",
        "role": "smoke test",
        "path": "tests/vendors/test_real_vendor_runtime_smoke.py",
        "required": True,
        "note": "Backend-neutral real vendor runtime smoke anchor.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "doc",
        "role": "parity matrix",
        "path": "docs/backend_conformance_matrix.md",
        "required": True,
        "note": "Clause-level parity and vendor status summary.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "doc",
        "role": "runtime options matrix",
        "path": "docs/rti_options_and_test_matrix.md",
        "required": True,
        "note": "Supported vendor/runtime families and route inventory.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "preflight",
        "role": "preflight snapshot",
        "path": "analysis/preflight_artifacts/certi-preflight.json",
        "required": False,
        "note": "Optional machine-readable CERTI environment snapshot.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "preflight",
        "role": "preflight snapshot",
        "path": "analysis/preflight_artifacts/pitch-preflight.json",
        "required": False,
        "note": "Optional machine-readable Pitch environment snapshot.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "test",
        "role": "exchange parity",
        "path": "tests/vendors/test_certi_real_backend_exchange_matrix.py",
        "required": True,
        "note": "Real CERTI exchange scenario parity slice.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "test",
        "role": "time parity",
        "path": "tests/vendors/test_certi_real_backend_time_matrix.py",
        "required": True,
        "note": "Real CERTI time-management compare slice.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "test",
        "role": "ownership parity",
        "path": "tests/vendors/test_certi_real_backend_ownership_matrix.py",
        "required": True,
        "note": "Real CERTI ownership compare slice.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "support",
        "role": "shared matrix helpers",
        "path": "tests/vendors/certi_real_backend_matrix_support.py",
        "required": True,
        "note": "Shared CERTI runtime guards and helpers.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "doc",
        "role": "runbook",
        "path": "docs/certi_section8_runbook.md",
        "required": True,
        "note": "Operational runbook for CERTI compare workflows.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "doc",
        "role": "traceability note",
        "path": "docs/certi_spec_traceability.md",
        "required": True,
        "note": "Clause-level CERTI evidence and traceability context.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "doc",
        "role": "vendor findings",
        "path": "docs/certi_negotiated_ownership_findings.md",
        "required": True,
        "note": "Current negotiated ownership divergence notes for CERTI.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "test",
        "role": "exchange time ownership parity",
        "path": "tests/vendors/test_pitch_real_backend_matrix.py",
        "required": True,
        "note": "Real Pitch backend matrix across exchange, time, sync, and ownership slices.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "doc",
        "role": "quickstart",
        "path": "docs/pitch_docker_quickstart.md",
        "required": True,
        "note": "Shortest supported Pitch runtime activation path.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "doc",
        "role": "decision tree",
        "path": "docs/pitch_decision_tree.md",
        "required": True,
        "note": "Pitch operator decision tree and environment branching.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "doc",
        "role": "vendor findings",
        "path": "docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",
        "required": True,
        "note": "Current negotiated ownership divergence notes for Pitch.",
    },
)

_PROFILE_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "command": "./scripts/ci/vendor_runtime_smoke.sh certi-compare",
        "purpose": "Run the current upstream-vs-patched CERTI compare slice.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "command": "./scripts/ci/vendor_runtime_smoke.sh pitch",
        "purpose": "Run the current Pitch runtime smoke and matrix slice.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./scripts/ci/vendor_edge_matrix.sh all",
        "purpose": "Run the highest-value vendor edge packet refresh.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "python3 scripts/generate_compliance_artifacts.py",
        "purpose": "Refresh generated compliance matrices after a vendor run.",
    },
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return repr(value)


def _build_rows() -> tuple[VendorParityArtifactRow, ...]:
    rows: list[VendorParityArtifactRow] = []
    for spec in _ARTIFACT_SPECS:
        path = REPO_ROOT / spec["path"]
        rows.append(
            VendorParityArtifactRow(
                vendor_family=spec["vendor_family"],
                profile=spec["profile"],
                artifact_kind=spec["artifact_kind"],
                role=spec["role"],
                path=spec["path"],
                required=bool(spec["required"]),
                exists=path.exists(),
                note=spec["note"],
            )
        )
    return tuple(rows)


def _load_preflight_snapshot(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "tool": data.get("tool"),
        "result": data.get("result"),
        "environment": data.get("environment"),
        "exit_code": data.get("exit_code"),
    }


def _build_summary(rows: tuple[VendorParityArtifactRow, ...]) -> dict[str, Any]:
    profiles: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = f"{row.vendor_family}:{row.profile}"
        entry = profiles.setdefault(
            key,
            {
                "vendor_family": row.vendor_family,
                "profile": row.profile,
                "artifact_count": 0,
                "existing_count": 0,
                "missing_required_count": 0,
                "artifact_kinds": [],
            },
        )
        entry["artifact_count"] += 1
        if row.exists:
            entry["existing_count"] += 1
        if row.required and not row.exists:
            entry["missing_required_count"] += 1
        if row.artifact_kind not in entry["artifact_kinds"]:
            entry["artifact_kinds"].append(row.artifact_kind)

    preflight = {
        "certi": _load_preflight_snapshot(REPO_ROOT / "analysis" / "preflight_artifacts" / "certi-preflight.json"),
        "pitch": _load_preflight_snapshot(REPO_ROOT / "analysis" / "preflight_artifacts" / "pitch-preflight.json"),
    }
    required_count = sum(1 for row in rows if row.required)
    existing_count = sum(1 for row in rows if row.exists)
    missing_required_count = sum(1 for row in rows if row.required and not row.exists)
    return {
        "suite_name": "vendor-parity-artifacts",
        "profiles": list(profiles.values()),
        "artifact_count": len(rows),
        "required_count": required_count,
        "existing_count": existing_count,
        "missing_required_count": missing_required_count,
        "profile_commands": list(_PROFILE_COMMANDS),
        "preflight": preflight,
        "artifacts": [_jsonable(row) for row in rows],
    }


def _write_manifest_csv(path: Path, rows: tuple[VendorParityArtifactRow, ...]) -> Path:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "vendor_family",
                "profile",
                "artifact_kind",
                "role",
                "path",
                "required",
                "exists",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(_jsonable(row))
    return path


def _write_markdown(path: Path, summary: dict[str, Any], paths: VendorParityArtifactPaths) -> Path:
    lines = [
        "# Vendor Parity Artifacts",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- artifacts indexed: `{summary['artifact_count']}`",
        f"- required artifacts: `{summary['required_count']}`",
        f"- existing artifacts: `{summary['existing_count']}`",
        f"- missing required artifacts: `{summary['missing_required_count']}`",
        "",
        "## Profiles",
        "",
        "| Vendor | Profile | Indexed | Existing | Missing required | Kinds |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for profile in summary["profiles"]:
        kinds = ", ".join(profile["artifact_kinds"])
        lines.append(
            f"| {profile['vendor_family']} | {profile['profile']} | {profile['artifact_count']} | "
            f"{profile['existing_count']} | {profile['missing_required_count']} | {kinds} |"
        )
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for command in summary["profile_commands"]:
        lines.append(f"- `{command['command']}`")
        lines.append(f"  {command['purpose']}")
    lines.extend(
        [
            "",
            "## Preflight",
            "",
        ]
    )
    for vendor_family, snapshot in summary["preflight"].items():
        if snapshot is None:
            lines.append(f"- `{vendor_family}`: no JSON preflight snapshot is currently present")
        else:
            lines.append(
                f"- `{vendor_family}`: result `{snapshot.get('result')}`, environment `{snapshot.get('environment')}`, "
                f"exit `{snapshot.get('exit_code')}`, file `{snapshot.get('path')}`"
            )
    lines.extend(
        [
            "",
            "## Packet Files",
            "",
            f"- JSON summary: `{paths.summary_json.name}`",
            f"- Artifact manifest CSV: `{paths.artifact_manifest_csv.name}`",
            f"- Markdown report: `{paths.report_markdown.name}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
    return path


def write_vendor_parity_artifacts(output_dir: Path | str) -> VendorParityArtifactPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorParityArtifactPaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_parity_artifacts_summary.json",
        artifact_manifest_csv=output_path / "vendor_parity_artifacts_manifest.csv",
        report_markdown=output_path / "vendor_parity_artifacts_report.md",
    )
    rows = _build_rows()
    summary = _build_summary(rows)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_manifest_csv(paths.artifact_manifest_csv, rows)
    _write_markdown(paths.report_markdown, summary, paths)
    return paths


__all__ = [
    "VendorParityArtifactPaths",
    "VendorParityArtifactRow",
    "write_vendor_parity_artifacts",
]
