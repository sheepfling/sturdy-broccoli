"""Helpers for real RTI runtime discovery and launch profiles.

This module does two things:

1. Discover repo-local or sibling-workspace CERTI and Pitch runtime assets.
2. Build bridge/runtime configs that fit the existing ``jpype`` and ``py4j``
   backend adapters in this repo.

The actual HLA API surface still flows through ``hla2010.rti`` and the backend
adapter modules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import subprocess
from typing import Any, Sequence

from .backends.base import BackendUnavailableError
from .backends.jpype_backend import JPypeConfig
from .java_runtime import discover_java_tool, ensure_java_home


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _candidate_paths(*parts: str) -> list[Path]:
    root = project_root()
    sibling_root = root.parent / "hla-python"
    return [
        root.joinpath(*parts),
        sibling_root.joinpath(*parts),
    ]


def _first_existing(candidates: Sequence[Path], marker: str) -> Path | None:
    for path in candidates:
        if (path / marker).exists():
            return path
    return None


@dataclass(frozen=True)
class PitchRuntime:
    home: Path
    java_home: Path
    classpath: tuple[Path, ...]
    java_library_path: tuple[Path, ...]

    @property
    def java_bin(self) -> Path:
        return self.java_home / "bin" / "java"

    def jpype_config(self, **overrides: Any) -> JPypeConfig:
        config = {
            "classpath": tuple(str(item) for item in self.classpath),
        }
        config.update(overrides)
        return JPypeConfig(**config)


def discover_pitch_runtime(explicit_home: str | os.PathLike[str] | None = None) -> PitchRuntime:
    explicit = Path(explicit_home).expanduser().resolve() if explicit_home is not None else None
    env_home = os.environ.get("HLA2010_PITCH_HOME")
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    if env_home:
        candidates.append(Path(env_home).expanduser())
    candidates.extend(_candidate_paths("third_party", "pitch", "PITCH-prti1516e-manual"))
    candidates.extend(_candidate_paths("INBOX", "PITCH-prti1516e-manual"))
    home = _first_existing(candidates, "lib/prtifull.jar")
    if home is None:
        raise BackendUnavailableError("Pitch pRTI runtime not found; set HLA2010_PITCH_HOME to the extracted runtime")

    java_home = home / "Contents" / "Home"
    if not (java_home / "bin" / "java").exists():
        raise BackendUnavailableError(f"Pitch runtime at {home} does not contain a bundled Java runtime")

    lib_dir = home / "lib"
    extra_lib = home / ".i4j_external_12081" / "lib"
    clang12 = extra_lib / "clang12"
    classpath = tuple(sorted(lib_dir.glob("*.jar")))
    if not classpath:
        raise BackendUnavailableError(f"Pitch runtime at {home} does not contain RTI jars")

    return PitchRuntime(
        home=home,
        java_home=java_home,
        classpath=classpath,
        java_library_path=(lib_dir, extra_lib, clang12),
    )


@dataclass(frozen=True)
class CERTIRuntime:
    prefix: Path
    library_path_env: dict[str, str] = field(default_factory=dict)

    @property
    def bin_dir(self) -> Path:
        return self.prefix / "bin"

    @property
    def lib_dir(self) -> Path:
        return self.prefix / "lib"

    def executable(self, component: str) -> Path:
        path = self.bin_dir / component
        if not path.exists():
            raise BackendUnavailableError(f"CERTI component {component!r} not found below {self.bin_dir}")
        return path

    def runtime_env(self) -> dict[str, str]:
        env = dict(os.environ)
        dyld = env.get("DYLD_LIBRARY_PATH")
        env["DYLD_LIBRARY_PATH"] = f"{self.lib_dir}{':' + dyld if dyld else ''}"
        env.update(self.library_path_env)
        return env

    def popen(self, component: str, *args: str, **kwargs: Any) -> subprocess.Popen[str]:
        command = [str(self.executable(component)), *args]
        return subprocess.Popen(command, env=self.runtime_env(), text=True, **kwargs)


def discover_certi_runtime(explicit_prefix: str | os.PathLike[str] | None = None) -> CERTIRuntime:
    explicit = Path(explicit_prefix).expanduser().resolve() if explicit_prefix is not None else None
    env_prefix = os.environ.get("HLA2010_CERTI_PREFIX")
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    if env_prefix:
        candidates.append(Path(env_prefix).expanduser())
    candidates.extend(_candidate_paths("third_party", "certi", "install"))
    candidates.extend(_candidate_paths("INBOX", "CERTI-install"))
    prefix = _first_existing(candidates, "bin/rtig")
    if prefix is None:
        raise BackendUnavailableError("CERTI install prefix not found; set HLA2010_CERTI_PREFIX to the install root")
    return CERTIRuntime(prefix=prefix)


def launch_pitch_py4j_gateway(
    *,
    pitch_home: str | os.PathLike[str] | None = None,
    port: int = 25333,
    die_on_exit: bool = True,
):
    """Launch a Py4J gateway JVM with the Pitch jars on its classpath."""
    try:
        from py4j.java_gateway import launch_gateway
    except Exception as exc:
        raise BackendUnavailableError("Py4J is not installed") from exc

    runtime = discover_pitch_runtime(pitch_home)
    ensure_java_home()
    java_path = discover_java_tool("java")
    classpath = os.pathsep.join(str(item) for item in runtime.classpath)
    javaopts = [
        f"-Duser.home={runtime.home / 'user.home'}",
        f"-Djava.library.path={os.pathsep.join(str(item) for item in runtime.java_library_path)}",
    ]
    return launch_gateway(
        port=port,
        classpath=classpath,
        java_path=java_path,
        die_on_exit=die_on_exit,
        javaopts=javaopts,
    )


__all__ = [
    "CERTIRuntime",
    "PitchRuntime",
    "discover_certi_runtime",
    "discover_pitch_runtime",
    "launch_pitch_py4j_gateway",
    "project_root",
]
