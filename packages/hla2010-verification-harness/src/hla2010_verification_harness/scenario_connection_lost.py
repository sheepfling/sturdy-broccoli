"""Federate connection-lost callback verification scenario."""
from __future__ import annotations

from typing import Any, Callable


def run_connection_lost_callback_scenario(
    invoke_callback: Callable[[str], Any],
    *,
    federate: Any,
    fault_description: str = "simulated connection lost",
) -> dict[str, Any]:
    invoke_callback(fault_description)
    record = federate.last_callback("connectionLost")
    assert record is not None
    assert record.args == (fault_description,)
    assert federate.last_callback("connection_lost") is record
    return {
        "fault_description": fault_description,
        "record": record,
    }


__all__ = ["run_connection_lost_callback_scenario"]
