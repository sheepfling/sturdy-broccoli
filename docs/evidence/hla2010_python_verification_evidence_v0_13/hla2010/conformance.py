"""Service-by-service conformance matrix generation.

This module does not claim certification.  It creates an auditable engineering
matrix from the source-derived Java/C++ API metadata, the Python backend service
handlers, callback helpers, and the verification artifacts we currently have.

Section anchors: IEEE 1516.1-2010 §4-§12, especially the per-service clauses
listed in :mod:`hla.spec.refs`.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .raw_api import API_METADATA
from .spec_refs import method_reference
from .backends.base import CALLBACK_METHOD_NAMES, RTI_METHOD_NAMES, lower_camel_to_snake
from .backends.python_rti import PythonRTIBackend
from .ambassadors import RecordingFederateAmbassador
from .testing.mom_negative import generate_mom_negative_cases, generated_mom_negative_case_summary


_FOCUSED_EVIDENCE_BY_GROUP: dict[str, tuple[str, ...]] = {
    "Federation Management": (
        "tests/test_python_rti_backend.py",
        "tests/test_startup_sync_fom_java_translation_v09.py",
        "tests/test_compliance_slice_v011.py",
    ),
    "Declaration Management": (
        "tests/test_target_radar_scenario.py",
        "tests/test_python_rti_backend.py",
    ),
    "Object Management": (
        "tests/test_target_radar_scenario.py",
        "tests/test_compliance_slice_v011.py",
        "tests/test_mom_mim_time_v10.py",
    ),
    "Ownership Management": (
        "tests/test_python_rti_extended_services.py",
    ),
    "Time Management": (
        "tests/test_mom_mim_time_v10.py",
        "tests/test_mom_mim_and_time_semantics_v010.py",
        "tests/test_compliance_slice_v011.py",
    ),
    "Data Distribution Management": (
        "tests/test_compliance_slice_v011.py",
        "tests/test_python_rti_extended_services.py",
    ),
    "Support Services": (
        "tests/test_fom_time_factories.py",
        "tests/test_spec_traceability_all_methods.py",
    ),
    "Programming Language Mappings": (
        "tests/test_fom_time_factories.py",
        "tests/test_spec_traceability_all_methods.py",
    ),
}

_FOCUSED_EVIDENCE_BY_METHOD: dict[str, tuple[str, ...]] = {
    "connect": ("tests/test_startup_sync_fom_java_translation_v09.py",),
    "createFederationExecution": ("tests/test_fom_time_factories.py", "tests/test_startup_sync_fom_java_translation_v09.py"),
    "joinFederationExecution": ("tests/test_startup_sync_fom_java_translation_v09.py",),
    "registerFederationSynchronizationPoint": ("tests/test_startup_sync_fom_java_translation_v09.py",),
    "synchronizationPointAchieved": ("tests/test_startup_sync_fom_java_translation_v09.py",),
    "federationSynchronized": ("tests/test_startup_sync_fom_java_translation_v09.py",),
    "enableTimeRegulation": ("tests/test_mom_mim_time_v10.py", "tests/test_compliance_slice_v011.py"),
    "timeAdvanceRequest": ("tests/test_mom_mim_time_v10.py", "tests/test_compliance_slice_v011.py"),
    "timeAdvanceRequestAvailable": ("tests/test_mom_mim_time_v10.py",),
    "nextMessageRequest": ("tests/test_mom_mim_time_v10.py",),
    "flushQueueRequest": ("tests/test_mom_mim_time_v10.py",),
    "queryGALT": ("tests/test_mom_mim_time_v10.py", "tests/test_compliance_slice_v011.py"),
    "queryLITS": ("tests/test_mom_mim_time_v10.py", "tests/test_compliance_slice_v011.py"),
    "sendInteraction": ("tests/test_compliance_slice_v011.py", "tests/test_target_radar_scenario.py", "tests/test_mom_negative_matrix_v013.py"),
    "updateAttributeValues": ("tests/test_target_radar_scenario.py", "tests/test_compliance_slice_v011.py"),
    "requestAttributeValueUpdate": ("tests/test_target_radar_scenario.py", "tests/test_mom_mim_time_v10.py"),
}

_SECTION_TO_VERIFICATION_ASSET: dict[str, str] = {
    "4": "ASSET-FEDERATION-MGMT-STARTUP-SYNC",
    "5": "ASSET-DECLARATION-MGMT-SMOKE",
    "6": "ASSET-OBJECT-MGMT-TARGET-RADAR",
    "7": "ASSET-OWNERSHIP-MGMT-REFERENCE-SUBSET",
    "8": "ASSET-TIME-MGMT-ORDERING",
    "9": "ASSET-DDM-REGION-TIME-FILTERING",
    "10": "ASSET-SUPPORT-SERVICES-HANDLE-FACTORIES",
    "11": "ASSET-MOM-MIM-MATRIX",
    "12": "ASSET-LANGUAGE-BINDING-HANDLE-ENCODING",
}


@dataclass(frozen=True)
class ServiceConformanceRow:
    interface: str
    method_name: str
    python_name: str
    document: str
    section: str
    section_ref: str
    title: str
    service_group: str
    source_languages: tuple[str, ...]
    source_overload_count: int
    declared_exceptions: tuple[str, ...]
    python_entry_point: str
    implementation_status: str
    verification_status: str
    evidence: tuple[str, ...] = field(default_factory=tuple)
    negative_expectation_count: int = 0
    negative_executed_count: int = 0
    verification_asset_id: str = ""
    known_gaps: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ServiceConformanceMatrix:
    version: str
    rows: tuple[ServiceConformanceRow, ...]
    mom_negative_summary: Mapping[str, Any]

    def summary(self) -> dict[str, Any]:
        by_interface: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_verification: dict[str, int] = {}
        by_group: dict[str, int] = {}
        gap_rows = 0
        for row in self.rows:
            by_interface[row.interface] = by_interface.get(row.interface, 0) + 1
            by_status[row.implementation_status] = by_status.get(row.implementation_status, 0) + 1
            by_verification[row.verification_status] = by_verification.get(row.verification_status, 0) + 1
            by_group[row.service_group] = by_group.get(row.service_group, 0) + 1
            if row.known_gaps:
                gap_rows += 1
        return {
            "version": self.version,
            "row_count": len(self.rows),
            "by_interface": dict(sorted(by_interface.items())),
            "by_implementation_status": dict(sorted(by_status.items())),
            "by_verification_status": dict(sorted(by_verification.items())),
            "by_service_group": dict(sorted(by_group.items())),
            "rows_with_known_gaps": gap_rows,
            "mom_negative_summary": dict(self.mom_negative_summary),
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(
            {
                "summary": self.summary(),
                "rows": [row.as_dict() for row in self.rows],
            },
            indent=indent,
            sort_keys=True,
        )


def _metadata_for(interface: str, method: str) -> tuple[Mapping[str, Any], ...]:
    return tuple(API_METADATA.get(interface, {}).get(method, ()))


def _source_languages(overloads: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(sorted({str(item.get("language")) for item in overloads if item.get("language")}))


def _declared_exceptions(overloads: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    exceptions: set[str] = set()
    for item in overloads:
        exceptions.update(str(exc) for exc in item.get("throws", ()) if exc)
    return tuple(sorted(exceptions))


def _section_asset_id(section: str) -> str:
    root = str(section).split(".", 1)[0]
    return _SECTION_TO_VERIFICATION_ASSET.get(root, "ASSET-UNMAPPED")


def _evidence_for(method: str, service_group: str) -> tuple[str, ...]:
    evidence = list(_FOCUSED_EVIDENCE_BY_GROUP.get(service_group, ()))
    evidence.extend(_FOCUSED_EVIDENCE_BY_METHOD.get(method, ()))
    return tuple(dict.fromkeys(evidence))


def _verification_status(method: str, service_group: str, evidence: tuple[str, ...]) -> str:
    if method in _FOCUSED_EVIDENCE_BY_METHOD:
        return "focused-executable-tests"
    if evidence:
        return "group-level-slice-tests"
    if service_group == "Federate Ambassador Callback":
        return "callback-helper-covered"
    return "matrix-only-planned"


def build_service_conformance_matrix(*, version: str = "0.13.0") -> ServiceConformanceMatrix:
    """Build the current service-by-service conformance matrix."""

    mom_cases = generate_mom_negative_cases()
    mom_executable_count = sum(1 for case in mom_cases if case.execution_level == "rti-strict")
    rows: list[ServiceConformanceRow] = []

    for method in RTI_METHOD_NAMES:
        overloads = _metadata_for("RTIambassador", method)
        ref = method_reference(method)
        section = ref.section if ref else ""
        group = ref.service_group if ref and ref.service_group else "Unmapped"
        evidence = _evidence_for(method, group)
        handler = f"_svc_{method}"
        has_handler = hasattr(PythonRTIBackend, handler)
        gaps: list[str] = []
        if not has_handler:
            gaps.append("No pure-Python service handler is visible; calls may be adapter-only or unsupported.")
        if overloads and _declared_exceptions(overloads):
            gaps.append("Declared exception matrix is identified from source metadata; exhaustive negative execution remains incomplete.")
        rows.append(
            ServiceConformanceRow(
                interface="RTIambassador",
                method_name=method,
                python_name=lower_camel_to_snake(method),
                document=ref.document if ref else "IEEE 1516.1-2010",
                section=section,
                section_ref=f"IEEE 1516.1-2010 §{section}" if section else "unmapped",
                title=ref.title if ref else method,
                service_group=group,
                source_languages=_source_languages(overloads),
                source_overload_count=len(overloads),
                declared_exceptions=_declared_exceptions(overloads),
                python_entry_point=f"PythonRTIBackend.{handler}" if has_handler else "DelegatingRTIAmbassador/backend adapter",
                implementation_status="pure-python-reference-handler" if has_handler else "adapter-or-gap",
                verification_status=_verification_status(method, group, evidence),
                evidence=evidence,
                negative_expectation_count=len(_declared_exceptions(overloads)),
                negative_executed_count=mom_executable_count if method == "sendInteraction" else 0,
                verification_asset_id=_section_asset_id(section),
                known_gaps=tuple(gaps),
            )
        )

    for method in CALLBACK_METHOD_NAMES:
        overloads = _metadata_for("FederateAmbassador", method)
        ref = method_reference(method)
        section = ref.section if ref else ""
        group = ref.service_group if ref and ref.service_group else "Federate Ambassador Callback"
        has_helper = hasattr(RecordingFederateAmbassador, method) and hasattr(RecordingFederateAmbassador, lower_camel_to_snake(method))
        evidence = ("hla2010/ambassadors.py::RecordingFederateAmbassador", "tests/test_spec_traceability_and_extended_python_rti.py")
        rows.append(
            ServiceConformanceRow(
                interface="FederateAmbassador",
                method_name=method,
                python_name=lower_camel_to_snake(method),
                document=ref.document if ref else "IEEE 1516.1-2010",
                section=section,
                section_ref=f"IEEE 1516.1-2010 §{section}" if section else "unmapped",
                title=ref.title if ref else method,
                service_group=group,
                source_languages=_source_languages(overloads),
                source_overload_count=len(overloads),
                declared_exceptions=_declared_exceptions(overloads),
                python_entry_point="RecordingFederateAmbassador callback + snake_case alias" if has_helper else "callback helper missing",
                implementation_status="callback-helper" if has_helper else "callback-helper-gap",
                verification_status="callback-helper-covered" if has_helper else "matrix-only-planned",
                evidence=evidence if has_helper else (),
                negative_expectation_count=0,
                negative_executed_count=0,
                verification_asset_id=_section_asset_id(section),
                known_gaps=() if has_helper else ("No callback helper method found.",),
            )
        )

    return ServiceConformanceMatrix(
        version=version,
        rows=tuple(sorted(rows, key=lambda row: (row.interface, row.service_group, row.section, row.method_name))),
        mom_negative_summary=generated_mom_negative_case_summary(mom_cases),
    )


def write_service_conformance_json(path: str | Path, *, version: str = "0.13.0") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_service_conformance_matrix(version=version).to_json(indent=2) + "\n", encoding="utf-8")
    return target


def write_service_conformance_csv(path: str | Path, *, version: str = "0.13.0") -> Path:
    matrix = build_service_conformance_matrix(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ServiceConformanceRow.__dataclass_fields__.keys())
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in matrix.rows:
            record = row.as_dict()
            for key, value in list(record.items()):
                if isinstance(value, tuple):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


__all__ = [
    "ServiceConformanceMatrix",
    "ServiceConformanceRow",
    "build_service_conformance_matrix",
    "write_service_conformance_csv",
    "write_service_conformance_json",
]
