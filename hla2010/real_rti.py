"""Helpers for real RTI runtime discovery and launch profiles.

This module does two things:

1. Discover repo-local CERTI and Pitch runtime assets.
2. Build bridge/runtime configs that fit the existing ``jpype`` and ``py4j``
   backend adapters in this repo.

The actual HLA API surface still flows through ``hla2010.rti`` and the backend
adapter modules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
from typing import Any, Sequence

from .backends.base import BackendUnavailableError
from .backends.jpype_backend import JPypeConfig
from .java_runtime import discover_java_tool, ensure_java_home


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _candidate_paths(*parts: str) -> list[Path]:
    root = project_root()
    return [
        root.joinpath(*parts),
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

    @property
    def default_user_home(self) -> Path:
        env_value = os.environ.get("HLA2010_PITCH_USER_HOME")
        if env_value:
            return Path(env_value).expanduser()
        root = Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", "/private/tmp/hla-2010"))
        return root / "pitch-user-home"

    def jpype_config(self, **overrides: Any) -> JPypeConfig:
        user_home = Path(os.environ.get("HLA2010_PITCH_USER_HOME", str(self.default_user_home)))
        config = {
            "classpath": tuple(str(item) for item in self.classpath),
            "jvm_args": (
                f"-Duser.home={user_home}",
                f"-Djava.library.path={os.pathsep.join(str(item) for item in self.java_library_path)}",
            ),
            "rti_factory_name": "Federate Protocol",
        }
        config.update(overrides)
        return JPypeConfig(**config)

    def license_activator_command(self, *args: str, user_home: str | os.PathLike[str] | None = None) -> list[str]:
        return [
            str(self.java_bin),
            "-cp",
            str(self.home / "lib" / "prtifull.jar"),
            f"-Djava.library.path={self.home / 'lib'}",
            "-Dse.pitch.prti1516e.useSystemWideLicenseFile=true",
            f"-Duser.home={Path(user_home) if user_home is not None else self.default_user_home}",
            "se.pitch.prti1516e.LicenseActivator",
            *args,
        ]


@dataclass(frozen=True)
class PorticoRuntime:
    home: Path
    classpath: tuple[Path, ...]

    def jpype_config(self, **overrides: Any) -> JPypeConfig:
        config = {
            "classpath": tuple(str(item) for item in self.classpath),
        }
        config.update(overrides)
        return JPypeConfig(**config)

    @property
    def prefix(self) -> Path:
        return self.home


@dataclass(frozen=True)
class PitchLicenseRecord:
    license_id: str
    license_type: str
    seats: str
    hardware_id: str
    user: str


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


def _parse_pitch_license_list(output: str) -> tuple[PitchLicenseRecord, ...]:
    records: list[PitchLicenseRecord] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("Id  Type"):
            continue
        parts = re.split(r"\s{2,}", line)
        if len(parts) < 5:
            continue
        records.append(
            PitchLicenseRecord(
                license_id=parts[0],
                license_type=parts[1],
                seats=parts[2],
                hardware_id=parts[3],
                user=parts[4],
            )
        )
    return tuple(records)


def list_pitch_licenses(
    pitch_home: str | os.PathLike[str] | None = None,
    *,
    user_home: str | os.PathLike[str] | None = None,
) -> tuple[PitchLicenseRecord, ...]:
    runtime = discover_pitch_runtime(pitch_home)
    env = dict(os.environ)
    if user_home is not None:
        env["HOME"] = str(user_home)
    result = subprocess.run(
        runtime.license_activator_command("list", user_home=user_home),
        check=True,
        capture_output=True,
        text=True,
        env=env,
        cwd=runtime.home,
    )
    return _parse_pitch_license_list(result.stdout)


def prepare_pitch_user_home(
    runtime: PitchRuntime,
    *,
    user_home: str | os.PathLike[str] | None = None,
) -> Path:
    """Materialize a local Pitch user-home and verify license state."""

    source_user_home = runtime.default_user_home
    pitch_user_home = Path(user_home).expanduser() if user_home is not None else runtime.default_user_home
    pitch_user_home.mkdir(parents=True, exist_ok=True)
    if source_user_home.exists() and source_user_home != pitch_user_home:
        shutil.copytree(source_user_home, pitch_user_home, dirs_exist_ok=True)
    licenses = list_pitch_licenses(runtime.home, user_home=pitch_user_home)
    if not licenses:
        raise BackendUnavailableError(
            "Pitch CRC has no activated local license state. "
            "LicenseActivator list returned no licenses for the current runtime."
        )
    return pitch_user_home


@dataclass(frozen=True)
class CERTIRuntime:
    prefix: Path
    extra_lib_dirs: tuple[Path, ...] = ()
    library_path_env: dict[str, str] = field(default_factory=dict)

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


def discover_certi_runtime(explicit_prefix: str | os.PathLike[str] | None = None) -> CERTIRuntime:
    explicit = Path(explicit_prefix).expanduser().resolve() if explicit_prefix is not None else None
    env_prefix = os.environ.get("HLA2010_CERTI_PREFIX")
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    if env_prefix:
        candidates.append(Path(env_prefix).expanduser())
    candidates.extend(_candidate_paths("CERTI-install"))
    prefix = _first_existing(candidates, "bin/rtig")
    if prefix is None:
        raise BackendUnavailableError("CERTI install prefix not found; set HLA2010_CERTI_PREFIX to the install root")
    extra_lib_dirs: list[Path] = []

    env_build_root = os.environ.get("HLA2010_CERTI_BUILD_ROOT")
    build_candidates: list[Path] = []
    if env_build_root:
        build_candidates.append(Path(env_build_root).expanduser())
    build_candidates.extend(_candidate_paths("CERTI-build"))

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

    return CERTIRuntime(prefix=prefix, extra_lib_dirs=tuple(extra_lib_dirs))


def discover_certi_smoke_fom() -> Path:
    path = project_root() / "CERTI" / "test" / "InteractiveFederate" / "1516-2010" / "Certi-Test-02.xml"
    if path.exists():
        return path
    raise BackendUnavailableError("CERTI smoke FOM sample not found in the repo-local CERTI source tree")


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
    user_home = prepare_pitch_user_home(runtime)
    javaopts = [
        f"-Duser.home={user_home}",
        f"-Djava.library.path={os.pathsep.join(str(item) for item in runtime.java_library_path)}",
        "-Dse.pitch.prti1516e.useSystemWideLicenseFile=true",
    ]
    os.environ["HLA2010_PITCH_USER_HOME"] = str(user_home)
    return launch_gateway(
        port=port,
        classpath=classpath,
        java_path=java_path,
        die_on_exit=die_on_exit,
        javaopts=javaopts,
    )


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


@dataclass
class RuntimeProcess:
    name: str
    process: subprocess.Popen[str]
    env: dict[str, str] = field(default_factory=dict)
    host: str | None = None
    tcp_port: int | None = None
    children: tuple[subprocess.Popen[str], ...] = ()

    def poll(self) -> int | None:
        return self.process.poll()

    def terminate(self, *, timeout: float = 5.0) -> None:
        processes = (*self.children, self.process)
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
        for process in reversed(processes):
            if process.poll() is None:
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=timeout)


def reserve_tcp_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_tcp_listener(host: str, port: int, *, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.1)
    raise BackendUnavailableError(f"Timed out waiting for listener on {host}:{port}")


def _wait_for_process_boot(process: subprocess.Popen[str], *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise BackendUnavailableError(f"Runtime process exited early with code {process.returncode}")
        time.sleep(0.1)


def launch_pitch_runtime(
    *,
    pitch_home: str | os.PathLike[str] | None = None,
    args: Sequence[str] = ("-nogui", "-verbose"),
) -> RuntimeProcess:
    runtime = discover_pitch_runtime(pitch_home)
    env = dict(os.environ)
    pitch_user_home = prepare_pitch_user_home(runtime)
    env["HLA2010_PITCH_HOME"] = str(runtime.home)
    env["HOME"] = str(pitch_user_home)
    env["HLA2010_PITCH_USER_HOME"] = str(pitch_user_home)
    env["INSTALL4J_JAVA_HOME"] = str(runtime.java_home)
    os.environ["HLA2010_PITCH_USER_HOME"] = str(pitch_user_home)
    crc_classpath = os.pathsep.join(
        [
            str(runtime.home / "lib" / "prtifull.jar"),
            str(runtime.home / "lib" / "booster1516.jar"),
            str(runtime.home / "lib" / "webgui2-protocol.jar"),
        ]
    )
    crc_command = [
        str(runtime.java_bin),
        "-Xmx512m",
        f"-Duser.home={pitch_user_home}",
        f"-Djava.library.path={os.pathsep.join(str(item) for item in runtime.java_library_path)}",
        "-classpath",
        crc_classpath,
        "se.pitch.prti1516e.RTIexec",
        *args,
        "-nocmdline",
    ]
    crc_process = subprocess.Popen(crc_command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    fedpro_classpath = os.pathsep.join(str(path) for path in sorted((runtime.home / "lib").glob("*.jar")))
    fedpro_command = [
        str(runtime.java_bin),
        "-Dse.pitch.prti1516e.useSystemWideLicenseFile=true",
        f"-Duser.home={pitch_user_home}",
        f"-Djava.library.path={os.pathsep.join(str(item) for item in runtime.java_library_path)}",
        "-classpath",
        fedpro_classpath,
        "se.pitch.fedpro.server.hla.FedProServerApp",
    ]
    fedpro_process = subprocess.Popen(
        fedpro_command,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=runtime.home,
    )
    try:
        _wait_for_process_boot(crc_process)
        _wait_for_process_boot(fedpro_process)
        _wait_for_tcp_listener("127.0.0.1", 15164, timeout=15.0)
        try:
            _wait_for_tcp_listener("127.0.0.1", 8989, timeout=3.0)
        except BackendUnavailableError as exc:
            raise BackendUnavailableError(
                "Pitch FedPro server started, but CRC never exposed TCP port 8989. "
                "This usually means the local CRC runtime is not fully activated or installed."
            ) from exc
    except Exception:
        if fedpro_process.poll() is None:
            fedpro_process.terminate()
            fedpro_process.wait(timeout=5)
        if crc_process.poll() is None:
            crc_process.terminate()
            crc_process.wait(timeout=5)
        raise
    return RuntimeProcess(
        name="pitch",
        process=crc_process,
        env=env,
        host="127.0.0.1",
        tcp_port=15164,
        children=(fedpro_process,),
    )


def launch_certi_rtig(
    *,
    certi_prefix: str | os.PathLike[str] | None = None,
    host: str = "127.0.0.1",
    tcp_port: int | None = None,
    udp_port: int | None = None,
    verbose: int = 0,
) -> RuntimeProcess:
    runtime = discover_certi_runtime(certi_prefix)
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
    command = [str(project_root() / "scripts" / "run_certi_local.sh"), "rtig", "-v", str(verbose)]
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        _wait_for_tcp_listener(host, tcp_port)
    except Exception:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        raise
    return RuntimeProcess(name="certi-rtig", process=process, env=env, host=host, tcp_port=tcp_port)


__all__ = [
    "CERTIRuntime",
    "PitchRuntime",
    "PitchLicenseRecord",
    "PorticoRuntime",
    "discover_certi_runtime",
    "discover_certi_smoke_fom",
    "discover_pitch_runtime",
    "discover_portico_runtime",
    "list_pitch_licenses",
    "prepare_pitch_user_home",
    "launch_pitch_py4j_gateway",
    "launch_pitch_runtime",
    "launch_portico_py4j_gateway",
    "launch_certi_rtig",
    "_parse_pitch_license_list",
    "project_root",
    "reserve_tcp_port",
    "RuntimeProcess",
]
