from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
    / "hla1516_2_omt_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_omt_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 60
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 58, "partial": 2}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_omt_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.2-OMT-OMT_SCOPE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.2-COMPONENTS-001"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_CONFORMANCE_LABELS-023"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_CONFORMANCE_VERIFICATION-024"]["current_status"] == "mapped"
    assert rows["HLA1516.2-NORMALIZATION-030"]["current_status"] == "partial"
    assert rows["HLA1516.2-OMT-OMT_NORM_NORMALIZATION-027"]["current_status"] == "partial"
    assert "assess_omt_conformance" in rows["HLA1516.2-NORMALIZATION-030"]["notes"]
    assert "runtime DDM normalization semantics are not yet executed" in rows["HLA1516.2-NORMALIZATION-030"]["notes"]
    assert "assess_omt_conformance" in rows["HLA1516.2-OMT-OMT_NORM_NORMALIZATION-027"]["notes"]
    assert "runtime DDM normalization semantics are not yet executed" in rows["HLA1516.2-OMT-OMT_NORM_NORMALIZATION-027"]["notes"]
    assert rows["HLA1516.2-MERGE-PRINCIPLES-031"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_NORM_MERGING_PRINCIPLES-028"]["current_status"] == "mapped"
    assert rows["HLA1516.2-OMT-OMT_DIF-029"]["current_status"] == "mapped"
    assert rows["HLA1516.2-MERGE-029"]["current_status"] == "mapped"
