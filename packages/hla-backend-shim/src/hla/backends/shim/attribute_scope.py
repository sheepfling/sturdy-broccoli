"""Legacy-package re-export for the live Python 2025 RTI attribute-scope helpers."""

from __future__ import annotations

from hla.backends.python2025.attribute_scope_runtime import (
    deliver_forced_remove_callbacks,
    evaluate_attribute_scope_advisories,
)

__all__ = [
    "deliver_forced_remove_callbacks",
    "evaluate_attribute_scope_advisories",
]
