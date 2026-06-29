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
    ROOT / "requirements" / "2010" / "hla1516_framework_detailed_reconciliation.csv"
)
_DOC_ONLY_ROWS = {
    "HLA1516-FW-FW_SCOPE-001",
    "HLA1516-FW-FW_PURPOSE-002",
    "HLA1516-FW-RATIONALE-015",
}


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_framework_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/framework_bounded_family.md",
        )
    }


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
    assert statuses == Counter({"partial": 18, "mapped": 35})
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
    assert rows["HLA1516-FW-5_2-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-5_4-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-5_3-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_3-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_4-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_2-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-6_5-DET-001"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-003"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-002"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-004"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-007"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-008"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-009"]["current_status"] == "mapped"
    assert rows["HLA1516-RULE-010"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-RULE_8_OWNERSHIP-012"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-RULE_5_OWNERSHIP-009"]["current_status"] == "mapped"
    assert rows["HLA1516-FW-BIBLIOGRAPHY-016"]["current_status"] == "mapped"
    assert (
        rows["HLA1516-FW-BIBLIOGRAPHY-016"]["current_test_id"]
        == "tests/verification/test_framework_rule_docs_v1_0.py::test_framework_docs_capture_product_set_scope_and_source_policy"
    )


def test_framework_rows_anchor_to_live_tests_or_explicit_owner_docs() -> None:
    rows = _read_rows()
    typed_rows = _typed_rows_by_id()

    for row in rows:
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry at least one evidence reference"
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)
        for reference in references:
            _assert_reference_is_live(reference)

        if row["packet_requirement_id"] in _DOC_ONLY_ROWS:
            continue
        assert any(reference.startswith("tests/") for reference in references), (
            f"{row['packet_requirement_id']} should anchor to live test evidence rather than docs only"
        )


def test_framework_rows_do_not_use_closeout_packets_or_plan_docs_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())


def test_framework_partial_rows_carry_explicit_canonical_residual_dispositions() -> None:
    for row in _read_rows():
        if row["current_status"] != "partial":
            continue
        assert row["notes"].startswith("Canonical residual disposition:"), row[
            "packet_requirement_id"
        ]


