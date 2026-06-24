"""Entry point descriptor for the split pure Python RTI backend package."""
from __future__ import annotations

from typing import Any

from hla.backends.common import BackendInfo, RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest

from . import PythonRTIConfig, create_python_backend


def _create_backend(request: BackendRequest):
    options: dict[str, Any] = dict(request.options if hasattr(request, "options") else request)
    engine = options.pop("engine", None)
    config = options.pop("config", None)
    if options:
        config = config or PythonRTIConfig(**options)
    return create_python_backend(engine=engine, config=config)


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python1516e",
        aliases=("python", "python-1516e"),
        family="python-rti-1516e",
        supports=("rti1516e",),
        description="Primary Python 1516e RTI backend.",
        create_backend=_create_backend,
        discover=lambda: BackendInfo(name="python1516e-rti", kind="python/1516e"),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
