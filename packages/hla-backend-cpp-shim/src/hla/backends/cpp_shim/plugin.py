"""Backend plugin descriptors for the C++ shim contest routes."""
from __future__ import annotations

from hla.backends.common import BackendInfo, RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest

from .backend import create_cpp_shim_backend
from .cpp_intake_backend import create_cpp_sdk_intake_backend, discover_cpp_sdk_backend
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
        RTIBackendPlugin(
            name="cpp-2010-sdk-pybind",
            aliases=(),
            family="intake/cpp",
            supports=("rti1516e",),
            description="Generic C++ 2010 SDK intake route through a generated pybind capsule.",
            create_backend=lambda request: create_cpp_sdk_intake_backend("2010", "pybind", request),
            discover=lambda: discover_cpp_sdk_backend("2010", "pybind"),
        ),
        RTIBackendPlugin(
            name="cpp-2010-sdk-grpc",
            aliases=(),
            family="intake/cpp",
            supports=("rti1516e",),
            description="Generic C++ 2010 SDK intake route through a generated gRPC capsule.",
            create_backend=lambda request: create_cpp_sdk_intake_backend("2010", "grpc", request),
            discover=lambda: discover_cpp_sdk_backend("2010", "grpc"),
        ),
        RTIBackendPlugin(
            name="cpp-2025-sdk-pybind",
            aliases=(),
            family="intake/cpp",
            supports=("rti1516_2025",),
            description="Generic C++ 2025 SDK intake route through a generated pybind capsule.",
            create_backend=lambda request: create_cpp_sdk_intake_backend("2025", "pybind", request),
            discover=lambda: discover_cpp_sdk_backend("2025", "pybind"),
        ),
        RTIBackendPlugin(
            name="cpp-2025-sdk-grpc",
            aliases=(),
            family="intake/cpp",
            supports=("rti1516_2025",),
            description="Generic C++ 2025 SDK intake route through a generated gRPC capsule.",
            create_backend=lambda request: create_cpp_sdk_intake_backend("2025", "grpc", request),
            discover=lambda: discover_cpp_sdk_backend("2025", "grpc"),
        ),
        pybind_plugin(),
        grpc_plugin(),
    )


def _plugin_by_name(name: str) -> RTIBackendPlugin:
    for item in backend_plugins():
        if item.name == name:
            return item
    raise KeyError(name)


def cpp_standard_2010_pybind_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-standard-2010-pybind")


def cpp_standard_2010_grpc_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-standard-2010-grpc")


def cpp_standard_2025_pybind_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-standard-2025-pybind")


def cpp_standard_2025_grpc_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-standard-2025-grpc")


def cpp_2010_sdk_pybind_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-2010-sdk-pybind")


def cpp_2010_sdk_grpc_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-2010-sdk-grpc")


def cpp_2025_sdk_pybind_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-2025-sdk-pybind")


def cpp_2025_sdk_grpc_plugin() -> RTIBackendPlugin:
    return _plugin_by_name("cpp-2025-sdk-grpc")


def plugin() -> RTIBackendPlugin:
    return pybind_plugin()


__all__ = [
    "backend_plugins",
    "cpp_2010_sdk_grpc_plugin",
    "cpp_2010_sdk_pybind_plugin",
    "cpp_2025_sdk_grpc_plugin",
    "cpp_2025_sdk_pybind_plugin",
    "cpp_standard_2010_grpc_plugin",
    "cpp_standard_2010_pybind_plugin",
    "cpp_standard_2025_grpc_plugin",
    "cpp_standard_2025_pybind_plugin",
    "grpc_plugin",
    "plugin",
    "pybind_plugin",
]
