from __future__ import annotations

import json
import re
from hla2010_repo_internal.conformance_evidence import focused_evidence_by_method
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _compliance_harness_refs(*, backend: str, clauses: tuple[str, ...]) -> set[str]:
    payload = json.loads(
        (ROOT / "analysis" / "compliance" / f"{backend}_requirement_disposition.json").read_text(encoding="utf-8")
    )
    return {
        ref
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010" and row.get("clause_root") in clauses
        for ref in row["evidence_refs"]
        if ref.startswith("packages/hla2010-verification-harness/src/hla2010_verification_harness/")
    }


def _pitch_profile_compliance_harness_refs(*, clauses: tuple[str, ...]) -> set[str]:
    payload = json.loads((ROOT / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    return {
        ref
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010" and row.get("clause_root") in clauses
        for key in ("pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs")
        for ref in row.get(key, [])
        if ref.startswith("packages/hla2010-verification-harness/src/hla2010_verification_harness/")
    }


def _split_harness_ref(ref: str) -> tuple[str, str]:
    prefix = "packages/hla2010-verification-harness/src/"
    module_path, symbol = ref.removeprefix(prefix).split("::", 1)
    module_name = module_path.removesuffix(".py").replace("/", ".")
    return module_name, symbol


_HARNESS_REF_RE = re.compile(
    r"packages/hla2010-verification-harness/src/hla2010_verification_harness/[A-Za-z0-9_./-]+\.py::[A-Za-z0-9_]+"
)


def test_verification_harness_exports_object_management_shared_scenarios() -> None:
    import hla2010_verification_harness
    from hla2010_verification_harness import (
        OrphanObjectScenarioConfig,
        RequestAttributeValueUpdateScenarioConfig,
        run_orphan_object_lifecycle_scenario,
        run_request_attribute_value_update_routing_scenario,
        run_request_attribute_value_update_scenario,
    )

    assert hla2010_verification_harness.OrphanObjectScenarioConfig is OrphanObjectScenarioConfig
    assert (
        hla2010_verification_harness.RequestAttributeValueUpdateScenarioConfig
        is RequestAttributeValueUpdateScenarioConfig
    )
    assert hla2010_verification_harness.run_orphan_object_lifecycle_scenario is run_orphan_object_lifecycle_scenario
    assert (
        hla2010_verification_harness.run_request_attribute_value_update_routing_scenario
        is run_request_attribute_value_update_routing_scenario
    )
    assert hla2010_verification_harness.run_request_attribute_value_update_scenario is run_request_attribute_value_update_scenario


def test_verification_harness_object_management_exports_resolve_to_package_modules() -> None:
    from hla2010_verification_harness import (
        run_orphan_object_lifecycle_scenario,
        run_request_attribute_value_update_routing_scenario,
    )

    assert run_orphan_object_lifecycle_scenario.__module__ == "hla2010_verification_harness.scenario_orphan_object"
    assert (
        run_request_attribute_value_update_routing_scenario.__module__
        == "hla2010_verification_harness.scenario_request_attribute_value_update"
    )


def test_verification_harness_exports_clause4_shared_scenarios() -> None:
    import hla2010_verification_harness
    from hla2010_verification_harness import (
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
        run_scheduled_save_restore_time_state_scenario,
        run_restore_transient_state_scenario,
        run_save_restore_scenario,
        run_synchronization_registration_failure_scenario,
        run_synchronization_scenario,
    )

    assert hla2010_verification_harness.ExternalLostFederateVictimSession is ExternalLostFederateVictimSession
    assert hla2010_verification_harness.FederationLifecycleScenarioConfig is FederationLifecycleScenarioConfig
    assert hla2010_verification_harness.LostFederateScenarioConfig is LostFederateScenarioConfig
    assert hla2010_verification_harness.SaveRestoreScenarioConfig is SaveRestoreScenarioConfig
    assert hla2010_verification_harness.SynchronizationScenarioConfig is SynchronizationScenarioConfig
    assert hla2010_verification_harness.run_connection_lost_callback_scenario is run_connection_lost_callback_scenario
    assert hla2010_verification_harness.run_discovery_class_scenario is run_discovery_class_scenario
    assert hla2010_verification_harness.run_discovery_metadata_callback_scenario is run_discovery_metadata_callback_scenario
    assert (
        hla2010_verification_harness.run_external_lost_federate_observer_scenario
        is run_external_lost_federate_observer_scenario
    )
    assert (
        hla2010_verification_harness.run_failed_federate_synchronization_scenario
        is run_failed_federate_synchronization_scenario
    )
    assert hla2010_verification_harness.run_federation_lifecycle_scenario is run_federation_lifecycle_scenario
    assert hla2010_verification_harness.run_federation_listing_scenario is run_federation_listing_scenario
    assert hla2010_verification_harness.run_lost_federate_mom_scenario is run_lost_federate_mom_scenario
    assert hla2010_verification_harness.run_restore_callback_policy_scenario is run_restore_callback_policy_scenario
    assert hla2010_verification_harness.run_restore_federate_local_state_scenario is run_restore_federate_local_state_scenario
    assert hla2010_verification_harness.run_restore_object_state_scenario is run_restore_object_state_scenario
    assert (
        hla2010_verification_harness.run_scheduled_save_restore_time_state_scenario
        is run_scheduled_save_restore_time_state_scenario
    )
    assert hla2010_verification_harness.run_restore_transient_state_scenario is run_restore_transient_state_scenario
    assert hla2010_verification_harness.run_save_restore_scenario is run_save_restore_scenario
    assert (
        hla2010_verification_harness.run_synchronization_registration_failure_scenario
        is run_synchronization_registration_failure_scenario
    )
    assert hla2010_verification_harness.run_synchronization_scenario is run_synchronization_scenario


def test_verification_harness_clause4_exports_resolve_to_package_modules() -> None:
    from hla2010_verification_harness import (
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
        run_scheduled_save_restore_time_state_scenario,
        run_restore_transient_state_scenario,
        run_save_restore_scenario,
        run_synchronization_registration_failure_scenario,
    )

    assert ExternalLostFederateVictimSession.__module__ == "hla2010_verification_harness.scenario_lost_federate"
    assert run_connection_lost_callback_scenario.__module__ == "hla2010_verification_harness.scenario_connection_lost"
    assert run_discovery_class_scenario.__module__ == "hla2010_verification_harness.scenario_discovery_class"
    assert (
        run_discovery_metadata_callback_scenario.__module__
        == "hla2010_verification_harness.scenario_discovery_metadata"
    )
    assert (
        run_external_lost_federate_observer_scenario.__module__
        == "hla2010_verification_harness.scenario_lost_federate"
    )
    assert run_failed_federate_synchronization_scenario.__module__ == "hla2010_verification_harness.scenario_sync"
    assert run_federation_listing_scenario.__module__ == "hla2010_verification_harness.scenario_federation_lifecycle"
    assert run_lost_federate_mom_scenario.__module__ == "hla2010_verification_harness.scenario_lost_federate"
    assert run_restore_callback_policy_scenario.__module__ == "hla2010_verification_harness.scenario_save_restore"
    assert run_restore_federate_local_state_scenario.__module__ == "hla2010_verification_harness.scenario_save_restore"
    assert run_restore_object_state_scenario.__module__ == "hla2010_verification_harness.scenario_save_restore"
    assert run_scheduled_save_restore_time_state_scenario.__module__ == "hla2010_verification_harness.scenario_save_restore"
    assert run_restore_transient_state_scenario.__module__ == "hla2010_verification_harness.scenario_save_restore"
    assert run_save_restore_scenario.__module__ == "hla2010_verification_harness.scenario_save_restore"
    assert (
        run_synchronization_registration_failure_scenario.__module__
        == "hla2010_verification_harness.scenario_sync"
    )


def test_verification_harness_exports_clause6_plus_shared_suite_scenarios() -> None:
    import hla2010_verification_harness
    from hla2010_verification_harness import (
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

    assert hla2010_verification_harness.NegotiatedOwnershipScenarioConfig is NegotiatedOwnershipScenarioConfig
    assert hla2010_verification_harness.OwnershipScenarioConfig is OwnershipScenarioConfig
    assert hla2010_verification_harness.ResignScenarioConfig is ResignScenarioConfig
    assert hla2010_verification_harness.SuiteRecordingFederateAmbassador is SuiteRecordingFederateAmbassador
    assert hla2010_verification_harness.decode_handle_value_map is decode_handle_value_map
    assert hla2010_verification_harness.jsonable is jsonable
    assert (
        hla2010_verification_harness.probe_negotiated_attribute_ownership_offer
        is probe_negotiated_attribute_ownership_offer
    )
    assert hla2010_verification_harness.run_attribute_ownership_scenario is run_attribute_ownership_scenario
    assert hla2010_verification_harness.run_disconnect_mom_cleanup_scenario is run_disconnect_mom_cleanup_scenario
    assert hla2010_verification_harness.run_suite_ddm_scenario is run_suite_ddm_scenario


def test_verification_harness_clause6_plus_suite_exports_resolve_to_package_modules() -> None:
    from hla2010_verification_harness import (
        SuiteRecordingFederateAmbassador,
        decode_handle_value_map,
        jsonable,
        probe_negotiated_attribute_ownership_offer,
        run_attribute_ownership_scenario,
        run_disconnect_mom_cleanup_scenario,
        run_suite_ddm_scenario,
    )

    assert decode_handle_value_map.__module__ == "hla2010_verification_harness.two_federate_suite_scenarios"
    assert jsonable.__module__ == "hla2010_verification_harness.two_federate_suite_summary"
    assert (
        probe_negotiated_attribute_ownership_offer.__module__
        == "hla2010_verification_harness.scenario_ownership"
    )
    assert run_attribute_ownership_scenario.__module__ == "hla2010_verification_harness.scenario_ownership"
    assert run_disconnect_mom_cleanup_scenario.__module__ == "hla2010_verification_harness.scenario_resign"
    assert run_suite_ddm_scenario.__module__ == "hla2010_verification_harness.two_federate_suite_scenarios"
    assert (
        SuiteRecordingFederateAmbassador.__module__
        == "hla2010_verification_harness.two_federate_suite_pairs"
    )


def test_verification_harness_exports_section8_shared_scenarios() -> None:
    import hla2010_verification_harness
    from hla2010_verification_harness import (
        Section8MatrixConfig,
        run_section8_available_and_flush_case,
        run_section8_early_timestamp_send_case,
        run_section8_ordering_and_query_case,
        section8_matrix_config,
    )

    assert hla2010_verification_harness.Section8MatrixConfig is Section8MatrixConfig
    assert hla2010_verification_harness.run_section8_available_and_flush_case is run_section8_available_and_flush_case
    assert hla2010_verification_harness.run_section8_early_timestamp_send_case is run_section8_early_timestamp_send_case
    assert hla2010_verification_harness.run_section8_ordering_and_query_case is run_section8_ordering_and_query_case
    assert hla2010_verification_harness.section8_matrix_config is section8_matrix_config


def test_verification_harness_section8_exports_resolve_to_package_modules() -> None:
    from hla2010_verification_harness import (
        run_section8_available_and_flush_case,
        run_section8_early_timestamp_send_case,
        run_section8_ordering_and_query_case,
    )

    assert run_section8_available_and_flush_case.__module__ == "hla2010_verification_harness.section8_matrix"
    assert run_section8_early_timestamp_send_case.__module__ == "hla2010_verification_harness.section8_matrix"
    assert run_section8_ordering_and_query_case.__module__ == "hla2010_verification_harness.section8_matrix"


def test_clause4_and_clause6_compliance_harness_refs_are_exported_from_root_package() -> None:
    import hla2010_verification_harness

    refs = (
        _compliance_harness_refs(backend="python", clauses=("4", "6"))
        | _compliance_harness_refs(backend="pitch", clauses=("4", "6"))
        | _pitch_profile_compliance_harness_refs(clauses=("4", "6"))
    )
    assert refs

    for ref in refs:
        _module_name, symbol = _split_harness_ref(ref)
        assert hasattr(hla2010_verification_harness, symbol), ref


def test_clause4_and_clause6_compliance_harness_refs_resolve_to_expected_package_modules() -> None:
    import hla2010_verification_harness

    refs = (
        _compliance_harness_refs(backend="python", clauses=("4", "6"))
        | _compliance_harness_refs(backend="pitch", clauses=("4", "6"))
        | _pitch_profile_compliance_harness_refs(clauses=("4", "6"))
    )
    assert refs

    for ref in refs:
        module_name, symbol = _split_harness_ref(ref)
        exported = getattr(hla2010_verification_harness, symbol)
        assert exported.__module__ == module_name, ref


def test_conformance_evidence_harness_refs_do_not_use_stale_module_paths() -> None:
    refs = {
        ref
        for evidence_refs in focused_evidence_by_method().values()
        for ref in evidence_refs
        if ref.startswith("packages/hla2010-verification-harness/src/hla2010_verification_harness/")
    }
    assert refs
    assert all("scenario_declaration_management.py::" not in ref for ref in refs)


def test_conformance_evidence_harness_refs_resolve_to_expected_package_modules() -> None:
    import hla2010_verification_harness

    refs = {
        ref
        for evidence_refs in focused_evidence_by_method().values()
        for ref in evidence_refs
        if ref.startswith("packages/hla2010-verification-harness/src/hla2010_verification_harness/")
    }
    assert refs

    for ref in refs:
        module_name, symbol = _split_harness_ref(ref)
        exported = getattr(hla2010_verification_harness, symbol)
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
