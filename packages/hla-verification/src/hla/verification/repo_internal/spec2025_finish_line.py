"""Finish-line inventory for the IEEE 1516-2025 requirements tranche."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

HIGH_PRIORITIES = frozenset({"high", "very-high"})
CLOSED_STATUSES = frozenset({"implemented-slice", "unsupported-boundary", "legacy-only"})

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
        "status": "implemented-slice",
        "requirements": ("HLA2025-FR-010", "HLA2025-FI-009", "HLA2025-MOD-006"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_shim_route_trace_evidence.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 shim covers default logical-time factory selection, lookahead query/modify, "
            "timeAdvanceRequest, flushQueueRequest, timeAdvanceGrant, flushQueueGrant, and GALT/LITS queries. "
            "Full queued TSO ordering and cross-binding parity remain separate backlog work."
        ),
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
    {
        "id": "2025-switch-inquiry-control",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-008", "HLA2025-RET-001", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-fom-mim-error-taxonomy",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-callback-context-parameters",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-004", "HLA2025-RET-002", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
        ),
        "supported_scope": (
            "Python 2025 federate ambassador surface exposes direct callback context parameters "
            "for discovery, reflection, interaction, directed interaction, and remove callbacks "
            "without native Supplemental*Info helper objects."
        ),
    },
    {
        "id": "2025-directed-interaction-boundary",
        "status": "unsupported-boundary",
        "requirements": ("HLA2025-NEW-001", "HLA2025-REQ-002", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "2025 directed interaction RTI and callback method surface is present; the Python shim "
            "returns structured RTIinternalError unsupported-boundary evidence for directed publish, "
            "subscribe, and send services until two-federate directed delivery is implemented."
        ),
    },
    {
        "id": "2025-omt-reference-value-required",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-006", "HLA2025-OMT-002", "HLA2025-OMT-006"),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py",
        ),
        "supported_scope": (
            "Shared OMT parser preserves referenceDataTypes and attribute valueRequired metadata, "
            "serializer round-trips the metadata, and 2025 validation rejects invalid valueRequired values."
        ),
    },
    {
        "id": "2025-carry-forward-cleanup",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BLG-001", "HLA2025-BLG-002", "HLA2025-REQ-001"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv",
            "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv",
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Renumbered service-utilization rows preserve behavior claims while updating clause references. "
            "Common FOM/SOM object-model parsing remains shared and preserves nullable 2025 metadata."
        ),
    },
    {
        "id": "2025-exception-and-logical-time-deltas",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-009", "HLA2025-MOD-010", "HLA2025-VER-002"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "tests/test_rti1516_2025_validation.py",
            "requirements/2025/STRICT_DOC_INVENTORY.json",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Native 2025 exception inventory uses the 2025 FOM/MIM/auth names without FDD-era exception names. "
            "OMT XML parsing accepts 2025 logicalTime/logicalTimeInterval and serializer emits those names for 2025."
        ),
    },
    {
        "id": "2025-java-binding-source-trace",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-001", "HLA2025-FI-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/STRICT_DOC_INVENTORY.json",
            "requirements/2025/SOURCE_TRACE.md",
            "docs/evidence/java-intake/java-2025-standard-shim-2025-jpype.json",
            "docs/evidence/java-intake/java-2025-standard-shim-2025-py4j.json",
        ),
        "supported_scope": (
            "Java 2025 package, RTI/federate/encoder declaration inventory, source trace, and intake evidence "
            "are separated from common behavior rows. This is surface/intake evidence, not full Java behavior conformance."
        ),
    },
    {
        "id": "2025-cpp-binding-source-trace",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-002", "HLA2025-FI-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/SOURCE_TRACE.md",
            "docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json",
            "docs/evidence/cpp-intake/cpp-standard-2025-2025-grpc.json",
            "docs/evidence/shim_routes/cpp-standard-2025.json",
        ),
        "supported_scope": (
            "C++ 2025 namespace/source trace and route evidence are recorded separately from common behavior rows. "
            "This is source-trace/intake evidence, not a full C++ RTI behavior pass."
        ),
    },
    {
        "id": "2025-fedpro-transport-contract",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto",
        ),
        "supported_scope": (
            "2025 FedPro protobuf package, gRPC service binding, typed request/callback oneofs, and loopback "
            "transport smoke tests are present. Full FedPro session behavior remains outside this slice."
        ),
    },
    {
        "id": "2025-ddm-default-attribute-policy",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-007", "HLA2025-NEW-004", "HLA2025-FI-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim resolves object class, attribute, transportation, and dimension handles from the "
            "loaded FOM/FDD catalog, reports available dimensions for object and interaction classes, returns "
            "dimension upper bounds, and stores validated default attribute transportation/order policy changes. "
            "Full DDM region routing and object update application of defaults remain later behavior work."
        ),
    },
    {
        "id": "2025-ownership-basic-tag-callbacks",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-005", "HLA2025-FI-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports FOM-backed object instance registration, initial attribute ownership by "
            "the registering federate, unconditional divestiture with ownership validation, acquire-if-available "
            "with 2025 user-supplied tags, ownership unavailable/acquisition callbacks, ownership query callbacks, "
            "and isAttributeOwnedByFederate. Negotiated ownership and resign-time ownership policies remain later "
            "behavior work."
        ),
    },
    {
        "id": "2025-tail-unsupported-behavior-boundaries",
        "status": "unsupported-boundary",
        "requirements": ("HLA2025-NEW-007", "HLA2025-REQ-002"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Detailed MOM service-report serialization is recorded as an explicit Python shim unsupported boundary. "
            "Service surfaces and differential rows are traceable; behavior is not claimed complete."
        ),
    },
    {
        "id": "2025-wsdl-legacy-only",
        "status": "legacy-only",
        "requirements": ("HLA2025-RET-003", "HLA2025-BND-003", "HLA2025-REQ-002"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv",
            "CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto",
        ),
        "supported_scope": (
            "The 2010 WSDL binding remains legacy-only and is not counted as a native 2025 common behavior row. "
            "2025 transport work is isolated under FedPro/protobuf."
        ),
    },
)

BACKLOG_STATUS_BY_ROW = {
    "HLA2025-BLG-001": "implemented-slice",
    "HLA2025-BLG-002": "implemented-slice",
    "HLA2025-BND-001": "implemented-slice",
    "HLA2025-BND-002": "implemented-slice",
    "HLA2025-BND-003": "implemented-slice",
    "HLA2025-MOD-001": "implemented-slice",
    "HLA2025-MOD-002": "implemented-slice",
    "HLA2025-MOD-003": "implemented-slice",
    "HLA2025-MOD-004": "implemented-slice",
    "HLA2025-MOD-005": "implemented-slice",
    "HLA2025-MOD-006": "implemented-slice",
    "HLA2025-MOD-007": "implemented-slice",
    "HLA2025-MOD-008": "implemented-slice",
    "HLA2025-MOD-009": "implemented-slice",
    "HLA2025-MOD-010": "implemented-slice",
    "HLA2025-NEW-001": "unsupported-boundary",
    "HLA2025-NEW-002": "implemented-slice",
    "HLA2025-NEW-003": "implemented-slice",
    "HLA2025-NEW-004": "implemented-slice",
    "HLA2025-NEW-005": "implemented-slice",
    "HLA2025-NEW-006": "implemented-slice",
    "HLA2025-NEW-007": "unsupported-boundary",
    "HLA2025-RET-001": "implemented-slice",
    "HLA2025-RET-002": "implemented-slice",
    "HLA2025-RET-003": "legacy-only",
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

    high_priority_open = [row for row in completion_with_status if row["priority"] in HIGH_PRIORITIES and row["current_status"] not in CLOSED_STATUSES]
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
            "or an explicit supported-subset/unsupported-boundary row before it can be counted as closed."
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
        lines.append(f"| {row['id']} | {row['area']} | {row['priority']} | {row['current_status']} | {row['verification_work']} |")
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
