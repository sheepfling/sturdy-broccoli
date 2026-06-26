from __future__ import annotations

import json
from importlib import resources
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import uuid

import pytest

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e import NullFederateAmbassador
from hla.backends.common import make_rti_ambassador
from hla.backends.python1516e import InMemoryRTIEngine
from hla.transports.common.transport import TransportRequest
from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction, RestoreStatus, SaveFailureReason, SaveStatus
from hla.rti import create_backend
from hla.runtime.factory import create_rti_ambassador
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_2025_rti_ambassador
from hla.verification import (
    FederationLifecycleScenarioConfig,
    JoinScenarioConfig,
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    ResignScenarioConfig,
    SynchronizationScenarioConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_two_federate_exchange_scenario,
    run_attribute_ownership_scenario,
    run_federation_lifecycle_negative_scenario,
    run_join_precondition_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_resign_precondition_scenario,
    run_synchronization_scenario,
)
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador as NullFederateAmbassador2025
from hla.transports.rest import RestTransport, RestTransportConfig
from hla.transports.rest.rest_transport_host import start_2025_rest_server, start_python_rest_server

pytestmark = pytest.mark.requires_loopback_server

RESOURCE_ROOT = Path(str(resources.files("hla.fom").joinpath("resources", "foms")))
VENDOR_SMOKE_FOM = str((RESOURCE_ROOT / "VendorSmokeFOM.xml").resolve())


class _RestHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []

    def do_POST(self):  # noqa: N802 - HTTP handler naming
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(payload)
        self.requests.append(data)

        command = data.get("command")
        if command == "GET_HLA_VERSION":
            response = {"fields": ["HLA 1516.1-2010"], "metadata": {"fields": {"kind": "rest"}}}
        elif command == "CONNECT":
            response = {"fields": []}
        else:
            response = {"error": {"code": "RTIinternalError", "message": f"Unknown command: {command}"}}

        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args, **_kwargs):  # pragma: no cover - keep test output quiet
        return None


def _start_stub_server() -> tuple[ThreadingHTTPServer, str]:
    _RestHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _RestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


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


def test_rest_transport_round_trips_typed_envelopes():
    server, base_url = _start_stub_server()
    try:
        transport = RestTransport(RestTransportConfig(base_url=base_url)).start()
        response = transport.request(TransportRequest(command="GET_HLA_VERSION", fields=("ignored",)))

        assert response.fields == ("HLA 1516.1-2010",)
        assert response.metadata == {"kind": "rest"}
        assert _RestHandler.requests[0]["command"] == "GET_HLA_VERSION"
        assert _RestHandler.requests[0]["metadata"] == {"fields": {}}

        direct = transport.request(TransportRequest(command="CONNECT", fields=(CallbackModel.HLA_EVOKED.name, "")))
        assert direct.fields == ()
    finally:
        server.shutdown()
        server.server_close()


def test_rest_transport_registers_with_backend_factory():
    server, base_url = _start_stub_server()
    try:
        backend = create_backend("certi", spec="rti1516e", transport={"kind": "rest", "base_url": base_url})
        rti = make_rti_ambassador(backend)

        assert rti.getHLAversion() == "HLA 1516.1-2010"
        rti.connect(NullFederateAmbassador(), CallbackModel.HLA_EVOKED)
        assert _RestHandler.requests[0]["command"] == "GET_HLA_VERSION"
        assert _RestHandler.requests[1]["command"] == "CONNECT"
        assert _RestHandler.requests[1]["metadata"] == {"fields": {}}
    finally:
        server.shutdown()
        server.server_close()


def test_rest_transport_registers_with_2025_backend_factory():
    server = start_2025_rest_server()
    try:
        rti = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": server.base_url})

        assert rti._transport.__class__.__name__ == "RestTransport"
        assert rti._transport.config.base_url == server.base_url
        rti.connect(NullFederateAmbassador2025(), CallbackModel.HLA_EVOKED)
        rti.disconnect()
    finally:
        server.close()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-BND-003")
def test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario():
    from hla.fom.proto2025 import scenario_fom_paths

    leader_server = start_2025_rest_server()
    wing_server = start_2025_rest_server()
    leader = None
    wing = None
    federation_name = f"rest-2025-shared-lifecycle-negative-{uuid.uuid4().hex[:8]}"
    try:
        leader = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": leader_server.base_url})
        wing = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": wing_server.base_url})
        config = FederationLifecycleScenarioConfig(
            federation_name=federation_name,
            fom_modules=tuple(scenario_fom_paths("message-test")),
            logical_time_implementation_name="HLAinteger64Time",
        )

        summary = run_federation_lifecycle_negative_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert summary["federation_name"] == config.federation_name
        assert summary["leader_handle"] is not None
        assert summary["wing_handle"] is not None
        assert type(summary["already_connected"]).__name__ == "AlreadyConnected"
        assert type(summary["duplicate_create"]).__name__ == "FederationExecutionAlreadyExists"
        assert type(summary["disconnect_while_joined"]).__name__ == "FederateIsExecutionMember"
        assert type(summary["destroy_with_joined"]).__name__ == "FederatesCurrentlyJoined"
        assert type(summary["destroy_missing"]).__name__ == "FederationExecutionDoesNotExist"
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        wing_server.close()
        leader_server.close()


