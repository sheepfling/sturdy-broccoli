"""Compatibility shim for the HLA 1516.1-2010 spec implementation.

New code should import from :mod:`hla2010.spec`.
"""
from __future__ import annotations

from ._spec_impl import *  # noqa: F401,F403
