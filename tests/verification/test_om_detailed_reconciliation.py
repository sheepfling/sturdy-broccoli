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
    ROOT / "requirements" / "2010" / "hla1516_1_om_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_1_om_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/object_management_bounded_family.md",
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


def test_om_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 391
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 391})
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("CB_SIG", "mapped"): 42,
            ("SIG", "mapped"): 38,
            ("CB", "mapped"): 32,
            ("SVC", "mapped"): 28,
            ("EFF", "mapped"): 28,
            ("FED_CB", "mapped"): 25,
            ("CB_ORD", "mapped"): 25,
            ("ARG", "mapped"): 19,
            ("RTI_API", "mapped"): 19,
            ("EXC_API", "mapped"): 19,
            ("MOM_TRACE", "mapped"): 19,
            ("CB_ORDER", "mapped"): 17,
            ("CB_PAYLOAD", "mapped"): 17,
            ("EXC", "mapped"): 14,
            ("MOM", "mapped"): 14,
            ("PRE", "mapped"): 14,
            ("TEST", "mapped"): 14,
            ("RET", "mapped"): 5,
            ("OVW", "mapped"): 2,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_om_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-OM-OVERVIEW-006"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-OVERVIEW-007"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_3-OBJECTINSTANCENAMERESERVATIONSUCCEEDED-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_6-MULTIPLEOBJECTINSTANCENAMERESERVATIONSUCCEEDED-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_9-DISCOVEROBJECTINSTANCE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_11-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_11-REFLECTATTRIBUTEVALUES-CB_PAYLOAD-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_10-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_10-RTIAPI-002-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_19-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_19-RTIAPI-002-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_13-RECEIVEINTERACTION-CB_PAYLOAD-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_15-REMOVEOBJECTINSTANCE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_17-ATTRIBUTESINSCOPE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_20-PROVIDEATTRIBUTEVALUEUPDATE-CB_PAYLOAD-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_21-TURNUPDATESONFOROBJECTINSTANCE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_22-TURNUPDATESOFFFOROBJECTINSTANCE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_12-SENDINTERACTION-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_24-CONFIRMATTRIBUTETRANSPORTATIONTYPECHANGE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_23-REQUESTATTRIBUTETRANSPORTATIONTYPECHANGE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_26-REPORTATTRIBUTETRANSPORTATIONTYPE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_28-CONFIRMINTERACTIONTRANSPORTATIONTYPECHANGE-CB_ORDER-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_27-REQUESTINTERACTIONTRANSPORTATIONTYPECHANGE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-QUERYINTERACTIONTRANSPORTATIONTYPE-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_29-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-OM-6_30-REPORTINTERACTIONTRANSPORTATIONTYPE-CB_ORDER-001"]["current_status"] == "mapped"


def test_clause_6_object_name_argument_rows_use_direct_name_service_evidence():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    expected = {
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_time_ddm_extended.py::test_name_reservation_ddm_regions_ownership_and_time_support",
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-ARG-001": "tests/backends/test_python_backend_object_ownership_extended.py::test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
    }

    for packet_id, test_id in expected.items():
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == test_id
        assert "node-level" in row["notes"]


def test_clause_6_nearby_exception_rows_now_point_at_real_bounded_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    expected = {
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EXC-001": (
            "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_2-RTIAPI-001-EXC": (
            "test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EXC-001": (
            "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_4-RTIAPI-001-EXC": (
            "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EXC-001": (
            "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_5-RTIAPI-001-EXC": (
            "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EXC-001": (
            "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_7-RTIAPI-001-EXC": (
            "test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore",
            "SaveInProgress",
        ),
        "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EXC-001": (
            "test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore;tests/backends/test_python_backend_time_ddm_extended.py::test_strict_publication_gates_registration_update_and_interaction_sends",
            "ObjectClassNotPublished",
        ),
        "HLA1516.1-OM-6_8-RTIAPI-001-EXC": (
            "test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore;tests/backends/test_python_backend_time_ddm_extended.py::test_strict_publication_gates_registration_update_and_interaction_sends",
            "ObjectClassNotPublished",
        ),
        "HLA1516.1-OM-6_8-RTIAPI-002-EXC": (
            "test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore;tests/backends/test_python_backend_time_ddm_extended.py::test_strict_publication_gates_registration_update_and_interaction_sends",
            "ObjectInstanceNameInUse",
        ),
        "HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001": (
            "test_receive_interaction_callback_validates_payload_context_and_wraps_callback_failures",
            "FederateInternalError",
        ),
        "HLA1516.1-OM-6_12-RTIAPI-001-EXC": (
            "test_receive_interaction_callback_validates_payload_context_and_wraps_callback_failures",
            "FederateInternalError",
        ),
        "HLA1516.1-OM-6_12-RTIAPI-002-EXC": (
            "test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time",
            "InvalidLogicalTime",
        ),
    }

    for packet_id, (test_id, note_token) in expected.items():
        row = rows[packet_id]
        expected_status = "mapped"
        assert row["current_status"] == expected_status
        assert test_id in row["current_test_id"]
        assert note_token in row["notes"] or note_token in row["requirement_text"]


def test_clause_6_name_and_registration_effect_rows_now_use_direct_state_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    mapped_rows = {
        "HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-EFF-001": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-EFF-001": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_5-RESERVEMULTIPLEOBJECTINSTANCENAME-EFF-001": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_7-RELEASEMULTIPLEOBJECTINSTANCENAME-EFF-001": "test_name_reservation_and_release_effects_manage_state_without_creating_objects",
        "HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-EFF-001": "tests/backends/test_python_backend.py::test_two_python_federates_share_in_memory_rti",
    }

    for packet_id, test_id in mapped_rows.items():
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert test_id in row["current_test_id"]
        assert "Direct node-level" in row["notes"]


def test_om_rows_anchor_to_live_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry evidence references"
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)
        for reference in references:
            _assert_reference_is_live(reference)


def test_om_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())
