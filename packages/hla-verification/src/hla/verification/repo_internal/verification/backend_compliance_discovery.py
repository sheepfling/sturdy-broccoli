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
    ("blocked", 2, "unblock capability or document the hard backend limitation"),
    ("env-gated-positive", 2, "rerun or stabilize environment/preflight"),
    ("not-yet-matrixed", 3, "add focused vendor matrix/probe"),
    ("not-yet-tested", 3, "add focused Pitch requirement probe"),
    ("bridge-parity-positive", 4, "promote bridge-parity row into dedicated vendor matrix/probe"),
    ("classification-required", 4, "classify backend applicability/disposition"),
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
_IEEE_1516_1_2010 = "IEEE 1516.1-2010 (2010 edition)"
_IEEE_1516_2_2010 = "IEEE 1516.2-2010 (2010 edition)"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


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


def _summary_view(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("summary")
    if isinstance(nested, dict) and nested:
        return nested
    return payload


def _sorted_counts(values: dict[str, int]) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda item: (-item[1], item[0])))


def _section_root(section_ref: str) -> str:
    match = re.search(r"§\s*(\d+)", str(section_ref or ""))
    return match.group(1) if match else ""


def _edition_qualified_section_ref(section_ref: object) -> str:
    value = str(section_ref or "")
    value = value.replace("IEEE 1516.1-2010 §", f"{_IEEE_1516_1_2010} §")
    value = value.replace("IEEE 1516.2-2010 §", f"{_IEEE_1516_2_2010} §")
    return value


def _section_sort_key(section_ref: str) -> tuple[int, str]:
    root = _section_root(section_ref)
    return (int(root) if root.isdigit() else 999, str(section_ref))


def _matches_backend_filter(row: dict[str, Any], backend_filter: str | None) -> bool:
    if not backend_filter:
        return True
    needle = backend_filter.lower()
    return any(
        needle in str(value).lower()
        for value in (
            row.get("backend_id", ""),
            row.get("backend_family", ""),
        )
    )


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


_SYNTHETIC_BACKEND_FAMILY_BY_DISPOSITION_BACKEND = {
    "python": "python-reference",
    "certi": "vendor-certi",
    "pitch": "vendor-pitch-java-bridge",
    "portico": "vendor-portico-java-bridge",
    "portico-jpype": "vendor-portico-java-bridge",
    "portico-py4j": "vendor-portico-java-bridge",
}

_DISPOSITION_BACKLOG_SOURCES = {
    "portico": "analysis/compliance/portico_requirement_disposition.json",
    "portico-jpype": "analysis/compliance/portico-jpype_requirement_disposition.json",
    "portico-py4j": "analysis/compliance/portico-py4j_requirement_disposition.json",
}


def _inject_disposition_only_backend_row(
    backends: dict[str, dict[str, Any]],
    *,
    backend_id: str,
    backend_family: str,
    summary: dict[str, Any],
) -> None:
    if backend_id in backends:
        return

    disposition_counts = {
        str(name): int(count)
        for name, count in summary.get("disposition_counts", {}).items()
        if str(name)
    }
    if not disposition_counts:
        return

    section_refs = sorted(str(name) for name in summary.get("clause_summary", {}).keys() if str(name))
    backends[backend_id] = {
        "backend_id": backend_id,
        "backend_family": backend_family,
        "matrices_present": {"requirement-disposition"},
        "status_counts": dict(disposition_counts),
        "session_status_counts": {},
        "section_refs": set(section_refs),
        "evidence_tests": set(),
        "slice_rows": [],
    }


