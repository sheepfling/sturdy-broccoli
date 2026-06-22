"""Compatibility-wrapper backend surface over the live Python 2025 RTI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.backends.common import BackendInfo
from hla.rti.plugin_api import BackendRequest

from .backend import Python2025Backend, Python2025RTIAmbassador


@dataclass(frozen=True, slots=True)
class ShimBackendInfo(BackendInfo):
    name: str = "shim-2025"
    kind: str = "shim/2025"
    version: str = "0.13.0"
    details: dict[str, Any] = field(
        default_factory=lambda: {
            "spec": "rti1516_2025",
            "provider": "shim",
            "implementation_lane": "hla-backend-python2025",
            "counts_as_python_2025_rti": False,
            "wrapper_only": True,
        }
    )


class Shim2025RTIAmbassador(Python2025RTIAmbassador):
    backend_info = ShimBackendInfo()


class Shim2025Backend(Python2025Backend):
    info = ShimBackendInfo()

    def create_rti_ambassador(self) -> Shim2025RTIAmbassador:
        ambassador = Shim2025RTIAmbassador()
        ambassador.backend_info = self.info
        return ambassador


def create_shim_backend(request: BackendRequest) -> Shim2025Backend:
    if request.spec.name != "rti1516_2025":
        raise ValueError(
            f"the current Python 2025 RTI backend only supports rti1516_2025, not {request.spec.name!r}"
        )
    options = dict(request.options)
    if "transport" in options:
        raise ValueError(
            "transport-hosted creation through backend='shim' is not implemented yet; "
            "the compatibility-wrapper lane does not own a hosted 2025 adapter and should not accept transport=..."
        )
    if options:
        unsupported = ", ".join(sorted(options))
        raise ValueError(
            f"unsupported backend option(s) for backend='shim': {unsupported}; "
            "the wrapper-only 2025 backend does not currently accept backend-specific factory options"
        )
    return Shim2025Backend(request)


__all__ = ["ShimBackendInfo", "Shim2025Backend", "Shim2025RTIAmbassador", "create_shim_backend"]
