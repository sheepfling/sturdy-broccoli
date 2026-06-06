"""REST-hosted RTI transport servers using the same polling callback contract as gRPC."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any, Mapping

from .python_rti import InMemoryRTIEngine, PythonRTIConfig, rti_ambassador
from .transport import TransportRequest
from ..rti import create_rti_ambassador
from .rest_transport import _dejsonify, _jsonify, _validate_struct, _wrap_struct
from .grpc_transport.python_server import _RTITransportServicer


@dataclass(frozen=True)
class PythonRTIRestServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    engine: InMemoryRTIEngine | None = None
    python_config: PythonRTIConfig | None = None
    request_path: str = "/rti/request"


@dataclass(frozen=True)
class CERTIRestServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    backend_options: Mapping[str, Any] = field(default_factory=dict)
    request_path: str = "/rti/request"


class _TransportHTTPHandler(BaseHTTPRequestHandler):
    server_ref: "_BaseRestServer"

    def do_POST(self):  # noqa: N802 - HTTP handler naming
        if self.path != self.server_ref.request_path:
            self.send_error(404)
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length).decode("utf-8")
        try:
            request = self.server_ref._decode_request(payload)
            response = self.server_ref.servicer._handle_request(request)
            body = self.server_ref._encode_response(response)
            self.send_response(200)
        except Exception as exc:
            body = self.server_ref._encode_error(exc)
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args, **_kwargs):  # pragma: no cover - keep test output quiet
        return None


class _BaseRestServer:
    def __init__(self, *, request_path: str, servicer: _RTITransportServicer, host: str, port: int) -> None:
        self.request_path = request_path
        self.servicer = servicer
        handler = type("_BoundTransportHTTPHandler", (_TransportHTTPHandler,), {})
        handler.server_ref = self
        self.server = ThreadingHTTPServer((host, port), handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.base_url = f"http://{host}:{self.server.server_port}"
        self._started = False

    def start(self):
        if not self._started:
            self.thread.start()
            self._started = True
        return self

    def close(self) -> None:
        self.servicer.close()
        if self._started:
            self.server.shutdown()
            self.server.server_close()
            self.thread.join(timeout=5)
            self._started = False

    def _decode_request(self, body: str) -> TransportRequest:
        data = json.loads(body or "{}")
        if not isinstance(data, dict):
            raise ValueError("REST transport request must be an object")
        fields = data.get("fields", [])
        if not isinstance(fields, list):
            raise ValueError("REST transport request fields must be a list")
        metadata = _validate_struct(data.get("metadata", {"fields": {}}), name="request metadata")
        return TransportRequest(
            command=str(data.get("command", "")),
            fields=tuple(_dejsonify(field) for field in fields),
            metadata=_dejsonify(metadata["fields"]),
        )

    def _encode_response(self, response) -> bytes:
        payload = {
            "fields": [_jsonify(field) for field in response.fields],
            "metadata": _wrap_struct(dict(response.metadata)),
        }
        return json.dumps(payload).encode("utf-8")

    def _encode_error(self, exc: Exception) -> bytes:
        code = exc.__class__.__name__ if exc.__class__.__name__.endswith("Error") is False else "RTIinternalError"
        payload = {"error": {"code": code, "message": str(exc)}}
        return json.dumps(payload).encode("utf-8")


class PythonRTIRestServer(_BaseRestServer):
    def __init__(self, config: PythonRTIRestServerConfig = PythonRTIRestServerConfig()) -> None:
        super().__init__(
            request_path=config.request_path,
            servicer=_RTITransportServicer(rti_ambassador(engine=config.engine, config=config.python_config)),
            host=config.host,
            port=config.port,
        )


class CERTIRestServer(_BaseRestServer):
    def __init__(self, config: CERTIRestServerConfig = CERTIRestServerConfig()) -> None:
        super().__init__(
            request_path=config.request_path,
            servicer=_RTITransportServicer(create_rti_ambassador("certi", **dict(config.backend_options))),
            host=config.host,
            port=config.port,
        )


def start_python_rti_rest_server(
    *,
    engine: InMemoryRTIEngine | None = None,
    python_config: PythonRTIConfig | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
    request_path: str = "/rti/request",
) -> PythonRTIRestServer:
    return PythonRTIRestServer(
        PythonRTIRestServerConfig(
            host=host,
            port=port,
            engine=engine,
            python_config=python_config,
            request_path=request_path,
        )
    ).start()


def start_certi_rest_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    request_path: str = "/rti/request",
    **backend_options: Any,
) -> CERTIRestServer:
    return CERTIRestServer(
        CERTIRestServerConfig(host=host, port=port, request_path=request_path, backend_options=dict(backend_options))
    ).start()


__all__ = [
    "CERTIRestServer",
    "CERTIRestServerConfig",
    "PythonRTIRestServer",
    "PythonRTIRestServerConfig",
    "start_certi_rest_server",
    "start_python_rti_rest_server",
]
