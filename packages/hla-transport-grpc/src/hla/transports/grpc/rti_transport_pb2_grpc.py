"""gRPC service helpers for the RTI transport proto."""
from __future__ import annotations

import grpc
from google.protobuf import message as _message

from . import rti_transport_pb2 as rti__transport__pb2


def _serialize_request(message: _message.Message) -> bytes:
    return message.SerializeToString()


def _deserialize_request(data: bytes):
    return rti__transport__pb2.TransportRequest().FromString(data)  # type: ignore[reportAttributeAccessIssue]


def _serialize_response(message: _message.Message) -> bytes:
    return message.SerializeToString()


def _deserialize_response(data: bytes):
    return rti__transport__pb2.TransportResponse().FromString(data)  # type: ignore[reportAttributeAccessIssue]


class RTITransportServiceStub:
    def __init__(self, channel: grpc.Channel):
        self.Request = channel.unary_unary(
            "/hla.rti1516e.backends.grpc_transport.RTITransportService/Request",
            request_serializer=_serialize_request,
            response_deserializer=_deserialize_response,
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
            request_deserializer=_deserialize_request,
            response_serializer=_serialize_response,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "hla.rti1516e.backends.grpc_transport.RTITransportService",
        rpc_method_handlers,
    )
    server.add_generic_rpc_handlers((generic_handler,))


__all__ = [
    "RTITransportServiceStub",
    "RTITransportServiceServicer",
    "add_RTITransportServiceServicer_to_server",
]
