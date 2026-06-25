"""Copyable scaffold for vendor-specific gRPC transport variants."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from hla.backends.common import BackendUnavailableError
from hla.transports.common import RTITransport, TransportError, TransportRequest, TransportResponse, register_transport_factory

_CALLBACK_POLL_COMMANDS = frozenset({"EVOKE", "EVOKE_MANY"})


@dataclass(frozen=True)
class VendorGrpcTransportConfig:
    """Configuration for a thin vendor-specific gRPC route variant."""

    target: str
    timeout: float = 30.0
    metadata: Mapping[str, str] = field(default_factory=dict)
    command_rpc_names: Mapping[str, str] = field(
        default_factory=lambda: {
            "GET_HLA_VERSION": "GetHlaVersion",
            "GET_FEDERATE_HANDLE": "GetFederateHandle",
            "CONNECT": "Connect",
        }
    )
    callback_poll_rpc_name: str = "EvokeCallback"


class VendorGrpcWireAdapter:
    """Route-local mapping between transport requests and vendor gRPC payloads."""

    def __init__(self, config: VendorGrpcTransportConfig):
        self.config = config

    def encode_request(self, request: TransportRequest) -> dict[str, Any]:
        rpc_name = self.config.command_rpc_names.get(request.command, request.command)
        metadata = dict(self.config.metadata)
        metadata.update({str(key): str(value) for key, value in request.metadata.items()})
        return {
            "rpc": rpc_name,
            "payload": {
                "command": request.command,
                "fields": list(request.fields),
            },
            "metadata": metadata,
        }

    def decode_response(self, request: TransportRequest, response: Mapping[str, Any]) -> TransportResponse:
        error = response.get("error")
        if isinstance(error, Mapping):
            code = str(error.get("code", "RTIinternalError"))
            message = str(error.get("message", request.command))
            raise TransportError(code, message)
        fields = tuple(response.get("fields", ()))
        metadata = response.get("metadata", {})
        if not isinstance(metadata, Mapping):
            metadata = {}
        return TransportResponse(fields=fields, metadata=metadata)

    def encode_callback_poll(self) -> dict[str, Any]:
        return {
            "rpc": self.config.callback_poll_rpc_name,
            "payload": {},
            "metadata": dict(self.config.metadata),
        }

    def decode_callback_request(self, response: Mapping[str, Any]) -> TransportResponse:
        delivered = bool(response.get("delivered", False))
        callback_name = str(response.get("callback_name", "")) if delivered else ""
        callback_fields = tuple(response.get("fields", ())) if delivered else ()
        if not delivered:
            return TransportResponse(fields=("0",))
        return TransportResponse(fields=("1", callback_name, *callback_fields))

    def capability_report(self) -> dict[str, object]:
        return {
            "transport_kind": "vendor-grpc",
            "callback_poll_rpc_name": self.config.callback_poll_rpc_name,
            "mapped_command_count": len(self.config.command_rpc_names),
        }


class QuirkyVendorGrpcWireAdapter(VendorGrpcWireAdapter):
    """Concrete example of a mildly awkward vendor-specific gRPC dialect.

    This adapter intentionally uses a non-FedPro envelope shape so the repo has
    a maintained example of how to isolate quirks without changing RTI
    semantics.
    """

    def encode_request(self, request: TransportRequest) -> dict[str, Any]:
        rpc_name = self.config.command_rpc_names.get(request.command, request.command)
        metadata = dict(self.config.metadata)
        metadata.update({str(key): str(value) for key, value in request.metadata.items()})
        metadata.setdefault("x-quirky-wire", "enabled")
        return {
            "rpc": rpc_name,
            "quirks": {
                "style": "capsule-v1",
                "field_count": len(request.fields),
            },
            "capsule": {
                "verb": request.command.lower(),
                "items": [
                    {
                        "slot": index,
                        "text": str(field),
                    }
                    for index, field in enumerate(request.fields)
                ],
            },
            "metadata": metadata,
        }

    def decode_response(self, request: TransportRequest, response: Mapping[str, Any]) -> TransportResponse:
        problem = response.get("problem")
        if isinstance(problem, Mapping):
            code = str(problem.get("kind", "RTIinternalError"))
            message = str(problem.get("detail", request.command))
            raise TransportError(code, message)
        result = response.get("result", {})
        fields = ()
        metadata: Mapping[str, Any] = {}
        if isinstance(result, Mapping):
            fields = tuple(result.get("values", ()))
            result_meta = result.get("meta", {})
            if isinstance(result_meta, Mapping):
                metadata = result_meta
        return TransportResponse(fields=fields, metadata=metadata)

    def encode_callback_poll(self) -> dict[str, Any]:
        return {
            "rpc": self.config.callback_poll_rpc_name,
            "poll": {
                "mode": "single-tick",
            },
            "metadata": {
                **dict(self.config.metadata),
                "x-quirky-wire": "enabled",
            },
        }

    def decode_callback_request(self, response: Mapping[str, Any]) -> TransportResponse:
        envelope = response.get("callbackEnvelope", {})
        if not isinstance(envelope, Mapping) or not bool(envelope.get("present", False)):
            return TransportResponse(fields=("0",))
        callback_name = str(envelope.get("name", ""))
        callback_fields = tuple(envelope.get("arguments", ()))
        return TransportResponse(fields=("1", callback_name, *callback_fields))

    def capability_report(self) -> dict[str, object]:
        return {
            **super().capability_report(),
            "transport_kind": "quirky-vendor-grpc",
            "wire_style": "capsule-v1",
        }


class VendorGrpcTransport(RTITransport):
    """Thin transport shell for a vendor-specific gRPC route variant.

    The default scaffold requires a route-local invoke function to be supplied.
    Real integrations should replace that callable with concrete gRPC stub
    wiring while keeping the adapter contract unchanged.
    """

    def __init__(
        self,
        config: VendorGrpcTransportConfig,
        *,
        adapter: VendorGrpcWireAdapter | None = None,
        invoke: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
    ) -> None:
        self.config = config
        self.adapter = adapter or VendorGrpcWireAdapter(config)
        self._invoke = invoke

    def start(self) -> "VendorGrpcTransport":
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        if self._invoke is None:
            raise BackendUnavailableError(
                "VendorGrpcTransport scaffold requires a route-local invoke implementation"
            )
        if request.command in _CALLBACK_POLL_COMMANDS:
            response = self._invoke(self.config.callback_poll_rpc_name, self.adapter.encode_callback_poll())
            return self.adapter.decode_callback_request(response)
        encoded = self.adapter.encode_request(request)
        response = self._invoke(str(encoded["rpc"]), encoded)
        return self.adapter.decode_response(request, response)

    def close(self) -> None:
        return None

    def capability_report(self) -> dict[str, object]:
        return {
            **self.adapter.capability_report(),
            "target": self.config.target,
        }


def create_vendor_grpc_transport(
    config: VendorGrpcTransportConfig,
    *,
    adapter: VendorGrpcWireAdapter | None = None,
    invoke: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> VendorGrpcTransport:
    return VendorGrpcTransport(config, adapter=adapter, invoke=invoke)


def create_quirky_vendor_grpc_transport(
    config: VendorGrpcTransportConfig,
    *,
    invoke: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> VendorGrpcTransport:
    return VendorGrpcTransport(config, adapter=QuirkyVendorGrpcWireAdapter(config), invoke=invoke)


register_transport_factory(
    "vendor-grpc",
    lambda spec: create_vendor_grpc_transport(
        VendorGrpcTransportConfig(
            **{key: value for key, value in dict(spec.options).items() if key != "invoke"}
        ),
        invoke=dict(spec.options).get("invoke"),
    ),
)
register_transport_factory(
    "quirky-vendor-grpc",
    lambda spec: create_quirky_vendor_grpc_transport(
        VendorGrpcTransportConfig(
            **{key: value for key, value in dict(spec.options).items() if key != "invoke"}
        ),
        invoke=dict(spec.options).get("invoke"),
    ),
)


__all__ = [
    "QuirkyVendorGrpcWireAdapter",
    "VendorGrpcTransport",
    "VendorGrpcTransportConfig",
    "VendorGrpcWireAdapter",
    "create_quirky_vendor_grpc_transport",
    "create_vendor_grpc_transport",
]
