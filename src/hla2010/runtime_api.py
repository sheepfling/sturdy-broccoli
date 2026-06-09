"""Runtime-facing Pythonic HLA API facade.

The clean abstract/prototype contract lives in :mod:`hla2010.spec`.
This module keeps the concrete Python runtime convenience layer for adapters
and existing users that want snake_case methods over the source names.
"""
from __future__ import annotations

from typing import Callable

from .spec_inventory import RTIAMBASSADOR_METHODS
from ._spec_impl import FederateAmbassadorSpec, RTIambassadorSpec, lower_camel_to_snake


def _make_forwarder(method_name: str) -> Callable[..., object]:
    snake_name = lower_camel_to_snake(method_name)

    def _method(self, *args: object, **kwargs: object) -> object:
        return getattr(self, method_name)(*args, **kwargs)

    _method.__name__ = snake_name
    _method.__qualname__ = f"PythonicRTIAmbassadorMixin.{snake_name}"
    _method.__doc__ = f"Forward the Pythonic alias `{snake_name}` to `{method_name}`."
    return _method


class PythonicRTIAmbassadorMixin:
    """Mixin that forwards snake_case RTI service names to source names."""


for _method_name in RTIAMBASSADOR_METHODS:
    _snake_name = lower_camel_to_snake(_method_name)
    if _snake_name != _method_name:
        setattr(PythonicRTIAmbassadorMixin, _snake_name, _make_forwarder(_method_name))


class RTIambassador(PythonicRTIAmbassadorMixin, RTIambassadorSpec):
    """Concrete subclass point for Python RTI adapters."""


RTIAmbassador = RTIambassador


class FederateAmbassador(FederateAmbassadorSpec):
    """Prototype base for federate callback implementations."""


NullFederateAmbassador = FederateAmbassador

__all__ = [
    "FederateAmbassador",
    "NullFederateAmbassador",
    "PythonicRTIAmbassadorMixin",
    "RTIAmbassador",
    "RTIambassador",
]
