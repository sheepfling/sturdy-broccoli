"""Pybind route helpers for the C++ shim contest backend."""
from __future__ import annotations

from typing import Any

from hla.rti.plugin_api import BackendRequest

from .backend import CppShimBackend, create_cpp_shim_backend
from .loader import BindingTarget, LoadedBinding, binding_target_from_options, load_binding


def create_pybind_backend(request: BackendRequest | None = None) -> Any:
    return create_cpp_shim_backend("pybind", request)


def load_pybind_binding(request: BackendRequest | None = None) -> LoadedBinding | None:
    options = dict(request.options if request is not None else {})
    target = binding_target_from_options(options)
    if target is None:
        return None
    return load_binding(target)


__all__ = [
    "BindingTarget",
    "CppShimBackend",
    "LoadedBinding",
    "create_pybind_backend",
    "load_pybind_binding",
]
