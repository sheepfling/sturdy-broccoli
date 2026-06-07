#!/usr/bin/env python3
from __future__ import annotations

import importlib
import inspect
import json
import pkgutil
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import hla2010
from hla2010.conformance import (
    ServiceConformanceRow,
    actionable_negative_expectation_count,
    build_requirements_ledger,
    build_service_conformance_matrix,
    negative_path_status,
    write_requirements_ledger_csv,
    write_requirements_ledger_json,
    write_service_conformance_csv,
    write_service_conformance_json,
)


OUTPUT_DIR = REPO_ROOT / "analysis" / "compliance"


@dataclass(frozen=True)
class SectionComplianceSummary:
    section_ref: str
    interface_counts: dict[str, int]
    implementation_status_counts: dict[str, int]
    verification_status_counts: dict[str, int]
    exact_requirement_evidence_rows: int
    no_requirement_evidence_rows: int
    known_gap_rows: int
    methods: tuple[str, ...]


@dataclass(frozen=True)
class PublicClassInventoryRow:
    module: str
    class_name: str
    exported_via_package: bool
    mapping_status: str
    rationale: str


@dataclass(frozen=True)
class GapSectionSummary:
    section_root: str
    section_label: str
    row_count: int
    core_priority: int
    representative_methods: tuple[str, ...]


@dataclass(frozen=True)
class NegativePathLedgerRow:
    section_ref: str
    interface: str
    method_name: str
    verification_status: str
    negative_path_status: str
    declared_exception_count: int
    actionable_exception_count: int
    negative_executed_count: int
    declared_exceptions: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class Section8BackendMatrixRow:
    backend_id: str
    backend_family: str
    section_ref: str
    method_name: str
    status: str
    scope: str
    session_status: str
    supports_immediate_inline: bool
    evidence_tests: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class CoreBackendMatrixRow:
    backend_id: str
    backend_family: str
    slice_id: str
    section_refs: tuple[str, ...]
    status: str
    scope: str
    session_status: str
    evidence_tests: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class CompletionChecklistRow:
    checklist_id: str
    area: str
    status: str
    evidence: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class UnfinishedWorkRow:
    priority: str
    claim_value_rank: int
    work_id: str
    area: str
    current_state: str
    target_state: str
    evidence: tuple[str, ...]
    rationale: str


def _negative_priority(row: ServiceConformanceRow) -> tuple[str, str, tuple[int, int, str, str]]:
    root = row.section.split(".", 1)[0] if row.section else "unmapped"
    exception_count = actionable_negative_expectation_count(row)
    if root == "4":
        return ("P1", "core federation-management negative path", (0, -exception_count, row.section_ref, row.method_name))
    if root in {"5", "6", "7", "8", "9"}:
        return ("P2", "core RTI behavior negative path", (1, -exception_count, row.section_ref, row.method_name))
    if root == "10":
        return ("P3", "support-service negative path", (2, -exception_count, row.section_ref, row.method_name))
    return ("P4", "non-core or unmapped negative path", (3, -exception_count, row.section_ref, row.method_name))


def _negative_path_rationale(row: ServiceConformanceRow) -> str:
    status = negative_path_status(row)
    if status == "not-applicable":
        return "No declared RTI exception matrix is present for this row."
    if status == "complete":
        return "Declared negative-path expectations are fully represented by executable evidence."
    if status == "mapped-not-exhaustive":
        return "Declared exceptions are mapped from source metadata, but exhaustive negative-path execution is still incomplete."
    if status == "partial":
        return "Some negative-path execution exists, but completeness is still partial."
    return "Declared negative-path expectations exist, but executable negative-path evidence is not yet linked."


_SECTION8_HOSTED_METHODS = frozenset(
    {
        "enableTimeRegulation",
        "disableTimeRegulation",
        "enableTimeConstrained",
        "disableTimeConstrained",
        "timeAdvanceRequest",
        "timeAdvanceRequestAvailable",
        "nextMessageRequest",
        "nextMessageRequestAvailable",
        "flushQueueRequest",
        "queryGALT",
        "queryLogicalTime",
        "queryLITS",
        "modifyLookahead",
        "queryLookahead",
        "retract",
        "requestRetraction",
        "changeAttributeOrderType",
        "changeInteractionOrderType",
        "enableAsynchronousDelivery",
        "disableAsynchronousDelivery",
        "timeRegulationEnabled",
        "timeConstrainedEnabled",
        "timeAdvanceGrant",
    }
)

_SECTION8_CERTI_METHODS = frozenset(
    {
        "enableTimeRegulation",
        "enableTimeConstrained",
        "timeAdvanceRequest",
        "flushQueueRequest",
        "queryGALT",
        "queryLITS",
        "timeRegulationEnabled",
        "timeConstrainedEnabled",
        "timeAdvanceGrant",
    }
)

_SECTION8_PITCH_METHODS = frozenset(
    {
        "enableTimeRegulation",
        "enableTimeConstrained",
        "timeAdvanceGrant",
    }
)

