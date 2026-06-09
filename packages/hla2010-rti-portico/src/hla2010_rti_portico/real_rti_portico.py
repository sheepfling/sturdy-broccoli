"""Portico runtime discovery and launch helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Sequence

from hla2010.backends.base import BackendUnavailableError
from hla2010.java_runtime import discover_java_tool, ensure_java_home

if TYPE_CHECKING:
    from hla2010_rti_java_jpype import JPypeConfig


def _project_root() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "pyproject.toml").exists() and (parent / "hla2010").exists():
            return parent
    return path.parents[4]


def _candidate_paths(*parts: str) -> list[Path]:
    return [_project_root().joinpath(*parts)]


def _first_existing(candidates: Sequence[Path], marker: str) -> Path | None:
    for path in candidates:
        if (path / marker).exists():
            return path
    return None


@dataclass(frozen=True)
class PorticoRuntime:
    home: Path
    classpath: tuple[Path, ...]

    def jpype_config(self, **overrides: Any) -> "JPypeConfig":
        from hla2010_rti_java_jpype import JPypeConfig

        config = {
            "classpath": tuple(str(item) for item in self.classpath),
        }
        config.update(overrides)
        return JPypeConfig(**config)

    @property
    def prefix(self) -> Path:
        return self.home


def discover_portico_runtime(explicit_home: str | os.PathLike[str] | None = None) -> PorticoRuntime:
    explicit = Path(explicit_home).expanduser().resolve() if explicit_home is not None else None
    env_home = os.environ.get("HLA2010_PORTICO_HOME") or os.environ.get("RTI_HOME")
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    if env_home:
        candidates.append(Path(env_home).expanduser())
    candidates.extend(_candidate_paths("third_party", "portico"))
    candidates.extend(_candidate_paths("INBOX", "portico"))
    home = _first_existing(candidates, "lib/portico.jar")
    if home is None:
        raise BackendUnavailableError(
            "Portico RTI runtime not found; set HLA2010_PORTICO_HOME or RTI_HOME to the Portico install root"
        )

    classpath = tuple(sorted(home.joinpath("lib").glob("*.jar")))
    if not classpath:
        raise BackendUnavailableError(f"Portico runtime at {home} does not contain RTI jars")

    return PorticoRuntime(home=home, classpath=classpath)


def launch_portico_py4j_gateway(
    *,
    portico_home: str | os.PathLike[str] | None = None,
    port: int = 25333,
    die_on_exit: bool = True,
):
    """Launch a Py4J gateway JVM with the Portico jars on its classpath."""
    try:
        from py4j.java_gateway import launch_gateway
    except Exception as exc:
        raise BackendUnavailableError("Py4J is not installed") from exc

    runtime = discover_portico_runtime(portico_home)
    ensure_java_home()
    java_path = discover_java_tool("java")
    classpath = os.pathsep.join(str(item) for item in runtime.classpath)
    return launch_gateway(
        port=port,
        classpath=classpath,
        java_path=java_path,
        die_on_exit=die_on_exit,
    )


__all__ = ["PorticoRuntime", "discover_portico_runtime", "launch_portico_py4j_gateway"]
