from __future__ import annotations

from pathlib import Path

from hla.rti1516e.raw_api import API_METADATA
from hla.verification.repo_internal.verification.asset_plan import build_verification_plan
from hla.verification.repo_internal.verification.repo_seed_artifacts import (
    build_service_conformance_matrix,
    write_service_conformance_matrix_csv,
    write_service_conformance_matrix_json,
)


def test_service_by_service_conformance_matrix_covers_generated_api_surface(tmp_path: Path):
    matrix = build_service_conformance_matrix(version="0.13.0")
    expected_rows = sum(len(API_METADATA[interface]) for interface in ("RTIambassador", "FederateAmbassador"))

    assert matrix["summary"]["row_count"] == expected_rows
    assert matrix["summary"]["interface_counts"]["RTIambassador"] == len(API_METADATA["RTIambassador"])
    assert matrix["summary"]["interface_counts"]["FederateAmbassador"] == len(API_METADATA["FederateAmbassador"])
    assert matrix["summary"]["status_counts"]["callback-helper-tested"] > 0
    assert matrix["summary"]["status_counts"].get("planned-or-adapter-gap", 0) >= 0

    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}
    assert by_method[("RTIambassador", "connect")]["section"] == "1516.1-2010 (2010 edition) §4.2"
    assert by_method[("RTIambassador", "connect")]["requirement_id"] == "REQ-RTI-FM-4_2-connect"
    assert "packages/hla-backend-inmemory/src/hla.backends.inmemory/backend.py" in by_method[("RTIambassador", "connect")]["implementation_refs"]
    assert by_method[("RTIambassador", "connect")]["positive_test_refs"]
    assert by_method[("RTIambassador", "connect")]["artifact_refs"]
    assert "packages/hla-backend-inmemory/src/hla.backends.inmemory/backend.py" in by_method[("RTIambassador", "sendInteraction")]["implementation_refs"]
    assert by_method[("RTIambassador", "sendInteraction")]["negative_evidence"]
    assert by_method[("RTIambassador", "sendInteraction")]["negative_test_refs"]
    assert by_method[("FederateAmbassador", "timeAdvanceGrant")]["callback_helper"] is True
    assert by_method[("FederateAmbassador", "timeAdvanceGrant")]["requirement_id"] == "REQ-FED-TM-8_13-timeAdvanceGrant"


def test_clause4_service_conformance_evidence_prefers_shared_harness_scenarios() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "createFederationExecutionWithMIM"): (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_with_mim_matrix",
        ),
        ("RTIambassador", "disconnect"): (
            "packages/hla-verification/src/hla.verification/scenario_resign.py::run_disconnect_mom_cleanup_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_disconnect_mom_cleanup_matrix",
        ),
        ("RTIambassador", "destroyFederationExecution"): (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_matrix",
        ),
        ("RTIambassador", "listFederationExecutions"): (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_listing_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_listing_matrix",
        ),
        ("RTIambassador", "resignFederationExecution"): (
            "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_precondition_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix",
        ),
        ("FederateAmbassador", "reportFederationExecutions"): (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_listing_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_listing_matrix",
        ),
        ("RTIambassador", "registerFederationSynchronizationPoint"): (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
        ),
        ("RTIambassador", "abortFederationSave"): (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_abort_matrix",
        ),
        ("FederateAmbassador", "federationSaveStatusResponse"): (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
        ),
        ("RTIambassador", "abortFederationRestore"): (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_matrix",
        ),
        ("RTIambassador", "queryFederationRestoreStatus"): (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
        ),
        ("RTIambassador", "requestFederationRestore"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_state_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_state",
        ),
        ("FederateAmbassador", "federationRestored"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_state_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_state",
        ),
    }

    banned_refs = {
        "tests/backends/test_python_backend.py",
        "tests/scenarios/test_startup_sync_fom_java_translation_v09.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]
        assert not any(ref in banned_refs for ref in row["positive_test_refs"])


def test_clause6_service_conformance_evidence_prefers_shared_harness_scenarios() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "publishObjectClassAttributes"): (
            "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_matrix",
        ),
        ("RTIambassador", "unpublishObjectClass"): (
            "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_overload_matrix",
        ),
        ("RTIambassador", "subscribeObjectClassAttributesPassively"): (
            "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_overload_matrix",
        ),
        ("RTIambassador", "registerObjectInstance"): (
            "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix",
        ),
        ("RTIambassador", "requestAttributeValueUpdate"): (
            "packages/hla-verification/src/hla.verification/scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_request_attribute_value_update_matrix",
        ),
        ("RTIambassador", "queryAttributeTransportationType"): (
            "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_transportation_type_matrix",
        ),
        ("FederateAmbassador", "discoverObjectInstance"): (
            "packages/hla-verification/src/hla.verification/scenario_discovery_class.py::run_discovery_class_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_class_matrix",
        ),
        ("FederateAmbassador", "reportAttributeTransportationType"): (
            "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_transportation_type_matrix",
        ),
    }

    banned_refs = {
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]
        assert not any(ref in banned_refs for ref in row["positive_test_refs"])
        assert not any("scenario_declaration_management.py::" in ref for ref in row["evidence"])