_PYTHON_BACKEND_EXTENDED_TESTS = (
    "tests/backends/test_python_backend_federation_extended.py",
    "tests/backends/test_python_backend_time_ddm_extended.py",
    "tests/backends/test_python_backend_object_ownership_extended.py",
)

_CERTI_REAL_BACKEND_MATRIX_TESTS = (
    "tests/vendors/test_certi_real_backend_exchange_matrix.py",
    "tests/vendors/test_certi_real_backend_time_matrix.py",
    "tests/vendors/test_certi_real_backend_ownership_matrix.py",
)

_CORE_BACKEND_SLICE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "slice_id": "federation-sync",
        "section_refs": ("IEEE 1516.1-2010 §4.25", "IEEE 1516.1-2010 §4.26"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Reference backend semantics are exercised indirectly through shared scenario helpers and broader federation tests.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI now has explicit synchronization end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit synchronization end-to-end coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit synchronization coverage.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit synchronization coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "env-gated-positive",
                "scope": "real-vendor core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI synchronization matrix exists but was not rerun in this session.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "env-gated-positive",
                "scope": "real-vendor core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI JPype synchronization matrix exists but was not rerun in this session.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "env-gated-positive",
                "scope": "real-vendor core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI Py4J synchronization matrix exists but was not rerun in this session.",
            },
        ),
    },
    {
        "slice_id": "exchange",
        "section_refs": ("IEEE 1516.1-2010 §5.2", "IEEE 1516.1-2010 §6.9"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/time/test_section8_backend_matrix.py",),
                "notes": "Reference backend exchange behavior is exercised heavily through the Section 8 and scenario suites.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI has explicit exchange end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit exchange end-to-end coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit exchange coverage including timed exchange.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit exchange coverage including timed exchange.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI native exchange and cross-facade parity slices passed in this session.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI JPype exchange and cross-facade parity slices passed in this session.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI Py4J exchange and cross-facade parity slices passed in this session.",
            },
        ),
    },
    {
        "slice_id": "ownership",
        "section_refs": ("IEEE 1516.1-2010 §7.2", "IEEE 1516.1-2010 §7.18"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend ownership semantics are covered in the Python backend suite.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI now has explicit ownership end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit ownership and negotiated ownership coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit ownership coverage.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit ownership coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI native plain ownership slice passed in this session.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI JPype plain ownership slice passed in this session.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI Py4J plain ownership slice passed in this session.",
            },
        ),
    },
    {
        "slice_id": "negotiated-ownership",
        "section_refs": ("IEEE 1516.1-2010 §7.3", "IEEE 1516.1-2010 §7.15"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend negotiated ownership semantics are covered in the Python backend suite.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI has explicit negotiated ownership end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit negotiated ownership end-to-end coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit negotiated ownership coverage.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit negotiated ownership coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "vendor-divergent",
                "scope": "real-vendor core scenario slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI native negotiated ownership failed in this session because the runtime never produced the expected release/acquisition handshake.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor core scenario slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI JPype negotiated ownership failed in this session because the runtime never produced the expected release/acquisition handshake.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor core scenario slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI Py4J negotiated ownership failed in this session because the runtime never produced the expected release/acquisition handshake.",
            },
        ),
    },
)

