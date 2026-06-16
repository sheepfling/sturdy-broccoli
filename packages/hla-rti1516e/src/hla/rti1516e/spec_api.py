"""Compatibility shim for the HLA 1516.1-2010 spec implementation.

New code should import from :mod:`hla.rti1516e.spec`.
"""
from __future__ import annotations

from ._spec_impl import FederateAmbassadorSpec, RTIambassadorSpec, lower_camel_to_snake

__all__ = [
    "FederateAmbassadorSpec",
    "RTIambassadorSpec",
    "lower_camel_to_snake",
]
