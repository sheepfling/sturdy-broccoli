"""Input coercion and guard helpers for the dedicated Python 2025 lane."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.exceptions import (
    FederateNotExecutionMember,
    InvalidLogicalTime,
    InvalidLookahead,
    NotConnected,
    RestoreInProgress,
    RTIinternalError,
    SaveInProgress,
)


def require_connected(backend: Any, method_name: str) -> None:
    if not backend._connected:
        raise NotConnected(f"Cannot call {method_name} before connect")


def require_joined(backend: Any, method_name: str) -> None:
    require_connected(backend, method_name)
    if not backend._joined:
        raise FederateNotExecutionMember(f"Cannot call {method_name} before joinFederationExecution")


def require_no_save_or_restore(backend: Any, method_name: str) -> None:
    federation = backend._federation_record()
    if federation.save_label is not None:
        raise SaveInProgress(f"A federation save is already in progress during {method_name}")
    if federation.restore_label is not None:
        raise RestoreInProgress(f"A federation restore is already in progress during {method_name}")


def normalize_reserved_object_instance_name(object_instance_name: Any, *, method_name: str) -> str:
    if not isinstance(object_instance_name, str) or not object_instance_name:
        raise RTIinternalError(f"{method_name} requires non-empty object instance names")
    return object_instance_name


def normalize_reserved_object_instance_name_set(
    object_instance_names: Any,
    *,
    method_name: str,
) -> set[str]:
    if isinstance(object_instance_names, str):
        raise RTIinternalError(f"{method_name} requires a non-empty set of object instance names")
    try:
        names = set(object_instance_names)
    except TypeError as exc:
        raise RTIinternalError(f"{method_name} requires a non-empty set of object instance names") from exc
    if not names:
        raise RTIinternalError(f"{method_name} requires a non-empty set of object instance names")
    return {
        normalize_reserved_object_instance_name(name, method_name=method_name)
        for name in names
    }


def normalize_object_class_subscription_args(object_class=None, attributes=None, **kwargs):  # noqa: ANN001, ANN205
    if object_class is None:
        object_class = kwargs.pop("the_class", None)
    if attributes is None:
        attributes = kwargs.pop("attribute_list", None)
    if kwargs:
        unexpected = ", ".join(sorted(kwargs))
        raise TypeError(f"Unexpected keyword arguments: {unexpected}")
    if object_class is None or attributes is None:
        raise TypeError("object_class/the_class and attributes/attribute_list are required")
    return object_class, attributes


def coerce_time(backend: Any, value: Any) -> Any:
    factory = backend._logical_time_factory
    time_type = getattr(factory, "time_type", None)
    if time_type is not None and isinstance(value, time_type):
        return value
    if hasattr(value, "getValue"):
        value = value.getValue()
    elif hasattr(value, "value"):
        value = value.value
    try:
        return factory.makeTime(value)
    except Exception as exc:
        raise InvalidLogicalTime(repr(value)) from exc


def coerce_interval(backend: Any, value: Any) -> Any:
    factory = backend._logical_time_factory
    interval_type = getattr(factory, "interval_type", None)
    if interval_type is not None and isinstance(value, interval_type):
        return value
    if hasattr(value, "getValue"):
        value = value.getValue()
    elif hasattr(value, "value"):
        value = value.value
    try:
        return factory.makeInterval(value)
    except Exception as exc:
        raise InvalidLookahead(repr(value)) from exc


__all__ = [
    "coerce_interval",
    "coerce_time",
    "normalize_object_class_subscription_args",
    "normalize_reserved_object_instance_name",
    "normalize_reserved_object_instance_name_set",
    "require_connected",
    "require_joined",
    "require_no_save_or_restore",
]