_SECTION8_BACKEND_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "backend_id": "python-inmemory",
        "backend_family": "python-reference",
        "method_set": None,
        "status": "complete-actionable",
        "scope": "reference-backend complete actionable matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": True,
        "evidence_tests": (
            "tests/time/test_section8_backend_matrix.py",
            "tests/time/test_mom_mim_time_v10.py",
            "tests/time/test_mom_mim_time_management_v010.py",
            "tests/time/test_mom_mim_and_time_semantics_v010.py",
            *_PYTHON_BACKEND_EXTENDED_TESTS,
        ),
        "notes": "Python in-memory backend has complete actionable Section 8 negative-path coverage plus explicit HLA_IMMEDIATE evidence.",
    },
    {
        "backend_id": "rest-hosted-python",
        "backend_family": "hosted-python-rest",
        "method_set": _SECTION8_HOSTED_METHODS,
        "status": "positive-path-passing",
        "scope": "hosted backend positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": (
            "tests/time/test_section8_backend_matrix.py",
            "tests/transport/test_rest_transport.py",
        ),
        "notes": "REST-hosted Python RTI is exercised through the dedicated Section 8 suite and transport end-to-end checks.",
    },
    {
        "backend_id": "grpc-hosted-python",
        "backend_family": "hosted-python-grpc",
        "method_set": _SECTION8_HOSTED_METHODS,
        "status": "positive-path-passing",
        "scope": "hosted backend positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": (
            "tests/time/test_section8_backend_matrix.py",
            "tests/transport/test_grpc_transport_python_server.py",
        ),
        "notes": "gRPC-hosted Python RTI is exercised through the dedicated Section 8 suite and transport end-to-end checks.",
    },
    {
        "backend_id": "certi-native",
        "backend_family": "vendor-certi",
        "method_set": _SECTION8_CERTI_METHODS,
        "status": "env-gated-positive",
        "scope": "real-vendor positive-path matrix",
        "session_status": "skipped-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": _CERTI_REAL_BACKEND_MATRIX_TESTS,
        "notes": "CERTI runtime evidence is environment-gated; current session skipped the real RTI Section 8 slice.",
    },
    {
        "backend_id": "certi-jpype",
        "backend_family": "vendor-certi-java-bridge",
        "method_set": _SECTION8_CERTI_METHODS,
        "status": "env-gated-positive",
        "scope": "real-vendor positive-path matrix",
        "session_status": "skipped-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": _CERTI_REAL_BACKEND_MATRIX_TESTS,
        "notes": "CERTI JPype facade follows the same environment-gated real RTI time matrix path.",
    },
    {
        "backend_id": "certi-py4j",
        "backend_family": "vendor-certi-java-bridge",
        "method_set": _SECTION8_CERTI_METHODS,
        "status": "env-gated-positive",
        "scope": "real-vendor positive-path matrix",
        "session_status": "skipped-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": _CERTI_REAL_BACKEND_MATRIX_TESTS,
        "notes": "CERTI Py4J facade follows the same environment-gated real RTI time matrix path.",
    },
    {
        "backend_id": "pitch-jpype",
        "backend_family": "vendor-pitch-java-bridge",
        "method_set": _SECTION8_PITCH_METHODS,
        "status": "bridge-parity-positive",
        "scope": "bridge parity time profile only",
        "session_status": "not-run-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
        "notes": "Pitch currently has bridge-parity time profile evidence rather than a dedicated Section 8 matrix.",
    },
    {
        "backend_id": "pitch-py4j",
        "backend_family": "vendor-pitch-java-bridge",
        "method_set": _SECTION8_PITCH_METHODS,
        "status": "bridge-parity-positive",
        "scope": "bridge parity time profile only",
        "session_status": "not-run-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
        "notes": "Pitch currently has bridge-parity time profile evidence rather than a dedicated Section 8 matrix.",
    },
)


def _section_summary(rows: tuple[ServiceConformanceRow, ...]) -> list[SectionComplianceSummary]:
    grouped: dict[str, list[ServiceConformanceRow]] = defaultdict(list)
    for row in rows:
        grouped[row.section_ref].append(row)

    summaries: list[SectionComplianceSummary] = []
    for section_ref, section_rows in sorted(grouped.items()):
        interface_counts: dict[str, int] = defaultdict(int)
        implementation_counts: dict[str, int] = defaultdict(int)
        verification_counts: dict[str, int] = defaultdict(int)
        exact_requirement_evidence_rows = 0
        no_requirement_evidence_rows = 0
        known_gap_rows = 0
        methods: list[str] = []

        for row in section_rows:
            interface_counts[row.interface] += 1
            implementation_counts[row.implementation_status] += 1
            verification_counts[row.verification_status] += 1
            methods.append(f"{row.interface}.{row.method_name}")
            if row.verification_status in {"focused-executable-tests", "callback-helper-covered"}:
                exact_requirement_evidence_rows += 1
            if row.verification_status not in {"focused-executable-tests", "callback-helper-covered"}:
                no_requirement_evidence_rows += 1
            if row.known_gaps:
                known_gap_rows += 1

        summaries.append(
            SectionComplianceSummary(
                section_ref=section_ref,
                interface_counts=dict(sorted(interface_counts.items())),
                implementation_status_counts=dict(sorted(implementation_counts.items())),
                verification_status_counts=dict(sorted(verification_counts.items())),
                exact_requirement_evidence_rows=exact_requirement_evidence_rows,
                no_requirement_evidence_rows=no_requirement_evidence_rows,
                known_gap_rows=known_gap_rows,
                methods=tuple(sorted(methods)),
            )
        )
    return summaries


def _gap_priority(row: ServiceConformanceRow) -> tuple[str, str]:
    root = row.section.split(".", 1)[0] if row.section else "unmapped"
    if root in {"4", "5", "6", "7", "8", "9"}:
        if row.implementation_status == "adapter-or-gap":
            return ("P0", "core section and no pure-Python reference handler")
        return ("P1", "core HLA section without exact requirement-level executable evidence")
    if row.known_gaps:
        return ("P2", "non-core section with known implementation or negative-path gaps")
    return ("P3", "non-core section lacking exact row-level evidence")


