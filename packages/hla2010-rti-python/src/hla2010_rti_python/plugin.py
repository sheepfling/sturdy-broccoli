"""Entry point descriptor for the split pure Python RTI backend package."""
from __future__ import annotations

from typing import Any

from hla2010.backends.base import BackendInfo
from hla2010.rti import RTIBackendPlugin

from . import PythonRTIConfig, create_python_backend


def _create_backend(options: dict[str, Any]):
    engine = options.pop("engine", None)
    config = options.pop("config", None)
    if options:
        config = config or PythonRTIConfig(**options)
    return create_python_backend(engine=engine, config=config)


def plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="python",
        aliases=("inmemory", "in-memory", "python-inmemory", "python-in-memory"),
        family="python-reference",
        description="Pure in-memory Python RTI backend.",
        create_backend=_create_backend,
        discover=lambda: BackendInfo(name="python-inmemory-rti", kind="python/in-memory"),
    )


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "plugin"]
