"""CERTI runtime discovery and launch helpers."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hla2010.backends.base import BackendUnavailableError
from hla2010_rti_runtime_common import RuntimeProcess, reserve_tcp_port, wait_for_tcp_listener


def _project_root() -> Path:
    return Path(os.environ.get("HLA2010_PROJECT_ROOT", os.getcwd())).expanduser().resolve()


def _candidate_paths(*parts: str) -> list[Path]:
    return [_project_root().joinpath(*parts)]


def _local_state_path(*parts: str) -> Path:
    root = Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", str(_project_root() / ".local")))
    return root.joinpath(*parts)


@dataclass(frozen=True)
class CERTIRuntime:
    prefix: Path
    extra_lib_dirs: tuple[Path, ...] = ()
    library_path_env: dict[str, str] = field(default_factory=dict)
    profile: str = "default"

    @property
    def home(self) -> Path:
        return self.prefix

    @property
    def bin_dir(self) -> Path:
        return self.prefix / "bin"

    @property
    def lib_dir(self) -> Path:
        return self.prefix / "lib"

    @property
    def lib_dirs(self) -> tuple[Path, ...]:
        ordered = [*self.extra_lib_dirs, self.lib_dir]
        existing: list[Path] = []
        seen: set[Path] = set()
        for path in ordered:
            if path.exists() and path not in seen:
                existing.append(path)
                seen.add(path)
        return tuple(existing)

    def executable(self, component: str) -> Path:
        path = self.bin_dir / component
        if not path.exists():
            raise BackendUnavailableError(f"CERTI component {component!r} not found below {self.bin_dir}")
        return path

    def runtime_env(self) -> dict[str, str]:
        env = dict(os.environ)
        dyld = env.get("DYLD_LIBRARY_PATH")
        lib_path = os.pathsep.join(str(path) for path in self.lib_dirs)
        env["DYLD_LIBRARY_PATH"] = f"{lib_path}{':' + dyld if dyld else ''}"
        env.setdefault("CERTI_HOME", str(self.prefix))
        env.setdefault("CERTI_FOM_PATH", str(self.prefix / "share" / "federations"))
        env.update(self.library_path_env)
        return env

    def popen(self, component: str, *args: str, **kwargs: Any) -> subprocess.Popen[str]:
        command = [str(self.executable(component)), *args]
        return subprocess.Popen(command, env=self.runtime_env(), text=True, **kwargs)


@dataclass(frozen=True)
class CERTIRuntimeProfile:
    """Named CERTI baseline used for vendor-vs-local parity evidence."""

    name: str
    runtime: CERTIRuntime
    source: str


def discover_certi_runtime(
    explicit_prefix: str | os.PathLike[str] | None = None,
    *,
    certi_build_root: str | os.PathLike[str] | None = None,
    allow_repo_build_overlay: bool = True,
    profile: str = "default",
) -> CERTIRuntime:
    explicit = Path(explicit_prefix).expanduser().resolve() if explicit_prefix is not None else None
    env_prefix = os.environ.get("HLA2010_CERTI_PREFIX")
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    if env_prefix:
        candidates.append(Path(env_prefix).expanduser())
    candidates.append(_local_state_path("certi", "patched", "install"))
    prefix = _first_existing(candidates, "bin/rtig")
    if prefix is None:
        raise BackendUnavailableError("CERTI install prefix not found; set HLA2010_CERTI_PREFIX to the install root")
    extra_lib_dirs: list[Path] = []

    env_build_root = os.environ.get("HLA2010_CERTI_BUILD_ROOT")
    build_candidates: list[Path] = []
    if certi_build_root is not None:
        build_candidates.append(Path(certi_build_root).expanduser())
    elif env_build_root and allow_repo_build_overlay:
        build_candidates.append(Path(env_build_root).expanduser())
    if allow_repo_build_overlay:
        build_candidates.append(_local_state_path("certi", "patched", "build"))

    for build_root in build_candidates:
        build_root = build_root.expanduser().resolve()
        rtie_dir = build_root / "libRTI" / "ieee1516-2010"
        certi_dir = build_root / "libCERTI"
        if (rtie_dir / "libRTI1516ed.dylib").exists():
            extra_lib_dirs.append(rtie_dir)
        if (certi_dir / "libCERTId.dylib").exists():
            extra_lib_dirs.append(certi_dir)
        if extra_lib_dirs:
            break

    return CERTIRuntime(prefix=prefix, extra_lib_dirs=tuple(extra_lib_dirs), profile=profile)


def discover_certi_runtime_profile(name: str) -> CERTIRuntimeProfile:
    """Resolve a named CERTI runtime baseline without cross-contaminating libs.

    ``certi-upstream`` is intentionally opt-in and never falls back to the
    repo-local build overlay. ``certi-patched`` is the repo-local vendored build
    unless callers override the patched-prefix/build-root environment variables.
    """

    normalized = name.strip().lower().replace("_", "-")
    if normalized in {"certi-upstream", "upstream", "original", "pristine"}:
        prefix = os.environ.get("HLA2010_CERTI_UPSTREAM_PREFIX") or os.environ.get("HLA2010_CERTI_ORIGINAL_PREFIX")
        build_root = os.environ.get("HLA2010_CERTI_UPSTREAM_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_ORIGINAL_BUILD_ROOT")
        if not prefix:
            raise BackendUnavailableError(
                "upstream CERTI baseline not configured; set HLA2010_CERTI_UPSTREAM_PREFIX "
                "to an unmodified CERTI install"
            )
        runtime = discover_certi_runtime(
            prefix,
            certi_build_root=build_root,
            allow_repo_build_overlay=False,
            profile="certi-upstream",
        )
        return CERTIRuntimeProfile(name="certi-upstream", runtime=runtime, source="upstream")

    if normalized in {"certi-patched", "patched", "local", "repo-local"}:
        prefix = os.environ.get("HLA2010_CERTI_PATCHED_PREFIX") or os.environ.get("HLA2010_CERTI_PREFIX")
        build_root = os.environ.get("HLA2010_CERTI_PATCHED_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_BUILD_ROOT")
        runtime = discover_certi_runtime(
            prefix,
            certi_build_root=build_root,
            allow_repo_build_overlay=True,
            profile="certi-patched",
        )
        return CERTIRuntimeProfile(name="certi-patched", runtime=runtime, source="repo-local patched")

    if normalized in {"certi", "default", "active"}:
        runtime = discover_certi_runtime(profile="certi")
        return CERTIRuntimeProfile(name="certi", runtime=runtime, source="active default")

    raise ValueError(f"Unknown CERTI runtime profile: {name!r}")


def _first_existing(candidates: list[Path], marker: str) -> Path | None:
    for path in candidates:
        if (path / marker).exists():
            return path
    return None


def discover_certi_smoke_fom() -> Path:
    path = _project_root() / "CERTI" / "test" / "InteractiveFederate" / "1516-2010" / "Certi-Test-02.xml"
    if path.exists():
        return path
    raise BackendUnavailableError("CERTI smoke FOM sample not found in the repo-local CERTI source tree")


def launch_certi_rtig(
    *,
    certi_prefix: str | os.PathLike[str] | None = None,
    certi_build_root: str | os.PathLike[str] | None = None,
    allow_repo_build_overlay: bool = True,
    host: str = "127.0.0.1",
    tcp_port: int | None = None,
    udp_port: int | None = None,
    verbose: int = 0,
) -> RuntimeProcess:
    runtime = discover_certi_runtime(
        certi_prefix,
        certi_build_root=certi_build_root,
        allow_repo_build_overlay=allow_repo_build_overlay,
    )
    tcp_port = int(tcp_port or reserve_tcp_port(host))
    udp_port = int(udp_port or (tcp_port + 100))
    env = runtime.runtime_env()
    env.update(
        {
            "CERTI_HOST": host,
            "CERTI_TCP_PORT": str(tcp_port),
            "CERTI_UDP_PORT": str(udp_port),
        }
    )
    runner = Path(os.environ.get("HLA2010_CERTI_RUN_SCRIPT", str(_project_root() / "scripts" / "run_certi_local.sh")))
    command = [str(runner), "rtig", "-v", str(verbose)]
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        wait_for_tcp_listener(host, tcp_port)
    except Exception:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        raise
    return RuntimeProcess(name="certi-rtig", process=process, env=env, host=host, tcp_port=tcp_port)


__all__ = [
    "CERTIRuntime",
    "CERTIRuntimeProfile",
    "discover_certi_runtime",
    "discover_certi_runtime_profile",
    "discover_certi_smoke_fom",
    "launch_certi_rtig",
]
