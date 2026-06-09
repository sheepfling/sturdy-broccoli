"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

Keep the top-level package intentionally small. New code should import the
clean spec layer first, and reach for the runtime facade only when it needs a
concrete adapter surface.
"""
from __future__ import annotations

from . import enums, exceptions, fom, handles, mom, rti, spec_refs, time, types
from .enums import CallbackModel, SaveFailureReason
from .exceptions import RTIexception
from .handles import AttributeHandle

__version__ = "0.12.0"

__all__ = [
    "AttributeHandle",
    "CallbackModel",
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
