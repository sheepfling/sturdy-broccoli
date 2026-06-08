"""Backend compliance discovery helpers.

This module turns the generated compliance packet into compact operator-facing
catalogs so backend parity and the next missing vendor work can be discovered
without manually opening multiple matrices.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_BACKLOG_PRIORITY_RULES: tuple[tuple[str, int, str], ...] = (
    ("vendor-divergent", 1, "investigate or isolate with focused vendor test"),
    ("env-gated-positive", 2, "rerun or stabilize environment/preflight"),
    ("not-yet-matrixed", 3, "add focused vendor matrix/probe"),
    ("bridge-parity-positive", 4, "promote bridge-parity row into dedicated vendor matrix/probe"),
    ("positive-path-passing", 5, "widen from positive-path slice into deeper vendor matrix coverage"),
    ("defended-partial", 6, "leave defended or split into narrower vendor row"),
)
_BACKLOG_PRIORITY_BY_STATUS = {status: (rank, action) for status, rank, action in _BACKLOG_PRIORITY_RULES}
_BACKLOG_PRIORITIES = tuple(status for status, _rank, _action in _BACKLOG_PRIORITY_RULES)
_BACKLOG_PRIORITY_LABELS = {
    1: "P1",
    2: "P2",
    3: "P3",
    4: "P4",
    5: "P5",
    6: "P6",
}
_BACKLOG_INCLUDED_MATRIX_STATUSES = frozenset(
    {"vendor-divergent", "env-gated-positive", "not-yet-matrixed", "bridge-parity-positive", "positive-path-passing"}
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _compliance_dir(project_root: str | Path | None = None) -> Path:
    root = Path(project_root) if project_root is not None else _repo_root()
    return root / "analysis" / "compliance"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_markdown(path: Path, lines: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _sorted_counts(values: dict[str, int]) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda item: (-item[1], item[0])))


def _section_root(section_ref: str) -> str:
    match = re.search(r"§\s*(\d+)", str(section_ref or ""))
    return match.group(1) if match else ""


def _section_sort_key(section_ref: str) -> tuple[int, str]:
    root = _section_root(section_ref)
    return (int(root) if root.isdigit() else 999, str(section_ref))


def _matches_backend_filter(row: dict[str, Any], backend_filter: str | None) -> bool:
    if not backend_filter:
        return True
    return backend_filter in {str(row.get("backend_id", "")), str(row.get("backend_family", ""))}


def _matches_section_filter(row: dict[str, Any], section_filter: str | None) -> bool:
    if not section_filter:
        return True
    candidates = {
        str(row.get("section_root", "")),
        str(row.get("section_ref", "")),
        str(row.get("requirement_id", "")),
    }
    return section_filter in candidates


def _matches_priority_filter(row: dict[str, Any], priority_filter: str | None) -> bool:
    if not priority_filter:
        return True
    return priority_filter in {str(row.get("priority", "")), str(row.get("current_status", ""))}


def _sort_backlog_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            int(row["priority_rank"]),
            _section_sort_key(str(row.get("section_ref", ""))),
            str(row.get("backend_id", "")),
            str(row.get("requirement_id", "")),
            str(row.get("slice_or_method", "")),
        ),
    )


def build_backend_compliance_catalog(project_root: str | Path | None = None) -> dict[str, Any]:
    compliance_dir = _compliance_dir(project_root)
    core_path = compliance_dir / "core_backend_matrix.json"
    section8_path = compliance_dir / "section8_backend_matrix.json"
    pitch_path = compliance_dir / "pitch_backend_matrix.json"
    requirements_path = compliance_dir / "requirements_matrix_2010.json"

    core = _load_json(core_path)
    section8 = _load_json(section8_path)
    pitch = _load_json(pitch_path)
    requirements = _load_json(requirements_path)

    backends: dict[str, dict[str, Any]] = {}

    def ensure_backend(backend_id: str, backend_family: str) -> dict[str, Any]:
        row = backends.setdefault(
            backend_id,
            {
                "backend_id": backend_id,
                "backend_family": backend_family,
                "matrices_present": set(),
                "status_counts": {},
                "session_status_counts": {},
                "section_refs": set(),
                "evidence_tests": set(),
                "slice_rows": [],
            },
        )
        if not row.get("backend_family"):
            row["backend_family"] = backend_family
        return row

    def add_counts(target: dict[str, int], key: str) -> None:
        if not key:
            return
        target[key] = target.get(key, 0) + 1

    for source_name, matrix, matrix_kind in (
        ("core_backend_matrix.json", core, "core"),
        ("section8_backend_matrix.json", section8, "section8"),
        ("pitch_backend_matrix.json", pitch, "pitch"),
    ):
        for row in matrix["rows"]:
            backend = ensure_backend(str(row["backend_id"]), str(row["backend_family"]))
            backend["matrices_present"].add(matrix_kind)
            add_counts(backend["status_counts"], str(row.get("status", "")))
            add_counts(backend["session_status_counts"], str(row.get("session_status", "")))
            for ref in row.get("section_refs", []):
                backend["section_refs"].add(str(ref))
            section_ref = row.get("section_ref")
            if section_ref:
                backend["section_refs"].add(str(section_ref))
            for test_ref in row.get("evidence_tests", []):
                backend["evidence_tests"].add(str(test_ref))
            backend["slice_rows"].append(
                {
                    "matrix": matrix_kind,
                    "source": f"analysis/compliance/{source_name}",
                    "status": row.get("status", ""),
                    "session_status": row.get("session_status", ""),
                    "scope": row.get("scope", ""),
                    "notes": row.get("notes", ""),
                    "slice_id": row.get("slice_id", row.get("method_name", "")),
                    "section_refs": row.get("section_refs", [row.get("section_ref", "")]),
                    "evidence_tests": row.get("evidence_tests", []),
                }
            )

    requirement_vendor_summary = {
        "python_runtime_status_counts": {},
        "certi_runtime_status_counts": {},
        "pitch_runtime_status_counts": {},
        "vendor_profile_bucket_counts": {},
    }
    for row in requirements["rows"]:
        if str(row.get("document")) != "IEEE 1516.1-2010":
            continue
        for field, summary_key in (
            ("python_runtime_status", "python_runtime_status_counts"),
            ("certi_runtime_status", "certi_runtime_status_counts"),
            ("pitch_runtime_status", "pitch_runtime_status_counts"),
            ("vendor_profile_bucket", "vendor_profile_bucket_counts"),
        ):
            value = str(row.get(field, "")).strip()
            if value:
                add_counts(requirement_vendor_summary[summary_key], value)

    backend_rows: list[dict[str, Any]] = []
    for backend_id in sorted(backends):
        backend = backends[backend_id]
        notable = [
            row
            for row in backend["slice_rows"]
            if str(row["status"]) in {"vendor-divergent", "not-yet-matrixed", "env-gated-positive", "bridge-parity-positive"}
        ]
        backend_rows.append(
            {
                "backend_id": backend["backend_id"],
                "backend_family": backend["backend_family"],
                "matrices_present": sorted(backend["matrices_present"]),
                "status_counts": _sorted_counts(backend["status_counts"]),
                "session_status_counts": _sorted_counts(backend["session_status_counts"]),
                "section_refs": sorted(backend["section_refs"]),
                "evidence_tests": sorted(backend["evidence_tests"]),
                "slice_count": len(backend["slice_rows"]),
                "notable_rows": notable[:8],
            }
        )

    return {
        "summary": {
            "backend_count": len(backend_rows),
            "core_row_count": core.get("row_count", len(core.get("rows", ()))),
            "section8_row_count": section8.get("row_count", len(section8.get("rows", ()))),
            "pitch_row_count": pitch.get("row_count", len(pitch.get("rows", ()))),
            "requirements_row_count": requirements.get("summary", {}).get("row_count", len(requirements.get("rows", ()))),
        },
        "operator_entrypoints": {
            "refresh_command": "python3 scripts/generate_compliance_artifacts.py",
            "discover_command": "python3 scripts/discover_backend_compliance.py",
            "primary_artifacts": [
                "analysis/compliance/core_backend_matrix.json",
                "analysis/compliance/section8_backend_matrix.json",
                "analysis/compliance/pitch_backend_matrix.json",
                "analysis/compliance/requirements_matrix_2010.json",
                "analysis/compliance/vendor_discovery_backlog.json",
            ],
        },
        "source_artifacts": [
            "analysis/compliance/core_backend_matrix.json",
            "analysis/compliance/section8_backend_matrix.json",
            "analysis/compliance/pitch_backend_matrix.json",
            "analysis/compliance/requirements_matrix_2010.json",
            "analysis/compliance/vendor_discovery_backlog.json",
            "docs/backend_conformance_matrix.md",
            "docs/rti_options_and_test_matrix.md",
        ],
        "requirements_vendor_summary": {
            key: _sorted_counts(value) for key, value in requirement_vendor_summary.items()
        },
        "backends": backend_rows,
    }


def build_vendor_discovery_backlog(project_root: str | Path | None = None) -> dict[str, Any]:
    compliance_dir = _compliance_dir(project_root)
    core = _load_json(compliance_dir / "core_backend_matrix.json")
    section8 = _load_json(compliance_dir / "section8_backend_matrix.json")
    pitch = _load_json(compliance_dir / "pitch_backend_matrix.json")
    requirements = _load_json(compliance_dir / "requirements_matrix_2010.json")

    rows: list[dict[str, Any]] = []

    for source_name, matrix, matrix_kind in (
        ("core_backend_matrix.json", core, "core"),
        ("section8_backend_matrix.json", section8, "section8"),
        ("pitch_backend_matrix.json", pitch, "pitch"),
    ):
        for row in matrix["rows"]:
            status = str(row.get("status", ""))
            if status not in _BACKLOG_INCLUDED_MATRIX_STATUSES:
                continue
            if status == "positive-path-passing" and "hosted-python" not in str(row.get("backend_family", "")):
                continue
            priority_rank, action = _BACKLOG_PRIORITY_BY_STATUS[status]
            section_ref = str(row.get("section_ref") or ", ".join(row.get("section_refs", [])))
            evidence_tests = [str(item) for item in row.get("evidence_tests", [])]
            rows.append(
                {
                    "priority": _BACKLOG_PRIORITY_LABELS[priority_rank],
                    "priority_rank": priority_rank,
                    "backend_id": str(row.get("backend_id", "")),
                    "backend_family": str(row.get("backend_family", "")),
                    "requirement_id": "",
                    "section_ref": section_ref,
                    "section_root": _section_root(section_ref),
                    "current_status": status,
                    "source_artifact": f"analysis/compliance/{source_name}",
                    "evidence_tests": evidence_tests,
                    "rationale": str(row.get("notes", "")),
                    "recommended_next_action": action,
                    "scope": str(row.get("scope", "")),
                    "session_status": str(row.get("session_status", "")),
                    "slice_or_method": str(row.get("slice_id", row.get("method_name", ""))),
                    "row_kind": f"{matrix_kind}-backend-row",
                }
            )

    requirements_rows = requirements.get("rows", [])
    supported_subset_by_broad: dict[str, list[dict[str, Any]]] = {}
    for row in requirements_rows:
        supported_for = str(row.get("supported_subset_for", "")).strip()
        if supported_for and str(row.get("status")) == "pass":
            supported_subset_by_broad.setdefault(supported_for, []).append(row)

    for row in requirements_rows:
        if str(row.get("kind")) != "extracted-requirement":
            continue
        if str(row.get("status")) != "partial":
            continue
        requirement_id = str(row.get("requirement_id", ""))
        if not (str(row.get("policy_basis", "")).strip() or supported_subset_by_broad.get(requirement_id)):
            continue
        priority_rank, action = _BACKLOG_PRIORITY_BY_STATUS["defended-partial"]
        rows.append(
            {
                "priority": _BACKLOG_PRIORITY_LABELS[priority_rank],
                "priority_rank": priority_rank,
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "requirement_id": requirement_id,
                "section_ref": str(row.get("section_ref", "")),
                "section_root": _section_root(str(row.get("section_ref", ""))),
                "current_status": "defended-partial",
                "source_artifact": "analysis/compliance/requirements_matrix_2010.json",
                "evidence_tests": [str(item) for item in row.get("positive_test_refs", []) if str(item).startswith("tests/")],
                "rationale": str(row.get("notes", "")),
                "recommended_next_action": action,
                "scope": str(row.get("claim_scope", "")),
                "session_status": "n/a-generated-requirement",
                "slice_or_method": requirement_id,
                "row_kind": "requirement-defended-partial",
            }
        )

    rows = _sort_backlog_rows(rows)
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    backend_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["current_status"]] = status_counts.get(row["current_status"], 0) + 1
        priority_counts[row["priority"]] = priority_counts.get(row["priority"], 0) + 1
        backend_counts[row["backend_id"]] = backend_counts.get(row["backend_id"], 0) + 1

    return {
        "summary": {
            "row_count": len(rows),
            "status_counts": _sorted_counts(status_counts),
            "priority_counts": dict(sorted(priority_counts.items())),
            "backend_counts": _sorted_counts(backend_counts),
        },
        "rows": rows,
    }


def write_vendor_discovery_backlog_artifacts(
    project_root: str | Path | None = None,
    *,
    json_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> tuple[Path, Path]:
    root = Path(project_root) if project_root is not None else _repo_root()
    compliance_dir = _compliance_dir(root)
    payload = build_vendor_discovery_backlog(root)

    json_target = Path(json_path) if json_path is not None else compliance_dir / "vendor_discovery_backlog.json"
    md_target = Path(markdown_path) if markdown_path is not None else compliance_dir / "vendor_discovery_backlog.md"
    _write_json(json_target, payload)

    md_lines = [
        "# Vendor Discovery Backlog",
        "",
        "Ranked vendor/backend discovery work derived from the generated compliance packet.",
        "",
        "Priority order:",
        "",
    ]
    for status, rank, action in _BACKLOG_PRIORITY_RULES:
        md_lines.append(f"- `{_BACKLOG_PRIORITY_LABELS[rank]}` `{status}`: {action}")
    md_lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Rows: {payload['summary']['row_count']}",
            "- Status counts: "
            + (", ".join(f"{name}={count}" for name, count in payload["summary"]["status_counts"].items()) or "none"),
            "- Priority counts: "
            + (", ".join(f"{name}={count}" for name, count in payload["summary"]["priority_counts"].items()) or "none"),
            "",
            "| Priority | Backend | Family | Section / Requirement | Status | Next action | Source | Evidence |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["rows"]:
        target = row["requirement_id"] or row["section_ref"]
        evidence = ", ".join(row["evidence_tests"][:2]) or "-"
        md_lines.append(
            f"| {row['priority']} | {row['backend_id']} | {row['backend_family']} | {target} | {row['current_status']} | "
            f"{row['recommended_next_action']} | {row['source_artifact']} | {evidence} |"
        )
    _write_markdown(md_target, md_lines)
    return json_target, md_target


def _filter_backlog_rows(
    rows: list[dict[str, Any]],
    *,
    backend_filter: str | None = None,
    section_filter: str | None = None,
    priority_filter: str | None = None,
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if _matches_backend_filter(row, backend_filter)
        and _matches_section_filter(row, section_filter)
        and _matches_priority_filter(row, priority_filter)
    ]


def build_discovery_payload(
    project_root: str | Path | None = None,
    *,
    backend_filter: str | None = None,
    section_filter: str | None = None,
    priority_filter: str | None = None,
) -> dict[str, Any]:
    catalog = build_backend_compliance_catalog(project_root)
    backlog = build_vendor_discovery_backlog(project_root)
    if not any((backend_filter, section_filter, priority_filter)):
        return {"catalog": catalog, "backlog": backlog}

    filtered_catalog = dict(catalog)
    filtered_catalog["backends"] = [
        row
        for row in catalog["backends"]
        if _matches_backend_filter(row, backend_filter)
        and (
            not section_filter
            or any(section_filter in {ref, _section_root(ref)} for ref in row.get("section_refs", []))
        )
    ]
    filtered_catalog["summary"] = dict(filtered_catalog["summary"])
    filtered_catalog["summary"]["backend_count"] = len(filtered_catalog["backends"])

    filtered_backlog = dict(backlog)
    filtered_backlog["rows"] = _filter_backlog_rows(
        backlog["rows"],
        backend_filter=backend_filter,
        section_filter=section_filter,
        priority_filter=priority_filter,
    )
    filtered_backlog["summary"] = dict(filtered_backlog["summary"])
    filtered_backlog["summary"]["row_count"] = len(filtered_backlog["rows"])
    return {"catalog": filtered_catalog, "backlog": filtered_backlog}


def render_backend_compliance_catalog_text(
    catalog: dict[str, Any],
    *,
    backend_filter: str | None = None,
    backlog: dict[str, Any] | None = None,
    section_filter: str | None = None,
    priority_filter: str | None = None,
) -> str:
    lines = [
        "Backend Compliance Discovery",
        "",
        f"Backends: {catalog['summary']['backend_count']}",
        (
            "Artifacts: "
            f"core={catalog['summary']['core_row_count']}, "
            f"section8={catalog['summary']['section8_row_count']}, "
            f"pitch={catalog['summary']['pitch_row_count']}, "
            f"requirements={catalog['summary']['requirements_row_count']}"
        ),
        f"Refresh: {catalog['operator_entrypoints']['refresh_command']}",
        f"Discover: {catalog['operator_entrypoints']['discover_command']}",
        "",
        "Requirement vendor status counts:",
    ]
    for key, counts in catalog["requirements_vendor_summary"].items():
        rendered = ", ".join(f"{name}={count}" for name, count in counts.items()) or "none"
        lines.append(f"- {key}: {rendered}")

    lines.append("")
    lines.append("Backends:")
    for backend in catalog["backends"]:
        if backend_filter and backend_filter not in {backend["backend_id"], backend["backend_family"]}:
            continue
        lines.append(f"- {backend['backend_id']} ({backend['backend_family']})")
        lines.append(f"  matrices: {', '.join(backend['matrices_present'])}")
        lines.append(
            "  statuses: "
            + (", ".join(f"{name}={count}" for name, count in backend["status_counts"].items()) or "none")
        )
        lines.append(
            "  session: "
            + (", ".join(f"{name}={count}" for name, count in backend["session_status_counts"].items()) or "none")
        )
        if backend["notable_rows"]:
            first = backend["notable_rows"][0]
            lines.append(
                "  notable: "
                f"{first['matrix']}::{first['slice_id']} -> {first['status']} ({first['session_status']})"
            )
        if backend["evidence_tests"]:
            lines.append(f"  evidence: {backend['evidence_tests'][0]}")

    if backlog is not None:
        filtered_rows = _filter_backlog_rows(
            backlog["rows"],
            backend_filter=backend_filter,
            section_filter=section_filter,
            priority_filter=priority_filter,
        )
        lines.extend(["", "Vendor discovery backlog:"])
        if section_filter or priority_filter:
            applied = []
            if section_filter:
                applied.append(f"section={section_filter}")
            if priority_filter:
                applied.append(f"priority={priority_filter}")
            lines.append(f"filters: {', '.join(applied)}")
        lines.append(f"rows: {len(filtered_rows)}")
        for row in filtered_rows[:12]:
            target = row["requirement_id"] or row["section_ref"]
            lines.append(
                f"- {row['priority']} {row['backend_id']} {target} -> {row['current_status']}: {row['recommended_next_action']}"
            )
    return "\n".join(lines) + "\n"


__all__ = [
    "build_backend_compliance_catalog",
    "build_discovery_payload",
    "build_vendor_discovery_backlog",
    "render_backend_compliance_catalog_text",
    "write_vendor_discovery_backlog_artifacts",
]
