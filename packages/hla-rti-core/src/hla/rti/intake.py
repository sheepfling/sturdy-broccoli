"""Shared artifact-intake status vocabulary and evidence helpers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


INTAKE_STATUS_LADDER = (
    "planned",
    "profile-valid",
    "discoverable",
    "header-green",
    "compile-green",
    "link-green",
    "capsule-built",
    "capsule-launch-green",
    "adapter-smoke-green",
    "factory-green",
    "ambassador-green",
    "connect-green",
    "callback-poll-green",
    "callback-green",
    "core-green",
    "trace-green",
    "behavior-blocked",
    "failed",
)


@dataclass(frozen=True, slots=True)
class IntakeArtifact:
    kind: str
    name: str
    edition: str
    route: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class IntakeCheck:
    name: str
    status: str
    message: str | None = None
    details: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return self.status in {
            "pass",
            "profile-valid",
            "discoverable",
            "header-green",
            "compile-green",
            "link-green",
            "capsule-built",
            "capsule-launch-green",
            "adapter-smoke-green",
            "factory-green",
            "ambassador-green",
            "connect-green",
            "callback-poll-green",
            "callback-green",
            "core-green",
            "trace-green",
        }

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def intake_status_from_checks(checks: tuple[IntakeCheck, ...], *, blocked: bool = False) -> str:
    if blocked:
        return "behavior-blocked"
    failed = [check for check in checks if check.status in {"fail", "failed"}]
    if failed:
        return "failed"
    green = [check.status for check in checks if check.status in INTAKE_STATUS_LADDER]
    if not green:
        return "planned"
    order = {status: index for index, status in enumerate(INTAKE_STATUS_LADDER)}
    return max(green, key=lambda status: order.get(status, -1))


__all__ = [
    "INTAKE_STATUS_LADDER",
    "IntakeArtifact",
    "IntakeCheck",
    "intake_status_from_checks",
]
