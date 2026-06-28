from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_PATH = (
    ROOT / "requirements" / "2010" / "hla1516_1_sup_detailed_reconciliation.csv"
)
_DISALLOWED_TRUTH_SOURCES = (
    "docs/plans/",
    "analysis/compliance/presentation_packets",
    "analysis/compliance/python_final_requirements_report.md",
    "analysis/compliance/python_boss_capability_brief.md",
)


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


def test_sup_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 603
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 474, "partial": 129}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("SIG", "mapped"): 86,
            ("SVC", "mapped"): 82,
            ("EFF", "mapped"): 55,
            ("ARG", "mapped"): 43,
            ("EXC", "partial"): 43,
            ("MOM", "mapped"): 43,
            ("PRE", "partial"): 43,
            ("TEST", "mapped"): 43,
            ("RTI_API", "mapped"): 43,
            ("EXC_API", "partial"): 43,
            ("MOM_TRACE", "mapped"): 43,
            ("RET", "mapped"): 31,
            ("CB", "mapped"): 4,
            ("OVW", "mapped"): 1,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_sup_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-SUP-OVERVIEW-013"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-EXC"]["current_status"] == "partial"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-SUP-10_2-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert "applicable precondition surface" in rows[
        "HLA1516.1-SUP-10_6-GETOBJECTCLASSHANDLE-PRE-001"
    ]["notes"]
    assert "invalid-name, invalid-handle, or invalid-type lookup guards" in rows[
        "HLA1516.1-SUP-10_6-GETOBJECTCLASSHANDLE-PRE-001"
    ]["notes"]
    assert "standard exception surface" in rows[
        "HLA1516.1-SUP-10_13-GETUPDATERATEVALUE-EXC-001"
    ]["notes"]
    assert "InvalidUpdateRateDesignator" in rows[
        "HLA1516.1-SUP-10_13-GETUPDATERATEVALUE-EXC-001"
    ]["notes"]
    assert "imported API-exception row remains broader" in rows[
        "HLA1516.1-SUP-10_41-RTIAPI-001-EXC"
    ]["notes"]
    assert "CallNotAllowedFromWithinCallback" in rows[
        "HLA1516.1-SUP-10_41-RTIAPI-001-EXC"
    ]["notes"]


def test_sup_handles_overview_row_has_direct_lookup_and_factory_evidence():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    row = rows["HLA1516.1-SUP-OVERVIEW-013"]

    assert row["current_status"] == "mapped"
    test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
    assert test_ids == [
        "tests/backends/test_python_backend_support_services.py::test_support_lookups_round_trip_class_handle_and_name",
        "tests/backends/test_python_backend_support_services.py::test_support_dimension_and_update_rate_helpers",
        "tests/backends/test_python_backend_support_services.py::test_support_normalizers_and_factories",
        "tests/backends/test_python_backend_support_services.py::test_support_invalid_inputs_raise_expected_errors",
    ]
    assert "stable" in row["notes"].lower()
    assert "round trips" in row["notes"].lower()


def test_sup_partial_rows_use_explicit_bounded_envelope_notes() -> None:
    rows = _read_rows()
    generic_note = (
        "Repo-native support-service tests exercise related positive or negative behavior, "
        "but this packet row is broader than the current direct evidence."
    )

    for row in rows:
        if row["current_status"] != "partial":
            continue
        assert generic_note not in row["notes"]
        if row["reconciliation_kind"] == "PRE":
            assert "applicable precondition surface" in row["notes"]
        elif row["reconciliation_kind"] == "EXC":
            assert "standard exception surface" in row["notes"]
        elif row["reconciliation_kind"] == "EXC_API":
            assert "imported API-exception row remains broader" in row["notes"]


def test_sup_rows_anchor_to_live_evidence_refs() -> None:
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry evidence references"
        for reference in references:
            _assert_reference_is_live(reference)


def test_sup_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    for row in _read_rows():
        for forbidden in _DISALLOWED_TRUTH_SOURCES:
            assert forbidden not in row["current_test_id"], (
                f"{row['packet_requirement_id']} should not use {forbidden} as a truth source"
            )
