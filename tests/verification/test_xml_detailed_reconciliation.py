from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements import load_2010_reconciliation_rows

try:
    from reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources
except ModuleNotFoundError:
    from tests.reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources


ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_PATH = ROOT / "requirements" / "2010" / "hla1516_xml_detailed_reconciliation.csv"


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_xml_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md",
        )
    }


def _split_refs(refs: str) -> list[str]:
    return [item.strip() for item in refs.split(";") if item.strip()]


def test_xml_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 367
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"partial": 364, "mapped": 3}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("XML_ELEM", "partial"): 274,
            ("XML_TYPE", "partial"): 89,
            ("CLAUSE12_13_DETAIL", "partial"): 1,
            ("XML_DIF", "mapped"): 1,
            ("OMT_CLAUSE_DETAIL", "mapped"): 1,
            ("XML_SCHEMA", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_xml_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.2-XML-DIF-032"]["current_status"] == "mapped"
    assert rows["HLA1516.2-XML-SCHEMA-033"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_XSD-030"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FDD_XSD_NORMATIVE-019"]["current_status"] == "partial"
    assert rows["HLA1516.2-XML-ELEM-001"]["current_status"] == "partial"
    assert rows["HLA1516.2-XML-TYPE-001"]["current_status"] == "partial"
    assert rows["HLA1516.1-FDD_XSD_NORMATIVE-019"]["notes"].startswith(
        "Canonical residual disposition:"
    )
    assert "broader IEEE 1516.1 normative-source claim remains intentionally partial" in rows[
        "HLA1516.1-FDD_XSD_NORMATIVE-019"
    ]["notes"]
    assert "atom-level XML element row remains intentionally partial" in rows[
        "HLA1516.2-XML-ELEM-001"
    ]["notes"]
    assert "atom-level XML type row remains intentionally partial" in rows[
        "HLA1516.2-XML-TYPE-001"
    ]["notes"]


def test_xml_partial_rows_carry_explicit_canonical_residual_dispositions() -> None:
    for row in _read_rows():
        if row["current_status"] != "partial":
            continue
        assert row["notes"].startswith("Canonical residual disposition:"), row[
            "packet_requirement_id"
        ]


def test_xml_rows_preserve_typed_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)


def test_xml_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())
