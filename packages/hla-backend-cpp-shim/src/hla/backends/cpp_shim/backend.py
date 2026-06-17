"""Stub C++ shim backend implementation."""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

from hla.backends.common import BackendInfo, RecordingBackend
from hla.rti.plugin_api import BackendRequest

from .loader import LoadedBinding, binding_target_from_options, load_binding


@dataclass(frozen=True, slots=True)
class CppShimBackendConfig:
    route: str = "pybind"
    kernel: str = "stub"
    binding: LoadedBinding | None = None
    details: dict[str, Any] = field(default_factory=dict)


class CppShimBackend(RecordingBackend):
    """Small backend wrapper used to exercise the C++ shim route names."""

    def __init__(self, config: CppShimBackendConfig):
        super().__init__()
        self.config = config
        self.info = BackendInfo(
            name=f"cpp-shim-{config.route}",
            kind=f"cpp/{config.route}/shim",
            details={
                "route": config.route,
                "kernel": config.kernel,
                **({"binding": dict(config.binding.details), "binding_kind": config.binding.kind} if config.binding is not None else {}),
                **dict(config.details),
            },
        )


def _call_binding_factory(factory: Any, request: BackendRequest | None) -> Any | None:
    if not callable(factory):
        return None

    try:
        signature = inspect.signature(factory)
    except (TypeError, ValueError):
        signature = None

    if signature is None:
        try:
            return factory(request)
        except TypeError:
            return factory()

    parameters = tuple(signature.parameters.values())
    if not parameters:
        return factory()
    if len(parameters) == 1:
        return factory(request)
    return factory(request)


def create_cpp_shim_backend(route: str, request: BackendRequest | None = None) -> Any:
    if request is not None and request.spec.name == "rti1516_2025":
        from .backend_2025 import CppRouteShim2025Backend

        return CppRouteShim2025Backend(route, request)
    if request is not None and request.spec.name != "rti1516e":
        raise ValueError(f"C++ shim route does not support HLA spec {request.spec.name!r}")

    options = dict(request.options if request is not None else {})
    kernel = str(options.pop("kernel", "stub"))
    binding_target = binding_target_from_options(options)
    binding = load_binding(binding_target) if binding_target is not None else None
    factory = None if binding is None else binding.resolve_callable("create_backend", "create_pybind_backend", "create_kernel")
    created = _call_binding_factory(factory, request) if factory is not None else None

    if isinstance(created, RecordingBackend):
        return created
    if hasattr(created, "info") and hasattr(created, "invoke"):
        return created

    config = CppShimBackendConfig(route=route, kernel=kernel, binding=binding, details=options)
    return CppShimBackend(config)


__all__ = ["CppShimBackend", "CppShimBackendConfig", "create_cpp_shim_backend"]
