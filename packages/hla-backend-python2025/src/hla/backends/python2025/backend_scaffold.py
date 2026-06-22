"""Historical pre-promotion scaffold retained only as an archival reference."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.backends.common import BackendInfo, BackendUnavailableError, Invocation, RTIBackend
from hla.rti.plugin_api import BackendRequest


@dataclass(frozen=True, slots=True)
class Python2025BackendInfo(BackendInfo):
    """Historical metadata for the archived pre-promotion scaffold."""

    name: str = "python2025"
    kind: str = "python/2025/historical-scaffold"
    version: str = "0.13.0"
    details: dict[str, Any] = field(
        default_factory=lambda: {
            "spec": "rti1516_2025",
            "state": "historical-scaffold-archived",
            "note": "The live 2025 Python RTI now executes from hla.backends.python2025.backend; this file is retained only as a historical pre-promotion scaffold reference.",
        }
    )


class Python2025BackendScaffold(RTIBackend):
    """Archived scaffold stub retained so the old transition artifact stays explicit."""

    def __init__(self, request: BackendRequest):
        self.request = request
        self.info = Python2025BackendInfo()

    def invoke(self, invocation: Invocation) -> Any:
        raise BackendUnavailableError(
            "backend_scaffold.py is a historical artifact only; "
            "the live 2025 Python RTI executes from hla.backends.python2025.backend."
        )

    def create_rti_ambassador(self) -> Any:
        raise BackendUnavailableError(
            "backend_scaffold.py is a historical artifact only; "
            "use backend='python2025' for the main 2025 Python RTI implementation."
        )


def create_python2025_backend(request: BackendRequest) -> Python2025BackendScaffold:
    return Python2025BackendScaffold(request)


__all__ = [
    "Python2025BackendInfo",
    "Python2025BackendScaffold",
    "create_python2025_backend",
]
