from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIFFERENTIAL_SET = ROOT / "requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv"
REUSE_DISPOSITION = ROOT / "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv"
STRICT_DOC_INVENTORY = ROOT / "requirements/2025/STRICT_DOC_INVENTORY.json"
SOURCE_TRACE = ROOT / "requirements/2025/SOURCE_TRACE.md"
CANONICAL_REQUIREMENTS = ROOT / "requirements/2025/canonical_requirements.json"
BACKEND_RESOLUTION = ROOT / "requirements/2025/backend_resolution.json"
FEDPRO_PROTO_DIR = ROOT / "packages/hla-transport-grpc/proto/rti1516_2025/fedpro"
FEDPRO_2025_TEST = ROOT / "tests/transport/test_grpc_transport_2025.py"
WSDL_2010 = ROOT / "CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _canonical_requirement_rows() -> list[dict[str, object]]:
    return json.loads(CANONICAL_REQUIREMENTS.read_text(encoding="utf-8"))["rows"]


def _backend_resolution_rows() -> list[dict[str, object]]:
    return json.loads(BACKEND_RESOLUTION.read_text(encoding="utf-8"))["rows"]


def _binding_resolution_rows() -> dict[str, dict[str, object]]:
    return {
        str(row["requirement_id"]): row
        for row in _backend_resolution_rows()
        if str(row.get("resolution_type", "")) == "binding-route-resolution"
    }


def _matching_requirement_rows(rows: list[dict[str, object]], ids: set[str]) -> list[dict[str, object]]:
    return [row for row in rows if str(row.get("requirement_id", "")) in ids]


def _canonical_service_rows(start: int, end: int) -> list[dict[str, object]]:
    return [
        row
        for row in _canonical_requirement_rows()
        if str(row.get("requirement_id", "")).startswith("HLA2025-FI-SVC-")
        and start <= int(str(row.get("requirement_id", "")).split("-")[-1]) <= end
    ]


