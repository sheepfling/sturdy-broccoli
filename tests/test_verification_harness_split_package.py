from __future__ import annotations

import json
import re
from pathlib import Path

from compliance_helpers import is_1516_1_2010_row
from hla.verification.repo_internal.conformance_evidence import focused_evidence_by_method

ROOT = Path(__file__).resolve().parents[1]


def _compliance_harness_refs(*, backend: str, clauses: tuple[str, ...]) -> set[str]:
    payload = json.loads(
        (ROOT / "analysis" / "compliance" / f"{backend}_requirement_disposition.json").read_text(encoding="utf-8")
    )
    return {
        ref
        for row in payload["rows"]
        if is_1516_1_2010_row(row) and row.get("clause_root") in clauses
        for ref in row["evidence_refs"]
        if ref.startswith("packages/hla-verification/src/hla.verification/")
    }


def _pitch_profile_compliance_harness_refs(*, clauses: tuple[str, ...]) -> set[str]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return {
        ref
        for row in payload["rows"]
        if is_1516_1_2010_row(row) and row.get("clause_root") in clauses
        for key in ("pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs")
        for ref in row.get(key, [])
        if ref.startswith("packages/hla-verification/src/hla.verification/")
    }


def _split_harness_ref(ref: str) -> tuple[str, str]:
    prefix = "packages/hla-verification/src/"
    module_path, symbol = ref.removeprefix(prefix).split("::", 1)
    module_name = ".".join(module_path.removesuffix(".py").split("/"))
    return module_name, symbol


_HARNESS_REF_RE = re.compile(
    r"packages/hla-verification/src/hla.verification/[A-Za-z0-9_./-]+\.py::[A-Za-z0-9_]+"
)


def test_verification_harness_exports_object_management_shared_scenarios() -> None:
    import hla.verification
    from hla.verification import (
        OrphanObjectScenarioConfig,
        RequestAttributeValueUpdateScenarioConfig,
        run_orphan_object_lifecycle_scenario,
        run_request_attribute_value_update_routing_scenario,
        run_request_attribute_value_update_scenario,
    )

    assert hla.verification.OrphanObjectScenarioConfig is OrphanObjectScenarioConfig
    assert (
        hla.verification.RequestAttributeValueUpdateScenarioConfig
        is RequestAttributeValueUpdateScenarioConfig
    )
    assert hla.verification.run_orphan_object_lifecycle_scenario is run_orphan_object_lifecycle_scenario
    assert (
        hla.verification.run_request_attribute_value_update_routing_scenario
        is run_request_attribute_value_update_routing_scenario
    )
    assert hla.verification.run_request_attribute_value_update_scenario is run_request_attribute_value_update_scenario


def test_verification_harness_object_management_exports_resolve_to_package_modules() -> None:
    from hla.verification import (
        run_orphan_object_lifecycle_scenario,
        run_request_attribute_value_update_routing_scenario,
    )

    assert run_orphan_object_lifecycle_scenario.__module__ == "hla.verification.scenario_orphan_object"
    assert (
        run_request_attribute_value_update_routing_scenario.__module__
        == "hla.verification.scenario_request_attribute_value_update"
    )


def test_verification_harness_exports_clause4_shared_scenarios() -> None:
    import hla.verification
    from hla.verification import (
        ExternalLostFederateVictimSession,
        FederationLifecycleScenarioConfig,
        LostFederateScenarioConfig,
        SaveRestoreScenarioConfig,
        SynchronizationScenarioConfig,
        run_connection_lost_callback_scenario,
        run_discovery_class_scenario,
        run_discovery_metadata_callback_scenario,
        run_external_lost_federate_observer_scenario,
        run_failed_federate_synchronization_scenario,
        run_federation_lifecycle_scenario,
        run_federation_listing_scenario,
        run_lost_federate_mom_scenario,
        run_restore_callback_policy_scenario,
        run_restore_federate_local_state_scenario,
        run_restore_object_state_scenario,
        run_restore_transient_state_scenario,
        run_save_restore_scenario,
        run_scheduled_save_restore_time_state_scenario,
        run_synchronization_registration_failure_scenario,
        run_synchronization_scenario,
    )

    assert hla.verification.ExternalLostFederateVictimSession is ExternalLostFederateVictimSession
    assert hla.verification.FederationLifecycleScenarioConfig is FederationLifecycleScenarioConfig
    assert hla.verification.LostFederateScenarioConfig is LostFederateScenarioConfig
    assert hla.verification.SaveRestoreScenarioConfig is SaveRestoreScenarioConfig
    assert hla.verification.SynchronizationScenarioConfig is SynchronizationScenarioConfig
    assert hla.verification.run_connection_lost_callback_scenario is run_connection_lost_callback_scenario
    assert hla.verification.run_discovery_class_scenario is run_discovery_class_scenario
    assert hla.verification.run_discovery_metadata_callback_scenario is run_discovery_metadata_callback_scenario
    assert (
        hla.verification.run_external_lost_federate_observer_scenario
        is run_external_lost_federate_observer_scenario
    )
    assert (
        hla.verification.run_failed_federate_synchronization_scenario
        is run_failed_federate_synchronization_scenario
    )
    assert hla.verification.run_federation_lifecycle_scenario is run_federation_lifecycle_scenario
    assert hla.verification.run_federation_listing_scenario is run_federation_listing_scenario
    assert hla.verification.run_lost_federate_mom_scenario is run_lost_federate_mom_scenario
    assert hla.verification.run_restore_callback_policy_scenario is run_restore_callback_policy_scenario
    assert hla.verification.run_restore_federate_local_state_scenario is run_restore_federate_local_state_scenario
    assert hla.verification.run_restore_object_state_scenario is run_restore_object_state_scenario
    assert (
        hla.verification.run_scheduled_save_restore_time_state_scenario
        is run_scheduled_save_restore_time_state_scenario
    )
    assert hla.verification.run_restore_transient_state_scenario is run_restore_transient_state_scenario
    assert hla.verification.run_save_restore_scenario is run_save_restore_scenario
    assert (
        hla.verification.run_synchronization_registration_failure_scenario
        is run_synchronization_registration_failure_scenario
    )
    assert hla.verification.run_synchronization_scenario is run_synchronization_scenario


