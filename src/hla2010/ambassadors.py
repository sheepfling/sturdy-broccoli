"""Reusable FederateAmbassador helpers for local RTI development.

The IEEE API leaves FederateAmbassador implementation to the federate developer;
these helpers make tests and small simulations easier while preserving the same
callback names used by Java/C++ RTIs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .runtime_api import FederateAmbassador
from .backends.base import CALLBACK_METHOD_NAMES, lower_camel_to_snake
from .spec_refs import SpecReference, method_reference


class NullFederateAmbassador(FederateAmbassador):
    """No-op FederateAmbassador implementation for tests and simple clients.

    This mirrors the common Java/C++ convenience pattern: a federate can inherit
    from this class and override only callbacks it cares about.  The base
    :class:`hla2010.api.FederateAmbassador` already provides no-op callback
    bodies; this named class makes that intent explicit in application code.
    """

    pass


@dataclass(frozen=True)
class CallbackRecord:
    """One RTI-initiated service invocation on a FederateAmbassador."""

    method_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    reference: SpecReference | None = None

    @property
    def snake_name(self) -> str:
        return lower_camel_to_snake(self.method_name)


class RecordingFederateAmbassador(FederateAmbassador):
    """FederateAmbassador that records every callback with its spec reference.

    Subclasses can implement ``on_<snake_case_callback>`` hooks.  The hook is
    called after the event is recorded.  This keeps examples readable while
    still exposing the raw callback stream for tests.
    """

    def __init__(self) -> None:
        self.records: list[CallbackRecord] = []

    @property
    def events(self) -> list[tuple[str, tuple[Any, ...]]]:
        """Backward-compatible event view used by earlier examples/tests."""
        return [(record.method_name, record.args) for record in self.records]

    def record_callback(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        record = CallbackRecord(method_name, tuple(args), dict(kwargs), method_reference(method_name))
        self.records.append(record)
        hook = getattr(self, f"on_{record.snake_name}", None)
        if callable(hook):
            return hook(*args, **kwargs)
        return None

    def clear(self) -> None:
        self.records.clear()

    def callbacks_named(self, method_name: str) -> list[CallbackRecord]:
        return [record for record in self.records if record.method_name == method_name or record.snake_name == method_name]

    def last_callback(self, method_name: str | None = None) -> CallbackRecord | None:
        if method_name is None:
            return self.records[-1] if self.records else None
        matches = self.callbacks_named(method_name)
        return matches[-1] if matches else None


def _make_callback(method_name: str) -> Callable[..., Any]:
    def _callback(self: RecordingFederateAmbassador, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback(method_name, *args, **kwargs)

    _callback.__name__ = method_name
    ref = method_reference(method_name)
    setattr(_callback, "spec_reference", ref)
    _callback.__doc__ = (
        f"Record FederateAmbassador callback {method_name}. "
        f"Spec reference: {ref.label}." if ref else f"Record FederateAmbassador callback {method_name}."
    )
    return _callback


for _method_name in CALLBACK_METHOD_NAMES:
    setattr(RecordingFederateAmbassador, _method_name, _make_callback(_method_name))
    setattr(RecordingFederateAmbassador, lower_camel_to_snake(_method_name), _make_callback(_method_name))


class FederateAmbassadorMultiplexer(FederateAmbassador):
    """Forward callbacks to multiple FederateAmbassador instances in order."""

    def __init__(self, ambassadors: Iterable[FederateAmbassador] = ()) -> None:
        self.ambassadors = list(ambassadors)

    def add(self, ambassador: FederateAmbassador) -> None:
        self.ambassadors.append(ambassador)

    def dispatch(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        for ambassador in list(self.ambassadors):
            getattr(ambassador, method_name)(*args, **kwargs)


def _make_mux_callback(method_name: str) -> Callable[..., Any]:
    def _callback(self: FederateAmbassadorMultiplexer, *args: Any, **kwargs: Any) -> Any:
        return self.dispatch(method_name, *args, **kwargs)

    _callback.__name__ = method_name
    ref = method_reference(method_name)
    setattr(_callback, "spec_reference", ref)
    _callback.__doc__ = (
        f"Forward FederateAmbassador callback {method_name}. "
        f"Spec reference: {ref.label}." if ref else f"Forward FederateAmbassador callback {method_name}."
    )
    return _callback


for _method_name in CALLBACK_METHOD_NAMES:
    setattr(FederateAmbassadorMultiplexer, _method_name, _make_mux_callback(_method_name))
    setattr(FederateAmbassadorMultiplexer, lower_camel_to_snake(_method_name), _make_mux_callback(_method_name))


__all__ = [
    "CallbackRecord",
    "NullFederateAmbassador",
    "FederateAmbassadorMultiplexer",
    "RecordingFederateAmbassador",
]
