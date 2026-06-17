"""Backend plugin descriptors for the C++ shim contest routes."""
from __future__ import annotations

from hla.backends.common import BackendInfo, RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest

from .backend import create_cpp_shim_backend
from .pybind_backend import create_pybind_backend
from .standard import create_cpp_standard_backend, discover_cpp_standard


def _discover(route: str) -> BackendInfo:
    return BackendInfo(
        name=f"cpp-shim-{route}",
        kind=f"cpp/{route}/shim",
        details={"route": route, "implementation": "python skeleton"},
    )


def pybind_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="cpp-shim-pybind",
        aliases=("cpp-shim", "native-cpp-shim", "cpp-shim-native"),
        family="cpp-shim",
        supports=("rti1516e", "rti1516_2025"),
        description="C++ shim contest backend exposed through a pybind11 route.",
        create_backend=create_pybind_backend,
        discover=lambda: _discover("pybind"),
    )


def grpc_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="cpp-shim-grpc",
        aliases=("cpp-shim-sidecar", "native-cpp-shim-grpc"),
        family="cpp-shim",
        supports=("rti1516e", "rti1516_2025"),
        description="C++ shim contest backend exposed through a gRPC sidecar route.",
        create_backend=lambda request: create_cpp_shim_backend("grpc", request),
        discover=lambda: _discover("grpc"),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (
        RTIBackendPlugin(
            name="cpp-standard-2010-pybind",
            aliases=(),
            family="standard/cpp",
            supports=("rti1516e",),
            description="HLA-X C++ 2010 standard shim artifact through the pybind route.",
            create_backend=lambda request: create_cpp_standard_backend("pybind", request),
            discover=lambda: discover_cpp_standard("pybind", "2010"),
        ),
        RTIBackendPlugin(
            name="cpp-standard-2010-grpc",
            aliases=(),
            family="standard/cpp",
            supports=("rti1516e",),
            description="HLA-X C++ 2010 standard shim artifact through the gRPC route.",
            create_backend=lambda request: create_cpp_standard_backend("grpc", request),
            discover=lambda: discover_cpp_standard("grpc", "2010"),
        ),
        RTIBackendPlugin(
            name="cpp-standard-2025-pybind",
            aliases=(),
            family="standard/cpp",
            supports=("rti1516_2025",),
            description="HLA-X C++ 2025 standard shim artifact through the pybind route.",
            create_backend=lambda request: create_cpp_standard_backend("pybind", request),
            discover=lambda: discover_cpp_standard("pybind", "2025"),
        ),
        RTIBackendPlugin(
            name="cpp-standard-2025-grpc",
            aliases=(),
            family="standard/cpp",
            supports=("rti1516_2025",),
            description="HLA-X C++ 2025 standard shim artifact through the gRPC route.",
            create_backend=lambda request: create_cpp_standard_backend("grpc", request),
            discover=lambda: discover_cpp_standard("grpc", "2025"),
        ),
        pybind_plugin(),
        grpc_plugin(),
    )


def plugin() -> RTIBackendPlugin:
    return pybind_plugin()


__all__ = ["backend_plugins", "grpc_plugin", "plugin", "pybind_plugin"]
