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
RECONCILIATION_PATH = (
    ROOT / "requirements" / "2010" / "hla1516_1_dm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_1_dm_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md",
        )
    }


def _split_refs(refs: str) -> list[str]:
    return [item.strip() for item in refs.split(";") if item.strip()]


def _assert_reference_is_live(reference: str) -> None:
    if "=" in reference and "::" not in reference:
        _label, reference = reference.split("=", 1)

    if "::" in reference:
        file_part, test_name = reference.split("::", 1)
        path = ROOT / file_part
        assert path.exists(), f"missing evidence file for {reference}"
        text = path.read_text(encoding="utf-8")
        base_name = test_name.split("[", 1)[0]
        assert (test_name in text or base_name in text), f"missing test anchor for {reference}"
        return

    path = ROOT / reference
    if path.exists():
        return

    matches: list[str] = []
    for candidate in (ROOT / "tests").rglob("*.py"):
        if f"def {reference}(" in candidate.read_text(encoding="utf-8"):
            matches.append(str(candidate.relative_to(ROOT)))
    assert matches, f"unresolved bare evidence ref {reference}"
    assert len(matches) == 1, f"ambiguous bare evidence ref {reference}: {matches}"


def test_declaration_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 212
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 212})
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_declaration_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-DM-OVERVIEW-004"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-OVERVIEW-004"]["reconciliation_kind"] == "OVW"
    assert rows["HLA1516.1-DM-OVERVIEW-005"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001"]["reconciliation_kind"] == "FED_CB"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001-ORD"]["reconciliation_kind"] == "CB_ORD"
    assert rows["HLA1516.1-DM-5_12-FEDCB-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_12-FEDCB-001-SIG"]["reconciliation_kind"] == "CB_SIG"
    assert rows["HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-TEST-001"]["reconciliation_kind"] == "TEST"


def test_dm_rows_anchor_to_live_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry evidence references"
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)
        for reference in references:
            _assert_reference_is_live(reference)


def test_dm_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())
