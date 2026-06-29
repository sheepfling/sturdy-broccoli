"""Entry point descriptor for the generic Py4J Java RTI backend."""
from __future__ import annotations

import importlib.util
from typing import Any

from hla.bridges.java.common import BackendInfo, RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest

from .factory import create_py4j_backend
from .runtime import Py4JConfig


def _optional_module_info(module_name: str, *, name: str, kind: str) -> BackendInfo | None:
    if importlib.util.find_spec(module_name) is None:
        return None
    return BackendInfo(name=name, kind=kind, details={"python_module": module_name})


def _py4j_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options)
    options.setdefault("java_api_profile", request.spec.name)
    config = options.pop("config", None) or Py4JConfig(**options)
    return create_py4j_backend(config)


def py4j_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e", "rti1516_2025"),
        name="py4j",
        aliases=("java-py4j",),
        family="java",
        description="Generic Java RTI adapter through Py4J.",
        create_backend=_py4j_backend_factory,
        discover=lambda: _optional_module_info("py4j", name="Py4J", kind="java/py4j"),
    )


def plugin() -> RTIBackendPlugin:
    return py4j_plugin()


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin", "py4j_plugin"]
