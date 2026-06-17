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
    """Backend wrapper that exposes the 2025 shim through a C++ route name."""

    def __init__(self, route: str, request: BackendRequest):
        self.route = route
        self.request = request
        self.info = CppRouteBackendInfo(
            name=f"cpp-shim-{route}",
            kind=f"cpp/{route}/shim",
            details={"route": route, "spec": "rti1516_2025", "implementation": "2025 Python shim"},
        )

    def create_rti_ambassador(self) -> Any:
        from hla.backends.shim.backend import create_shim_backend

        native_backend = create_shim_backend(self.request)
        ambassador = native_backend.create_rti_ambassador()
        ambassador.backend_info = self.info
        return ambassador


__all__ = ["CppRouteBackendInfo", "CppRouteShim2025Backend"]