PYTHON2025_BACKEND_EVIDENCE_PATH = "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py"
PYTHON2025_BACKEND_PACKAGE_PATH = "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/"
SHIM_BACKEND_EVIDENCE_PATH = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
CALLBACK_BINDING_DELTA_DOC = "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
FRAMEWORK_RULES_DOC = "docs/requirements/ieee-1516-2025/framework_rules.md"
BINDING_HOSTED_BOUNDARY_DOC = "docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md"
OMT_XS_ANY_DOC = "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md"
RETIRED_LEGACY_MAPPING_DOC = "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"
SUPPORT_SERVICES_DOC = "docs/requirements/ieee-1516-2025/support_services_bounded_proof.md"
TIME_MANAGEMENT_DOC = "docs/requirements/ieee-1516-2025/time_management_bounded_proof.md"
FEDERATION_MANAGEMENT_DOC = "docs/requirements/ieee-1516-2025/federation_management_bounded_proof.md"
DECLARATION_MANAGEMENT_DOC = "docs/requirements/ieee-1516-2025/declaration_management_bounded_proof.md"
OBJECT_MANAGEMENT_DOC = "docs/requirements/ieee-1516-2025/object_management_bounded_proof.md"
OWNERSHIP_MANAGEMENT_DOC = "docs/requirements/ieee-1516-2025/ownership_management_bounded_proof.md"
DDM_MANAGEMENT_DOC = "docs/requirements/ieee-1516-2025/ddm_bounded_proof.md"
DELTA_UMBRELLA_IDS = {
    "HLA2025-FI-CB-001",
    "HLA2025-FI-CB-002",
    "HLA2025-FI-CB-003",
    "HLA2025-FI-CB-004",
    "HLA2025-FI-CB-005",
    "HLA2025-FI-CB-006",
    "HLA2025-FI-CB-007",
    "HLA2025-FI-CB-008",
    "HLA2025-FI-CFG-001",
    "HLA2025-FI-AUTH-001",
    "HLA2025-BIND-FEDPRO-001",
    "HLA2025-BIND-JAVA-CPP-001",
}
FRAMEWORK_UMBRELLA_IDS = {f"HLA2025-FR-{index:03d}" for index in range(1, 11)}
RETIRED_LEGACY_IDS = {
    "HLA2025-FI-RET-001",
    "HLA2025-FI-RET-002",
    "HLA2025-FI-RET-003",
    "HLA2025-FI-RET-004",
    "HLA2025-FI-RET-005",
    "HLA2025-FI-RET-006",
    "HLA2025-FI-RET-007",
    "HLA2025-FI-RET-008",
    "HLA2025-FI-RET-009",
    "HLA2025-FI-RET-010",
    "HLA2025-FI-RET-011",
    "HLA2025-OMT-RET-001",
    "HLA2025-OMT-RET-002",
    "HLA2025-OMT-RET-003",
    "HLA2025-OMT-RET-004",
    "HLA2025-OMT-RET-005",
    "HLA2025-OMT-RET-006",
    "HLA2025-OMT-RET-007",
    "HLA2025-OMT-RET-008",
    "HLA2025-OMT-RET-009",
    "HLA2025-OMT-RET-010",
    "HLA2025-OMT-RET-011",
    "HLA2025-OMT-RET-012",
    "HLA2025-OMT-RET-013",
}
NON_COVERED_2025_IDS = DELTA_UMBRELLA_IDS | FRAMEWORK_UMBRELLA_IDS | RETIRED_LEGACY_IDS
STALE_COVERED_STATUS = "not-promoted-to-covered: repo evidence path/test anchor still required"
SERVICE_COVERED_STATUS = "covered: repo evidence anchor and executable test recorded"
SERVICE_USAGE_COVERED_STATUS = "covered: parser/serializer round-trip and FI cross-check evidence recorded"
DIRECT_SERVICE_USAGE_EVIDENCE = (
    "tests/factories/test_fom_omt_parsing.py; tests/factories/test_fom_roundtrip.py; "
    "tests/test_rti1516_2025_validation.py; packages/hla-rti-core/src/hla/fom/__init__.py"
)


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-MIL-002", "HLA2025-TRACE-001")
def test_harmonization_packets_keep_covered_runtime_evidence_on_python2025_lane() -> None:
    covered_rows = [row for row in _canonical_requirement_rows() if row.get("canonical_status") == "covered"]
    assert covered_rows
    assert any(PYTHON2025_BACKEND_PACKAGE_PATH in "; ".join(row.get("evidence_refs", [])) for row in covered_rows)
    assert all(SHIM_BACKEND_EVIDENCE_PATH not in "; ".join(row.get("evidence_refs", [])) for row in covered_rows)


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-REQ-001")
def test_covered_2025_rows_do_not_keep_stale_not_promoted_status_markers() -> None:
    covered_rows = [row for row in _canonical_requirement_rows() if str(row.get("canonical_status", "")) == "covered"]
    assert covered_rows
    assert all(str(row.get("repo_evidence_status", "")) != STALE_COVERED_STATUS for row in covered_rows)

    service_rows = [row for row in covered_rows if str(row.get("row_kind", "")) == "service-or-callback"]
    assert service_rows
    assert all(str(row.get("repo_evidence_status", "")) == SERVICE_COVERED_STATUS for row in service_rows)

    service_usage_rows = [row for row in covered_rows if str(row.get("row_kind", "")) == "service-usage-crosscheck"]
    assert service_usage_rows
    assert all(str(row.get("repo_evidence_status", "")) == SERVICE_USAGE_COVERED_STATUS for row in service_usage_rows)
    assert all("; ".join(row.get("evidence_refs", [])) == DIRECT_SERVICE_USAGE_EVIDENCE for row in service_usage_rows)
    assert all("tests/requirements/" not in "; ".join(row.get("evidence_refs", [])) for row in service_usage_rows)


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-BIND-FEDPRO-001", "HLA2025-BIND-JAVA-CPP-001")
def test_harmonization_packets_repoint_delta_umbrella_rows_to_real_callback_binding_evidence() -> None:
    placeholder_prefix = "tests/hla2025/fi/deltas/"
    matched = _matching_requirement_rows(_canonical_requirement_rows(), DELTA_UMBRELLA_IDS)
    assert len(matched) == len(DELTA_UMBRELLA_IDS)
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert CALLBACK_BINDING_DELTA_DOC in evidence
        assert placeholder_prefix not in evidence


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-FI-CB-008", "HLA2025-BIND-FEDPRO-001", "HLA2025-BIND-JAVA-CPP-001")
def test_delta_umbrella_rows_are_explicit_evidenced_owner_doc_closures_not_missing_evidence_rows() -> None:
    matched = _matching_requirement_rows(_canonical_requirement_rows(), DELTA_UMBRELLA_IDS)
    assert len(matched) == len(DELTA_UMBRELLA_IDS)
    for row in matched:
        assert str(row.get("canonical_status", "")) == "duplicate/umbrella"
        assert str(row.get("row_kind", "")) == "delta-umbrella"

        evidence = "; ".join(row.get("evidence_refs", []))
        assert CALLBACK_BINDING_DELTA_DOC in evidence
        assert "test_2025_finish_line_snapshot.py" not in evidence
        assert "test_2025_tail_backlog_evidence.py" not in evidence

        repo_status = str(row.get("repo_evidence_status", ""))
        assert repo_status.startswith("owner-doc-closed:")
        assert "keep duplicate/umbrella" in repo_status

        rationale = str(row.get("canonical_status_reason", ""))
        assert "non-standalone umbrella" in rationale
        assert "child FI/binding rows" in rationale


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FR-010")
def test_framework_umbrella_rows_are_explicit_evidenced_owner_doc_closures_not_missing_evidence_rows() -> None:
    matched = _matching_requirement_rows(_canonical_requirement_rows(), FRAMEWORK_UMBRELLA_IDS)
    assert len(matched) == len(FRAMEWORK_UMBRELLA_IDS)
    for row in matched:
        assert str(row.get("canonical_status", "")) == "duplicate/umbrella"
        assert str(row.get("row_kind", "")) == "framework-umbrella"

        evidence = "; ".join(row.get("evidence_refs", []))
        assert FRAMEWORK_RULES_DOC in evidence
        assert "traceability_matrix.json" in evidence
        assert "literal:linked-fi-omt-child-rows" in evidence

        repo_status = str(row.get("repo_evidence_status", ""))
        assert repo_status.startswith("owner-doc-closed:")
        assert "child-row links" in repo_status
        assert "keep duplicate/umbrella" in repo_status

        rationale = str(row.get("canonical_status_reason", ""))
        assert "non-standalone parent" in rationale
        assert "linked child FI/OMT/runtime rows" in rationale


