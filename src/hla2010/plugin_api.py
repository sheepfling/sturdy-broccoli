"""Runtime-checkable plugin and adapter surface contracts.

The clean abstract spec lives in :mod:`hla2010.spec`. This module carries the
structural protocols that are convenient at integration boundaries, where
callers may want to validate shape without forcing inheritance from the spec
ABCs.
"""
from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable


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
    "RTIBackendLike",
    "RTIBackendPluginLike",
    "RTIambassadorLike",
]
