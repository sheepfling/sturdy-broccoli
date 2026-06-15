"""Shared backend-factory helpers for the target/radar example runners."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from collections import Counter
from dataclasses import dataclass, field
from importlib import import_module
from importlib import resources
from typing import Any

def target_radar_fom_path() -> str:
    """Return the packaged target/radar FOM module path."""

    return str(resources.files("hla2010_fom_target_radar.resources.foms").joinpath("TargetRadarFOMmodule.xml"))


class TargetRadarBackendUnavailableError(RuntimeError):
    """Raised when an example-selected backend is unavailable in this workspace."""


@dataclass
class TargetRadarFactory:
    """Explicit role-based RTI factory used by the target/radar scenarios."""

    maker: Callable[[str], Any]
    closer: Callable[[], None] | None = None

    def make_rti(self, role: str) -> Any:
        return self.maker(role)

    def close(self) -> None:
        if self.closer is not None:
            self.closer()


def make_target_radar_factory(
    backend: str,
    *,
    classpath: Sequence[str] = (),
    rti_factory_name: str | None = None,
    py4j_address: str = "127.0.0.1",
    py4j_port: int = 25333,
    py4j_callback_port: int = 0,
    backend_options: dict[str, Any] | None = None,
) -> TargetRadarFactory:
    """Build a backend factory for the target/radar example runners."""

    normalized = backend.strip().lower()
    backend_options = dict(backend_options or {})
    if normalized in {"python", "inmemory", "in-memory"}:
        pair_by_role: dict[str, Any] = {}
        create_python_pair = import_module("hla2010_rti_python").create_python_pair

        def factory(role: str) -> Any:
            if role not in pair_by_role:
                target_rti, radar_rti = create_python_pair()
                pair_by_role.update({"target": target_rti, "radar": radar_rti})
            return pair_by_role[role]

        return TargetRadarFactory(factory)

    if normalized in {"python-grpc", "grpc-hosted-python", "hosted-python-grpc"}:
        pair_by_role: dict[str, Any] = {}
        references = Counter()
        try:
            create_python_engine = import_module("hla2010_rti_python").InMemoryRTIEngine
            start_python_grpc_server = import_module("hla2010_rti_transport_grpc").start_python_grpc_server
            create_rti_ambassador = import_module("hla2010_rti_runtime_common").create_rti_ambassador
            engine = create_python_engine()
            target_server = start_python_grpc_server(engine=engine)
            radar_server = start_python_grpc_server(engine=engine)
        except ModuleNotFoundError as exc:
            raise TargetRadarBackendUnavailableError(
                "python-grpc requires the hla2010 gRPC transport dependencies; rerun ./tools/bootstrap python"
            ) from exc
        except (ImportError, OSError, RuntimeError) as exc:
            raise TargetRadarBackendUnavailableError(
                f"python-grpc could not start a loopback gRPC host: {exc}"
            ) from exc

        def _close_servers() -> None:
            if references["open"] != 0:
                return
            radar_server.close()
            target_server.close()

        def factory(role: str) -> Any:
            if role not in pair_by_role:
                pair_by_role.update(
                    {
                        "target": create_rti_ambassador("python", transport={"kind": "grpc", "target": target_server.target}),
                        "radar": create_rti_ambassador("python", transport={"kind": "grpc", "target": radar_server.target}),
                    }
                )
                references["open"] = len(pair_by_role)
            return pair_by_role[role]

        def close_factory() -> None:
            references["open"] = max(references["open"] - 1, 0)
            _close_servers()

        return TargetRadarFactory(factory, closer=close_factory)

    if normalized in {"jpype", "java-jpype"}:
        java_jpype = import_module("hla2010_rti_java_jpype")

        jpype_options = dict(backend_options)
        classpath_list = [item for item in classpath if item]
        if classpath_list and "classpath" not in jpype_options:
            jpype_options["classpath"] = classpath_list
        if rti_factory_name is not None and "rti_factory_name" not in jpype_options:
            jpype_options["rti_factory_name"] = rti_factory_name
        config = jpype_options.pop("config", None) or java_jpype.JPypeConfig(**jpype_options)

        def factory(_role: str) -> Any:
            return java_jpype.rti_ambassador(config)

        return TargetRadarFactory(factory)

    if normalized in {"py4j", "java-py4j"}:
        java_py4j = import_module("hla2010_rti_java_py4j")

        py4j_options = dict(backend_options)
        py4j_options.setdefault("gateway_parameters", {"address": py4j_address, "port": py4j_port})
        py4j_options.setdefault("callback_server_parameters", {"port": py4j_callback_port})
        if rti_factory_name is not None and "rti_factory_name" not in py4j_options:
            py4j_options["rti_factory_name"] = rti_factory_name
        config = py4j_options.pop("config", None) or java_py4j.Py4JConfig(**py4j_options)

        def factory(_role: str) -> Any:
            return java_py4j.rti_ambassador(config)

        return TargetRadarFactory(factory)

    create_rti_ambassador = import_module("hla2010_rti_runtime_common").create_rti_ambassador

    def factory(_role: str) -> Any:
        return create_rti_ambassador(normalized, **backend_options)

    return TargetRadarFactory(factory)


__all__ = [
    "TargetRadarBackendUnavailableError",
    "TargetRadarFactory",
    "make_target_radar_factory",
    "target_radar_fom_path",
]