def _append_disposition_only_backlog_row(
    rows: list[dict[str, Any]],
    *,
    backend_id: str,
    backend_family: str,
    summary: dict[str, Any],
) -> None:
    disposition_counts = {
        str(name): int(count)
        for name, count in summary.get("disposition_counts", {}).items()
        if str(name)
    }
    status = "classification-required"
    if disposition_counts.get(status, 0) <= 0:
        return

    priority_rank, action = _BACKLOG_PRIORITY_BY_STATUS[status]
    source_artifact = _DISPOSITION_BACKLOG_SOURCES[backend_id]
    rows.append(
        {
            "priority": _BACKLOG_PRIORITY_LABELS[priority_rank],
            "priority_rank": priority_rank,
            "backend_id": backend_id,
            "backend_family": backend_family,
            "requirement_id": "",
            "section_ref": "",
            "section_root": "",
            "current_status": status,
            "source_artifact": source_artifact,
            "evidence_tests": [],
            "rationale": (
                f"{backend_id} currently appears only through the generated requirement disposition packet; "
                "applicable rows remain classification-required until shared-harness wrapper tranches or "
                "real runtime evidence are promoted into backend matrices."
            ),
            "recommended_next_action": action,
            "scope": "generated-backend-disposition",
            "session_status": "n/a-requirement-disposition",
            "slice_or_method": backend_id,
            "row_kind": "synthetic-requirement-disposition-backlog-row",
        }
    )


