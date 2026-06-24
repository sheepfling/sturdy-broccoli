"""Compatibility wrapper for save/restore runtime semantics."""

from __future__ import annotations

from hla.backends.python1516_2025.save_restore_lifecycle import (
    abort_federation_restore,
    abort_federation_save,
    capture_federation_save_snapshot,
    complete_restore,
    complete_save,
    federate_save_begun,
    process_scheduled_save,
    query_federation_restore_status,
    query_federation_save_status,
    request_federation_restore,
    request_federation_save,
    restore_federation_save_snapshot,
    start_federation_save,
)

__all__ = [
    "abort_federation_restore",
    "abort_federation_save",
    "capture_federation_save_snapshot",
    "complete_restore",
    "complete_save",
    "federate_save_begun",
    "process_scheduled_save",
    "query_federation_restore_status",
    "query_federation_save_status",
    "request_federation_restore",
    "request_federation_save",
    "restore_federation_save_snapshot",
    "start_federation_save",
]
