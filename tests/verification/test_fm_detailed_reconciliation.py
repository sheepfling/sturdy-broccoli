from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_PATH = (
    ROOT / "requirements" / "2010" / "hla1516_1_fm_detailed_reconciliation.csv"
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


def test_fm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 632
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 628, "partial": 4}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_fm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-FM-4_2-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_2-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_2-ARG-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_5-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_11-ARG-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_15-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_16-ARG-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_20-ARG-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_25-ARG-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_32-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-CB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-EFF-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-EXC-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_9-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_9-ARG-004"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_10-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_12-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_13-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_15-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_15-ARG-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_17-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_20-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_23-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_25-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_26-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_27-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_29-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_32-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_10-EFF-004"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_16-EFF-002"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_16-RTIAPI-002-EFF"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-OVERVIEW-001"]["current_status"] == "partial"


def test_fm_connection_lost_rows_point_to_direct_runtime_loss_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    direct_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_force_federate_loss_delivers_connection_lost_and_clears_execution_membership"
    )

    for packet_id in (
        "HLA1516.1-FM-4_4-001",
        "HLA1516.1-FM-4_4-ARG-001",
        "HLA1516.1-FM-4_4-FEDCB-001",
        "HLA1516.1-FM-4_4-MOM-001",
        "HLA1516.1-FM-4_4-SVC-001",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == direct_test
        assert row["notes"].startswith("Direct ")

    effect_row = rows["HLA1516.1-FM-4_4-EFF-001"]
    assert effect_row["current_status"] == "mapped"
    assert effect_row["current_test_id"] == direct_test
    assert "final disconnected not-connected state" in effect_row["notes"]


def test_fm_no_remaining_executable_semantic_partials() -> None:
    rows = _read_rows()
    executable_partial_ids = {
        row["packet_requirement_id"]
        for row in rows
        if row["current_status"] == "partial"
        and row["reconciliation_kind"] not in {"ARG", "OVW"}
    }
    assert executable_partial_ids == set()


def test_fm_new_argument_rows_point_to_direct_runtime_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-FM-4_2-ARG-001"]["current_test_id"] == (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_connect_create_and_join_apply_positive_lifecycle_effects"
    )
    assert rows["HLA1516.1-FM-4_2-ARG-002"]["current_test_id"] == (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_connect_create_and_join_apply_positive_lifecycle_effects"
    )
    assert rows["HLA1516.1-FM-4_9-ARG-001"]["current_test_id"] == (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_join_federation_execution_generates_unique_name_when_omitted"
    )
    assert rows["HLA1516.1-FM-4_10-ARG-001"]["current_test_id"].endswith(
        "test_resign_unconditionally_divests_owned_attributes_before_membership_teardown"
    )
    assert rows["HLA1516.1-FM-4_15-ARG-002"]["current_test_id"] == (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_synchronization_lifecycle_states_are_visible_in_mom_summary"
    )


def test_fm_remaining_create_time_argument_partial_is_explicitly_narrowed() -> None:
    row = {
        candidate["packet_requirement_id"]: candidate for candidate in _read_rows()
    }["HLA1516.1-FM-4_5-ARG-004"]

    assert row["current_status"] == "partial"
    assert (
        "test_create_federation_execution_accepts_explicit_logical_time_implementation"
        in row["current_test_id"]
    )
    assert "overclaims an unconditional omitted-argument fallback to HLAfloat64Time" in row["notes"]