def build_backend_compliance_catalog(project_root: str | Path | None = None) -> dict[str, Any]:
    compliance_dir = _compliance_dir(project_root)
    core_path = compliance_dir / "core_backend_matrix.json"
    section8_path = compliance_dir / "section8_backend_matrix.json"
    pitch_path = compliance_dir / "pitch_backend_matrix.json"
    requirements_path = compliance_dir / "requirements_matrix_2010.json"
    python_disposition_path = compliance_dir / "python_requirement_disposition.json"
    certi_disposition_path = compliance_dir / "certi_requirement_disposition.json"
    certi_native_disposition_path = compliance_dir / "certi-native_requirement_disposition.json"
    certi_jpype_disposition_path = compliance_dir / "certi-jpype_requirement_disposition.json"
    certi_py4j_disposition_path = compliance_dir / "certi-py4j_requirement_disposition.json"
    portico_disposition_path = compliance_dir / "portico_requirement_disposition.json"
    portico_jpype_disposition_path = compliance_dir / "portico-jpype_requirement_disposition.json"
    portico_py4j_disposition_path = compliance_dir / "portico-py4j_requirement_disposition.json"
    pitch_disposition_path = compliance_dir / "pitch_requirement_disposition.json"
    pitch_jpype_disposition_path = compliance_dir / "pitch-jpype_requirement_disposition.json"
    pitch_py4j_disposition_path = compliance_dir / "pitch-py4j_requirement_disposition.json"

    core = _load_json(core_path)
    section8 = _load_json(section8_path)
    pitch = _load_json(pitch_path)
    requirements = _load_json(requirements_path)
    python_disposition = _load_json(python_disposition_path) if python_disposition_path.exists() else {"summary": {}, "rows": []}
    certi_disposition = _load_json(certi_disposition_path) if certi_disposition_path.exists() else {"summary": {}, "rows": []}
    certi_native_disposition = _load_json(certi_native_disposition_path) if certi_native_disposition_path.exists() else {"summary": {}, "rows": []}
    certi_jpype_disposition = _load_json(certi_jpype_disposition_path) if certi_jpype_disposition_path.exists() else {"summary": {}, "rows": []}
    certi_py4j_disposition = _load_json(certi_py4j_disposition_path) if certi_py4j_disposition_path.exists() else {"summary": {}, "rows": []}
    portico_disposition = _load_json(portico_disposition_path) if portico_disposition_path.exists() else {"summary": {}, "rows": []}
    portico_jpype_disposition = _load_json(portico_jpype_disposition_path) if portico_jpype_disposition_path.exists() else {"summary": {}, "rows": []}
    portico_py4j_disposition = _load_json(portico_py4j_disposition_path) if portico_py4j_disposition_path.exists() else {"summary": {}, "rows": []}
    pitch_disposition = _load_json(pitch_disposition_path) if pitch_disposition_path.exists() else {"summary": {}, "rows": []}
    pitch_jpype_disposition = _load_json(pitch_jpype_disposition_path) if pitch_jpype_disposition_path.exists() else {"summary": {}, "rows": []}
    pitch_py4j_disposition = _load_json(pitch_py4j_disposition_path) if pitch_py4j_disposition_path.exists() else {"summary": {}, "rows": []}
    python_disposition_summary = _summary_view(python_disposition)
    certi_disposition_summary = _summary_view(certi_disposition)
    certi_native_disposition_summary = _summary_view(certi_native_disposition)
    certi_jpype_disposition_summary = _summary_view(certi_jpype_disposition)
    certi_py4j_disposition_summary = _summary_view(certi_py4j_disposition)
    portico_disposition_summary = _summary_view(portico_disposition)
    portico_jpype_disposition_summary = _summary_view(portico_jpype_disposition)
    portico_py4j_disposition_summary = _summary_view(portico_py4j_disposition)
    pitch_disposition_summary = _summary_view(pitch_disposition)
    pitch_jpype_disposition_summary = _summary_view(pitch_jpype_disposition)
    pitch_py4j_disposition_summary = _summary_view(pitch_py4j_disposition)

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
        "python_runtime_disposition_counts": {},
        "certi_runtime_status_counts": {},
        "certi_runtime_disposition_counts": {},
        "pitch_runtime_status_counts": {},
        "pitch_runtime_disposition_counts": {},
        "pitch_jpype_runtime_disposition_counts": {},
        "pitch_py4j_runtime_disposition_counts": {},
        "vendor_profile_bucket_counts": {},
    }
    for row in requirements["rows"]:
        if str(row.get("document")) not in {"IEEE 1516.1-2010", "IEEE 1516.1-2010 (2010 edition)"}:
            continue
        for field, summary_key in (
            ("python_runtime_status", "python_runtime_status_counts"),
            ("python_runtime_disposition", "python_runtime_disposition_counts"),
            ("certi_runtime_status", "certi_runtime_status_counts"),
            ("certi_runtime_disposition", "certi_runtime_disposition_counts"),
            ("pitch_runtime_status", "pitch_runtime_status_counts"),
            ("pitch_runtime_disposition", "pitch_runtime_disposition_counts"),
            ("pitch_jpype_runtime_disposition", "pitch_jpype_runtime_disposition_counts"),
            ("pitch_py4j_runtime_disposition", "pitch_py4j_runtime_disposition_counts"),
            ("vendor_profile_bucket", "vendor_profile_bucket_counts"),
        ):
            value = str(row.get(field, "")).strip()
            if value:
                add_counts(requirement_vendor_summary[summary_key], value)

    for summary in (
        python_disposition_summary,
        certi_disposition_summary,
        pitch_disposition_summary,
        portico_disposition_summary,
        portico_jpype_disposition_summary,
        portico_py4j_disposition_summary,
    ):
        backend_id = str(summary.get("backend", "")).strip()
        backend_family = _SYNTHETIC_BACKEND_FAMILY_BY_DISPOSITION_BACKEND.get(backend_id, "")
        if backend_id and backend_family:
            _inject_disposition_only_backend_row(
                backends,
                backend_id=backend_id,
                backend_family=backend_family,
                summary=summary,
            )

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
            "python_requirement_disposition_row_count": python_disposition_summary.get("row_count", len(python_disposition.get("rows", ()))),
            "certi_requirement_disposition_row_count": certi_disposition_summary.get("row_count", len(certi_disposition.get("rows", ()))),
            "certi_native_requirement_disposition_row_count": certi_native_disposition_summary.get("row_count", len(certi_native_disposition.get("rows", ()))),
            "certi_jpype_requirement_disposition_row_count": certi_jpype_disposition_summary.get("row_count", len(certi_jpype_disposition.get("rows", ()))),
            "certi_py4j_requirement_disposition_row_count": certi_py4j_disposition_summary.get("row_count", len(certi_py4j_disposition.get("rows", ()))),
            "portico_requirement_disposition_row_count": portico_disposition_summary.get("row_count", len(portico_disposition.get("rows", ()))),
            "portico_jpype_requirement_disposition_row_count": portico_jpype_disposition_summary.get("row_count", len(portico_jpype_disposition.get("rows", ()))),
            "portico_py4j_requirement_disposition_row_count": portico_py4j_disposition_summary.get("row_count", len(portico_py4j_disposition.get("rows", ()))),
            "pitch_requirement_disposition_row_count": pitch_disposition_summary.get("row_count", len(pitch_disposition.get("rows", ()))),
            "pitch_jpype_requirement_disposition_row_count": pitch_jpype_disposition_summary.get("row_count", len(pitch_jpype_disposition.get("rows", ()))),
            "pitch_py4j_requirement_disposition_row_count": pitch_py4j_disposition_summary.get("row_count", len(pitch_py4j_disposition.get("rows", ()))),
        },
        "operator_entrypoints": {
            "refresh_command": "./tools/compliance generate",
            "discover_command": "./tools/compliance discover",
            "primary_artifacts": [
                "analysis/compliance/core_backend_matrix.json",
                "analysis/compliance/section8_backend_matrix.json",
                "analysis/compliance/pitch_backend_matrix.json",
                "analysis/compliance/python_requirement_disposition.json",
                "analysis/compliance/certi_requirement_disposition.json",
                "analysis/compliance/certi-native_requirement_disposition.json",
                "analysis/compliance/certi-jpype_requirement_disposition.json",
                "analysis/compliance/certi-py4j_requirement_disposition.json",
                "analysis/compliance/portico_requirement_disposition.json",
                "analysis/compliance/portico-jpype_requirement_disposition.json",
                "analysis/compliance/portico-py4j_requirement_disposition.json",
                "analysis/compliance/pitch_requirement_disposition.json",
                "analysis/compliance/pitch-jpype_requirement_disposition.json",
                "analysis/compliance/pitch-py4j_requirement_disposition.json",
                "analysis/compliance/requirements_matrix_2010.json",
                "analysis/compliance/vendor_discovery_backlog.json",
            ],
        },
        "source_artifacts": [
            "analysis/compliance/core_backend_matrix.json",
            "analysis/compliance/section8_backend_matrix.json",
            "analysis/compliance/pitch_backend_matrix.json",
            "analysis/compliance/python_requirement_disposition.json",
            "analysis/compliance/certi_requirement_disposition.json",
            "analysis/compliance/certi-native_requirement_disposition.json",
            "analysis/compliance/certi-jpype_requirement_disposition.json",
            "analysis/compliance/certi-py4j_requirement_disposition.json",
            "analysis/compliance/portico_requirement_disposition.json",
            "analysis/compliance/portico-jpype_requirement_disposition.json",
            "analysis/compliance/portico-py4j_requirement_disposition.json",
            "analysis/compliance/pitch_requirement_disposition.json",
            "analysis/compliance/pitch-jpype_requirement_disposition.json",
            "analysis/compliance/pitch-py4j_requirement_disposition.json",
            "analysis/compliance/requirements_matrix_2010.json",
            "analysis/compliance/vendor_discovery_backlog.json",
            "docs/backend_conformance_matrix.md",
            "docs/rti_options_and_test_matrix.md",
        ],
        "requirements_vendor_summary": {
            key: _sorted_counts(value) for key, value in requirement_vendor_summary.items()
        },
        "python_requirement_disposition_summary": python_disposition_summary,
        "certi_requirement_disposition_summary": certi_disposition_summary,
        "certi_native_requirement_disposition_summary": certi_native_disposition_summary,
        "certi_jpype_requirement_disposition_summary": certi_jpype_disposition_summary,
        "certi_py4j_requirement_disposition_summary": certi_py4j_disposition_summary,
        "portico_requirement_disposition_summary": portico_disposition_summary,
        "portico_jpype_requirement_disposition_summary": portico_jpype_disposition_summary,
        "portico_py4j_requirement_disposition_summary": portico_py4j_disposition_summary,
        "pitch_requirement_disposition_summary": pitch_disposition_summary,
        "pitch_jpype_requirement_disposition_summary": pitch_jpype_disposition_summary,
        "pitch_py4j_requirement_disposition_summary": pitch_py4j_disposition_summary,
        "backends": backend_rows,
    }


