from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.backends.grpc_transport import start_certi_grpc_server
from hla2010.enums import OrderType, ResignAction
from hla2010.rti import create_rti_ambassador
from hla2010_verification_harness.scenario_exchange import (
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_two_federate_exchange_scenario,
)
from hla2010_verification_harness.scenario_ownership import OwnershipScenarioConfig, run_attribute_ownership_scenario
from hla2010_verification_harness.scenario_sync import SynchronizationScenarioConfig, run_synchronization_scenario
from hla2010.time import HLAfloat64Interval, HLAfloat64Time
from hla2010_rti_certi.real_rti_certi import discover_certi_smoke_fom, launch_certi_rtig
from tests.vendors.runtime_support import cleanup_federation, close_all, require_vendor_preflight, reserve_udp_pair, terminate_all

pytestmark = pytest.mark.requires_loopback_server


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")
    require_vendor_preflight("certi", operator_hint="./tools/certi-easy preflight")


def test_grpc_transport_can_host_certi_exchange_end_to_end():
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    left_server = right_server = None
    left = right = None
    try:
        with reserve_udp_pair() as lease:
            left_udp_port, right_udp_port = lease.ports
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=left_udp_port)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=right_udp_port)
        left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
        right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})

        left_fed = RecordingFederateAmbassador()
        right_fed = RecordingFederateAmbassador()
        federation_name = f"GrpcHostedCERTIFederation-{uuid.uuid4().hex[:8]}"
        config = TwoFederateExchangeConfig(
            federation_name=federation_name,
            fom_modules=(smoke_fom,),
            logical_time_implementation_name="HLAinteger64Time",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            interaction_class_name="MsgR",
            parameter_name="MsgDataR",
            object_instance_name="GrpcHostedCERTIObject-1",
            attribute_payload=b"payload-r",
            attribute_tag=b"reflect-tag",
            interaction_payload=b"hello-r",
            interaction_tag=b"interaction-tag",
            enable_time_management=True,
            lookahead=HLAfloat64Interval(1.0),
            advance_time=HLAfloat64Time(8.0),
            timestamped_attribute_payload=b"payload-tso",
            timestamped_attribute_tag=b"reflect-tso",
            timestamped_attribute_time=HLAfloat64Time(5.0),
            timestamped_interaction_payload=b"hello-tso",
            timestamped_interaction_tag=b"interaction-tso",
            timestamped_interaction_time=HLAfloat64Time(6.0),
        )
        summary = run_two_federate_exchange_scenario(
            left,
            right,
            config=config,
            publisher_federate=left_fed,
            subscriber_federate=right_fed,
        )
        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=left_fed,
            subscriber_federate=right_fed,
            config=config,
        )
        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

        cleanup_federation(
            federation_name,
            destroyer=left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(right, left),
        )
    finally:
        close_all(right, left, right_server, left_server)
        terminate_all(rtig)


def test_grpc_transport_can_host_certi_synchronization_end_to_end():
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    left_server = right_server = None
    left = right = None
    try:
        with reserve_udp_pair() as lease:
            left_udp_port, right_udp_port = lease.ports
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=left_udp_port)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=right_udp_port)
        left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
        right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})

        left_fed = RecordingFederateAmbassador()
        right_fed = RecordingFederateAmbassador()
        federation_name = f"GrpcHostedCERTISync-{uuid.uuid4().hex[:8]}"
        summary = run_synchronization_scenario(
            left,
            right,
            config=SynchronizationScenarioConfig(
                federation_name=federation_name,
                fom_modules=(smoke_fom,),
                logical_time_implementation_name="HLAinteger64Time",
                leader_name="Leader",
                wing_name="Wing",
                federate_type="SyncFederate",
                label="ReadyToRun",
                tag=b"startup",
            ),
            leader_federate=left_fed,
            wing_federate=right_fed,
        )

        assert summary["leader_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["wing_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"

        cleanup_federation(
            federation_name,
            destroyer=left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((right, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
            disconnect_rtis=(right, left),
        )
    finally:
        close_all(right, left, right_server, left_server)
        terminate_all(rtig)


def test_grpc_transport_can_host_certi_ownership_end_to_end():
    _require_real_rti_smoke()
    try:
        rtig = launch_certi_rtig(verbose=0)
        smoke_fom = discover_certi_smoke_fom()
    except BackendUnavailableError as exc:
        pytest.skip(str(exc))

    left_server = right_server = None
    left = right = None
    try:
        with reserve_udp_pair() as lease:
            left_udp_port, right_udp_port = lease.ports
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=left_udp_port)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=right_udp_port)
        left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
        right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})

        left_fed = RecordingFederateAmbassador()
        right_fed = RecordingFederateAmbassador()
        federation_name = f"GrpcHostedCERTIOwnership-{uuid.uuid4().hex[:8]}"
        summary = run_attribute_ownership_scenario(
            left,
            right,
            config=OwnershipScenarioConfig(
                federation_name=federation_name,
                fom_modules=(smoke_fom,),
                logical_time_implementation_name="HLAinteger64Time",
                owner_name="Owner",
                acquirer_name="Acquirer",
                federate_type="OwnershipFederate",
                object_class_name="TestObjectClassR",
                attribute_name="DataR",
                object_instance_name="GrpcHostedCERTIOwnedObject-1",
            ),
            owner_federate=left_fed,
            acquirer_federate=right_fed,
        )

        assert summary["not_owned"].args == (summary["object_instance"], summary["owner_attribute"])
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["informed"].args[0] == summary["object_instance"]

        cleanup_federation(
            federation_name,
            destroyer=left,
            destroyer_resign_action=ResignAction.DELETE_OBJECTS,
            remaining_resignations=((right, ResignAction.NO_ACTION),),
            disconnect_rtis=(right, left),
        )
    finally:
        close_all(right, left, right_server, left_server)
        terminate_all(rtig)