@pytest.mark.requirements("HLA2025-RET-001", "HLA2025-RET-003")
def test_retired_legacy_rows_are_explicit_evidenced_owner_doc_closures_not_missing_evidence_rows() -> None:
    expected_evidence = (
        "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md; "
        "bounded:migration-compatibility-fixture-if-supported"
    )
    matched = _matching_requirement_rows(_canonical_requirement_rows(), RETIRED_LEGACY_IDS)
    assert len(matched) == len(RETIRED_LEGACY_IDS)
    for row in matched:
        assert str(row.get("canonical_status", "")) == "retired/legacy-only"
        assert str(row.get("row_kind", "")) == "legacy-mapping"
        assert "; ".join(row.get("evidence_refs", [])) == expected_evidence

        rationale = str(row.get("canonical_status_reason", ""))
        assert "Legacy-only diff row" in rationale
        assert "keep out of 2025 normative coverage" in rationale

        assert str(row.get("repo_evidence_status", "")) == "legacy-only: excluded unless compatibility support is intentional"

@pytest.mark.requirements("HLA2025-OMT-COMP-006", "HLA2025-OMT-COMP-039", "HLA2025-OMT-COMP-224")
def test_harmonization_packets_keep_xs_any_rows_on_bounded_omt_tolerance_evidence() -> None:
    matched = [
        row
        for row in _canonical_requirement_rows()
        if str(row.get("requirement_id", "")).startswith("HLA2025-OMT-COMP-")
        and "xs:any" in str(row.get("service_or_check", ""))
    ]
    assert len(matched) == 45
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert OMT_XS_ANY_DOC in evidence
        assert "tests/test_rti1516_2025_validation.py" in evidence
        assert "packages/hla-rti-core/src/hla/fom/__init__.py" in evidence


