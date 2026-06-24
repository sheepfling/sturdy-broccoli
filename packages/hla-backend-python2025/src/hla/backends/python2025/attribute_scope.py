"""Compatibility exports for attribute-scope runtime semantics."""

from __future__ import annotations

from .attribute_scope_runtime import deliver_forced_remove_callbacks, evaluate_attribute_scope_advisories

__all__ = [
    "deliver_forced_remove_callbacks",
    "evaluate_attribute_scope_advisories",
]
