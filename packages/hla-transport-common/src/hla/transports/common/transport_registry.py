"""Shared transport registry for backend adapters."""
from __future__ import annotations

import importlib
from typing import Any, Mapping

from hla.backends.common.plugin_api import RTITransportSpec
from .transport import SubprocessLineTransport

_TRANSPORT_FACTORIES: dict[str, Any] = {}
_TRANSPORT_MODULES: dict[str, str] = {
    "grpc": "hla.transports.grpc.transport",
    "http-json": "hla.transports.rest",
    "rest": "hla.transports.rest",
}


def _normalize_kind(kind: str) -> str:
    return kind.strip().lower().replace("_", "-")


def register_transport_factory(kind: str, factory: Any) -> None:
    """Register a transport factory for a normalized transport kind."""

    _TRANSPORT_FACTORIES[_normalize_kind(kind)] = factory


def coerce_transport_spec(value: Any):
    """Create a transport instance from a transport selection value."""

    if value is None:
        return None
    if hasattr(value, "request") and hasattr(value, "start"):
        return value
    if isinstance(value, RTITransportSpec):
        spec = value
    elif isinstance(value, Mapping):
        if "kind" in value or "options" in value:
            spec = RTITransportSpec(
                kind=value.get("kind", "subprocess-line"),
                options=value.get("options", {k: v for k, v in value.items() if k not in {"kind", "options"}}),
            )
        else:
            raise TypeError(f"Unsupported transport specification mapping: {value!r}")
    elif isinstance(value, str):
        spec = RTITransportSpec(kind=value)
    else:
        raise TypeError(f"Unsupported transport specification: {value!r}")

    normalized = _normalize_kind(spec.kind)
    factory = _TRANSPORT_FACTORIES.get(normalized)
    if factory is None:
        module_name = _TRANSPORT_MODULES.get(normalized)
        if module_name is not None:
            importlib.import_module(module_name)
            factory = _TRANSPORT_FACTORIES.get(normalized)
    if factory is not None:
        return factory(spec)
    if normalized in {"subprocess", "subprocess-line", "stdio", "pipe"}:
        return SubprocessLineTransport(**dict(spec.options))
    raise ValueError(f"Unknown transport kind: {spec.kind!r}")


__all__ = ["RTITransportSpec", "coerce_transport_spec", "register_transport_factory"]