@pytest.mark.requirements("HLA2025-OMT-COMP-006", "HLA2025-OMT-COMP-039", "HLA2025-OMT-COMP-224")
def test_omt_xs_any_bounded_proof_doc_enumerates_all_tracked_rows() -> None:
    text = (ROOT / OMT_XS_ANY_DOC).read_text(encoding="utf-8")

    assert "object-model-root-and-identity" in text
    assert "object-class-and-attribute-extension-points" in text
    assert "interaction-class-and-parameter-extension-points" in text
    assert "datatype-and-encoding-extension-points" in text
    assert "container-table-and-reference-extension-points" in text
    for number in (
        6,
        8,
        19,
        21,
        27,
        35,
        39,
        45,
        47,
        56,
        57,
        59,
        67,
        68,
        70,
        77,
        81,
        82,
        102,
        106,
        107,
        113,
        115,
        129,
        130,
        134,
        145,
        147,
        154,
        156,
        171,
        176,
        178,
        181,
        189,
        193,
        197,
        198,
        202,
        204,
        208,
        210,
        219,
        222,
        224,
    ):
        assert f"HLA2025-OMT-COMP-{number:03d}" in text


@pytest.mark.requirements("HLA2025-RET-001", "HLA2025-RET-003")
def test_harmonization_packets_keep_retired_rows_on_explicit_legacy_mapping_doc() -> None:
    matched = _matching_requirement_rows(_canonical_requirement_rows(), RETIRED_LEGACY_IDS)
    assert len(matched) == len(RETIRED_LEGACY_IDS)
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert RETIRED_LEGACY_MAPPING_DOC in evidence
        assert str(row.get("canonical_status", "")) == "retired/legacy-only"


@pytest.mark.requirements("HLA2025-RET-001", "HLA2025-RET-003")
def test_retired_legacy_mapping_doc_accounts_for_all_retired_rows() -> None:
    text = (ROOT / RETIRED_LEGACY_MAPPING_DOC).read_text(encoding="utf-8")

    assert "retired/legacy-only" in text
    assert "not active 2025 obligations" in text
    assert "hla-backend-python1516-2025" in text
    assert "hla-backend-shim" in text
    for row_id in sorted(RETIRED_LEGACY_IDS):
        assert row_id in text
    assert "disableAttributeRelevanceAdvisorySwitch" in text
    assert "releaseMultipleObjectInstanceNames" in text
    assert "logicalTimeInterval" in text


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_support_service_rows_on_bounded_support_service_evidence() -> None:
    matched = [
        row
        for row in _canonical_requirement_rows()
        if str(row.get("requirement_id", "")).startswith("HLA2025-FI-SVC-")
        and str(row.get("service_group", "")) == "Support services"
    ]
    assert len(matched) == 59
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert SUPPORT_SERVICES_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence
        assert "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py" in evidence


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003")
def test_binding_boundary_note_tracks_all_three_binding_rows_as_non_owner_routes() -> None:
    text = (ROOT / BINDING_HOSTED_BOUNDARY_DOC).read_text(encoding="utf-8")

    assert "HLA2025-BND-001" in text
    assert "HLA2025-BND-002" in text
    assert "HLA2025-BND-003" in text
    assert "not an independent Java RTI" in text
    assert "not an independent C++ RTI" in text
    assert "not a second RTI implementation lane" in text
    assert "hla-backend-python1516-2025" in text
    assert "hla-backend-shim" in text
    assert "tests/requirements/test_2025_route_parity_matrix.py" in text
    assert "tests/backends/test_standard_shim_artifacts.py" in text
    assert "tests/transport/test_grpc_transport_2025.py" in text


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-FI-SVC-070", "HLA2025-FI-SVC-193", "HLA2025-FI-SVC-196")
def test_backend_resolution_keeps_fedpro_route_boundaries_explicit() -> None:
    rows = _binding_resolution_rows()

    split_row = rows["HLA2025-FI-SVC-070"]
    split_fields = split_row["backend_fields"]
    assert split_row["canonical_status"] == "covered"
    assert split_fields["fedpro_surface"] == "present-via-class-and-instance-split"
    assert split_fields["fedpro_match_or_note"] == (
        "RequestClassAttributeValueUpdateRequest; RequestInstanceAttributeValueUpdateRequest"
    )
    assert split_fields["binding_surface_summary"] == (
        "Java=present; C++=present; FedPro=present-via-class-and-instance-split"
    )
    assert "class-scoped and instance-scoped transport commands" in split_row["boundary_note"]
    assert "broader parity claims remain bounded" in split_row["boundary_note"]

    for requirement_id in ("HLA2025-FI-SVC-193", "HLA2025-FI-SVC-194", "HLA2025-FI-SVC-195", "HLA2025-FI-SVC-196"):
        row = rows[requirement_id]
        fields = row["backend_fields"]
        assert row["canonical_status"] == "covered"
        assert fields["fedpro_surface"] == "not-present-route-boundary-callback-pump-control"
        assert fields["binding_surface_summary"] == (
            "Java=present; C++=present; FedPro=not-present-route-boundary-callback-pump-control"
        )
        assert "callback-pump control as a transport RPC" in row["boundary_note"]
        assert "local runtime dispatch policy boundary" in row["boundary_note"]
        assert "not a hosted route semantics gap in the main python1516_2025 lane" in row["boundary_note"]


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_time_management_rows_on_time_management_proof_note() -> None:
    matched = _canonical_service_rows(101, 125)
    assert len(matched) == 25
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert TIME_MANAGEMENT_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence
        assert "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py" in evidence


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_federation_management_rows_on_federation_management_proof_note() -> None:
    matched = _canonical_service_rows(1, 34)
    assert len(matched) == 34
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert FEDERATION_MANAGEMENT_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence
        assert "tests/scenarios/test_federation_management_backend_matrix.py" in evidence


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_declaration_management_rows_on_declaration_management_proof_note() -> None:
    matched = _canonical_service_rows(35, 50)
    assert len(matched) == 16
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert DECLARATION_MANAGEMENT_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/scenarios/test_object_management_backend_matrix.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_object_management_rows_on_object_management_proof_note() -> None:
    matched = _canonical_service_rows(51, 82)
    assert len(matched) == 32
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert OBJECT_MANAGEMENT_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/scenarios/test_object_management_backend_matrix.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_ownership_management_rows_on_ownership_management_proof_note() -> None:
    matched = _canonical_service_rows(83, 100)
    assert len(matched) == 18
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert OWNERSHIP_MANAGEMENT_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/scenarios/test_ownership_management_backend_matrix.py" in evidence
        assert "tests/backends/test_python_backend_object_ownership_extended.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence


