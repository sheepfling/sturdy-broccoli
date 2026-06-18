"""IEEE 1516-2025 route parity matrix and artifact writers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

ROUTE_IDS_2025 = (
    "python-2025-inprocess",
    "python-2025-fedpro-grpc",
    "java-standard-2025-jpype",
    "java-standard-2025-py4j",
    "cpp-standard-2025-pybind",
    "cpp-standard-2025-grpc",
)

PARITY_COVERED = "parity-covered"
PARTIAL = "partial"
MISSING = "missing"


@dataclass(frozen=True)
class Spec2025RouteParityRow:
    scenario: str
    route: str
    status: str
    requirements: tuple[str, ...]
    evidence_tests: tuple[str, ...]
    notes: str


_PYTHON_CORE_TESTS = ("tests/test_rti1516_2025_spec_and_shim.py",)
_FEDPRO_TESTS = ("tests/transport/test_grpc_transport_2025.py",)
_ROUTE_EVIDENCE_TESTS = (
    "tests/backends/test_shim_route_trace_evidence.py",
    "tests/requirements/test_2025_tail_backlog_evidence.py",
)
_FINISH_LINE_TESTS = ("tests/requirements/test_2025_finish_line_snapshot.py",)


def _row(
    scenario: str,
    route: str,
    status: str,
    requirements: tuple[str, ...],
    evidence_tests: tuple[str, ...],
    notes: str,
) -> Spec2025RouteParityRow:
    return Spec2025RouteParityRow(
        scenario=scenario,
        route=route,
        status=status,
        requirements=requirements,
        evidence_tests=evidence_tests,
        notes=notes,
    )


_EXPLICIT_SPEC2025_ROUTE_PARITY_ROWS: tuple[Spec2025RouteParityRow, ...] = (
    _row(
        "federation_lifecycle",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-FI-005", "HLA2025-FI-006"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers connect, create, join, resign, destroy, disconnect, and callback polling.",
    ),
    _row(
        "federation_lifecycle",
        "python-2025-fedpro-grpc",
        PARITY_COVERED,
        ("HLA2025-FI-005", "HLA2025-FI-006", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers the same lifecycle session through typed protobuf calls.",
    ),
    _row(
        "federation_lifecycle",
        "java-standard-2025-jpype",
        PARTIAL,
        ("HLA2025-BND-001", "HLA2025-FI-003", "HLA2025-FI-004"),
        _ROUTE_EVIDENCE_TESTS,
        "Artifact-gated Java route records runtime capability only when the 2025 jar is built; not full behavioral parity.",
    ),
    _row(
        "federation_lifecycle",
        "java-standard-2025-py4j",
        PARTIAL,
        ("HLA2025-BND-001", "HLA2025-FI-003", "HLA2025-FI-004"),
        _ROUTE_EVIDENCE_TESTS,
        "Artifact-gated Java route records runtime capability only when the 2025 jar is built; not full behavioral parity.",
    ),
    _row(
        "federation_lifecycle",
        "cpp-standard-2025-pybind",
        PARTIAL,
        ("HLA2025-BND-002", "HLA2025-FI-003", "HLA2025-FI-004"),
        _ROUTE_EVIDENCE_TESTS,
        "C++ source trace and local runtime capability evidence exist; full cross-route behavior remains open.",
    ),
    _row(
        "federation_lifecycle",
        "cpp-standard-2025-grpc",
        PARTIAL,
        ("HLA2025-BND-002", "HLA2025-FI-003", "HLA2025-FI-004"),
        _ROUTE_EVIDENCE_TESTS,
        "C++ source trace and local runtime capability evidence exist; full cross-route behavior remains open.",
    ),
    _row(
        "object_exchange",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-FI-001"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers FOM-backed publish/subscribe, discovery, attribute reflection, and interaction receipt.",
    ),
    _row(
        "object_exchange",
        "python-2025-fedpro-grpc",
        PARITY_COVERED,
        ("HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers object discovery, attribute reflection, interaction receipt, and timestamped variants.",
    ),
    _row(
        "object_exchange",
        "java-standard-2025-jpype",
        MISSING,
        ("HLA2025-BND-001", "HLA2025-FI-004"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 object-exchange parity scenario is recorded yet.",
    ),
    _row(
        "object_exchange",
        "java-standard-2025-py4j",
        MISSING,
        ("HLA2025-BND-001", "HLA2025-FI-004"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 object-exchange parity scenario is recorded yet.",
    ),
    _row(
        "object_exchange",
        "cpp-standard-2025-pybind",
        MISSING,
        ("HLA2025-BND-002", "HLA2025-FI-004"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 object-exchange parity scenario is recorded yet.",
    ),
    _row(
        "object_exchange",
        "cpp-standard-2025-grpc",
        MISSING,
        ("HLA2025-BND-002", "HLA2025-FI-004"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 object-exchange parity scenario is recorded yet.",
    ),
    _row(
        "ownership",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-FR-005", "HLA2025-FR-008", "HLA2025-FI-001"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers basic, negotiated, cancellation, unavailable, release-denied, and resign ownership slices.",
    ),
    _row(
        "ownership",
        "python-2025-fedpro-grpc",
        PARTIAL,
        ("HLA2025-FR-005", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers basic divest/acquire/query callbacks, negotiated divestiture, release requests, "
        "release denial, acquisition cancellation, divestiture-if-wanted, and cancel-negotiated-offer callbacks; "
        "resign-time ownership policy remains in-process only.",
    ),
    _row(
        "ownership",
        "java-standard-2025-jpype",
        MISSING,
        ("HLA2025-FR-005", "HLA2025-FR-008", "HLA2025-BND-001"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 ownership parity scenario is recorded yet.",
    ),
    _row(
        "ownership",
        "java-standard-2025-py4j",
        MISSING,
        ("HLA2025-FR-005", "HLA2025-FR-008", "HLA2025-BND-001"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 ownership parity scenario is recorded yet.",
    ),
    _row(
        "ownership",
        "cpp-standard-2025-pybind",
        MISSING,
        ("HLA2025-FR-005", "HLA2025-FR-008", "HLA2025-BND-002"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 ownership parity scenario is recorded yet.",
    ),
    _row(
        "ownership",
        "cpp-standard-2025-grpc",
        MISSING,
        ("HLA2025-FR-005", "HLA2025-FR-008", "HLA2025-BND-002"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 ownership parity scenario is recorded yet.",
    ),
    _row(
        "ddm",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-MOD-007", "HLA2025-NEW-004", "HLA2025-FI-001"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers object-region filtering, scope advisory callbacks, and 2025 default attribute policy calls.",
    ),
    _row(
        "ddm",
        "python-2025-fedpro-grpc",
        PARTIAL,
        ("HLA2025-MOD-007", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers object attribute and interaction class region-overlap filtering "
        "with conveyed region evidence, not the full DDM matrix.",
    ),
    _row(
        "ddm",
        "java-standard-2025-jpype",
        MISSING,
        ("HLA2025-MOD-007", "HLA2025-BND-001"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 DDM parity scenario is recorded yet.",
    ),
    _row(
        "ddm",
        "java-standard-2025-py4j",
        MISSING,
        ("HLA2025-MOD-007", "HLA2025-BND-001"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 DDM parity scenario is recorded yet.",
    ),
    _row(
        "ddm",
        "cpp-standard-2025-pybind",
        MISSING,
        ("HLA2025-MOD-007", "HLA2025-BND-002"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 DDM parity scenario is recorded yet.",
    ),
    _row(
        "ddm",
        "cpp-standard-2025-grpc",
        MISSING,
        ("HLA2025-MOD-007", "HLA2025-BND-002"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 DDM parity scenario is recorded yet.",
    ),
    _row(
        "time_management",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-MOD-006"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers logical-time factories, regulation/constrained mode, grants, queued TSO, and retraction.",
    ),
    _row(
        "time_management",
        "python-2025-fedpro-grpc",
        PARTIAL,
        ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers regulation/constrained grants, time advance, queued TSO delivery, and pre-delivery retract.",
    ),
    _row(
        "time_management",
        "java-standard-2025-jpype",
        MISSING,
        ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-BND-001"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 time-management parity scenario is recorded yet.",
    ),
    _row(
        "time_management",
        "java-standard-2025-py4j",
        MISSING,
        ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-BND-001"),
        _FINISH_LINE_TESTS,
        "No executable Java 2025 time-management parity scenario is recorded yet.",
    ),
    _row(
        "time_management",
        "cpp-standard-2025-pybind",
        MISSING,
        ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-BND-002"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 time-management parity scenario is recorded yet.",
    ),
    _row(
        "time_management",
        "cpp-standard-2025-grpc",
        MISSING,
        ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-BND-002"),
        _FINISH_LINE_TESTS,
        "No executable C++ 2025 time-management parity scenario is recorded yet.",
    ),
    _row(
        "save_restore",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-FI-001", "HLA2025-FI-005", "HLA2025-REQ-002"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers federation save/restore lifecycle and rollback callback slices.",
    ),
    _row(
        "save_restore",
        "python-2025-fedpro-grpc",
        PARTIAL,
        ("HLA2025-FI-001", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers save/restore lifecycle calls, status callbacks, "
        "success/failure callbacks, and abort callbacks; object/time rollback remains in-process only.",
    ),
    _row(
        "mom",
        "python-2025-inprocess",
        PARTIAL,
        ("HLA2025-NEW-004", "HLA2025-FI-001"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim records MOM switch/report serialization slices, not full MOM manager action routing.",
    ),
    _row(
        "mom",
        "python-2025-fedpro-grpc",
        PARTIAL,
        ("HLA2025-NEW-004", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route emits MOM service-invocation report callbacks, not full MOM manager action routing.",
    ),
    _row(
        "support_services",
        "python-2025-inprocess",
        PARITY_COVERED,
        ("HLA2025-FI-001", "HLA2025-MOD-007"),
        _PYTHON_CORE_TESTS,
        "Python 2025 shim covers support lookups needed by the current runtime scenarios.",
    ),
    _row(
        "support_services",
        "python-2025-fedpro-grpc",
        PARTIAL,
        ("HLA2025-FI-001", "HLA2025-BND-003"),
        _FEDPRO_TESTS,
        "Hosted FedPro 2025 route covers FOM handle, dimension, transportation, and service-reporting switch lookups.",
    ),
)


_SCENARIO_REQUIREMENTS = {
    "federation_lifecycle": ("HLA2025-FI-005", "HLA2025-FI-006"),
    "object_exchange": ("HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-FI-001"),
    "ownership": ("HLA2025-FR-005", "HLA2025-FR-008", "HLA2025-FI-001"),
    "ddm": ("HLA2025-MOD-007", "HLA2025-NEW-004", "HLA2025-FI-001"),
    "time_management": ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-MOD-006"),
    "save_restore": ("HLA2025-FI-001", "HLA2025-FI-005", "HLA2025-REQ-002"),
    "mom": ("HLA2025-NEW-004", "HLA2025-FI-001"),
    "support_services": ("HLA2025-FI-001", "HLA2025-MOD-007"),
}


def _binding_requirement(route: str) -> str:
    if route.startswith("java-"):
        return "HLA2025-BND-001"
    if route.startswith("cpp-"):
        return "HLA2025-BND-002"
    if route == "python-2025-fedpro-grpc":
        return "HLA2025-BND-003"
    return "HLA2025-FI-004"


def _missing_route_note(scenario: str, route: str) -> str:
    if route.startswith("java-"):
        return f"No executable Java 2025 {scenario} parity scenario is recorded yet."
    if route.startswith("cpp-"):
        return f"No executable C++ 2025 {scenario} parity scenario is recorded yet."
    if route == "python-2025-fedpro-grpc":
        return f"No executable FedPro 2025 {scenario} route scenario is recorded yet."
    return f"No executable Python 2025 {scenario} route scenario is recorded yet."


def _complete_route_rows(rows: tuple[Spec2025RouteParityRow, ...]) -> tuple[Spec2025RouteParityRow, ...]:
    existing = {(row.scenario, row.route) for row in rows}
    completed = list(rows)
    for scenario, requirements in _SCENARIO_REQUIREMENTS.items():
        for route in ROUTE_IDS_2025:
            if (scenario, route) in existing:
                continue
            completed.append(
                _row(
                    scenario,
                    route,
                    MISSING,
                    (*requirements, _binding_requirement(route)),
                    _FINISH_LINE_TESTS,
                    _missing_route_note(scenario, route),
                )
            )
    return tuple(sorted(completed, key=lambda row: (row.scenario, ROUTE_IDS_2025.index(row.route))))


SPEC2025_ROUTE_PARITY_ROWS: tuple[Spec2025RouteParityRow, ...] = _complete_route_rows(_EXPLICIT_SPEC2025_ROUTE_PARITY_ROWS)


def summarize_spec2025_route_parity(rows: tuple[Spec2025RouteParityRow, ...] = SPEC2025_ROUTE_PARITY_ROWS) -> dict[str, object]:
    by_status = {status: 0 for status in (PARITY_COVERED, PARTIAL, MISSING)}
    by_route: dict[str, dict[str, int]] = {
        route: {status: 0 for status in (PARITY_COVERED, PARTIAL, MISSING)}
        for route in ROUTE_IDS_2025
    }
    for row in rows:
        by_status[row.status] = by_status.get(row.status, 0) + 1
        by_route.setdefault(row.route, {status: 0 for status in (PARITY_COVERED, PARTIAL, MISSING)})
        by_route[row.route][row.status] = by_route[row.route].get(row.status, 0) + 1
    return {
        "routes": ROUTE_IDS_2025,
        "scenario_count": len({row.scenario for row in rows}),
        "row_count": len(rows),
        "by_status": by_status,
        "by_route": by_route,
        "rows": [
            {
                "scenario": row.scenario,
                "route": row.route,
                "status": row.status,
                "requirements": list(row.requirements),
                "evidence_tests": list(row.evidence_tests),
                "notes": row.notes,
            }
            for row in rows
        ],
    }


def write_spec2025_route_parity_matrix(output_dir: str | Path) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    csv_path = output_path / "spec2025_route_parity_matrix.csv"
    md_path = output_path / "spec2025_route_parity_matrix.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["scenario", "route", "status", "requirements", "evidence_tests", "notes"],
        )
        writer.writeheader()
        for row in SPEC2025_ROUTE_PARITY_ROWS:
            writer.writerow(
                {
                    "scenario": row.scenario,
                    "route": row.route,
                    "status": row.status,
                    "requirements": "; ".join(row.requirements),
                    "evidence_tests": "; ".join(row.evidence_tests),
                    "notes": row.notes,
                }
            )

    lines = [
        "# IEEE 1516-2025 Route Parity Matrix",
        "",
        "This matrix is not a conformance claim. It records which 2025 scenarios have executable route evidence and which routes remain partial or missing.",
        "",
        "| Scenario | Route | Status | Requirements | Evidence tests | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in SPEC2025_ROUTE_PARITY_ROWS:
        lines.append(
            f"| {row.scenario} | {row.route} | {row.status} | "
            f"{', '.join(row.requirements)} | {', '.join(row.evidence_tests)} | {row.notes} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path


__all__ = [
    "MISSING",
    "PARITY_COVERED",
    "PARTIAL",
    "ROUTE_IDS_2025",
    "SPEC2025_ROUTE_PARITY_ROWS",
    "Spec2025RouteParityRow",
    "summarize_spec2025_route_parity",
    "write_spec2025_route_parity_matrix",
]
