"""C++ shim RTI backends."""
from __future__ import annotations

from .backend import CppShimBackend, create_cpp_shim_backend
from .cpp_capsule_runtime import CAbiCapsuleClient, GrpcCapsuleClient, smoke_capsule
from .cpp_intake import CppSdkIntakeRequest, discover_cpp_sdk, generate_cpp_sdk_capsule, load_cpp_sdk_profile, write_cpp_intake_reports
from .loader import BindingTarget, LoadedBinding, binding_target_from_options, load_binding
from .plugin import backend_plugins, grpc_plugin, pybind_plugin
from .pybind_backend import create_pybind_backend, load_pybind_binding

__all__ = [
    "BindingTarget",
    "CAbiCapsuleClient",
    "CppShimBackend",
    "CppSdkIntakeRequest",
    "GrpcCapsuleClient",
    "LoadedBinding",
    "backend_plugins",
    "binding_target_from_options",
    "create_cpp_shim_backend",
    "create_pybind_backend",
    "discover_cpp_sdk",
    "generate_cpp_sdk_capsule",
    "grpc_plugin",
    "load_binding",
    "load_cpp_sdk_profile",
    "load_pybind_binding",
    "pybind_plugin",
    "smoke_capsule",
    "write_cpp_intake_reports",
]