@pytest.mark.requirements("HLA2025-REQ-001")
def test_harmonization_packets_keep_ddm_rows_on_ddm_proof_note() -> None:
    matched = _canonical_service_rows(126, 137)
    assert len(matched) == 12
    for row in matched:
        evidence = "; ".join(row.get("evidence_refs", []))
        assert DDM_MANAGEMENT_DOC in evidence
        assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in evidence
        assert "tests/backends/test_python_backend_time_ddm_extended.py" in evidence
        assert "tests/scenarios/test_ddm_backend_matrix.py" in evidence
        assert "tests/transport/test_grpc_transport_2025.py" in evidence


@pytest.mark.requirements("HLA2025-BLG-001",
    "HLA2025-REQ-001",
    "HLA2025-OMT-SU-001",
    "HLA2025-OMT-SU-002",
    "HLA2025-OMT-SU-003",
    "HLA2025-OMT-SU-004",
    "HLA2025-OMT-SU-005",
    "HLA2025-OMT-SU-006",
    "HLA2025-OMT-SU-007",
    "HLA2025-OMT-SU-008",
    "HLA2025-OMT-SU-009",
    "HLA2025-OMT-SU-010",
    "HLA2025-OMT-SU-011",
    "HLA2025-OMT-SU-012",
    "HLA2025-OMT-SU-013",
    "HLA2025-OMT-SU-014",
    "HLA2025-OMT-SU-015",
    "HLA2025-OMT-SU-016",
    "HLA2025-OMT-SU-017",
    "HLA2025-OMT-SU-018",
    "HLA2025-OMT-SU-019",
    "HLA2025-OMT-SU-020",
    "HLA2025-OMT-SU-021",
    "HLA2025-OMT-SU-022",
    "HLA2025-OMT-SU-023",
    "HLA2025-OMT-SU-024",
    "HLA2025-OMT-SU-025",
    "HLA2025-OMT-SU-026",
    "HLA2025-OMT-SU-027",
    "HLA2025-OMT-SU-028",
    "HLA2025-OMT-SU-029",
    "HLA2025-OMT-SU-030",
    "HLA2025-OMT-SU-031",
    "HLA2025-OMT-SU-032",
    "HLA2025-OMT-SU-033",
    "HLA2025-OMT-SU-034",
    "HLA2025-OMT-SU-035",
    "HLA2025-OMT-SU-036",
    "HLA2025-OMT-SU-037",
    "HLA2025-OMT-SU-038",
    "HLA2025-OMT-SU-039",
    "HLA2025-OMT-SU-040",
    "HLA2025-OMT-SU-041",
    "HLA2025-OMT-SU-042",
    "HLA2025-OMT-SU-043",
    "HLA2025-OMT-SU-044",
    "HLA2025-OMT-SU-045",
    "HLA2025-OMT-SU-046",
    "HLA2025-OMT-SU-047",
    "HLA2025-OMT-SU-048",
    "HLA2025-OMT-SU-049",
    "HLA2025-OMT-SU-050",
    "HLA2025-OMT-SU-051",
    "HLA2025-OMT-SU-052",
    "HLA2025-OMT-SU-053",
    "HLA2025-OMT-SU-054",
    "HLA2025-OMT-SU-055",
    "HLA2025-OMT-SU-056",
    "HLA2025-OMT-SU-057",
    "HLA2025-OMT-SU-058",
    "HLA2025-OMT-SU-059",
    "HLA2025-OMT-SU-060",
    "HLA2025-OMT-SU-061",
    "HLA2025-OMT-SU-062",
    "HLA2025-OMT-SU-063",
    "HLA2025-OMT-SU-064",
    "HLA2025-OMT-SU-065",
    "HLA2025-OMT-SU-066",
    "HLA2025-OMT-SU-067",
    "HLA2025-OMT-SU-068",
    "HLA2025-OMT-SU-069",
    "HLA2025-OMT-SU-070",
    "HLA2025-OMT-SU-071",
    "HLA2025-OMT-SU-072",
    "HLA2025-OMT-SU-073",
    "HLA2025-OMT-SU-074",
    "HLA2025-OMT-SU-075",
    "HLA2025-OMT-SU-076",
    "HLA2025-OMT-SU-077",
    "HLA2025-OMT-SU-078",
    "HLA2025-OMT-SU-079",
    "HLA2025-OMT-SU-080",
    "HLA2025-OMT-SU-081",
    "HLA2025-OMT-SU-082",
    "HLA2025-OMT-SU-083",
    "HLA2025-OMT-SU-084",
    "HLA2025-OMT-SU-085",
    "HLA2025-OMT-SU-086",
    "HLA2025-OMT-SU-087",
    "HLA2025-OMT-SU-088",
    "HLA2025-OMT-SU-089",
    "HLA2025-OMT-SU-090",
    "HLA2025-OMT-SU-091",
    "HLA2025-OMT-SU-092",
    "HLA2025-OMT-SU-093",
    "HLA2025-OMT-SU-094",
    "HLA2025-OMT-SU-095",
    "HLA2025-OMT-SU-096",
    "HLA2025-OMT-SU-097",
    "HLA2025-OMT-SU-098",
    "HLA2025-OMT-SU-099",
    "HLA2025-OMT-SU-100",
    "HLA2025-OMT-SU-101",
    "HLA2025-OMT-SU-102",
    "HLA2025-OMT-SU-103",
    "HLA2025-OMT-SU-104",
    "HLA2025-OMT-SU-105",
    "HLA2025-OMT-SU-106",
    "HLA2025-OMT-SU-107",
    "HLA2025-OMT-SU-108",
    "HLA2025-OMT-SU-109",
    "HLA2025-OMT-SU-110",
    "HLA2025-OMT-SU-111",
    "HLA2025-OMT-SU-112",
    "HLA2025-OMT-SU-113",
    "HLA2025-OMT-SU-114",
    "HLA2025-OMT-SU-115",
    "HLA2025-OMT-SU-116",
    "HLA2025-OMT-SU-117",
    "HLA2025-OMT-SU-118",
    "HLA2025-OMT-SU-119",
    "HLA2025-OMT-SU-120",
    "HLA2025-OMT-SU-121",
    "HLA2025-OMT-SU-122",
    "HLA2025-OMT-SU-123",
    "HLA2025-OMT-SU-124",
    "HLA2025-OMT-SU-125",
    "HLA2025-OMT-SU-126",
    "HLA2025-OMT-SU-127",
    "HLA2025-OMT-SU-128",
    "HLA2025-OMT-SU-129",
    "HLA2025-OMT-SU-130",
    "HLA2025-OMT-SU-131",
    "HLA2025-OMT-SU-132",
    "HLA2025-OMT-SU-133",
    "HLA2025-OMT-SU-134",
    "HLA2025-OMT-SU-135",
    "HLA2025-OMT-SU-136",
    "HLA2025-OMT-SU-137",
    "HLA2025-OMT-SU-138",
    "HLA2025-OMT-SU-139",
    "HLA2025-OMT-SU-140",
    "HLA2025-OMT-SU-141",
    "HLA2025-OMT-SU-142",
    "HLA2025-OMT-SU-143",
    "HLA2025-OMT-SU-144",
    "HLA2025-OMT-SU-145",
    "HLA2025-OMT-SU-146",
    "HLA2025-OMT-SU-147",
    "HLA2025-OMT-SU-148",
    "HLA2025-OMT-SU-149",
    "HLA2025-OMT-SU-150",
    "HLA2025-OMT-SU-151",
    "HLA2025-OMT-SU-152",
    "HLA2025-OMT-SU-153",
    "HLA2025-OMT-SU-154",
    "HLA2025-OMT-SU-155",
    "HLA2025-OMT-SU-156",
    "HLA2025-OMT-SU-157",
    "HLA2025-OMT-SU-158",
    "HLA2025-OMT-SU-159",
    "HLA2025-OMT-SU-160",
    "HLA2025-OMT-SU-161",
    "HLA2025-OMT-SU-162",
    "HLA2025-OMT-SU-163",
    "HLA2025-OMT-SU-164",
    "HLA2025-OMT-SU-165",
    "HLA2025-OMT-SU-166",
    "HLA2025-OMT-SU-167",
    "HLA2025-OMT-SU-168",
    "HLA2025-OMT-SU-169",
    "HLA2025-OMT-SU-170",
    "HLA2025-OMT-SU-171",
    "HLA2025-OMT-SU-172",
    "HLA2025-OMT-SU-173",
    "HLA2025-OMT-SU-174",
    "HLA2025-OMT-SU-175",
    "HLA2025-OMT-SU-176",
    "HLA2025-OMT-SU-177",
    "HLA2025-OMT-SU-178",
    "HLA2025-OMT-SU-179",
    "HLA2025-OMT-SU-180",
    "HLA2025-OMT-SU-181",
    "HLA2025-OMT-SU-182",
    "HLA2025-OMT-SU-183",
    "HLA2025-OMT-SU-184",
    "HLA2025-OMT-SU-185",
    "HLA2025-OMT-SU-186",
    "HLA2025-OMT-SU-187",
    "HLA2025-OMT-SU-188",
    "HLA2025-OMT-SU-189",
    "HLA2025-OMT-SU-190",
    "HLA2025-OMT-SU-191",
    "HLA2025-OMT-SU-192",
    "HLA2025-OMT-SU-193",
    "HLA2025-OMT-SU-194",
    "HLA2025-OMT-SU-195",
    "HLA2025-OMT-SU-196"
)
def test_2025_renumbered_service_utilization_rows_preserve_behavior_and_update_references() -> None:
    rows = _csv_rows(DIFFERENTIAL_SET)
    renumbered = [
        row
        for row in rows
        if row["reuse_action"] == "Carry forward with reference update"
        and row["surface_type"] == "OMT serviceUtilization"
    ]

    assert len(renumbered) >= 90
    assert all(row["2010_section_or_location"] for row in renumbered)
    assert all(row["2025_section_or_location"] for row in renumbered)
    assert all(row["2010_section_or_location"] != row["2025_section_or_location"] for row in renumbered)
    assert all(row["2010_detail"] == row["2025_detail"] for row in renumbered)
    assert all("update clause number" in row["requirement_action"] for row in renumbered)

    sample = {row["item"]: row for row in renumbered}
    assert sample["announceSynchronizationPoint"]["2010_detail"] == "isCallback=true"
    assert sample["announceSynchronizationPoint"]["2025_detail"] == "isCallback=true"
    assert sample["abortFederationRestore"]["2010_detail"] == "isCallback=false"
    assert sample["abortFederationRestore"]["2025_detail"] == "isCallback=false"


