from __future__ import annotations

from concurrent import futures

import grpc
import pytest

from hla2010.runtime_api import FederateAmbassador
from hla2010.backends.base import make_rti_ambassador
from hla2010.backends.grpc_transport import GrpcTransport, GrpcTransportConfig
from hla2010.backends.grpc_transport import rti_transport_pb2 as pb2
from hla2010.backends.grpc_transport import rti_transport_pb2_grpc as pb2_grpc
from hla2010.backends.transport import TransportRequest
from hla2010.enums import CallbackModel
from hla2010.rti import create_backend

pytestmark = pytest.mark.requires_loopback_server


class _GrpcServicer(pb2_grpc.RTITransportServiceServicer):
    requests: list[pb2.TransportRequest] = []

    def Request(self, request, context):  # noqa: N802 - gRPC generated naming
        self.requests.append(request)
        if request.command == "GET_HLA_VERSION":
            return pb2.TransportResponse(
                fields=[pb2.TransportValue(string_value="HLA 1516.1-2010")],
                metadata=pb2.TransportStruct(fields={"kind": pb2.TransportValue(string_value="grpc")}),
            )
        if request.command == "CONNECT":
            return pb2.TransportResponse()
        return pb2.TransportResponse(
            error=pb2.TransportError(code="RTIinternalError", message=f"Unknown command: {request.command}")
        )


def _start_server() -> tuple[grpc.Server, str]:
    _GrpcServicer.requests = []
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    pb2_grpc.add_RTITransportServiceServicer_to_server(_GrpcServicer(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    return server, f"127.0.0.1:{port}"


def test_grpc_transport_round_trips_typed_envelopes():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target)).start()
        response = transport.request(TransportRequest(command="GET_HLA_VERSION", fields=("ignored",)))

        assert response.fields == ("HLA 1516.1-2010",)
        assert response.metadata == {"kind": "grpc"}
        assert _GrpcServicer.requests[0].command == "GET_HLA_VERSION"

        direct = transport.request(TransportRequest(command="CONNECT", fields=(CallbackModel.HLA_EVOKED.name, "")))
        assert direct.fields == ()
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_grpc_transport_registers_with_backend_factory():
    server, target = _start_server()
    backend = None
    try:
        backend = create_backend("certi", transport={"kind": "grpc", "target": target})
        rti = make_rti_ambassador(backend)

        assert rti.getHLAversion() == "HLA 1516.1-2010"
        rti.connect(FederateAmbassador(), CallbackModel.HLA_EVOKED)
        assert _GrpcServicer.requests[0].command == "GET_HLA_VERSION"
        assert _GrpcServicer.requests[1].command == "CONNECT"
    finally:
        if backend is not None:
            backend.close()
        server.stop(0).wait()
