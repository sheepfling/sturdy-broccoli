"""Backend-neutral RTI adapter plumbing.

The public HLA API surface is kept in :mod:`hla2010.api` and
:mod:`hla2010.raw_api`.  This module adds a narrow runtime adapter layer so the
same Python federate code can target different backends: a pure Python backend,
a Java RTI through JPype, a Java RTI through Py4J, or a future C++/wire adapter.

A backend only has to implement ``RTIBackend.invoke``.  ``DelegatingRTIAmbassador``
installs concrete implementations for every source-derived RTIambassador method
and forwards calls to that backend.
"""
from __future__ import annotations

from abc import ABC, abstractmethod, update_abstractmethods
from dataclasses import dataclass, field
import re
from types import TracebackType
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence

from ..api import FederateAmbassador, RTIambassador
from ..exceptions import RTIexception, RTIinternalError
from ..raw_api import API_METADATA
from ..spec_refs import method_reference

RTI_METHOD_NAMES: tuple[str, ...] = tuple(API_METADATA["RTIambassador"].keys())
CALLBACK_METHOD_NAMES: tuple[str, ...] = tuple(API_METADATA["FederateAmbassador"].keys())

_CAMEL_WORD_RE = re.compile(r"(?<!^)(?=[A-Z])")


def lower_camel_to_snake(name: str) -> str:
    """Convert a source HLA lowerCamelCase method name to snake_case.

    The IEEE Java API contains a few acronym-heavy names, notably
    ``getHLAversion``.  Normalize those before applying the generic split.
    """
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def snake_to_lower_camel(name: str) -> str:
    """Convert a snake_case method name to lowerCamelCase."""
    parts = name.split("_")
    if not parts:
        return name
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


@dataclass(frozen=True)
class Invocation:
    """A backend-neutral RTI service invocation.

    ``method_name`` is always the source lowerCamelCase RTIambassador name, even
    when the user called a Pythonic snake_case alias.
    """

    method_name: str
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    overloads: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class BackendInfo:
    """Descriptive information exposed by a backend."""

    name: str
    kind: str = "generic"
    version: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)


class BackendUnavailableError(RTIinternalError):
    """Raised when an optional backend dependency or runtime is unavailable."""


class BackendConversionError(RTIinternalError):
    """Raised when an adapter cannot convert a value across a backend boundary."""


class UnsupportedBackendService(RTIinternalError):
    """Raised when a backend cannot provide a requested HLA service."""


class RTIBackend(ABC):
    """Small interface implemented by concrete RTI backends.

    The backend layer deliberately does not mirror all 150+ HLA services.  It
    receives a single :class:`Invocation` object and may dispatch however its
    runtime requires.
    """

    info: BackendInfo

    def start(self) -> "RTIBackend":
        """Initialize backend resources.  The default backend has nothing to do."""
        return self

    @abstractmethod
    def invoke(self, invocation: Invocation) -> Any:
        """Invoke one RTIambassador service."""
        raise NotImplementedError

    def adapt_federate_ambassador(self, ambassador: FederateAmbassador) -> Any:
        """Return the backend representation for a Python federate ambassador.

        Generic backends can use the Python object directly.  Java backends
        override this to return a JPype JProxy or a Py4J callback object.
        """
        return ambassador

    def close(self) -> None:
        """Release backend resources."""
        return None

    def translate_exception(self, exc: BaseException, invocation: Invocation) -> RTIexception:
        """Convert an unexpected backend exception to the Python RTI hierarchy."""
        if isinstance(exc, RTIexception):
            return exc
        return RTIinternalError(
            f"{self.__class__.__name__} failed during {invocation.method_name}: {exc}",
            cause=exc,
        )


