"""Legacy-package re-export for the live Python 2025 RTI update-rate runtime."""

from __future__ import annotations

from hla.backends.python2025.update_rate_runtime import (
    apply_update_rate_reduction_for_subscriber,
    default_update_rate_designator_for_attribute,
    default_update_rate_for_attribute,
    get_update_rate_value,
    resolve_update_rate_designator,
    subscribed_update_rate_for_attribute,
    time_scalar,
)

__all__ = [
    "apply_update_rate_reduction_for_subscriber",
    "default_update_rate_designator_for_attribute",
    "default_update_rate_for_attribute",
    "get_update_rate_value",
    "resolve_update_rate_designator",
    "subscribed_update_rate_for_attribute",
    "time_scalar",
]
