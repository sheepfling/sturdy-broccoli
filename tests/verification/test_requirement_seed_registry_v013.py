from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / "requirements"
REFERENCE_DIR = REQUIREMENTS_DIR / "2010"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_requirement_seed_files_exist_and_have_seed_rows():
    files = {
        "framework": REFERENCE_DIR / "hla1516_framework_rules.csv",
        "framework_clause12": REFERENCE_DIR / "hla1516_clause_12_save_restore.csv",
        "interface": REFERENCE_DIR / "hla1516_1_federate_interface.csv",
        "priority_1516_1": REFERENCE_DIR / "hla1516_1_priority_clauses_4_8_11.csv",
        "clause5_1516_1": REFERENCE_DIR / "hla1516_1_clause_5_declaration_management.csv",
        "clause6_1516_1": REFERENCE_DIR / "hla1516_1_clause_6_object_management.csv",
        "omt": REFERENCE_DIR / "hla1516_2_omt.csv",
        "priority_1516_2": REFERENCE_DIR / "hla1516_2_priority_omt.csv",
        "traceability": REFERENCE_DIR / "traceability_matrix.csv",
    }
    for path in files.values():
        assert path.exists(), path

    framework_rows = _rows(files["framework"])
    framework_clause12_rows = _rows(files["framework_clause12"])
    interface_rows = _rows(files["interface"])
    priority_rows = _rows(files["priority_1516_1"])
    clause5_rows = _rows(files["clause5_1516_1"])
    clause6_rows = _rows(files["clause6_1516_1"])
    omt_rows = _rows(files["omt"])
    priority_omt_rows = _rows(files["priority_1516_2"])
    trace_rows = _rows(files["traceability"])

    assert any(row["requirement_id"] == "HLA1516-RULE-001" for row in framework_rows)
    assert any(row["requirement_id"] == "HLA1516-RULE-12.1-001" for row in framework_clause12_rows)
    assert any(row["requirement_id"] == "HLA1516-RULE-12.2-003" for row in framework_clause12_rows)
    assert any(row["requirement_id"] == "HLA1516.1-FM-001" for row in interface_rows)
    assert any(row["requirement_id"] == "HLA1516.1-FM-4.2-001" for row in priority_rows)
    assert any(row["requirement_id"] == "HLA1516.1-TM-8.18-001" for row in priority_rows)
    assert any(row["requirement_id"] == "HLA1516.1-MOM-11.5-001" for row in priority_rows)
    assert any(row["requirement_id"] == "HLA1516.1-DM-5.2-001" for row in clause5_rows)
    assert any(row["requirement_id"] == "HLA1516.1-DM-5.8-001" for row in clause5_rows)
    assert any(row["requirement_id"] == "HLA1516.1-OM-6.8-001" for row in clause6_rows)
    assert any(row["requirement_id"] == "HLA1516.1-OM-6.19-002" for row in clause6_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OC-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-SYNC-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-MERGE-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-XML-001" for row in omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OC-4.2-001" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-SYNC-4.9-001" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-DT-4.13-054" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-MERGE-7.0-008" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-XML-ANNEX-005" for row in priority_omt_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OMT-E-001" for row in priority_omt_rows)
    assert any(row["current_artifact_id"] == "REQ-MOM-OBSERVER-001" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516-RULE-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.1-MOM-11.5-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.2-OMT-7-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.2-SYNC-4.9-001" and row["status"] == "mapped" for row in trace_rows)
    assert any(row["requirement_id"] == "HLA1516.2-MERGE-7.0-008" and row["status"] == "mapped" for row in trace_rows)


def test_requirement_registry_declares_three_standard_sources():
    registry = (REFERENCE_DIR / "requirement_id_registry.yaml").read_text(encoding="utf-8")
    assert "source_id: HLA1516" in registry
    assert "source_id: HLA1516.1" in registry
    assert "source_id: HLA1516.2" in registry
    assert "HLA1516.1-FM-001" in registry
