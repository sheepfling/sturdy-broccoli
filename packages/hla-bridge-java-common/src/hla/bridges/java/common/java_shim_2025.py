"""2025 Java-route shim wrappers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RouteBackendInfo:
    name: str
    kind: str
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=dict)


class JavaRouteShim2025Backend:
    """Backend wrapper that exposes the 2025 shim through a Java route name."""

    def __init__(self, profile: str, request: Any):
        self.profile = profile
        self.request = request
        self.info = RouteBackendInfo(
            name=f"java-shim-{profile}",
            kind=f"java/{profile}/shim",
            details={"profile": profile, "spec": "rti1516_2025", "implementation": "2025 Python shim"},
        )

    def create_rti_ambassador(self) -> Any:
        from hla.backends.shim.backend import create_shim_backend

        native_backend = create_shim_backend(self.request)
        ambassador = native_backend.create_rti_ambassador()
        ambassador.backend_info = self.info
        return ambassador


__all__ = ["JavaRouteShim2025Backend", "RouteBackendInfo"]