@pytest.mark.requirements("HLA2025-BLG-002", "HLA2025-NEW-006", "HLA2025-REQ-001")
def test_2025_common_object_model_reuse_keeps_shared_model_and_adds_nullable_2025_metadata() -> None:
    rows = _csv_rows(REUSE_DISPOSITION)
    by_area = {row["Code area"]: row for row in rows}
    common_model = by_area["Common FOM/SOM object-model representation"]

    assert common_model["Disposition"] == "Reuse directly in common core"
    assert "Object class" in common_model["2010 code candidate"]
    assert "valueRequired" in common_model["2025 impact"]
    assert "nullable/optional fields" in common_model["Implementation recommendation"]
    assert "2025-only metadata" in common_model["Requirement/test action"]


@pytest.mark.requirements("HLA2025-MOD-009", "HLA2025-MOD-001", "HLA2025-MOD-002")
def test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms() -> None:
    inventory = json.loads(STRICT_DOC_INVENTORY.read_text(encoding="utf-8"))
    rti_groups = inventory["rti_overload_groups"]

    connect = " ".join(rti_groups["connect"])
    create = " ".join(rti_groups["createFederationExecution"])
    create_with_mim = " ".join(rti_groups["createFederationExecutionWithMIM"])
    joined = " ".join(rti_groups["joinFederationExecution"])
    native_surface = "\n".join(connect for overloads in rti_groups.values() for connect in overloads)

    assert "Unauthorized" in connect
    assert "InvalidCredentials" in connect
    assert "RtiConfiguration" in connect
    assert "Credentials" in connect
    assert "InvalidLocalSettingsDesignator" not in connect

    assert {"InvalidFOM", "InconsistentFOM", "ErrorReadingFOM", "CouldNotOpenFOM"} <= set(create.replace(",", " ").split())
    assert {"InvalidMIM", "ErrorReadingMIM", "CouldNotOpenMIM", "DesignatorIsHLAstandardMIM"} <= set(
        create_with_mim.replace(",", " ").split()
    )
    assert "CouldNotCreateLogicalTimeFactory" in joined
    assert "InconsistentFDD" not in native_surface
    assert "ErrorReadingFDD" not in native_surface
    assert "CouldNotOpenFDD" not in native_surface


