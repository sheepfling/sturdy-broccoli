"""Entry point descriptor for the split pure Python RTI backend package."""
from __future__ import annotations

from typing import Any

from hla2010_rti_backend_common import BackendInfo, RTIBackendPlugin
from hla2010_rti_transport_common import HostedRTIBackend, HostedRTIBackendConfig, coerce_transport_spec

from . import PythonRTIConfig, create_python_backend


def _create_backend(options: dict[str, Any]):
    transport = coerce_transport_spec(options.pop("transport", None))
    engine = options.pop("engine", None)
    config = options.pop("config", None)
    if transport is not None:
        if engine is not None:
            raise TypeError("Hosted Python RTI routes do not accept a local engine")
        if options:
            raise TypeError(f"Hosted Python RTI routes do not accept in-process backend options: {sorted(options)}")
        if config is not None:
            raise TypeError("Hosted Python RTI routes do not accept PythonRTIConfig on the client side")
        return HostedRTIBackend(
            HostedRTIBackendConfig(
                transport=transport,
                backend_name="python",
                backend_kind="python/hosted",
            )
        )
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
