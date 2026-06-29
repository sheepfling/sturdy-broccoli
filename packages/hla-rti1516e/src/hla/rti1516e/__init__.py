"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

The canonical standard-facing API lives at this package root.
"""
from __future__ import annotations

from .ambassadors import NullFederateAmbassador
from .enums import CallbackModel, OrderType, ResignAction, ServiceGroup
from .federate_ambassador import FederateAmbassador, lower_camel_to_snake
from .rti_ambassador import RTIambassador

__version__ = "0.13.0"


__all__ = [
    "CallbackModel",
    "FederateAmbassador",
    "NullFederateAmbassador",
    "OrderType",
    "RTIambassador",
    "ResignAction",
    "ServiceGroup",
    "__version__",
    "lower_camel_to_snake",
]
