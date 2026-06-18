from __future__ import annotations

from concurrent import futures

import grpc
import pytest
from hla.transports.common.transport import TransportRequest
from hla.transports.grpc import GrpcTransport, GrpcTransportConfig
from hla.transports.grpc.fedpro2025 import FederateAmbassador_2025_pb2 as callback_pb2
from hla.transports.grpc.fedpro2025 import HLA2025RTITransport_pb2_grpc as transport_pb2_grpc
from hla.transports.grpc.fedpro2025 import RTIambassador_2025_pb2 as rti_pb2
from hla.transports.grpc.fedpro2025 import datatypes_2025_pb2 as datatypes_pb2
from hla.transports.grpc.python_server_2025 import start_2025_grpc_server

pytestmark = pytest.mark.requires_loopback_server


class _FedPro2025Servicer(transport_pb2_grpc.HLA2025FedProGatewayServicer):
    def Call(self, request, context):  # noqa: N802 - grpc generated naming
        request_kind = request.WhichOneof("callRequest")
        if request_kind in {
            "connectRequest",
            "connectWithCredentialsRequest",
            "connectWithConfigurationRequest",
            "connectWithConfigurationAndCredentialsRequest",
        }:
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        if request_kind == "getFederateHandleRequest":
            return rti_pb2.CallResponse(getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(result=datatypes_pb2.FederateHandle(data=b"42")))
        return rti_pb2.CallResponse(
            exceptionData=datatypes_pb2.ExceptionData(
                exceptionName="RTIinternalError",
                details=f"Unsupported test call: {request_kind}",
            )
        )

    def EvokeCallback(self, request, context):  # noqa: N802 - grpc generated naming
        return callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"7")))


def _start_server() -> tuple[grpc.Server, str]:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    transport_pb2_grpc.add_HLA2025FedProGatewayServicer_to_server(_FedPro2025Servicer(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    return server, f"127.0.0.1:{port}"


def test_fedpro2025_schema_imports_are_canonical():
    assert rti_pb2.CallRequest.DESCRIPTOR.full_name == "rti1516_2025.fedpro.CallRequest"
    assert callback_pb2.CallbackRequest.DESCRIPTOR.full_name == "rti1516_2025.fedpro.CallbackRequest"
    assert hasattr(transport_pb2_grpc, "HLA2025FedProGatewayStub")


def test_2025_grpc_transport_round_trips_typed_call_oneofs():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target, schema="rti1516_2025")).start()
        response = transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", "")))
        assert response.fields == ("",)

        handle = transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)))
        assert handle.fields == ("42",)
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_2025_grpc_transport_round_trips_typed_callback_oneofs():
    server, target = _start_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=target, schema="2025")).start()
        response = transport.request(TransportRequest(command="EVOKE"))

        assert response.fields[:2] == ("1", "TIME_ADVANCE_GRANT")
        assert response.fields[-1] == "7"
        assert response.fields[2] in {"HLAfloat64Time", "HLAinteger64Time"}
    finally:
        if transport is not None:
            transport.close()
        server.stop(0).wait()


def test_2025_transport_server_smoke_uses_the_new_schema_package():
    server = start_2025_grpc_server()
    transport = None
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()
        handle = transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)))
        assert handle.fields == ("42",)
    finally:
        if transport is not None:
            transport.close()
        server.close()


def test_2025_transport_server_runs_lifecycle_session_over_fedpro_schema():
    server = start_2025_grpc_server()
    transport = None
    federation_name = "fedpro-2025-lifecycle"
    try:
        transport = GrpcTransport(GrpcTransportConfig(target=server.target, schema="rti1516_2025")).start()

        assert transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", ""))).fields == ("",)
        assert (
            transport.request(
                TransportRequest(
                    command="CREATE",
                    fields=(federation_name, "HLAinteger64Time", "TargetRadarFOMmodule.xml"),
                )
            ).fields
            == ()
        )
        assert transport.request(
            TransportRequest(
                command="JOIN",
                fields=("FedPro2025Federate", "TestFederate", federation_name),
            )
        ).fields == ("1", "HLAinteger64Time")

        callback = transport.request(TransportRequest(command="EVOKE"))
        assert callback.fields == ("1", "TIME_ADVANCE_GRANT", "HLAinteger64Time", "7")

        assert transport.request(TransportRequest(command="RESIGN", fields=("NO_ACTION",))).fields == ()
        assert transport.request(TransportRequest(command="DESTROY", fields=(federation_name,))).fields == ()
        assert transport.request(TransportRequest(command="DISCONNECT")).fields == ()

        assert server.servicer.calls == [
            "connectRequest",
            "createFederationExecutionWithModulesAndTimeRequest",
            "joinFederationExecutionWithNameRequest",
            "resignFederationExecutionRequest",
            "destroyFederationExecutionRequest",
            "disconnectRequest",
        ]
        assert federation_name not in server.servicer.federations
        assert server.servicer.joined_federates == {}
    finally:
        if transport is not None:
            transport.close()
        server.close()