def test_fm_callback_order_rows_use_direct_callback_model_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    sync_model_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_synchronization_callbacks_respect_callback_model_for_registration_announcement_and_completion"
    )
    save_model_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_save_callbacks_respect_callback_model_for_initiation_outcomes_and_status"
    )
    restore_model_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_restore_callbacks_respect_callback_model_for_request_progress_outcomes_and_status"
    )

    for packet_id in (
        "HLA1516.1-FM-4_12-FEDCB-001-ORD",
        "HLA1516.1-FM-4_12-FEDCB-001-ORD-DUP02",
        "HLA1516.1-FM-4_13-FEDCB-001-ORD",
        "HLA1516.1-FM-4_15-FEDCB-001-ORD",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == sync_model_test
        assert "queued HLA_EVOKED delivery against immediate HLA_IMMEDIATE delivery" in row["notes"]

    for packet_id in (
        "HLA1516.1-FM-4_17-FEDCB-001-ORD",
        "HLA1516.1-FM-4_17-FEDCB-002-ORD",
        "HLA1516.1-FM-4_20-FEDCB-001-ORD",
        "HLA1516.1-FM-4_20-FEDCB-001-ORD-DUP02",
        "HLA1516.1-FM-4_23-FEDCB-001-ORD",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == save_model_test
        assert "queued HLA_EVOKED delivery against immediate HLA_IMMEDIATE delivery" in row["notes"]

    for packet_id in (
        "HLA1516.1-FM-4_25-FEDCB-001-ORD",
        "HLA1516.1-FM-4_25-FEDCB-001-ORD-DUP02",
        "HLA1516.1-FM-4_26-FEDCB-001-ORD",
        "HLA1516.1-FM-4_27-FEDCB-001-ORD",
        "HLA1516.1-FM-4_29-FEDCB-001-ORD",
        "HLA1516.1-FM-4_29-FEDCB-001-ORD-DUP02",
        "HLA1516.1-FM-4_32-FEDCB-001-ORD",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == restore_model_test
        assert "queued HLA_EVOKED delivery against immediate HLA_IMMEDIATE delivery" in row["notes"]


def test_fm_connection_lost_precondition_and_callback_model_rows_use_direct_backend_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    model_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_force_federate_loss_requires_joined_live_victim_and_honors_callback_model"
    )

    for packet_id in (
        "HLA1516.1-FM-4_4-CB-001",
        "HLA1516.1-FM-4_4-FEDCB-001-ORD",
        "HLA1516.1-FM-4_4-PRE-001",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        if packet_id == "HLA1516.1-FM-4_4-CB-001":
            assert row["current_test_id"] == (
                model_test
                + ";tests/verification/test_spec_traceability_all_methods.py::"
                "test_all_generated_ambassador_methods_are_section_mapped"
            )
        else:
            assert row["current_test_id"] == model_test
        assert row["notes"].startswith("Direct ")


def test_fm_overview_rows_anchor_to_owner_surface_plus_live_evidence() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    lifecycle_row = rows["HLA1516.1-FM-OVERVIEW-001"]
    assert lifecycle_row["current_status"] == "partial"
    lifecycle_refs = {item.strip() for item in lifecycle_row["current_test_id"].split(";") if item.strip()}
    assert "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md" in lifecycle_refs
    assert "requirements/2010/hla1516_framework_detailed_reconciliation.csv" in lifecycle_refs
    assert (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_connect_create_and_join_apply_positive_lifecycle_effects"
    ) in lifecycle_refs
    assert (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_disconnect_requires_resign_and_marks_backend_not_connected"
    ) in lifecycle_refs
    assert (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_force_federate_loss_delivers_connection_lost_and_clears_execution_membership"
    ) in lifecycle_refs
    assert "lost-federate disconnected-state teardown" in lifecycle_row["notes"]

    modules_row = rows["HLA1516.1-FM-OVERVIEW-002"]
    assert modules_row["current_status"] == "partial"
    module_refs = {item.strip() for item in modules_row["current_test_id"].split(";") if item.strip()}
    assert "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md" in module_refs
    assert "requirements/2010/hla1516_framework_detailed_reconciliation.csv" in module_refs
    assert (
        "tests/factories/test_fom_omt_parsing.py::"
        "test_merge_with_standard_mim_preserves_standard_mom_definitions_and_catalog_metadata"
    ) in module_refs
    assert "direct FOM/MIM witnesses prove active FDD assembly" in modules_row["notes"]

    lost_row = rows["HLA1516.1-FM-OVERVIEW-003"]
    assert lost_row["current_status"] == "partial"
    lost_refs = {item.strip() for item in lost_row["current_test_id"].split(";") if item.strip()}
    assert "docs/requirements/ieee-1516-2010/federation_management_bounded_family.md" in lost_refs
    assert "requirements/2010/hla1516_framework_detailed_reconciliation.csv" in lost_refs
    assert (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_force_federate_loss_delivers_connection_lost_and_clears_execution_membership"
    ) in lost_refs
    assert (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_force_federate_loss_requires_joined_live_victim_and_honors_callback_model"
    ) in lost_refs
    assert "not every framework-level lost-federate consequence is isolated" in lost_row["notes"]


def test_fm_list_and_report_exception_and_mom_rows_use_direct_backend_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    callback_failure_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_connection_lost_and_report_federation_executions_wrap_callback_failures_as_federate_internal_error"
    )
    mom_reporting_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_list_federation_executions_is_observable_through_mom_service_invocation_reporting"
    )

    assert rows["HLA1516.1-FM-4_4-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-EXC-001"]["current_test_id"] == callback_failure_test
    assert rows["HLA1516.1-FM-4_4-EXC-001"]["notes"].startswith("Direct ")

    assert rows["HLA1516.1-FM-4_8-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-EXC-001"]["current_test_id"] == callback_failure_test
    assert rows["HLA1516.1-FM-4_8-EXC-001"]["notes"].startswith("Direct ")

    assert rows["HLA1516.1-FM-4_7-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001-MOM"]["current_test_id"] == mom_reporting_test
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001-MOM"]["notes"].startswith("Direct ")


def test_fm_resign_and_scheduled_save_effect_rows_use_direct_backend_witnesses() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    resign_cancel_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_resign_canceling_directives_clear_pending_acquisition_requests"
    )
    save_replace_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_request_federation_save_latest_scheduled_request_supersedes_prior_requested_save"
    )

    assert rows["HLA1516.1-FM-4_10-EFF-004"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_10-EFF-004"]["current_test_id"] == resign_cancel_test
    assert rows["HLA1516.1-FM-4_10-EFF-004"]["notes"].startswith("Direct ")

    for packet_id in (
        "HLA1516.1-FM-4_16-EFF-002",
        "HLA1516.1-FM-4_16-RTIAPI-002-EFF",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == save_replace_test
        assert row["notes"].startswith("Direct ")


def test_fm_list_federation_executions_internal_error_rows_use_direct_backend_witness() -> None:
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    internal_error_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_list_federation_executions_surfaces_rti_internal_error_for_corrupt_runtime_state"
    )

    row = rows["HLA1516.1-FM-4_7-EXC-002"]
    assert row["current_status"] == "mapped"
    assert row["current_test_id"] == internal_error_test
    assert row["notes"].startswith("Direct ")

    exc_api_row = rows["HLA1516.1-FM-4_7-RTIAPI-001-EXC"]
    assert exc_api_row["current_status"] == "mapped"
    test_ids = {item.strip() for item in exc_api_row["current_test_id"].split(";") if item.strip()}
    assert test_ids == {
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_list_federation_executions_requires_connection_and_reports_known_federations",
        internal_error_test,
    }
    assert exc_api_row["notes"].startswith("Direct ")


def test_fm_report_federation_executions_argument_row_has_direct_payload_evidence():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    row = rows["HLA1516.1-FM-4_8-ARG-001"]

    assert row["current_status"] == "mapped"
    assert (
        row["current_test_id"]
        == "tests/backends/test_python_backend_federation_extended.py::test_list_federation_executions_requires_connection_and_reports_known_federations"
    )
    assert "node-level" in row["notes"]
    assert "federation-execution information records" in row["notes"]


def test_fm_save_restore_effect_rows_use_direct_positive_state_witnesses():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    single_test_rows = {
        "HLA1516.1-FM-4_18-EFF-001": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_18-RTIAPI-001-EFF": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_19-EFF-001": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_19-RTIAPI-001-EFF": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_19-RTIAPI-001-EFF-DUP02": "tests/backends/test_python_backend_federation_extended.py::test_save_failure_reports_federation_not_saved_and_clears_status",
        "HLA1516.1-FM-4_21-EFF-001": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        "HLA1516.1-FM-4_21-RTIAPI-001-EFF": "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
    }

    for packet_id, test_id in single_test_rows.items():
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == test_id
        assert row["notes"].startswith("Direct ")

    for packet_id in (
        "HLA1516.1-FM-4_20-EFF-001",
        "HLA1516.1-FM-4_20-EFF-002",
        "HLA1516.1-FM-4_22-EFF-001",
        "HLA1516.1-FM-4_22-RTIAPI-001-EFF",
    ):
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) == 2
        assert all(
            test_id.startswith("tests/backends/test_python_backend_federation_extended.py::")
            for test_id in test_ids
        )
        assert row["notes"].startswith("Direct ")


