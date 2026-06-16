"""Shared callback-recording ambassador helpers for split packages."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hla.rti1516e.spec import FederateAmbassadorSpec
from hla.rti1516e.spec_refs import SpecReference, method_reference

from .base import CALLBACK_METHOD_NAMES, lower_camel_to_snake

_CALLBACK_BY_SNAKE = {
    lower_camel_to_snake(method_name): method_name
    for method_name in CALLBACK_METHOD_NAMES
}


@dataclass(frozen=True)
class CallbackRecord:
    """One RTI-initiated callback captured from a federate ambassador."""

    method_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    reference: SpecReference | None = None

    @property
    def snake_name(self) -> str:
        return lower_camel_to_snake(self.method_name)


class RecordingFederateAmbassador(FederateAmbassadorSpec):
    """Federate ambassador that records callbacks with spec references."""

    def __init__(self) -> None:
        self.records: list[CallbackRecord] = []

    @property
    def events(self) -> list[tuple[str, tuple[Any, ...]]]:
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
        return [
            record
            for record in self.records
            if record.method_name == method_name or record.snake_name == method_name
        ]

    def last_callback(self, method_name: str | None = None) -> CallbackRecord | None:
        if method_name is None:
            return self.records[-1] if self.records else None
        matches = self.callbacks_named(method_name)
        return matches[-1] if matches else None

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        if name in {"records", "events", "record_callback", "clear", "callbacks_named", "last_callback", "__class__"}:
            return attr

        method_name = name if name in CALLBACK_METHOD_NAMES else _CALLBACK_BY_SNAKE.get(name)
        if method_name is None:
            return attr

        owner_attr = getattr(type(self), name, None)
        base_attr = getattr(FederateAmbassadorSpec, name, None)
        if owner_attr is not None and owner_attr is not base_attr:
            return attr

        return lambda *args, **kwargs: self.record_callback(method_name, *args, **kwargs)


__all__ = [
    "CallbackRecord",
    "RecordingFederateAmbassador",
]
