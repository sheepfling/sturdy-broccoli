from __future__ import annotations

from concurrent import futures

import grpc
import pytest

from hla.backends.common import make_rti_ambassador
from hla.rti import create_backend
from hla.transports.common.transport import TransportError, TransportRequest
from hla.transports.grpc import GrpcTransport, GrpcTransportConfig
from hla.transports.grpc.fedpro2010 import FederateAmbassador_pb2 as callback_pb2
from hla.transports.grpc.fedpro2010 import HLA2010RTITransport_pb2_grpc as transport_pb2_grpc
from hla.transports.grpc.fedpro2010 import RTIambassador_pb2 as rti_pb2
from hla.transports.grpc.fedpro2010 import datatypes_pb2

pytestmark = pytest.mark.requires_loopback_server


class _FedProServicer(transport_pb2_grpc.HLA2010FedProGatewayServicer):
    requests: list[rti_pb2.CallRequest] = []
    callback_request: callback_pb2.CallbackRequest = callback_pb2.CallbackRequest(
        timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"7"))
    )

    def Call(self, request, context):  # noqa: N802 - gRPC generated naming
        self.requests.append(request)
        request_kind = request.WhichOneof("callRequest")
        if request_kind == "getFederateHandleRequest":
            return rti_pb2.CallResponse(
                getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(
                    result=datatypes_pb2.FederateHandle(data=b"42")
                )
            )
        if request_kind == "connectRequest":
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        return rti_pb2.CallResponse(
            exceptionData=datatypes_pb2.ExceptionData(
                exceptionName="RTIinternalError",
                details=f"Unsupported test call: {request_kind}",
            )
        )

    def EvokeCallback(self, request, context):  # noqa: N802 - gRPC generated naming
        return self.callback_request


def _start_server() -> tuple[grpc.Server, str]:
    _FedProServicer.requests = []
    _FedProServicer.callback_request = callback_pb2.CallbackRequest(
        timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"7"))
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    transport_pb2_grpc.add_HLA2010FedProGatewayServicer_to_server(_FedProServicer(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    return server, f"127.0.0.1:{port}"


def test_fedpro2010_schema_imports_are_canonical():
    assert rti_pb2.CallRequest.DESCRIPTOR.full_name == "rti1516e.fedpro.CallRequest"
    assert callback_pb2.CallbackRequest.DESCRIPTOR.full_name == "rti1516e.fedpro.CallbackRequest"
    assert hasattr(transport_pb2_grpc, "HLA2010FedProGatewayStub")


def test_grpc_transport_round_trips_typed_call_oneofs():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target)).start()
        response = transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)))

        assert response.fields == ("42",)
        assert _FedProServicer.requests[0].WhichOneof("callRequest") == "getFederateHandleRequest"
        assert _FedProServicer.requests[0].getFederateHandleRequest.federateName == "alpha"

        direct = transport.request(TransportRequest(command="CONNECT", fields=("HLA_EVOKED", "")))
        assert direct.fields == ()
        assert _FedProServicer.requests[1].WhichOneof("callRequest") == "connectRequest"
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_grpc_transport_reports_typed_exceptions():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target)).start()
        with pytest.raises(TransportError, match="GET_HLA_VERSION"):
            transport.request(TransportRequest(command="GET_HLA_VERSION"))
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_grpc_transport_round_trips_typed_callback_oneofs():
    server, target = _start_server()
    transport = None
    try:
        _FedProServicer.callback_request = callback_pb2.CallbackRequest(
            provideAttributeValueUpdate=callback_pb2.ProvideAttributeValueUpdate(
                objectInstance=datatypes_pb2.ObjectInstanceHandle(data=b"12"),
                attributes=datatypes_pb2.AttributeHandleSet(
                    attributeHandle=[
                        datatypes_pb2.AttributeHandle(data=b"3"),
                        datatypes_pb2.AttributeHandle(data=b"4"),
                    ]
                ),
                userSuppliedTag=b"rcs",
            )
        )
        transport = GrpcTransport(GrpcTransportConfig(target=target)).start()

        response = transport.request(TransportRequest(command="EVOKE"))

        assert response.fields == ("1", "PROVIDE_ATTRIBUTE_VALUE_UPDATE", "12", "3,4", "726373")
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_grpc_transport_registers_with_backend_factory():
    server, target = _start_server()
    backend = None
    try:
        backend = create_backend("certi", spec="rti1516e", transport={"kind": "grpc", "target": target})
        rti = make_rti_ambassador(backend)

        handle = rti.getFederateHandle("alpha")

        assert int(handle.value) == 42
        assert _FedProServicer.requests[0].WhichOneof("callRequest") == "getFederateHandleRequest"
    finally:
        if backend is not None:
            backend.close()
        server.stop(0).wait()
