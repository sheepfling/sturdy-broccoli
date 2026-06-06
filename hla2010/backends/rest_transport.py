"""REST transport for RTI backend adapters.

This transport speaks the OpenAPI envelope in ``docs/openapi/rti_transport.yaml``.
It is intentionally narrow: requests and responses carry a command, typed field
values, and a ``metadata.fields`` object that mirrors the schema used by the
typed transport seam in ``hla2010.backends.transport``.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import base64
import json
from enum import Enum
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .base import BackendUnavailableError
from .transport import RTITransport, TransportError, TransportRequest, TransportResponse
from ..rti import register_transport_factory


def _wrap_struct(values: Mapping[str, Any]) -> dict[str, Any]:
    return {"fields": {str(key): _jsonify(value) for key, value in values.items()}}


def _jsonify(value: Any) -> Any:
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
        return {"__type__": "dataclass", "class": value.__class__.__name__, "value": _jsonify(asdict(value))}
    if isinstance(value, Mapping):
        return {str(key): _jsonify(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonify(item) for item in value]
    return str(value)


def _dejsonify(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_dejsonify(item) for item in value)
    if isinstance(value, dict):
        marker = value.get("__type__")
        if marker == "bytes":
            return base64.b64decode(value.get("base64", ""))
        if marker == "dataclass":
            return _dejsonify(value.get("value"))
        if marker == "enum":
            return value.get("name")
        return {key: _dejsonify(item) for key, item in value.items()}
    return value


def _validate_struct(value: Any, *, name: str) -> dict[str, Any]:
    if value is None:
        return {"fields": {}}
    if not isinstance(value, dict):
        raise TransportError("RTIinternalError", f"REST transport {name} must be an object")
    extra = set(value) - {"fields"}
    if extra:
        raise TransportError("RTIinternalError", f"REST transport {name} has unexpected keys: {', '.join(sorted(extra))}")
    fields = value.get("fields", {})
    if not isinstance(fields, dict):
        raise TransportError("RTIinternalError", f"REST transport {name}.fields must be an object")
    return {"fields": fields}


@dataclass(frozen=True)
class RestTransportConfig:
    """Configuration for :class:`RestTransport`."""

    base_url: str
    request_path: str = "/rti/request"
    timeout: float = 30.0
    headers: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url must be provided")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must use http:// or https://")


class RestTransport(RTITransport):
    """Typed JSON-over-HTTP transport for HLA backend adapters."""

    def __init__(self, config: RestTransportConfig):
        self.config = config
        self._started = False

    def start(self) -> "RestTransport":
        self._started = True
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        if not self._started:
            self.start()

        url = urljoin(self.config.base_url.rstrip("/") + "/", self.config.request_path.lstrip("/"))
        payload = self._build_payload(request)
        headers = {"Content-Type": "application/json", **dict(self.config.headers or {})}
        http_request = Request(url, data=payload, headers=headers, method="POST")

        try:
            with urlopen(http_request, timeout=self.config.timeout) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            self._raise_for_body(body, default_code=f"HTTP{exc.code}")
        except URLError as exc:
            raise BackendUnavailableError(f"REST transport could not reach {url}: {exc.reason}") from exc

        return self._decode_response_body(body)

    def _build_payload(self, request: TransportRequest) -> bytes:
        payload = {
            "command": request.command,
            "fields": [_jsonify(field) for field in request.fields],
            "metadata": _wrap_struct(dict(request.metadata)),
        }
        return json.dumps(payload).encode("utf-8")

    def _decode_response_body(self, body: str) -> TransportResponse:
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
            metadata = _validate_struct(data.get("metadata", {"fields": {}}), name="response metadata")
            if not isinstance(fields, list):
                raise TransportError("RTIinternalError", "REST transport response fields must be a list")
            return TransportResponse(
                fields=tuple(_dejsonify(field) for field in fields),
                metadata=_dejsonify(metadata["fields"]),
            )
        if isinstance(data, list):
            return TransportResponse(fields=tuple(_dejsonify(item) for item in data))
        raise TransportError("RTIinternalError", f"Unexpected REST transport response: {data!r}")

    def _raise_for_body(self, body: str, *, default_code: str) -> None:
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


def create_rest_transport(config: RestTransportConfig) -> RestTransport:
    return RestTransport(config)


register_transport_factory("rest", lambda spec: create_rest_transport(RestTransportConfig(**dict(spec.options))))
register_transport_factory("http-json", lambda spec: create_rest_transport(RestTransportConfig(**dict(spec.options))))


__all__ = [
    "RestTransport",
    "RestTransportConfig",
    "create_rest_transport",
]