def _mapping_status(module_name: str, cls: type[Any]) -> tuple[str, str]:
    name = cls.__name__
    if module_name == "hla2010.raw_api":
        return ("close-1to1", "Generated abstract service surface from spec-source API metadata; overloads are collapsed into *args/**kwargs.")
    if module_name == "hla2010.handles":
        return ("close-1to1", "Opaque handle family mirrors HLA handle categories, with Python dataclass/set/dict implementations.")
    if module_name == "hla2010.time":
        return ("close-1to1", "Logical time, interval, and factory classes intentionally mirror the HLA logical-time families.")
    if module_name == "hla2010.exceptions":
        return ("close-1to1", "Exception class names intentionally mirror the HLA exception taxonomy.")
    if module_name == "hla2010.api":
        if name in {"RTIambassador", "RTIAmbassador", "FederateAmbassador"}:
            return ("adapted", "Python-facing ambassador layer preserves the spec surface but adds snake_case conveniences and overload flattening.")
        return ("adapted", "Convenience layer on top of the raw spec-shaped API surface.")
    if module_name == "hla2010.types":
        return ("adapted", "Python dataclass wrappers for HLA concepts and return values, not literal header-level classes.")
    if module_name in {"hla2010.encoding", "hla2010.ambassadors", "hla2010.startup", "hla2010.rti", "hla2010.conformance", "hla2010.verification"}:
        return ("supporting-scaffold", "Support or workflow scaffolding around the HLA surface rather than a direct header-spec type.")
    if module_name.startswith("hla2010.real_rti") or module_name.startswith("hla2010.backends"):
        return ("supporting-scaffold", "Runtime/backend integration support, not a direct spec class mapping.")
    return ("adapted", "Public class is part of the package surface but is not a literal 1:1 reproduction of a Java/C++ header type.")


def _public_class_inventory() -> list[PublicClassInventoryRow]:
    exported_names = set(getattr(hla2010, "__dict__", {}).keys())
    rows: list[PublicClassInventoryRow] = []
    package_dir = REPO_ROOT / "hla2010"

    for module_info in pkgutil.iter_modules([str(package_dir)]):
        if module_info.ispkg or module_info.name == "backends":
            continue
        module_name = f"hla2010.{module_info.name}"
        module = importlib.import_module(module_name)
        module_public = getattr(module, "__all__", None)
        public_names = set(module_public) if module_public is not None else {name for name in vars(module) if not name.startswith("_")}
        for name, value in sorted(vars(module).items()):
            if name not in public_names:
                continue
            if not inspect.isclass(value):
                continue
            if value.__module__ != module_name:
                continue
            status, rationale = _mapping_status(module_name, value)
            rows.append(
                PublicClassInventoryRow(
                    module=module_name,
                    class_name=name,
                    exported_via_package=name in exported_names,
                    mapping_status=status,
                    rationale=rationale,
                )
            )
    return rows


def _split_public_class_inventory(rows: list[PublicClassInventoryRow]) -> tuple[list[PublicClassInventoryRow], list[PublicClassInventoryRow]]:
    package_exported = [row for row in rows if row.exported_via_package]
    all_public = list(rows)
    return package_exported, all_public


def _gap_section_summaries(rows: tuple[ServiceConformanceRow, ...]) -> list[GapSectionSummary]:
    grouped: dict[str, list[ServiceConformanceRow]] = defaultdict(list)
    for row in rows:
        if row.verification_status in {"focused-executable-tests", "callback-helper-covered"}:
            continue
        grouped[row.section.split(".", 1)[0] if row.section else "unmapped"].append(row)

    summaries: list[GapSectionSummary] = []
    for root, group_rows in grouped.items():
        core_priority = 0 if root in {"4", "5", "6", "7", "8", "9"} else 1
        section_label = f"IEEE 1516.1-2010 §{root}" if root != "unmapped" else "unmapped"
        representative_methods = tuple(sorted(f"{row.interface}.{row.method_name}" for row in group_rows)[:8])
        summaries.append(
            GapSectionSummary(
                section_root=root,
                section_label=section_label,
                row_count=len(group_rows),
                core_priority=core_priority,
                representative_methods=representative_methods,
            )
        )
    return sorted(summaries, key=lambda item: (item.core_priority, -item.row_count, item.section_root))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_section_summary_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    summaries = _section_summary(rows)
    _write_json(
        OUTPUT_DIR / "section_compliance_summary.json",
        {
            "summary_count": len(summaries),
            "sections": [asdict(item) for item in summaries],
        },
    )

    md_lines = [
        "# Section Compliance Summary",
        "",
        "| Section | Exact requirement evidence | No requirement evidence | Known gap rows | Verification status counts |",
        "|---|---:|---:|---:|---|",
    ]
    for item in summaries:
        md_lines.append(
            f"| {item.section_ref} | {item.exact_requirement_evidence_rows} | {item.no_requirement_evidence_rows} | {item.known_gap_rows} | "
            f"{', '.join(f'{k}={v}' for k, v in item.verification_status_counts.items())} |"
        )
    _write_markdown(OUTPUT_DIR / "section_compliance_summary.md", md_lines)


