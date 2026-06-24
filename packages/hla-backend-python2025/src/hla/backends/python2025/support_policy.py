"""Compatibility exports for support-policy runtime semantics."""

from __future__ import annotations

from .support_policy_runtime import (
    get_automatic_resign_directive,
    get_switch,
    normalize_service_group,
    safe_report_arg,
    serialize_mom_service_report,
    service_report_records_snapshot,
    set_attribute_scope_advisory_switch,
    set_automatic_resign_directive,
    set_switch,
)

__all__ = [
    "get_automatic_resign_directive",
    "get_switch",
    "normalize_service_group",
    "safe_report_arg",
    "serialize_mom_service_report",
    "service_report_records_snapshot",
    "set_attribute_scope_advisory_switch",
    "set_automatic_resign_directive",
    "set_switch",
]
