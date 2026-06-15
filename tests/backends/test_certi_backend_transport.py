from __future__ import annotations

from hla2010.spec import FederateAmbassadorSpec
from hla2010.exceptions import FederationExecutionDoesNotExist, RTIinternalError
from hla2010_rti_backend_common import make_rti_ambassador
from hla2010_rti_certi import CERTIBackend, CERTIConfig
from hla2010_rti_certi.certi.service_adapter import CERTIBackend as PackageCERTIBackend
from hla2010_rti_certi.certi.transport import CERTITransport, CERTITransportProtocol
from hla2010_rti_transport_common.transport import RTITransport, TransportError, TransportRequest, TransportResponse
from hla2010.enums import CallbackModel
from hla2010_rti_runtime_common import RTITransportSpec, create_backend, register_transport_factory
import pytest


class FakeTransport(RTITransport):
    def __init__(self, responses: dict[str, list[str]]):
        self.responses = responses
        self.requests: list[tuple[str, tuple[object, ...]]] = []
        self.started = False
        self.closed = False

    def start(self) -> FakeTransport:
        self.started = True
        return self

    def request(self, request: TransportRequest):
        self.requests.append((request.command, request.fields))
        return TransportResponse(fields=tuple(self.responses.get(request.command, [])))

    def close(self) -> None:
        self.closed = True


class ErrorTransport(RTITransport):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def start(self) -> ErrorTransport:
        return self

    def request(self, request: TransportRequest):
        raise TransportError(self.code, self.message)


def test_certi_backend_can_run_against_an_injected_transport():
    transport = FakeTransport({"GET_HLA_VERSION": ["HLA 1516.1-2010"]})
    backend = CERTIBackend(CERTIConfig(transport=transport))
    rti = make_rti_ambassador(backend)

    assert backend.start() is backend
    assert transport.started is True
    assert rti.get_hla_version() == "HLA 1516.1-2010"

    rti.connect(FederateAmbassadorSpec(), CallbackModel.HLA_EVOKED)
    assert transport.requests[0][0] == "GET_HLA_VERSION"
    assert transport.requests[1][0] == "CONNECT"
    assert transport.requests[1][1] == (CallbackModel.HLA_EVOKED.name, "")

    backend.close()
    assert transport.closed is True


def test_certi_package_split_is_explicit():
    assert PackageCERTIBackend is CERTIBackend
    assert issubclass(CERTITransport, CERTITransportProtocol)


def test_backend_factory_accepts_transport_specs_transparently():
    transport = FakeTransport({"GET_HLA_VERSION": ["HLA 1516.1-2010"]})
    backend = create_backend("certi", transport=transport)
    assert backend.config.transport is transport

    spec = RTITransportSpec(kind="subprocess-line", options={"command": ["/bin/echo"]})
    assert spec.kind == "subprocess-line"


def test_transport_request_and_response_are_typed_envelopes():
    request = TransportRequest(command="PING", fields=("alpha", 3))
    response = TransportResponse(fields=("PONG",))

    assert request.command == "PING"
    assert request.fields == ("alpha", 3)
    assert response.fields == ("PONG",)


def test_transport_registry_can_route_future_wire_kinds():
    transport = FakeTransport({"GET_HLA_VERSION": ["HLA 1516.1-2010"]})
    register_transport_factory("test-grpc-wire", lambda spec: transport)

    backend = create_backend("certi", transport={"kind": "test-grpc-wire"})
    assert backend.config.transport is transport


def test_certi_transport_errors_map_to_explicit_hla_exception_types():
    backend = CERTIBackend(CERTIConfig(transport=ErrorTransport("FederationExecutionDoesNotExist", "missing")))

    with pytest.raises(FederationExecutionDoesNotExist, match="missing"):
        backend.start().helper_request("DESTROY", "missing")


def test_certi_transport_errors_fall_back_to_internal_error_for_unknown_codes():
    backend = CERTIBackend(CERTIConfig(transport=ErrorTransport("UnknownWireError", "bad-wire")))

    with pytest.raises(RTIinternalError, match="bad-wire"):
        backend.start().helper_request("DESTROY", "missing")
