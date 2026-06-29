from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from hla.verification.repo_internal.verification.spec2025_traceability_matrix import (
    TRACEABILITY_ARTIFACT_REL,
    build_spec2025_traceability_matrix,
    write_spec2025_traceability_matrix,
)

ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE_PACKET = (
    ROOT / "docs" / "requirements" / "ieee-1516-2025" / "executable_tests" / "hla_2025_executable_test_requirements_v3.csv"
)
_TRACEABILITY_PREFIX = "tests/requirements/test_2025_traceability.py::"


def _load_executable_packet_rows() -> list[dict[str, str]]:
    with EXECUTABLE_PACKET.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


_EXECUTABLE_PACKET_ROWS = _load_executable_packet_rows()


def test_spec2025_traceability_matrix_writer_emits_expected_structure(tmp_path: Path) -> None:
    expected = build_spec2025_traceability_matrix(ROOT)
    output_path = write_spec2025_traceability_matrix(ROOT, tmp_path / "traceability_matrix.json")
    actual = json.loads(output_path.read_text(encoding="utf-8"))

    assert actual["artifact"] == "spec2025-traceability-matrix"
    assert actual["scope"] == expected["scope"]
    assert actual["row_count"] == expected["row_count"]
    assert set(actual) == {"artifact", "scope", "row_count", "rows"}
    assert len(actual["rows"]) == actual["row_count"] > 0

    actual_rows = {row["requirement_id"]: row for row in actual["rows"]}
    expected_rows = {row["requirement_id"]: row for row in expected["rows"]}
    assert set(actual_rows) == set(expected_rows)

    for requirement_id in (
        "HLA2025-FR-001",
        "HLA2025-FR-010",
        "HLA2025-FI-CB-007",
        "HLA2025-FI-CFG-001",
        "HLA2025-BIND-JAVA-CPP-001",
    ):
        assert actual_rows[requirement_id] == expected_rows[requirement_id]


def test_spec2025_traceability_matrix_routes_through_canonical_owner_and_live_evidence() -> None:
    matrix = build_spec2025_traceability_matrix(ROOT)

    assert matrix["artifact"] == "spec2025-traceability-matrix"
    assert matrix["row_count"] > 0

    rows = {row["requirement_id"]: row for row in matrix["rows"]}
    sample_ids = (
        "HLA2025-FR-001",
        "HLA2025-FR-010",
        "HLA2025-FI-CB-007",
        "HLA2025-FI-CFG-001",
        "HLA2025-BIND-JAVA-CPP-001",
    )

    for requirement_id in sample_ids:
        row = rows[requirement_id]
        assert row["owner_doc"].startswith("docs/requirements/ieee-1516-2025/")
        assert row["child_requirement_ids"]
        assert row["evidence_anchors"]
        assert "docs/plans/" not in row["owner_doc"]
        assert "worklist" not in row["owner_doc"]


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FR-010")
def test_spec2025_framework_traceability_rows_are_child_mapped_and_evidence_backed() -> None:
    matrix = build_spec2025_traceability_matrix(ROOT)
    rows = {row["requirement_id"]: row for row in matrix["rows"]}

    for requirement_id in (f"HLA2025-FR-{index:03d}" for index in range(1, 11)):
        row = rows[requirement_id]
        assert row["harmonization_disposition"] == "duplicate/umbrella"
        assert row["row_role"] == "framework-umbrella"
        assert row["owner_doc"] == "docs/requirements/ieee-1516-2025/framework_rules.md"
        assert row["child_requirement_ids"]
        assert row["evidence_anchors"]

    assert rows["HLA2025-FR-001"]["child_requirement_ids"] == [
        "HLA2025-OMT-001",
        "HLA2025-OMT-005",
        "HLA2025-OMT-006",
        "HLA2025-REQ-001",
    ]
    assert rows["HLA2025-FR-010"]["child_requirement_ids"] == [
        "HLA2025-FI-009",
        "HLA2025-FI-SVC-101",
        "HLA2025-FI-SVC-107",
        "HLA2025-FI-SVC-112",
        "HLA2025-FI-SVC-121",
        "HLA2025-MOD-006",
    ]


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-BIND-FEDPRO-001", "HLA2025-BIND-JAVA-CPP-001")
def test_spec2025_callback_binding_traceability_rows_are_child_mapped_and_evidence_backed() -> None:
    matrix = build_spec2025_traceability_matrix(ROOT)
    rows = {row["requirement_id"]: row for row in matrix["rows"]}

    for requirement_id in [
        *(f"HLA2025-FI-CB-{index:03d}" for index in range(1, 9)),
        "HLA2025-FI-CFG-001",
        "HLA2025-FI-AUTH-001",
        "HLA2025-BIND-FEDPRO-001",
        "HLA2025-BIND-JAVA-CPP-001",
    ]:
        row = rows[requirement_id]
        assert row["harmonization_disposition"] == "duplicate/umbrella"
        assert row["row_role"] == "delta-umbrella"
        assert row["owner_doc"] == "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
        assert row["child_requirement_ids"]
        assert row["evidence_anchors"]

    assert rows["HLA2025-FI-CB-007"]["child_requirement_ids"] == [
        "HLA2025-BND-003",
        "HLA2025-FI-SVC-063",
        "HLA2025-FI-SVC-064",
    ]
    assert rows["HLA2025-BIND-JAVA-CPP-001"]["child_requirement_ids"] == [
        "HLA2025-BND-001",
        "HLA2025-BND-002",
        "HLA2025-FI-003",
        "HLA2025-FI-004",
    ]


def _make_traceability_anchor_test(pytest_candidate: str, parent_requirement_id: str) -> None:
    def _test() -> None:
        rows = [row for row in _EXECUTABLE_PACKET_ROWS if row["pytest_candidate"] == pytest_candidate]
        matrix = build_spec2025_traceability_matrix(ROOT)
        matrix_rows = {row["requirement_id"]: row for row in matrix["rows"]}

        assert len(rows) == 1
        row = rows[0]
        assert row["parent_requirement_id"] == parent_requirement_id
        assert row["evidence_artifact"] == TRACEABILITY_ARTIFACT_REL
        assert (ROOT / row["evidence_artifact"]).exists()
        assert row["implementation_target"]
        assert row["requirement_summary"]
        assert row["expected_result_from_extraction"]
        assert row["parent_requirement_id"] in matrix_rows

        matrix_row = matrix_rows[row["parent_requirement_id"]]
        assert matrix_row["pytest_candidate"] == pytest_candidate
        assert matrix_row["executable_test_id"]
        assert matrix_row["implementation_target"] == row["implementation_target"]
        assert matrix_row["requirement_summary"] == row["requirement_summary"]
        assert matrix_row["expected_result_from_extraction"] == row["expected_result_from_extraction"]
        assert matrix_row["expected_status"] == row["expected_status"]
        assert matrix_row["traceability_basis"] in {
            "direct-requirement-evidence",
            "duplicate-umbrella-child-evidence",
            "packet-only-no-direct-anchor",
        }
        assert isinstance(matrix_row["evidence_anchors"], list)

    _test.__name__ = pytest_candidate.split("::", 1)[1]
    globals()[_test.__name__] = pytest.mark.requirements(parent_requirement_id)(_test)


for _row in _EXECUTABLE_PACKET_ROWS:
    _pytest_candidate = _row["pytest_candidate"]
    if _pytest_candidate.startswith(_TRACEABILITY_PREFIX):
        _make_traceability_anchor_test(_pytest_candidate, _row["parent_requirement_id"])
