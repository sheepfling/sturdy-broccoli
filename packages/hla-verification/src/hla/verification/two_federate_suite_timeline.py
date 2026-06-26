"""Timeline recording helpers for the two-federate verification suite."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from hla.backends.common import CallbackRecord


@dataclass(frozen=True)
class TimelineEvent:
    sequence: int
    profile: str
    scenario: str
    role: str
    method_name: str
    snake_name: str
    reference: str


@dataclass
class TimelineRecorder:
    events: list[TimelineEvent]
    sequence: int = 0
    event_sink: Callable[[dict[str, Any]], None] | None = None

    def record(self, *, profile: str, scenario: str, role: str, callback: CallbackRecord) -> None:
        self.sequence += 1
        event = TimelineEvent(
            sequence=self.sequence,
            profile=profile,
            scenario=scenario,
            role=role,
            method_name=callback.method_name,
            snake_name=callback.snake_name,
            reference=callback.reference.label if callback.reference else "",
        )
        self.events.append(event)
        if self.event_sink is not None:
            self.event_sink(
                {
                    "kind": "callback",
                    "provider": "two-federate",
                    "profile": profile,
                    "scenario": scenario,
                    "role": role,
                    "callback": callback.method_name,
                    "callback_snake_name": callback.snake_name,
                    "reference": callback.reference.label if callback.reference else "",
                }
            )


__all__ = ["TimelineEvent", "TimelineRecorder"]