@pytest.mark.requirements(
    "HLA2025-FR-001",
    "HLA2025-FI-001",
    "HLA2025-FI-002",
    "HLA2025-FI-SVC-004",
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-006",
    "HLA2025-FI-SVC-007",
    "HLA2025-BND-003",
)
def test_2025_rest_transport_server_runs_shared_join_precondition_scenario():
    from hla.fom.proto2025 import scenario_fom_paths

    leader_server = start_2025_rest_server()
    wing_server = start_2025_rest_server()
    late_server = start_2025_rest_server()
    leader = None
    wing = None
    late = None
    federation_name = f"rest-2025-shared-join-preconditions-{uuid.uuid4().hex[:8]}"
    try:
        leader = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": leader_server.base_url})
        wing = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": wing_server.base_url})
        late = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": late_server.base_url})
        config = JoinScenarioConfig(
            federation_name=federation_name,
            fom_modules=tuple(scenario_fom_paths("message-test")),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            late_name="Late",
            federate_type="JoinFederate",
            save_name=f"JOIN-BLOCK-{uuid.uuid4().hex[:8]}",
        )

        summary = run_join_precondition_scenario(
            leader,
            wing,
            late,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
            late_federate=RecordingFederateAmbassador(),
        )

        assert type(summary["not_connected"]).__name__ == "NotConnected"
        assert type(summary["missing_federation"]).__name__ == "FederationExecutionDoesNotExist"
        assert type(summary["duplicate_name"]).__name__ == "FederateNameAlreadyInUse"
        assert type(summary["already_joined"]).__name__ == "FederateAlreadyExecutionMember"
        assert type(summary["save_in_progress"]).__name__ == "SaveInProgress"
        assert type(summary["restore_in_progress"]).__name__ == "RestoreInProgress"
    finally:
        if late is not None:
            late.close()
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        late_server.close()
        wing_server.close()
        leader_server.close()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-BND-003")
def test_2025_rest_transport_server_runs_shared_resign_precondition_scenario():
    leader_server = start_2025_rest_server()
    wing_server = start_2025_rest_server()
    leader = None
    wing = None
    federation_name = f"rest-2025-shared-resign-preconditions-{uuid.uuid4().hex[:8]}"
    try:
        leader = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": leader_server.base_url})
        wing = create_2025_rti_ambassador(transport={"kind": "rest", "base_url": wing_server.base_url})
        config = ResignScenarioConfig(
            federation_name=federation_name,
            fom_modules=("resource:VendorSmokeFOM.xml",),
            logical_time_implementation_name="HLAinteger64Time",
            leader_name="Leader",
            wing_name="Wing",
            federate_type="ResignFederate",
        )

        summary = run_resign_precondition_scenario(
            leader,
            wing,
            config=config,
            leader_federate=RecordingFederateAmbassador(),
            wing_federate=RecordingFederateAmbassador(),
        )

        assert type(summary["not_connected"]).__name__ == "NotConnected"
        assert type(summary["not_joined"]).__name__ == "FederateNotExecutionMember"
        assert type(summary["invalid_action"]).__name__ == "InvalidResignAction"
        assert type(summary["owns_attributes"]).__name__ == "FederateOwnsAttributes"
        assert type(summary["acquisition_pending"]).__name__ == "OwnershipAcquisitionPending"
        assert summary["object_instance"] is not None
        assert summary["attribute"] is not None
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        wing_server.close()
        leader_server.close()


