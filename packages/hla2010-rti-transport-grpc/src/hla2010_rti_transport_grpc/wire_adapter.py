"""Stable seams around the current gRPC/protobuf wire contract.

The current transport uses one generic request/response RPC with a flexible
protobuf value envelope. Future protocol work may replace that protobuf shape
without changing transport startup, lifecycle, or hosted RTI semantics.
"""
from __future__ import annotations

from typing import Any, Mapping, Protocol

from hla2010_rti_transport_common import TransportRequest, TransportResponse

GRPC_TRANSPORT_SERVICE_NAME = ".".join(
    ("hla2010", "backends", "grpc_transport", "RTITransportService")
)
GRPC_TRANSPORT_REQUEST_METHOD = "Request"
GRPC_TRANSPORT_REQUEST_PATH = f"/{GRPC_TRANSPORT_SERVICE_NAME}/{GRPC_TRANSPORT_REQUEST_METHOD}"


class TransportWireAdapter(Protocol):
    """Encode and decode backend transport envelopes for a concrete wire schema."""

    def encode_request(self, request: TransportRequest) -> Any:
        ...

    def decode_request(self, request: Any) -> TransportRequest:
        ...

    def encode_response(self, response: TransportResponse) -> Any:
        ...

    def encode_error(self, code: str, message: str, metadata: Mapping[str, Any] | None = None) -> Any:
        ...

    def decode_response(self, response: Any) -> TransportResponse:
        ...


__all__ = [
    "GRPC_TRANSPORT_REQUEST_METHOD",
    "GRPC_TRANSPORT_REQUEST_PATH",
    "GRPC_TRANSPORT_SERVICE_NAME",
    "TransportWireAdapter",
]
