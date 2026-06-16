"""Concrete gRPC transport for backend adapters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence, cast

from hla.backends.common import BackendUnavailableError
from hla.transports.common import RTITransport, TransportError, TransportRequest, TransportResponse, register_transport_factory
from hla.transports.grpc.fedpro2010 import HLA2010RTITransport_pb2_grpc as pb2_grpc
from .client import GrpcTransportClientAdapter


_CALLBACK_POLL_COMMANDS = frozenset({"EVOKE", "EVOKE_MANY"})

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
        self._channel = None
        self._stub = None
        self.client_adapter = GrpcTransportClientAdapter()

    def start(self) -> "GrpcTransport":
        if self._channel is None:
            if self.config.secure:
                raise BackendUnavailableError("Secure gRPC transport is not configured in this workspace")
            grpc_runtime = cast(Any, grpc)
            self._channel = grpc_runtime.insecure_channel(self.config.target, options=list(self.config.channel_options))
            grpc_runtime.channel_ready_future(self._channel).result(timeout=self.config.timeout)
            self._stub = pb2_grpc.HLA2010FedProGatewayStub(self._channel)
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        if self._stub is None:
            self.start()
        assert self._stub is not None
        if request.command in _CALLBACK_POLL_COMMANDS:
            callback = self._stub.EvokeCallback(
                self.client_adapter.encode_callback_poll(),
                timeout=self.config.timeout,
                metadata=tuple(self.config.metadata.items()),
            )
            return self.client_adapter.decode_callback_request(callback)
        response = self._stub.Call(
            self.client_adapter.encode_request(request),
            timeout=self.config.timeout,
            metadata=tuple(self.config.metadata.items()),
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