@pytest.mark.requirements("HLA2025-MOD-007", "HLA2025-NEW-004", "HLA2025-NEW-007")
def test_2025_differentials_capture_replacement_policy_and_mom_switch_surface() -> None:
    rows = _csv_rows(DIFFERENTIAL_SET)
    by_surface_item = {(row["surface_type"], row["item"]): row for row in rows}

    retired_ddm = by_surface_item[("OMT serviceUtilization", "getAvailableDimensionsForClassAttribute")]
    replacement_ddm = by_surface_item[("OMT serviceUtilization", "getAvailableDimensionsForObjectClass")]
    assert retired_ddm["reuse_action"] == "Retire or map"
    assert "Replace with getAvailableDimensionsForObjectClass" in retired_ddm["notes"]
    assert replacement_ddm["reuse_action"] == "Map existing requirement"
    assert replacement_ddm["2025_section_or_location"] == "10.21"

    default_transport = by_surface_item[("OMT serviceUtilization", "changeDefaultAttributeTransportationType")]
    default_order = by_surface_item[("OMT serviceUtilization", "changeDefaultAttributeOrderType")]
    assert default_transport["requirement_action"] == "Add 2025 requirement"
    assert default_transport["2025_section_or_location"] == "6.27"
    assert default_order["requirement_action"] == "Add 2025 requirement"
    assert default_order["2025_section_or_location"] == "8.25"

    service_reporting = by_surface_item[("MIM object attribute", "HLAobjectRoot.HLAmanager.HLAfederate.HLAserviceReporting")]
    report_file = by_surface_item[("MIM object attribute", "HLAobjectRoot.HLAmanager.HLAfederate.HLAreportServiceFile")]
    set_switches_parameter = by_surface_item[
        ("MIM interaction parameter", "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches.HLAserviceReporting")
    ]
    assert service_reporting["reuse_action"] == "Add"
    assert "valueRequired" in service_reporting["2025_detail"]
    assert report_file["reuse_action"] == "Add"
    assert set_switches_parameter["reuse_action"] == "Add"