def test_framework_rule_3_rows_now_anchor_to_direct_exchange_and_declaration_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    route_test = (
        "tests/backends/test_python_backend_time_ddm_extended.py::"
        "test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions"
    )
    gate_test = (
        "tests/backends/test_python_backend_time_ddm_extended.py::"
        "test_dm_ddm_subscriptions_gate_discovery_reflect_and_receive_until_declared"
    )

    for packet_id in (
        "HLA1516-FW-5_3-DET-001",
        "HLA1516-FW-RULE_3_RTI_EXCHANGE-007",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == route_test
        assert "RTI services during" in row["notes"]

    for packet_id in (
        "HLA1516-FW-5_3-DET-002",
        "HLA1516-FW-5_3-DET-003",
        "HLA1516-RULE-003",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert gate_test in row["current_test_id"]


def test_framework_rule_8_direct_row_now_anchors_to_dynamic_ownership_runtime_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    row = rows["HLA1516-FW-RULE_8_OWNERSHIP-012"]

    assert row["current_status"] == "mapped"
    assert row["current_test_id"] == (
        "tests/backends/test_python_backend_object_ownership_extended.py::"
        "test_python_rti_negotiated_ownership_tracks_divesting_and_candidate_flows"
    )
    assert "dynamic object-attribute ownership transfer" in row["notes"]


def test_framework_rule_2_rows_now_anchor_to_direct_runtime_state_split_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    witness = (
        "tests/backends/test_python_backend_object_ownership_extended.py::"
        "test_framework_rule_2_runtime_keeps_simulation_state_in_joined_federates_and_mom_state_in_rti"
    )

    for packet_id in (
        "HLA1516-FW-5_2-DET-001",
        "HLA1516-FW-5_2-DET-002",
        "HLA1516-FW-5_2-DET-003",
        "HLA1516-FW-RULE_2_FEDERATE_STATE-006",
        "HLA1516-RULE-002",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == witness

    assert "joined federate owner" in rows["HLA1516-FW-5_2-DET-001"]["notes"]
    assert "MOM federation object attributes remain RTI-owned" in rows["HLA1516-FW-5_2-DET-002"]["notes"]
    assert "RTI owns only the management exception" in rows["HLA1516-FW-5_2-DET-003"]["notes"]
    assert "simulation object representation stays with the joined federate" in rows["HLA1516-FW-RULE_2_FEDERATE_STATE-006"]["notes"]


def test_framework_rule_4_interface_rows_now_anchor_to_direct_runtime_surface_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    witness = (
        "tests/backends/test_python_backend_object_ownership_extended.py::"
        "test_framework_rule_4_joined_federates_use_standard_hla_interface_surface"
    )

    for packet_id in (
        "HLA1516-FW-5_4-DET-001",
        "HLA1516-FW-RULE_4_INTERFACE-008",
        "HLA1516-RULE-004",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == witness

    assert "standard generated HLA service and callback entry points" in rows["HLA1516-FW-5_4-DET-001"]["notes"]
    assert "private backend-only entry path" in rows["HLA1516-FW-RULE_4_INTERFACE-008"]["notes"]


def test_framework_rule_8_capability_rows_now_anchor_to_direct_dynamic_ownership_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    witness = (
        "tests/backends/test_python_backend_object_ownership_extended.py::"
        "test_python_rti_negotiated_ownership_tracks_divesting_and_candidate_flows"
    )

    for packet_id in (
        "HLA1516-FW-6_3-DET-001",
        "HLA1516-RULE-008",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == witness

    assert "offer divestiture and acquire object-attribute ownership dynamically" in rows["HLA1516-FW-6_3-DET-001"]["notes"]
    assert "dynamic ownership transfer and acceptance" in rows["HLA1516-RULE-008"]["notes"]


def test_framework_rule_9_capability_rows_now_anchor_to_direct_update_rate_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    witness = (
        "tests/backends/test_python_backend_support_services.py::"
        "test_framework_rule_9_subscribers_can_vary_attribute_update_conditions_by_designator"
    )

    for packet_id in (
        "HLA1516-FW-6_4-DET-001",
        "HLA1516-RULE-009",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == witness

    assert "vary attribute update conditions by selecting different update-rate designators" in rows["HLA1516-FW-6_4-DET-001"]["notes"]
    assert "distinct delivery behavior" in rows["HLA1516-RULE-009"]["notes"]


def test_framework_rule_7_capability_rows_now_anchor_to_direct_exchange_runtime_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    witness = (
        "tests/backends/test_python_backend_time_ddm_extended.py::"
        "test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions"
    )

    for packet_id in (
        "HLA1516-FW-6_2-DET-001",
        "HLA1516-FW-6_2-DET-002",
        "HLA1516-RULE-007",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == witness

    assert "update attributes and a subscribing federate can reflect them" in rows["HLA1516-FW-6_2-DET-001"]["notes"]
    assert "send interactions and a subscribing federate can receive them" in rows["HLA1516-FW-6_2-DET-002"]["notes"]
    assert "update, reflection, sending, and receipt capabilities" in rows["HLA1516-RULE-007"]["notes"]


def test_framework_rule_10_time_coordination_rows_now_anchor_to_direct_runtime_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    witness = (
        "tests/time/test_mom_mim_time_v10.py::"
        "test_framework_rule_10_time_management_coordinates_federate_exchange_with_federation_time"
    )

    for packet_id in (
        "HLA1516-FW-6_5-DET-001",
        "HLA1516-RULE-010",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == witness

    assert "timestamped interaction delivery and grants occur in time order" in rows["HLA1516-FW-6_5-DET-001"]["notes"]
    assert "compatibly with coordinated federation exchange" in rows["HLA1516-RULE-010"]["notes"]
