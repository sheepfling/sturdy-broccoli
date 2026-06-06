from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.api import FederateAmbassador
from hla2010.backends import make_rti_ambassador
from hla2010.backends.python_rti import InMemoryRTIEngine
from hla2010.backends.rest_transport import RestTransport, RestTransportConfig
from hla2010.backends.rest_transport_host import start_python_rti_rest_server
from hla2010.backends.transport import TransportRequest
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.rti import create_backend, create_rti_ambassador
from hla2010.testing import (
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_two_federate_exchange_scenario,
)
from hla2010.time import HLAfloat64Interval, HLAfloat64Time


pytestmark = pytest.mark.requires_loopback_server


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
        backend = create_backend("certi", transport={"kind": "rest", "base_url": base_url})
        rti = make_rti_ambassador(backend)

        assert rti.getHLAversion() == "HLA 1516.1-2010"
        rti.connect(FederateAmbassador(), CallbackModel.HLA_EVOKED)
        assert _RestHandler.requests[0]["command"] == "GET_HLA_VERSION"
        assert _RestHandler.requests[1]["command"] == "CONNECT"
        assert _RestHandler.requests[1]["metadata"] == {"fields": {}}
    finally:
        server.shutdown()
        server.server_close()


def test_rest_transport_can_host_python_rti_exchange_end_to_end():
    engine = InMemoryRTIEngine()
    publisher_server = start_python_rti_rest_server(engine=engine)
    subscriber_server = start_python_rti_rest_server(engine=engine)
    publisher = subscriber = None
    try:
        publisher = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": publisher_server.base_url})
        subscriber = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": subscriber_server.base_url})
        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        config = TwoFederateExchangeConfig(
            federation_name="RestHostedPythonFederation",
            fom_modules=(str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve()),),
            logical_time_implementation_name="HLAfloat64Time",
            object_class_name="TestObjectClassR",
            attribute_name="DataR",
            interaction_class_name="MsgR",
            parameter_name="MsgDataR",
            object_instance_name="RestHostedObject-1",
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
        publisher.resign_federation_execution(ResignAction.NO_ACTION)
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
    publisher_server = start_python_rti_rest_server(engine=engine)
    subscriber_server = start_python_rti_rest_server(engine=engine)
    publisher = subscriber = None
    try:
        publisher = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": publisher_server.base_url})
        subscriber = create_rti_ambassador("certi", transport={"kind": "rest", "base_url": subscriber_server.base_url})
        publisher_federate = RecordingFederateAmbassador()
        subscriber_federate = RecordingFederateAmbassador()
        publisher.connect(publisher_federate, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_federate, CallbackModel.HLA_EVOKED)

        fom = str(Path("hla2010/resources/foms/VendorSmokeFOM.xml").resolve())
        publisher.create_federation_execution("RestPollingContractFederation", [fom], "HLAfloat64Time")
        publisher.join_federation_execution("Publisher", "ProbeFederate", "RestPollingContractFederation")
        subscriber.join_federation_execution("Subscriber", "ProbeFederate", "RestPollingContractFederation")

        publisher_class = publisher.get_object_class_handle("TestObjectClassR")
        subscriber_class = subscriber.get_object_class_handle("TestObjectClassR")
        publisher_attr = publisher.get_attribute_handle(publisher_class, "DataR")
        subscriber_attr = subscriber.get_attribute_handle(subscriber_class, "DataR")
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
        publisher.resign_federation_execution(ResignAction.NO_ACTION)
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