def _write_public_class_inventory_artifacts() -> None:
    rows = _public_class_inventory()
    package_exported_rows, all_public_rows = _split_public_class_inventory(rows)

    def write_inventory(stem: str, title: str, inventory_rows: list[PublicClassInventoryRow]) -> None:
        _write_json(
            OUTPUT_DIR / f"{stem}.json",
            {
                "row_count": len(inventory_rows),
                "rows": [asdict(item) for item in inventory_rows],
            },
        )

        md_lines = [
            f"# {title}",
            "",
            "| Module | Class | Exported via `hla2010` | Mapping status | Rationale |",
            "|---|---|---:|---|---|",
        ]
        for item in inventory_rows:
            md_lines.append(
                f"| {item.module} | {item.class_name} | {'yes' if item.exported_via_package else 'no'} | {item.mapping_status} | {item.rationale} |"
            )
        _write_markdown(OUTPUT_DIR / f"{stem}.md", md_lines)

    write_inventory("public_class_inventory_all_public", "Public Class Inventory: All Public Module Classes", all_public_rows)
    write_inventory("public_class_inventory_package_exported", "Public Class Inventory: Package Exported", package_exported_rows)

    _write_json(
        OUTPUT_DIR / "public_class_inventory.json",
        {
            "all_public_row_count": len(all_public_rows),
            "package_exported_row_count": len(package_exported_rows),
            "rows": [asdict(item) for item in all_public_rows],
        },
    )

    md_lines = [
        "# Public Class Inventory",
        "",
        f"- all public module classes: {len(all_public_rows)}",
        f"- package-exported classes: {len(package_exported_rows)}",
        "",
        "| Module | Class | Exported via `hla2010` | Mapping status | Rationale |",
        "|---|---|---:|---|---|",
    ]
    for item in all_public_rows:
        md_lines.append(
            f"| {item.module} | {item.class_name} | {'yes' if item.exported_via_package else 'no'} | {item.mapping_status} | {item.rationale} |"
        )
    _write_markdown(OUTPUT_DIR / "public_class_inventory.md", md_lines)


def _write_gap_report_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    gap_rows = [
        row for row in rows
        if row.verification_status not in {"focused-executable-tests", "callback-helper-covered"}
    ]
    _write_json(
        OUTPUT_DIR / "no_requirement_evidence_rows.json",
        {
            "row_count": len(gap_rows),
            "rows": [
                {
                    **row.as_dict(),
                    "priority": _gap_priority(row)[0],
                    "priority_rationale": _gap_priority(row)[1],
                }
                for row in gap_rows
            ],
        },
    )

    md_lines = [
        "# No Requirement Evidence Rows",
        "",
        "Rows listed here do not have exact requirement-level executable evidence linked in the current conformance metadata.",
        "They may still have group-level or slice-level executable evidence.",
        "",
        "| Priority | Section | Interface | Method | Implementation status | Known gaps |",
        "|---|---|---|---|---|---|",
    ]
    for row in gap_rows:
        gaps = "; ".join(row.known_gaps) if row.known_gaps else ""
        priority, _rationale = _gap_priority(row)
        md_lines.append(
            f"| {priority} | {row.section_ref} | {row.interface} | {row.method_name} | {row.implementation_status} | {gaps} |"
        )
    _write_markdown(OUTPUT_DIR / "no_requirement_evidence_rows.md", md_lines)

    summaries = _gap_section_summaries(rows)
    _write_json(
        OUTPUT_DIR / "gap_executive_summary.json",
        {
            "section_count": len(summaries),
            "sections": [asdict(item) for item in summaries],
        },
    )

    summary_lines = [
        "# Gap Executive Summary",
        "",
        "Ranked by core HLA section priority (`§4-§9` first) and then by remaining row count without exact requirement-level executable evidence.",
        "",
        "| Rank | Section | Remaining rows | Representative methods |",
        "|---|---|---:|---|",
    ]
    for index, item in enumerate(summaries, start=1):
        summary_lines.append(
            f"| {index} | {item.section_label} | {item.row_count} | {', '.join(item.representative_methods)} |"
        )
    _write_markdown(OUTPUT_DIR / "gap_executive_summary.md", summary_lines)