def test_fm_core_lifecycle_effect_and_return_rows_use_direct_runtime_witnesses():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    connect_rows = {
        "HLA1516.1-FM-4_2-EFF-001",
        "HLA1516.1-FM-4_2-RTIAPI-001-EFF",
        "HLA1516.1-FM-4_2-RTIAPI-002-EFF",
    }
    connect_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_connect_create_and_join_apply_positive_lifecycle_effects"
    )

    for packet_id in connect_rows:
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == connect_test
        assert row["notes"].startswith("Direct ")

    create_rows = {
        "HLA1516.1-FM-4_5-EFF-001",
        "HLA1516.1-FM-4_5-RTIAPI-001-EFF",
        "HLA1516.1-FM-4_5-RTIAPI-002-EFF",
        "HLA1516.1-FM-4_5-RTIAPI-003-EFF",
        "HLA1516.1-FM-4_5-RTIAPI-004-EFF",
        "HLA1516.1-FM-4_5-RTIAPI-005-EFF",
    }
    create_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_create_federation_execution_applies_full_effect_vector"
    )

    for packet_id in create_rows:
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == create_test
        assert row["notes"].startswith("Direct ")

    join_rows = {
        "HLA1516.1-FM-4_9-EFF-001",
        "HLA1516.1-FM-4_9-RET-001",
        "HLA1516.1-FM-4_9-RTIAPI-001-RET",
        "HLA1516.1-FM-4_9-RTIAPI-002-RET",
        "HLA1516.1-FM-4_9-RTIAPI-003-RET",
        "HLA1516.1-FM-4_9-RTIAPI-004-RET",
    }
    join_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_join_federation_execution_applies_full_effect_vector"
    )

    for packet_id in join_rows:
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert row["current_test_id"] == join_test
        assert row["notes"].startswith("Direct ")

    resign_rows = {
        "HLA1516.1-FM-4_10-EFF-001",
        "HLA1516.1-FM-4_10-EFF-002",
        "HLA1516.1-FM-4_10-EFF-003",
    }
    expected_resign_tests = {
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_resign_delete_object_directives_clear_membership_and_owned_objects[delete_objects]",
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_resign_delete_object_directives_clear_membership_and_owned_objects[delete_objects_then_divest]",
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_resign_delete_object_directives_clear_membership_and_owned_objects[cancel_then_delete_then_divest]",
    }

    for packet_id in resign_rows:
        row = rows[packet_id]
        assert row["current_status"] == "mapped"
        assert {
            item.strip() for item in row["current_test_id"].split(";") if item.strip()
        } == expected_resign_tests
        assert row["notes"].startswith("Direct ")

    broad_resign_test = (
        "tests/backends/test_python_backend_federation_extended.py::"
        "test_resign_federation_execution_applies_full_effect_vector"
    )
    broad_resign_row = rows["HLA1516.1-FM-4_10-RTIAPI-001-EFF"]
    assert broad_resign_row["current_status"] == "mapped"
    assert broad_resign_row["current_test_id"] == broad_resign_test
    assert broad_resign_row["notes"].startswith("Direct ")


def test_fm_rows_anchor_to_live_evidence_refs_even_when_legacy_rows_use_bare_names() -> None:
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry evidence references"
        for reference in references:
            _assert_reference_is_live(reference)


def test_fm_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    for row in _read_rows():
        for forbidden in _DISALLOWED_TRUTH_SOURCES:
            assert forbidden not in row["current_test_id"], (
                f"{row['packet_requirement_id']} should not use {forbidden} as a truth source"
            )
