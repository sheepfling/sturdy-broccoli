from __future__ import annotations

from pathlib import Path

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.grpc_transport.python_server import start_python_grpc_server
from hla2010.backends.python import InMemoryRTIEngine
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.rti import create_rti_ambassador
from hla2010.testing.scenarios import (
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_synchronization_scenario,
    run_two_federate_exchange_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time

pytestmark = pytest.mark.requires_loopback_server


def _start_grpc_pair():
    engine = InMemoryRTIEngine()
    left_server = start_python_grpc_server(engine=engine)
    right_server = start_python_grpc_server(engine=engine)
    left = create_rti_ambassador("certi", transport={"kind": "grpc", "target": left_server.target})
    right = create_rti_ambassador("certi", transport={"kind": "grpc", "target": right_server.target})
    return left_server, right_server, left, right


def _exchange_time_profile(time_factory_name: str) -> dict[str, object]:
    if time_factory_name == "HLAinteger64Time":
        return {
            "logical_time_implementation_name": "HLAinteger64Time",
            "lookahead": HLAinteger64Interval(1),
            "advance_time": HLAinteger64Time(8),
            "timestamped_attribute_time": HLAinteger64Time(5),
            "timestamped_interaction_time": HLAinteger64Time(6),
        }
    if time_factory_name == "HLAfloat64Time":
        return {
            "logical_time_implementation_name": "HLAfloat64Time",
            "lookahead": HLAfloat64Interval(1.0),
            "advance_time": HLAfloat64Time(8.0),
            "timestamped_attribute_time": HLAfloat64Time(5.0),
            "timestamped_interaction_time": HLAfloat64Time(6.0),
        }
    raise AssertionError(f"unexpected time factory {time_factory_name}")


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_grpc_transport_can_host_python_rti_exchange_end_to_end(time_factory_name: str):
    publisher_server = subscriber_server = None
    publisher = subscriber = None
    try:
        publisher_server, subscriber_server, publisher, subscriber = _start_grpc_pair()

        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        config = TwoFederateExchangeConfig(
            federation_name=f"GrpcHostedPythonFederation-{time_factory_name}",
            fom_modules=(str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve()),),
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            interaction_class_name="MsgR",
            parameter_name="MsgDataR",
            object_instance_name=f"GrpcHostedObject-{time_factory_name}-1",
            attribute_payload=b"payload-r",
            attribute_tag=b"reflect-tag",
            interaction_payload=b"hello-r",
            interaction_tag=b"interaction-tag",
            enable_time_management=True,
            timestamped_attribute_payload=b"payload-tso",
            timestamped_attribute_tag=b"reflect-tso",
            timestamped_interaction_payload=b"hello-tso",
            timestamped_interaction_tag=b"interaction-tso",
            **_exchange_time_profile(time_factory_name),
        )

        summary = run_two_federate_exchange_scenario(
            publisher,
            subscriber,
            config=config,
            publisher_federate=publisher_federate,
            subscriber_federate=subscriber_federate,
        )
        history = assert_two_federate_exchange_callback_history(
            summary,
            publisher_federate=publisher_federate,
            subscriber_federate=subscriber_federate,
            config=config,
        )

        assert history["receive_reflect"].args[3] is OrderType.RECEIVE
        assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

        subscriber.resign_federation_execution(ResignAction.NO_ACTION)
        publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        publisher.destroy_federation_execution(config.federation_name)
        subscriber.disconnect()
        publisher.disconnect()
    finally:
        if subscriber is not None:
            subscriber.close()
        if publisher is not None:
            publisher.close()
        if subscriber_server is not None:
            subscriber_server.close()
        if publisher_server is not None:
            publisher_server.close()


def test_grpc_transport_can_host_python_rti_synchronization_end_to_end():
    leader_server = wing_server = None
    leader = wing = None
    try:
        leader_server, wing_server, leader, wing = _start_grpc_pair()
        leader_federate = RecordingFederateAmbassador()
        wing_federate = RecordingFederateAmbassador()
        config = SynchronizationScenarioConfig(
            federation_name="GrpcHostedSyncFederation",
            fom_modules=(str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve()),),
            logical_time_implementation_name="HLAfloat64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="SyncFederate",
            label="ReadyToRun",
            tag=b"startup",
        )
        summary = run_synchronization_scenario(
            leader,
            wing,
            config=config,
            leader_federate=leader_federate,
            wing_federate=wing_federate,
        )
        assert summary["leader_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["wing_announce"].args[:2] == ("ReadyToRun", b"startup")
        assert summary["leader_sync"].args[0] == "ReadyToRun"
        assert summary["wing_sync"].args[0] == "ReadyToRun"

        wing.resign_federation_execution(ResignAction.NO_ACTION)
        leader.resign_federation_execution(ResignAction.NO_ACTION)
        leader.destroy_federation_execution(config.federation_name)
        wing.disconnect()
        leader.disconnect()
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        if wing_server is not None:
            wing_server.close()
        if leader_server is not None:
            leader_server.close()


def test_grpc_transport_can_host_python_rti_ownership_end_to_end():
    owner_server = acquirer_server = None
    owner = acquirer = None
    try:
        owner_server, acquirer_server, owner, acquirer = _start_grpc_pair()
        owner_federate = RecordingFederateAmbassador()
        acquirer_federate = RecordingFederateAmbassador()
        config = OwnershipScenarioConfig(
            federation_name="GrpcHostedOwnershipFederation",
            fom_modules=(str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve()),),
            logical_time_implementation_name="HLAfloat64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            object_instance_name="GrpcOwnedObject-1",
        )
        summary = run_attribute_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_federate,
            acquirer_federate=acquirer_federate,
        )
        assert summary["not_owned"].args == (summary["object_instance"], summary["owner_attribute"])
        assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
        assert summary["informed"].args[0] == summary["object_instance"]

        acquirer.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
        owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        owner.destroy_federation_execution(config.federation_name)
        acquirer.disconnect()
        owner.disconnect()
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        if acquirer_server is not None:
            acquirer_server.close()
        if owner_server is not None:
            owner_server.close()


