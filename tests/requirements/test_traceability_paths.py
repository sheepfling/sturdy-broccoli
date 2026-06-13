from __future__ import annotations

from hla2010_repo_internal.traceability import (
    FORBIDDEN_STALE_PATH_PREFIXES,
    REQUIREMENTS_LEDGER_PATH,
    TRACEABILITY_MATRIX_PATH,
    load_csv_rows,
    split_refs,
    validate_active_traceability,
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
