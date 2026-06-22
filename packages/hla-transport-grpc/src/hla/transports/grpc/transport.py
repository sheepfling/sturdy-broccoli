"""Concrete gRPC transport for backend adapters."""
from __future__ import annotations

import importlib
import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence, cast

from hla.backends.common import BackendUnavailableError
from hla.transports.common import RTITransport, TransportError, TransportRequest, TransportResponse, register_transport_factory
from .client import GrpcTransportClientAdapter as GrpcTransportClientAdapter2010
from .client_2025 import GrpcTransportClientAdapter as GrpcTransportClientAdapter2025


_CALLBACK_POLL_COMMANDS = frozenset({"EVOKE", "EVOKE_MANY"})
_SCHEMA_ALIASES = {
    "2010": "rti1516e",
    "rti1516e": "rti1516e",
    "rti1516_e": "rti1516e",
    "2025": "rti1516_2025",
    "rti1516_2025": "rti1516_2025",
    "rti1516-2025": "rti1516_2025",
}
_SCHEMA_MODULES = {
    "rti1516e": (
        GrpcTransportClientAdapter2010,
        "hla.transports.grpc.fedpro2010.HLA2010RTITransport_pb2_grpc",
    ),
    "rti1516_2025": (
        GrpcTransportClientAdapter2025,
        "hla.transports.grpc.fedpro2025.HLA2025RTITransport_pb2_grpc",
    ),
}

try:  # pragma: no cover - import guarded for optional dependency
    import grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None  # type: ignore[assignment]
    _GRPC_IMPORT_ERROR = exc
else:
    _GRPC_IMPORT_ERROR = None


@dataclass(frozen=True)
class GrpcTransportConfig:
    """Configuration for :class:`GrpcTransport`."""

    target: str
    schema: str = "rti1516e"
    timeout: float = 30.0
    metadata: Mapping[str, str] = field(default_factory=dict)
    channel_options: Sequence[tuple[str, Any]] = field(default_factory=tuple)
    secure: bool = False


class GrpcTransport(RTITransport):
    """Typed gRPC transport carrying HLA traffic."""

    def __init__(self, config: GrpcTransportConfig):
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise BackendUnavailableError("gRPC transport requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        schema_name = _SCHEMA_ALIASES.get(str(config.schema).strip().lower(), str(config.schema).strip().lower())
        try:
            adapter_cls, pb2_grpc_module = _SCHEMA_MODULES[schema_name]
        except KeyError as exc:
            supported = ", ".join(sorted(_SCHEMA_MODULES))
            raise ValueError(f"Unsupported gRPC schema {config.schema!r}; supported schemas: {supported}") from exc
        self._schema_name = schema_name
        self._adapter_cls = adapter_cls
        self._pb2_grpc = importlib.import_module(pb2_grpc_module)
        self._channel = None
        self._stub = None
        self.client_adapter = self._adapter_cls()
        metadata = dict(config.metadata)
        metadata.setdefault("x-hla-session-id", uuid.uuid4().hex)
        self._request_metadata = tuple(metadata.items())

    def start(self) -> "GrpcTransport":
        if self._channel is None:
            if self.config.secure:
                raise BackendUnavailableError("Secure gRPC transport is not configured in this workspace")
            grpc_runtime = cast(Any, grpc)
            self._channel = grpc_runtime.insecure_channel(self.config.target, options=list(self.config.channel_options))
            grpc_runtime.channel_ready_future(self._channel).result(timeout=self.config.timeout)
            if self._schema_name == "rti1516_2025":
                self._stub = self._pb2_grpc.HLA2025FedProGatewayStub(self._channel)
            else:
                self._stub = self._pb2_grpc.HLA2010FedProGatewayStub(self._channel)
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        if self._stub is None:
            self.start()
        assert self._stub is not None
        if request.command in _CALLBACK_POLL_COMMANDS:
            callback = self._stub.EvokeCallback(
                self.client_adapter.encode_callback_poll(),
                timeout=self.config.timeout,
                metadata=self._request_metadata,
            )
            return self.client_adapter.decode_callback_request(callback)
        response = self._stub.Call(
            self.client_adapter.encode_request(request),
            timeout=self.config.timeout,
            metadata=self._request_metadata,
        )
        try:
            return self.client_adapter.decode_response(request, response)
        except TransportError:
            raise

    def close(self) -> None:
        self._stub = None
        if self._channel is not None:
            self._channel.close()
            self._channel = None

    def capability_report(self) -> dict[str, object]:
        adapter_report = {}
        report_method = getattr(self.client_adapter, "capability_report", None)
        if callable(report_method):
            adapter_report = dict(report_method())
        return {
            **adapter_report,
            "target": self.config.target,
            "schema": self._schema_name,
            "secure": self.config.secure,
            "started": self._channel is not None,
        }


def create_grpc_transport(config: GrpcTransportConfig) -> GrpcTransport:
    return GrpcTransport(config)


register_transport_factory(
    "grpc",
    lambda spec: create_grpc_transport(GrpcTransportConfig(**dict(spec.options))),
)


__all__ = [
    "GrpcTransport",
    "GrpcTransportConfig",
    "create_grpc_transport",
]