class DelegatingRTIAmbassador(RTIambassador):
    """Concrete RTIambassador that delegates every service to an ``RTIBackend``.

    This is the key abstraction point.  User code talks to this object using the
    normal HLA method names or the snake_case aliases.  Backend-specific code is
    kept behind ``RTIBackend``.
    """

    def __init__(self, backend: RTIBackend, *, start: bool = True):
        self.backend = backend
        if start:
            self.backend.start()

    @property
    def backend_info(self) -> BackendInfo:
        return getattr(self.backend, "info", BackendInfo(name=self.backend.__class__.__name__))

    def _invoke(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        if method_name not in API_METADATA["RTIambassador"]:
            raise UnsupportedBackendService(f"Unknown RTIambassador service: {method_name}")

        adapted_args = tuple(args)
        if method_name == "connect" and adapted_args:
            first = adapted_args[0]
            if isinstance(first, FederateAmbassador):
                adapted_args = (self.backend.adapt_federate_ambassador(first), *adapted_args[1:])

        invocation = Invocation(
            method_name=method_name,
            args=adapted_args,
            kwargs=dict(kwargs),
            overloads=tuple(API_METADATA["RTIambassador"].get(method_name, ())),
        )
        try:
            return self.backend.invoke(invocation)
        except RTIexception:
            raise
        except BaseException as exc:
            raise self.backend.translate_exception(exc, invocation) from exc

    def close(self) -> None:
        self.backend.close()

    def __enter__(self) -> "DelegatingRTIAmbassador":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.close()
        return False


# Install concrete lowerCamelCase implementations for every source-derived
# RTIambassador service.  The snake_case aliases already live on
# PythonicRTIAmbassadorMixin, so they automatically reach these methods.
def _make_forwarder(method_name: str) -> Callable[..., Any]:
    def _forwarder(self: DelegatingRTIAmbassador, *args: Any, **kwargs: Any) -> Any:
        return self._invoke(method_name, *args, **kwargs)

    _forwarder.__name__ = method_name
    _forwarder.__qualname__ = f"DelegatingRTIAmbassador.{method_name}"
    ref = method_reference(method_name)
    if ref is not None:
        _forwarder.__doc__ = (
            f"Delegate HLA RTI service {method_name} to the configured backend. "
            f"Spec reference: {ref.label}."
        )
    else:
        _forwarder.__doc__ = f"Delegate HLA RTI service {method_name} to the configured backend."
    _forwarder.spec_reference = ref  # type: ignore[attr-defined]
    return _forwarder


for _method_name in RTI_METHOD_NAMES:
    setattr(DelegatingRTIAmbassador, _method_name, _make_forwarder(_method_name))
update_abstractmethods(DelegatingRTIAmbassador)


class RecordingBackend(RTIBackend):
    """Tiny backend for tests and examples.

    It records invocations and returns values from a method-name keyed mapping.
    This lets us verify the adapter layer without an RTI installation.
    """

    def __init__(self, results: Mapping[str, Any] | None = None):
        self.info = BackendInfo(name="recording", kind="test")
        self.results: MutableMapping[str, Any] = dict(results or {})
        self.calls: list[Invocation] = []
        self.started = False
        self.closed = False

    def start(self) -> "RecordingBackend":
        self.started = True
        return self

    def invoke(self, invocation: Invocation) -> Any:
        self.calls.append(invocation)
        result = self.results.get(invocation.method_name)
        if callable(result):
            return result(invocation)
        return result

    def close(self) -> None:
        self.closed = True


def make_rti_ambassador(backend: RTIBackend, *, start: bool = True) -> DelegatingRTIAmbassador:
    """Create a backend-backed RTIambassador."""
    return DelegatingRTIAmbassador(backend, start=start)


__all__ = [
    "BackendConversionError",
    "BackendInfo",
    "BackendUnavailableError",
    "CALLBACK_METHOD_NAMES",
    "DelegatingRTIAmbassador",
    "Invocation",
    "RTIBackend",
    "RTI_METHOD_NAMES",
    "RecordingBackend",
    "UnsupportedBackendService",
    "lower_camel_to_snake",
    "make_rti_ambassador",
    "snake_to_lower_camel",
]
