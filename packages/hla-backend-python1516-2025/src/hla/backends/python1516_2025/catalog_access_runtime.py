"""Catalog and handle-access helpers for the dedicated Python 2025 lane."""

from __future__ import annotations

from typing import Any

from hla.rti1516_2025.exceptions import (
    FederateNotExecutionMember,
    FederationExecutionDoesNotExist,
    InvalidFOM,
)


def normalize_handle(handle: Any, expected_type: type[Any], exception_type: type[Exception]) -> int:
    if not isinstance(handle, expected_type):
        if type(handle).__name__ != expected_type.__name__:
            raise exception_type(f"Expected {expected_type.__name__}; got {type(handle).__name__}")
        value = getattr(handle, "value", None)
        if isinstance(value, int) and value >= 0:
            return value
        raise exception_type(f"Expected {expected_type.__name__}; got {type(handle).__name__}")
    value = getattr(handle, "value", None)
    if not isinstance(value, int) or value < 0:
        raise exception_type(f"Invalid {expected_type.__name__}: {handle!r}")
    return value


def federation_record(backend: Any) -> Any:
    backend._require_joined("FOM catalog access")
    if backend._federation_name is None:
        raise FederateNotExecutionMember("Cannot access FOM catalog before joinFederationExecution")
    federation = backend._FEDERATION_REGISTRY.get(backend._federation_name)
    if federation is None:
        raise FederationExecutionDoesNotExist(backend._federation_name)
    return federation


def catalog(backend: Any) -> Any:
    merged_catalog = federation_record(backend).fom_catalog
    if merged_catalog is None:
        raise InvalidFOM("Federation execution does not have a merged FOM catalog")
    return merged_catalog


def stable_handles(names: Any) -> dict[str, int]:
    return {name: index for index, name in enumerate(sorted(str(name) for name in names), start=1)}


def object_class_handles(backend: Any) -> dict[str, int]:
    return stable_handles(catalog(backend).object_classes)


def interaction_class_handles(backend: Any) -> dict[str, int]:
    return stable_handles(catalog(backend).interaction_classes)


def dimension_handles(backend: Any) -> dict[str, int]:
    return stable_handles(catalog(backend).dimensions)


def dimension_spec(backend: Any, dimension_name: str) -> Any | None:
    merged_catalog = catalog(backend)
    modules = tuple(getattr(merged_catalog, "modules", ()))
    mim_module = getattr(merged_catalog, "mim_module", None)
    if mim_module is not None:
        modules = (*modules, mim_module)
    for module in modules:
        spec = getattr(module, "dimension_specs", {}).get(dimension_name)
        if spec is not None:
            return spec
    return None


def dimension_default_upper_bound(backend: Any, dimension_name: str) -> int:
    spec = dimension_spec(backend, dimension_name)
    if spec is None or spec.upper_bound in {None, ""}:
        return (1 << 63) - 1
    try:
        return int(str(spec.upper_bound))
    except ValueError:
        return (1 << 63) - 1


def transportation_handles(backend: Any) -> dict[str, int]:
    names: set[str] = {str(name) for name in getattr(catalog(backend), "transportation_names", ())}
    names.update({"HLAreliable", "HLAbestEffort"})
    return stable_handles(names)


__all__ = [
    "catalog",
    "dimension_default_upper_bound",
    "dimension_handles",
    "dimension_spec",
    "federation_record",
    "interaction_class_handles",
    "normalize_handle",
    "object_class_handles",
    "stable_handles",
    "transportation_handles",
]
