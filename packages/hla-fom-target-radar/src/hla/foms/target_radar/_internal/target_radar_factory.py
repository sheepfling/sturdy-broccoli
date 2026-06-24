"""Shared backend-factory helpers for the target/radar example runners."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from importlib import import_module
from importlib import resources
from typing import Any

from .target_radar_2025_adapter import TargetRadar2025RTIAdapter


_TARGET_RADAR_2025_BACKENDS = {
    "python2025",
    "python-2025",
    "python-2025-backend",
}


def target_radar_fom_path() -> str:
    """Return the packaged target/radar FOM module path."""

    return str(resources.files("hla.foms.target_radar.resources.foms").joinpath("TargetRadarFOMmodule.xml"))


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
        pair_by_role: dict[str, Any] = {}
        create_python_pair = import_module("hla.backends.inmemory").create_python_pair

        def factory(role: str) -> Any:
            if role not in pair_by_role:
                target_rti, radar_rti = create_python_pair()
                pair_by_role.update({"target": target_rti, "radar": radar_rti})
            return pair_by_role[role]

        return factory

    if normalized in {"jpype", "java-jpype"}:
        java_jpype = import_module("hla.bridges.java.jpype")

        jpype_options = dict(backend_options)
        classpath_list = [item for item in classpath if item]
        if classpath_list and "classpath" not in jpype_options:
            jpype_options["classpath"] = classpath_list
        if rti_factory_name is not None and "rti_factory_name" not in jpype_options:
            jpype_options["rti_factory_name"] = rti_factory_name
        config = jpype_options.pop("config", None) or java_jpype.JPypeConfig(**jpype_options)

        def factory(_role: str) -> Any:
            return java_jpype.rti_ambassador(config)

        return factory

    if normalized in {"py4j", "java-py4j"}:
        java_py4j = import_module("hla.bridges.java.py4j")

        py4j_options = dict(backend_options)
        py4j_options.setdefault("gateway_parameters", {"address": py4j_address, "port": py4j_port})
        py4j_options.setdefault("callback_server_parameters", {"port": py4j_callback_port})
        if rti_factory_name is not None and "rti_factory_name" not in py4j_options:
            py4j_options["rti_factory_name"] = rti_factory_name
        config = py4j_options.pop("config", None) or java_py4j.Py4JConfig(**py4j_options)

        def factory(_role: str) -> Any:
            return java_py4j.rti_ambassador(config)

        return factory

    if normalized in _TARGET_RADAR_2025_BACKENDS:
        create_rti_ambassador = import_module("hla.runtime.rti1516_2025_factory").create_rti_ambassador

        def factory(_role: str) -> Any:
            rti = create_rti_ambassador(backend=normalized, **backend_options)
            return TargetRadar2025RTIAdapter(rti)

        return factory

    create_rti_ambassador = import_module("hla.rti").create_rti_ambassador

    def factory(_role: str) -> Any:
        rti = create_rti_ambassador(spec="2025", backend=normalized, **backend_options)
        if normalized in _TARGET_RADAR_2025_BACKENDS:
            return TargetRadar2025RTIAdapter(rti)
        return rti

    return factory


__all__ = ["make_target_radar_factory", "target_radar_fom_path"]
