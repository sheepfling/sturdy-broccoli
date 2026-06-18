"""Finish-line inventory for the IEEE 1516-2025 requirements tranche."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

HIGH_PRIORITIES = frozenset({"high", "very-high"})

IMPLEMENTED_EVIDENCE_SLICES: tuple[Mapping[str, Any], ...] = (
    {
        "id": "2025-factory-composition",
        "status": "implemented-slice",
        "requirements": ("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/test_hla_factory_composition.py",
            "packages/hla-rti-core/src/hla/rti/factory.py",
        ),
    },
    {
        "id": "2025-auth-connect",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_encoding_auth_contexts.py",
            "packages/hla-rti-core/src/hla/rti/factory.py",
        ),
    },
    {
        "id": "2025-fom-validation",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FR-001", "HLA2025-OMT-001", "HLA2025-OMT-005", "HLA2025-OMT-006"),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/test_hla_factory_composition.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py",
        ),
    },
    {
        "id": "2025-lifecycle-and-members",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-005", "HLA2025-FI-006", "HLA2025-NEW-002", "HLA2025-NEW-003"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-logical-time",
        "status": "partial",
        "requirements": ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-MOD-006"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_shim_route_trace_evidence.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "remaining": "flushQueueGrant ordering and full generic binding checks are still open.",
    },
    {
        "id": "2025-fom-showcase",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FR-001", "HLA2025-FR-003", "HLA2025-FR-004"),
        "evidence": (
            "tests/scenarios/test_proto2025_fom_showcase.py",
            "packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py",
        ),
    },
    {
        "id": "2025-handle-normalization",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-005", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
)

BACKLOG_STATUS_BY_ROW = {
    "HLA2025-MOD-001": "implemented-slice",
    "HLA2025-MOD-002": "partial",
    "HLA2025-MOD-003": "partial",
    "HLA2025-MOD-006": "partial",
    "HLA2025-NEW-002": "implemented-slice",
    "HLA2025-NEW-003": "implemented-slice",
    "HLA2025-NEW-005": "implemented-slice",
    "HLA2025-NEW-006": "partial",
    "HLA2025-VER-001": "partial",
    "HLA2025-VER-002": "implemented-slice",
}


@dataclass(frozen=True, slots=True)
class Spec2025Paths:
    project_root: Path
    completion_backlog: Path
    executable_summary: Path
    executable_rows: Path
    registry: Path


def _paths(project_root: Path) -> Spec2025Paths:
    req_dir = project_root / "docs" / "requirements" / "ieee-1516-2025"
    return Spec2025Paths(
        project_root=project_root,
        completion_backlog=project_root / "requirements" / "2025" / "requirement_completion_backlog.csv",
        executable_summary=req_dir / "executable_tests" / "hla_2025_executable_test_requirements_v3_summary.json",
        executable_rows=req_dir / "executable_tests" / "hla_2025_executable_test_requirements_v3.csv",
        registry=req_dir / "requirements.json",
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _counter(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row[field] for row in rows).items()))


def _next_status(row_id: str) -> str:
    return BACKLOG_STATUS_BY_ROW.get(row_id, "planned")


def _priority_rank(row: dict[str, str]) -> tuple[int, str]:
    priority_order = {"very-high": 0, "high": 1, "medium-high": 2}
    status_order = {"planned": 0, "partial": 1, "implemented-slice": 2}
    return (
        priority_order.get(row["priority"], 9) * 10 + status_order.get(row["current_status"], 9),
        row["id"],
    )


def build_spec2025_finish_line_snapshot(project_root: Path) -> dict[str, Any]:
    """Return the current 2025 requirements finish-line inventory."""

    paths = _paths(project_root)
    completion_rows = _read_csv(paths.completion_backlog)
    executable_summary = json.loads(paths.executable_summary.read_text(encoding="utf-8"))
    executable_rows = _read_csv(paths.executable_rows)
    registry = json.loads(paths.registry.read_text(encoding="utf-8"))
    registry_requirements = registry.get("requirements", ())

    completion_with_status: list[dict[str, str]] = []
    for row in completion_rows:
        item = dict(row)
        item["current_status"] = _next_status(row["id"])
        completion_with_status.append(item)

    high_priority_open = [
        row
        for row in completion_with_status
        if row["priority"] in HIGH_PRIORITIES and row["current_status"] != "implemented-slice"
    ]
    high_priority_open = sorted(high_priority_open, key=_priority_rank)

    executable_status_counts = dict(sorted(Counter(row["expected_status"] for row in executable_rows).items()))
    executable_priority_counts = dict(sorted(Counter(row["priority"] for row in executable_rows).items()))

    return {
        "scope": "IEEE 1516-2025 requirements finish-line inventory, not a conformance claim",
        "registry": {
            "initial_tranche_requirements": len(registry_requirements),
            "imported_packets": [packet["id"] for packet in registry.get("imported_packets", ())],
        },
        "completion_backlog": {
            "row_count": len(completion_with_status),
            "by_bucket": _counter(completion_with_status, "bucket"),
            "by_priority": _counter(completion_with_status, "priority"),
            "by_current_status": _counter(completion_with_status, "current_status"),
            "high_priority_open_count": len(high_priority_open),
            "high_priority_open": [
                {
                    "id": row["id"],
                    "bucket": row["bucket"],
                    "area": row["area"],
                    "priority": row["priority"],
                    "current_status": row["current_status"],
                    "acceptance_criteria": row["acceptance_criteria"],
                    "verification_work": row["verification_work"],
                }
                for row in high_priority_open
            ],
        },
        "executable_test_backlog": {
            "row_count": executable_summary["executable_test_rows"],
            "source_rows": executable_summary["source_rows"],
            "by_test_kind": executable_summary["by_test_kind"],
            "by_expected_status": executable_summary["by_expected_status"],
            "by_priority": executable_priority_counts,
            "expected_status_counts_from_rows": executable_status_counts,
        },
        "implemented_evidence_slices": [dict(slice_) for slice_ in IMPLEMENTED_EVIDENCE_SLICES],
        "finish_rule": (
            "Each remaining row needs a positive test, a negative unsupported-boundary test, "
            "or an explicit supported-subset row before it can be counted as closed."
        ),
    }


def build_spec2025_finish_line_markdown(project_root: Path) -> list[str]:
    snapshot = build_spec2025_finish_line_snapshot(project_root)
    backlog = snapshot["completion_backlog"]
    executable = snapshot["executable_test_backlog"]
    lines = [
        "# IEEE 1516-2025 Requirements Finish Line",
        "",
        "This inventory is deliberately conservative. It records implemented slices, partial slices, and planned work without using HLA conformance language.",
        "",
        "## Current Scale",
        "",
        f"- Initial curated registry rows: {snapshot['registry']['initial_tranche_requirements']}",
        f"- Imported executable-test rows: {executable['row_count']}",
        f"- Completion-backlog rows: {backlog['row_count']}",
        f"- High-priority rows still open: {backlog['high_priority_open_count']}",
        "",
        "## Implemented Evidence Slices",
        "",
        "| Slice | Status | Requirements | Evidence |",
        "|---|---|---|---|",
    ]
    for slice_ in snapshot["implemented_evidence_slices"]:
        lines.append(
            "| {id} | {status} | {requirements} | {evidence} |".format(
                id=slice_["id"],
                status=slice_["status"],
                requirements=", ".join(slice_["requirements"]),
                evidence=", ".join(slice_["evidence"]),
            )
        )
    lines.extend(
        [
            "",
            "## Highest-Priority Open Work",
            "",
            "| ID | Area | Priority | Status | Verification work |",
            "|---|---|---|---|---|",
        ]
    )
    for row in backlog["high_priority_open"]:
        lines.append(
            f"| {row['id']} | {row['area']} | {row['priority']} | {row['current_status']} | {row['verification_work']} |"
        )
    lines.extend(
        [
            "",
            "## Finish Rule",
            "",
            str(snapshot["finish_rule"]),
            "",
            "Do not promote `partial` rows by broad wording. Narrow the claim or add the missing positive/negative evidence.",
        ]
    )
    return lines


def write_spec2025_finish_line(output_dir: Path, project_root: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_spec2025_finish_line_snapshot(project_root)
    json_path = output_dir / "spec2025_finish_line_snapshot.json"
    markdown_path = output_dir / "spec2025_finish_line.md"
    json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text("\n".join(build_spec2025_finish_line_markdown(project_root)) + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


__all__ = [
    "build_spec2025_finish_line_markdown",
    "build_spec2025_finish_line_snapshot",
    "write_spec2025_finish_line",
]
