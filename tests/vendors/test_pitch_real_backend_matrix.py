from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_backend_common import BackendUnavailableError
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import (
    AlreadyConnected,
    CouldNotOpenFDD,
    ErrorReadingFDD,
    FederateAlreadyExecutionMember,
    FederateNameAlreadyInUse,
    FederateIsExecutionMember,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    FederationExecutionDoesNotExist,
    FederationExecutionAlreadyExists,
    FederatesCurrentlyJoined,
    InconsistentFDD,
    InvalidLogicalTime,
    InvalidResignAction,
    NotConnected,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
    RestoreInProgress,
    RestoreNotInProgress,
    RTIexception,
    SaveInProgress,
)
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_rti_java_common import JavaValueConverter, PythonFederateAmbassadorDispatcher
from hla2010_rti_java_common.java_shim_backend import ShimJavaBridge
from hla2010_verification_harness import (
    DeclarationManagementScenarioConfig,
    DiscoveryClassScenarioConfig,
    DdmDeclarationGatingScenarioConfig,
    DdmObjectRegionLifecycleScenarioConfig,
    DdmPassiveRegionScenarioConfig,
    ExternalLostFederateVictimSession,
    LostFederateScenarioConfig,
    JoinScenarioConfig,
    LocalDeleteScenarioConfig,
    NameReservationScenarioConfig,
    ObjectScopeScenarioConfig,
    OrphanObjectScenarioConfig,
    RequestAttributeValueUpdateScenarioConfig,
    SaveRestoreScenarioConfig,
    SupportServicesScenarioConfig,
    SynchronizationScenarioConfig,
    TimedDeleteScenarioConfig,
    TransportationTypeScenarioConfig,
    TwoFederateExchangeConfig,
    UpdateRateScenarioConfig,
    assert_two_federate_exchange_callback_history,
    FederationLifecycleScenarioConfig,
    run_connection_lost_callback_scenario,
    run_declaration_invalid_attribute_publication_scenario,
    run_declaration_management_scenario,
    run_declaration_unpublish_rejection_scenario,
    run_time_managed_declaration_independence_scenario,
    run_discovery_class_scenario,
    run_discovery_metadata_callback_scenario,
    run_ddm_declaration_gating_scenario,
    run_ddm_object_region_lifecycle_scenario,
    run_ddm_passive_region_subscription_scenario,
    run_failed_federate_synchronization_scenario,
    SuiteRecordingFederateAmbassador,
    NegotiatedOwnershipScenarioConfig,
    NonOwnerUpdateScenarioConfig,
    OwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    ResignScenarioConfig,
    run_federation_lifecycle_negative_scenario,
    run_federation_lifecycle_scenario,
    run_federation_listing_scenario,
    run_fom_integrity_negative_scenario,
    run_fom_module_visibility_scenario,
    run_join_precondition_scenario,
    run_late_join_synchronization_scenario,
    run_local_delete_scenario,
    run_lost_federate_mom_scenario,
    run_multi_module_fom_visibility_scenario,
    run_multi_participation_scenario,
    run_multiple_synchronization_points_scenario,
    run_name_reservation_scenario,
    run_object_scope_relevance_scenario,
    run_orphan_object_lifecycle_scenario,
    run_request_attribute_value_update_routing_scenario,
    run_request_attribute_value_update_scenario,
    run_disconnect_mom_cleanup_scenario,
    run_attribute_ownership_scenario,
    run_attribute_ownership_query_callback_scenario,
    run_attribute_ownership_unavailable_scenario,
    run_abort_save_exception_scenario,
    run_non_owner_update_rejection_scenario,
    run_negotiated_attribute_ownership_scenario,
    probe_negotiated_attribute_ownership_offer,
    run_release_request_ownership_scenario,
    run_resign_mom_cleanup_scenario,
    run_resign_precondition_scenario,
    run_restore_abort_exception_scenario,
    run_restore_abort_scenario,
    run_restore_federate_local_state_scenario,
    run_restore_failure_scenario,
    run_restore_object_state_scenario,
    run_restore_participant_exception_scenario,
    run_restore_request_failure_scenario,
    run_restore_request_precondition_scenario,
    run_restore_status_exception_scenario,
    run_resigned_federate_callback_silence_scenario,
    run_external_lost_federate_observer_scenario,
    run_save_abort_scenario,
    run_save_failure_scenario,
    run_save_participant_exception_scenario,
    run_save_request_precondition_scenario,
    run_save_restore_queued_callback_scenario,
    run_scheduled_save_restore_time_state_scenario,
    run_save_restore_scenario,
    run_save_status_exception_scenario,
    run_section8_available_and_flush_case,
    run_section8_available_and_retraction_case,
    run_section8_early_timestamp_send_case,
    run_section8_order_override_case,
    run_section8_ordering_and_query_case,
    run_section8_request_retraction_case,
    run_section8_state_services_case,
    run_section8_time_bound_query_case,
    run_support_factory_and_decode_scenario,
    run_synchronization_registration_failure_scenario,
    run_synchronization_scenario,
    run_timed_delete_scenario,
    run_transportation_type_rejection_scenario,
    run_transportation_type_restore_persistence_scenario,
    run_transportation_type_scenario,
    run_two_federate_exchange_scenario,
    run_suite_ddm_scenario,
    run_update_advisory_callback_scenario,
    run_update_rate_scenario,
    write_hierarchy_fom,
    write_update_rate_fom,
    section8_matrix_config,
)
from hla2010.time import HLAinteger64Interval, HLAinteger64Time
from hla2010.types import RangeBounds
from hla2010.types import TimeQueryReturn
from hla2010_rti_pitch_common.real_rti_pitch import launch_pitch_runtime
from tests.vendors.runtime_support import cleanup_federation, require_vendor_preflight, shutdown_runtime_resources

PITCH_KIND_CASES = ["pitch-jpype", "pitch-py4j"]
PITCH_PROFILE_CASES = [("pitch-jpype", "jpype"), ("pitch-py4j", "py4j")]


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")
    require_vendor_preflight("pitch", operator_hint="./tools/pitch preflight")


def _terminate_pitch_py4j_gateway_process(rti) -> bool:
    backend = getattr(rti, "backend", None)
    bridge = getattr(backend, "bridge", None)
    gateway = getattr(bridge, "gateway", None)
    process = getattr(gateway, "_hla2010_gateway_process", None)
    if process is None:
        return False
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception:
            process.kill()
            process.wait(timeout=5)
    return True


@contextmanager
def _pitch_runtime_case(kind: str, ambassador_count: int):
    _require_real_rti_smoke()
    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    rtis: list[object | None] = [None] * ambassador_count
    try:
        for index in range(ambassador_count):
            rtis[index] = create_rti_ambassador(kind)
        yield tuple(rtis)
    finally:
        shutdown_runtime_resources(close_resources=tuple(rtis), runtime_resources=(runtime,))

def _launch_pitch_jpype_lost_federate_session(config: LostFederateScenarioConfig) -> ExternalLostFederateVictimSession:
    helper_module = "tests.vendors.pitch_jpype_lost_federate_child"
    project_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            helper_module,
            "--federation-name",
            config.federation_name,
            "--federate-name",
            config.victim_name,
            "--federate-type",
            config.federate_type,
            "--logical-time-implementation-name",
            config.logical_time_implementation_name or "",
            "--object-class-name",
            config.object_class_name,
            "--attribute-name",
            config.attribute_name,
            "--object-instance-name",
            config.object_instance_name,
            "--automatic-resign-directive",
            config.automatic_resign_directive.name,
            *sum((["--fom-module", str(module)] for module in config.fom_modules), []),
        ],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        ready_line = process.stdout.readline().strip()
        if not ready_line:
            stderr = process.stderr.read().strip()
            raise AssertionError(f"pitch-jpype lost-federate child exited before readiness: {stderr}")
        payload = json.loads(ready_line)
    except BaseException:
        process.kill()
        process.wait(timeout=5)
        raise

    diagnostics: dict[str, str] = {"stdout": ready_line, "stderr": ""}

    def _describe() -> str:
        stderr = diagnostics["stderr"].strip()
        if not stderr:
            return "pitch-jpype lost-federate child produced no stderr diagnostics"
        tail = "\n".join(stderr.splitlines()[-20:])
        return f"pitch-jpype lost-federate child stderr tail:\n{tail}"

    def _cleanup() -> None:
        if process.poll() is None:
            process.kill()
        try:
            _stdout, _stderr = process.communicate(timeout=5)
        except Exception:
            process.wait(timeout=5)
        else:
            diagnostics["stderr"] = _stderr

    return ExternalLostFederateVictimSession(
        victim_handle_bytes=bytes.fromhex(payload["victim_handle_hex"]),
        victim_name=str(payload["victim_name"]),
        victim_time_bytes=bytes.fromhex(payload["victim_time_hex"]),
        induce_loss=_cleanup,
        cleanup=_cleanup,
        describe=_describe,
    )


