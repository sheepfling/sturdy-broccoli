from __future__ import annotations

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


def test_requirement_csv_json_surfaces_do_not_use_editionless_ieee_2010_labels() -> None:
    surface_dirs = (
        ROOT / "requirements",
        ROOT / "analysis" / "compliance",
        ROOT / "analysis" / "traceability",
    )
    violations: list[str] = []
    for directory in surface_dirs:
        for path in sorted(directory.rglob("*")):
            if path.suffix not in {".csv", ".json", ".yaml"}:
                continue
            text = path.read_text(encoding="utf-8")
            match = EDITIONLESS_STANDARD_RE.search(text)
            if match is None:
                continue
            line = text[: match.start()].count("\n") + 1
            violations.append(f"{path.relative_to(ROOT).as_posix()}:{line}: {match.group(0)}")
    assert not violations, "\n".join(violations)