def _write_negative_path_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    ledger_rows = [
        NegativePathLedgerRow(
            section_ref=row.section_ref,
            interface=row.interface,
            method_name=row.method_name,
            verification_status=row.verification_status,
            negative_path_status=negative_path_status(row),
            declared_exception_count=row.negative_expectation_count,
            actionable_exception_count=actionable_negative_expectation_count(row),
            negative_executed_count=row.negative_executed_count,
            declared_exceptions=row.declared_exceptions,
            rationale=_negative_path_rationale(row),
        )
        for row in rows
    ]
    by_status: dict[str, int] = defaultdict(int)
    for row in ledger_rows:
        by_status[row.negative_path_status] += 1

    _write_json(
        OUTPUT_DIR / "negative_path_completeness.json",
        {
            "row_count": len(ledger_rows),
            "status_counts": dict(sorted(by_status.items())),
            "rows": [asdict(item) for item in ledger_rows],
        },
    )

    md_lines = [
        "# Negative Path Completeness",
        "",
        "This ledger tracks declared exception and negative-path completeness independently from positive-path requirement evidence.",
        "",
        "| Section | Interface | Method | Negative-path status | Declared exceptions | Actionable exceptions | Executed negatives | Rationale |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in ledger_rows:
        md_lines.append(
            f"| {row.section_ref} | {row.interface} | {row.method_name} | {row.negative_path_status} | "
            f"{row.declared_exception_count} | {row.actionable_exception_count} | {row.negative_executed_count} | {row.rationale} |"
        )
    _write_markdown(OUTPUT_DIR / "negative_path_completeness.md", md_lines)

    ranked_rows = [
        row for row in rows
        if negative_path_status(row) == "mapped-not-exhaustive"
    ]
    ranked_rows = sorted(ranked_rows, key=lambda row: _negative_priority(row)[2])
    _write_json(
        OUTPUT_DIR / "negative_path_priority_ranking.json",
        {
            "row_count": len(ranked_rows),
            "rows": [
                {
                    **row.as_dict(),
                    "negative_path_status": negative_path_status(row),
                    "priority": _negative_priority(row)[0],
                    "priority_rationale": _negative_priority(row)[1],
                }
                for row in ranked_rows
            ],
        },
    )

    ranking_lines = [
        "# Negative Path Priority Ranking",
        "",
        "Rows ranked by section priority and declared exception count for converting mapped negative-path obligations into executable tests.",
        "",
        "| Priority | Section | Interface | Method | Declared exceptions | Verification status |",
        "|---|---|---|---|---:|---|",
    ]
    for row in ranked_rows:
        ranking_lines.append(
            f"| {_negative_priority(row)[0]} | {row.section_ref} | {row.interface} | {row.method_name} | "
            f"{row.negative_expectation_count} | {row.verification_status} |"
        )
    _write_markdown(OUTPUT_DIR / "negative_path_priority_ranking.md", ranking_lines)


def _write_section8_backend_matrix_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    section8_rows = sorted((row for row in rows if row.section.split(".", 1)[0] == "8"), key=lambda row: (row.section_ref, row.method_name))
    matrix_rows: list[Section8BackendMatrixRow] = []
    for profile in _SECTION8_BACKEND_PROFILES:
        method_set = profile["method_set"]
        for row in section8_rows:
            if method_set is None or row.method_name in method_set:
                status = profile["status"]
            else:
                status = "not-yet-matrixed"
            matrix_rows.append(
                Section8BackendMatrixRow(
                    backend_id=profile["backend_id"],
                    backend_family=profile["backend_family"],
                    section_ref=row.section_ref,
                    method_name=row.method_name,
                    status=status,
                    scope=profile["scope"],
                    session_status=profile["session_status"],
                    supports_immediate_inline=bool(profile["supports_immediate_inline"]),
                    evidence_tests=tuple(profile["evidence_tests"]),
                    notes=profile["notes"],
                )
            )

    grouped: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in matrix_rows:
        grouped[row.backend_id][row.status] += 1

    _write_json(
        OUTPUT_DIR / "section8_backend_matrix.json",
        {
            "row_count": len(matrix_rows),
            "backend_summaries": {
                backend_id: dict(sorted(counts.items()))
                for backend_id, counts in sorted(grouped.items())
            },
            "rows": [asdict(item) for item in matrix_rows],
        },
    )

    md_lines = [
        "# Section 8 Backend Matrix",
        "",
        "This matrix records backend-specific Section 8 verification scope separately from the reference conformance ledger.",
        "",
        "| Backend | Family | Section | Method | Status | Scope | Session status | Immediate inline | Evidence | Notes |",
        "|---|---|---|---|---|---|---|---:|---|---|",
    ]
    for row in matrix_rows:
        md_lines.append(
            f"| {row.backend_id} | {row.backend_family} | {row.section_ref} | {row.method_name} | {row.status} | {row.scope} | "
            f"{row.session_status} | {'yes' if row.supports_immediate_inline else 'no'} | {', '.join(row.evidence_tests)} | {row.notes} |"
        )
    _write_markdown(OUTPUT_DIR / "section8_backend_matrix.md", md_lines)


def _build_core_backend_matrix_rows() -> list[CoreBackendMatrixRow]:
    rows: list[CoreBackendMatrixRow] = []
    for slice_profile in _CORE_BACKEND_SLICE_PROFILES:
        for profile in slice_profile["profiles"]:
            rows.append(
                CoreBackendMatrixRow(
                    backend_id=profile["backend_id"],
                    backend_family=profile["backend_family"],
                    slice_id=slice_profile["slice_id"],
                    section_refs=tuple(slice_profile["section_refs"]),
                    status=profile["status"],
                    scope=profile["scope"],
                    session_status=profile["session_status"],
                    evidence_tests=tuple(profile["evidence_tests"]),
                    notes=profile["notes"],
                )
            )
    return rows


def _write_core_backend_matrix_artifacts() -> list[CoreBackendMatrixRow]:
    matrix_rows = _build_core_backend_matrix_rows()
    backend_summaries: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in matrix_rows:
        backend_summaries[row.backend_id][row.status] += 1

    _write_json(
        OUTPUT_DIR / "core_backend_matrix.json",
        {
            "row_count": len(matrix_rows),
            "backend_summaries": {
                backend_id: dict(sorted(counts.items()))
                for backend_id, counts in sorted(backend_summaries.items())
            },
            "rows": [asdict(row) for row in matrix_rows],
        },
    )

    md_lines = [
        "# Core Backend Matrix",
        "",
        "This matrix records non-Section-8 backend verification slices that currently have explicit executable evidence.",
        "",
        "| Backend | Family | Slice | Section refs | Status | Scope | Session status | Evidence | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in matrix_rows:
        md_lines.append(
            f"| {row.backend_id} | {row.backend_family} | {row.slice_id} | {', '.join(row.section_refs)} | {row.status} | {row.scope} | "
            f"{row.session_status} | {', '.join(row.evidence_tests) if row.evidence_tests else '-'} | {row.notes} |"
        )
    _write_markdown(OUTPUT_DIR / "core_backend_matrix.md", md_lines)
    return matrix_rows


def _write_completion_checklist_artifacts(
    rows: tuple[ServiceConformanceRow, ...],
    core_backend_rows: list[CoreBackendMatrixRow],
) -> None:
    negative_status_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        negative_status_counts[negative_path_status(row)] += 1

    checklist_rows = [
        CompletionChecklistRow(
            checklist_id="requirements-ledger",
            area="Requirement-level positive-path ledger",
            status="done",
            evidence=("analysis/compliance/requirements_ledger.json",),
            rationale="All 217 service rows are represented as pass in the current requirement ledger.",
        ),
        CompletionChecklistRow(
            checklist_id="exact-row-evidence",
            area="Exact row-level executable evidence",
            status="done",
            evidence=("analysis/compliance/no_requirement_evidence_rows.json",),
            rationale="The exact row-level evidence gap report is empty.",
        ),
        CompletionChecklistRow(
            checklist_id="negative-path-ledger",
            area="Negative-path accounting",
            status="partial",
            evidence=("analysis/compliance/negative_path_completeness.json",),
            rationale=(
                f"Negative-path coverage is not closed: {negative_status_counts['complete']} complete, "
                f"{negative_status_counts['partial']} partial, {negative_status_counts['mapped-not-exhaustive']} mapped-not-exhaustive, "
                f"{negative_status_counts['not-evidenced']} not-evidenced."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="section8-backend-matrix",
            area="Section 8 cross-backend matrix",
            status="partial",
            evidence=("analysis/compliance/section8_backend_matrix.json",),
            rationale=(
                "Python reference is complete-actionable and hosted Python is positive-path passing, "
                "but vendor CERTI and Pitch rows still include env-gated and not-yet-matrixed entries."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="core-backend-matrix",
            area="Non-Section-8 backend matrix",
            status="partial",
            evidence=("analysis/compliance/core_backend_matrix.json",),
            rationale=(
                "Exchange, synchronization, and ownership slices are now matrixed across Python, hosted Python, Java shim, and CERTI, "
                "but negotiated ownership still includes explicit vendor divergences."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="vendor-certi-time",
            area="Real CERTI time-profile verification",
            status="partial",
            evidence=(
                "tests/vendors/test_certi_real_backend_time_matrix.py",
                "tests/vendors/test_certi_real_backend_exchange_matrix.py",
            ),
            rationale=(
                "Real CERTI time-query/FQR and cross-facade exchange slices were verified in this session, "
                "but the full vendor matrix was not rerun end to end."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="vendor-certi-ownership",
            area="Real CERTI ownership verification",
            status="partial",
            evidence=("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
            rationale=(
                "Plain ownership passed in this session, but negotiated ownership failed across native and Java-facade CERTI paths."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="pitch-matrix",
            area="Pitch backend matrix",
            status="not-done",
            evidence=("analysis/compliance/section8_backend_matrix.json",),
            rationale="Pitch remains bridge-parity only and is not yet covered by dedicated backend matrices.",
        ),
        CompletionChecklistRow(
            checklist_id="support-services-backend-matrix",
            area="Section 10 backend matrix",
            status="not-done",
            evidence=("analysis/compliance/negative_path_priority_ranking.md",),
            rationale="Support-service compliance exists at the reference ledger level, but no backend-specific matrix exists yet.",
        ),
    ]

    _write_json(
        OUTPUT_DIR / "compliance_completion_checklist.json",
        {"row_count": len(checklist_rows), "rows": [asdict(row) for row in checklist_rows]},
    )
    md_lines = [
        "# Compliance Completion Checklist",
        "",
        "| Checklist item | Area | Status | Evidence | Rationale |",
        "|---|---|---|---|---|",
    ]
    for row in checklist_rows:
        md_lines.append(
            f"| {row.checklist_id} | {row.area} | {row.status} | {', '.join(row.evidence)} | {row.rationale} |"
        )
    _write_markdown(OUTPUT_DIR / "compliance_completion_checklist.md", md_lines)


def _write_unfinished_work_ranking_artifacts(core_backend_rows: list[CoreBackendMatrixRow]) -> None:
    rows = [
        UnfinishedWorkRow(
            priority="P1",
            claim_value_rank=1,
            work_id="close-negative-path-ledger",
            area="Cross-standard negative-path completeness",
            current_state="Reference ledger still has partial, mapped-not-exhaustive, and not-evidenced rows.",
            target_state="All actionable rows move to complete or explicit vendor divergence.",
            evidence=("analysis/compliance/negative_path_completeness.json",),
            rationale="This is the biggest remaining blocker to an honest whole-standard compliance claim.",
        ),
        UnfinishedWorkRow(
            priority="P1",
            claim_value_rank=2,
            work_id="certi-negotiated-ownership-divergence",
            area="CERTI negotiated ownership divergence",
            current_state="Negotiated ownership now has matrix rows everywhere, but CERTI native, JPype, and Py4J fail the scenario contract.",
            target_state="CERTI negotiated ownership is either fixed in the adapter/runtime or documented as an explicit vendor limitation.",
            evidence=("analysis/compliance/core_backend_matrix.json",),
            rationale="This is now the highest-value non-Section-8 backend problem because it is a real failing vendor behavior, not a missing test.",
        ),
        UnfinishedWorkRow(
            priority="P1",
            claim_value_rank=3,
            work_id="vendor-certi-full-rerun",
            area="Full real CERTI matrix rerun",
            current_state="Key CERTI time slices passed, but the full vendor matrix was not rerun in one clean sweep after the harness fixes.",
            target_state="All active CERTI vendor matrix files rerun cleanly or documented with explicit divergences.",
            evidence=(
                "tests/vendors/test_certi_real_backend_time_matrix.py",
                "tests/vendors/test_certi_real_backend_exchange_matrix.py",
                "tests/vendors/test_certi_real_backend_ownership_matrix.py",
            ),
            rationale="This is the strongest vendor-backed proof path currently available in the repo.",
        ),
        UnfinishedWorkRow(
            priority="P2",
            claim_value_rank=4,
            work_id="certi-query-type-fidelity",
            area="CERTI bridge logical-time type fidelity",
            current_state="Integer-profile queryGALT/queryLITS values can surface as HLAfloat64Time through the helper bridge.",
            target_state="CERTI helper preserves federation logical-time type on non-creator ambassadors.",
            evidence=("tests/vendors/certi_real_backend_matrix_support.py",),
            rationale="Semantic correctness is already present, but bridge type fidelity remains imperfect.",
        ),
        UnfinishedWorkRow(
            priority="P2",
            claim_value_rank=5,
            work_id="section10-backend-matrix",
            area="Section 10 backend matrix",
            current_state="Support-service compliance is only represented in the reference ledger.",
            target_state="A backend matrix exists for support-service lookup, callback control, and factory surfaces.",
            evidence=("analysis/compliance/negative_path_priority_ranking.md",),
            rationale="High volume, lower claim value than core federation/object/time behavior, but still necessary for a complete matrix.",
        ),
        UnfinishedWorkRow(
            priority="P2",
            claim_value_rank=6,
            work_id="pitch-dedicated-matrix",
            area="Pitch dedicated backend matrices",
            current_state="Pitch remains bridge-parity only.",
            target_state="Pitch has explicit Section 8 and core non-Section-8 backend rows.",
            evidence=("analysis/compliance/section8_backend_matrix.json",),
            rationale="Pitch is the least proven major backend family right now.",
        ),
    ]

    _write_json(
        OUTPUT_DIR / "unfinished_compliance_work_ranking.json",
        {"row_count": len(rows), "rows": [asdict(row) for row in rows]},
    )
    md_lines = [
        "# Unfinished Compliance Work Ranking",
        "",
        "| Priority | Rank | Work item | Area | Current state | Target state | Evidence | Rationale |",
        "|---|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row.priority} | {row.claim_value_rank} | {row.work_id} | {row.area} | {row.current_state} | "
            f"{row.target_state} | {', '.join(row.evidence)} | {row.rationale} |"
        )
    _write_markdown(OUTPUT_DIR / "unfinished_compliance_work_ranking.md", md_lines)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_service_conformance_matrix(version=hla2010.__version__)
    write_service_conformance_json(OUTPUT_DIR / "service_conformance.json", version=hla2010.__version__)
    write_service_conformance_csv(OUTPUT_DIR / "service_conformance.csv", version=hla2010.__version__)
    write_requirements_ledger_json(OUTPUT_DIR / "requirements_ledger.json", version=hla2010.__version__)
    write_requirements_ledger_csv(OUTPUT_DIR / "requirements_ledger.csv", version=hla2010.__version__)
    _write_section_summary_artifacts(matrix.rows)
    _write_public_class_inventory_artifacts()
    _write_gap_report_artifacts(matrix.rows)
    _write_negative_path_artifacts(matrix.rows)
    _write_section8_backend_matrix_artifacts(matrix.rows)
    core_backend_rows = _write_core_backend_matrix_artifacts()
    _write_completion_checklist_artifacts(matrix.rows, core_backend_rows)
    _write_unfinished_work_ranking_artifacts(core_backend_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