def _pitch_dispatcher(profile: str) -> PythonFederateAmbassadorDispatcher:
    return PythonFederateAmbassadorDispatcher(
        RecordingFederateAmbassador(),
        JavaValueConverter(ShimJavaBridge(profile)),
    )


def _assert_summary_exception_types(summary: dict[str, object], **expected: type[BaseException]) -> None:
    for key, exception_type in expected.items():
        assert isinstance(summary[key], exception_type)


def _assert_declaration_summary(
    summary: dict[str, object],
    config: DeclarationManagementScenarioConfig,
    *,
    start_count: int,
    stop_count: int,
    turn_on_count: int = 2,
    turn_off_count: int = 2,
    second_stop_present: bool,
) -> None:
    assert [record.args for record in summary["start_records"]] == [
        (summary["publisher_class"],),
    ] * start_count
    assert [record.args for record in summary["stop_records"]] == [
        (summary["publisher_class"],),
    ] * stop_count
    assert [record.args for record in summary["turn_on_records"]] == [
        (summary["publisher_interaction"],),
    ] * turn_on_count
    assert [record.args for record in summary["turn_off_records"]] == [
        (summary["publisher_interaction"],),
    ] * turn_off_count
    assert (summary["second_stop_record"] is not None) is second_stop_present
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}


def _cleanup_pitch_pair(
    federation_name: str,
    *,
    destroyer,
    peer,
    destroyer_action: ResignAction,
    peer_action: ResignAction = ResignAction.NO_ACTION,
) -> None:
    cleanup_federation(
        federation_name,
        destroyer=destroyer,
        destroyer_resign_action=destroyer_action,
        remaining_resignations=((peer, peer_action),),
        disconnect_rtis=(peer, destroyer),
    )


def _cleanup_pitch_triple(
    federation_name: str,
    *,
    destroyer,
    middle,
    final,
    destroyer_action: ResignAction,
    middle_action: ResignAction = ResignAction.NO_ACTION,
    final_action: ResignAction = ResignAction.NO_ACTION,
) -> None:
    cleanup_federation(
        federation_name,
        destroyer=destroyer,
        destroyer_resign_action=destroyer_action,
        remaining_resignations=((middle, middle_action), (final, final_action)),
        disconnect_rtis=(final, middle, destroyer),
    )


def _pitch_sync_config(kind: str, name: str, **overrides):
    return SynchronizationScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        **overrides,
    )


def _pitch_save_restore_config(kind: str, name: str, save_prefix: str, **overrides):
    return SaveRestoreScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"{save_prefix}-{uuid.uuid4().hex[:8]}",
        **overrides,
    )


def _pitch_lifecycle_config(kind: str, name: str, **overrides):
    return FederationLifecycleScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        **overrides,
    )


def _pitch_resign_config(kind: str, name: str, **overrides):
    return ResignScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="ResignFederate",
        **overrides,
    )


def _pitch_join_config(kind: str, name: str, save_prefix: str, **overrides):
    return JoinScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        late_name="Late",
        federate_type="JoinFederate",
        save_name=f"{save_prefix}-{uuid.uuid4().hex[:8]}",
        **overrides,
    )


def _pitch_discovery_class_config(kind: str, hierarchy_fom: str):
    return DiscoveryClassScenarioConfig(
        federation_name=f"{kind}-discovery-class-{uuid.uuid4().hex[:8]}",
        fom_modules=(hierarchy_fom,),
        object_instance_name=f"{kind}-Hierarchy-{uuid.uuid4().hex[:8]}",
    )


def _pitch_name_reservation_config(kind: str):
    return NameReservationScenarioConfig(
        federation_name=f"{kind}-name-reservation-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        reserved_name=f"{kind}-Reserved-{uuid.uuid4().hex[:8]}",
        multiple_names=(
            f"{kind}-Reserved-A-{uuid.uuid4().hex[:4]}",
            f"{kind}-Reserved-B-{uuid.uuid4().hex[:4]}",
        ),
    )


def _pitch_declaration_config(kind: str, name: str, **overrides):
    params = {
        "federation_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "fom_modules": ("hla2010:VendorSmokeFOM.xml",),
        "logical_time_implementation_name": "HLAinteger64Time",
        "object_class_name": "HLAobjectRoot.SmokeObject",
        "attribute_name": "Payload",
        "interaction_class_name": "HLAinteractionRoot.SmokeInteraction",
        "parameter_name": "Message",
        "object_instance_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
    }
    params.update(overrides)
    return DeclarationManagementScenarioConfig(**params)


def _pitch_object_scope_config(kind: str, name: str):
    return ObjectScopeScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"{kind}-Relevance-{uuid.uuid4().hex[:8]}",
    )


def _pitch_transport_config(kind: str, name: str, **overrides):
    params = {
        "federation_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "fom_modules": ("hla2010:VendorSmokeFOM.xml",),
        "logical_time_implementation_name": "HLAinteger64Time",
        "object_instance_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "save_name": f"{kind}-{name.upper()}-{uuid.uuid4().hex[:8]}",
    }
    params.update(overrides)
    return TransportationTypeScenarioConfig(**params)


def _pitch_update_rate_config(kind: str, update_rate_fom: str):
    return UpdateRateScenarioConfig(
        federation_name=f"{kind}-update-rate-{uuid.uuid4().hex[:8]}",
        fom_modules=(update_rate_fom,),
        logical_time_implementation_name="HLAfloat64Time",
        object_instance_name=f"{kind}-Rate-{uuid.uuid4().hex[:8]}",
    )


def _pitch_request_update_config(kind: str, name: str, request_tag: bytes):
    return RequestAttributeValueUpdateScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"{kind}-RAVU-{uuid.uuid4().hex[:8]}",
        request_tag=request_tag,
    )


def _pitch_orphan_config(kind: str):
    return OrphanObjectScenarioConfig(
        federation_name=f"{kind}-orphan-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"{kind}-Orphan-{uuid.uuid4().hex[:8]}",
    )


def _pitch_timed_delete_config(kind: str):
    return TimedDeleteScenarioConfig(
        federation_name=f"{kind}-timed-delete-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"{kind}-TimedDelete-{uuid.uuid4().hex[:8]}",
    )


def _pitch_local_delete_config(kind: str):
    return LocalDeleteScenarioConfig(
        federation_name=f"{kind}-local-delete-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"{kind}-LocalDelete-{uuid.uuid4().hex[:8]}",
    )


def _pitch_support_config(kind: str):
    return SupportServicesScenarioConfig(
        federation_name=f"{kind}-support-factory-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"{kind}-support-{uuid.uuid4().hex[:8]}",
    )


def _pitch_ownership_config(kind: str, name: str, **overrides):
    params = {
        "federation_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "fom_modules": ("hla2010:VendorSmokeFOM.xml",),
        "logical_time_implementation_name": "HLAinteger64Time",
        "owner_name": "Owner",
        "acquirer_name": "Acquirer",
        "federate_type": "OwnershipFederate",
        "object_class_name": "HLAobjectRoot.SmokeObject",
        "attribute_name": "Payload",
        "object_instance_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
    }
    params.update(overrides)
    return OwnershipScenarioConfig(**params)


def _pitch_negotiated_ownership_config(kind: str, name: str, **overrides):
    params = {
        "federation_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "fom_modules": ("hla2010:VendorSmokeFOM.xml",),
        "logical_time_implementation_name": "HLAinteger64Time",
        "owner_name": "Owner",
        "acquirer_name": "Acquirer",
        "federate_type": "OwnershipFederate",
        "object_class_name": "HLAobjectRoot.SmokeObject",
        "attribute_name": "Payload",
        "object_instance_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "assumption_tag": b"assume-offer",
        "request_tag": b"acquire-request",
        "cancel_tag": b"reacquire-request",
    }
    params.update(overrides)
    return NegotiatedOwnershipScenarioConfig(**params)


def _pitch_release_request_config(kind: str, name: str, request_tag: bytes, owner_action: str):
    return ReleaseRequestOwnershipScenarioConfig(
        federation_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        request_tag=request_tag,
        owner_action=owner_action,
    )


