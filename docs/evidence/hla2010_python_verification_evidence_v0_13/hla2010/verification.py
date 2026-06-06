"""Verification asset planning for the HLA 1516.1/1516.2 Python RTI.

This module deliberately separates implementation progress from conformance
claims.  It emits versioned, machine-readable planning artifacts that link
feature slices to specification sections, executable tests, scenarios, known
assumptions, and remaining gaps.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
import csv
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class VerificationAsset:
    """One traceable verification artifact or planned artifact."""

    asset_id: str
    asset_type: str
    title: str
    section_refs: tuple[str, ...]
    status: str
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationPlan:
    """Versioned verification plan for this development RTI."""

    version: str
    scope: str
    assets: tuple[VerificationAsset, ...] = field(default_factory=tuple)

    def by_status(self) -> dict[str, list[VerificationAsset]]:
        grouped: dict[str, list[VerificationAsset]] = {}
        for asset in self.assets:
            grouped.setdefault(asset.status, []).append(asset)
        return grouped

    def by_section(self) -> dict[str, list[VerificationAsset]]:
        grouped: dict[str, list[VerificationAsset]] = {}
        for asset in self.assets:
            for section in asset.section_refs:
                grouped.setdefault(section, []).append(asset)
        return grouped

    def coverage_summary(self) -> dict[str, Any]:
        grouped = self.by_status()
        return {
            "version": self.version,
            "scope": self.scope,
            "asset_count": len(self.assets),
            "status_counts": {status: len(items) for status, items in sorted(grouped.items())},
            "sections": sorted(self.by_section()),
            "gap_asset_ids": [asset.asset_id for asset in self.assets if asset.status in {"gap", "planned"} or asset.gaps],
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "scope": self.scope,
            "summary": self.coverage_summary(),
            "assets": [asset.as_dict() for asset in self.assets],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), indent=indent, sort_keys=True)


def build_verification_plan(version: str = "0.13.0") -> VerificationPlan:
    """Return the current honest verification plan.

    Status vocabulary:
    ``implemented-slice`` means focused tests exist for the present subset;
    ``implemented-smoke`` means scenario/parity smoke evidence exists;
    ``planned`` means the asset is identified but not yet implemented;
    ``gap`` means the behavior is known incomplete or externally blocked.
    """

    assets = (
        VerificationAsset(
            "REQ-MOM-TABLE-001",
            "requirement",
            "MOM object and interaction exposure is derived from the active MIM/FOM catalog",
            ("1516.1-2010 §11.2", "1516.1-2010 §11.3", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "hla2010/mom_catalog.py::build_mom_exposure_model",
                "tests/test_mom_catalog_validation_v012.py::test_mom_catalog_is_derived_from_standard_mim_and_exposes_validation_matrix",
            ),
            notes="The active catalog now drives MOM object attributes, interaction parameters, request/report pairs, direction, and matrix output.",
        ),
        VerificationAsset(
            "REQ-MOM-NEG-001",
            "requirement",
            "Strict MOM decoding reports and raises through generated parameterized negative-path tests",
            ("1516.1-2010 §11.4.1", "1516.1-2010 §11.5"),
            "implemented-slice",
            (
                "hla2010/mom_negative_testing.py::build_mom_negative_test_cases",
                "tests/test_mom_negative_matrix_executable_v013.py::test_generated_mom_negative_matrix_case_executes",
                "verification/mom_negative_matrix_v0_13.json",
            ),
            gaps=("Semantic HLAservice precondition-negative rows remain planned separately because they require service-specific federation setup.",),
        ),
        VerificationAsset(
            "REQ-MOM-REPORT-001",
            "requirement",
            "MOM reports use the exact parameter names declared in the active MIM catalog",
            ("1516.1-2010 §11.3", "1516.1-2010 §11.4.1", "1516.1-2010 Annex G"),
            "implemented-slice",
            ("tests/test_mom_catalog_validation_v012.py::test_mom_report_payload_uses_exact_mim_catalog_parameters",),
            gaps=("Report payload values are still local-process diagnostics for several specialized report classes.",),
        ),
        VerificationAsset(
            "REQ-MOM-SERVICE-001",
            "requirement",
            "MOM HLAservice interactions are modeled as RTI-received actions with negative-path service failure reporting",
            ("1516.1-2010 §11.3", "1516.1-2010 §11.4.1"),
            "implemented-slice",
            ("hla2010/backends/python_rti.py::_run_mom_service_action", "verification/mom_negative_matrix_v0_12.json"),
            gaps=("Not every Annex G service action has a complete semantic implementation yet.",),
        ),
        VerificationAsset(
            "REQ-SERVICE-FILE-001",
            "requirement",
            "Service-report file output contains initial and per-service records with section anchors",
            ("1516.1-2010 §11.5",),
            "implemented-slice",
            ("hla2010/service_reporting.py", "tests/test_compliance_slice_v011.py::test_mom_service_reports_to_file_and_global_report_file"),
            gaps=("The current format is JSONL for auditability; exact vendor/report-file formatting is not claimed.",),
        ),
        VerificationAsset(
            "REQ-TIME-ORDER-001",
            "requirement",
            "Timestamp-order queues respect local GALT/LITS-style lower-bound rules and DDM filtering before delivery",
            ("1516.1-2010 §8.1", "1516.1-2010 §8.13", "1516.1-2010 §8.16", "1516.1-2010 §8.18", "1516.1-2010 §9"),
            "implemented-slice",
            ("hla2010/time_management.py", "tests/test_compliance_slice_v011.py::test_ddm_region_filtering_applies_before_timestamp_order_delivery"),
            gaps=("The distributed-time algorithm remains a local-process approximation, not a proven multi-process LBTS algorithm.",),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-001",
            "requirement",
            "Save/restore coordinates with time-state and restores logical-time state",
            ("1516.1-2010 §4.16-§4.25", "1516.1-2010 §8"),
            "implemented-slice",
            ("tests/test_compliance_slice_v011.py::test_scheduled_save_waits_for_time_and_restore_reinstates_time_state",),
            gaps=("External persistent save-file interchange is not implemented.",),
        ),
        VerificationAsset(
            "SCENARIO-TARGET-RADAR-001",
            "scenario",
            "Two-federate Target/Radar simulation runs over Python RTI and Java shim profiles",
            ("1516.1-2010 §4", "1516.1-2010 §5", "1516.1-2010 §6", "1516.1-2010 §8"),
            "implemented-smoke",
            ("examples/target_radar_simulation.py", "tests/test_target_radar_scenario.py", "test_run_summary.txt"),
            gaps=("Scenario is a smoke demonstration, not a conformance test.",),
        ),
        VerificationAsset(
            "ASSET-CONFORMANCE-MATRIX-001",
            "verification-artifact",
            "Service-by-service conformance matrix covering RTIambassador services and MOM receive interactions",
            ("1516.1-2010 §4-§11", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "hla2010/conformance.py::build_service_conformance_matrix",
                "analysis/service_conformance_matrix_v0_13.json",
                "analysis/service_conformance_matrix_v0_13.csv",
                "tests/test_service_conformance_matrix_v013.py",
            ),
            gaps=("Rows identify handlers and current evidence; several handler-only rows still need service-specific behavior/exception tests.",),
        ),
        VerificationAsset(
            "ASSET-MOM-SERVICE-SEMANTIC-NEG-001",
            "planned-artifact",
            "Bespoke semantic negative-path harnesses for every MOM HLAservice action",
            ("1516.1-2010 §11.4.1", "1516.1-2010 Annex G"),
            "planned",
            ("analysis/service_conformance_matrix_v0_13.json", "verification/mom_negative_matrix_v0_13.json"),
            gaps=("The generated parameter-validation rows are executable; service-action rows still need per-service precondition setup so success paths are not misreported as negative evidence.",),
        ),
        VerificationAsset(
            "ASSET-CROSS-RTI-BRIDGE-001",
            "planned-artifact",
            "Cross-run verification against at least one real Java RTI via JPype and Py4J",
            ("1516.1-2010 Java binding", "1516.1-2010 §4-§10"),
            "gap",
            ("tests/test_optional_real_java_bridges.py",),
            gaps=("No vendor RTI, jpype1, or py4j package is available in this sandbox.",),
        ),
        VerificationAsset(
            "ASSET-NEGATIVE-MOM-MATRIX-001",
            "verification-artifact",
            "Generated MOM negative-path matrix with executable parameter-validation rows",
            ("1516.1-2010 §11.4.1", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "verification/mom_negative_matrix_v0_13.json",
                "analysis/mom_negative_matrix_v0_13.json",
                "hla2010/mom_negative_testing.py::mom_negative_case_report",
                "tests/test_mom_negative_matrix_executable_v013.py",
            ),
            gaps=("Service-action semantic negative cases remain visible as planned rows until each has a bespoke precondition harness.",),
        ),
    )
    return VerificationPlan(version=version, scope="Pure Python RTI plus Java adapter/shim compatibility layer", assets=assets)


def write_verification_assets(path: str | Path, *, version: str = "0.13.0") -> Path:
    """Write the current plan as JSON and return the output path."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_verification_plan(version).to_json(indent=2) + "\n", encoding="utf-8")
    return target


def write_traceability_csv(path: str | Path, *, version: str = "0.13.0") -> Path:
    """Write a flat section-to-asset traceability CSV."""

    plan = build_verification_plan(version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["asset_id", "asset_type", "title", "section_ref", "status", "evidence", "gaps"])
        for asset in plan.assets:
            for section in asset.section_refs:
                writer.writerow([
                    asset.asset_id,
                    asset.asset_type,
                    asset.title,
                    section,
                    asset.status,
                    "; ".join(asset.evidence),
                    "; ".join(asset.gaps),
                ])
    return target


__all__ = [
    "VerificationAsset",
    "VerificationPlan",
    "build_verification_plan",
    "write_verification_assets",
    "write_traceability_csv",
]
