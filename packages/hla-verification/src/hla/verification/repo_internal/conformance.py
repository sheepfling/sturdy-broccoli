"""Service-by-service conformance matrix generation.

This module does not claim certification.  It creates an auditable engineering
matrix from the source-derived Java/C++ API metadata, the Python backend service
handlers, callback helpers, and the verification artifacts we currently have.

Section anchors: IEEE 1516.1-2010 §4-§12, especially the per-service clauses
listed in :mod:`hla.rti1516e.spec_refs`.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from hla.verification.repo_internal.conformance_runtime import (
    focused_evidence_by_group,
    negative_executed_by_method,
    negative_path_gap,
    negative_test_ref_fallbacks,
    non_actionable_negative_exceptions,
    python_backend_handler_names,
    section_to_verification_asset,
    service_group_requirement_prefix,
    verification_asset_artifact_refs,
)
from hla.verification.repo_internal.conformance_evidence import focused_evidence_by_method

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.common import CALLBACK_METHOD_NAMES, RTI_METHOD_NAMES, lower_camel_to_snake
from hla.rti1516e.raw_api import API_METADATA
from hla.rti1516e.spec_refs import IEEE_1516_1_2010, method_reference
from hla.verification.repo_internal.mom_negative_testing import build_mom_negative_test_cases
from hla.verification.repo_internal.mom_negative_testing import default_mom_model, mom_negative_case_report


@dataclass(frozen=True)
class ServiceConformanceRow:
    requirement_id: str
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
    implementation_refs: tuple[str, ...] = field(default_factory=tuple)
    positive_test_refs: tuple[str, ...] = field(default_factory=tuple)
    negative_test_refs: tuple[str, ...] = field(default_factory=tuple)
    artifact_refs: tuple[str, ...] = field(default_factory=tuple)
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


@dataclass(frozen=True)
class RequirementLedgerRow:
    requirement_id: str
    interface: str
    method_name: str
    python_name: str
    document: str
    section: str
    section_ref: str
    title: str
    service_group: str
    outcome: str
    implementation_status: str
    verification_status: str
    implementation_refs: tuple[str, ...] = field(default_factory=tuple)
    positive_test_refs: tuple[str, ...] = field(default_factory=tuple)
    negative_test_refs: tuple[str, ...] = field(default_factory=tuple)
    artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    known_gaps: tuple[str, ...] = field(default_factory=tuple)
    verification_asset_id: str = ""
    rationale: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequirementLedger:
    version: str
    rows: tuple[RequirementLedgerRow, ...]

    def summary(self) -> dict[str, Any]:
        by_outcome: dict[str, int] = {}
        by_interface: dict[str, int] = {}
        by_section: dict[str, dict[str, int]] = {}
        for row in self.rows:
            by_outcome[row.outcome] = by_outcome.get(row.outcome, 0) + 1
            by_interface[row.interface] = by_interface.get(row.interface, 0) + 1
            section_bucket = by_section.setdefault(row.section_ref, {})
            section_bucket[row.outcome] = section_bucket.get(row.outcome, 0) + 1
        return {
            "version": self.version,
            "row_count": len(self.rows),
            "outcome_counts": dict(sorted(by_outcome.items())),
            "interface_counts": dict(sorted(by_interface.items())),
            "section_outcomes": {key: dict(sorted(value.items())) for key, value in sorted(by_section.items())},
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
    return section_to_verification_asset().get(root, "ASSET-UNMAPPED")

def _normalize_requirement_section(section: str) -> str:
    token = str(section).strip() or "unmapped"
    return token.replace("§", "").replace(".", "_").replace(" ", "_").replace("-", "_").replace("/", "_")


def _requirement_prefix(interface: str, service_group: str) -> str:
    interface_token = "RTI" if interface == "RTIambassador" else "FED"
    group_token = service_group_requirement_prefix().get(service_group, "GEN")
    return f"{interface_token}-{group_token}"


def requirement_id_for_row(row: ServiceConformanceRow) -> str:
    return (
        f"REQ-{_requirement_prefix(row.interface, row.service_group)}-"
        f"{_normalize_requirement_section(row.section)}-{row.method_name}"
    )


def _evidence_for(method: str, service_group: str) -> tuple[str, ...]:
    evidence = list(focused_evidence_by_group().get(service_group, ()))
    evidence.extend(focused_evidence_by_method().get(method, ()))
    return tuple(dict.fromkeys(evidence))


def _implementation_refs(row: ServiceConformanceRow) -> tuple[str, ...]:
    refs = [row.python_entry_point]
    if row.interface == "RTIambassador":
        refs.append("packages/hla-backend-inmemory/src/hla.backends.inmemory/backend.py")
    elif row.interface == "FederateAmbassador":
        refs.append("hla2010/ambassadors.py")
    return tuple(dict.fromkeys(refs))


def _positive_test_refs(evidence: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(item for item in evidence if item.startswith("tests/"))


def _negative_test_refs(
    method: str,
    service_group: str,
    evidence: tuple[str, ...],
    negative_executed_count: int,
) -> tuple[str, ...]:
    if negative_executed_count <= 0:
        return ()
    explicit = [item for item in evidence if item.startswith("tests/") and "negative" in item.lower()]
    if explicit:
        return tuple(dict.fromkeys(explicit))
    fallback = negative_test_ref_fallbacks().get(service_group, ())
    if fallback:
        return fallback
    return tuple(item for item in evidence if item.startswith("tests/"))


def _artifact_refs(verification_asset_id: str, positive_test_refs: tuple[str, ...], negative_test_refs: tuple[str, ...]) -> tuple[str, ...]:
    refs = list(verification_asset_artifact_refs().get(verification_asset_id, ("analysis/compliance/service_conformance.json",)))
    refs.extend(
        item
        for item in positive_test_refs + negative_test_refs
        if item.startswith("analysis/") or item.startswith("verification/")
    )
    return tuple(dict.fromkeys(refs))


def _verification_status(method: str, service_group: str, evidence: tuple[str, ...]) -> str:
    if method in focused_evidence_by_method():
        return "focused-executable-tests"
    if evidence:
        return "group-level-slice-tests"
    if service_group == "Federate Ambassador Callback":
        return "callback-helper-covered"
    return "matrix-only-planned"


def _functional_known_gaps(row: ServiceConformanceRow) -> tuple[str, ...]:
    return tuple(gap for gap in row.known_gaps if gap != negative_path_gap())


def actionable_negative_expectation_count(row: ServiceConformanceRow) -> int:
    ignored = non_actionable_negative_exceptions()
    return sum(1 for exc in row.declared_exceptions if exc not in ignored)


def _negative_path_rationale(row: ServiceConformanceRow) -> str:
    expectation_count = actionable_negative_expectation_count(row)
    if expectation_count == 0:
        return "No declared RTI exception matrix is present for this row."
    if row.negative_executed_count >= expectation_count:
        if any(exc in non_actionable_negative_exceptions() for exc in row.declared_exceptions):
            return (
                "All actionable negative-path expectations are represented by executable evidence; "
                "generic internal-failure declarations remain excluded from completeness scoring."
            )
        return "Declared negative-path expectations are fully represented by executable evidence."
    if row.negative_executed_count > 0:
        return "Some declared negative-path expectations are covered by executable tests, but coverage is not yet exhaustive."
    if negative_path_gap() in row.known_gaps:
        return "Declared exceptions are mapped from source metadata, but exhaustive negative-path execution is still incomplete."
    return "Some negative-path evidence exists, but completeness has not been explicitly recorded."


def negative_path_status(row: ServiceConformanceRow) -> str:
    expectation_count = actionable_negative_expectation_count(row)
    if expectation_count == 0:
        return "not-applicable"
    if row.negative_executed_count >= expectation_count:
        return "complete"
    if row.negative_executed_count > 0:
        return "partial"
    if negative_path_gap() in row.known_gaps:
        return "mapped-not-exhaustive"
    return "not-evidenced"


def _requirement_outcome(row: ServiceConformanceRow) -> tuple[str, str]:
    if row.implementation_status in {"adapter-or-gap", "callback-helper-gap"}:
        return "fail", "No backend-neutral implementation surface is present for this requirement."
    if row.verification_status == "matrix-only-planned":
        return "not-evidenced", "The requirement is mapped, but no executable evidence is linked yet."
    if _functional_known_gaps(row):
        return "partial", "Executable evidence exists, but known functional gaps remain for this requirement."
    if row.verification_status in {"focused-executable-tests", "callback-helper-covered"}:
        if negative_path_gap() in row.known_gaps:
            return "pass", "Executable positive-path evidence exists at the requirement level; negative-path completeness is tracked separately."
        return "pass", "Executable evidence exists at the requirement level with no recorded functional gap for this row."
    return "partial", "Only group-level or slice-level evidence exists for this requirement."


def build_service_conformance_matrix(*, version: str = "0.13.0") -> ServiceConformanceMatrix:
    """Build the current service-by-service conformance matrix."""

    mom_model = default_mom_model()
    mom_cases = build_mom_negative_test_cases(mom_model)
    mom_executable_count = sum(1 for case in mom_cases if case.execution_level == "rti-strict")
    rows: list[ServiceConformanceRow] = []

    for method in RTI_METHOD_NAMES:
        overloads = _metadata_for("RTIambassador", method)
        ref = method_reference(method)
        section = ref.section if ref else ""
        group = ref.service_group if ref and ref.service_group else "Unmapped"
        evidence = _evidence_for(method, group)
        handler = f"_svc_{method}"
        has_handler = handler in python_backend_handler_names()
        gaps: list[str] = []
        if not has_handler:
            gaps.append("No pure-Python service handler is visible; calls may be adapter-only or unsupported.")
        if overloads and _declared_exceptions(overloads):
            gaps.append(negative_path_gap())
        negative_executed_count = negative_executed_by_method().get(method, mom_executable_count if method == "sendInteraction" else 0)
        asset_id = _section_asset_id(section)
        seed_row = ServiceConformanceRow(
            requirement_id="",
            interface="RTIambassador",
            method_name=method,
            python_name=lower_camel_to_snake(method),
            document=ref.document if ref else IEEE_1516_1_2010,
            section=section,
            section_ref=f"{ref.document if ref else IEEE_1516_1_2010} §{section}" if section else "unmapped",
            title=ref.title if ref else method,
            service_group=group,
            source_languages=_source_languages(overloads),
            source_overload_count=len(overloads),
            declared_exceptions=_declared_exceptions(overloads),
            python_entry_point=(
                f"hla.backends.inmemory.backend.PythonRTIBackend.{handler}"
                if has_handler
                else "DelegatingRTIAmbassador/backend adapter"
            ),
            implementation_status="pure-python-reference-handler" if has_handler else "adapter-or-gap",
            verification_status=_verification_status(method, group, evidence),
            evidence=evidence,
            negative_expectation_count=len(_declared_exceptions(overloads)),
            negative_executed_count=negative_executed_count,
            verification_asset_id=asset_id,
            known_gaps=tuple(gaps),
        )
        requirement_id = requirement_id_for_row(seed_row)
        implementation_refs = _implementation_refs(seed_row)
        positive_test_refs = _positive_test_refs(evidence)
        negative_test_refs = _negative_test_refs(method, group, evidence, negative_executed_count)
        artifact_refs = _artifact_refs(asset_id, positive_test_refs, negative_test_refs)
        rows.append(
            ServiceConformanceRow(
                requirement_id=requirement_id,
                interface=seed_row.interface,
                method_name=seed_row.method_name,
                python_name=seed_row.python_name,
                document=seed_row.document,
                section=seed_row.section,
                section_ref=seed_row.section_ref,
                title=seed_row.title,
                service_group=seed_row.service_group,
                source_languages=seed_row.source_languages,
                source_overload_count=seed_row.source_overload_count,
                declared_exceptions=seed_row.declared_exceptions,
                python_entry_point=seed_row.python_entry_point,
                implementation_status=seed_row.implementation_status,
                verification_status=seed_row.verification_status,
                implementation_refs=implementation_refs,
                positive_test_refs=positive_test_refs,
                negative_test_refs=negative_test_refs,
                artifact_refs=artifact_refs,
                evidence=evidence,
                negative_expectation_count=seed_row.negative_expectation_count,
                negative_executed_count=seed_row.negative_executed_count,
                verification_asset_id=seed_row.verification_asset_id,
                known_gaps=seed_row.known_gaps,
            )
        )

    for method in CALLBACK_METHOD_NAMES:
        overloads = _metadata_for("FederateAmbassador", method)
        ref = method_reference(method)
        section = ref.section if ref else ""
        group = ref.service_group if ref and ref.service_group else "Federate Ambassador Callback"
        has_helper = hasattr(RecordingFederateAmbassador, method) and hasattr(RecordingFederateAmbassador, lower_camel_to_snake(method))
        callback_evidence = focused_evidence_by_method().get(
            method,
            ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
        )
        evidence = (
            "packages/hla-backend-common/src/hla.backends.common/recording.py::RecordingFederateAmbassador",
            *callback_evidence,
        )
        asset_id = _section_asset_id(section)
        seed_row = ServiceConformanceRow(
            requirement_id="",
            interface="FederateAmbassador",
            method_name=method,
            python_name=lower_camel_to_snake(method),
            document=ref.document if ref else IEEE_1516_1_2010,
            section=section,
            section_ref=f"{ref.document if ref else IEEE_1516_1_2010} §{section}" if section else "unmapped",
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
            verification_asset_id=asset_id,
            known_gaps=() if has_helper else ("No callback helper method found.",),
        )
        requirement_id = requirement_id_for_row(seed_row)
        implementation_refs = _implementation_refs(seed_row)
        positive_test_refs = _positive_test_refs(seed_row.evidence)
        negative_test_refs = ()
        artifact_refs = _artifact_refs(asset_id, positive_test_refs, negative_test_refs)
        rows.append(
            ServiceConformanceRow(
                requirement_id=requirement_id,
                interface=seed_row.interface,
                method_name=seed_row.method_name,
                python_name=seed_row.python_name,
                document=seed_row.document,
                section=seed_row.section,
                section_ref=seed_row.section_ref,
                title=seed_row.title,
                service_group=seed_row.service_group,
                source_languages=seed_row.source_languages,
                source_overload_count=seed_row.source_overload_count,
                declared_exceptions=seed_row.declared_exceptions,
                python_entry_point=seed_row.python_entry_point,
                implementation_status=seed_row.implementation_status,
                verification_status=seed_row.verification_status,
                implementation_refs=implementation_refs,
                positive_test_refs=positive_test_refs,
                negative_test_refs=negative_test_refs,
                artifact_refs=artifact_refs,
                evidence=seed_row.evidence,
                negative_expectation_count=seed_row.negative_expectation_count,
                negative_executed_count=seed_row.negative_executed_count,
                verification_asset_id=seed_row.verification_asset_id,
                known_gaps=seed_row.known_gaps,
            )
        )

    return ServiceConformanceMatrix(
        version=version,
        rows=tuple(sorted(rows, key=lambda row: (row.interface, row.service_group, row.section, row.method_name))),
        mom_negative_summary=mom_negative_case_report(mom_model),
    )


def build_requirements_ledger(*, version: str = "0.13.0") -> RequirementLedger:
    matrix = build_service_conformance_matrix(version=version)
    rows: list[RequirementLedgerRow] = []
    for row in matrix.rows:
        outcome, rationale = _requirement_outcome(row)
        rows.append(
            RequirementLedgerRow(
                requirement_id=requirement_id_for_row(row),
                interface=row.interface,
                method_name=row.method_name,
                python_name=row.python_name,
                document=row.document,
                section=row.section,
                section_ref=row.section_ref,
                title=row.title,
                service_group=row.service_group,
                outcome=outcome,
                implementation_status=row.implementation_status,
                verification_status=row.verification_status,
                implementation_refs=row.implementation_refs,
                positive_test_refs=row.positive_test_refs,
                negative_test_refs=row.negative_test_refs,
                artifact_refs=row.artifact_refs,
                evidence=row.evidence,
                known_gaps=row.known_gaps,
                verification_asset_id=row.verification_asset_id,
                rationale=rationale,
            )
        )
    return RequirementLedger(version=version, rows=tuple(rows))


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


def write_requirements_ledger_json(path: str | Path, *, version: str = "0.13.0") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_requirements_ledger(version=version).to_json(indent=2) + "\n", encoding="utf-8")
    return target


def write_requirements_ledger_csv(path: str | Path, *, version: str = "0.13.0") -> Path:
    ledger = build_requirements_ledger(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(RequirementLedgerRow.__dataclass_fields__.keys())
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in ledger.rows:
            record = row.as_dict()
            for key, value in list(record.items()):
                if isinstance(value, tuple):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


__all__ = [
    "RequirementLedger",
    "RequirementLedgerRow",
    "ServiceConformanceMatrix",
    "ServiceConformanceRow",
    "build_requirements_ledger",
    "build_service_conformance_matrix",
    "negative_path_status",
    "actionable_negative_expectation_count",
    "write_requirements_ledger_csv",
    "write_requirements_ledger_json",
    "write_service_conformance_csv",
    "write_service_conformance_json",
]