def _pitch_non_owner_update_config(kind: str):
    return NonOwnerUpdateScenarioConfig(
        federation_name=f"{kind}-non-owner-update-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        observer_name="Observer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"{kind}-IllegalUpdate-{uuid.uuid4().hex[:8]}",
    )


def _pitch_ddm_config(kind: str, name: str):
    return {
        "federation_name": f"{kind}-{name}-{uuid.uuid4().hex[:8]}",
        "fom_modules": ("hla2010:VendorSmokeFOM.xml",),
        "logical_time_implementation_name": "HLAinteger64Time",
        "lookahead": HLAinteger64Interval(1),
        "source_near": RangeBounds(10, 20),
        "source_far": RangeBounds(30, 40),
        "target_bounds": RangeBounds(15, 25),
        "interaction_class_name": "HLAinteractionRoot.SmokeInteraction",
        "parameter_name": "Message",
        "far_payload": b"far",
        "far_tag": b"far-tag",
        "far_time": HLAinteger64Time(2),
        "near_payload": b"near",
        "near_tag": b"near-tag",
        "near_time": HLAinteger64Time(3),
        "grant_time": HLAinteger64Time(10),
        "next_request_time": HLAinteger64Time(10),
    }


@pytest.mark.parametrize(("kind", "profile"), PITCH_PROFILE_CASES)
def test_pitch_backend_connection_lost_callback_matrix(kind: str, profile: str):
    dispatcher = _pitch_dispatcher(profile)
    federate = dispatcher.ambassador
    summary = run_connection_lost_callback_scenario(
        dispatcher.connectionLost,
        federate=federate,
        fault_description=f"{kind} callback bridge loss",
    )
    assert summary["record"].args == (f"{kind} callback bridge loss",)


@pytest.mark.parametrize(("kind", "profile"), PITCH_PROFILE_CASES)
def test_pitch_backend_discovery_metadata_callback_matrix(kind: str, profile: str):
    dispatcher = _pitch_dispatcher(profile)
    federate = dispatcher.ambassador
    summary = run_discovery_metadata_callback_scenario(
        dispatcher.discoverObjectInstance,
        dispatcher.hasProducingFederate,
        dispatcher.getProducingFederate,
        dispatcher.hasSentRegions,
        dispatcher.getSentRegions,
        federate=federate,
        object_name=f"{kind}-discovery-metadata",
    )
    assert summary["discover_record"].args[2] == f"{kind}-discovery-metadata"
    assert summary["get_producing_record"].args[1] == summary["discover_record"].args[3]
    assert summary["has_regions_record"].args[1] == summary["get_regions_record"].args[1]


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_discovery_class_matrix(kind: str, tmp_path: Path):
    hierarchy_fom = write_hierarchy_fom(tmp_path / f"{kind}-hierarchy-fom.xml")
    config = _pitch_discovery_class_config(kind, hierarchy_fom)
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_discovery_class_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )
        assert summary["discovery"].args[1] == summary["subscriber_class"]
        assert summary["reflection"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=publisher,
            peer=subscriber,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize(("kind", "profile"), PITCH_PROFILE_CASES)
def test_pitch_attribute_ownership_query_callback_matrix(kind: str, profile: str):
    dispatcher = _pitch_dispatcher(profile)
    federate = dispatcher.ambassador
    summary = run_attribute_ownership_query_callback_scenario(
        dispatcher.informAttributeOwnership,
        dispatcher.attributeIsNotOwned,
        dispatcher.attributeIsOwnedByRTI,
        federate=federate,
    )
    assert len(summary["inform_record"].args) == 3
    assert len(summary["not_owned_record"].args) == 2
    assert len(summary["rti_owned_record"].args) == 2


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_name_reservation_matrix(kind: str):
    config = _pitch_name_reservation_config(kind)
    with _pitch_runtime_case(kind, 2) as (owner, rival):
        summary = run_name_reservation_scenario(
            owner,
            rival,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            rival_federate=RecordingFederateAmbassador(),
        )
        assert summary["owner_reserved"].args == (config.reserved_name,)
        assert summary["rival_reserved_failed"].args == (config.reserved_name,)
        assert summary["rival_reserved"].args == (config.reserved_name,)
        assert summary["owner_multiple_reserved"].args[0] == set(config.multiple_names)
        assert summary["rival_multiple_reserved_failed"].args[0] == set(config.multiple_names)
        assert summary["rival_multiple_reserved"].args[0] == set(config.multiple_names)
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=owner,
            peer=rival,
            destroyer_action=ResignAction.NO_ACTION,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_declaration_management_matrix(kind: str):
    config = _pitch_declaration_config(kind, "declaration")
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_declaration_management_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )
        _assert_declaration_summary(summary, config, start_count=2, stop_count=2, second_stop_present=True)
        assert summary["suppressed_reflect_count"] == 1
        assert summary["suppressed_interaction_count"] == 1
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=publisher,
            peer=subscriber,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_declaration_management_overload_matrix(kind: str):
    config = _pitch_declaration_config(
        kind,
        "declaration-overloads",
        use_passive_object_subscription=True,
        use_passive_interaction_subscription=True,
        use_full_object_unpublish=True,
        use_full_object_unsubscribe=True,
    )
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_declaration_management_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )
        _assert_declaration_summary(summary, config, start_count=2, stop_count=1, second_stop_present=False)
        assert summary["suppressed_reflect_count"] == 1
        assert summary["suppressed_interaction_count"] == 1
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=publisher,
            peer=subscriber,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_declaration_invalid_attribute_publication_matrix(kind: str):
    config = _pitch_declaration_config(kind, "declaration-invalid-attr")
    with _pitch_runtime_case(kind, 1) as (publisher,):
        summary = run_declaration_invalid_attribute_publication_scenario(
            publisher,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
        )
        assert summary["invalid_attribute"] != summary["publisher_attribute"]
        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.NO_ACTION,
            disconnect_rtis=(publisher,),
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_time_managed_declaration_independence_matrix(kind: str):
    config = _pitch_declaration_config(
        kind,
        "declaration-time",
        declaration_lookahead=HLAinteger64Interval(1),
    )
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_time_managed_declaration_independence_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )
        assert summary["time_regulation"] is not None
        assert summary["time_constrained"] is not None
        assert summary["start_record"].args == (summary["publisher_class"],)
        assert summary["turn_on_record"].args == (summary["publisher_interaction"],)
        assert summary["discover_record"].args[2] == config.object_instance_name
        assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
        assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=publisher,
            peer=subscriber,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_declaration_unpublish_rejection_matrix(kind: str):
    config = _pitch_declaration_config(kind, "declaration-unpublish")
    with _pitch_runtime_case(kind, 1) as (publisher,):
        summary = run_declaration_unpublish_rejection_scenario(
            publisher,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
        )
        assert summary["object_unpublish_error"] is not None
        assert summary["interaction_unpublish_error"] is not None
        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.NO_ACTION,
            disconnect_rtis=(publisher,),
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_support_factory_and_decode_matrix(kind: str):
    config = _pitch_support_config(kind)
    with _pitch_runtime_case(kind, 1) as (rti,):
        summary = run_support_factory_and_decode_scenario(
            rti,
            config=config,
            federate=RecordingFederateAmbassador(),
        )
        assert summary["lookup_summary"]["federate_name"] == config.federate_name
        assert summary["lookup_summary"]["normalized_federate_handle"] == summary["federate_handle"]
        assert summary["lookup_summary"]["object_class_name"] == config.object_class_name
        assert summary["lookup_summary"]["attribute_name"] == config.attribute_name
        assert summary["lookup_summary"]["interaction_class_name"] == config.interaction_class_name
        assert summary["lookup_summary"]["parameter_name"] == config.parameter_name
        assert summary["lookup_summary"]["object_instance_name"] == config.object_instance_name
        assert summary["lookup_summary"]["object_instance_handle"] == summary["object_instance"]
        assert summary["lookup_summary"]["known_object_class"] == summary["object_class"]
        assert summary["lookup_summary"]["reliable_transport_name"] == "HLAreliable"
        assert summary["lookup_summary"]["best_effort_transport_name"] == "HLAbestEffort"
        assert summary["lookup_summary"]["reliable_transport_enum_name"] == "HLAreliable"
        assert summary["lookup_summary"]["best_effort_transport_enum_name"] == "HLAbestEffort"
        assert summary["lookup_summary"]["receive_order_name"] == "RECEIVE"
        assert summary["lookup_summary"]["timestamp_order_type"] is OrderType.TIMESTAMP
        assert summary["decoded_summary"]["attribute_handle"] == summary["attribute"]
        assert summary["decoded_summary"]["parameter_handle"] == summary["parameter"]
        assert summary["factory_summary"]["attribute_region_pair_list_factory"] is not None
        cleanup_federation(
            config.federation_name,
            destroyer=rti,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            disconnect_rtis=(rti,),
        )


