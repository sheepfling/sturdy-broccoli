"""Timeline recording helpers for the two-federate verification suite."""
from __future__ import annotations

from dataclasses import dataclass

from hla2010.ambassadors import CallbackRecord


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

    def record(self, *, profile: str, scenario: str, role: str, callback: CallbackRecord) -> None:
        self.sequence += 1
        self.events.append(
            TimelineEvent(
                sequence=self.sequence,
                profile=profile,
                scenario=scenario,
                role=role,
                method_name=callback.method_name,
                snake_name=callback.snake_name,
                reference=callback.reference.label if callback.reference else "",
            )
        )


__all__ = ["TimelineEvent", "TimelineRecorder"]
