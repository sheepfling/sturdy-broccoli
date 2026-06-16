"""Entry point descriptor for the generic JPype Java RTI backend."""
from __future__ import annotations

import importlib.util
from typing import Any

from hla.rti.plugin_api import BackendRequest

from hla.bridges.java.common import BackendInfo, RTIBackendPlugin

from .factory import create_jpype_backend
from .runtime import JPypeConfig


def _optional_module_info(module_name: str, *, name: str, kind: str) -> BackendInfo | None:
    if importlib.util.find_spec(module_name) is None:
        return None
    return BackendInfo(name=name, kind=kind, details={"python_module": module_name})


def _jpype_backend_factory(request: BackendRequest):
    options: dict[str, Any] = dict(request.options)
    config = options.pop("config", None) or JPypeConfig(**options)
    return create_jpype_backend(config)


def jpype_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        supports=("rti1516e",),
        name="jpype",
        aliases=("java-jpype",),
        family="java",
        description="Generic Java RTI adapter through JPype.",
        create_backend=_jpype_backend_factory,
        discover=lambda: _optional_module_info("jpype", name="JPype", kind="java/jpype"),
    )


def plugin() -> RTIBackendPlugin:
    return jpype_plugin()


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "jpype_plugin", "plugin"]
