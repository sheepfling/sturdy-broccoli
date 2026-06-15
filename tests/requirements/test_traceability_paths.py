from __future__ import annotations

"""Traceability tests for the IEEE/HLA 2010 editorial-edition requirement surfaces."""

import re
from pathlib import Path

from hla2010_repo_internal.requirements_source import validate_authored_requirement_row_documents
from hla2010_repo_internal.traceability import (
    FORBIDDEN_STALE_PATH_PREFIXES,
    REQUIREMENTS_LEDGER_PATH,
    TRACEABILITY_MATRIX_PATH,
    load_csv_rows,
    split_refs,
    validate_active_traceability,
)

ROOT = Path(__file__).resolve().parents[2]
EDITIONLESS_STANDARD_RE = re.compile(r"IEEE 1516(?:\.1|\.2)?-2010(?! \(2010 edition\))")
EDITIONLESS_HLA_STANDARD_RE = re.compile(r"\bHLA 1516(?:\.1|\.2)?(?:-2010)?(?! \(2010 edition\))\b")
PUBLIC_STANDARD_LABEL_PATHS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "requirements" / "README.md",
    ROOT / "docs" / "requirements_authoring_map.md",
    ROOT / "docs" / "requirements_crud.md",
    ROOT / "docs" / "requirements_edit_one_row.md",
    ROOT / "docs" / "requirements_trace_one_method.md",
    ROOT / "docs" / "requirements_traceability.md",
    ROOT / "analysis" / "compliance" / "python_final_requirements_report.md",
    ROOT / "analysis" / "compliance" / "python_boss_capability_brief.md",
    ROOT / "requirements" / "imports" / "hla_1516_requirements_codebase_packet_v1_0" / "README.md",
    ROOT
    / "requirements"
    / "imports"
    / "hla_1516_requirements_codebase_packet_v1_0"
    / "work_packet"
    / "AGENT_WORK_PACKET.md",
    ROOT
    / "requirements"
    / "imports"
    / "hla_1516_requirements_codebase_packet_v1_0"
    / "work_packet"
    / "ACCEPTANCE_CHECKLIST.md",
)
PRIMARY_REQUIREMENT_EDITORIAL_SURFACES = (
    ROOT / "analysis" / "compliance" / "requirements_matrix_2010.csv",
    ROOT / "analysis" / "compliance" / "requirements_matrix_2010.json",
    ROOT / "analysis" / "compliance" / "verification_assets.json",
    ROOT / "analysis" / "compliance" / "verification_traceability.csv",
    ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.json",
    ROOT / "docs" / "verification" / "clause13_conformance_packet.json",
    ROOT / "docs" / "verification" / "clause13_conformance_packet.md",
    ROOT / "docs" / "backend_conformance_matrix.md",
    ROOT / "docs" / "supported_subset_policy.md",
    ROOT / "docs" / "plans" / "PLN-001_hla_2010_foundation.md",
)


def test_active_traceability_refs_resolve() -> None:
    errors = validate_active_traceability()
    assert not errors, "\n".join(
        f"{error.source}:{error.row_id}:{error.field}: {error.message}: {error.ref}"
        for error in errors
    )


def test_no_stale_root_backend_paths_remain_in_active_traceability_files() -> None:
    for path in (TRACEABILITY_MATRIX_PATH, REQUIREMENTS_LEDGER_PATH):
        text = path.read_text(encoding="utf-8")
        for prefix in FORBIDDEN_STALE_PATH_PREFIXES:
            assert prefix not in text, f"{path} still contains stale prefix {prefix}"


def test_every_mapped_traceability_row_has_test_or_artifact_evidence() -> None:
    for row in load_csv_rows(TRACEABILITY_MATRIX_PATH):
        if row["status"] != "mapped":
            continue
        assert split_refs(row.get("test_refs", "")) or split_refs(row.get("artifact_refs", "")), row["requirement_id"]


def test_every_partial_traceability_row_has_supported_boundary_note() -> None:
    for row in load_csv_rows(TRACEABILITY_MATRIX_PATH):
        if row["status"] != "partial":
            continue
        assert "supported" in row.get("notes", "").casefold(), row["requirement_id"]


def test_authored_requirement_rows_use_exact_edition_qualified_source_documents() -> None:
    errors = validate_authored_requirement_row_documents()
    assert not errors, "\n".join(errors)


def test_requirement_csv_json_surfaces_do_not_use_editionless_hla_or_ieee_2010_labels() -> None:
    # Keep this scan on the authored/source-oriented requirements surfaces.
    # Generated compliance packets are covered separately by packet-specific tests
    # so this check does not fail on unrelated packet churn in a dirty workspace.
    surface_dirs = (ROOT / "requirements", ROOT / "analysis" / "traceability")
    violations: list[str] = []
    for directory in surface_dirs:
        for path in sorted(directory.rglob("*")):
            if path.suffix not in {".csv", ".json", ".yaml"}:
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in (EDITIONLESS_STANDARD_RE, EDITIONLESS_HLA_STANDARD_RE):
                for match in pattern.finditer(text):
                    line = text[: match.start()].count("\n") + 1
                    violations.append(f"{path.relative_to(ROOT).as_posix()}:{line}: {match.group(0)}")
    assert not violations, "\n".join(violations)


def test_public_standard_label_surfaces_do_not_use_editionless_hla_or_ieee_2010_labels() -> None:
    violations: list[str] = []
    for path in PUBLIC_STANDARD_LABEL_PATHS:
        text = path.read_text(encoding="utf-8")
        for pattern in (EDITIONLESS_STANDARD_RE, EDITIONLESS_HLA_STANDARD_RE):
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                violations.append(f"{path.relative_to(ROOT).as_posix()}:{line}: {match.group(0)}")
    assert not violations, "\n".join(violations)


def test_primary_requirement_editorial_surfaces_use_edition_qualified_2010_labels() -> None:
    violations: list[str] = []
    for path in PRIMARY_REQUIREMENT_EDITORIAL_SURFACES:
        text = path.read_text(encoding="utf-8")
        for pattern in (EDITIONLESS_STANDARD_RE, EDITIONLESS_HLA_STANDARD_RE):
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                violations.append(f"{path.relative_to(ROOT).as_posix()}:{line}: {match.group(0)}")
    assert not violations, "\n".join(violations)
