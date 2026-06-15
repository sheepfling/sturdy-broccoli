from __future__ import annotations

from importlib import resources
from pathlib import Path

import pytest
grpc = pytest.importorskip("grpc")

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_backend_common import BackendUnavailableError
from hla2010_rti_transport_grpc.client import GrpcTransportClientAdapter
from hla2010_rti_transport_grpc import rti_transport_pb2 as pb2
from hla2010_rti_transport_grpc import rti_transport_pb2_grpc as pb2_grpc
from hla2010_rti_transport_grpc.python_server import start_python_grpc_server
from hla2010_rti_python import InMemoryRTIEngine
from hla2010.enums import CallbackModel, OrderType, ResignAction, RestoreStatus, SaveFailureReason, SaveStatus
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_verification_harness import (
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_two_federate_exchange_scenario,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_synchronization_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time

pytestmark = pytest.mark.requires_loopback_server

RESOURCE_ROOT = Path(str(resources.files("hla2010").joinpath("resources", "foms")))
VENDOR_SMOKE_FOM = str((RESOURCE_ROOT / "VendorSmokeFOM.xml").resolve())


class _RecordingWireAdapter(GrpcTransportClientAdapter):
    def __init__(self) -> None:
        self.decode_request_calls = 0
        self.encode_response_calls = 0

    def decode_request(self, request):
        self.decode_request_calls += 1
        return super().decode_request(request)

    def encode_response(self, response):
        self.encode_response_calls += 1
        return super().encode_response(response)


def _start_grpc_pair():
    engine = InMemoryRTIEngine()
    left_server = start_python_grpc_server(engine=engine)
    right_server = start_python_grpc_server(engine=engine)
    left = create_rti_ambassador("python", transport={"kind": "grpc", "target": left_server.target})
    right = create_rti_ambassador("python", transport={"kind": "grpc", "target": right_server.target})
    return left_server, right_server, left, right


def test_grpc_transport_host_reports_loopback_unavailable(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "hla2010_rti_transport_grpc.python_server.reserve_tcp_port",
        lambda host="127.0.0.1": (_ for _ in ()).throw(BackendUnavailableError(f"Local socket bind is not permitted for {host}")),
    )

    with pytest.raises(BackendUnavailableError, match="Local socket bind is not permitted"):
        start_python_grpc_server(engine=InMemoryRTIEngine())


def test_grpc_transport_python_server_accepts_injected_wire_adapter():
    server = None
    channel = None
    wire_adapter = _RecordingWireAdapter()
    try:
        server = start_python_grpc_server(engine=InMemoryRTIEngine(), wire_adapter=wire_adapter)
        channel = grpc.insecure_channel(server.target)
        pb2_grpc.RTITransportServiceStub(channel).Request(pb2.TransportRequest(command="GET_HLA_VERSION"))

        assert wire_adapter.decode_request_calls == 1
        assert wire_adapter.encode_response_calls == 1
    finally:
        if channel is not None:
            channel.close()
        if server is not None:
            server.close()


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
        assert publisher.backend_info.kind == "python/hosted"
        assert subscriber.backend_info.kind == "python/hosted"

        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        config = TwoFederateExchangeConfig(
            federation_name=f"GrpcHostedPythonFederation-{time_factory_name}",
            fom_modules=(VENDOR_SMOKE_FOM,),
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            interaction_class_name="HLAinteractionRoot.SmokeInteraction",
            parameter_name="Message",
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

        subscriber.resignFederationExecution(ResignAction.NO_ACTION)
        publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
        publisher.destroyFederationExecution(config.federation_name)
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
            fom_modules=(VENDOR_SMOKE_FOM,),
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

        wing.resignFederationExecution(ResignAction.NO_ACTION)
        leader.resignFederationExecution(ResignAction.NO_ACTION)
        leader.destroyFederationExecution(config.federation_name)
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


def test_grpc_transport_can_host_python_rti_fm_lifecycle_end_to_end():
    leader_server = wing_server = None
    leader = wing = None
    try:
        leader_server, wing_server, leader, wing = _start_grpc_pair()
        leader_federate = RecordingFederateAmbassador()
        wing_federate = RecordingFederateAmbassador()
        federation_name = "GrpcHostedLifecycleFederation"
        fom = VENDOR_SMOKE_FOM

        leader.connect(leader_federate, CallbackModel.HLA_EVOKED)
        wing.connect(wing_federate, CallbackModel.HLA_EVOKED)
        leader.createFederationExecution(federation_name, [fom], "HLAfloat64Time")
        leader_handle = leader.joinFederationExecution("Leader", "LifecycleFederate", federation_name)
        wing_handle = wing.joinFederationExecution("Wing", "LifecycleFederate", federation_name)
        assert leader_handle is not None
        assert wing_handle is not None
        wing.resignFederationExecution(ResignAction.NO_ACTION)
        leader.resignFederationExecution(ResignAction.NO_ACTION)
        leader.destroyFederationExecution(federation_name)

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


def test_grpc_transport_can_host_python_rti_save_restore_end_to_end():
    leader_server = wing_server = None
    leader = wing = None
    try:
        leader_server, wing_server, leader, wing = _start_grpc_pair()
        leader_federate = RecordingFederateAmbassador()
        wing_federate = RecordingFederateAmbassador()
        federation_name = "GrpcHostedSaveRestoreFederation"
        save_name = "GRPC-SAVE-1"
        abort_save_name = "GRPC-SAVE-ABORT"
        fom = VENDOR_SMOKE_FOM

        leader.connect(leader_federate, CallbackModel.HLA_EVOKED)
        wing.connect(wing_federate, CallbackModel.HLA_EVOKED)
        leader.createFederationExecution(federation_name, [fom], "HLAfloat64Time")
        leader.joinFederationExecution("Leader", "SaveRestoreFederate", federation_name)
        wing.joinFederationExecution("Wing", "SaveRestoreFederate", federation_name)

        leader.requestFederationSave(save_name)
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        assert leader_federate.last_callback("initiateFederateSave").args == (save_name,)
        assert wing_federate.last_callback("initiateFederateSave").args == (save_name,)

        leader.federateSaveBegun()
        wing.federateSaveBegun()
        leader.federateSaveComplete()
        wing.federateSaveComplete()
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        assert leader_federate.last_callback("federationSaved") is not None

        leader.queryFederationSaveStatus()
        for _ in range(6):
            leader.evokeMultipleCallbacks(0.0, 0.0)
        save_status = leader_federate.last_callback("federationSaveStatusResponse").args[0]
        assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in save_status)

        leader.requestFederationRestore(save_name)
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        assert leader_federate.last_callback("requestFederationRestoreSucceeded").args == (save_name,)
        assert wing_federate.last_callback("initiateFederateRestore") is not None
        assert leader_federate.last_callback("federationRestoreBegun") is not None

        leader.federateRestoreComplete()
        wing.federateRestoreComplete()
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        assert leader_federate.last_callback("federationRestored") is not None

        leader.queryFederationRestoreStatus()
        for _ in range(6):
            leader.evokeMultipleCallbacks(0.0, 0.0)
        restore_status = leader_federate.last_callback("federationRestoreStatusResponse").args[0]
        assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in restore_status)

        leader.requestFederationSave(abort_save_name)
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        leader.federateSaveBegun()
        wing.federateSaveBegun()
        leader.abortFederationSave()
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        assert leader_federate.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)

        leader.requestFederationRestore(abort_save_name)
        for _ in range(12):
            leader.evokeMultipleCallbacks(0.0, 0.0)
            wing.evokeMultipleCallbacks(0.0, 0.0)
        assert leader_federate.last_callback("requestFederationRestoreFailed").args == (abort_save_name,)

        wing.resignFederationExecution(ResignAction.NO_ACTION)
        leader.resignFederationExecution(ResignAction.NO_ACTION)
        leader.destroyFederationExecution(federation_name)
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
            fom_modules=(VENDOR_SMOKE_FOM,),
            logical_time_implementation_name="HLAfloat64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
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

        acquirer.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
        owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
        owner.destroyFederationExecution(config.federation_name)
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
            fom_modules=(VENDOR_SMOKE_FOM,),
            logical_time_implementation_name="HLAfloat64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="NegotiatedOwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
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

        acquirer.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
        owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
        owner.destroyFederationExecution(config.federation_name)
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

        fom = VENDOR_SMOKE_FOM
        publisher.createFederationExecution("GrpcPollingContractFederation", [fom], "HLAfloat64Time")
        publisher.joinFederationExecution("Publisher", "ProbeFederate", "GrpcPollingContractFederation")
        subscriber.joinFederationExecution("Subscriber", "ProbeFederate", "GrpcPollingContractFederation")

        publisher_class = publisher.getObjectClassHandle("HLAobjectRoot.SmokeObject")
        subscriber_class = subscriber.getObjectClassHandle("HLAobjectRoot.SmokeObject")
        publisher_attr = publisher.getAttributeHandle(publisher_class, "Payload")
        subscriber_attr = subscriber.getAttributeHandle(subscriber_class, "Payload")
        publisher.publishObjectClassAttributes(publisher_class, {publisher_attr})
        subscriber.subscribeObjectClassAttributes(subscriber_class, {subscriber_attr})

        obj = publisher.registerObjectInstance(publisher_class, "BufferedObject-1")
        publisher.updateAttributeValues(obj, {publisher_attr: b"buffered"}, b"tag")

        assert subscriber.evokeMultipleCallbacks(0.0, 0.05) is True
        first = subscriber_federate.last_callback()
        assert first is not None
        assert first.method_name == "discoverObjectInstance"

        assert subscriber.evokeCallback(0.0) is True
        second = subscriber_federate.last_callback()
        assert second is not None
        assert second.method_name == "reflectAttributeValues"
        assert second.args[1] == {subscriber_attr: b"buffered"}

        subscriber.resignFederationExecution(ResignAction.NO_ACTION)
        publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
        publisher.destroyFederationExecution("GrpcPollingContractFederation")
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
