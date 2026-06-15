from __future__ import annotations

import math
import uuid

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_fom_target_radar.scenarios import run_target_radar_scenario
from hla2010.enums import OrderType, ResignAction
from hla2010.exceptions import (
    AlreadyConnected,
    CouldNotOpenFDD,
    ErrorReadingFDD,
    FederateAlreadyExecutionMember,
    FederateIsExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InconsistentFDD,
    InvalidResignAction,
    NotConnected,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
    RestoreInProgress,
    RestoreNotInProgress,
    SaveInProgress,
)
from hla2010_rti_python import PythonRTIConfig
from hla2010.time import HLAinteger64Interval, HLAinteger64Time
from hla2010_verification_harness import (
    DdmObjectRegionLifecycleScenarioConfig,
    DdmDeclarationGatingScenarioConfig,
    DdmPassiveRegionScenarioConfig,
    DeclarationManagementScenarioConfig,
    FederationLifecycleScenarioConfig,
    JoinScenarioConfig,
    NegotiatedOwnershipScenarioConfig,
    NonOwnerUpdateScenarioConfig,
    OwnershipScenarioConfig,
    RequestAttributeValueUpdateScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    ResignScenarioConfig,
    SaveRestoreScenarioConfig,
    SupportServicesScenarioConfig,
    SuiteRecordingFederateAmbassador,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_abort_save_exception_scenario,
    run_attribute_ownership_scenario,
    run_attribute_ownership_unavailable_scenario,
    run_ddm_object_region_lifecycle_scenario,
    run_ddm_declaration_gating_scenario,
    run_ddm_passive_region_subscription_scenario,
    run_support_factory_and_decode_scenario,
    run_restore_federate_local_state_scenario,
    run_restore_object_state_scenario,
    run_restore_request_failure_scenario,
    run_restore_failure_scenario,
    run_save_abort_scenario,
    run_save_failure_scenario,
    run_declaration_management_scenario,
    run_disconnect_mom_cleanup_scenario,
    run_federation_lifecycle_negative_scenario,
    run_federation_listing_scenario,
    run_federation_lifecycle_scenario,
    run_fom_integrity_negative_scenario,
    run_fom_module_visibility_scenario,
    run_failed_federate_synchronization_scenario,
    run_join_precondition_scenario,
    run_late_join_synchronization_scenario,
    run_multi_module_fom_visibility_scenario,
    run_multi_participation_scenario,
    run_multiple_synchronization_points_scenario,
    run_non_owner_update_rejection_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_request_attribute_value_update_routing_scenario,
    run_request_attribute_value_update_scenario,
    run_resign_mom_cleanup_scenario,
    run_resign_precondition_scenario,
    run_resigned_federate_callback_silence_scenario,
    run_release_request_ownership_scenario,
    run_restore_abort_exception_scenario,
    run_restore_abort_scenario,
    run_restore_abort_scenario,
    run_restore_participant_exception_scenario,
    run_restore_request_precondition_scenario,
    run_restore_status_exception_scenario,
    run_save_restore_queued_callback_scenario,
    run_save_restore_scenario,
    run_save_participant_exception_scenario,
    run_save_request_precondition_scenario,
    run_save_status_exception_scenario,
    run_synchronization_registration_failure_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from tests.scenarios.python_route_parity_support import python_route_params, python_rti_pair, python_rti_triple, python_single_rti
from tests.vendors.runtime_support import cleanup_federation


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_target_radar(route) -> None:
    with python_rti_pair(route) as pair:
        result = run_target_radar_scenario(
            lambda role: pair.left if role == "target" else pair.right,
            federation_name=f"target-radar-{route}-{uuid.uuid4().hex[:8]}",
            steps=3,
        )

    assert len(result.track_reports) == 3
    assert any(name == "provide_attribute_value_update" for name, _ in result.target_events)
    assert [name for name, _ in result.radar_events].count("track") == 3
    first = result.track_reports[0]
    assert first.target_name == "Target-1"
    assert math.isclose(first.range_m, math.sqrt(10_250.0**2 + 1_030.0**2 + 2_000.0**2))
    assert first.rcs_square_meters == 12.5
    assert result.track_reports[-1].range_m > result.track_reports[0].range_m


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_federation_lifecycle(route) -> None:
    with python_single_rti(route) as rti:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-lifecycle-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
        )
        summary = run_federation_lifecycle_scenario(
            rti,
            config=config,
            federate=RecordingFederateAmbassador(),
        )

        assert summary["federation_name"] == config.federation_name
        assert summary["federate_handle"] is not None


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_object_exchange(route) -> None:
    with python_rti_pair(route) as pair:
        publisher_fed = RecordingFederateAmbassador()
        subscriber_fed = RecordingFederateAmbassador()
        config = TwoFederateExchangeConfig(
            federation_name=f"python-exchange-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            interaction_class_name="HLAinteractionRoot.SmokeInteraction",
            parameter_name="Message",
            object_instance_name=f"python-object-{uuid.uuid4().hex[:8]}",
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

        summary = run_two_federate_exchange_scenario(
            pair.left,
            pair.right,
            config=config,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discover"].args[2] == config.object_instance_name
        assert summary["reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-r"}
        assert summary["interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-r"}
        assert summary["remove"] is not None
        assert summary["remove"].args[1] == config.delete_tag

        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
            config=config,
        )
        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_ownership(route) -> None:
    with python_rti_pair(route) as pair:
        config = OwnershipScenarioConfig(
            federation_name=f"python-ownership-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-owned-{uuid.uuid4().hex[:8]}",
        )

        summary = run_attribute_ownership_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
        )

        assert summary["not_owned"].args == (summary["object_instance"], summary["owner_attribute"])
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
        assert summary["informed"].args[0] == summary["object_instance"]
        assert summary["informed"].args[1] == summary["owner_attribute"]
        assert summary["informed_federate_name"] == config.acquirer_name

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_synchronization(route) -> None:
    with python_rti_pair(route) as pair:
        config = SynchronizationScenarioConfig(
            federation_name=f"python-sync-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SyncFederate",
            label="ReadyToRun",
            tag=b"startup",
        )

        summary = run_synchronization_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_registration"].args == ("ReadyToRun",)
        assert summary["leader_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["wing_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_synchronization_registration_failure(route) -> None:
    with python_rti_pair(route) as pair:
        config = SynchronizationScenarioConfig(
            federation_name=f"python-sync-failure-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SyncFederate",
            label="ReadyToRun",
            tag=b"startup",
        )

        summary = run_synchronization_registration_failure_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["registration_success"].args == ("ReadyToRun",)
        assert summary["registration_failure"].args[0] == "ReadyToRun"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_failed_federate_synchronization(route) -> None:
    with python_rti_pair(route) as pair:
        config = SynchronizationScenarioConfig(
            federation_name=f"python-sync-failed-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SyncFederate",
            label="PreRun",
            tag=b"startup",
        )

        summary = run_failed_federate_synchronization_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            leader_success=True,
            wing_success=False,
        )

        assert summary["leader_sync"].args[0] == "PreRun"
        assert summary["wing_handle"] in summary["leader_sync"].args[1]
        assert summary["leader_handle"] not in summary["leader_sync"].args[1]


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_late_join_synchronization(route) -> None:
    with python_rti_triple(route) as trio:
        config = SynchronizationScenarioConfig(
            federation_name=f"python-sync-late-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            late_name="Late",
            federate_type="SyncFederate",
            label="ReadyToRun",
            tag=b"startup",
        )

        summary = run_late_join_synchronization_scenario(
            trio.left,
            trio.middle,
            trio.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            late_federate=RecordingFederateAmbassador(),
        )

        assert summary["late_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"
        assert summary["late_sync"].args[0] == "ReadyToRun"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_multiple_synchronization_points(route) -> None:
    with python_rti_pair(route) as pair:
        config = SynchronizationScenarioConfig(
            federation_name=f"python-sync-multi-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SyncFederate",
            label="ReadyToRun",
            tag=b"startup",
            second_label="PreRun",
            second_tag=b"prerun",
        )

        summary = run_multiple_synchronization_points_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert {record.args[0] for record in summary["leader_announces"]} == {"ReadyToRun", "PreRun"}
        assert {record.args[0] for record in summary["wing_announces"]} == {"ReadyToRun", "PreRun"}
        assert summary["first_sync_leader"].args[0] == "ReadyToRun"
        assert summary["first_sync_wing"].args[0] == "ReadyToRun"
        assert summary["second_sync_leader"].args[0] == "PreRun"
        assert summary["second_sync_wing"].args[0] == "PreRun"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_negotiated_ownership(route) -> None:
    with python_rti_pair(route) as pair:
        config = NegotiatedOwnershipScenarioConfig(
            federation_name=f"python-negotiated-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-negotiated-{uuid.uuid4().hex[:8]}",
            assumption_tag=b"assume-offer",
            request_tag=b"acquire-request",
            cancel_tag=b"reacquire-request",
        )

        summary = run_negotiated_attribute_ownership_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
        )

        assert summary["negotiated_divestiture_supported"] is True
        assert summary["assumption"] is not None
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
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_release_request_ownership(route) -> None:
    with python_rti_pair(route) as pair:
        config = ReleaseRequestOwnershipScenarioConfig(
            federation_name=f"python-release-request-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-release-{uuid.uuid4().hex[:8]}",
            request_tag=b"acquire-request",
            owner_action="ifwanted",
        )

        summary = run_release_request_ownership_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
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
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_release_request_denied(route) -> None:
    with python_rti_pair(route) as pair:
        config = ReleaseRequestOwnershipScenarioConfig(
            federation_name=f"python-release-denied-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-release-denied-{uuid.uuid4().hex[:8]}",
            request_tag=b"deny-request",
            owner_action="deny",
        )

        summary = run_release_request_ownership_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
        )

        assert summary["release"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"deny-request",
        )
        assert summary["acquired"] is None

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_ownership_unavailable(route) -> None:
    with python_rti_pair(route) as pair:
        config = OwnershipScenarioConfig(
            federation_name=f"python-ownership-unavailable-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-unavailable-{uuid.uuid4().hex[:8]}",
        )

        summary = run_attribute_ownership_unavailable_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            acquirer_federate=RecordingFederateAmbassador(),
        )

        assert summary["unavailable"].args[0] == summary["object_instance"]
        assert summary["acquirer_attribute"] in summary["unavailable"].args[1]

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_restore(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-restore-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-{uuid.uuid4().hex[:8]}",
        )

        summary = run_save_restore_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_initiate_save"].args[0] == config.save_name
        assert summary["wing_initiate_save"].args == (config.save_name,)
        assert summary["leader_restore_succeeded"].args == (config.save_name,)
        assert summary["wing_initiate_restore"].args[0] == config.save_name


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_restore_queued_callbacks(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-restore-queued-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-QUEUED-{uuid.uuid4().hex[:8]}",
        )

        summary = run_save_restore_queued_callback_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["leader_initiate_save"].args[0] == config.save_name
        assert summary["wing_initiate_save"].args == (config.save_name,)
        assert summary["leader_saved"] is not None
        assert summary["wing_saved"] is not None
        assert summary["leader_restore_succeeded"].args == (config.save_name,)
        assert summary["wing_initiate_restore"].args[0] == config.save_name
        assert summary["leader_restored"] is not None
        assert summary["wing_restored"] is not None


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_declaration_management(route) -> None:
    with python_rti_pair(route) as pair:
        config = DeclarationManagementScenarioConfig(
            federation_name=f"python-declaration-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            interaction_class_name="HLAinteractionRoot.SmokeInteraction",
            parameter_name="Message",
            object_instance_name=f"python-declaration-{uuid.uuid4().hex[:8]}",
        )

        summary = run_declaration_management_scenario(
            pair.left,
            pair.right,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
            subscriber_federate=RecordingFederateAmbassador(),
        )

        assert [record.args for record in summary["start_records"]] == [
            (summary["publisher_class"],),
            (summary["publisher_class"],),
        ]
        assert [record.args for record in summary["stop_records"]] == [
            (summary["publisher_class"],),
            (summary["publisher_class"],),
        ]
        assert [record.args for record in summary["turn_on_records"]] == [
            (summary["publisher_interaction"],),
            (summary["publisher_interaction"],),
        ]
        assert [record.args for record in summary["turn_off_records"]] == [
            (summary["publisher_interaction"],),
            (summary["publisher_interaction"],),
        ]
        assert summary["discover_record"].args[2] == config.object_instance_name
        assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
        assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
        assert summary["suppressed_reflect_count"] == 1
        assert summary["suppressed_interaction_count"] == 1

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_request_attribute_value_update(route) -> None:
    with python_rti_pair(route) as pair:
        config = RequestAttributeValueUpdateScenarioConfig(
            federation_name=f"python-ravu-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            object_instance_name=f"RAVU-{uuid.uuid4().hex[:8]}",
            request_tag=b"python-ravu",
        )

        summary = run_request_attribute_value_update_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            requester_federate=RecordingFederateAmbassador(),
        )

        assert summary["provide_record"].args == (
            summary["object_instance"],
            {summary["owner_attribute"]},
            b"python-ravu",
        )

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_request_attribute_value_update_routing(route) -> None:
    with python_rti_triple(route) as trio:
        config = RequestAttributeValueUpdateScenarioConfig(
            federation_name=f"python-ravu-routing-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            object_instance_name=f"python-RAVU-{uuid.uuid4().hex[:8]}",
            request_tag=b"object-only",
        )

        summary = run_request_attribute_value_update_routing_scenario(
            trio.left,
            trio.middle,
            trio.right,
            config=config,
            owner_a_federate=RecordingFederateAmbassador(),
            owner_b_federate=RecordingFederateAmbassador(),
            requester_federate=RecordingFederateAmbassador(),
        )

        assert summary["object_target_provide_a"].args == (summary["object_a"], {summary["requester_attribute"]}, b"object-only")
        assert summary["object_target_provide_b"] is None
        assert summary["class_target_provide_a"].args == (summary["object_a"], {summary["requester_attribute"]}, b"class-wide")
        assert summary["class_target_provide_b"].args == (summary["object_b"], {summary["requester_attribute"]}, b"class-wide")

        cleanup_federation(
            config.federation_name,
            destroyer=trio.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((trio.middle, ResignAction.DELETE_OBJECTS), (trio.right, ResignAction.NO_ACTION)),
            disconnect_rtis=(trio.right, trio.middle, trio.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_non_owner_update_rejection(route) -> None:
    with python_rti_pair(route) as pair:
        config = NonOwnerUpdateScenarioConfig(
            federation_name=f"python-non-owner-update-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            owner_name="Owner",
            observer_name="Observer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name=f"python-illegal-update-{uuid.uuid4().hex[:8]}",
        )

        summary = run_non_owner_update_rejection_scenario(
            pair.left,
            pair.right,
            config=config,
            owner_federate=RecordingFederateAmbassador(),
            observer_federate=RecordingFederateAmbassador(),
        )

        assert summary["failure"] is not None
        assert summary["failure_type"]

        cleanup_federation(
            config.federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_ddm_object_region_lifecycle(route) -> None:
    with python_rti_pair(route) as pair:
        federation_name = f"python-ddm-object-{route}-{uuid.uuid4().hex[:8]}"
        publisher_fed = SuiteRecordingFederateAmbassador(profile=route, scenario="ddm-object-lifecycle", role="publisher")
        subscriber_fed = SuiteRecordingFederateAmbassador(profile=route, scenario="ddm-object-lifecycle", role="subscriber")

        summary = run_ddm_object_region_lifecycle_scenario(
            pair.left,
            pair.right,
            config=DdmObjectRegionLifecycleScenarioConfig(
                federation_name=federation_name,
                fom_modules=("TargetRadarFOMmodule.xml",),
            ),
            publisher_federate=publisher_fed,
            subscriber_federate=subscriber_fed,
        )

        assert summary["discovery"] is not None
        assert summary["provide"] is not None
        assert summary["received"] is not None
        assert summary["suppressed_receive"] is None

        cleanup_federation(
            federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_federation_lifecycle_with_mim(route) -> None:
    with python_single_rti(route) as rti:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-lifecycle-mim-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            use_mim_create=True,
        )
        summary = run_federation_lifecycle_scenario(rti, config=config, federate=RecordingFederateAmbassador())
        assert summary["federation_name"] == config.federation_name
        assert summary["use_mim_create"] is True


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_federation_listing(route) -> None:
    with python_single_rti(route) as rti:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-listing-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
        )
        summary = run_federation_listing_scenario(rti, config=config, federate=RecordingFederateAmbassador())
        assert summary["federation_name"] == config.federation_name
        assert summary["report"].method_name == "reportFederationExecutions"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_fom_module_visibility(route) -> None:
    with python_single_rti(route) as rti:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-fom-visibility-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
        )
        summary = run_fom_module_visibility_scenario(rti, config=config, federate=RecordingFederateAmbassador())
        assert summary["federation_name"] == config.federation_name
        assert summary["federate_handle"] is not None


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_federation_lifecycle_negative(route) -> None:
    with python_rti_pair(route) as pair:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-lifecycle-negative-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
        )
        summary = run_federation_lifecycle_negative_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["already_connected"], AlreadyConnected)
        assert isinstance(summary["duplicate_create"], FederationExecutionAlreadyExists)
        assert isinstance(summary["disconnect_while_joined"], FederateIsExecutionMember)
        assert isinstance(summary["destroy_with_joined"], FederatesCurrentlyJoined)
        assert isinstance(summary["destroy_missing"], FederationExecutionDoesNotExist)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_multi_participation(route) -> None:
    with python_rti_triple(route) as trio:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-multi-participation-{route}-{uuid.uuid4().hex[:8]}",
            secondary_federation_name=f"python-multi-participation-secondary-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            federate_name="Leader",
            second_federate_name="Wing",
            secondary_federate_name="Shadow",
        )
        summary = run_multi_participation_scenario(
            trio.left,
            trio.middle,
            trio.right,
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


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_fom_integrity_negative(route) -> None:
    strict_config = PythonRTIConfig(name=f"python-fom-negative-{route}", strict_fom_loading=True)
    with python_rti_pair(route, python_config=strict_config) as pair:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-fom-negative-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            federate_name="Leader",
            second_federate_name="Wing",
            federate_type="LifecycleType",
        )
        summary = run_fom_integrity_negative_scenario(
            pair.left,
            pair.right,
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


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_multi_module_fom_visibility(route) -> None:
    with python_single_rti(route) as rti:
        config = FederationLifecycleScenarioConfig(
            federation_name=f"python-fom-multi-{route}-{uuid.uuid4().hex[:8]}",
            federate_name="Leader",
            federate_type="LifecycleType",
        )
        summary = run_multi_module_fom_visibility_scenario(rti, config=config, federate=RecordingFederateAmbassador())
        assert summary["federation_name"] == config.federation_name
        assert summary["federate_handle"] is not None


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_abort_exception(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-status-negative-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-STATUS-{uuid.uuid4().hex[:8]}",
        )
        summary = run_restore_abort_exception_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["restore_not_in_progress"], RestoreNotInProgress)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_status_exception(route) -> None:
    with python_single_rti(route) as rti:
        summary = run_save_status_exception_scenario(rti, federate=RecordingFederateAmbassador())
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_status_exception(route) -> None:
    with python_single_rti(route) as rti:
        summary = run_restore_status_exception_scenario(rti, federate=RecordingFederateAmbassador())
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_request_precondition(route) -> None:
    with python_rti_pair(route) as pair:
        summary = run_save_request_precondition_scenario(
            pair.left,
            pair.right,
            config=SaveRestoreScenarioConfig(
                federation_name=f"python-save-request-{route}-{uuid.uuid4().hex[:8]}",
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
                logical_time_implementation_name="HLAinteger64Time",
                leader_name="Leader",
                wing_name="Wing",
                federate_type="SaveRestoreFederate",
                save_name=f"SAVE-REQ-{uuid.uuid4().hex[:8]}",
            ),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["save_in_progress"], SaveInProgress)
        assert isinstance(summary["restore_in_progress"], RestoreInProgress)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_request_precondition(route) -> None:
    with python_rti_pair(route) as pair:
        summary = run_restore_request_precondition_scenario(
            pair.left,
            pair.right,
            config=SaveRestoreScenarioConfig(
                federation_name=f"python-restore-request-{route}-{uuid.uuid4().hex[:8]}",
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
                logical_time_implementation_name="HLAinteger64Time",
                leader_name="Leader",
                wing_name="Wing",
                federate_type="SaveRestoreFederate",
                save_name=f"RESTORE-REQ-{uuid.uuid4().hex[:8]}",
            ),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["save_in_progress"], SaveInProgress)
        assert isinstance(summary["restore_in_progress"], RestoreInProgress)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_participant_exception(route) -> None:
    with python_rti_pair(route) as pair:
        summary = run_save_participant_exception_scenario(
            pair.left,
            pair.right,
            config=SaveRestoreScenarioConfig(
                federation_name=f"python-save-participant-{route}-{uuid.uuid4().hex[:8]}",
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
                logical_time_implementation_name="HLAinteger64Time",
                leader_name="Leader",
                wing_name="Wing",
                federate_type="SaveRestoreFederate",
                save_name=f"SAVE-PART-{uuid.uuid4().hex[:8]}",
            ),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["begun_not_connected"], NotConnected)
        assert isinstance(summary["complete_not_connected"], NotConnected)
        assert isinstance(summary["not_complete_not_connected"], NotConnected)
        assert isinstance(summary["begun_not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["complete_not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["not_complete_not_joined"], FederateNotExecutionMember)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_abort_save_exception(route) -> None:
    with python_single_rti(route) as rti:
        summary = run_abort_save_exception_scenario(rti, federate=RecordingFederateAmbassador())
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_participant_exception(route) -> None:
    with python_rti_pair(route) as pair:
        summary = run_restore_participant_exception_scenario(
            pair.left,
            pair.right,
            config=SaveRestoreScenarioConfig(
                federation_name=f"python-restore-participant-{route}-{uuid.uuid4().hex[:8]}",
                fom_modules=("hla2010:VendorSmokeFOM.xml",),
                logical_time_implementation_name="HLAinteger64Time",
                leader_name="Leader",
                wing_name="Wing",
                federate_type="SaveRestoreFederate",
                save_name=f"RESTORE-PART-{uuid.uuid4().hex[:8]}",
            ),
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["complete_not_connected"], NotConnected)
        assert isinstance(summary["not_complete_not_connected"], NotConnected)
        assert isinstance(summary["complete_not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["not_complete_not_joined"], FederateNotExecutionMember)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_resigned_federate_callback_silence(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-resign-callback-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"POST-RESIGN-SAVE-{uuid.uuid4().hex[:8]}",
        )
        summary = run_resigned_federate_callback_silence_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_initiate_save"].args == (config.save_name,)
        assert summary["leader_saved"] is not None
        assert summary["wing_record_count_after"] == summary["wing_record_count_before"]
        assert summary["wing_post_resign_records"] == []


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_resign_precondition(route) -> None:
    with python_rti_pair(route) as pair:
        config = ResignScenarioConfig(
            federation_name=f"python-resign-negative-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="ResignFederate",
            object_instance_name=f"Pending-Acquisition-{uuid.uuid4().hex[:8]}",
        )
        summary = run_resign_precondition_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["not_joined"], FederateNotExecutionMember)
        assert isinstance(summary["invalid_action"], InvalidResignAction)
        assert isinstance(summary["owns_attributes"], FederateOwnsAttributes)
        assert isinstance(summary["acquisition_pending"], OwnershipAcquisitionPending)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_resign_mom_cleanup(route) -> None:
    with python_rti_pair(route) as pair:
        config = ResignScenarioConfig(
            federation_name=f"python-resign-mom-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="ResignFederate",
        )
        summary = run_resign_mom_cleanup_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["wing_before"].args[1]
        assert summary["federation_after"].args[1]
        assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_disconnect_mom_cleanup(route) -> None:
    with python_rti_pair(route) as pair:
        config = ResignScenarioConfig(
            federation_name=f"python-disconnect-mom-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="ResignFederate",
        )
        summary = run_disconnect_mom_cleanup_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_before"].args[1]
        assert summary["federation_after"].args[1]
        assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_join_precondition(route) -> None:
    with python_rti_triple(route) as trio:
        config = JoinScenarioConfig(
            federation_name=f"python-join-negative-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            late_name="Late",
            federate_type="JoinFederate",
            save_name=f"JOIN-BLOCK-{uuid.uuid4().hex[:8]}",
        )
        summary = run_join_precondition_scenario(
            trio.left,
            trio.middle,
            trio.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            late_federate=RecordingFederateAmbassador(),
        )
        assert isinstance(summary["not_connected"], NotConnected)
        assert isinstance(summary["missing_federation"], FederationExecutionDoesNotExist)
        assert isinstance(summary["duplicate_name"], FederateNameAlreadyInUse)
        assert isinstance(summary["already_joined"], FederateAlreadyExecutionMember)
        assert isinstance(summary["save_in_progress"], SaveInProgress)
        assert isinstance(summary["restore_in_progress"], RestoreInProgress)


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_object_state(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-restore-object-state-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-OBJECT-{uuid.uuid4().hex[:8]}",
        )
        summary = run_restore_object_state_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_restore_succeeded"].args == (config.save_name,)
        assert summary["wing_initiate_restore"].args[0] == config.save_name
        assert summary["informed_federate_name"] == config.wing_name


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_federate_local_state(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-restore-local-state-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("TargetRadarFOMmodule.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-LOCAL-{uuid.uuid4().hex[:8]}",
        )
        summary = run_restore_federate_local_state_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_restored"] is not None
        assert summary["wing_restored"] is not None


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_failure(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-failure-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-FAIL-{uuid.uuid4().hex[:8]}",
        )
        summary = run_save_failure_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_not_saved"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_SAVE"
        assert summary["wing_not_saved"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_SAVE"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_request_failure(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-restore-request-failure-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-{uuid.uuid4().hex[:8]}",
        )
        summary = run_restore_request_failure_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            missing_save_name=f"MISSING-{uuid.uuid4().hex[:8]}",
        )
        assert summary["restore_failed"].args[0].startswith("MISSING-")


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_failure(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-restore-failure-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-RESTORE-{uuid.uuid4().hex[:8]}",
        )
        summary = run_restore_failure_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_not_restored"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_RESTORE"
        assert summary["wing_not_restored"].args[0].name == "FEDERATE_REPORTED_FAILURE_DURING_RESTORE"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_save_abort(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-save-abort-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"SAVE-ABORT-{uuid.uuid4().hex[:8]}",
        )
        summary = run_save_abort_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_not_saved"].args[0].name == "SAVE_ABORTED"
        assert summary["wing_not_saved"].args[0].name == "SAVE_ABORTED"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_restore_abort(route) -> None:
    with python_rti_pair(route) as pair:
        config = SaveRestoreScenarioConfig(
            federation_name=f"python-restore-abort-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SaveRestoreFederate",
            save_name=f"RESTORE-ABORT-{uuid.uuid4().hex[:8]}",
        )
        summary = run_restore_abort_scenario(
            pair.left,
            pair.right,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )
        assert summary["leader_not_restored"].args[0].name == "RESTORE_ABORTED"
        assert summary["wing_not_restored"].args[0].name == "RESTORE_ABORTED"


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_ddm_declaration_gating(route) -> None:
    with python_rti_pair(route) as pair:
        federation_name = f"python-ddm-declaration-{route}-{uuid.uuid4().hex[:8]}"
        summary = run_ddm_declaration_gating_scenario(
            pair.left,
            pair.right,
            config=DdmDeclarationGatingScenarioConfig(
                federation_name=federation_name,
                fom_modules=("TargetRadarFOMmodule.xml",),
            ),
            publisher_federate=SuiteRecordingFederateAmbassador(profile=route, scenario="ddm-declaration-gating", role="publisher"),
            subscriber_federate=SuiteRecordingFederateAmbassador(profile=route, scenario="ddm-declaration-gating", role="subscriber"),
        )
        assert summary["discovery_before_subscription"] is None
        assert summary["reflection_before_subscription"] is None
        assert summary["interaction_before_subscription"] is None
        assert summary["discovery_after_subscription"] is not None
        assert summary["reflection_after_subscription"] is not None
        assert summary["interaction_after_subscription"] is not None
        cleanup_federation(
            federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_ddm_passive_region_subscription(route) -> None:
    with python_rti_pair(route) as pair:
        federation_name = f"python-ddm-passive-{route}-{uuid.uuid4().hex[:8]}"
        summary = run_ddm_passive_region_subscription_scenario(
            pair.left,
            pair.right,
            config=DdmPassiveRegionScenarioConfig(
                federation_name=federation_name,
                fom_modules=("TargetRadarFOMmodule.xml",),
            ),
            publisher_federate=SuiteRecordingFederateAmbassador(profile=route, scenario="ddm-passive", role="publisher"),
            subscriber_federate=SuiteRecordingFederateAmbassador(profile=route, scenario="ddm-passive", role="subscriber"),
        )
        assert summary["discovery"] is not None
        assert summary["received"] is not None
        cleanup_federation(
            federation_name,
            destroyer=pair.left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((pair.right, ResignAction.NO_ACTION),),
            disconnect_rtis=(pair.right, pair.left),
        )


@pytest.mark.parametrize("route", python_route_params())
def test_python_route_parity_support_factory_and_decode(route) -> None:
    with python_single_rti(route) as rti:
        config = SupportServicesScenarioConfig(
            federation_name=f"python-support-factory-{route}-{uuid.uuid4().hex[:8]}",
            fom_modules=("hla2010:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            object_instance_name=f"python-support-{uuid.uuid4().hex[:8]}",
        )
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
