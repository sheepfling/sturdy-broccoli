from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / "requirements"
REFERENCE_REQUIREMENTS_DIR = REQUIREMENTS_DIR
DOCS_DIR = REPO_ROOT / "docs" / "verification"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _test_function_exists(test_id: str) -> bool:
    needle = f"def {test_id}"
    for path in (REPO_ROOT / "tests").rglob("*.py"):
        try:
            if needle in path.read_text(encoding="utf-8"):
                return True
        except UnicodeDecodeError:
            continue
    return False


def test_1516_2_priority_rows_have_traceability_entries_with_matching_status():
    priority_rows = _rows(REFERENCE_REQUIREMENTS_DIR / "hla1516_2_priority_omt.csv")
    trace_rows = {
        row["requirement_id"]: row
        for row in _rows(REQUIREMENTS_DIR / "traceability_matrix.csv")
        if row["requirement_id"].startswith("HLA1516.2-")
    }

    missing = [row["requirement_id"] for row in priority_rows if row["requirement_id"] not in trace_rows]
    assert missing == []

    for row in priority_rows:
        trace = trace_rows[row["requirement_id"]]
        assert trace["status"] == row["status"]
        assert trace["implementation_refs"]
        assert "requirements/hla1516_2_priority_omt.csv" in trace["artifact_refs"]
        if row["status"] == "mapped":
            assert row["test_id"]
            assert trace["test_refs"]


def test_1516_2_hierarchy_doc_mentions_new_omt_tranches():
    text = (DOCS_DIR / "requirements_hierarchy.md").read_text(encoding="utf-8")

    assert "HLA1516.2-SYNC-4.9-001" in text
    assert "HLA1516.2-TRANS-4.10-001" in text
    assert "HLA1516.2-URATE-4.11-001" in text
    assert "HLA1516.2-SWITCH-4.12-001" in text
    assert "HLA1516.2-DT-4.13-001" in text
    assert "HLA1516.2-NOTE-4.14-001" in text
    assert "HLA1516.2-MERGE-7.0-001" in text
    assert "HLA1516.2-XML-ANNEX-001" in text


def test_1516_2_hierarchy_doc_declares_omt_lexicon_and_conformance_boundary():
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


def test_mapped_1516_2_rows_only_reference_real_test_ids():
    priority_rows = _rows(REFERENCE_REQUIREMENTS_DIR / "hla1516_2_priority_omt.csv")

    missing: list[tuple[str, str]] = []
    for row in priority_rows:
        if row["status"] != "mapped":
            continue
        test_ids = [value.strip() for value in row["test_id"].split(";") if value.strip()]
        if not test_ids:
            continue
        for test_id in test_ids:
            if not _test_function_exists(test_id):
                missing.append((row["requirement_id"], test_id))

    assert missing == []
