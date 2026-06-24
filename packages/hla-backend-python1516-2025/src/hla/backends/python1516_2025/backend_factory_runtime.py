"""Factory-facing backend wrappers for the live 2025 Python RTI lane."""

from __future__ import annotations

from importlib import import_module
from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from hla.backends.common import BackendInfo
from hla.rti.plugin_api import BackendRequest


@dataclass(frozen=True, slots=True)
class Python2025BackendInfo(BackendInfo):
    name: str = "python1516_2025-rti"
    kind: str = "python/2025"
    version: str = "0.13.0"
    details: dict[str, Any] = field(
        default_factory=lambda: {
            "spec": "rti1516_2025",
            "provider": "python1516_2025",
            "implementation_lane": "hla-backend-python1516-2025",
            "counts_as_python_2025_rti": True,
        }
    )


class Python2025Backend:
    """Factory-facing backend wrapper that returns a 2025-native ambassador."""

    info = Python2025BackendInfo()

    def __init__(self, request: BackendRequest):
        self.request = request

    def create_rti_ambassador(self):  # noqa: ANN201
        Python2025RTIAmbassador = import_module(
            "hla.backends.python1516_2025.backend"
        ).Python2025RTIAmbassador
        ambassador = Python2025RTIAmbassador()
        ambassador.backend_info = self.info
        return ambassador


class HostedPython2025Backend(Python2025Backend):
    """Factory-facing backend wrapper for the hosted FedPro transport route."""

    def __init__(self, request: BackendRequest, transport: Any):
        super().__init__(request)
        self.transport = transport

    def create_rti_ambassador(self):  # noqa: ANN201
        FedPro2025RTIAmbassador = import_module(
            "hla.backends.python1516_2025.hosted_fedpro"
        ).FedPro2025RTIAmbassador
        ambassador = FedPro2025RTIAmbassador(self.transport)
        ambassador.backend_info = replace(
            self.info,
            details={**dict(self.info.details), "wrapper_only": False},
        )
        return ambassador


def create_python2025_backend(request: BackendRequest) -> Python2025Backend:
    if request.spec.name != "rti1516_2025":
        raise ValueError(
            f"the current Python 2025 RTI backend only supports rti1516_2025, not {request.spec.name!r}"
        )
    options = dict(request.options)
    transport_spec = options.pop("transport", None)
    if transport_spec is not None:
        from hla.transports.common import coerce_transport_spec

        if isinstance(transport_spec, Mapping):
            transport_spec = dict(transport_spec)
            if "kind" in transport_spec or "options" in transport_spec:
                option_map = {
                    key: value for key, value in transport_spec.items() if key not in {"kind", "options"}
                }
                option_map.update(dict(transport_spec.get("options", {})))
                option_map.setdefault("schema", "rti1516_2025")
                transport_spec["options"] = option_map
                transport_spec.setdefault("kind", "grpc")
            else:
                transport_spec.setdefault("kind", "grpc")
                transport_spec.setdefault("schema", "rti1516_2025")
        transport = coerce_transport_spec(transport_spec)
        if transport is None:
            raise ValueError("backend='python1516_2025' received an empty transport specification")
        return HostedPython2025Backend(request, transport)
    if options:
        unsupported = ", ".join(sorted(options))
        raise ValueError(
            f"unsupported backend option(s) for backend='python1516_2025': {unsupported}; "
            "the in-process 2025 backend does not currently accept backend-specific factory options"
        )
    return Python2025Backend(request)
