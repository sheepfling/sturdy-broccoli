"""Vendor runtime preflight status classification."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .path_rendering import jsonable as _portable_jsonable


REPO_ROOT = Path(__file__).resolve().parents[3]
BLOCKED_ENVIRONMENTS = frozenset(
    {
        "loopback-blocked",
        "docker-blocked",
        "bundle-blocked",
        "ports-blocked",
    }
)


@dataclass(frozen=True)
class VendorRuntimeStatusPaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


def _jsonable(value: Any) -> Any:
    return _portable_jsonable(value)


def _artifact_path(artifact_dir: Path, vendor: str) -> Path:
    return artifact_dir / f"{vendor}-preflight.json"


def _load_snapshot(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _extract_next_steps(snapshot: dict[str, Any] | None) -> list[str]:
    if snapshot is None:
        return []
    next_steps = snapshot.get("next_steps")
    if isinstance(next_steps, list):
        return [str(step) for step in next_steps if str(step).strip()]
    next_step = snapshot.get("next_step")
    if next_step is None:
        return []
    rendered = str(next_step).strip()
    return [rendered] if rendered else []


def _extract_blocked_checks(snapshot: dict[str, Any] | None) -> list[dict[str, Any]]:
    if snapshot is None:
        return []
    checks = snapshot.get("checks")
    if not isinstance(checks, list):
        return []
    blocked: list[dict[str, Any]] = []
    for item in checks:
        if not isinstance(item, dict):
            continue
        if bool(item.get("ok")):
            continue
        blocked.append(
            {
                "name": str(item.get("name", "unknown")),
                "status": None if item.get("status") is None else str(item.get("status")),
                "detail": None if item.get("detail") is None else str(item.get("detail")),
                "message": None if item.get("message") is None else str(item.get("message")),
            }
        )
    return blocked


def _extract_required_markers(snapshot: dict[str, Any] | None) -> dict[str, str]:
    if snapshot is None:
        return {}
    markers = snapshot.get("required_markers")
    if not isinstance(markers, dict):
        return {}
    return {
        str(name): str(value)
        for name, value in markers.items()
        if value is not None and str(value).strip()
    }


def _extract_required_ports(snapshot: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if snapshot is None:
        return {}
    ports = snapshot.get("ports")
    if not isinstance(ports, dict):
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for name, value in ports.items():
        if not isinstance(value, dict):
            continue
        rows[str(name)] = {
            "host": None if value.get("host") is None else str(value.get("host")),
            "port": value.get("port"),
            "status": None if value.get("status") is None else str(value.get("status")),
            "detail": None if value.get("detail") is None else str(value.get("detail")),
        }
    return rows


def _primary_blocked_check(blocked_checks: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not blocked_checks:
        return None
    return blocked_checks[0]


def _classify_vendor(vendor: str, snapshot: dict[str, Any] | None, lane: str, artifact_path: Path) -> dict[str, Any]:
    blocked_checks = _extract_blocked_checks(snapshot)
    required_markers = _extract_required_markers(snapshot)
    required_ports = _extract_required_ports(snapshot)
    next_steps = _extract_next_steps(snapshot)
    primary_blocked = _primary_blocked_check(blocked_checks)
    if snapshot is None:
        classification = "missing-artifact"
        actionable = False
        lane_ok = False
        note = "preflight artifact is missing or unreadable"
        environment = None
        result = None
        exit_code = None
        blocked_reason = "missing-artifact"
    else:
        environment = snapshot.get("environment")
        result = snapshot.get("result")
        exit_code = snapshot.get("exit_code")
        if exit_code == 0:
            classification = "ready"
            actionable = True
            lane_ok = True
            note = "vendor runtime prerequisites are ready"
            blocked_reason = None
        elif environment in BLOCKED_ENVIRONMENTS:
            classification = "environment-blocked"
            actionable = False
            lane_ok = lane == "repo-green"
            note = "host/runtime prerequisites are blocked on this surface"
            blocked_reason = None if primary_blocked is None else primary_blocked["name"]
        else:
            classification = "unexpected-preflight-failure"
            actionable = False
            lane_ok = False
            note = "preflight failed for a reason outside the expected blocked-environment set"
            blocked_reason = None if primary_blocked is None else primary_blocked["name"]

    return {
        "vendor": vendor,
        "artifact_path": _jsonable(artifact_path),
        "present": snapshot is not None,
        "tool": None if snapshot is None else snapshot.get("tool"),
        "environment": environment,
        "result": result,
        "exit_code": exit_code,
        "classification": classification,
        "actionable": actionable,
        "lane_ok": lane_ok,
        "blocked_reason": blocked_reason,
        "blocked_checks": blocked_checks,
        "required_markers": required_markers,
        "required_ports": required_ports,
        "next_steps": next_steps,
        "note": note,
    }


def build_vendor_runtime_status(
    *,
    artifact_dir: Path | str,
    lane: str = "repo-green",
    vendors: tuple[str, ...] = ("certi", "pitch"),
) -> dict[str, Any]:
    if lane not in {"repo-green", "vendor-green"}:
        raise ValueError(f"unsupported lane: {lane}")

    artifact_path = Path(artifact_dir)
    vendor_rows = []
    for vendor in vendors:
        if vendor not in {"certi", "pitch"}:
            raise ValueError(f"unsupported vendor: {vendor}")
        path = _artifact_path(artifact_path, vendor)
        vendor_rows.append(_classify_vendor(vendor, _load_snapshot(path), lane, path))

    overall_ok = all(bool(row["lane_ok"]) for row in vendor_rows)
    classifications = {str(row["classification"]) for row in vendor_rows}
    if overall_ok:
        overall_classification = lane
        exit_code = 0
    elif "environment-blocked" in classifications:
        overall_classification = "environment-blocked"
        exit_code = 1
    elif "missing-artifact" in classifications:
        overall_classification = "missing-artifact"
        exit_code = 1
    else:
        overall_classification = "unexpected-preflight-failure"
        exit_code = 1

    return {
        "suite_name": "vendor-runtime-status",
        "lane": lane,
        "artifact_dir": _jsonable(artifact_path),
        "vendors": [_jsonable(row) for row in vendor_rows],
        "overall_classification": overall_classification,
        "ready_vendors": [row["vendor"] for row in vendor_rows if row["classification"] == "ready"],
        "blocked_vendors": [row["vendor"] for row in vendor_rows if row["classification"] == "environment-blocked"],
        "missing_vendors": [row["vendor"] for row in vendor_rows if row["classification"] == "missing-artifact"],
        "unexpected_failure_vendors": [
            row["vendor"] for row in vendor_rows if row["classification"] == "unexpected-preflight-failure"
        ],
        "recommended_next_steps": {
            row["vendor"]: row["next_steps"] for row in vendor_rows if row["next_steps"]
        },
        "exit_code": exit_code,
    }


def _write_markdown(path: Path, summary: dict[str, Any]) -> Path:
    lines = [
        "# Vendor Runtime Status",
        "",
        f"- lane: `{summary['lane']}`",
        f"- overall classification: `{summary['overall_classification']}`",
        f"- exit code: `{summary['exit_code']}`",
        f"- artifact dir: `{summary['artifact_dir']}`",
        "",
        "## Vendors",
        "",
        "| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for vendor in summary["vendors"]:
        lines.append(
            f"| {vendor['vendor']} | {vendor['classification']} | {vendor['environment'] or ''} | "
            f"{'' if vendor['exit_code'] is None else vendor['exit_code']} | "
            f"{vendor['blocked_reason'] or ''} | {vendor['artifact_path']} | {vendor['note']} |"
        )
        if vendor["blocked_checks"]:
            lines.append("")
            lines.append(f"Blocked checks for `{vendor['vendor']}`:")
            for check in vendor["blocked_checks"]:
                detail = check["detail"] or check["message"] or "blocked"
                lines.append(f"- `{check['name']}`: {detail}")
        if vendor["required_markers"]:
            lines.append("")
            lines.append(f"Required markers for `{vendor['vendor']}`:")
            for name, marker in vendor["required_markers"].items():
                lines.append(f"- `{name}`: `{marker}`")
        if vendor["required_ports"]:
            lines.append("")
            lines.append(f"Required ports for `{vendor['vendor']}`:")
            for name, port in vendor["required_ports"].items():
                host = port["host"] or "unknown-host"
                number = "" if port["port"] is None else port["port"]
                status = f" [{port['status']}]" if port["status"] else ""
                lines.append(f"- `{name}`: `{host}:{number}`{status}")
        if vendor["next_steps"]:
            lines.append("")
            lines.append(f"Next steps for `{vendor['vendor']}`:")
            for step in vendor["next_steps"]:
                lines.append(f"- `{step}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_vendor_runtime_status(
    output_dir: Path | str,
    *,
    artifact_dir: Path | str,
    lane: str = "repo-green",
    vendors: tuple[str, ...] = ("certi", "pitch"),
) -> VendorRuntimeStatusPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorRuntimeStatusPaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_runtime_status_summary.json",
        report_markdown=output_path / "vendor_runtime_status_report.md",
    )
    summary = build_vendor_runtime_status(artifact_dir=artifact_dir, lane=lane, vendors=vendors)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(paths.report_markdown, summary)
    return paths


__all__ = [
    "BLOCKED_ENVIRONMENTS",
    "VendorRuntimeStatusPaths",
    "build_vendor_runtime_status",
    "write_vendor_runtime_status",
]
