"""Client-side adapter between typed transport envelopes and REST JSON DTOs."""
from __future__ import annotations

import base64
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Mapping, cast

from hla.transports.common import TransportError, TransportRequest, TransportResponse


class RestTransportClientAdapter:
    """Map typed transport envelopes onto the OpenAPI JSON transport envelope."""

    @staticmethod
    def _encode_value(value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, bytes):
            return {"__type__": "bytes", "base64": base64.b64encode(value).decode("ascii")}
        if isinstance(value, bytearray):
            return {"__type__": "bytes", "base64": base64.b64encode(bytes(value)).decode("ascii")}
        if isinstance(value, memoryview):
            return {"__type__": "bytes", "base64": base64.b64encode(value.tobytes()).decode("ascii")}
        if isinstance(value, Enum):
            return {
                "__type__": "enum",
                "class": value.__class__.__name__,
                "name": value.name,
                "value": value.value,
            }
        if is_dataclass(value):
            dataclass_value = cast(Any, value)
            return {
                "__type__": "dataclass",
                "class": dataclass_value.__class__.__name__,
                "value": RestTransportClientAdapter._encode_value(asdict(dataclass_value)),
            }
        if isinstance(value, Mapping):
            return {str(key): RestTransportClientAdapter._encode_value(item) for key, item in value.items()}
        if isinstance(value, (tuple, list, set, frozenset)):
            return [RestTransportClientAdapter._encode_value(item) for item in value]
        return str(value)

    @staticmethod
    def _decode_value(value: Any) -> Any:
        if isinstance(value, list):
            return tuple(RestTransportClientAdapter._decode_value(item) for item in value)
        if isinstance(value, dict):
            marker = value.get("__type__")
            if marker == "bytes":
                return base64.b64decode(value.get("base64", ""))
            if marker == "dataclass":
                return RestTransportClientAdapter._decode_value(value.get("value"))
            if marker == "enum":
                return value.get("name")
            return {key: RestTransportClientAdapter._decode_value(item) for key, item in value.items()}
        return value

    @staticmethod
    def encode_struct(values: Mapping[str, Any]) -> dict[str, Any]:
        return {"fields": {str(key): RestTransportClientAdapter._encode_value(value) for key, value in values.items()}}

    @staticmethod
    def decode_struct(value: Any, *, name: str) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TransportError("RTIinternalError", f"REST transport {name} must be an object")
        extra = set(value) - {"fields"}
        if extra:
            raise TransportError("RTIinternalError", f"REST transport {name} has unexpected keys: {', '.join(sorted(extra))}")
        fields = value.get("fields", {})
        if not isinstance(fields, dict):
            raise TransportError("RTIinternalError", f"REST transport {name}.fields must be an object")
        return {str(key): RestTransportClientAdapter._decode_value(item) for key, item in fields.items()}

    def encode_request(self, request: TransportRequest) -> bytes:
        payload = {
            "command": request.command,
            "fields": [self._encode_value(field) for field in request.fields],
            "metadata": self.encode_struct(dict(request.metadata)),
        }
        return json.dumps(payload).encode("utf-8")

    def decode_request(self, body: str) -> TransportRequest:
        data = json.loads(body or "{}")
        if not isinstance(data, dict):
            raise TransportError("RTIinternalError", "REST transport request must be an object")
        fields = data.get("fields", [])
        if not isinstance(fields, list):
            raise TransportError("RTIinternalError", "REST transport request fields must be a list")
        metadata = self.decode_struct(data.get("metadata", {"fields": {}}), name="request metadata")
        return TransportRequest(
            command=str(data.get("command", "")),
            fields=tuple(self._decode_value(field) for field in fields),
            metadata=metadata,
        )

    def encode_response(self, response: TransportResponse) -> bytes:
        payload = {
            "fields": [self._encode_value(field) for field in response.fields],
            "metadata": self.encode_struct(dict(response.metadata)),
        }
        return json.dumps(payload).encode("utf-8")

    def encode_error(self, exc: Exception) -> bytes:
        code = exc.__class__.__name__ if not exc.__class__.__name__.endswith("Error") else "RTIinternalError"
        payload = {"error": {"code": code, "message": str(exc)}}
        return json.dumps(payload).encode("utf-8")

    def decode_response(self, body: str) -> TransportResponse:
        data = json.loads(body or "{}")
        if isinstance(data, dict):
            error = data.get("error")
            if error:
                if isinstance(error, dict):
                    code = str(error.get("code", "RTIinternalError"))
                    message = str(error.get("message", code))
                else:
                    code = "RTIinternalError"
                    message = str(error)
                raise TransportError(code, message)
            extra = set(data) - {"fields", "metadata", "error"}
            if extra:
                raise TransportError("RTIinternalError", f"Unexpected REST transport response keys: {', '.join(sorted(extra))}")
            fields = data.get("fields", ())
            if not isinstance(fields, list):
                raise TransportError("RTIinternalError", "REST transport response fields must be a list")
            return TransportResponse(
                fields=tuple(self._decode_value(field) for field in fields),
                metadata=self.decode_struct(data.get("metadata", {"fields": {}}), name="response metadata"),
            )
        if isinstance(data, list):
            return TransportResponse(fields=tuple(self._decode_value(item) for item in data))
        raise TransportError("RTIinternalError", f"Unexpected REST transport response: {data!r}")

    def raise_for_error_body(self, body: str, *, default_code: str) -> None:
        try:
            data = json.loads(body)
        except Exception:
            raise TransportError(default_code, body or default_code)

        if isinstance(data, dict):
            error = data.get("error")
            if isinstance(error, dict):
                code = str(error.get("code", default_code))
                message = str(error.get("message", code))
                raise TransportError(code, message)
            message = str(data.get("message", body or default_code))
            code = str(data.get("code", default_code))
            raise TransportError(code, message)

        raise TransportError(default_code, body or default_code)


__all__ = ["RestTransportClientAdapter"]
