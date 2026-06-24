"""2025 C++-route shim wrappers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti.plugin_api import BackendRequest


@dataclass(frozen=True, slots=True)
class CppRouteBackendInfo:
    name: str
    kind: str
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=dict)


class CppRouteShim2025Backend:
    """Backend wrapper that exposes the current Python 2025 RTI through a C++ route name."""

    def __init__(self, route: str, request: BackendRequest):
        self.route = route
        self.request = request
        self.info = CppRouteBackendInfo(
            name=f"cpp-shim-{route}",
            kind=f"cpp/{route}/shim",
            details={
                "route": route,
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
        ambassador.backend_info = CppRouteBackendInfo(
            name=self.info.name,
            kind=self.info.kind,
            version=native_info.version,
            details={**dict(native_info.details), **dict(self.info.details)},
        )
        return ambassador


__all__ = ["CppRouteBackendInfo", "CppRouteShim2025Backend"]
