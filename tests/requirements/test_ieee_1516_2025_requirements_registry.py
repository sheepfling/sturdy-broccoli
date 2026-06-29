from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = ROOT / "docs/requirements/ieee-1516-2025"
REGISTRY = REGISTRY_DIR / "requirements.json"
CANONICAL_REQUIREMENTS = ROOT / "requirements/2025/canonical_requirements.json"
BACKEND_RESOLUTION = ROOT / "requirements/2025/backend_resolution.json"
EXECUTABLE_REQUIREMENTS = REGISTRY_DIR / "executable_tests/hla_2025_executable_test_requirements_v3.csv"
TEST_SURFACE_MANIFEST = ROOT / "testing/test_surface_manifest.json"


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _assert_contains_all(text: str, snippets: list[str]) -> None:
    for snippet in snippets:
        assert snippet in text


def _canonical_rows_by_id() -> dict[str, dict[str, object]]:
    payload = json.loads(CANONICAL_REQUIREMENTS.read_text(encoding="utf-8"))
    return {row["requirement_id"]: row for row in payload["rows"]}


def _backend_rows_by_id(requirement_id: str) -> list[dict[str, object]]:
    payload = json.loads(BACKEND_RESOLUTION.read_text(encoding="utf-8"))
    return [row for row in payload["rows"] if row["requirement_id"] == requirement_id]


def _lane_owner_commands() -> dict[str, str]:
    payload = json.loads(TEST_SURFACE_MANIFEST.read_text(encoding="utf-8"))
    return {
        lane["id"]: " ".join(lane["owner_command"])
        for lane in payload["lanes"]
        if lane.get("owner_command")
    }


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_ieee_1516_2025_requirements_registry_has_initial_tranche() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    requirements = {row["id"]: row for row in data["requirements"]}

    assert data["extraction_stance"]["classification"]["shall"] == "normative requirement"
    assert len(requirements) == 28
    assert {f"HLA2025-FR-{index:03d}" for index in range(1, 11)} <= set(requirements)
    assert {f"HLA2025-FI-{index:03d}" for index in range(1, 10)} <= set(requirements)
    assert {f"HLA2025-OMT-{index:03d}" for index in range(1, 8)} <= set(requirements)

    assert requirements["HLA2025-REQ-002"]["text_summary"].startswith("Do not label")
    assert "two-federate-core-exchange" in requirements["HLA2025-FR-003"]["tests"]
    assert "full interface service surface accounting" in requirements["HLA2025-FI-002"]["tests"]
    assert "validate_hla_name" in requirements["HLA2025-OMT-001"]["tests"]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-TRACE-001", "HLA2025-BND-003")
