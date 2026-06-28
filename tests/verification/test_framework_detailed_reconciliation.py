from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_PATH = (
    ROOT / "requirements" / "2010" / "hla1516_framework_detailed_reconciliation.csv"
)
_DISALLOWED_TRUTH_SOURCES = (
    "docs/plans/",
    "analysis/compliance/presentation_packets",
    "analysis/compliance/python_final_requirements_report.md",
    "analysis/compliance/python_boss_capability_brief.md",
)
_DOC_ONLY_ROWS = {
    "HLA1516-FW-FW_SCOPE-001",
    "HLA1516-FW-FW_PURPOSE-002",
    "HLA1516-FW-RATIONALE-015",
}


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _split_refs(refs: str) -> list[str]:
    return [item.strip() for item in refs.split(";") if item.strip()]


def _assert_reference_is_live(reference: str) -> None:
    if "::" in reference:
        file_part, test_name = reference.split("::", 1)
        path = ROOT / file_part
        assert path.exists(), f"missing evidence file for {reference}"
        text = path.read_text(encoding="utf-8")
        assert test_name in text, f"missing test anchor for {reference}"
        return

    path = ROOT / reference
    assert path.exists(), f"missing evidence artifact {reference}"


def test_framework_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 53
    statuses = Counter(row["current_status"] for row in rows)
    assert statuses == Counter({"partial": 41, "mapped": 12})
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_framework_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516-FW-FW_HLA_COMPONENTS-003"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-FW_HLA_COMPONENTS-003"]["curated_requirement_id"].startswith(
        "HLA1516-FW-001;"
    )
    assert rows["HLA1516-FW-5_1-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-5_2-DET-001"]["current_status"] == "partial"
    assert rows["HLA1516-FW-RULE_5_OWNERSHIP-009"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-BIBLIOGRAPHY-016"]["current_status"] == "mapped"
    assert (
        rows["HLA1516-FW-BIBLIOGRAPHY-016"]["current_test_id"]
        == "tests/verification/test_framework_rule_docs_v1_0.py::test_framework_docs_capture_product_set_scope_and_source_policy"
    )


def test_framework_rows_anchor_to_live_tests_or_explicit_owner_docs() -> None:
    rows = _read_rows()

    for row in rows:
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry at least one evidence reference"
        for reference in references:
            _assert_reference_is_live(reference)

        if row["packet_requirement_id"] in _DOC_ONLY_ROWS:
            continue
        assert any(reference.startswith("tests/") for reference in references), (
            f"{row['packet_requirement_id']} should anchor to live test evidence rather than docs only"
        )


def test_framework_rows_do_not_use_closeout_packets_or_plan_docs_as_truth_sources() -> None:
    for row in _read_rows():
        for forbidden in _DISALLOWED_TRUTH_SOURCES:
            assert forbidden not in row["current_test_id"], (
                f"{row['packet_requirement_id']} should not use {forbidden} as a truth source"
            )