def test_verification_harness_clause4_exports_resolve_to_package_modules() -> None:
    from hla.verification import (
        ExternalLostFederateVictimSession,
        run_connection_lost_callback_scenario,
        run_discovery_class_scenario,
        run_discovery_metadata_callback_scenario,
        run_external_lost_federate_observer_scenario,
        run_failed_federate_synchronization_scenario,
        run_federation_listing_scenario,
        run_lost_federate_mom_scenario,
        run_restore_callback_policy_scenario,
        run_restore_federate_local_state_scenario,
        run_restore_object_state_scenario,
        run_restore_transient_state_scenario,
        run_save_restore_scenario,
        run_scheduled_save_restore_time_state_scenario,
        run_synchronization_registration_failure_scenario,
    )

    assert ExternalLostFederateVictimSession.__module__ == "hla.verification.scenario_lost_federate"
    assert run_connection_lost_callback_scenario.__module__ == "hla.verification.scenario_connection_lost"
    assert run_discovery_class_scenario.__module__ == "hla.verification.scenario_discovery_class"
    assert (
        run_discovery_metadata_callback_scenario.__module__
        == "hla.verification.scenario_discovery_metadata"
    )
    assert (
        run_external_lost_federate_observer_scenario.__module__
        == "hla.verification.scenario_lost_federate"
    )
    assert run_failed_federate_synchronization_scenario.__module__ == "hla.verification.scenario_sync"
    assert run_federation_listing_scenario.__module__ == "hla.verification.scenario_federation_lifecycle"
    assert run_lost_federate_mom_scenario.__module__ == "hla.verification.scenario_lost_federate"
    assert run_restore_callback_policy_scenario.__module__ == "hla.verification.scenario_save_restore"
    assert run_restore_federate_local_state_scenario.__module__ == "hla.verification.scenario_save_restore"
    assert run_restore_object_state_scenario.__module__ == "hla.verification.scenario_save_restore"
    assert run_scheduled_save_restore_time_state_scenario.__module__ == "hla.verification.scenario_save_restore"
    assert run_restore_transient_state_scenario.__module__ == "hla.verification.scenario_save_restore"
    assert run_save_restore_scenario.__module__ == "hla.verification.scenario_save_restore"
    assert (
        run_synchronization_registration_failure_scenario.__module__
        == "hla.verification.scenario_sync"
    )


def test_verification_harness_exports_clause6_plus_shared_suite_scenarios() -> None:
    import hla.verification
    from hla.verification import (
        NegotiatedOwnershipScenarioConfig,
        OwnershipScenarioConfig,
        ResignScenarioConfig,
        SuiteRecordingFederateAmbassador,
        decode_handle_value_map,
        jsonable,
        probe_negotiated_attribute_ownership_offer,
        run_attribute_ownership_scenario,
        run_disconnect_mom_cleanup_scenario,
        run_suite_ddm_scenario,
    )

    assert hla.verification.NegotiatedOwnershipScenarioConfig is NegotiatedOwnershipScenarioConfig
    assert hla.verification.OwnershipScenarioConfig is OwnershipScenarioConfig
    assert hla.verification.ResignScenarioConfig is ResignScenarioConfig
    assert hla.verification.SuiteRecordingFederateAmbassador is SuiteRecordingFederateAmbassador
    assert hla.verification.decode_handle_value_map is decode_handle_value_map
    assert hla.verification.jsonable is jsonable
    assert (
        hla.verification.probe_negotiated_attribute_ownership_offer
        is probe_negotiated_attribute_ownership_offer
    )
    assert hla.verification.run_attribute_ownership_scenario is run_attribute_ownership_scenario
    assert hla.verification.run_disconnect_mom_cleanup_scenario is run_disconnect_mom_cleanup_scenario
    assert hla.verification.run_suite_ddm_scenario is run_suite_ddm_scenario


