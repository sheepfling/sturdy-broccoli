"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

Keep the top-level package intentionally small. Import detailed APIs from their
own modules rather than relying on a broad barrel import surface.
"""
from __future__ import annotations

from . import enums, exceptions, fom, handles, mom, rti, spec_refs, time, types
from .api import FederateAmbassador, RTIAmbassador, RTIambassador
from .enums import CallbackModel, SaveFailureReason
from .exceptions import RTIexception
from .handles import AttributeHandle

__version__ = "0.12.0"

__all__ = [
    "AttributeHandle",
    "CallbackModel",
    "FederateAmbassador",
    "RTIAmbassador",
    "RTIambassador",
    "RTIexception",
    "SaveFailureReason",
    "enums",
    "exceptions",
    "fom",
    "handles",
    "mom",
    "rti",
    "spec_refs",
    "time",
    "types",
]
