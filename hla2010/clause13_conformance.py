from __future__ import annotations

import ast
import csv
import json
from pathlib import Path
from typing import Any

from .verification import build_requirements_ledger, build_service_conformance_matrix


DEFAULT_MARKER_PATHS = (
    "tests/backends/test_python_backend_federation_extended.py",
    "tests/backends/test_python_backend_object_ownership_extended.py",
)

CLAUSE13_EVIDENCE_REFS = {
    "federate_markers": (
        "scripts/report_test_requirement_markers.py",
        "tests/verification/test_clause4_clause5_requirement_markers.py",
    ),
    "callbacks": (
        "tests/verification/test_spec_traceability_all_methods.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
    ),
    "language_binding": (
        "tests/verification/test_spec_traceability_all_methods.py",
        "tests/verification/test_requirements_ledger_v013.py",
        "analysis/compliance/service_conformance.json",
        "analysis/compliance/requirements_ledger.json",
    ),
    "object_models": (
        "tests/factories/test_fom_omt_parsing.py",
        "tests/mom/test_mom_catalog_validation_v012.py",
        "requirements/hla_1516_master_harmonization_index_v1_0.csv",
    ),
    "rti_services": (
        "analysis/compliance/service_conformance.json",
        "analysis/compliance/requirements_ledger.json",
        "tests/verification/test_service_conformance_matrix_v013.py",
    ),
}


def _repo_root(project_root: str | Path | None = None) -> Path:
    if project_root is None:
        return Path(__file__).resolve().parents[1]
    return Path(project_root).resolve()


