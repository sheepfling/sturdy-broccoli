from __future__ import annotations

import os
import uuid

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.base import BackendUnavailableError
from hla2010.backends.grpc_transport import start_certi_grpc_server
from hla2010.enums import OrderType, ResignAction
from hla2010.real_rti import discover_certi_smoke_fom, launch_certi_rtig
from hla2010.rti import create_rti_ambassador
from hla2010.testing import (
    OwnershipScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_attribute_ownership_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time


pytestmark = pytest.mark.requires_loopback_server


def _require_real_rti_smoke() -> None:
    if os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
        pytest.skip("real vendor RTI smoke disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1")


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
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=60901)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=60911)
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

        right.resign_federation_execution(ResignAction.NO_ACTION)
        left.resign_federation_execution(ResignAction.NO_ACTION)
        left.destroy_federation_execution(federation_name)
        right.disconnect()
        left.disconnect()
    finally:
        if right is not None:
            right.close()
        if left is not None:
            left.close()
        if right_server is not None:
            right_server.close()
        if left_server is not None:
            left_server.close()
        rtig.terminate()


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
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=61001)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=61011)
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

        right.resign_federation_execution(ResignAction.NO_ACTION)
        left.resign_federation_execution(ResignAction.NO_ACTION)
        left.destroy_federation_execution(federation_name)
        right.disconnect()
        left.disconnect()
    finally:
        if right is not None:
            right.close()
        if left is not None:
            left.close()
        if right_server is not None:
            right_server.close()
        if left_server is not None:
            left_server.close()
        rtig.terminate()


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
        left_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=61101)
        right_server = start_certi_grpc_server(launch_rtig=False, tcp_port=rtig.tcp_port, udp_port=61111)
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

        right.resign_federation_execution(ResignAction.NO_ACTION)
        left.resign_federation_execution(ResignAction.NO_ACTION)
        left.destroy_federation_execution(federation_name)
        right.disconnect()
        left.disconnect()
    finally:
        if right is not None:
            right.close()
        if left is not None:
            left.close()
        if right_server is not None:
            right_server.close()
        if left_server is not None:
            left_server.close()
        rtig.terminate()
