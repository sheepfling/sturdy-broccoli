"""Explicit legacy aliases to the main Python 2025 runtime lane.

Deprecated: this module remains only until callers migrate off the shim
package root.
"""
from __future__ import annotations

from hla.backends.python2025.backend import (
    Python2025Backend,
    Python2025BackendInfo,
    Python2025BackendScaffold,
    Python2025RTIAmbassador,
    create_python2025_backend,
)

__all__ = [
    "Python2025Backend",
    "Python2025BackendInfo",
    "Python2025BackendScaffold",
    "Python2025RTIAmbassador",
    "create_python2025_backend",
]
