"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

The canonical standard-facing API lives at this package root.
"""
from __future__ import annotations

from .federate_ambassador import FederateAmbassador, NullFederateAmbassador, lower_camel_to_snake
from .rti_ambassador import RTIambassador
from .enums import CallbackModel, OrderType, ResignAction, ServiceGroup

__version__ = "0.13.0"


def __getattr__(name: str):
    if name in {"RtiFactory", "create_rti_ambassador"}:
        from .factory import RtiFactory, create_rti_ambassador

        return {"RtiFactory": RtiFactory, "create_rti_ambassador": create_rti_ambassador}[name]
    raise AttributeError(name)

__all__ = [
    "CallbackModel",
    "FederateAmbassador",
    "NullFederateAmbassador",
    "OrderType",
    "RTIambassador",
    "ResignAction",
    "RtiFactory",
    "ServiceGroup",
    "__version__",
    "create_rti_ambassador",
    "lower_camel_to_snake",
]
