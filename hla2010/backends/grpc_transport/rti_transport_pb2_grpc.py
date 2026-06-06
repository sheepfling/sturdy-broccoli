"""gRPC service helpers for the RTI transport proto."""
from __future__ import annotations

import grpc

from . import rti_transport_pb2 as rti__transport__pb2


class RTITransportServiceStub:
    def __init__(self, channel: grpc.Channel):
        self.Request = channel.unary_unary(
            "/hla2010.backends.grpc_transport.RTITransportService/Request",
            request_serializer=rti__transport__pb2.TransportRequest.SerializeToString,
            response_deserializer=rti__transport__pb2.TransportResponse.FromString,
        )


class RTITransportServiceServicer:
    def Request(self, request, context):  # pragma: no cover - base shim only
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_RTITransportServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Request": grpc.unary_unary_rpc_method_handler(
            servicer.Request,
            request_deserializer=rti__transport__pb2.TransportRequest.FromString,
            response_serializer=rti__transport__pb2.TransportResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "hla2010.backends.grpc_transport.RTITransportService",
        rpc_method_handlers,
    )
    server.add_generic_rpc_handlers((generic_handler,))


__all__ = [
    "RTITransportServiceStub",
    "RTITransportServiceServicer",
    "add_RTITransportServiceServicer_to_server",
]