def test_2025_canonical_requirement_catalog_maps_rows_to_owner_docs_shards_and_evidence() -> None:
    rows = _canonical_rows_by_id()

    assert len(rows) == 691

    assert rows["HLA2025-FI-SVC-001"]["canonical_status"] == "covered"
    assert rows["HLA2025-FI-SVC-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/federation_management_bounded_proof.md"
    assert rows["HLA2025-FI-SVC-001"]["primary_test_shard"] == "unit-python-2025-core"
    assert rows["HLA2025-FI-SVC-001"]["primary_command"] == "./tools/test-surface run unit-python-2025-core"
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in rows["HLA2025-FI-SVC-001"]["evidence_refs"]

    assert rows["HLA2025-FI-SVC-057"]["canonical_status"] == "covered"
    assert rows["HLA2025-FI-SVC-057"]["owner_doc"] == "docs/requirements/ieee-1516-2025/object_management_bounded_proof.md"
    assert rows["HLA2025-FI-SVC-057"]["primary_test_shard"] == "unit-python-2025-core"
    assert "tests/scenarios/test_object_management_backend_matrix.py" in rows["HLA2025-FI-SVC-057"]["evidence_refs"]

    assert rows["HLA2025-FI-CB-001"]["canonical_status"] == "duplicate/umbrella"
    assert rows["HLA2025-FI-CB-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
    assert rows["HLA2025-FI-CB-001"]["primary_test_shard"] == "unit-shim-tooling"

    assert rows["HLA2025-FR-001"]["canonical_status"] == "duplicate/umbrella"
    assert rows["HLA2025-FR-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/framework_rules.md"
    assert rows["HLA2025-FR-001"]["primary_test_shard"] == "unit-python-2025-core"

    assert rows["HLA2025-OMT-COMP-006"]["canonical_status"] == "covered"
    assert rows["HLA2025-OMT-COMP-006"]["owner_doc"] == "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md"
    assert rows["HLA2025-OMT-COMP-006"]["primary_test_shard"] == "unit-fom-tooling"

    assert rows["HLA2025-FI-RET-001"]["canonical_status"] == "retired/legacy-only"
    assert rows["HLA2025-FI-RET-001"]["owner_doc"] == "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"
    assert rows["HLA2025-FI-RET-001"]["primary_test_shard"] == "unit-foundation"


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003", "HLA2025-FI-CB-001")
def test_2025_backend_resolution_catalog_keeps_backend_and_route_truth_separate_from_canonical_status() -> None:
    callback_rows = _backend_rows_by_id("HLA2025-FI-SVC-193")
    assert len(callback_rows) == 2

    owners = {row["canonical_owner"] for row in callback_rows}
    assert owners == {
        "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md",
        "docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md",
    }

    binding_route_row = next(
        row for row in callback_rows
        if row["canonical_owner"] == "docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md"
    )
    assert binding_route_row["primary_shard"] == "unit-transport-local"
    assert binding_route_row["primary_command"] == "./tools/test-surface run unit-transport-local"
    assert binding_route_row["backend_fields"]["java_surface"] == "present"
    assert binding_route_row["backend_fields"]["cpp_surface"] == "present"
    assert binding_route_row["backend_fields"]["fedpro_surface"] == "not-present-route-boundary-callback-pump-control"

    pitch_row = next(
        row for row in callback_rows
        if row["canonical_owner"] == "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md"
    )
    assert pitch_row["row_kind"] == "requirement-row"
    assert pitch_row["resolution_type"] == "vendor-route-resolution"
    assert pitch_row["primary_shard"] == "unit-transport-local"
    assert pitch_row["primary_command"] == "./tools/test-surface run unit-transport-local"
    assert pitch_row["evidence_refs"] == [
        "artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_summary.json",
        "artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md",
        "packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md",
        "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md",
        "requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv",
    ]
    assert pitch_row["backend_fields"]["pitch_202x_row_resolution"] == "bounded-fi-overlap-only"
    assert pitch_row["backend_fields"]["pitch_202x_vendor_command"] == "./tools/pitch 202x-micro-certify"

    grouped_row = _backend_rows_by_id(
        "group::0-retired-filter-and-replacement-map::Retired / replacement mapping candidates::Federate Interface legacy API"
    )[0]
    assert grouped_row["row_kind"] == "grouped-projection"
    assert grouped_row["resolution_type"] == "grouped-backend-view"
    assert grouped_row["canonical_owner"] == "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"
    assert grouped_row["primary_shard"] == "unit-foundation"
    assert grouped_row["primary_command"] == "./tools/test-surface run unit-foundation"
    assert grouped_row["evidence_refs"] == [
        "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md",
        "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv",
    ]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_canonical_catalog_rows_keep_owner_shard_and_evidence_traceability_coherent() -> None:
    rows = _canonical_rows_by_id()
    lane_commands = _lane_owner_commands()
    allowed_literal_evidence = {
        "linked FI/OMT child rows",
        "migration/compatibility fixture if supported",
    }

    for requirement_id, row in rows.items():
        owner_doc = str(row["owner_doc"])
        owner_path = ROOT / owner_doc
        assert owner_path.exists(), requirement_id

        primary_shard = str(row["primary_test_shard"])
        assert primary_shard in lane_commands, requirement_id
        assert str(row["primary_command"]) == lane_commands[primary_shard], requirement_id

        evidence_refs = list(row["evidence_refs"])
        assert evidence_refs, requirement_id

        for evidence in evidence_refs:
            if evidence in allowed_literal_evidence:
                assert str(row["row_kind"]) in {"framework-umbrella", "legacy-mapping"}, requirement_id
                continue
            evidence_path = ROOT / str(evidence).split(":", 1)[0]
            assert evidence_path.exists(), (requirement_id, evidence)

        if str(row["row_kind"]) in {"framework-umbrella", "legacy-mapping", "delta-umbrella"}:
            assert owner_doc in evidence_refs, requirement_id


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_backend_resolution_rows_keep_owner_shard_and_evidence_traceability_coherent() -> None:
    payload = json.loads(BACKEND_RESOLUTION.read_text(encoding="utf-8"))
    lane_commands = _lane_owner_commands()
    allowed_row_kinds = {"requirement-row", "grouped-projection"}
    allowed_resolution_types = {
        "binding-route-resolution",
        "vendor-group-resolution",
        "vendor-route-resolution",
        "grouped-backend-view",
    }

    for row in payload["rows"]:
        requirement_id = str(row["requirement_id"])
        assert str(row["row_kind"]) in allowed_row_kinds, requirement_id
        assert str(row["resolution_type"]) in allowed_resolution_types, requirement_id

        owner_doc = str(row["canonical_owner"])
        assert owner_doc, requirement_id
        assert (ROOT / owner_doc).exists(), requirement_id

        primary_shard = str(row["primary_shard"])
        assert primary_shard in lane_commands, requirement_id
        assert str(row["primary_command"]) == lane_commands[primary_shard], requirement_id

        evidence_refs = list(row["evidence_refs"])
        assert evidence_refs, requirement_id
        for evidence in evidence_refs:
            evidence_path = ROOT / str(evidence).split(":", 1)[0]
            assert evidence_path.exists(), (requirement_id, evidence)


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_markdown_views_exist() -> None:
    expected = {
        "README.md",
        "binding_and_hosted_route_boundaries.md",
        "callback_bounded_proof.md",
        "callback_binding_deltas.md",
        "declaration_management_bounded_proof.md",
        "ddm_bounded_proof.md",
        "federation_management_bounded_proof.md",
        "fom_backed_scenario_bounded_proof.md",
        "hosted_fedpro_bounded_proof.md",
        "framework_rules.md",
        "federate_interface.md",
        "lookahead_window_bounded_proof.md",
        "object_management_bounded_proof.md",
        "omt_xs_any_extension_tolerance.md",
        "omt.md",
        "ownership_management_bounded_proof.md",
        "pitch_202x_bounded_comparison.md",
        "python1516_2025_direct_bounded_proof.md",
        "python1516_2025_exclusion_boundaries.md",
        "save_restore_bounded_proof.md",
        "support_services_bounded_proof.md",
        "standard_binding_runtime_capability_bounded_proof.md",
        "time_management_bounded_proof.md",
        "traceability_matrix.md",
    }
    assert expected <= {path.name for path in REGISTRY_DIR.iterdir()}


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_readme_indexes_bounded_proof_notes() -> None:
    text = (REGISTRY_DIR / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for filename in (
        "fom_backed_scenario_bounded_proof.md",
        "save_restore_bounded_proof.md",
        "callback_bounded_proof.md",
        "lookahead_window_bounded_proof.md",
        "federation_management_bounded_proof.md",
        "python1516_2025_direct_bounded_proof.md",
        "declaration_management_bounded_proof.md",
        "object_management_bounded_proof.md",
        "ownership_management_bounded_proof.md",
        "ddm_bounded_proof.md",
        "support_services_bounded_proof.md",
        "standard_binding_runtime_capability_bounded_proof.md",
        "time_management_bounded_proof.md",
        "hosted_fedpro_bounded_proof.md",
        "binding_and_hosted_route_boundaries.md",
        "pitch_202x_bounded_comparison.md",
        "python1516_2025_exclusion_boundaries.md",
        "callback_binding_deltas.md",
        "omt_xs_any_extension_tolerance.md",
    ):
        assert f"`{filename}`" in text

    assert "bounded requirement-facing proof note" in normalized
    assert "main `python1516_2025` lane plus hosted replay" in normalized
    assert "tracked Proto2025 and Target/Radar example/FOM-backed scenario suite over the main `python1516_2025` lanes" in normalized
    assert "save/restore lifecycle control, shared rollback, routing/policy rollback, ownership rollback, and time-window/time-state rollback" in normalized
    assert "callback-delivery families, callback-control hygiene, and direct-versus-hosted callback surface boundaries over the main `python1516_2025` runtime" in normalized
    assert "Target/Radar lookahead ladder, including future-exclusion, output ordering, pipeline overlap, negative-oracle guards, and bounded save/restore window rollback" in normalized
    assert "direct `python1516_2025` main-surface runtime lane over `hla-backend-python1516-2025`" in normalized
    assert "Java, C++, and hosted FedPro binding/route boundaries over the main `python1516_2025` runtime" in text
    assert "explicit exclusion map for legacy aliases, Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope OMT extension semantics" in normalized


@pytest.mark.requirements(
    "HLA2025-FI-004",
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-010",
    "HLA2025-FI-SVC-011",
)
def test_ieee_1516_2025_requirements_readme_calls_out_basic_execution_rules() -> None:
    text = (REGISTRY_DIR / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Basic Execution Rules" in text
    assert 'canonical 2025 "have we joined yet?" rule family' in text
    assert "connect before RTI interaction" in normalized
    assert "joined versus not-joined execution-member guards" in normalized
    assert "plain object registration rejected until the caller has joined" in normalized
    assert "delete, local-delete, update, interaction, query, and region-gated DDM services rejected until the caller has joined" in normalized
    assert "Update Attribute Values" in text
    assert "Request Attribute Value Update" in text
    assert "Query Attribute Transportation Type" in text
    assert "Send Interaction With Regions" in text
    assert "Request Attribute Value Update With Regions" in text
    assert "after resign, those execution-affecting services continue to reject the caller as no longer joined, including delete/local-delete plus the region-gated DDM send and request-update variants" in normalized
    assert "destroy rejected while federates are still joined" in normalized
    assert "after destroy succeeds, later destroy or join attempts against that missing federation reject with `FederationExecutionDoesNotExist`" in normalized
    assert "federation membership listing and reporting" in normalized
    assert "resign and disconnect cleanup after membership changes" in normalized
    assert "requirements/2025/canonical_requirements.json" in text
    assert "requirements/2025/backend_resolution.json" in text
    assert "../execution_membership_rules.md" in text
    assert "`federation_management_bounded_proof.md`" in text
    assert "`object_management_bounded_proof.md`" in text
    assert "`ddm_bounded_proof.md`" in text
    assert "hla_2025_executable_test_requirements_v3.csv" in text
    assert "`HLA2025-FI-004-XT-REQ-CONNECT_BEFORE_RTI_INTERACTION`" in text
    assert "`HLA2025-FI-SVC-005`, `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-010`, and" in text
    assert "`HLA2025-FI-SVC-011`" in text
    assert "`HLA2025-FI-SVC-057`" in text
    assert "`HLA2025-FI-SVC-065`" in text
    assert "`HLA2025-FI-SVC-067`" in text
    assert "`HLA2025-FI-SVC-059`" in text
    assert "`HLA2025-FI-SVC-061`" in text
    assert "`HLA2025-FI-SVC-070`" in text
    assert "`HLA2025-FI-SVC-077`" in text
    assert "`HLA2025-FI-SVC-136`" in text
    assert "`HLA2025-FI-SVC-137`" in text
    assert "`NotConnected`" in text
    assert "`FederateNotExecutionMember`" in text
    assert "`FederatesCurrentlyJoined`" in text
    assert "`FederationExecutionDoesNotExist`" in text
    assert "The intended 2025 state-machine reading is:" in text
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py" in text
    assert "tests/transport/test_grpc_transport_2025.py" in text
    assert "tests/backends/test_python_backend_object_ownership_extended.py" in text
    assert "tests/backends/test_python_backend_time_ddm_extended.py" in text
    assert "tests/scenarios/test_federation_management_backend_matrix.py" in text
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py" in text
    assert "./tools/test-focus run execution-membership" in text
    assert "direct lane, hosted 2025 gRPC/FedPro route, and REST-hosted Python route" in normalized


@pytest.mark.requirements("HLA2025-FI-SVC-060", "HLA2025-FI-SVC-070", "HLA2025-FI-SVC-074")
def test_2025_object_management_bounded_proof_calls_out_execution_member_guards() -> None:
    text = (REGISTRY_DIR / "object_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Execution-membership guard coverage is part of this bounded claim" in normalized
    assert "Before join, after resign, or after disconnect" in text
    assert "`NotConnected` or `FederateNotExecutionMember`" in text
    assert "`HLA2025-FI-SVC-057`" in text
    assert "`HLA2025-FI-SVC-065`" in text
    assert "`HLA2025-FI-SVC-067`" in text
    assert "`HLA2025-FI-SVC-059`" in text
    assert "`HLA2025-FI-SVC-061`" in text
    assert "`HLA2025-FI-SVC-070`" in text
    assert "`HLA2025-FI-SVC-077`" in text
    assert "tests/backends/test_python_backend_object_ownership_extended.py" in text
    assert "tests/backends/test_python_backend_time_ddm_extended.py" in text
    assert "test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore" in text
    assert "test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore" in text
    assert "test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore" in text
    assert "test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore" in text
    assert "test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore" in text
    assert "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "REST-hosted Python route is part of the narrower" in text
    assert "it is not currently promoted as a full object-management family replay owner here" in normalized


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-MIL-001", "HLA2025-MIL-002")
def test_hosted_fedpro_bounded_proof_markdown_keeps_main_runtime_identity_and_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "hosted_fedpro_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current hosted-route claim for `python1516_2025-fedpro-grpc`." in normalized
    assert "bounded transport/runtime slice rather than a second RTI implementation family" in normalized
    assert "sole repo-owned IEEE 1516.1-2025 Python RTI implementation lane" in normalized
    assert "The hosted route is parity-covered across the tracked scenario families" in normalized
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`docs/backend_route_inventory_remote.md`" in text
    assert "`packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`" in text
    assert "`docs/requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md`" in text
    assert "`docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`" in text
    assert "`federation_lifecycle`" in text
    assert "`time_management`" in text
    assert "`support_services`" in text
    assert "`hla-backend-python1516-2025`" in text
    assert "shared Target/Radar example path" in normalized
    assert "`./tools/python verify-routes-2025`" in text
    assert "`./tools/python verify-main-2025`" in text
    assert "does not claim that `python1516_2025-fedpro-grpc` is a second full RTI implementation lane" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_readme_tracks_current_runtime_proof_lane() -> None:
    text = (REGISTRY_DIR / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Current Technical Lane" in text
    assert "deeper runtime-proof expansion over the promoted `python1516_2025` RTI surface" in normalized
    assert "the tracked example/FOM-backed scenario bounded proof note" in normalized
    assert "the dedicated save/restore bounded proof note" in normalized
    assert "the dedicated callback bounded proof note" in normalized
    assert "the dedicated lookahead-window bounded proof note" in normalized
    assert "the dedicated direct `python1516_2025` bounded proof note" in normalized
    assert "the dedicated hosted FedPro bounded proof plus route-parity evidence that replays those runtime families" in normalized
    assert "wrapper-only shim boundaries" in normalized
    assert "one explicit exclusion map that gathers the non-claim areas around the main `python1516_2025` runtime lane" in normalized
    assert "FOM/OMT validation still matters inside that lane" in normalized
    assert "one proof family inside the broader 2025 runtime-evidence closeout" in normalized

@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003")
def test_python2025_exclusion_boundaries_markdown_gathers_non_claim_areas() -> None:
    text = (REGISTRY_DIR / "python1516_2025_exclusion_boundaries.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records what the repository is explicitly **not** claiming" in text
    assert "main IEEE 1516.1-2025 Python RTI implementation statement" in text
    assert "`hla-backend-python1516-2025` is the sole repo-owned Python RTI implementation lane" in normalized
    assert "Legacy aliases and shim imports" in text
    assert "Java/C++ bindings" in text
    assert "Hosted transport boundaries" in text
    assert "Duplicate/umbrella rows" in text
    assert "Retired/legacy-only rows" in text
    assert "OMT extension semantics" in text
    assert "`hla-backend-shim` is deprecated temporary import-compatibility scaffolding and wrapper-only compatibility support" in normalized
    assert "not alternate Python RTIs and not exhaustive cross-binding behavior conformance" in normalized
    assert "bounded hosted transport/runtime slice over `hla-backend-python1516-2025`" in normalized
    assert "normalization aids and mapping notes rather than standalone one-row conformance assertions" in normalized
    assert "explicit exclusions from active 2025 support obligations" in normalized
    assert "direct `python1516_2025` lane plus hosted FedPro replay" in text
    assert "Arbitrary third-party extension execution semantics remain out of scope" in text
    assert "`../../python_rti_backend.md`" in text
    assert "`hosted_fedpro_bounded_proof.md`" in text
    assert "`standard_binding_runtime_capability_bounded_proof.md`" in text
    assert "`retired_legacy_mapping.md`" in text
    assert "`omt_xs_any_extension_tolerance.md`" in text


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-MIL-001", "HLA2025-MIL-002")
def test_python2025_direct_bounded_proof_markdown_keeps_main_lane_claim_explicit() -> None:
    text = (REGISTRY_DIR / "python1516_2025_direct_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current direct-lane claim for `python1516_2025`." in normalized
    assert "The direct lane is the main executable bounded proof surface for the current 2025 Python RTI." in normalized
    assert "sole repo-owned IEEE 1516.1-2025 Python RTI implementation lane" in normalized
    assert "`hla-backend-python1516-2025`" in text
    assert "`federation_lifecycle`" in text
    assert "`object_exchange`" in text
    assert "`ownership`" in text
    assert "`ddm`" in text
    assert "`time_management`" in text
    assert "`save_restore`" in text
    assert "`mom`" in text
    assert "`support_services`" in text
    assert "`omt_validation`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/scenarios/test_target_radar_scenario.py`" in text
    assert "`tests/test_fom_target_radar_split_package.py`" in text
    assert "`tests/test_rti1516_2025_validation.py`" in text
    assert "`docs/test_surface.md`" in text
    assert "`docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md`" in text
    assert "`docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`" in text
    assert "verify-main-2025" in text
    assert "`./tools/python verify-routes-2025`" in text
    assert "not a wrapper-owned surface and not a full unqualified conformance claim" in normalized
    assert "does not treat `hla-backend-shim` as part of the implementation owner claim for this lane" in normalized


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-MIL-002", "HLA2025-FR-001", "HLA2025-FR-003", "HLA2025-FR-004")
def test_fom_backed_scenario_bounded_proof_markdown_keeps_tracked_suite_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "fom_backed_scenario_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing claim for tracked example and FOM-backed scenario execution" in normalized
    assert "`message-test`" in text
    assert "`space-lite`" in text
    assert "`time-mgmt-test`" in text
    assert "`target-radar`" in text
    assert "`tests/scenarios/test_proto2025_fom_showcase.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`Proto2025_MessageTest.xml`" in text
    assert "`Proto2025_SpaceLite.xml`" in text
    assert "`Proto2025_TimeMgmtTest.xml`" in text
    assert "It does not yet prove every conceivable example FOM scenario outside the tracked suite." in normalized
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner" in normalized


@pytest.mark.requirements("HLA2025-FI-SVC-018", "HLA2025-FI-SVC-024", "HLA2025-FI-005", "HLA2025-REQ-002")
def test_save_restore_bounded_proof_markdown_keeps_rollback_family_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "save_restore_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing save/restore claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`" in text
    assert "`HLA2025-REQ-002`" in text
    assert "`HLA2025-FI-SVC-024`, `HLA2025-FI-SVC-025`, `HLA2025-FI-SVC-033`, `HLA2025-FI-SVC-034`" in text
    assert "`HLA2025-FI-005`" in text
    assert "`HLA2025-FI-001`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/transport/test_rest_transport.py`" in text
    assert "`tests/scenarios/test_save_restore_backend_matrix.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`./tools/test-focus run python-2025-save-restore`" in text
    assert "`./tools/python verify-main-2025`" in text
    assert "`./tools/python verify-routes-2025`" in text
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner" in normalized
    assert "Hosted FedPro remains transport-seam evidence over `hla-backend-python1516-2025`" in text
    assert "REST-hosted Python route" in text
    assert "the only current save/restore family promoted to the REST-hosted Python route" in normalized
    assert "`HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`" in text
    assert "`HLA2025-FI-SVC-030`, `HLA2025-FI-SVC-031`, and" in text
    assert "`HLA2025-FI-SVC-032`" in text
    assert "broader rollback families remain direct-lane plus hosted FedPro proof" in normalized
    assert "does not claim that every save/restore requirement now has its own standalone clause-by-clause conformance proof" in normalized


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-FI-CB-005", "HLA2025-FI-CB-008", "HLA2025-BIND-FEDPRO-001")
def test_callback_bounded_proof_markdown_keeps_callback_family_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "callback_bounded_proof.md").read_text(encoding="utf-8")
    normalized = _normalize(text)

    _assert_contains_all(
        normalized,
        [
            "This note records the repo's current requirement-facing callback claim as a bounded proof statement",
            "This note is intentionally a cross-family bounded callback evidence surface over linked child rows",
            "`HLA2025-FI-SVC-193`, `HLA2025-FI-SVC-194`, `HLA2025-FI-SVC-195`, and `HLA2025-FI-SVC-196`",
            "not as a license to relabel every touched child service row as callback closure",
            "direct-lane plus hosted FedPro callback evidence",
            "`hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner",
            "does not claim exhaustive callback-by-callback signature equivalence",
            "REST-hosted Python route is not currently promoted as an owner for these 2025 callback proof families",
            "the hosted transport seam, 2025 execution-membership control, and selected lifecycle/control-flow witnesses",
        ],
    )
    _assert_contains_all(
        text,
        [
            "Declaration relevance and interest advisories",
            "Federation sync, save/restore, and reporting callbacks",
            "Object discovery, delivery, and removal",
            "Object advisory, transport, and name-reservation callbacks",
            "Supplemental callback context and region metadata",
            "Ownership negotiation and query callbacks",
            "Time grant, regulation, and retraction callbacks",
            "Callback control and backlog hygiene",
            "`tests/test_rti1516_2025_python1516_2025_runtime.py`",
            "`tests/transport/test_grpc_transport_2025.py`",
            "`tests/scenarios/test_federation_management_backend_matrix.py`",
            "`tests/scenarios/test_save_restore_backend_matrix.py`",
            "`tests/scenarios/test_ownership_management_backend_matrix.py`",
            "`tests/scenarios/test_python_route_parity.py`",
            "`./tools/test-focus run python-2025-mom-callbacks`",
            "`./tools/python verify-main-2025`",
            "`./tools/python verify-routes-2025`",
            "direct `python1516_2025` lane plus hosted FedPro replay",
            "Hosted FedPro remains transport-seam evidence over `hla-backend-python1516-2025`",
        ],
    )



@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FR-001", "HLA2025-FR-010")
def test_framework_rules_markdown_maps_umbrella_rows_to_child_evidence() -> None:
    text = (REGISTRY_DIR / "framework_rules.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "These rows remain `duplicate/umbrella` in the canonical 2025 requirement catalog." in normalized
    assert "`HLA2025-REQ-001`, `HLA2025-OMT-001`, `HLA2025-OMT-005`, `HLA2025-OMT-006`" in text
    assert "`HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`" in text
    assert "`HLA2025-FI-009`, `HLA2025-MOD-006`, `HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-112`, `HLA2025-FI-SVC-121`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "| HLA2025-FR-005 |" in text
    assert "| HLA2025-FR-010 |" in text
    assert "The primary implementation lane behind the executable anchors above is `hla-backend-python1516-2025`." in normalized
    assert "`hla-backend-shim` is not a runtime owner for these framework rules." in normalized
    assert "Each rule closes only through linked child FI, OMT, and runtime evidence" in normalized
    assert "non-standalone parent or normalization surface" in normalized
    assert "do not count a framework umbrella row as a separate covered implementation bucket" in normalized
    assert "do not promote them to standalone `covered`" in text


@pytest.mark.requirements("HLA2025-FI-SVC-107", "HLA2025-FI-SVC-116", "HLA2025-FI-SVC-121", "HLA2025-MOD-006")
def test_lookahead_window_bounded_proof_markdown_keeps_proof_ladder_and_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "lookahead_window_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing claim for lookahead window closure" in normalized
    assert "`time-window-core`" in text
    assert "`time-window-future-exclusion`" in text
    assert "`time-window-output-delivery`" in text
    assert "`time-window-consumer-order`" in text
    assert "`time-window-pipeline-two-scans`" in text
    assert "`time-window-receive-order-poison`" in text
    assert "`time-window-save-restore-window-state`" in text
    assert "`time-window-save-restore-output-resume`" in text
    assert "`time-window-save-restore-pipeline-resume`" in text
    assert "`lookahead-processing-window-certified`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`./tools/pitch time-window-probe`" in text
    assert "`./tools/pitch time-window-restore-state-probe`" in text
    assert "hosted FedPro replay" in normalized
    assert "direct `python1516_2025` plus hosted FedPro replay evidence" in normalized
    assert "must fail if the RTI allows a future-message exclusion bug or a closed-window causality leak" in normalized
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner" in normalized


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-BIND-FEDPRO-001", "HLA2025-BIND-JAVA-CPP-001")
def test_callback_binding_delta_markdown_maps_umbrella_rows_to_runtime_and_binding_evidence() -> None:
    text = (REGISTRY_DIR / "callback_binding_deltas.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "These rows remain `duplicate/umbrella` in the canonical 2025 requirement catalog." in normalized
    assert "`HLA2025-FI-SVC-193`" in text
    assert "`HLA2025-FI-SVC-194`" in text
    assert "`HLA2025-FI-SVC-195`, `HLA2025-FI-SVC-196`" in text
    assert "`HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, `HLA2025-BND-003`" in text
    assert "`HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, `HLA2025-FI-004`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "| HLA2025-FI-CB-008 |" in text
    assert "| HLA2025-FI-CFG-001 |" in text
    assert "| HLA2025-FI-AUTH-001 |" in text
    assert "| HLA2025-BIND-JAVA-CPP-001 |" in text
    assert "The primary runtime owner behind the executable anchors above is `hla-backend-python1516-2025`." in normalized
    assert "`hla-backend-shim`, `hla-backend-cpp-shim`, and the Java bridge packages are wrapper/binding surfaces over that runtime lane;" in normalized
    assert "Each row closes only through the linked child FI/binding rows" in normalized
    assert "non-standalone delta or normalization surface" in normalized
    assert "explicit hosted FedPro transport calls for enable/disable semantics" in text
    assert "direct `python1516_2025` lane plus hosted FedPro replay" in text
    assert "no narrower standalone callback-control claim was identified" in normalized
    assert "no narrower standalone directed-interaction callback-parameterization claim was identified" in normalized
    assert "no narrower standalone FedPro protocol-capability claim was identified" in normalized
    assert "no narrower standalone Java/C++ binding-capability claim was identified" in normalized
    assert "no narrower standalone configuration-result or authorization-credentials claim was identified" in normalized
    assert "these rows stay `duplicate/umbrella`, not standalone runtime proof rows" in text
    assert "The repo should not promote these rows to standalone `covered` runtime claims" in text


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003")
def test_binding_and_hosted_boundary_markdown_keeps_python2025_as_main_runtime_lane() -> None:
    text = (REGISTRY_DIR / "binding_and_hosted_route_boundaries.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing reading for the three binding rows." in normalized
    assert "`tests/requirements/test_2025_tail_backlog_evidence.py`" in text
    assert "`tests/requirements/test_2025_route_parity_matrix.py`" in text
    assert "`tests/backends/test_standard_shim_artifacts.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto`" in text
    assert "`hla-backend-python1516-2025` is the only main 2025 Python RTI implementation lane" in normalized
    assert "bounded adaptation and hosted-route owner surface" in normalized
    assert "not an independent Java RTI" in text
    assert "not an independent C++ RTI" in text
    assert "not a second RTI implementation lane" in text


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-BND-003")
def test_pitch_202x_bounded_comparison_markdown_keeps_bounded_backend_resolution_explicit() -> None:
    text = (REGISTRY_DIR / "pitch_202x_bounded_comparison.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "It is the canonical owner doc behind the 2025 backend-resolution reading for this bounded vendor lane." in normalized
    assert "downstream projections of that backend-resolution story, not requirement truth" in normalized
    assert "It does not promote Pitch into a second 2025 RTI owner." in normalized
    assert "It does not claim IEEE 1516.1-2025 vendor conformance." in normalized
    assert "`requirements/2025/backend_resolution.json`" in text
    assert "`requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`" in text
    assert "`requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv`" in text
    assert "`./tools/pitch 202x-micro-certify`" in text
    assert "`pitch-202x-jpype`, `pitch-202x-py4j`" in text
    assert "bounded backend-resolution owner surface" in normalized
    assert "`hla-backend-shim` remains a compatibility wrapper and is not a runtime owner" in normalized
    assert "Java bridge packages and `hla-backend-cpp-shim` remain wrapper/binding surfaces" in normalized
    assert "Hosted FedPro is a bounded transport/runtime slice over `hla-backend-python1516-2025`;" in normalized


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-BND-002")
def test_standard_binding_runtime_capability_markdown_keeps_bounded_binding_claim_explicit() -> None:
    text = (REGISTRY_DIR / "standard_binding_runtime_capability_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing claim for the standard Java and C++ 2025 binding routes." in normalized
    assert "artifact-gated/runtime-capability traces over the main `hla-backend-python1516-2025` runtime" in normalized
    assert "Both Java and C++ standard-route families are parity-covered across the tracked eight scenario families" in normalized
    assert "`java-standard-2025-jpype`" in text
    assert "`java-standard-2025-py4j`" in text
    assert "`cpp-standard-2025-pybind`" in text
    assert "`cpp-standard-2025-grpc`" in text
    assert "`tests/backends/test_standard_shim_artifacts.py`" in text
    assert "`docs/evidence/shim_routes/java-standard-2025.json`" in text
    assert "`docs/evidence/shim_routes/cpp-standard-2025.json`" in text
    assert "`packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`" in text
    assert "does not claim exhaustive cross-binding behavior equivalence" in normalized


@pytest.mark.requirements("HLA2025-OMT-COMP-006", "HLA2025-OMT-COMP-039", "HLA2025-OMT-COMP-224")
def test_omt_xs_any_markdown_keeps_bounded_payload_preservation_claim_explicit() -> None:
    text = (REGISTRY_DIR / "omt_xs_any_extension_tolerance.md").read_text(encoding="utf-8")
    normalized = _normalize(text)

    _assert_contains_all(
        normalized.lower(),
        [
            "this bounded-proof note covers the 45 omt component rows",
            "payload preservation, schema-tolerant parsing, and serializer round-trip",
            "does not claim arbitrary third-party extension execution semantics",
            "bounded omt extension-tolerance owner surface",
        ],
    )
    _assert_contains_all(
        text,
        [
            "`HLA2025-OMT-COMP-006`, `HLA2025-OMT-COMP-008`",
            "`HLA2025-OMT-COMP-019`, `HLA2025-OMT-COMP-021`, `HLA2025-OMT-COMP-027`",
            "`HLA2025-OMT-COMP-102`, `HLA2025-OMT-COMP-110`, `HLA2025-OMT-COMP-134`",
            "`HLA2025-OMT-COMP-145`, `HLA2025-OMT-COMP-147`, `HLA2025-OMT-COMP-154`",
            "`HLA2025-OMT-COMP-202`, `HLA2025-OMT-COMP-204`, `HLA2025-OMT-COMP-208`",
            "### `object-model-root-and-identity`",
            "### `container-table-and-reference-extension-points`",
            "`tests/test_rti1516_2025_validation.py`",
            "`packages/hla-rti1516e/src/hla/rti1516e/fom.py`",
            "does not claim arbitrary third-party extension execution semantics",
        ],
    )


@pytest.mark.requirements("HLA2025-REQ-001")
def test_support_services_bounded_proof_markdown_keeps_python_lane_and_bounded_route_claim_explicit() -> None:
    text = (REGISTRY_DIR / "support_services_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current support-services claim as a bounded, requirement-facing proof statement." in normalized
    assert "per-service runtime traceability across the Python 2025 lanes" in normalized
    assert "hosted FedPro remains a bounded runtime slice rather than a full support-service conformance route" in normalized
    assert "REST-hosted Python route is not yet promoted to these support-service proof families" in normalized
    assert "The canonical support-service owner rows carried by this note are the true Clause 10 support-service rows" in normalized
    assert "`HLA2025-FI-SVC-138` through `HLA2025-FI-SVC-156`" in text
    assert "`HLA2025-FI-SVC-158`, `HLA2025-FI-SVC-162` through `HLA2025-FI-SVC-196`" in normalized
    assert "`name-reservation-and-release-flows` is backed by linked object-management rows" in normalized
    assert "`HLA2025-FI-SVC-157`, `HLA2025-FI-SVC-159`, `HLA2025-FI-SVC-160`, `HLA2025-FI-SVC-161`, or `HLA2025-FI-SVC-164` stay owned by the DDM note" in normalized
    assert "`name-reservation-and-release-flows`" in text
    assert "`identity-catalog-and-handle-normalization-lookups`" in text
    assert "`factory-decode-and-hosted-support-seam`" in text
    assert "| Family | Focus | Direct-backed | FedPro-hosted-backed | REST-hosted-backed |" in text
    assert "| `name-reservation-and-release-flows`" in text
    assert "| Yes | Yes | No |" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`./tools/test-focus run python-2025-mom-callbacks`" in text
    assert "`./tools/python verify-main-2025`" in text
    assert "`./tools/python verify-routes-2025`" in text
    assert "does not currently maintain matching REST-hosted family replay" in normalized
    assert "does not promote the REST-hosted Python route to the named support-service proof families above" in normalized
    assert "not as a license to relabel OM or DDM rows as support-service closure" in normalized


@pytest.mark.requirements("HLA2025-FI-SVC-101", "HLA2025-FI-SVC-107", "HLA2025-FI-SVC-116", "HLA2025-FI-SVC-121")
def test_time_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "time_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = _normalize(text)

    _assert_contains_all(
        normalized,
        [
            "This note records the repo's current requirement-facing time-management claim as a bounded proof statement",
            "The canonical time-management owner rows carried by this note are the Clause 8 service rows `HLA2025-FI-SVC-101` through `HLA2025-FI-SVC-125`.",
            "`HLA2025-FI-009` and `HLA2025-MOD-006` are intentionally linked helper rows",
            "not as a license to relabel broader interface-model rows as time-service closure",
            "direct-lane and hosted FedPro replay proof families",
            "direct `python1516_2025` lane and hosted FedPro replay both exercise the repo's time-window core",
            "`hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner",
            "useful vendor credence",
        ],
    )
    _assert_contains_all(
        text,
        [
            "`HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-102`, `HLA2025-FI-SVC-103`",
            "`HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-108`, `HLA2025-FI-SVC-109`",
            "`HLA2025-FI-SVC-116`, `HLA2025-FI-SVC-117`, `HLA2025-FI-SVC-118`",
            "`HLA2025-FI-SVC-121`, `HLA2025-FI-SVC-122`, `HLA2025-FI-SVC-123`",
            "`tests/test_rti1516_2025_python1516_2025_runtime.py`",
            "`tests/transport/test_grpc_transport_2025.py`",
            "`tests/backends/test_shim_route_trace_evidence.py`",
            "`./tools/test-focus run python-2025-time`",
            "`./tools/python verify-main-2025`",
            "`./tools/python verify-routes-2025`",
            "`./tools/pitch time-window-probe`",
            "`./tools/pitch time-window-restore-state-probe`",
            "do not replace the broader `hla-backend-python1516-2025` proof",
        ],
    )


@pytest.mark.requirements("HLA2025-REQ-001")
def test_federation_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "federation_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = _normalize(text)

    _assert_contains_all(
        normalized,
        [
            "This note records the repo's current requirement-facing federation-management claim as a bounded proof statement",
            "direct-lane and hosted FedPro replay proof families",
            "direct `python1516_2025` lane plus hosted FedPro replay",
            "`hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner",
        ],
    )
    _assert_contains_all(
        text,
        [
            "`HLA2025-FI-SVC-001`, `HLA2025-FI-SVC-002`, `HLA2025-FI-SVC-004`",
            "`HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009`, `HLA2025-FI-SVC-010`",
            "`HLA2025-FI-SVC-013`, `HLA2025-FI-SVC-014`, `HLA2025-FI-SVC-015`",
            "`HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`",
            "`tests/test_rti1516_2025_python1516_2025_runtime.py`",
            "`tests/transport/test_grpc_transport_2025.py`",
            "`tests/scenarios/test_federation_management_backend_matrix.py`",
            "Execution-membership guard coverage is part of this bounded claim",
            "Before join, after resign, or after disconnect",
            "`NotConnected` or `FederateNotExecutionMember`",
            "REST-hosted Python route",
            "`destroyFederationExecution` rejects with `FederatesCurrentlyJoined`",
            "`FederationExecutionDoesNotExist`",
            "Current exact execution-membership evidence anchors for this 2025 reading",
            "test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end",
            "test_2025_provider_runs_resign_precondition_scenario_end_to_end",
            "test_2025_provider_reports_federation_executions_and_members",
            "test_python_backend_join_precondition_matrix",
            "test_python_backend_resign_precondition_matrix",
            "test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route",
            "test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route",
            "test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route",
            "test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario",
            "test_2025_rest_transport_server_runs_shared_join_precondition_scenario",
            "test_2025_rest_transport_server_runs_shared_resign_precondition_scenario",
            "`./tools/test-focus run execution-membership`",
            "`./tools/python verify-main-2025`",
            "`./tools/python verify-routes-2025`",
        ],
    )


@pytest.mark.requirements("HLA2025-REQ-001")
def test_declaration_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "declaration_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing declaration-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-035`, `HLA2025-FI-SVC-036`, `HLA2025-FI-SVC-037`" in text
    assert "`HLA2025-FI-SVC-041`, `HLA2025-FI-SVC-042`, `HLA2025-FI-SVC-043`" in text
    assert "`HLA2025-FI-SVC-047`, `HLA2025-FI-SVC-048`, `HLA2025-FI-SVC-049`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/scenarios/test_object_management_backend_matrix.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "The canonical declaration-management owner rows carried by this note are the Clause 5 service rows `HLA2025-FI-SVC-035` through `HLA2025-FI-SVC-050`." in normalized
    assert "`HLA2025-FI-SVC-039`, `HLA2025-FI-SVC-040`, `HLA2025-FI-SVC-045`, and `HLA2025-FI-SVC-046` remain declaration owner rows here" in normalized
    assert "not as a license to relabel later object-exchange routing or callback-only helper evidence as declaration closure" in normalized
    assert "direct-lane and hosted FedPro replay proof families" in normalized
    assert "direct `python1516_2025` lane plus hosted FedPro replay" in normalized
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_object_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "object_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing object-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-051`, `HLA2025-FI-SVC-052`, `HLA2025-FI-SVC-053`" in text
    assert "`HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`" in text
    assert "`HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-066`, `HLA2025-FI-SVC-067`" in text
    assert "`HLA2025-FI-SVC-074`, `HLA2025-FI-SVC-075`, `HLA2025-FI-SVC-076`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/scenarios/test_object_management_backend_matrix.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "direct-lane and hosted FedPro replay proof families" in normalized
    assert "direct `python1516_2025` lane plus hosted FedPro replay" in normalized
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ownership_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "ownership_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing ownership-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-084`, `HLA2025-FI-SVC-086`" in text
    assert "`HLA2025-FI-SVC-092`, `HLA2025-FI-SVC-093`, `HLA2025-FI-SVC-094`" in text
    assert "`HLA2025-FI-SVC-085`, `HLA2025-FI-SVC-088`, `HLA2025-FI-SVC-089`" in text
    assert "`HLA2025-FI-SVC-090`, `HLA2025-FI-SVC-091`, `HLA2025-FI-SVC-096`, `HLA2025-FI-SVC-097`" in text
    assert "| Query visibility | `HLA2025-FI-SVC-098`, `HLA2025-FI-SVC-099` |" in text
    assert "| Resign policies | `HLA2025-FI-SVC-100` |" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/scenarios/test_ownership_management_backend_matrix.py`" in text
    assert "`tests/backends/test_python_backend_object_ownership_extended.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/transport/test_rest_transport.py`" in text
    assert "`./tools/test-focus run python-2025-ownership`" in text
    assert "`./tools/python verify-main-2025`" in text
    assert "`./tools/python verify-routes-2025`" in text
    assert "The canonical ownership-management owner rows carried by this note are the Clause 7 service rows `HLA2025-FI-SVC-083` through `HLA2025-FI-SVC-100`." in normalized
    assert "`HLA2025-FI-005` remains a linked helper row rather than a canonical ownership-service owner row" in normalized
    assert "not as a license to relabel broader save/restore owner rows as ownership closure" in normalized
    assert "direct-lane and hosted FedPro replay proof families" in normalized
    assert "direct `python1516_2025` lane plus hosted FedPro replay" in normalized
    assert "REST-hosted Python route now extends the transfer, release, acquisition, cancellation, and query-visibility families" in normalized
    assert "REST-hosted Python route is not yet promoted to this narrower resign-policy claim" in normalized
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ddm_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "ddm_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing data-distribution- management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-126`, `HLA2025-FI-SVC-127`, `HLA2025-FI-SVC-130`" in text
    assert "`HLA2025-FI-SVC-128`, `HLA2025-FI-SVC-129`, `HLA2025-FI-SVC-131`, `HLA2025-FI-SVC-132`, `HLA2025-FI-SVC-133`, `HLA2025-FI-SVC-137`" in text
    assert "`HLA2025-FI-SVC-134`, `HLA2025-FI-SVC-135`" in text
    assert "`HLA2025-FI-SVC-136`" in text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py`" in text
    assert "`tests/backends/test_python_backend_time_ddm_extended.py`" in text
    assert "`tests/scenarios/test_ddm_backend_matrix.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`./tools/test-focus run python-2025-ddm`" in text
    assert "`./tools/python verify-main-2025`" in text
    assert "`./tools/python verify-routes-2025`" in text
    assert "Execution-membership guard coverage is also part of this bounded claim" in text
    assert "`sendInteractionWithRegions` and" in text
    assert "`requestAttributeValueUpdateWithRegions` are expected to reject the caller" in text
    assert "`NotConnected` or `FederateNotExecutionMember`" in text
    assert "`HLA2025-FI-SVC-136`" in text
    assert "`HLA2025-FI-SVC-137`" in text
    assert "test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore" in text
    assert "REST-hosted Python route is part of the narrower" in text
    assert "it is not currently promoted as a full DDM family replay owner here" in normalized
    assert "direct-lane and hosted FedPro replay proof families" in normalized
    assert "direct `python1516_2025` lane plus hosted FedPro replay" in normalized
    assert "`hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner" in normalized
