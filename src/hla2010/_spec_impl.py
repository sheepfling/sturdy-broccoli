"""Pythonic source-backed HLA 1516.1-2010 API spec.

This module is the clean, Python-facing contract layer.

The lowerCamelCase method names remain available for traceability and for
bridge compatibility, but the intended user-facing API is snake_case.

The method inventory comes from ``hla2010.spec_inventory``.  IEEE clause
references come from ``hla2010.spec_refs`` and the Java/C++ source locations
are surfaced directly in the method docstrings.
"""
from __future__ import annotations

from abc import ABC, abstractmethod, update_abstractmethods
import re
from typing import Callable

from .spec_inventory import FEDERATE_AMBASSADOR_METHODS, RTIAMBASSADOR_METHODS
from .spec_refs import method_reference
from .spec_sources import method_source_summary


def lower_camel_to_snake(name: str) -> str:
    """Convert a lowerCamelCase HLA method name to snake_case."""

    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def _attach_method_metadata(
    method: Callable[..., object],
    method_name: str,
    snake_name: str,
    *,
    abstract: bool,
    owner_name: str,
    ) -> Callable[..., object]:
    ref = method_reference(method_name)
    source_summary = method_source_summary(method_name)
    method.__name__ = snake_name if abstract else method_name
    method.__qualname__ = f"{owner_name}.{method.__name__}"
    doc_parts = [f"{snake_name} ({method_name})."]
    if ref is not None:
        doc_parts.append(f"IEEE reference: {ref.label}.")
    if source_summary:
        doc_parts.append(f"Sources: {source_summary}.")
    method.__doc__ = " ".join(doc_parts)
    setattr(method, "spec_reference", ref)
    setattr(method, "spec_source_summary", source_summary)
    if abstract:
        setattr(method, "__isabstractmethod__", True)
    return method


def _make_rti_abstract_method(method_name: str) -> Callable[..., object]:
    snake_name = lower_camel_to_snake(method_name)

    @abstractmethod
    def _method(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    return _attach_method_metadata(_method, method_name, snake_name, abstract=True, owner_name="RTIambassadorSpec")


def _make_rti_camel_alias(method_name: str) -> Callable[..., object]:
    snake_name = lower_camel_to_snake(method_name)

    def _method(self, *args: object, **kwargs: object) -> object:
        return getattr(self, snake_name)(*args, **kwargs)

    return _attach_method_metadata(_method, method_name, snake_name, abstract=False, owner_name="RTIambassadorSpec")


def _make_callback_method(method_name: str) -> Callable[..., object]:
    snake_name = lower_camel_to_snake(method_name)

    def _method(self, *args: object, **kwargs: object) -> object:
        return None

    return _attach_method_metadata(_method, method_name, snake_name, abstract=False, owner_name="FederateAmbassadorSpec")


def _make_callback_alias(method_name: str) -> Callable[..., object]:
    snake_name = lower_camel_to_snake(method_name)

    def _method(self, *args: object, **kwargs: object) -> object:
        return getattr(self, snake_name)(*args, **kwargs)

    return _attach_method_metadata(_method, method_name, snake_name, abstract=False, owner_name="FederateAmbassadorSpec")


class RTIambassadorSpec(ABC):
    """Pythonic abstract contract for an HLA RTI ambassador."""


class FederateAmbassadorSpec:
    """Pythonic no-op prototype base for federate callbacks."""


for _method_name in RTIAMBASSADOR_METHODS:
    _snake_name = lower_camel_to_snake(_method_name)
    setattr(RTIambassadorSpec, _snake_name, _make_rti_abstract_method(_method_name))
    if _snake_name != _method_name:
        setattr(RTIambassadorSpec, _method_name, _make_rti_camel_alias(_method_name))


for _method_name in FEDERATE_AMBASSADOR_METHODS:
    _snake_name = lower_camel_to_snake(_method_name)
    setattr(FederateAmbassadorSpec, _snake_name, _make_callback_method(_method_name))
    if _snake_name != _method_name:
        setattr(FederateAmbassadorSpec, _method_name, _make_callback_alias(_method_name))


update_abstractmethods(RTIambassadorSpec)

__all__ = [
    "FederateAmbassadorSpec",
    "RTIambassadorSpec",
    "lower_camel_to_snake",
]