def build_vendor_discovery_backlog(project_root: str | Path | None = None) -> dict[str, Any]:
    compliance_dir = _compliance_dir(project_root)
    core = _load_json(compliance_dir / "core_backend_matrix.json")
    section8 = _load_json(compliance_dir / "section8_backend_matrix.json")
    pitch = _load_json(compliance_dir / "pitch_backend_matrix.json")
    requirements = _load_json(compliance_dir / "requirements_matrix_2010.json")
    pitch_disposition_path = compliance_dir / "pitch_requirement_disposition.json"
    pitch_disposition = _load_json(pitch_disposition_path) if pitch_disposition_path.exists() else {"rows": []}
    portico_disposition_path = compliance_dir / "portico_requirement_disposition.json"
    portico_jpype_disposition_path = compliance_dir / "portico-jpype_requirement_disposition.json"
    portico_py4j_disposition_path = compliance_dir / "portico-py4j_requirement_disposition.json"
    portico_disposition = _load_json(portico_disposition_path) if portico_disposition_path.exists() else {"summary": {}, "rows": []}
    portico_jpype_disposition = _load_json(portico_jpype_disposition_path) if portico_jpype_disposition_path.exists() else {"summary": {}, "rows": []}
    portico_py4j_disposition = _load_json(portico_py4j_disposition_path) if portico_py4j_disposition_path.exists() else {"summary": {}, "rows": []}

    rows: list[dict[str, Any]] = []
    pitch_requirement_backlog_statuses = {"blocked", "vendor-divergent", "not-yet-tested", "classification-required"}
    pitch_requirement_targets = {
        (backend_id, str(row.get("section_ref", "")))
        for row in pitch_disposition.get("rows", [])
        for backend_id, disposition_key in (
            ("pitch-jpype", "pitch_jpype_disposition"),
            ("pitch-py4j", "pitch_py4j_disposition"),
        )
        if str(row.get(disposition_key, "")) in pitch_requirement_backlog_statuses
    }

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
            section_ref = _edition_qualified_section_ref(row.get("section_ref") or ", ".join(row.get("section_refs", [])))
            if matrix_kind == "pitch" and (str(row.get("backend_id", "")), section_ref) in pitch_requirement_targets:
                continue
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
                "section_ref": _edition_qualified_section_ref(row.get("section_ref", "")),
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

    for row in pitch_disposition.get("rows", []):
        status = str(row.get("pitch_disposition", ""))
        if status not in pitch_requirement_backlog_statuses:
            continue
        priority_rank, action = _BACKLOG_PRIORITY_BY_STATUS[status]
        section_ref = _edition_qualified_section_ref(row.get("section_ref", ""))
        rows.append(
            {
                "priority": _BACKLOG_PRIORITY_LABELS[priority_rank],
                "priority_rank": priority_rank,
                "backend_id": "pitch-requirements",
                "backend_family": "vendor-pitch-java-bridge",
                "requirement_id": str(row.get("requirement_id", "")),
                "section_ref": section_ref,
                "section_root": _section_root(section_ref),
                "current_status": status,
                "source_artifact": "analysis/compliance/pitch_requirement_disposition.json",
                "evidence_tests": [str(item) for item in row.get("evidence_refs", [])],
                "rationale": str(row.get("notes", "")),
                "recommended_next_action": action,
                "scope": str(row.get("applicability", "")),
                "session_status": "n/a-requirement-disposition",
                "slice_or_method": str(row.get("requirement_id") or row.get("matrix_id", "")),
                "row_kind": "pitch-requirement-disposition-row",
            }
        )
        family_evidence = tuple(str(item) for item in row.get("evidence_refs", []))
        for profile_backend_id, disposition_key, evidence_key in (
            ("pitch-jpype", "pitch_jpype_disposition", "pitch_jpype_evidence_refs"),
            ("pitch-py4j", "pitch_py4j_disposition", "pitch_py4j_evidence_refs"),
        ):
            profile_status = str(row.get(disposition_key, ""))
            if profile_status not in pitch_requirement_backlog_statuses:
                continue
            profile_evidence = tuple(str(item) for item in row.get(evidence_key, []))
            if profile_status == status and profile_evidence == family_evidence:
                continue
            profile_priority_rank, profile_action = _BACKLOG_PRIORITY_BY_STATUS[profile_status]
            rows.append(
                {
                    "priority": _BACKLOG_PRIORITY_LABELS[profile_priority_rank],
                    "priority_rank": profile_priority_rank,
                    "backend_id": profile_backend_id,
                    "backend_family": "vendor-pitch-java-bridge",
                    "requirement_id": str(row.get("requirement_id", "")),
                    "section_ref": section_ref,
                    "section_root": _section_root(section_ref),
                    "current_status": profile_status,
                    "source_artifact": "analysis/compliance/pitch_requirement_disposition.json",
                    "evidence_tests": list(profile_evidence),
                    "rationale": str(row.get("notes", "")),
                    "recommended_next_action": profile_action,
                    "scope": str(row.get("applicability", "")),
                    "session_status": "n/a-requirement-disposition",
                    "slice_or_method": str(row.get("requirement_id") or row.get("matrix_id", "")),
                    "row_kind": "pitch-requirement-profile-row",
                }
            )

    backlog_backend_ids = {str(row["backend_id"]) for row in rows}
    for summary in (
        _summary_view(portico_disposition),
        _summary_view(portico_jpype_disposition),
        _summary_view(portico_py4j_disposition),
    ):
        backend_id = str(summary.get("backend", "")).strip()
        backend_family = _SYNTHETIC_BACKEND_FAMILY_BY_DISPOSITION_BACKEND.get(backend_id, "")
        if not backend_id or not backend_family or backend_id in backlog_backend_ids:
            continue
        _append_disposition_only_backlog_row(
            rows,
            backend_id=backend_id,
            backend_family=backend_family,
            summary=summary,
        )
        backlog_backend_ids.add(backend_id)

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
        evidence = ", ".join(row["evidence_tests"]) or "-"
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
    pitch_disposition = catalog.get("pitch_requirement_disposition_summary", {})
    python_disposition = catalog.get("python_requirement_disposition_summary", {})
    certi_disposition = catalog.get("certi_requirement_disposition_summary", {})
    certi_native_disposition = catalog.get("certi_native_requirement_disposition_summary", {})
    certi_jpype_disposition = catalog.get("certi_jpype_requirement_disposition_summary", {})
    certi_py4j_disposition = catalog.get("certi_py4j_requirement_disposition_summary", {})
    portico_disposition = catalog.get("portico_requirement_disposition_summary", {})
    portico_jpype_disposition = catalog.get("portico_jpype_requirement_disposition_summary", {})
    portico_py4j_disposition = catalog.get("portico_py4j_requirement_disposition_summary", {})
    pitch_jpype_disposition = catalog.get("pitch_jpype_requirement_disposition_summary", {})
    pitch_py4j_disposition = catalog.get("pitch_py4j_requirement_disposition_summary", {})
    for label, summary in (
        ("python_requirement_dispositions", python_disposition),
        ("certi_requirement_dispositions", certi_disposition),
        ("certi-native_requirement_dispositions", certi_native_disposition),
        ("certi-jpype_requirement_dispositions", certi_jpype_disposition),
        ("certi-py4j_requirement_dispositions", certi_py4j_disposition),
        ("portico_requirement_dispositions", portico_disposition),
        ("portico-jpype_requirement_dispositions", portico_jpype_disposition),
        ("portico-py4j_requirement_dispositions", portico_py4j_disposition),
    ):
        disposition_counts = summary.get("disposition_counts", {})
        if disposition_counts:
            rendered = ", ".join(f"{name}={count}" for name, count in disposition_counts.items())
            lines.append(f"- {label}: {rendered}")
    disposition_counts = pitch_disposition.get("disposition_counts", {})
    if disposition_counts:
        rendered = ", ".join(f"{name}={count}" for name, count in disposition_counts.items())
        lines.append(f"- pitch_requirement_dispositions: {rendered}")
    profile_disposition_counts = pitch_disposition.get("profile_disposition_counts", {})
    for profile, counts in sorted(profile_disposition_counts.items()):
        rendered = ", ".join(f"{name}={count}" for name, count in counts.items()) or "none"
        lines.append(f"- {profile}_requirement_dispositions: {rendered}")
    profile_clause_summary = pitch_disposition.get("profile_clause_summary", {})
    for profile in ("pitch-jpype", "pitch-py4j"):
        clause4_counts = profile_clause_summary.get(profile, {}).get(f"{_IEEE_1516_1_2010} §4", {})
        if clause4_counts:
            rendered = ", ".join(f"{name}={count}" for name, count in clause4_counts.items())
            lines.append(f"- {profile}_clause4_requirement_dispositions: {rendered}")

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