def test_verification_harness_clause6_plus_suite_exports_resolve_to_package_modules() -> None:
    from hla.verification import (
        SuiteRecordingFederateAmbassador,
        decode_handle_value_map,
        jsonable,
        probe_negotiated_attribute_ownership_offer,
        run_attribute_ownership_scenario,
        run_disconnect_mom_cleanup_scenario,
        run_suite_ddm_scenario,
    )

    assert decode_handle_value_map.__module__ == "hla.verification.two_federate_suite_scenarios"
    assert jsonable.__module__ == "hla.verification.two_federate_suite_summary"
    assert (
        probe_negotiated_attribute_ownership_offer.__module__
        == "hla.verification.scenario_ownership"
    )
    assert run_attribute_ownership_scenario.__module__ == "hla.verification.scenario_ownership"
    assert run_disconnect_mom_cleanup_scenario.__module__ == "hla.verification.scenario_resign"
    assert run_suite_ddm_scenario.__module__ == "hla.verification.two_federate_suite_scenarios"
    assert (
        SuiteRecordingFederateAmbassador.__module__
        == "hla.verification.two_federate_suite_pairs"
    )


def test_verification_harness_exports_section8_shared_scenarios() -> None:
    import hla.verification
    from hla.verification import (
        Section8MatrixConfig,
        run_section8_available_and_flush_case,
        run_section8_early_timestamp_send_case,
        run_section8_ordering_and_query_case,
        section8_matrix_config,
    )

    assert hla.verification.Section8MatrixConfig is Section8MatrixConfig
    assert hla.verification.run_section8_available_and_flush_case is run_section8_available_and_flush_case
    assert hla.verification.run_section8_early_timestamp_send_case is run_section8_early_timestamp_send_case
    assert hla.verification.run_section8_ordering_and_query_case is run_section8_ordering_and_query_case
    assert hla.verification.section8_matrix_config is section8_matrix_config


def test_verification_harness_section8_exports_resolve_to_package_modules() -> None:
    from hla.verification import (
        run_section8_available_and_flush_case,
        run_section8_early_timestamp_send_case,
        run_section8_ordering_and_query_case,
    )

    assert run_section8_available_and_flush_case.__module__ == "hla.verification.section8_matrix"
    assert run_section8_early_timestamp_send_case.__module__ == "hla.verification.section8_matrix"
    assert run_section8_ordering_and_query_case.__module__ == "hla.verification.section8_matrix"


def test_clause4_and_clause6_compliance_harness_refs_are_exported_from_root_package() -> None:
    import hla.verification

    refs = (
        _compliance_harness_refs(backend="python1516e", clauses=("4", "6"))
        | _compliance_harness_refs(backend="pitch", clauses=("4", "6"))
        | _pitch_profile_compliance_harness_refs(clauses=("4", "6"))
    )
    assert refs

    for ref in refs:
        _module_name, symbol = _split_harness_ref(ref)
        assert hasattr(hla.verification, symbol), ref


def test_clause4_and_clause6_compliance_harness_refs_resolve_to_expected_package_modules() -> None:
    import hla.verification

    refs = (
        _compliance_harness_refs(backend="python1516e", clauses=("4", "6"))
        | _compliance_harness_refs(backend="pitch", clauses=("4", "6"))
        | _pitch_profile_compliance_harness_refs(clauses=("4", "6"))
    )
    assert refs

    for ref in refs:
        module_name, symbol = _split_harness_ref(ref)
        exported = getattr(hla.verification, symbol)
        assert exported.__module__ == module_name, ref


def test_conformance_evidence_harness_refs_do_not_use_stale_module_paths() -> None:
    refs = {
        ref
        for evidence_refs in focused_evidence_by_method().values()
        for ref in evidence_refs
        if ref.startswith("packages/hla-verification/src/hla.verification/")
    }
    assert refs
    assert all("scenario_declaration_management.py::" not in ref for ref in refs)


def test_conformance_evidence_harness_refs_resolve_to_expected_package_modules() -> None:
    import hla.verification

    refs = {
        ref
        for evidence_refs in focused_evidence_by_method().values()
        for ref in evidence_refs
        if ref.startswith("packages/hla-verification/src/hla.verification/")
    }
    assert refs

    for ref in refs:
        module_name, symbol = _split_harness_ref(ref)
        exported = getattr(hla.verification, symbol)
        assert exported.__module__ == module_name, ref


def test_committed_compliance_artifacts_do_not_reference_stale_harness_module_paths() -> None:
    artifact_paths = (
        ROOT / "analysis" / "compliance" / "service_conformance.json",
        ROOT / "analysis" / "compliance" / "service_conformance.csv",
        ROOT / "analysis" / "compliance" / "requirements_ledger.json",
        ROOT / "analysis" / "compliance" / "negative_path_priority_ranking.json",
    )
    refs = {
        ref
        for path in artifact_paths
        for ref in _HARNESS_REF_RE.findall(path.read_text(encoding="utf-8"))
    }
    assert refs

    for ref in refs:
        module_name, symbol = _split_harness_ref(ref)
        module = __import__(module_name, fromlist=[symbol])
        assert hasattr(module, symbol), ref
