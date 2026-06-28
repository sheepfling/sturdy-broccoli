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
RECONCILIATION_PATH = ROOT / "requirements" / "2010" / "hla1516_1_mom_detailed_reconciliation.csv"


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_1_mom_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/support_services_bounded_family.md",
        )
    }


def _split_refs(refs: str) -> list[str]:
    return [item.strip() for item in refs.split(";") if item.strip()]


def test_mom_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 320
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 320})
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("MIM_PARAM", "mapped"): 101,
            ("MIM_INT", "mapped"): 85,
            ("MIM_DT", "mapped"): 53,
            ("MIM_ATTR", "mapped"): 45,
            ("OVW", "mapped"): 7,
            ("OBJ", "mapped"): 7,
            ("RTI", "mapped"): 7,
            ("INT", "mapped"): 6,
            ("MIM_OBJ", "mapped"): 4,
            ("SRV", "mapped"): 3,
            ("TABLE", "mapped"): 1,
            ("CLAUSE12_13_DETAIL", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_mom_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-MOM-11_1-OVW-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MOM-OVERVIEW-014"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-OBJ-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-ATTR-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-INT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-PARAM-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM-DT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-MIM_NORMATIVE-020"]["current_status"] == "mapped"


def test_mom_rows_preserve_typed_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)


def test_mom_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())