def test_clause7_service_conformance_evidence_prefers_shared_harness_scenarios() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "unconditionalAttributeOwnershipDivestiture"): (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_matrix",
        ),
        ("RTIambassador", "attributeOwnershipReleaseDenied"): (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_release_request_ownership_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_denied_ownership_matrix",
        ),
        ("RTIambassador", "queryAttributeOwnership"): (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_query_callback_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix",
        ),
        ("FederateAmbassador", "requestAttributeOwnershipAssumption"): (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::probe_negotiated_attribute_ownership_offer",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_negotiated_divesting_offer_probe_matrix",
        ),
        ("FederateAmbassador", "attributeIsOwnedByRTI"): (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_query_callback_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix",
        ),
    }

    banned_refs = {
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]
        assert not any(ref in banned_refs for ref in row["positive_test_refs"])


def test_clause8_service_conformance_evidence_uses_future_exclusion_harness_for_time_bounds() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "timeAdvanceRequestAvailable"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_future_exclusion_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_future_exclusion",
        ),
        ("RTIambassador", "queryGALT"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_future_exclusion_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_future_exclusion",
        ),
        ("RTIambassador", "queryLITS"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_future_exclusion_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_future_exclusion",
        ),
        ("FederateAmbassador", "timeAdvanceGrant"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_future_exclusion_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_future_exclusion",
        ),
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]


def test_clause6_service_conformance_includes_time_window_interaction_routes() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "sendInteraction"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_output_delivery_scenario",
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_consumer_order_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_output_delivery",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_consumer_order",
        ),
        ("FederateAmbassador", "receiveInteraction"): (
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_output_delivery_scenario",
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_consumer_order_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_output_delivery",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_consumer_order",
        ),
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]


def test_clause9_service_conformance_evidence_prefers_shared_harness_scenarios() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "createRegion"): (
            "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario",
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix",
        ),
        ("RTIambassador", "registerObjectInstanceWithRegions"): (
            "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario",
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix",
        ),
        ("RTIambassador", "subscribeObjectClassAttributesPassivelyWithRegions"): (
            "packages/hla-verification/src/hla.verification/scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario",
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_passive_region_subscription_matrix",
        ),
        ("RTIambassador", "sendInteractionWithRegions"): (
            "packages/hla-verification/src/hla.verification/two_federate_suite_scenarios.py::run_suite_ddm_scenario",
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix",
        ),
        ("RTIambassador", "requestAttributeValueUpdateWithRegions"): (
            "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario",
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix",
        ),
    }

    banned_refs = {
        "tests/verification/test_compliance_slice_v011.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]
        assert not any(ref in banned_refs for ref in row["positive_test_refs"])


def test_clause10_and_12_support_service_conformance_evidence_prefers_shared_harness_scenarios() -> None:
    matrix = build_service_conformance_matrix(version="0.13.0")
    by_method = {(row["interface"], row["method"]): row for row in matrix["rows"]}

    expected_harness_evidence = {
        ("RTIambassador", "getFederateName"): (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
        ),
        ("RTIambassador", "getObjectClassName"): (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
        ),
        ("RTIambassador", "normalizeFederateHandle"): (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
        ),
        ("RTIambassador", "getAttributeHandleFactory"): (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
        ),
        ("RTIambassador", "getAttributeSetRegionSetPairListFactory"): (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
        ),
        ("RTIambassador", "decodeAttributeHandle"): (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
        ),
    }

    banned_refs = {
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_all_methods.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    }

    for key, expected_refs in expected_harness_evidence.items():
        row = by_method[key]
        for ref in expected_refs:
            assert ref in row["evidence"]
        assert not any(ref in banned_refs for ref in row["positive_test_refs"])


def test_service_conformance_matrix_writers_emit_review_assets(tmp_path: Path):
    json_path = write_service_conformance_matrix_json(tmp_path / "matrix.json", version="0.13.0")
    csv_path = write_service_conformance_matrix_csv(tmp_path / "matrix.csv", version="0.13.0")

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "row_id,requirement_id,interface,method" in csv_text
    assert "REQ-RTI-FM-4_2-connect" in csv_text


def test_verification_plan_now_tracks_executable_mom_matrix_and_conformance_matrix():
    plan = build_verification_plan("0.13.0")
    assets = {asset.asset_id: asset for asset in plan.assets}

    assert assets["REQ-MOM-NEG-001"].status == "implemented-slice"
    assert any("test_mom_negative_matrix_parametrized_v013.py" in item for item in assets["REQ-MOM-NEG-001"].evidence)
    assert assets["REQ-MOM-OBSERVER-001"].status == "implemented-slice"
    assert any("test_mom_observer_slice_reconstructs_service_invocation_reporting" in item for item in assets["REQ-MOM-OBSERVER-001"].evidence)
    assert assets["ASSET-CONFORMANCE-MATRIX-001"].status == "implemented-slice"
    assert any("service_conformance_matrix_v0_13.json" in item for item in assets["ASSET-CONFORMANCE-MATRIX-001"].evidence)
    assert assets["ASSET-VERIFICATION-TRACEABILITY-001"].status == "implemented-slice"
    assert any("verification_traceability.csv" in item for item in assets["ASSET-VERIFICATION-TRACEABILITY-001"].evidence)
    assert assets["ASSET-VENDOR-PARITY-PACKET-001"].status == "implemented-slice"
    assert any("test_vendor_parity_artifacts.py" in item for item in assets["ASSET-VENDOR-PARITY-PACKET-001"].evidence)
