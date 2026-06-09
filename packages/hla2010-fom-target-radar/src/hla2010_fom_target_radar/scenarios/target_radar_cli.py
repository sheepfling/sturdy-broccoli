"""Shared entrypoint helpers for the target/radar example runners."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from importlib import resources
from typing import Any

from hla2010.backends.python import InMemoryRTIEngine
from hla2010.rti import create_rti_ambassador


def target_radar_fom_path() -> str:
    """Return the packaged target/radar FOM module path."""

    return str(resources.files("hla2010_fom_target_radar.resources.foms").joinpath("TargetRadarFOMmodule.xml"))


def make_target_radar_factory(
    backend: str,
    *,
    classpath: Sequence[str] = (),
    rti_factory_name: str | None = None,
    py4j_address: str = "127.0.0.1",
    py4j_port: int = 25333,
    py4j_callback_port: int = 0,
    backend_options: dict[str, Any] | None = None,
) -> Callable[[str], Any]:
    """Build a backend factory for the target/radar example runners."""

    normalized = backend.strip().lower()
    backend_options = dict(backend_options or {})
    if normalized in {"python", "inmemory", "in-memory"}:
        engine = InMemoryRTIEngine(name="target-radar-engine")

        def factory(_role: str) -> Any:
            return create_rti_ambassador("python", engine=engine)

        return factory

    if normalized in {"java-shim-jpype", "java-shim-py4j"}:
        from hla2010.testing.java_shim_kernel import SharedJavaShimKernel

        kernel = SharedJavaShimKernel()

        def factory(_role: str) -> Any:
            return create_rti_ambassador(normalized, kernel=kernel, shared=True)

        return factory

    if normalized in {"jpype", "java-jpype"}:
        from hla2010.backends.jpype import JPypeConfig, rti_ambassador

        jpype_options = dict(backend_options)
        classpath_list = [item for item in classpath if item]
        if classpath_list and "classpath" not in jpype_options:
            jpype_options["classpath"] = classpath_list
        if rti_factory_name is not None and "rti_factory_name" not in jpype_options:
            jpype_options["rti_factory_name"] = rti_factory_name
        config = jpype_options.pop("config", None) or JPypeConfig(**jpype_options)

        def factory(_role: str) -> Any:
            return rti_ambassador(config)

        return factory

    if normalized in {"py4j", "java-py4j"}:
        from hla2010.backends.py4j import Py4JConfig, rti_ambassador

        py4j_options = dict(backend_options)
        py4j_options.setdefault("gateway_parameters", {"address": py4j_address, "port": py4j_port})
        py4j_options.setdefault("callback_server_parameters", {"port": py4j_callback_port})
        if rti_factory_name is not None and "rti_factory_name" not in py4j_options:
            py4j_options["rti_factory_name"] = rti_factory_name
        config = py4j_options.pop("config", None) or Py4JConfig(**py4j_options)

        def factory(_role: str) -> Any:
            return rti_ambassador(config)

        return factory

    def factory(_role: str) -> Any:
        return create_rti_ambassador(normalized, **backend_options)

    return factory


__all__ = ["make_target_radar_factory", "target_radar_fom_path"]
