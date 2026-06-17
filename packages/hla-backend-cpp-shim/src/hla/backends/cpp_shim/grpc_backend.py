"""gRPC route helpers for the C++ shim contest backend."""
from __future__ import annotations

from hla.rti.plugin_api import BackendRequest

from .backend import CppShimBackend, create_cpp_shim_backend


def create_grpc_backend(request: BackendRequest | None = None) -> CppShimBackend:
    return create_cpp_shim_backend("grpc", request)


__all__ = ["CppShimBackend", "create_grpc_backend"]
