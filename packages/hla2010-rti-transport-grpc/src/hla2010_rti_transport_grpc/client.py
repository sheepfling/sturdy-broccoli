"""Client-side adapter between typed transport envelopes and protobuf objects."""
from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, cast

from hla2010.backends.transport import TransportError, TransportRequest, TransportResponse
from . import rti_transport_pb2 as pb2

_pb2 = cast(Any, pb2)


class GrpcTransportClientAdapter:
    """Map typed transport envelopes onto generated protobuf client objects."""

    @staticmethod
    def _encode_value(value: Any) -> Any:
        if value is None:
            return _pb2.TransportValue(null_value=0)
        if isinstance(value, bool):
            return _pb2.TransportValue(bool_value=value)
        if isinstance(value, int) and not isinstance(value, bool):
            return _pb2.TransportValue(int64_value=int(value))
        if isinstance(value, float):
            return _pb2.TransportValue(double_value=float(value))
        if isinstance(value, str):
            return _pb2.TransportValue(string_value=value)
        if isinstance(value, (bytes, bytearray, memoryview)):
            return _pb2.TransportValue(bytes_value=bytes(value))
        if isinstance(value, Enum):
            return _pb2.TransportValue(string_value=value.name)
        if isinstance(value, Mapping):
            return _pb2.TransportValue(
                struct_value=_pb2.TransportStruct(
                    fields={str(key): GrpcTransportClientAdapter._encode_value(item) for key, item in value.items()}
                )
            )
        if isinstance(value, (tuple, list, set, frozenset)):
            return _pb2.TransportValue(
                list_value=_pb2.TransportList(values=[GrpcTransportClientAdapter._encode_value(item) for item in value])
            )
        return _pb2.TransportValue(string_value=str(value))

    @staticmethod
    def _decode_value(value: Any) -> Any:
        kind = value.WhichOneof("kind")
        if kind == "null_value":
            return None
        if kind == "bool_value":
            return value.bool_value
        if kind == "int64_value":
            return int(value.int64_value)
        if kind == "double_value":
            return float(value.double_value)
        if kind == "string_value":
            return value.string_value
        if kind == "bytes_value":
            return bytes(value.bytes_value)
        if kind == "list_value":
            return tuple(GrpcTransportClientAdapter._decode_value(item) for item in value.list_value.values)
        if kind == "struct_value":
            return {key: GrpcTransportClientAdapter._decode_value(item) for key, item in value.struct_value.fields.items()}
        return None

    @staticmethod
    def _encode_struct(values: Mapping[str, Any]) -> Any:
        return _pb2.TransportStruct(fields={str(key): GrpcTransportClientAdapter._encode_value(value) for key, value in values.items()})

    @staticmethod
    def _decode_struct(value: Any | None) -> dict[str, Any]:
        if value is None:
            return {}
        return {key: GrpcTransportClientAdapter._decode_value(item) for key, item in value.fields.items()}

    def encode_request(self, request: TransportRequest) -> Any:
        return _pb2.TransportRequest(
            command=request.command,
            fields=[self._encode_value(field) for field in request.fields],
            metadata=self._encode_struct(dict(request.metadata)),
        )

    def decode_request(self, request: Any) -> TransportRequest:
        return TransportRequest(
            command=request.command,
            fields=tuple(self._decode_value(field) for field in request.fields),
            metadata=self._decode_struct(request.metadata),
        )

    def encode_response(self, response: TransportResponse) -> Any:
        return _pb2.TransportResponse(
            fields=[self._encode_value(field) for field in response.fields],
            metadata=self._encode_struct(dict(response.metadata)),
        )

    def encode_error(self, code: str, message: str, metadata: Mapping[str, Any] | None = None) -> Any:
        return _pb2.TransportResponse(
            error=_pb2.TransportError(
                code=code,
                message=message,
                metadata=self._encode_struct(dict(metadata or {})),
            )
        )

    def decode_response(self, response: Any) -> TransportResponse:
        if response.HasField("error"):
            error = response.error
            raise TransportError(
                error.code or "RTIinternalError",
                error.message or error.code or "RTIinternalError",
            )
        return TransportResponse(
            fields=tuple(self._decode_value(field) for field in response.fields),
            metadata=self._decode_struct(response.metadata),
        )


__all__ = ["GrpcTransportClientAdapter"]
