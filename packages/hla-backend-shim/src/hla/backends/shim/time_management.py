"""Time-management helpers imported from the shared Python 2025 RTI runtime."""

from __future__ import annotations

from hla.backends.python1516_2025.time_management_runtime import (
    build_time_management_federation,
    build_time_management_state,
    deliver_due_tso_callbacks_for_request,
    disable_time_constrained,
    disable_time_regulation,
    enable_time_constrained,
    enable_time_regulation,
    modify_lookahead,
    process_time_advances,
    query_galt_for,
    query_lits_for,
    query_lookahead,
    request_time_advance,
    retract_message,
    try_grant_pending_time_advance,
    validate_tso_send_time,
)
