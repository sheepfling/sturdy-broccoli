from __future__ import annotations

import math
import uuid

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_fom_target_radar.scenarios import run_target_radar_scenario
from hla2010.enums import OrderType, ResignAction
from hla2010.time import HLAinteger64Interval, HLAinteger64Time
from hla2010_verification_harness import (
    DdmObjectRegionLifecycleScenarioConfig,
    DeclarationManagementScenarioConfig,
    FederationLifecycleScenarioConfig,
    NegotiatedOwnershipScenarioConfig,
    NonOwnerUpdateScenarioConfig,
    OwnershipScenarioConfig,
    RequestAttributeValueUpdateScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    SaveRestoreScenarioConfig,
    SuiteRecordingFederateAmbassador,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_attribute_ownership_scenario,
    run_attribute_ownership_unavailable_scenario,
    run_ddm_object_region_lifecycle_scenario,
    run_declaration_management_scenario,
    run_federation_lifecycle_scenario,
    run_failed_federate_synchronization_scenario,
    run_late_join_synchronization_scenario,
    run_multiple_synchronization_points_scenario,
    run_non_owner_update_rejection_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_request_attribute_value_update_routing_scenario,
    run_request_attribute_value_update_scenario,
    run_release_request_ownership_scenario,
    run_save_restore_queued_callback_scenario,
    run_save_restore_scenario,
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