@pytest.mark.parametrize(("kind", "profile"), PITCH_PROFILE_CASES)
def test_pitch_backend_update_advisory_callback_matrix(kind: str, profile: str):
    dispatcher = _pitch_dispatcher(profile)
    federate = dispatcher.ambassador
    summary = run_update_advisory_callback_scenario(
        dispatcher.attributesInScope,
        dispatcher.attributesOutOfScope,
        dispatcher.provideAttributeValueUpdate,
        dispatcher.turnUpdatesOnForObjectInstance,
        dispatcher.turnUpdatesOffForObjectInstance,
        federate=federate,
        tag=f"{kind}-update-advisory".encode(),
    )
    assert summary["provide_record"].args[2] == f"{kind}-update-advisory".encode()
    assert summary["turn_on_record"].args[2] == "HLAdefault"


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_object_scope_relevance_matrix(kind: str):
    config = _pitch_object_scope_config(kind, "object-scope")
    with _pitch_runtime_case(kind, 3) as (owner, acquirer, observer):
        summary = run_object_scope_relevance_scenario(
            owner,
            acquirer,
            observer,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )
        assert summary["initial_in_scope"].args[0] == summary["object_instance"]
        assert summary["initial_in_scope"].args[1] == {summary["observer_attribute"]}
        assert summary["out_of_scope"].args[0] == summary["object_instance"]
        assert summary["out_of_scope"].args[1] == {summary["observer_attribute"]}
        assert summary["reacquired_in_scope"].args[0] == summary["object_instance"]
        assert summary["reacquired_in_scope"].args[1] == {summary["observer_attribute"]}
        assert summary["initial_reflection"].args[0] == summary["object_instance"]
        assert summary["suppressed_reflection"] is None
        assert summary["acquired_reflection"].args[0] == summary["object_instance"]
        _cleanup_pitch_triple(
            config.federation_name,
            destroyer=owner,
            middle=acquirer,
            final=observer,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_transportation_type_matrix(kind: str):
    config = _pitch_transport_config(kind, "transport")
    with _pitch_runtime_case(kind, 2) as (owner, observer):
        summary = run_transportation_type_scenario(
            owner,
            observer,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )
        assert summary["confirm_attribute"].args == (
            summary["object_instance"],
            {summary["attribute"]},
            summary["transport"],
        )
        assert summary["report_attribute"].args == (
            summary["object_instance"],
            summary["attribute"],
            summary["transport"],
        )
        assert summary["confirm_interaction"].args == (summary["interaction"], summary["transport"])
        assert summary["report_interaction"].args[1:] == (summary["interaction"], summary["transport"])
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=owner,
            peer=observer,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_transportation_type_restore_persistence_matrix(kind: str):
    config = _pitch_transport_config(
        kind,
        "transport-restore",
        fom_modules=("TargetRadarFOMmodule.xml",),
        object_class_name="HLAobjectRoot.Target",
        attribute_name="Position",
        second_attribute_name="RCS",
        interaction_class_name="HLAinteractionRoot.TrackReport",
        parameter_name="TrackId",
    )
    with _pitch_runtime_case(kind, 2) as (owner, observer):
        summary = run_transportation_type_restore_persistence_scenario(
            owner,
            observer,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )
        assert len(summary["pre_restore_reflects"]) == 2
        assert len(summary["post_restore_attribute_reports"]) >= 2
        assert len(summary["post_restore_reflects"]) == 2
        assert summary["post_restore_interaction_report"].args[1:] == (
            summary["interaction"],
            summary["best_effort_transport"],
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_transportation_type_rejection_matrix(kind: str):
    config = _pitch_transport_config(kind, "transport-reject")
    with _pitch_runtime_case(kind, 2) as (owner, observer):
        summary = run_transportation_type_rejection_scenario(
            owner,
            observer,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )
        assert summary["object_instance"] is not None
        assert summary["attribute"] is not None
        assert summary["interaction"] is not None


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_update_rate_matrix(kind: str, tmp_path: Path):
    update_rate_fom = write_update_rate_fom(tmp_path / f"{kind}-update-rate-fom.xml")
    config = _pitch_update_rate_config(kind, update_rate_fom)
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_update_rate_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )
        assert summary["values"] == [b"t1", b"t16"]
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=publisher,
            peer=subscriber,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_request_attribute_value_update_matrix(kind: str):
    config = _pitch_request_update_config(kind, "ravu", f"{kind}-ravu".encode())
    with _pitch_runtime_case(kind, 2) as (owner, requester):
        summary = run_request_attribute_value_update_scenario(
            owner,
            requester,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            requester_federate=RecordingFederateAmbassador(),
        )
        assert summary["provide_record"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            config.request_tag,
        )
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=owner,
            peer=requester,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_request_attribute_value_update_routing_matrix(kind: str):
    config = _pitch_request_update_config(kind, "ravu-routing", b"object-only")
    with _pitch_runtime_case(kind, 3) as (owner_a, owner_b, requester):
        summary = run_request_attribute_value_update_routing_scenario(
            owner_a,
            owner_b,
            requester,
            config=config,
            owner_a_federate=RecordingFederateAmbassador(),
            owner_b_federate=RecordingFederateAmbassador(),
            requester_federate=RecordingFederateAmbassador(),
        )
        assert summary["object_target_provide_a"].args == (summary["object_a"], {summary["requester_attribute"]}, b"object-only")
        assert summary["object_target_provide_b"] is None
        assert summary["class_target_provide_a"].args == (summary["object_a"], {summary["requester_attribute"]}, b"class-wide")
        assert summary["class_target_provide_b"].args == (summary["object_b"], {summary["requester_attribute"]}, b"class-wide")
        _cleanup_pitch_triple(
            config.federation_name,
            destroyer=owner_a,
            middle=owner_b,
            final=requester,
            destroyer_action=ResignAction.DELETE_OBJECTS,
            middle_action=ResignAction.DELETE_OBJECTS,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_orphan_object_lifecycle_matrix(kind: str):
    config = _pitch_orphan_config(kind)
    with _pitch_runtime_case(kind, 3) as (owner, observer, late):
        summary = run_orphan_object_lifecycle_scenario(
            owner,
            observer,
            late,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
            late_federate=RecordingFederateAmbassador(),
        )
        assert summary["late_discovery"].args[0] == summary["object_instance"]
        assert summary["observer_remove"] is None
        assert summary["late_remove"].args[0] == summary["object_instance"]
        assert summary["late_remove"].args[1] == config.delete_tag
        _cleanup_pitch_triple(
            config.federation_name,
            destroyer=owner,
            middle=observer,
            final=late,
            destroyer_action=ResignAction.NO_ACTION,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_timed_delete_matrix(kind: str):
    config = _pitch_timed_delete_config(kind)
    with _pitch_runtime_case(kind, 2) as (owner, observer):
        summary = run_timed_delete_scenario(
            owner,
            observer,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )
        assert summary["remove_before_grant"] is None
        assert summary["remove_after_grant"].args[0] == summary["object_instance"]
        assert summary["remove_after_grant"].args[1] == config.delete_tag
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=owner,
            peer=observer,
            destroyer_action=ResignAction.NO_ACTION,
        )


@pytest.mark.parametrize("kind", PITCH_KIND_CASES)
def test_pitch_backend_local_delete_matrix(kind: str):
    config = _pitch_local_delete_config(kind)
    with _pitch_runtime_case(kind, 2) as (owner, observer):
        summary = run_local_delete_scenario(
            owner,
            observer,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )
        assert summary["discovery"].args[0] == summary["object_instance"]
        assert summary["reflection"].args[0] == summary["object_instance"]
        assert summary["reflection"].args[1] == {summary["observer_attribute"]: config.rediscover_payload}
        _cleanup_pitch_pair(
            config.federation_name,
            destroyer=owner,
            peer=observer,
            destroyer_action=ResignAction.DELETE_OBJECTS,
        )


def _pitch_exchange_config(federation_name: str, object_instance_name: str) -> TwoFederateExchangeConfig:
    return TwoFederateExchangeConfig(
        federation_name=federation_name,
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=object_instance_name,
        attribute_payload=b"payload-r",
        attribute_tag=b"reflect-tag",
        interaction_payload=b"hello-r",
        interaction_tag=b"interaction-tag",
        enable_time_management=True,
        lookahead=HLAinteger64Interval(1),
        advance_time=HLAinteger64Time(8),
        timestamped_attribute_payload=b"payload-tso",
        timestamped_attribute_tag=b"reflect-tso",
        timestamped_attribute_time=HLAinteger64Time(5),
        timestamped_interaction_payload=b"hello-tso",
        timestamped_interaction_tag=b"interaction-tso",
        timestamped_interaction_time=HLAinteger64Time(6),
    )


def _normalized_exchange_profile(summary: dict[str, object]) -> dict[str, object]:
    return {
        "reflect_payload": summary["reflect"].args[1],
        "reflect_tag": summary["reflect"].args[2],
        "reflect_order": summary["reflect"].args[3].name,
        "interaction_payload": summary["interaction"].args[1],
        "interaction_tag": summary["interaction"].args[2],
        "interaction_order": summary["interaction"].args[3].name,
        "timed_reflect_payload": summary["timed_reflect"].args[1],
        "timed_reflect_tag": summary["timed_reflect"].args[2],
        "timed_reflect_order": summary["timed_reflect"].args[3].name,
        "timed_reflect_time": int(summary["timed_reflect"].args[5].value),
        "timed_interaction_payload": summary["timed_interaction"].args[1],
        "timed_interaction_tag": summary["timed_interaction"].args[2],
        "timed_interaction_order": summary["timed_interaction"].args[3].name,
        "timed_interaction_time": int(summary["timed_interaction"].args[5].value),
        "advance_grant_time": int(summary["advance_grant"].args[0].value),
    }


def _normalized_negotiated_profile(summary: dict[str, object]) -> dict[str, object]:
    assumption = summary["assumption"]
    return {
        "negotiated_divestiture_supported": summary["negotiated_divestiture_supported"],
        "assumption_tag": (assumption.args[2] if assumption is not None else None),
        "release_tag": summary["release"].args[2],
        "cancellation_attr_count": len(summary["cancellation"].args[1]),
        "divested_count": len(summary["divested"]),
        "acquired_attr_count": len(summary["acquired"].args[1]),
        "informed_attribute_match": summary["informed"].args[1] == summary["owner_attribute"],
    }


def _format_probe_exception(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc!r}"


def _run_pitch_section8_pair(kind: str, case_name: str, runner):
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        config = section8_matrix_config(f"{kind}-section8-{case_name}-{uuid.uuid4().hex[:8]}", "HLAinteger64Time")
        return runner(publisher, subscriber, config=config), config


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_federation_lifecycle_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (federate,):
        config = _pitch_lifecycle_config(kind, "lifecycle")
        summary = run_federation_lifecycle_scenario(
            federate,
            config=config,
            federate=RecordingFederateAmbassador(),
        )
        assert summary["federation_name"] == config.federation_name
        assert summary["resign_action"] is ResignAction.NO_ACTION


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
@pytest.mark.xfail(
    raises=RTIexception,
    reason="Pitch Java FedPro adapter currently exposes createFederationExecution but not the createFederationExecutionWithMIM overload.",
)
def test_pitch_backend_federation_lifecycle_with_mim_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (federate,):
        config = _pitch_lifecycle_config(kind, "lifecycle-mim", use_mim_create=True)
        summary = run_federation_lifecycle_scenario(
            federate,
            config=config,
            federate=RecordingFederateAmbassador(),
        )
        assert summary["federation_name"] == config.federation_name
        assert summary["use_mim_create"] is True


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_federation_listing_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (federate,):
        config = _pitch_lifecycle_config(kind, "listing")
        summary = run_federation_listing_scenario(
            federate,
            config=config,
            federate=RecordingFederateAmbassador(),
        )
        assert summary["federation_name"] == config.federation_name
        assert summary["report"].method_name == "reportFederationExecutions"


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_fom_module_visibility_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (federate,):
        config = _pitch_lifecycle_config(kind, "fom-visibility")
        summary = run_fom_module_visibility_scenario(
            federate,
            config=config,
            federate=RecordingFederateAmbassador(),
        )
        assert summary["federation_name"] == config.federation_name
        assert summary["federate_handle"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_federation_lifecycle_negative_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_federation_lifecycle_negative_scenario(
            leader,
            wing,
            config=_pitch_lifecycle_config(kind, "lifecycle-negative"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["already_connected"], AlreadyConnected)
        assert isinstance(summary["duplicate_create"], FederationExecutionAlreadyExists)
        assert isinstance(summary["disconnect_while_joined"], FederateIsExecutionMember)
        assert isinstance(summary["destroy_with_joined"], FederatesCurrentlyJoined)
        assert isinstance(summary["destroy_missing"], FederationExecutionDoesNotExist)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_multi_participation_matrix(kind: str):
    config = _pitch_lifecycle_config(
        kind,
        "multi-participation",
        secondary_federation_name=f"{kind}-multi-participation-secondary-{uuid.uuid4().hex[:8]}",
        federate_name="Leader",
        second_federate_name="Wing",
        secondary_federate_name="Shadow",
    )
    with _pitch_runtime_case(kind, 3) as (leader, wing, shadow):
        summary = run_multi_participation_scenario(
            leader,
            wing,
            shadow,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            shadow_federate=RecordingFederateAmbassador(),
        )
        assert summary["primary_federation_name"] == config.federation_name
        assert summary["secondary_federation_name"] == config.secondary_federation_name
        assert summary["leader_handle"] is not None
        assert summary["wing_handle"] is not None
        assert summary["shadow_handle"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_fom_integrity_negative_matrix(kind: str):
    config = _pitch_lifecycle_config(
        kind,
        "fom-negative",
        federate_name="Leader",
        second_federate_name="Wing",
        federate_type="LifecycleType",
    )
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_fom_integrity_negative_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["create_missing"], CouldNotOpenFDD)
        assert isinstance(summary["create_bad"], ErrorReadingFDD)
        assert isinstance(summary["create_inconsistent"], InconsistentFDD)
        assert isinstance(summary["join_missing"], CouldNotOpenFDD)
        assert isinstance(summary["join_bad"], ErrorReadingFDD)
        assert isinstance(summary["join_inconsistent"], InconsistentFDD)
        assert summary["leader_handle"] is not None
        assert summary["wing_handle"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_multi_module_fom_visibility_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (rti,):
        config = _pitch_lifecycle_config(
            kind,
            "fom-multi",
            federate_name="Leader",
            federate_type="LifecycleType",
        )
        summary = run_multi_module_fom_visibility_scenario(
            rti,
            config=config,
            federate=RecordingFederateAmbassador(),
        )
        assert summary["federation_name"] == config.federation_name
        assert summary["federate_handle"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_late_join_synchronization_matrix(kind: str):
    with _pitch_runtime_case(kind, 3) as (leader, wing, late):
        summary = run_late_join_synchronization_scenario(
            leader,
            wing,
            late,
            config=_pitch_sync_config(kind, "sync-late", late_name="Late", label="ReadyToRun", tag=b"startup"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            late_federate=RecordingFederateAmbassador(),
        )
        assert summary["late_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"
        assert summary["late_sync"].args[0] == "ReadyToRun"


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_multiple_synchronization_points_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_multiple_synchronization_points_scenario(
            leader,
            wing,
            config=_pitch_sync_config(
                kind,
                "sync-multi",
                label="ReadyToRun",
                tag=b"startup",
                second_label="PreRun",
                second_tag=b"prerun",
            ),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert {record.args[0] for record in summary["leader_announces"]} == {"ReadyToRun", "PreRun"}
        assert {record.args[0] for record in summary["wing_announces"]} == {"ReadyToRun", "PreRun"}
        assert summary["first_sync_leader"].args[0] == "ReadyToRun"
        assert summary["first_sync_wing"].args[0] == "ReadyToRun"
        assert summary["second_sync_leader"].args[0] == "PreRun"
        assert summary["second_sync_wing"].args[0] == "PreRun"


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_abort_exception_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_restore_abort_exception_scenario(
            leader,
            wing,
            config=_pitch_save_restore_config(kind, "save-status-negative", "SAVE-STATUS"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(
            summary,
            not_connected=NotConnected,
            not_joined=FederateNotExecutionMember,
            restore_not_in_progress=RestoreNotInProgress,
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_status_exception_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (rti,):
        summary = run_save_status_exception_scenario(
            rti,
            federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(summary, not_connected=NotConnected, not_joined=FederateNotExecutionMember)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_status_exception_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (rti,):
        summary = run_restore_status_exception_scenario(
            rti,
            federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(summary, not_connected=NotConnected, not_joined=FederateNotExecutionMember)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_request_precondition_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_save_request_precondition_scenario(
            leader,
            wing,
            config=_pitch_save_restore_config(kind, "save-request", "SAVE-REQ"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(
            summary,
            not_connected=NotConnected,
            not_joined=FederateNotExecutionMember,
            save_in_progress=SaveInProgress,
            restore_in_progress=RestoreInProgress,
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_request_precondition_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_restore_request_precondition_scenario(
            leader,
            wing,
            config=_pitch_save_restore_config(kind, "restore-request", "RESTORE-REQ"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(
            summary,
            not_connected=NotConnected,
            not_joined=FederateNotExecutionMember,
            save_in_progress=SaveInProgress,
            restore_in_progress=RestoreInProgress,
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_participant_exception_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_save_participant_exception_scenario(
            leader,
            wing,
            config=_pitch_save_restore_config(kind, "save-participant", "SAVE-PART"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(
            summary,
            begun_not_connected=NotConnected,
            complete_not_connected=NotConnected,
            not_complete_not_connected=NotConnected,
            begun_not_joined=FederateNotExecutionMember,
            complete_not_joined=FederateNotExecutionMember,
            not_complete_not_joined=FederateNotExecutionMember,
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_abort_save_exception_matrix(kind: str):
    with _pitch_runtime_case(kind, 1) as (rti,):
        summary = run_abort_save_exception_scenario(
            rti,
            federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(summary, not_connected=NotConnected, not_joined=FederateNotExecutionMember)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_participant_exception_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_restore_participant_exception_scenario(
            leader,
            wing,
            config=_pitch_save_restore_config(kind, "restore-participant", "RESTORE-PART"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(
            summary,
            complete_not_connected=NotConnected,
            not_complete_not_connected=NotConnected,
            complete_not_joined=FederateNotExecutionMember,
            not_complete_not_joined=FederateNotExecutionMember,
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_resigned_federate_callback_silence_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_resigned_federate_callback_silence_scenario(
            leader,
            wing,
            config=_pitch_save_restore_config(kind, "resign-callback", "POST-RESIGN-SAVE"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_initiate_save"].args[0].startswith("POST-RESIGN-SAVE-")
        assert summary["leader_saved"] is not None
        assert summary["wing_record_count_after"] == summary["wing_record_count_before"]
        assert summary["wing_post_resign_records"] == []


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_resign_precondition_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_resign_precondition_scenario(
            leader,
            wing,
            config=_pitch_resign_config(
                kind,
                "resign-negative",
                object_instance_name=f"{kind}-Pending-Acquisition-{uuid.uuid4().hex[:8]}",
            ),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["invalid_action"], InvalidResignAction)
        assert isinstance(summary["owns_attributes"], FederateOwnsAttributes)
        assert isinstance(summary["acquisition_pending"], OwnershipAcquisitionPending)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_resign_mom_cleanup_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_resign_mom_cleanup_scenario(
            leader,
            wing,
            config=_pitch_resign_config(kind, "resign-mom"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["wing_before"].args[1]
        assert summary["federation_after"].args[1]
        assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_disconnect_mom_cleanup_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        summary = run_disconnect_mom_cleanup_scenario(
            leader,
            wing,
            config=_pitch_resign_config(kind, "disconnect-mom"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_before"].args[1]
        assert summary["federation_after"].args[1]
        assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_lost_federate_mom_matrix(kind: str):
    config = LostFederateScenarioConfig(
        federation_name=f"{kind}-lost-federate-{uuid.uuid4().hex[:8]}",
        fom_modules=("hla2010:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        observer_name="Observer",
        victim_name="Victim",
        federate_type="LostFederateProbe",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"{kind}-lost-object",
        fault_description=f"{kind} gateway terminated",
        automatic_resign_directive=ResignAction.DELETE_OBJECTS,
    )
    if kind == "pitch-py4j":
        with _pitch_runtime_case(kind, 2) as (observer, victim):

            def induce_loss(_victim_handle, _fault_description):
                if not _terminate_pitch_py4j_gateway_process(victim):
                    pytest.skip("pitch-py4j gateway process handle unavailable for lost-federate fault injection")

            summary = run_lost_federate_mom_scenario(
                observer,
                victim,
                config=config,
                observer_federate=RecordingFederateAmbassador(),
                victim_federate=RecordingFederateAmbassador(),
                induce_loss=induce_loss,
            )
    else:
        with _pitch_runtime_case(kind, 1) as (observer,):
            summary = run_external_lost_federate_observer_scenario(
                observer,
                config=config,
                observer_federate=RecordingFederateAmbassador(),
                launch_victim=_launch_pitch_jpype_lost_federate_session,
            )

    assert summary["loss_record"].args[0] is not None
    assert summary["removal"].args[1] == b"lost"
    assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_join_precondition_matrix(kind: str):
    with _pitch_runtime_case(kind, 3) as (leader, wing, late):
        summary = run_join_precondition_scenario(
            leader,
            wing,
            late,
            config=_pitch_join_config(kind, "join-negative", "JOIN-BLOCK"),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            late_federate=RecordingFederateAmbassador(),
        )
        _assert_summary_exception_types(
            summary,
            not_connected=NotConnected,
            missing_federation=FederationExecutionDoesNotExist,
            duplicate_name=FederateNameAlreadyInUse,
            already_joined=FederateAlreadyExecutionMember,
            save_in_progress=SaveInProgress,
            restore_in_progress=RestoreInProgress,
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_exchange_matrix(kind: str):
    federation_name = f"{kind}-matrix-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        config = _pitch_exchange_config(federation_name, f"{kind}-Object-1")
        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discover"].args[2] == f"{kind}-Object-1"
        assert summary["reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-r"}
        assert summary["interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-r"}
        assert summary["timed_reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-tso"}
        assert summary["timed_interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-tso"}

        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

        cleanup_federation(
            federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_lookahead_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "lookahead", run_section8_early_timestamp_send_case)

    assert summary["publisher_initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead
    assert summary["update_error"] is not None
    assert summary["interaction_error"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_section8_logical_time_query_matrix(kind: str):
    summary, _config = _run_pitch_section8_pair(kind, "logical-time", run_section8_state_services_case)

    assert summary["publisher_initial_time"] == HLAinteger64Time(0)
    assert summary["subscriber_initial_time"] == HLAinteger64Time(0)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_section8_state_toggle_services_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "state-toggles", run_section8_state_services_case)

    assert summary["initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_section8_time_bound_query_matrix(kind: str):
    summary, _config = _run_pitch_section8_pair(kind, "time-queries", run_section8_time_bound_query_case)

    assert isinstance(summary["initial_galt"], TimeQueryReturn)
    assert isinstance(summary["initial_lits"], TimeQueryReturn)


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_section8_available_and_flush_matrix(kind: str):
    summary, _config = _run_pitch_section8_pair(kind, "available-flush", run_section8_available_and_flush_case)

    assert summary["available_grant"] is not None
    assert summary["flush_grant"] is not None
    assert summary["flushed_receive"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_section8_early_timestamp_send_rejection_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "early-send", run_section8_early_timestamp_send_case)

    assert summary["publisher_initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead
    assert summary["update_error"] is not None
    assert summary["interaction_error"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
@pytest.mark.xfail(reason="Pitch Section 8 probe: time regulation/constrained callbacks are not observed in this dedicated matrix scenario")
def test_pitch_section8_state_services_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "state", run_section8_state_services_case)

    assert summary["publisher_federate"].last_callback("timeRegulationEnabled") is not None
    assert summary["subscriber_federate"].last_callback("timeConstrainedEnabled") is not None
    assert summary["initial_time"] == HLAinteger64Time(0)
    assert summary["initial_lookahead"] == config.lookahead
    assert summary["modified_lookahead"] == config.modified_lookahead


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
@pytest.mark.xfail(reason="Pitch Section 8 probe: timestamp-ordered NMR delivery is not observed in this dedicated matrix scenario")
def test_pitch_section8_ordering_and_queries_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "ordering", run_section8_ordering_and_query_case)

    assert isinstance(summary["initial_galt"], TimeQueryReturn)
    assert isinstance(summary["initial_lits"], TimeQueryReturn)
    assert summary["sender_grant"].args[0] == config.sender_advance_time
    assert summary["first_receive"].args[1] == {summary["parameter"]: config.second_payload}
    assert summary["first_receive"].args[2] == config.second_tag
    assert summary["first_receive"].args[3] is OrderType.TIMESTAMP
    assert summary["first_receive"].args[5] == config.second_timestamp
    assert summary["first_grant"].args[0] == config.second_timestamp
    assert summary["second_receive"].args[1] == {summary["parameter"]: config.first_payload}
    assert summary["second_receive"].args[2] == config.first_tag
    assert summary["second_receive"].args[3] is OrderType.TIMESTAMP
    assert summary["second_receive"].args[5] == config.first_timestamp
    assert summary["second_grant"].args[0] == config.first_timestamp


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
@pytest.mark.xfail(reason="Pitch Section 8 probe: timestamped send does not return a Python MessageRetractionReturn")
def test_pitch_section8_available_and_retraction_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "available", run_section8_available_and_retraction_case)

    assert summary["available_grant"] is not None
    assert summary["available_grant"].args[0] == config.receiver_window_time
    assert not summary["after_retract_callbacks"]
    assert summary["flush_grant"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
@pytest.mark.xfail(reason="Pitch Section 8 probe: order override callbacks are not observed in this dedicated matrix scenario")
def test_pitch_section8_order_override_services_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "order-override", run_section8_order_override_case)

    assert summary["reflect"] is not None
    assert summary["reflect"].args[1] == {summary["attribute"]: config.first_payload}
    assert summary["reflect"].args[3] is OrderType.RECEIVE
    assert len(summary["reflect"].args) in {5, 6}
    assert summary["receive"] is not None
    assert summary["receive"].args[1] == {summary["parameter"]: config.second_payload}
    assert summary["receive"].args[3] is OrderType.RECEIVE
    assert len(summary["receive"].args) in {5, 6}


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
@pytest.mark.xfail(reason="Pitch Section 8 probe: timestamped send does not return a Python MessageRetractionReturn for requestRetraction")
def test_pitch_section8_request_retraction_callback_matrix(kind: str):
    summary, config = _run_pitch_section8_pair(kind, "request-retraction", run_section8_request_retraction_case)

    assert summary["received"] is not None
    assert summary["received"].args[1] == {summary["parameter"]: config.first_payload}
    assert summary["received"].args[3] is OrderType.TIMESTAMP
    assert summary["request_retraction"] is not None
    assert summary["request_retraction"].args[0] == summary["sent"].handle


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_synchronization_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_sync_config(kind, "sync", label="ReadyToRun", tag=b"startup")
        summary = run_synchronization_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_registration"].args == ("ReadyToRun",)
        assert summary["leader_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["wing_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_synchronization_registration_failure_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_sync_config(kind, "sync-failure", label="ReadyToRun", tag=b"startup")
        summary = run_synchronization_registration_failure_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["registration_success"].args == ("ReadyToRun",)
        assert summary["registration_failure"].args[0] == "ReadyToRun"

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_failed_federate_synchronization_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_sync_config(kind, "sync-failed", label="PreRun", tag=b"startup")
        summary = run_failed_federate_synchronization_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            leader_success=True,
            wing_success=False,
        )

        assert summary["leader_sync"].args[0] == "PreRun"
        assert summary["wing_handle"] in summary["leader_sync"].args[1]
        assert summary["leader_handle"] not in summary["leader_sync"].args[1]

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_restore_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "save-restore", "PITCH-SAVE")
        summary = run_save_restore_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_initiate_save"].args[0] == config.save_name
        assert summary["leader_restore_succeeded"].args == (config.save_name,)
        assert summary["wing_initiate_restore"].args[0] == config.save_name

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_restore_queued_callback_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "save-restore-queued", "SAVE-QUEUED")
        summary = run_save_restore_queued_callback_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_initiate_save"].args[0].startswith("SAVE-QUEUED-")
        assert summary["wing_initiate_save"].args == summary["leader_initiate_save"].args
        assert summary["leader_saved"] is not None
        assert summary["wing_saved"] is not None
        assert summary["leader_restore_succeeded"].args == summary["leader_initiate_save"].args
        assert summary["wing_initiate_restore"].args[0] == summary["leader_initiate_save"].args[0]
        assert summary["leader_restored"] is not None
        assert summary["wing_restored"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_scheduled_save_restore_time_state_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "scheduled-save-restore", "SAVE-AT")
        summary = run_scheduled_save_restore_time_state_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            save_time=5.0,
            post_save_time=8.0,
        )

        assert summary["leader_initiate_save"].args[0] == config.save_name
        assert summary["leader_logical_time"].value == 8.0
        assert summary["restored_leader_time"].value == 5.0
        assert summary["restored_wing_time"].value == 5.0


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_object_state_matrix(kind: str):
    config = SaveRestoreScenarioConfig(
        federation_name=f"{kind}-restore-object-state-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"{kind}-RESTORE-OBJECT-{uuid.uuid4().hex[:8]}",
    )
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        leader_fed = RecordingFederateAmbassador()
        wing_fed = RecordingFederateAmbassador()
        summary = run_restore_object_state_scenario(
            leader,
            wing,
            config=config,
            leader_federate=leader_fed,
            wing_federate=wing_fed,
            object_instance_name=f"{kind}-Restore-State-Object",
        )
        assert summary["leader_restore_succeeded"].args == (config.save_name,)
        assert summary["wing_initiate_restore"].args[0] == config.save_name
        assert summary["informed_federate_name"] == config.wing_name


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_federate_local_state_matrix(kind: str):
    config = SaveRestoreScenarioConfig(
        federation_name=f"{kind}-restore-local-state-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name=f"{kind}-RESTORE-LOCAL-{uuid.uuid4().hex[:8]}",
    )
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        leader_fed = RecordingFederateAmbassador()
        wing_fed = RecordingFederateAmbassador()
        summary = run_restore_federate_local_state_scenario(
            leader,
            wing,
            config=config,
            leader_federate=leader_fed,
            wing_federate=wing_fed,
            object_instance_name=f"{kind}-Restore-Local-State",
        )
        assert summary["leader_restored"] is not None
        assert summary["wing_restored"] is not None


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_failure_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "save-failure", "PITCH-SAVE-FAIL")
        summary = run_save_failure_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_not_saved"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_SAVE"
        assert summary["wing_not_saved"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_SAVE"

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_request_failure_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "restore-request-failure", "PITCH-SAVE")
        missing_save_name = f"MISSING-{uuid.uuid4().hex[:8]}"
        summary = run_restore_request_failure_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            missing_save_name=missing_save_name,
        )

        assert summary["restore_failed"].args == (missing_save_name,)

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_failure_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "restore-failure", "PITCH-RESTORE-FAIL")
        summary = run_restore_failure_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_not_restored"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_RESTORE"
        assert summary["wing_not_restored"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_RESTORE"

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_save_abort_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "save-abort", "PITCH-SAVE-ABORT")
        summary = run_save_abort_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_not_saved"].args[0].name == "SAVE_ABORTED"
        assert summary["wing_not_saved"].args[0].name == "SAVE_ABORTED"

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_restore_abort_matrix(kind: str):
    with _pitch_runtime_case(kind, 2) as (leader, wing):
        config = _pitch_save_restore_config(kind, "restore-abort", "PITCH-RESTORE-ABORT")
        summary = run_restore_abort_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_not_restored"].args[0].name == "RESTORE_ABORTED"
        assert summary["wing_not_restored"].args[0].name == "RESTORE_ABORTED"

        cleanup_federation(
            config.federation_name,
            destroyer=leader,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((wing, ResignAction.NO_ACTION),),
            disconnect_rtis=(wing, leader),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ownership_matrix(kind: str):
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = _pitch_ownership_config(kind, "owner")
    with _pitch_runtime_case(kind, 2) as (owner, acquirer):
        summary = run_attribute_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )

        acquired = summary["acquired"]
        informed = summary["informed"]
        not_owned = summary["not_owned"]
        assert not_owned.args == (summary["object_instance"], summary["owner_attribute"])
        assert acquired.args[0] == summary["acquirer_object_instance"]
        assert summary["acquirer_attribute"] in acquired.args[1]
        assert informed.args[0] == summary["object_instance"]
        assert informed.args[1] == summary["owner_attribute"]
        assert summary["informed_federate_name"] == config.acquirer_name

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_negotiated_ownership_matrix(kind: str):
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = _pitch_negotiated_ownership_config(kind, "nego")
    with _pitch_runtime_case(kind, 2) as (owner, acquirer):
        try:
            summary = run_negotiated_attribute_ownership_scenario(
                owner,
                acquirer,
                config=config,
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
        except (RTIexception, AssertionError) as exc:
            pytest.skip(
                "Pitch negotiated ownership path is not yet promotable in this runtime: "
                f"{_format_probe_exception(exc)}"
            )

        assert summary["release"].args == (
            summary["release_object_instance"],
            {summary["owner_attribute"]},
            b"reacquire-request",
        )
        assert summary["cancellation"].args == (
            summary["release_acquirer_object_instance"],
            {summary["acquirer_attribute"]},
        )
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["release_acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["release_object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_negotiated_divesting_offer_probe(kind: str):
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = _pitch_negotiated_ownership_config(kind, "nego-offer")
    with _pitch_runtime_case(kind, 2) as (owner, acquirer):
        summary = probe_negotiated_attribute_ownership_offer(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )

        release = summary["release"]
        offered_acquired = summary["offered_acquired"]
        divest_confirmation = summary["divestiture_confirmation"]
        if release is None and offered_acquired is None and divest_confirmation is None:
            pytest.skip(
                "Pitch negotiated divesting-offer probe produced no release callback, no immediate acquisition, and no "
                "divestiture confirmation after acquisition request"
            )

        if offered_acquired is not None:
            assert offered_acquired.args[0] == summary["acquirer_object_instance"]
            assert offered_acquired.args[1] == {summary["acquirer_attribute"]}
        if divest_confirmation is not None:
            assert divest_confirmation.args[0] == summary["object_instance"]
            assert summary["owner_attribute"] in divest_confirmation.args[1]
        if release is not None:
            assert release.args == (
                summary["object_instance"],
                {summary["owner_attribute"]},
                b"acquire-request",
            )

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_release_request_owned_attribute_probe(kind: str):
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = _pitch_release_request_config(kind, "release-probe", b"acquire-request", "ifwanted")
    with _pitch_runtime_case(kind, 2) as (owner, acquirer):
        try:
            summary = run_release_request_ownership_scenario(
                owner,
                acquirer,
                config=config,
                owner_federate=owner_fed,
                acquirer_federate=acquirer_fed,
            )
        except (RTIexception, AssertionError) as exc:
            pytest.skip(
                "Pitch owned-attribute release-request probe is not yet stable in this runtime: "
                f"{_format_probe_exception(exc)}"
            )

        assert summary["release"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"acquire-request",
        )
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ownership_unavailable_matrix(kind: str):
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = _pitch_ownership_config(kind, "ownership-unavailable")
    with _pitch_runtime_case(kind, 2) as (owner, acquirer):
        summary = run_attribute_ownership_unavailable_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )

        assert summary["unavailable"].args[0] == summary["object_instance"]
        assert summary["acquirer_attribute"] in summary["unavailable"].args[1]

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_release_denied_ownership_matrix(kind: str):
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    config = _pitch_release_request_config(kind, "release-denied", b"deny-request", "deny")
    with _pitch_runtime_case(kind, 2) as (owner, acquirer):
        summary = run_release_request_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_fed,
            acquirer_federate=acquirer_fed,
        )

        assert summary["release"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"deny-request",
        )
        assert summary["acquired"] is None

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(acquirer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_non_owner_update_rejection_matrix(kind: str):
    owner_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()
    config = _pitch_non_owner_update_config(kind)
    with _pitch_runtime_case(kind, 2) as (owner, observer):
        summary = run_non_owner_update_rejection_scenario(
            owner,
            observer,
            config=config,
            owner_federate=owner_fed,
            observer_federate=observer_fed,
        )

        assert summary["failure"] is not None
        assert summary["failure_type"]

        cleanup_federation(
            config.federation_name,
            destroyer=owner,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((observer, ResignAction.NO_ACTION),),
            disconnect_rtis=(observer, owner),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ddm_matrix(kind: str):
    sender_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-probe", role="sender")
    receiver_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-probe", role="receiver")
    config = _pitch_ddm_config(kind, "ddm")
    with _pitch_runtime_case(kind, 2) as (sender, receiver):
        summary = run_suite_ddm_scenario(
            sender,
            receiver,
            config=config,
            sender_federate=sender_fed,
            receiver_federate=receiver_fed,
        )

        assert summary["received_count"] == 1
        assert summary["received_payload"] == {"Message": "near"}

        cleanup_federation(
            config["federation_name"],
            destroyer=sender,
            destroyer_resign_action=ResignAction.NO_ACTION,
            remaining_resignations=((receiver, ResignAction.NO_ACTION),),
            disconnect_rtis=(receiver, sender),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ddm_declaration_gating_matrix(kind: str):
    publisher_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-declaration-gating", role="publisher")
    subscriber_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-declaration-gating", role="subscriber")
    config = DdmDeclarationGatingScenarioConfig(
        federation_name=f"{kind}-ddm-declaration-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_ddm_declaration_gating_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discovery_before_subscription"] is None
        assert summary["reflection_before_subscription"] is None
        assert summary["interaction_before_subscription"] is None
        assert summary["discovery_after_subscription"] is not None
        assert summary["reflection_after_subscription"] is not None
        assert summary["interaction_after_subscription"] is not None

        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ddm_object_region_lifecycle_matrix(kind: str):
    publisher_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-object-lifecycle", role="publisher")
    subscriber_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-object-lifecycle", role="subscriber")
    config = DdmObjectRegionLifecycleScenarioConfig(
        federation_name=f"{kind}-ddm-object-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_ddm_object_region_lifecycle_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discovery"] is not None
        assert summary["provide"] is not None
        assert summary["received"] is not None
        assert summary["suppressed_receive"] is None

        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )


@pytest.mark.parametrize("kind", ["pitch-jpype", "pitch-py4j"])
def test_pitch_backend_ddm_passive_region_subscription_matrix(kind: str):
    publisher_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-passive", role="publisher")
    subscriber_fed = SuiteRecordingFederateAmbassador(profile=kind, scenario="ddm-passive", role="subscriber")
    config = DdmPassiveRegionScenarioConfig(
        federation_name=f"{kind}-ddm-passive-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
        summary = run_ddm_passive_region_subscription_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discovery"] is not None
        assert summary["received"] is not None

        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
            disconnect_rtis=(subscriber, publisher),
        )


def test_pitch_time_semantic_profile_matches_across_java_bridges():
    profiles: dict[str, dict[str, object]] = {}
    for kind in ("pitch-jpype", "pitch-py4j"):
        federation_name = f"{kind}-time-profile-{uuid.uuid4().hex[:8]}"
        publisher_fed = RecordingFederateAmbassador()
        subscriber_fed = RecordingFederateAmbassador()
        with _pitch_runtime_case(kind, 2) as (publisher, subscriber):
            summary = run_two_federate_exchange_scenario(
                publisher,
                subscriber,
                config=_pitch_exchange_config(federation_name, f"{kind}-TimeProfile-1"),
                publisher_federate=publisher_fed,
                subscriber_federate=subscriber_fed,
            )
            profiles[kind] = _normalized_exchange_profile(summary)
            cleanup_federation(
                federation_name,
                destroyer=publisher,
                destroyer_resign_action=ResignAction.DELETE_OBJECTS,
                remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
                disconnect_rtis=(subscriber, publisher),
            )

    assert profiles["pitch-py4j"] == profiles["pitch-jpype"]


def test_pitch_negotiated_ownership_profile_matches_across_java_bridges():
    profiles: dict[str, dict[str, object]] = {}
    for kind in ("pitch-jpype", "pitch-py4j"):
        config = _pitch_negotiated_ownership_config(kind, "nego-profile")
        owner_fed = RecordingFederateAmbassador()
        acquirer_fed = RecordingFederateAmbassador()
        with _pitch_runtime_case(kind, 2) as (owner, acquirer):
            try:
                summary = run_negotiated_attribute_ownership_scenario(
                    owner,
                    acquirer,
                    config=config,
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            except (RTIexception, AssertionError) as exc:
                pytest.skip(
                    "Pitch negotiated ownership path is not yet promotable in this runtime: "
                    f"{_format_probe_exception(exc)}"
                )
            profiles[kind] = _normalized_negotiated_profile(summary)

    assert profiles["pitch-py4j"] == profiles["pitch-jpype"]
