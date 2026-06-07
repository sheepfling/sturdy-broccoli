"""Shared entrypoint helpers for the target/radar example runners."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from importlib import resources
from typing import Any

from ..backends.python import InMemoryRTIEngine
from ..rti import create_rti_ambassador


def target_radar_fom_path() -> str:
    """Return the packaged target/radar FOM module path."""

    return str(resources.files("hla2010.resources.foms").joinpath("TargetRadarFOMmodule.xml"))


def make_target_radar_factory(
    backend: str,
    *,
    classpath: Sequence[str] = (),
    rti_factory_name: str | None = None,
    py4j_address: str = "127.0.0.1",
    py4j_port: int = 25333,
    py4j_callback_port: int = 0,
) -> Callable[[str], Any]:
    """Build a backend factory for the target/radar example runners."""

    normalized = backend.strip().lower()
    if normalized in {"python", "inmemory", "in-memory"}:
        engine = InMemoryRTIEngine(name="target-radar-engine")

        def factory(_role: str) -> Any:
            return create_rti_ambassador("python", engine=engine)

        return factory

    if normalized in {"java-shim-jpype", "java-shim-py4j"}:
        from ..testing.java_shim import SharedJavaShimKernel

        kernel = SharedJavaShimKernel()

        def factory(_role: str) -> Any:
            return create_rti_ambassador(normalized, kernel=kernel, shared=True)

        return factory

    if normalized in {"jpype", "java-jpype"}:
        from ..backends.jpype import JPypeConfig, rti_ambassador

        classpath_list = [item for item in classpath if item]
        config = JPypeConfig(classpath=classpath_list, rti_factory_name=rti_factory_name)

        def factory(_role: str) -> Any:
            return rti_ambassador(config)

        return factory

    if normalized in {"py4j", "java-py4j"}:
        from ..backends.py4j import Py4JConfig, rti_ambassador

        def factory(_role: str) -> Any:
            return rti_ambassador(
                Py4JConfig(
                    gateway_parameters={"address": py4j_address, "port": py4j_port},
                    callback_server_parameters={"port": py4j_callback_port},
                    rti_factory_name=rti_factory_name,
                )
            )

        return factory

    raise ValueError(f"unsupported backend {backend!r}")


__all__ = ["make_target_radar_factory", "target_radar_fom_path"]
