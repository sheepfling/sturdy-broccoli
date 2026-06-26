from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
XML_LEDGER = ROOT / "requirements/2010/hla1516_xml_detailed_reconciliation.csv"
OMT_LEDGER = ROOT / "requirements/2010/hla1516_2_omt_detailed_reconciliation.csv"
BOUNDARY_DOC = ROOT / "docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md"
FRONT_DOOR_DOC = ROOT / "docs/requirements/ieee-1516-2010/README.md"
SOURCE_README = ROOT / "requirements/2010/README.md"
HIERARCHY_DOC = ROOT / "docs/verification/requirements_hierarchy.md"


def test_xml_partial_tail_current_shape_is_stable() -> None:
    rows = list(csv.DictReader(XML_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 364
    assert Counter(row["reconciliation_kind"] for row in partial_rows) == {
        "XML_ELEM": 274,
        "XML_TYPE": 89,
        "CLAUSE12_13_DETAIL": 1,
    }


def test_omt_partial_tail_is_only_annex_b_normalization() -> None:
    rows = list(csv.DictReader(OMT_LEDGER.open(newline="", encoding="utf-8")))
    partial_rows = [row for row in rows if row["current_status"] == "partial"]

    assert len(partial_rows) == 2
    assert Counter(row["implementation_area"] for row in partial_rows) == {
        "omt.normalization": 1,
        "ddm/normalization": 1,
    }


def test_omt_xml_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "2010 OMT/XML Bounded Family" in text
    assert "`364 partial`" in text
    assert "`274 XML_ELEM`" in text
    assert "`89 XML_TYPE`" in text
    assert "`1 CLAUSE12_13_DETAIL`" in text
    assert "`58 mapped`" in text
    assert "`2 partial`" in text


def test_omt_and_xml_owner_surfaces_are_split_in_front_doors() -> None:
    front_door = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    source_readme = SOURCE_README.read_text(encoding="utf-8")
    hierarchy = HIERARCHY_DOC.read_text(encoding="utf-8")

    for text in (front_door, source_readme, hierarchy):
        assert "OMT family" in text
        assert "OMT clause-detail and OMT/XML bridge" in text
        assert "XML family" in text

    assert "hla1516_2_omt_detailed_reconciliation.csv" in front_door
    assert "hla1516_2_omt_xml_detailed_reconciliation.csv" in front_door
    assert "hla1516_xml_detailed_reconciliation.csv" in front_door
    assert "bounded `partial` rows" in (ROOT / "requirements/README.md").read_text(encoding="utf-8")
