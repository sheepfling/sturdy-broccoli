from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def build_service_conformance_matrix(*, version: str = "0.13.0") -> dict[str, Any]:
    """Return a flat service-by-service conformance matrix dictionary.

    The canonical implementation lives in ``hla.rti1516e.conformance``; this adapter
    preserves the flatter repo-seed dictionary shape used by the current tests
    and artifact writers.
    """
    from hla.verification.repo_internal.conformance import build_service_conformance_matrix as _build

    canonical = _build(version=version)
    rows: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}
    interface_counts: dict[str, int] = {}

    for index, row in enumerate(canonical.rows, start=1):
        has_backend = (
            row.python_entry_point.startswith("PythonRTIBackend.")
            or row.python_entry_point.startswith("hla.backends.python1516e.backend.PythonRTIBackend.")
        )
        has_evidence = bool(row.evidence) or row.negative_executed_count > 0
        if row.interface == "FederateAmbassador" and row.implementation_status == "callback-helper":
            status = "callback-helper-tested" if has_evidence else "callback-helper-untested"
        elif has_backend and row.verification_status == "focused-executable-tests":
            status = "reference-implemented-tested"
        elif has_backend:
            status = "reference-implemented-untested"
        else:
            status = "planned-or-adapter-gap"

        status_counts[status] = status_counts.get(status, 0) + 1
        interface_counts[row.interface] = interface_counts.get(row.interface, 0) + 1
        rows.append(
            {
                "row_id": f"SCM-{index:04d}",
                "requirement_id": row.requirement_id,
                "interface": row.interface,
                "method": row.method_name,
                "python_name": row.python_name,
                "section": row.section_ref.replace("IEEE ", ""),
                "title": row.title,
                "service_group": row.service_group,
                "status": status,
                "source_languages": list(row.source_languages),
                "source_overload_count": row.source_overload_count,
                "declared_exceptions": list(row.declared_exceptions),
                "python_entry_point": row.python_entry_point,
                "implementation_refs": list(row.implementation_refs),
                "positive_test_refs": list(row.positive_test_refs),
                "negative_test_refs": list(row.negative_test_refs),
                "artifact_refs": list(row.artifact_refs),
                "python_backend_entrypoint": has_backend,
                "callback_helper": row.implementation_status == "callback-helper",
                "evidence": list(row.evidence),
                "negative_expectation_count": row.negative_expectation_count,
                "negative_executed_count": row.negative_executed_count,
                "negative_evidence": row.negative_executed_count > 0,
                "known_gaps": list(row.known_gaps),
            }
        )

    return {
        "summary": {
            "version": version,
            "row_count": len(rows),
            "interface_counts": dict(sorted(interface_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "source": "generated-from-package-source",
        },
        "rows": rows,
    }


def build_requirements_ledger(*, version: str = "0.13.0") -> dict[str, Any]:
    """Return a flat requirements ledger dictionary compatible with artifact writers."""
    from hla.verification.repo_internal.conformance import build_requirements_ledger as _build

    canonical = _build(version=version)
    rows: list[dict[str, Any]] = []
    for row in canonical.rows:
        rows.append(
            {
                "requirement_id": row.requirement_id,
                "interface": row.interface,
                "method": row.method_name,
                "python_name": row.python_name,
                "section": row.section_ref.replace("IEEE ", ""),
                "title": row.title,
                "service_group": row.service_group,
                "outcome": row.outcome,
                "implementation_status": row.implementation_status,
                "verification_status": row.verification_status,
                "implementation_refs": list(row.implementation_refs),
                "positive_test_refs": list(row.positive_test_refs),
                "negative_test_refs": list(row.negative_test_refs),
                "artifact_refs": list(row.artifact_refs),
                "verification_asset_id": row.verification_asset_id,
                "rationale": row.rationale,
                "evidence": list(row.evidence),
                "known_gaps": list(row.known_gaps),
            }
        )
    return {
        "summary": canonical.summary(),
        "rows": rows,
    }


def write_service_conformance_matrix_json(
    path: str | Path,
    *,
    version: str = "0.13.0",
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_service_conformance_matrix(version=version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_service_conformance_matrix_csv(
    path: str | Path,
    *,
    version: str = "0.13.0",
) -> Path:
    matrix = build_service_conformance_matrix(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_id",
        "requirement_id",
        "interface",
        "method",
        "python_name",
        "section",
        "title",
        "service_group",
        "status",
        "python_backend_entrypoint",
        "callback_helper",
        "negative_evidence",
    ]
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in matrix["rows"]:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


def write_service_conformance_summary_markdown(
    path: str | Path,
    *,
    version: str = "0.13.0",
) -> Path:
    matrix = build_service_conformance_matrix(version=version)
    summary = matrix["summary"]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Service-by-service conformance matrix v{version}",
        "",
        f"Rows: {summary['row_count']}",
        "",
        "## Interface counts",
        "",
    ]
    for key, value in summary["interface_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Status counts", ""])
    for key, value in summary["status_counts"].items():
        lines.append(f"- {key}: {value}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def write_requirements_ledger_json(
    path: str | Path,
    *,
    version: str = "0.13.0",
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_requirements_ledger(version=version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_requirements_ledger_csv(
    path: str | Path,
    *,
    version: str = "0.13.0",
) -> Path:
    ledger = build_requirements_ledger(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "requirement_id",
        "interface",
        "method",
        "python_name",
        "section",
        "title",
        "service_group",
        "outcome",
        "implementation_status",
        "verification_status",
        "implementation_refs",
        "positive_test_refs",
        "negative_test_refs",
        "artifact_refs",
        "verification_asset_id",
        "rationale",
    ]
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in ledger["rows"]:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


__all__ = [
    "build_requirements_ledger",
    "build_service_conformance_matrix",
    "write_requirements_ledger_csv",
    "write_requirements_ledger_json",
    "write_service_conformance_matrix_csv",
    "write_service_conformance_matrix_json",
    "write_service_conformance_summary_markdown",
]