def _load_master_index_capability_counts(repo_root: Path) -> dict[str, dict[str, int]]:
    path = repo_root / "requirements" / "hla_1516_master_harmonization_index_v1_0.csv"
    counts: dict[str, dict[str, int]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            capability = row["capability"]
            status = row["harmonization_status"]
            counts.setdefault(capability, {})
            counts[capability][status] = counts[capability].get(status, 0) + 1
    return counts


def _requirement_ids_from_decorator(decorator: ast.expr) -> list[str]:
    if not isinstance(decorator, ast.Call):
        return []
    func = decorator.func
    if not isinstance(func, ast.Attribute) or func.attr != "requirements":
        return []
    requirement_ids: list[str] = []
    for arg in decorator.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            requirement_id = arg.value.strip()
            if requirement_id:
                requirement_ids.append(requirement_id)
    return requirement_ids


def _load_requirement_markers(repo_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_path in DEFAULT_MARKER_PATHS:
        path = repo_root / relative_path
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue
            for decorator in node.decorator_list:
                for requirement_id in _requirement_ids_from_decorator(decorator):
                    rows.append(
                        {
                            "test_path": relative_path,
                            "test_name": node.name,
                            "requirement_id": requirement_id,
                        }
                    )
    return rows


def _marker_family_counts(marker_rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in marker_rows:
        parts = row["requirement_id"].split("-")
        if len(parts) < 3:
            continue
        family = parts[1]
        counts[family] = counts.get(family, 0) + 1
    return dict(sorted(counts.items()))


def _claim_backed(category_summaries: list[dict[str, Any]]) -> bool:
    return all(summary.get("evidence_present") for summary in category_summaries)


def build_clause13_conformance_packet(
    project_root: str | Path | None = None, *, version: str = "0.13.0"
) -> dict[str, Any]:
    repo_root = _repo_root(project_root)
    service_matrix = build_service_conformance_matrix(repo_root, version=version)
    requirements_ledger = build_requirements_ledger(repo_root, version=version)
    capability_counts = _load_master_index_capability_counts(repo_root)
    marker_rows = _load_requirement_markers(repo_root)
    marker_family_counts = _marker_family_counts(marker_rows)

    callback_rows = [
        row for row in service_matrix["rows"] if row["interface"] == "FederateAmbassador"
    ]
    callback_tested_rows = [
        row
        for row in callback_rows
        if row["status"] in {"callback-helper-tested", "reference-implemented-tested"}
    ]
    rti_rows = [row for row in service_matrix["rows"] if row["interface"] == "RTIambassador"]
    rti_tested_rows = [
        row for row in rti_rows if row["status"] == "reference-implemented-tested"
    ]
    rti_rows_with_negative_refs = [row for row in rti_rows if row["negative_test_refs"]]

    ledger_pass_rows = [row for row in requirements_ledger["rows"] if row["outcome"] == "pass"]

    federate_categories = [
        {
            "name": "standard_service_usage",
            "evidence_present": bool(marker_rows)
            and {"FM", "DM", "OM", "OWN", "TM", "DDM", "SUP"} <= set(marker_family_counts),
            "requirement_marker_count": len(marker_rows),
            "requirement_marker_families": marker_family_counts,
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["federate_markers"]),
        },
        {
            "name": "callbacks",
            "evidence_present": bool(callback_tested_rows),
            "callback_row_count": len(callback_rows),
            "callback_tested_row_count": len(callback_tested_rows),
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["callbacks"]),
        },
        {
            "name": "object_models",
            "evidence_present": all(
                capability_counts.get(capability, {}).get("mapped", 0) > 0
                for capability in ("CAP-MOM", "CAP-OMT", "CAP-XML")
            ),
            "capability_counts": {
                capability: capability_counts.get(capability, {})
                for capability in ("CAP-MOM", "CAP-OMT", "CAP-XML")
            },
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["object_models"]),
        },
        {
            "name": "language_binding",
            "evidence_present": capability_counts.get("CAP-API", {}).get("mapped", 0) > 0,
            "capability_counts": {"CAP-API": capability_counts.get("CAP-API", {})},
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["language_binding"]),
        },
    ]

    rti_categories = [
        {
            "name": "services_exceptions_callbacks",
            "evidence_present": bool(rti_tested_rows)
            and bool(rti_rows_with_negative_refs)
            and bool(callback_tested_rows),
            "rti_row_count": len(rti_rows),
            "rti_tested_row_count": len(rti_tested_rows),
            "rti_rows_with_negative_refs": len(rti_rows_with_negative_refs),
            "callback_tested_row_count": len(callback_tested_rows),
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["rti_services"]),
        },
        {
            "name": "mom_mim_behavior",
            "evidence_present": capability_counts.get("CAP-MOM", {}).get("mapped", 0) > 0,
            "capability_counts": {"CAP-MOM": capability_counts.get("CAP-MOM", {})},
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["object_models"]),
        },
        {
            "name": "language_bindings",
            "evidence_present": capability_counts.get("CAP-API", {}).get("mapped", 0) > 0,
            "capability_counts": {"CAP-API": capability_counts.get("CAP-API", {})},
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["language_binding"]),
        },
        {
            "name": "omt_fdd_handling",
            "evidence_present": capability_counts.get("CAP-OMT", {}).get("mapped", 0) > 0
            and capability_counts.get("CAP-XML", {}).get("mapped", 0) > 0,
            "capability_counts": {
                "CAP-OMT": capability_counts.get("CAP-OMT", {}),
                "CAP-XML": capability_counts.get("CAP-XML", {}),
            },
            "evidence_refs": list(CLAUSE13_EVIDENCE_REFS["object_models"]),
        },
    ]

    return {
        "version": version,
        "scope": "IEEE 1516.1-2010 Clause 13 conformance claim support packet",
        "notes": [
            "This packet does not claim certification.",
            "It packages current repo evidence so that federate and RTI conformance claims are explicitly backed by reviewable artifacts.",
        ],
        "service_conformance_summary": service_matrix["summary"],
        "requirements_ledger_summary": requirements_ledger["summary"],
        "federate_conformance": {
            "claim_backed": _claim_backed(federate_categories),
            "categories": federate_categories,
        },
        "rti_conformance": {
            "claim_backed": _claim_backed(rti_categories),
            "categories": rti_categories,
        },
        "aggregate_counts": {
            "requirements_ledger_pass_rows": len(ledger_pass_rows),
            "explicit_requirement_marker_count": len(marker_rows),
            "callback_tested_row_count": len(callback_tested_rows),
            "rti_tested_row_count": len(rti_tested_rows),
            "rti_rows_with_negative_refs": len(rti_rows_with_negative_refs),
        },
    }


def write_clause13_conformance_packet_json(
    path: str | Path, project_root: str | Path | None = None, *, version: str = "0.13.0"
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    packet = build_clause13_conformance_packet(project_root, version=version)
    target.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_clause13_conformance_packet_markdown(
    path: str | Path, project_root: str | Path | None = None, *, version: str = "0.13.0"
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    packet = build_clause13_conformance_packet(project_root, version=version)
    lines = [
        f"# Clause 13 Conformance Packet v{version}",
        "",
        "This packet does not claim certification. It packages current repo evidence so that IEEE 1516.1-2010 Clause 13 federate and RTI conformance claims are explicitly backed by reviewable artifacts.",
        "",
        "## Aggregate counts",
        "",
    ]
    for key, value in packet["aggregate_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Federate conformance", ""])
    lines.append(f"- claim_backed: {packet['federate_conformance']['claim_backed']}")
    for category in packet["federate_conformance"]["categories"]:
        lines.append(f"- {category['name']}: evidence_present={category['evidence_present']}")
    lines.extend(["", "## RTI conformance", ""])
    lines.append(f"- claim_backed: {packet['rti_conformance']['claim_backed']}")
    for category in packet["rti_conformance"]["categories"]:
        lines.append(f"- {category['name']}: evidence_present={category['evidence_present']}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


__all__ = [
    "build_clause13_conformance_packet",
    "write_clause13_conformance_packet_json",
    "write_clause13_conformance_packet_markdown",
]
