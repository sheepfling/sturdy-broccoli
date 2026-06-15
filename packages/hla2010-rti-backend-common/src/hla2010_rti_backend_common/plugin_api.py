"""Runtime-checkable plugin and adapter surface contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol, runtime_checkable


BACKEND_ENTRY_POINT_GROUP = "hla.rti_backends"
LEGACY_BACKEND_ENTRY_POINT_GROUP = "hla2010.rti_backends"
BACKEND_ENTRY_POINT_GROUPS = (
    BACKEND_ENTRY_POINT_GROUP,
    LEGACY_BACKEND_ENTRY_POINT_GROUP,
)


@dataclass(frozen=True)
class RTIBackendSpec:
    """Backend selection for RTI ambassador factories."""

    kind: str = "python"
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RTITransportSpec:
    """Transport selection for backends that expose a transport layer."""

    kind: str = "subprocess-line"
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RTIBackendPlugin:
    """Entry point descriptor for an installable RTI backend."""

    name: str
    create_backend: Callable[[dict[str, Any]], Any]
    aliases: tuple[str, ...] = ()
    family: str = "generic"
    description: str = ""
    discover: Callable[[], Any] | None = None


@dataclass(frozen=True)
class RTIBackendDiscovery:
    """Discovery status for one installed RTI backend plugin."""

    name: str
    aliases: tuple[str, ...]
    family: str
    description: str
    selectable_names: tuple[str, ...] = ()
    probe_supported: bool = False
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

    def create_backend(self, options: dict[str, Any]) -> Any: ...


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "BACKEND_ENTRY_POINT_GROUPS",
    "LEGACY_BACKEND_ENTRY_POINT_GROUP",
    "RTIBackendDiscovery",
    "RTIBackendLike",
    "RTIBackendPlugin",
    "RTIBackendPluginLike",
    "RTIBackendSpec",
    "RTITransportSpec",
    "RTIambassadorLike",
]
