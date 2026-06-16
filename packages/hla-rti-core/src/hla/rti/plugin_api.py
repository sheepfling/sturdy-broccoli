"""Runtime-checkable spec, backend, and adapter plugin contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol, runtime_checkable


SPEC_ENTRY_POINT_GROUP = "hla.specs"
BACKEND_ENTRY_POINT_GROUP = "hla.rti_backends"
TRANSPORT_ENTRY_POINT_GROUP = "hla.transports"


@dataclass(frozen=True, slots=True)
class HLASpec:
    """One standard-facing HLA API family."""

    name: str
    year: int
    standard: str
    python_package: str
    java_package: str
    cpp_namespace: str
    aliases: tuple[str, ...] = ()
    capabilities: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class SpecPlugin:
    """Entry point descriptor for an installable HLA spec API."""

    spec: HLASpec
    description: str = ""


@dataclass(frozen=True, slots=True)
class TransportRequest:
    """Transport selection for backends that expose a transport layer."""

    name: str
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BackendRequest:
    """Backend selection bound to a concrete HLA spec."""

    spec: HLASpec
    transport: TransportRequest | None = None
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RTIBackendSpec:
    """Legacy backend selection value accepted by compatibility call sites."""

    kind: str = "python"
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RTITransportSpec:
    """Legacy transport selection value accepted by compatibility call sites."""

    kind: str = "subprocess-line"
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RTIBackendPlugin:
    """Entry point descriptor for an installable RTI backend."""

    name: str
    create_backend: Callable[[BackendRequest], Any]
    supports: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    family: str = "generic"
    description: str = ""
    discover: Callable[[], Any] | None = None


@dataclass(frozen=True, slots=True)
class RTIBackendDiscovery:
    """Discovery status for one installed RTI backend plugin."""

    name: str
    aliases: tuple[str, ...]
    family: str
    description: str
    supports: tuple[str, ...] = ()
    available: bool | None = None
    info: Any = None
    error: str | None = None


@runtime_checkable
class RTIambassadorLike(Protocol):
    """Structural RTI ambassador surface used by scenarios and plugin code."""

    def connect(self, *args: Any, **kwargs: Any) -> Any: ...

    def create_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...

    def join_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...

    def resign_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...

    def disconnect(self, *args: Any, **kwargs: Any) -> Any: ...

    def destroy_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...

    def evoke_multiple_callbacks(self, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class RTIBackendLike(Protocol):
    """Structural backend surface used by the delegating ambassador."""

    info: Any

    def start(self) -> Any: ...

    def invoke(self, invocation: Any) -> Any: ...

    def adapt_federate_ambassador(self, ambassador: Any) -> Any: ...

    def close(self) -> None: ...

    def translate_exception(
        self, exc: BaseException, invocation: Any
    ) -> BaseException: ...


@runtime_checkable
class RTIBackendPluginLike(Protocol):
    """Structural backend plugin descriptor used by registry discovery."""

    name: str
    aliases: tuple[str, ...]
    family: str
    description: str
    discover: Callable[[], Any] | None

    def create_backend(self, request: BackendRequest) -> Any: ...


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "BackendRequest",
    "HLASpec",
    "RTIBackendDiscovery",
    "RTIBackendLike",
    "RTIBackendPlugin",
    "RTIBackendPluginLike",
    "RTIBackendSpec",
    "RTITransportSpec",
    "RTIambassadorLike",
    "SPEC_ENTRY_POINT_GROUP",
    "SpecPlugin",
    "TRANSPORT_ENTRY_POINT_GROUP",
    "TransportRequest",
]