def test_grpc_transport_can_host_python_rti_negotiated_ownership_end_to_end():
    owner_server = acquirer_server = None
    owner = acquirer = None
    try:
        owner_server, acquirer_server, owner, acquirer = _start_grpc_pair()
        owner_federate = RecordingFederateAmbassador()
        acquirer_federate = RecordingFederateAmbassador()
        config = NegotiatedOwnershipScenarioConfig(
            federation_name="GrpcHostedNegotiatedOwnershipFederation",
            fom_modules=(str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve()),),
            logical_time_implementation_name="HLAfloat64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="NegotiatedOwnershipFederate",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            object_instance_name="GrpcNegotiatedOwnedObject-1",
        )
        summary = run_negotiated_attribute_ownership_scenario(
            owner,
            acquirer,
            config=config,
            owner_federate=owner_federate,
            acquirer_federate=acquirer_federate,
        )
        assert summary["release"].args[0] == summary["release_object_instance"]
        assert summary["cancellation"].args[0] == summary["release_acquirer_object_instance"]
        assert summary["divested"] == {summary["owner_attribute"]}
        assert summary["acquired"].args[0] == summary["release_acquirer_object_instance"]
        if summary["assumption"] is not None:
            assert summary["offered_acquired"] is not None
            assert summary["divestiture_confirmation"] is not None

        acquirer.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
        owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        owner.destroy_federation_execution(config.federation_name)
        acquirer.disconnect()
        owner.disconnect()
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        if acquirer_server is not None:
            acquirer_server.close()
        if owner_server is not None:
            owner_server.close()


def test_grpc_transport_polling_contract_drains_buffered_callbacks():
    publisher_server = subscriber_server = None
    publisher = subscriber = None
    try:
        publisher_server, subscriber_server, publisher, subscriber = _start_grpc_pair()
        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        publisher.connect(publisher_federate, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_federate, CallbackModel.HLA_EVOKED)

        fom = str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve())
        publisher.create_federation_execution("GrpcPollingContractFederation", [fom], "HLAfloat64Time")
        publisher.join_federation_execution("Publisher", "ProbeFederate", "GrpcPollingContractFederation")
        subscriber.join_federation_execution("Subscriber", "ProbeFederate", "GrpcPollingContractFederation")

        publisher_class = publisher.get_object_class_handle("TestObjectClassR")
        subscriber_class = subscriber.get_object_class_handle("TestObjectClassR")
        publisher_attr = publisher.get_attribute_handle(publisher_class, "DataR")
        subscriber_attr = subscriber.get_attribute_handle(subscriber_class, "DataR")
        publisher.publish_object_class_attributes(publisher_class, {publisher_attr})
        subscriber.subscribe_object_class_attributes(subscriber_class, {subscriber_attr})

        obj = publisher.register_object_instance(publisher_class, "BufferedObject-1")
        publisher.update_attribute_values(obj, {publisher_attr: b"buffered"}, b"tag")

        assert subscriber.evoke_multiple_callbacks(0.0, 0.05) is True
        first = subscriber_federate.last_callback()
        assert first is not None
        assert first.method_name == "discoverObjectInstance"

        assert subscriber.evoke_callback(0.0) is True
        second = subscriber_federate.last_callback()
        assert second is not None
        assert second.method_name == "reflectAttributeValues"
        assert second.args[1] == {subscriber_attr: b"buffered"}

        subscriber.resign_federation_execution(ResignAction.NO_ACTION)
        publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        publisher.destroy_federation_execution("GrpcPollingContractFederation")
        subscriber.disconnect()
        publisher.disconnect()
    finally:
        if subscriber is not None:
            subscriber.close()
        if publisher is not None:
            publisher.close()
        if subscriber_server is not None:
            subscriber_server.close()
        if publisher_server is not None:
            publisher_server.close()
