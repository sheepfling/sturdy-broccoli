"""Python direct-vs-gRPC route parity registry and artifact writers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


PYTHON_ROUTE_IDS = ("python-direct", "python-grpc")


@dataclass(frozen=True)
class PythonRouteParityScenario:
    name: str
    routes: tuple[str, ...]
    evidence_tests: tuple[str, ...]
    notes: str


PYTHON_ROUTE_PARITY_SCENARIOS = (
    PythonRouteParityScenario(
        name="federation_lifecycle",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared lifecycle assertions run against direct Python and hosted Python over gRPC.",
    ),
    PythonRouteParityScenario(
        name="object_exchange",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared publish/subscribe, object reflection, and interaction exchange assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="declaration_management",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared declaration management start/stop and publish/subscribe gating assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="request_attribute_value_update",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared object-targeted and class-wide request-attribute-value-update routing assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="ownership",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared attribute ownership acquisition assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="synchronization",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared synchronization, registration failure, failed-federate, late-join, and multi-point assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="negotiated_ownership",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared negotiated divestiture and release-request ownership assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="ownership_edge_cases",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared release-denied, unavailable-ownership, and non-owner-update rejection assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="save_restore",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared save/restore and queued-callback save/restore assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="ddm",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared DDM object-region lifecycle assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="support_services",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="Shared support lookup, transport lookup, factory, and decode assertions run on both routes.",
    ),
    PythonRouteParityScenario(
        name="target_radar",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=("tests/scenarios/test_python_route_parity.py",),
        notes="The canonical Target/Radar scenario runs with the same observable assertions on both routes.",
    ),
    PythonRouteParityScenario(
        name="time_management",
        routes=PYTHON_ROUTE_IDS,
        evidence_tests=(
            "tests/time/test_section8_backend_matrix.py",
            "tests/time/test_lookahead_backend_matrix.py",
        ),
        notes="Section 8 and lookahead matrices already execute direct Python and hosted Python gRPC with matching assertions.",
    ),
)


def write_python_route_parity_matrix(output_dir: str | Path) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    csv_path = output_path / "python_route_parity_matrix.csv"
    md_path = output_path / "python_route_parity_matrix.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["scenario", "routes", "parity_status", "evidence_tests", "notes"])
        writer.writeheader()
        for scenario in PYTHON_ROUTE_PARITY_SCENARIOS:
            writer.writerow(
                {
                    "scenario": scenario.name,
                    "routes": "; ".join(scenario.routes),
                    "parity_status": "parity-covered" if tuple(scenario.routes) == PYTHON_ROUTE_IDS else "partial",
                    "evidence_tests": "; ".join(scenario.evidence_tests),
                    "notes": scenario.notes,
                }
            )

    lines = [
        "# Python Route Parity Matrix",
        "",
        "| Scenario | Routes | Status | Evidence tests | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for scenario in PYTHON_ROUTE_PARITY_SCENARIOS:
        lines.append(
            f"| {scenario.name} | {', '.join(scenario.routes)} | "
            f"{'parity-covered' if tuple(scenario.routes) == PYTHON_ROUTE_IDS else 'partial'} | "
            f"{', '.join(scenario.evidence_tests)} | {scenario.notes} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path


__all__ = [
    "PYTHON_ROUTE_IDS",
    "PYTHON_ROUTE_PARITY_SCENARIOS",
    "PythonRouteParityScenario",
    "write_python_route_parity_matrix",
]