@pytest.mark.parametrize("time_factory_name", ["HLAinteger64Time", "HLAfloat64Time"])
def test_rest_transport_can_host_python_rti_exchange_end_to_end(time_factory_name: str):
    engine = InMemoryRTIEngine()
    publisher_server = start_python_rest_server(engine=engine)
    subscriber_server = start_python_rest_server(engine=engine)
    publisher = subscriber = None
    try:
        publisher = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": publisher_server.base_url})
        subscriber = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": subscriber_server.base_url})
        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        config = TwoFederateExchangeConfig(
            federation_name=f"RestHostedPythonFederation-{time_factory_name}",
            fom_modules=(VENDOR_SMOKE_FOM,),
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            interaction_class_name="HLAinteractionRoot.SmokeInteraction",
            parameter_name="Message",
            object_instance_name=f"RestHostedObject-{time_factory_name}-1",
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
        subscriber_server.close()
        publisher_server.close()


def test_rest_transport_polling_contract_drains_buffered_callbacks():
    engine = InMemoryRTIEngine()
    publisher_server = start_python_rest_server(engine=engine)
    subscriber_server = start_python_rest_server(engine=engine)
    publisher = subscriber = None
    try:
        publisher = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": publisher_server.base_url})
        subscriber = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": subscriber_server.base_url})
        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        publisher.connect(publisher_federate, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_federate, CallbackModel.HLA_EVOKED)

        fom = VENDOR_SMOKE_FOM
        publisher.create_federation_execution("RestPollingContractFederation", [fom], "HLAfloat64Time")
        publisher.join_federation_execution("Publisher", "ProbeFederate", "RestPollingContractFederation")
        subscriber.join_federation_execution("Subscriber", "ProbeFederate", "RestPollingContractFederation")

        publisher_class = publisher.get_object_class_handle("HLAobjectRoot.SmokeObject")
        subscriber_class = subscriber.get_object_class_handle("HLAobjectRoot.SmokeObject")
        publisher_attr = publisher.get_attribute_handle(publisher_class, "Payload")
        subscriber_attr = subscriber.get_attribute_handle(subscriber_class, "Payload")
        publisher.publish_object_class_attributes(publisher_class, {publisher_attr})
        subscriber.subscribe_object_class_attributes(subscriber_class, {subscriber_attr})

        obj = publisher.register_object_instance(publisher_class, "BufferedRestObject-1")
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
        publisher.destroy_federation_execution("RestPollingContractFederation")
        subscriber.disconnect()
        publisher.disconnect()
    finally:
        if subscriber is not None:
            subscriber.close()
        if publisher is not None:
            publisher.close()
        subscriber_server.close()
        publisher_server.close()


def test_rest_transport_can_host_python_rti_synchronization_end_to_end():
    engine = InMemoryRTIEngine()
    leader_server = start_python_rest_server(engine=engine)
    wing_server = start_python_rest_server(engine=engine)
    leader = wing = None
    try:
        leader = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": leader_server.base_url})
        wing = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": wing_server.base_url})
        leader_federate = RecordingFederateAmbassador()
        wing_federate = RecordingFederateAmbassador()
        config = SynchronizationScenarioConfig(
            federation_name="RestHostedSyncFederation",
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
        wing_server.close()
        leader_server.close()


def test_rest_transport_can_host_python_rti_fm_lifecycle_end_to_end():
    engine = InMemoryRTIEngine()
    leader_server = start_python_rest_server(engine=engine)
    wing_server = start_python_rest_server(engine=engine)
    leader = wing = None
    try:
        leader = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": leader_server.base_url})
        wing = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": wing_server.base_url})
        leader_federate = RecordingFederateAmbassador()
        wing_federate = RecordingFederateAmbassador()
        federation_name = "RestHostedLifecycleFederation"
        fom = VENDOR_SMOKE_FOM

        leader.connect(leader_federate, CallbackModel.HLA_EVOKED)
        wing.connect(wing_federate, CallbackModel.HLA_EVOKED)
        leader.create_federation_execution(federation_name, [fom], "HLAfloat64Time")
        leader_handle = leader.join_federation_execution("Leader", "LifecycleFederate", federation_name)
        wing_handle = wing.join_federation_execution("Wing", "LifecycleFederate", federation_name)
        assert leader_handle is not None
        assert wing_handle is not None
        wing.resign_federation_execution(ResignAction.NO_ACTION)
        leader.resign_federation_execution(ResignAction.NO_ACTION)
        leader.destroy_federation_execution(federation_name)

        wing.disconnect()
        leader.disconnect()
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        wing_server.close()
        leader_server.close()


def test_rest_transport_can_host_python_rti_save_restore_end_to_end():
    engine = InMemoryRTIEngine()
    leader_server = start_python_rest_server(engine=engine)
    wing_server = start_python_rest_server(engine=engine)
    leader = wing = None
    try:
        leader = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": leader_server.base_url})
        wing = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": wing_server.base_url})
        leader_federate = RecordingFederateAmbassador()
        wing_federate = RecordingFederateAmbassador()
        federation_name = "RestHostedSaveRestoreFederation"
        save_name = "REST-SAVE-1"
        abort_save_name = "REST-SAVE-ABORT"
        fom = VENDOR_SMOKE_FOM

        leader.connect(leader_federate, CallbackModel.HLA_EVOKED)
        wing.connect(wing_federate, CallbackModel.HLA_EVOKED)
        leader.create_federation_execution(federation_name, [fom], "HLAfloat64Time")
        leader.join_federation_execution("Leader", "SaveRestoreFederate", federation_name)
        wing.join_federation_execution("Wing", "SaveRestoreFederate", federation_name)

        leader.request_federation_save(save_name)
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        assert leader_federate.last_callback("initiateFederateSave").args == (save_name,)
        assert wing_federate.last_callback("initiateFederateSave").args == (save_name,)

        leader.federate_save_begun()
        wing.federate_save_begun()
        leader.federate_save_complete()
        wing.federate_save_complete()
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        assert leader_federate.last_callback("federationSaved") is not None

        leader.query_federation_save_status()
        for _ in range(6):
            leader.evoke_multiple_callbacks(0.0, 0.0)
        save_status = leader_federate.last_callback("federationSaveStatusResponse").args[0]
        assert all(pair.save_status is SaveStatus.NO_SAVE_IN_PROGRESS for pair in save_status)

        leader.request_federation_restore(save_name)
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        assert leader_federate.last_callback("requestFederationRestoreSucceeded").args == (save_name,)
        assert wing_federate.last_callback("initiateFederateRestore") is not None
        assert leader_federate.last_callback("federationRestoreBegun") is not None

        leader.federate_restore_complete()
        wing.federate_restore_complete()
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        assert leader_federate.last_callback("federationRestored") is not None

        leader.query_federation_restore_status()
        for _ in range(6):
            leader.evoke_multiple_callbacks(0.0, 0.0)
        restore_status = leader_federate.last_callback("federationRestoreStatusResponse").args[0]
        assert all(pair.restore_status is RestoreStatus.NO_RESTORE_IN_PROGRESS for pair in restore_status)

        leader.request_federation_save(abort_save_name)
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        leader.federate_save_begun()
        wing.federate_save_begun()
        leader.abort_federation_save()
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        assert leader_federate.last_callback("federationNotSaved").args == (SaveFailureReason.SAVE_ABORTED,)

        leader.request_federation_restore(abort_save_name)
        for _ in range(12):
            leader.evoke_multiple_callbacks(0.0, 0.0)
            wing.evoke_multiple_callbacks(0.0, 0.0)
        assert leader_federate.last_callback("requestFederationRestoreFailed").args == (abort_save_name,)

        wing.resign_federation_execution(ResignAction.NO_ACTION)
        leader.resign_federation_execution(ResignAction.NO_ACTION)
        leader.destroy_federation_execution(federation_name)
        wing.disconnect()
        leader.disconnect()
    finally:
        if wing is not None:
            wing.close()
        if leader is not None:
            leader.close()
        wing_server.close()
        leader_server.close()


def test_rest_transport_can_host_python_rti_ownership_end_to_end():
    engine = InMemoryRTIEngine()
    owner_server = start_python_rest_server(engine=engine)
    acquirer_server = start_python_rest_server(engine=engine)
    owner = acquirer = None
    try:
        owner = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": owner_server.base_url})
        acquirer = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": acquirer_server.base_url})
        owner_federate = RecordingFederateAmbassador()
        acquirer_federate = RecordingFederateAmbassador()
        config = OwnershipScenarioConfig(
            federation_name="RestHostedOwnershipFederation",
            fom_modules=(VENDOR_SMOKE_FOM,),
            logical_time_implementation_name="HLAfloat64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="OwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name="RestOwnedObject-1",
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
        acquirer_server.close()
        owner_server.close()


def test_rest_transport_can_host_python_rti_negotiated_ownership_end_to_end():
    engine = InMemoryRTIEngine()
    owner_server = start_python_rest_server(engine=engine)
    acquirer_server = start_python_rest_server(engine=engine)
    owner = acquirer = None
    try:
        owner = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": owner_server.base_url})
        acquirer = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": acquirer_server.base_url})
        owner_federate = RecordingFederateAmbassador()
        acquirer_federate = RecordingFederateAmbassador()
        config = NegotiatedOwnershipScenarioConfig(
            federation_name="RestHostedNegotiatedOwnershipFederation",
            fom_modules=(VENDOR_SMOKE_FOM,),
            logical_time_implementation_name="HLAfloat64Time",
            owner_name="Owner",
            acquirer_name="Acquirer",
            federate_type="NegotiatedOwnershipFederate",
            object_class_name="HLAobjectRoot.SmokeObject",
            attribute_name="Payload",
            object_instance_name="RestNegotiatedOwnedObject-1",
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
        acquirer_server.close()
        owner_server.close()
