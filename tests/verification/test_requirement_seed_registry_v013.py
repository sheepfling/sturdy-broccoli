from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.requirements import (
    load_canonical_requirement_catalog,
    survey_requirement_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = REPO_ROOT / "requirements" / "2010"


def _canonical_rows_by_id() -> dict[str, object]:
    payload = load_canonical_requirement_catalog(REFERENCE_DIR / "canonical_requirements.json")
    return {row.requirement_id: row for row in payload.rows}


def _survey_family_by_path() -> dict[str, str]:
    survey = survey_requirement_artifacts(REPO_ROOT)
    return {entry.path: entry.family for entry in survey.entries}


def test_canonical_2010_catalog_covers_representative_seed_families() -> None:
    rows = _canonical_rows_by_id()

    expected_ids = (
        "HLA1516-RULE-001",
        "HLA1516-RULE-12.1-001",
        "HLA1516-RULE-12.2-003",
        "HLA1516.1-FM-001",
        "HLA1516.1-FM-4.2-001",
        "HLA1516.1-TM-8.18-001",
        "HLA1516.1-MOM-11.5-001",
        "HLA1516.1-DM-5.2-001",
        "HLA1516.1-DM-5.8-001",
        "HLA1516.1-OM-6.8-001",
        "HLA1516.1-OM-6.19-002",
        "HLA1516.2-OC-001",
        "HLA1516.2-SYNC-001",
        "HLA1516.2-MERGE-001",
        "HLA1516.2-XML-001",
        "HLA1516.2-OC-4.2-001",
        "HLA1516.2-SYNC-4.9-001",
        "HLA1516.2-DT-4.13-054",
        "HLA1516.2-MERGE-7.0-008",
        "HLA1516.2-XML-ANNEX-005",
        "HLA1516.2-OMT-E-001",
    )

    for requirement_id in expected_ids:
        row = rows[requirement_id]
        assert row.canonical_status == "pass", requirement_id

    assert rows["HLA1516-RULE-001"].source_document == "IEEE 1516-2010"
    assert rows["HLA1516.1-FM-001"].source_document == "IEEE 1516.1-2010 (2010 edition)"
    assert rows["HLA1516.2-XML-ANNEX-005"].source_document == "IEEE 1516.2-2010 (2010 edition)"


def test_legacy_seed_artifacts_are_demoted_but_preserved_as_provenance() -> None:
    rows = _canonical_rows_by_id()
    families = _survey_family_by_path()

    assert families["requirements/2010/hla1516_framework_rules.csv"] == "import-history"
    assert families["requirements/2010/hla1516_clause_12_save_restore.csv"] == "import-history"
    assert families["requirements/2010/hla1516_1_federate_interface.csv"] == "import-history"
    assert families["requirements/2010/hla1516_1_priority_clauses_4_8_11.csv"] == "import-history"
    assert families["requirements/2010/hla1516_1_clause_5_declaration_management.csv"] == "import-history"
    assert families["requirements/2010/hla1516_1_clause_6_object_management.csv"] == "import-history"
    assert families["requirements/2010/hla1516_2_omt.csv"] == "import-history"
    assert families["requirements/2010/traceability_matrix.csv"] == "projection"

    assert "requirements/2010/hla1516_framework_rules.csv" in rows["HLA1516-RULE-001"].evidence_refs
    assert "requirements/2010/hla1516_clause_12_save_restore.csv" in rows["HLA1516-RULE-12.1-001"].evidence_refs
    assert "requirements/2010/hla1516_1_federate_interface.csv" in rows["HLA1516.1-FM-001"].evidence_refs
    assert "requirements/2010/hla1516_1_priority_clauses_4_8_11.csv" in rows["HLA1516.1-FM-4.2-001"].evidence_refs
    assert "requirements/2010/hla1516_2_omt.csv" in rows["HLA1516.2-OC-001"].evidence_refs
    assert "requirements/2010/hla1516_2_priority_omt.csv" in rows["HLA1516.2-XML-ANNEX-005"].evidence_refs


def test_requirement_registry_still_declares_the_three_standard_sources() -> None:
    registry = (REFERENCE_DIR / "requirement_id_registry.yaml").read_text(encoding="utf-8")
    assert "source_id: HLA1516" in registry
    assert "source_id: HLA1516.1" in registry
    assert "source_id: HLA1516.2" in registry
    assert "HLA1516.1-FM-001" in registry
