"""Pitch 202X certification packet for trial-safe vendor credence runs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.verification.repo_internal.pitch_202x_surface_audit import (
    build_pitch_202x_surface_audit,
)
from hla.verification.repo_internal.spec2025_finish_line import _build_time_window_vendor_parity_audit


@dataclass(frozen=True)
class Pitch202xCertificationPaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


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


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _command_row(
    run: Mapping[str, Any],
    *,
    artifact_refs: list[str] | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(run["id"]),
        "label": str(run["label"]),
        "command": str(run["command"]),
        "exit_code": int(run["exit_code"]),
        "duration_seconds": round(float(run["duration_seconds"]), 3),
        "ok": int(run["exit_code"]) == 0,
        "artifact_refs": artifact_refs or [],
        "notes": notes,
    }


def _missing_run(run_id: str, label: str, command: str, note: str) -> dict[str, Any]:
    return {
        "id": run_id,
        "label": label,
        "command": command,
        "exit_code": 99,
        "duration_seconds": 0.0,
        "ok": False,
        "artifact_refs": [],
        "notes": note,
    }


def build_pitch_202x_certification_summary(
    *,
    project_root: Path,
    command_runs: list[Mapping[str, Any]],
) -> dict[str, Any]:
    surface_audit = build_pitch_202x_surface_audit(project_root)
    time_window_audit = _build_time_window_vendor_parity_audit()

    preflight_artifact = project_root / "analysis" / "preflight_artifacts" / "pitch-preflight.json"
    smoke_status_dir = project_root / "analysis" / "vendor_runtime_status" / "vendor_green_pitch_smoke"
    time_window_status_dir = project_root / "analysis" / "vendor_runtime_status" / "vendor_green_pitch_time_window_probe"
    restore_state_status_dir = (
        project_root / "analysis" / "vendor_runtime_status" / "vendor_green_pitch_time_window_restore_state_probe"
    )
    surface_md = project_root / "packages" / "hla-vendor-pitch" / "docs" / "evidence" / "pitch_202x_surface_audit_2026-06-23.md"
    surface_json = project_root / "packages" / "hla-vendor-pitch" / "docs" / "evidence" / "pitch_202x_surface_audit_2026-06-23.json"
    probe_md = project_root / "packages" / "hla-vendor-pitch" / "docs" / "evidence" / "pitch_202x_probe_2026-06-23.md"

    rows_by_id = {str(run["id"]): run for run in command_runs}
    preflight_run = rows_by_id.get("preflight")
    surface_run = rows_by_id.get("surface-audit")
    smoke_run = rows_by_id.get("smoke")
    time_window_run = rows_by_id.get("time-window-future-exclusion")
    restore_state_run = rows_by_id.get("time-window-restore-state")
    executed_runs = [
        _command_row(
            preflight_run or _missing_run("preflight", "preflight", "./tools/pitch preflight", "Preflight did not execute."),
            artifact_refs=[str(preflight_artifact.relative_to(project_root))],
            notes="Pitch runtime and Docker preflight gate for all real-runtime evidence.",
        ),
        _command_row(
            surface_run or _missing_run("surface-audit", "surface audit", "python3 scripts/report_pitch_202x_surface.py", "Surface audit did not execute."),
            artifact_refs=[
                str(surface_json.relative_to(project_root)),
                str(surface_md.relative_to(project_root)),
                str(probe_md.relative_to(project_root)),
            ],
            notes="Confirms the bundled jars expose a live vendor-specific 202X surface without overclaiming IEEE 2025 support.",
        ),
        _command_row(
            smoke_run or _missing_run("smoke", "smoke", "./tools/pitch smoke", "Smoke did not execute because an earlier gate failed."),
            artifact_refs=[
                str((smoke_status_dir / "vendor_runtime_status_summary.json").relative_to(project_root)),
                str((smoke_status_dir / "vendor_runtime_status_report.md").relative_to(project_root)),
            ],
            notes="Exercises the smallest promoted Pitch lifecycle and exchange smoke on the vendor runtime.",
        ),
        _command_row(
            time_window_run
            or _missing_run(
                "time-window-future-exclusion",
                "time window future exclusion",
                "./tools/pitch time-window-probe",
                "Future-exclusion probe did not execute because an earlier gate failed.",
            ),
            artifact_refs=[
                str((time_window_status_dir / "vendor_runtime_status_summary.json").relative_to(project_root)),
                str((time_window_status_dir / "vendor_runtime_status_report.md").relative_to(project_root)),
            ],
            notes="Trial-safe two-federate Target/Radar future-exclusion proof for vendor credence.",
        ),
        _command_row(
            restore_state_run
            or _missing_run(
                "time-window-restore-state",
                "time window restore state",
                "./tools/pitch time-window-restore-state-probe",
                "Restore-state probe did not execute because an earlier gate failed.",
            ),
            artifact_refs=[
                str((restore_state_status_dir / "vendor_runtime_status_summary.json").relative_to(project_root)),
                str((restore_state_status_dir / "vendor_runtime_status_report.md").relative_to(project_root)),
            ],
            notes="Trial-safe two-federate Target/Radar restore-state proof for vendor credence.",
        ),
    ]

    all_ok = all(row["ok"] for row in executed_runs)
    certification_state = "vendor-credence-candidate" if all_ok else "blocked-or-failed"

    scenario_allowlist = [
        {
            "scenario_id": "exchange-smoke",
            "trial_pitch_safe": True,
            "federate_count": 2,
            "vendor_test_selector": (
                "tests/vendors/test_real_vendor_runtime_smoke.py::"
                "pitch_java_real_exchange_smoke"
            ),
            "operator_route": "./tools/pitch smoke",
            "scenario_family": "target-radar-exchange",
            "notes": "Basic example FOM lifecycle plus object/interaction exchange under the promoted smoke lane.",
        },
        *[
            {
                "scenario_id": row["scenario_id"],
                "trial_pitch_safe": bool(row["trial_pitch_safe"]),
                "federate_count": int(row["federate_count"]),
                "vendor_test_selector": row.get("pitch_vendor_test"),
                "operator_route": row.get("recommended_pitch_operator_route"),
                "scenario_family": "target-radar-time-window",
                "notes": row["purpose"],
            }
            for row in time_window_audit["routes"]
            if bool(row["trial_pitch_safe"])
        ],
    ]

    known_boundaries = [
        {
            "area": "adapter-claim-boundary",
            "status": "not-2025-conformance",
            "summary": (
                "The checked-in pitch-202x backend routes still wrap the repo Python 2025 backend and do not count as "
                "real vendor-runtime evidence."
            ),
        },
        {
            "area": "negotiated-ownership",
            "status": "bridge-divergent",
            "summary": (
                "Negotiated ownership remains a documented bridge-divergent branch and is intentionally excluded from "
                "the 202x-certify promoted claim."
            ),
            "operator_route": "./tools/pitch negotiated-probe",
        },
        {
            "area": "time-window-restore-output",
            "status": "trial-unsafe",
            "summary": (
                "The restore-output Target/Radar proof needs three federates and is outside the current trial-safe "
                "Pitch route set."
            ),
            "operator_route": None,
        },
        {
            "area": "save-restore-ddm-lost-federate",
            "status": "known-gap",
            "summary": (
                "Save/restore, DDM, and lost-federate remain explicit Pitch gap/probe families and are not part of "
                "this 202X certification packet."
            ),
            "operator_routes": [
                "./tools/pitch save-restore-probe",
                "./tools/pitch ddm-probe",
                "./tools/pitch lost-federate-probe",
            ],
        },
    ]

    return {
        "suite_name": "pitch-202x-certification",
        "scope": (
            "Pitch vendor 202X surface plus trial-safe real-runtime vendor-credence packet; this is not an IEEE 1516-2025 "
            "conformance claim."
        ),
        "certification_state": certification_state,
        "project_root": str(project_root),
        "surface_audit": _jsonable(surface_audit),
        "time_window_vendor_parity_audit": _jsonable(time_window_audit),
        "executed_runs": executed_runs,
        "trial_safe_scenario_allowlist": scenario_allowlist,
        "known_boundaries": known_boundaries,
        "recommended_next_steps": (
            [
                "./tools/pitch time-window-review 5",
                "./tools/pitch time-window-restore-state-review 5",
                "./tools/pitch negotiated-probe",
            ]
            if all_ok
            else ["./tools/pitch preflight", "./tools/pitch doctor"]
        ),
    }


def _write_markdown(path: Path, summary: Mapping[str, Any]) -> Path:
    lines = [
        "# Pitch 202X Certification Packet",
        "",
        f"- certification state: `{summary['certification_state']}`",
        f"- scope: {summary['scope']}",
        f"- surface readiness: `{summary['surface_audit']['adapter_readiness']}`",
        f"- trial-safe route count: `{summary['time_window_vendor_parity_audit']['trial_pitch_safe_route_count']}`",
        "",
        "## Executed Runs",
        "",
        "| Run | Exit | Duration (s) | Command |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in summary["executed_runs"]:
        lines.append(
            f"| {row['label']} | {row['exit_code']} | {row['duration_seconds']} | `{row['command']}` |"
        )
    lines.extend(
        [
            "",
            "## Trial-Safe Scenario Allowlist",
            "",
            "| Scenario | Safe | Federates | Operator Route | Vendor Test |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in summary["trial_safe_scenario_allowlist"]:
        lines.append(
            f"| {row['scenario_id']} | {row['trial_pitch_safe']} | {row['federate_count']} | "
            f"{row['operator_route'] or ''} | {row['vendor_test_selector'] or ''} |"
        )
    lines.extend(["", "## Known Boundaries", ""])
    for row in summary["known_boundaries"]:
        lines.append(f"- `{row['area']}`: {row['summary']}")
    lines.extend(["", "## Next Steps", ""])
    for step in summary["recommended_next_steps"]:
        lines.append(f"- `{step}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_pitch_202x_certification(
    output_dir: Path | str,
    *,
    project_root: Path,
    command_runs: list[Mapping[str, Any]],
) -> Pitch202xCertificationPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = Pitch202xCertificationPaths(
        output_dir=output_path,
        summary_json=output_path / "pitch_202x_certification_summary.json",
        report_markdown=output_path / "pitch_202x_certification_report.md",
    )
    summary = build_pitch_202x_certification_summary(project_root=project_root, command_runs=command_runs)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(paths.report_markdown, summary)
    return paths


__all__ = [
    "Pitch202xCertificationPaths",
    "build_pitch_202x_certification_summary",
    "write_pitch_202x_certification",
]
