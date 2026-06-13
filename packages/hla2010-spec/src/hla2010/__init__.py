"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

Keep the top-level package intentionally lightweight. Import concrete submodules
directly so package import does not pull in FOM parsing, MOM tables, RTI
factories, or backend plugin machinery.
"""
from __future__ import annotations

__version__ = "0.13.0"

__all__ = [
    "__version__",
]
