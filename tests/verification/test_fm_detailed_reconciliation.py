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
        {"mapped": 559, "partial": 73}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_fm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-FM-4_2-SVC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_2-ARG-001"]["current_status"] == "partial"
    assert rows["HLA1516.1-FM-4_8-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_3-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-ARG-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_4-FEDCB-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_7-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-FM-4_8-FEDCB-001-ORD"]["current_status"] == "mapped"
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

    partial_row = rows["HLA1516.1-FM-4_4-EFF-001"]
    assert partial_row["current_status"] == "partial"
    assert partial_row["current_test_id"] == direct_test
    assert "does not prove a full disconnected-state transition" in partial_row["notes"]


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
