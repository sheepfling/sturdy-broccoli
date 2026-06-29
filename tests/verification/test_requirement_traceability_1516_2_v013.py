from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.requirements import (
    load_canonical_requirement_catalog,
    survey_requirement_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_REQUIREMENTS_DIR = REPO_ROOT / "requirements" / "2010"
DOCS_DIR = REPO_ROOT / "docs" / "verification"


def _canonical_rows_by_id() -> dict[str, object]:
    payload = load_canonical_requirement_catalog(REFERENCE_REQUIREMENTS_DIR / "canonical_requirements.json")
    return {row.requirement_id: row for row in payload.rows}


def test_1516_2_priority_rows_are_closed_in_canonical_catalog_with_preserved_seed_provenance() -> None:
    rows = _canonical_rows_by_id()

    expected_ids = (
        "HLA1516.2-OC-4.2-001",
        "HLA1516.2-SYNC-4.9-001",
        "HLA1516.2-DT-4.13-054",
        "HLA1516.2-MERGE-7.0-008",
        "HLA1516.2-XML-ANNEX-005",
        "HLA1516.2-OMT-E-001",
    )

    for requirement_id in expected_ids:
        row = rows[requirement_id]
        assert row.canonical_status == "pass"
        assert row.source_document == "IEEE 1516.2-2010 (2010 edition)"
        assert "requirements/2010/hla1516_2_priority_omt.csv" in row.evidence_refs
        assert any(ref.startswith("tests/") for ref in row.evidence_refs)


def test_1516_2_priority_omt_seed_artifact_is_not_a_primary_truth_surface() -> None:
    families = {entry.path: entry.family for entry in survey_requirement_artifacts(REPO_ROOT).entries}
    assert families["requirements/2010/hla1516_2_priority_omt.csv"] in {"import-history", "imported-requirement"}
    assert families["requirements/2010/traceability_matrix.csv"] == "projection"


def test_1516_2_hierarchy_doc_mentions_new_omt_tranches() -> None:
    text = (DOCS_DIR / "requirements_hierarchy.md").read_text(encoding="utf-8")

    assert "HLA1516.2-SYNC-4.9-001" in text
    assert "HLA1516.2-TRANS-4.10-001" in text
    assert "HLA1516.2-URATE-4.11-001" in text
    assert "HLA1516.2-SWITCH-4.12-001" in text
    assert "HLA1516.2-DT-4.13-001" in text
    assert "HLA1516.2-NOTE-4.14-001" in text
    assert "HLA1516.2-MERGE-7.0-001" in text
    assert "HLA1516.2-XML-ANNEX-001" in text


def test_1516_2_hierarchy_doc_declares_omt_lexicon_and_conformance_boundary() -> None:
    text = (DOCS_DIR / "requirements_hierarchy.md").read_text(encoding="utf-8")

    assert "## OMT Lexicon" in text
    assert "`FOM module`" in text
    assert "`SOM module`" in text
    assert "`MIM`" in text
    assert "`FDD`" in text
    assert "## Conformance Claim Boundary" in text
    assert "does not claim full IEEE 1516.2-2010 (2010 edition) conformance" in text
    assert "`mapped` requirement rows identify the implemented and executable OMT subset only" in text
    assert "`planned` requirement rows identify unimplemented" in text
