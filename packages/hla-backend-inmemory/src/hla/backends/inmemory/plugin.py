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
        name="inmemory",
        aliases=("python", "in-memory", "python-inmemory", "python-in-memory"),
        family="inmemory",
        supports=("rti1516e", "rti1516_2025"),
        description="Pure in-memory Python RTI backend.",
        create_backend=_create_backend,
        discover=lambda: BackendInfo(name="python-inmemory-rti", kind="python/in-memory"),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
