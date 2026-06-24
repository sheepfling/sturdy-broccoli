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
    """Backend wrapper that exposes the current Python 2025 RTI through a Java route name."""

    def __init__(self, profile: str, request: Any):
        self.profile = profile
        self.request = request
        self.info = RouteBackendInfo(
            name=f"java-shim-{profile}",
            kind=f"java/{profile}/shim",
            details={
                "profile": profile,
                "spec": "rti1516_2025",
                "implementation": "2025 Python RTI lane",
                "runtime_provider": "python1516_2025",
                "implementation_lane": "hla-backend-python2025",
                "counts_as_python_2025_rti": False,
                "wrapper_only": False,
            },
        )

    def create_rti_ambassador(self) -> Any:
        from hla.backends.python2025.backend import create_python2025_backend

        native_backend = create_python2025_backend(self.request)
        ambassador = native_backend.create_rti_ambassador()
        native_info = ambassador.backend_info
        ambassador.backend_info = RouteBackendInfo(
            name=self.info.name,
            kind=self.info.kind,
            version=native_info.version,
            details={**dict(native_info.details), **dict(self.info.details)},
        )
        return ambassador


__all__ = ["JavaRouteShim2025Backend", "RouteBackendInfo"]
