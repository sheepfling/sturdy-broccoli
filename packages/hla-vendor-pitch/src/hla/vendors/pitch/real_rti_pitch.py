"""Pitch runtime discovery and launch helpers."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from uuid import uuid4
from typing import Any, Sequence

from hla.bridges.java.common import BackendUnavailableError
from hla.bridges.java.common.java_runtime import discover_java_tool, ensure_java_home
from hla.rti import RuntimeProcess


_PITCH_USER_HOME_MARKER = ".hla2010_pitch_user_home_seeded"


def _project_root() -> Path:
    return Path(os.environ.get("HLA2010_PROJECT_ROOT", os.getcwd())).expanduser().resolve()


def _local_state_root() -> Path:
    return Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", str(_project_root() / ".local")))


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
        return _local_state_root() / "pitch" / "user-home"

    def jpype_config(self, **overrides: Any) -> Any:
        jpype_config_type = import_module("hla.bridges.java.jpype").JPypeConfig
        user_home = Path(os.environ.get("HLA2010_PITCH_USER_HOME", str(self.default_user_home)))
        config = {
            "classpath": tuple(str(item) for item in self.classpath),
            "jvm_args": (
                f"-Duser.home={user_home}",
                f"-Djava.library.path={os.pathsep.join(str(item) for item in self.java_library_path)}",
            ),
            "rti_factory_name": "Federate Protocol",
            "connect_local_settings_designator": pitch_fedpro_local_settings_designator(),
        }
        config.update(overrides)
        return jpype_config_type(**config)

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
class PitchLicenseRecord:
    license_id: str
    license_type: str
    seats: str
    hardware_id: str
    user: str


def pitch_fedpro_local_settings_designator() -> str:
    explicit = os.environ.get("HLA2010_PITCH_FEDPRO_LOCAL_SETTINGS_DESIGNATOR")
    if explicit:
        return explicit
    if os.environ.get("HLA2010_PITCH_CRC_MODE") == "docker":
        crc_port = os.environ.get("HLA2010_PITCH_CRC_PORT", "8989")
        return f"localhost;;crcAddress=127.0.0.1:{crc_port}"
    return os.environ.get("HLA2010_PITCH_FEDPRO_ADDRESS", "localhost")


def pitch_connect_local_settings_designator() -> str:
    return pitch_fedpro_local_settings_designator()


def _candidate_paths(*parts: str) -> list[Path]:
    return [_project_root().joinpath(*parts)]


def _first_existing(candidates: Sequence[Path], marker: str) -> Path | None:
    for path in candidates:
        if (path / marker).exists():
            return path
    return None


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


def _ensure_pitch_free_eula_accepted(runtime_state_dir: Path) -> None:
    settings_path = runtime_state_dir / "prti_common.settings"
    if settings_path.exists():
        lines = settings_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    replaced = False
    updated_lines: list[str] = []
    for line in lines:
        if line.strip().startswith("accepted"):
            updated_lines.append("accepted = true")
            replaced = True
        else:
            updated_lines.append(line)
    if not replaced:
        if updated_lines and updated_lines[-1] != "":
            updated_lines.append("")
        updated_lines.append("accepted = true")
    settings_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _upsert_pitch_settings(settings_path: Path, replacements: dict[str, str]) -> None:
    if settings_path.exists():
        lines = settings_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    seen: set[str] = set()
    updated_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        key = stripped.split("=", 1)[0] if "=" in stripped else ""
        if key in replacements:
            updated_lines.append(f"{key}={replacements[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)
    for key, value in replacements.items():
        if key not in seen:
            if updated_lines and updated_lines[-1] != "":
                updated_lines.append("")
            updated_lines.append(f"{key}={value}")
    settings_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _parse_pitch_extra_settings(env_var: str) -> dict[str, str]:
    raw = os.environ.get(env_var, "")
    if not raw.strip():
        return {}
    replacements: dict[str, str] = {}
    for line in raw.replace(";", "\n").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        key = key.strip()
        if not key:
            continue
        replacements[key] = value.strip()
    return replacements


def _normalize_pitch_crc_settings(runtime_state_dir: Path, *, crc_mode: str = "local") -> None:
    replacements = {
        "CRC.requireWebViewPassPhrase": "false",
        "CRC.webViewPassPhrase": "",
    }
    heartbeat_enable = os.environ.get("HLA2010_PITCH_CRC_HEARTBEAT_ENABLE")
    heartbeat_interval = os.environ.get("HLA2010_PITCH_CRC_HEARTBEAT_INTERVAL")
    heartbeat_action = os.environ.get("HLA2010_PITCH_CRC_HEARTBEAT_ACTION")
    if heartbeat_enable is not None:
        replacements["CRC.heartbeat.enable"] = heartbeat_enable
    if heartbeat_interval is not None:
        replacements["CRC.heartbeat.interval"] = heartbeat_interval
    if heartbeat_action is not None:
        replacements["CRC.heartbeat.action"] = heartbeat_action
    if crc_mode == "docker":
        replacements["CRC.skipConnectivityCheck"] = "true"
    _upsert_pitch_settings(runtime_state_dir / "prti1516eCRC.settings", replacements)


def _normalize_pitch_lrc_settings(runtime_state_dir: Path, *, crc_mode: str = "local") -> None:
    replacements = _parse_pitch_extra_settings("HLA2010_PITCH_LRC_EXTRA_SETTINGS")
    peer_heartbeat_interval = os.environ.get("HLA2010_PITCH_LRC_PEER_HEARTBEAT_INTERVAL_MILLIS")
    if peer_heartbeat_interval is not None:
        replacements["se.pitch.prti1516e.peerHeartbeatIntervalMillis"] = peer_heartbeat_interval
    if replacements:
        _upsert_pitch_settings(runtime_state_dir / "prti1516eLRC.settings", replacements)
    if crc_mode != "docker":
        return

    advertise_address = os.environ.get("HLA2010_PITCH_LRC_ADVERTISE_ADDRESS", "host.docker.internal")
    tcp_start = os.environ.get("HLA2010_PITCH_LRC_TCP_PORT_START", "6010")
    tcp_end = os.environ.get("HLA2010_PITCH_LRC_TCP_PORT_END", "6099")
    udp_start = os.environ.get("HLA2010_PITCH_LRC_UDP_PORT_START", "5010")
    udp_end = os.environ.get("HLA2010_PITCH_LRC_UDP_PORT_END", "5099")
    _upsert_pitch_settings(
        runtime_state_dir / "prti1516eLRC.settings",
        {
            "LRC.TCP.advertise.mode": "User",
            "LRC.TCP.advertise.address": advertise_address,
            "LRC.TCP.port-range.start": tcp_start,
            "LRC.TCP.port-range.end": tcp_end,
            "LRC.TCP.port-range.allow-fallback": "false",
            "LRC.UDP.port-range.start": udp_start,
            "LRC.UDP.port-range.end": udp_end,
            "LRC.UDP.port-range.allow-fallback": "false",
            "LRC.skipConnectivityCheck": "true",
        },
    )


def _normalize_pitch_fedpro_logging(runtime_state_dir: Path) -> None:
    log_dir = runtime_state_dir.parent / "logs" / "FedProServer"
    log_dir.mkdir(parents=True, exist_ok=True)
    _upsert_pitch_settings(
        runtime_state_dir / "FedProServer.logging",
        {
            "java.util.logging.ConsoleHandler.level": "ALL",
            "java.util.logging.FileHandler.pattern": "%h/logs/FedProServer/FedProServer-%g.log",
            "se.pitch.fedpro.level": os.environ.get("HLA2010_PITCH_FEDPRO_LOG_LEVEL", "FINE"),
            "se.pitch.prti1516e.level": os.environ.get("HLA2010_PITCH_LRC_LOG_LEVEL", "INFO"),
        },
    )


def _normalize_pitch_fedpro_timeouts(runtime_state_dir: Path) -> None:
    replacements = _parse_pitch_extra_settings("HLA2010_PITCH_FEDPRO_EXTRA_SETTINGS")
    timeout_heart_seconds = os.environ.get("HLA2010_PITCH_FEDPRO_TIMEOUT_HEART_SECONDS")
    timeout_purge_seconds = os.environ.get("HLA2010_PITCH_FEDPRO_TIMEOUT_PURGE_SECONDS")
    if timeout_heart_seconds is not None:
        replacements["timeout-heart-seconds"] = timeout_heart_seconds
    if timeout_purge_seconds is not None:
        replacements["timeout-purge-seconds"] = timeout_purge_seconds
    if replacements:
        _upsert_pitch_settings(runtime_state_dir / "FedProServer.properties", replacements)


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

    lib_dir = home / "lib"
    classpath = tuple(sorted(lib_dir.glob("*.jar")))
    if not classpath:
        raise BackendUnavailableError(f"Pitch runtime at {home} does not contain RTI jars")

    java_candidates: list[Path] = []
    external_java_home = os.environ.get("HLA2010_PITCH_JAVA_HOME")
    if external_java_home:
        java_candidates.append(Path(external_java_home).expanduser())
    java_candidates.extend(
        (
            home / "Contents" / "Home",
            home / "jre",
            home / ".install4j" / "jre.bundle" / "Contents" / "Home",
        )
    )
    java_home = next((path for path in java_candidates if (path / "bin" / "java").exists()), None)
    if java_home is None:
        raise BackendUnavailableError(f"Pitch runtime at {home} does not contain a bundled Java runtime")

    library_candidates = (
        home / ".i4j_external_12081" / "lib",
        lib_dir,
    )
    java_library_path: list[Path] = []
    seen: set[Path] = set()
    for candidate in library_candidates:
        if candidate.exists() and candidate not in seen:
            java_library_path.append(candidate)
            seen.add(candidate)
        clang12 = candidate / "clang12"
        if clang12.exists() and clang12 not in seen:
            java_library_path.append(clang12)
            seen.add(clang12)

    return PitchRuntime(
        home=home,
        java_home=java_home,
        classpath=classpath,
        java_library_path=tuple(java_library_path),
    )


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
    crc_mode: str | None = None,
) -> Path:
    """Materialize a local Pitch user-home."""

    source_user_home = runtime.home / "user.home"
    if not source_user_home.exists():
        source_user_home = runtime.default_user_home
    pitch_user_home = Path(user_home).expanduser() if user_home is not None else runtime.default_user_home
    pitch_user_home.mkdir(parents=True, exist_ok=True)
    marker_path = pitch_user_home / _PITCH_USER_HOME_MARKER
    runtime_state_dir = pitch_user_home / "prti1516e"
    should_seed = not marker_path.exists() and not runtime_state_dir.exists()
    if should_seed and source_user_home.exists() and source_user_home != pitch_user_home:
        shutil.copytree(source_user_home, pitch_user_home, dirs_exist_ok=True)
    if not marker_path.exists():
        marker_path.write_text(f"seeded-from={source_user_home}\n", encoding="utf-8")
    runtime_state_dir.mkdir(parents=True, exist_ok=True)
    _ensure_pitch_free_eula_accepted(runtime_state_dir)
    selected_crc_mode = crc_mode or os.environ.get("HLA2010_PITCH_CRC_MODE", "local")
    _normalize_pitch_crc_settings(runtime_state_dir, crc_mode=selected_crc_mode)
    _normalize_pitch_lrc_settings(runtime_state_dir, crc_mode=selected_crc_mode)
    _normalize_pitch_fedpro_logging(runtime_state_dir)
    _normalize_pitch_fedpro_timeouts(runtime_state_dir)
    try:
        list_pitch_licenses(runtime.home, user_home=pitch_user_home)
    except Exception:
        pass
    return pitch_user_home


def _isolated_pitch_user_home_base() -> Path:
    return _local_state_root() / "pitch" / "runtime-homes"


def _allocate_isolated_pitch_user_home() -> Path:
    base = _isolated_pitch_user_home_base()
    base.mkdir(parents=True, exist_ok=True)
    return base / f"launch-{uuid4().hex}"


def _drain_process_output(process: Any) -> tuple[str, str]:
    try:
        stdout, stderr = process.communicate(timeout=1)
        return stdout or "", stderr or ""
    except Exception:
        return "", ""


def _format_process_diagnostics(name: str, stdout: str, stderr: str) -> str:
    lines: list[str] = [f"{name} diagnostics:"]
    if stdout.strip():
        excerpt = "\n".join(stdout.strip().splitlines()[-20:])
        lines.append(f"{name} stdout tail:\n{excerpt}")
    if stderr.strip():
        excerpt = "\n".join(stderr.strip().splitlines()[-20:])
        lines.append(f"{name} stderr tail:\n{excerpt}")
    return "\n".join(lines)


def _launcher_mode_attempts(explicit_mode: str | None, env: dict[str, str]) -> tuple[str, ...]:
    if explicit_mode:
        return (explicit_mode,)
    configured = env.get("HLA2010_PITCH_LAUNCHER_FALLBACKS", "raw,install4j")
    modes = tuple(part.strip() for part in configured.split(",") if part.strip())
    return modes or ("raw",)


def launch_pitch_py4j_gateway(
    *,
    pitch_home: str | os.PathLike[str] | None = None,
    port: int = 25333,
    die_on_exit: bool = True,
    return_proc: bool = False,
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
        return_proc=return_proc,
    )


def launch_pitch_runtime(
    *,
    pitch_home: str | os.PathLike[str] | None = None,
    args: Sequence[str] = ("-nogui", "-verbose"),
    launcher_mode: str | None = None,
    ui_automation: bool | None = None,
    crc_mode: str | None = None,
    _subprocess: Any = subprocess,
    _wait_for_process_boot=None,
    _wait_for_tcp_listener=None,
) -> RuntimeProcess:
    repo_root = _project_root()
    runtime = discover_pitch_runtime(pitch_home)
    env = dict(os.environ)
    selected_crc_mode = crc_mode or env.get("HLA2010_PITCH_CRC_MODE", "local")
    fedpro_listener_timeout = float(env.get("HLA2010_PITCH_FEDPRO_LISTENER_TIMEOUT_SECONDS", "20.0"))
    crc_listener_timeout = float(env.get("HLA2010_PITCH_CRC_LISTENER_TIMEOUT_SECONDS", "45.0"))
    crc_port = int(env.get("HLA2010_PITCH_CRC_PORT", "8989"))
    fedpro_port = int(env.get("HLA2010_PITCH_FEDPRO_PORT", "15164"))
    process_boot_timeout = float(env.get("HLA2010_PITCH_PROCESS_BOOT_TIMEOUT_SECONDS", "10.0"))
    startup_retries = int(env.get("HLA2010_PITCH_STARTUP_RETRIES", "1"))
    launcher_modes = _launcher_mode_attempts(launcher_mode, env)

    if selected_crc_mode == "docker":
        crc_script = "run_pitch_docker_crc.sh"
        runtime_name = "pitch-docker"
    elif selected_crc_mode == "local":
        crc_script = "run_pitch_local.sh"
        runtime_name = "pitch"
    else:
        raise BackendUnavailableError(f"Unsupported Pitch CRC mode {selected_crc_mode!r}; expected 'local' or 'docker'")

    if _wait_for_process_boot is None or _wait_for_tcp_listener is None:
        from hla.rti import wait_for_process_boot as _default_wait_for_process_boot
        from hla.rti import wait_for_tcp_listener as _default_wait_for_tcp_listener

        _wait_for_process_boot = _wait_for_process_boot or _default_wait_for_process_boot
        _wait_for_tcp_listener = _wait_for_tcp_listener or _default_wait_for_tcp_listener

    last_exc: BaseException | None = None
    diagnostics: list[str] = []
    for attempt in range(startup_retries + 1):
        isolated_home: Path | None = None
        if attempt == 0:
            pitch_user_home = prepare_pitch_user_home(runtime, crc_mode=selected_crc_mode)
        else:
            isolated_home = _allocate_isolated_pitch_user_home()
            pitch_user_home = prepare_pitch_user_home(
                runtime,
                user_home=isolated_home,
                crc_mode=selected_crc_mode,
            )

        launch_env = dict(env)
        launch_env["HLA2010_PITCH_HOME"] = str(runtime.home)
        launch_env["HOME"] = str(pitch_user_home)
        launch_env["HLA2010_PITCH_USER_HOME"] = str(pitch_user_home)
        launch_env["HLA2010_PITCH_JAVA_HOME"] = str(runtime.java_home)
        launch_env["INSTALL4J_JAVA_HOME"] = str(runtime.java_home)
        launch_env["HLA2010_PITCH_CRC_MODE"] = selected_crc_mode
        selected_launcher_mode = launcher_modes[min(attempt, len(launcher_modes) - 1)]
        launch_env["HLA2010_PITCH_LAUNCHER_MODE"] = selected_launcher_mode
        if ui_automation is not None:
            launch_env["HLA2010_PITCH_UI_AUTOMATION"] = "1" if ui_automation else "0"

        crc_command = [str(repo_root / "scripts" / crc_script), *args]
        crc_env = dict(launch_env)
        if selected_crc_mode == "docker":
            crc_env["HOME"] = os.environ.get("HOME", str(Path.home()))
        crc_process = _subprocess.Popen(
            crc_command,
            env=crc_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=repo_root,
        )
        children: tuple[Any, ...] = ()
        if selected_crc_mode == "local":
            fedpro_classpath = os.pathsep.join(str(path) for path in sorted((runtime.home / "lib").glob("*.jar")))
            fedpro_command = [
                str(runtime.java_bin),
                f"-Djava.util.logging.config.file={pitch_user_home / 'prti1516e' / 'FedProServer.logging'}",
                "-Dse.pitch.prti1516e.useSystemWideLicenseFile=true",
                "-Dse.pitch.fedpro.acceptRtiAddressFromClient=true",
                "-Dse.pitch.fedpro.acceptAdditionalSettingsFromClient=true",
                f"-Duser.home={pitch_user_home}",
                f"-Djava.library.path={os.pathsep.join(str(item) for item in runtime.java_library_path)}",
                "-classpath",
                fedpro_classpath,
                "se.pitch.fedpro.server.hla.FedProServerApp",
            ]
            fedpro_process = _subprocess.Popen(
                fedpro_command,
                env=launch_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=runtime.home,
            )
            children = (fedpro_process,)
        try:
            _wait_for_process_boot(crc_process, timeout=process_boot_timeout)
            for child in children:
                _wait_for_process_boot(child, timeout=process_boot_timeout)
            _wait_for_tcp_listener("127.0.0.1", fedpro_port, timeout=fedpro_listener_timeout)
            _wait_for_tcp_listener("127.0.0.1", crc_port, timeout=crc_listener_timeout)
            time.sleep(float(launch_env.get("HLA2010_PITCH_STARTUP_SETTLE_SECONDS", "1.0")))
            cleanup_paths = (isolated_home,) if isolated_home is not None else ()
            return RuntimeProcess(
                name=runtime_name,
                process=crc_process,
                env=launch_env,
                host="127.0.0.1",
                tcp_port=fedpro_port,
                children=children,
                cleanup_paths=cleanup_paths,
            )
        except Exception as exc:
            last_exc = exc
            for child in children:
                if child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=5)
            if crc_process.poll() is None:
                crc_process.terminate()
                try:
                    crc_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    crc_process.kill()
                    crc_process.wait(timeout=5)
            crc_stdout, crc_stderr = _drain_process_output(crc_process)
            diagnostics.append(
                _format_process_diagnostics(
                    f"pitch crc attempt {attempt + 1} ({selected_launcher_mode})",
                    crc_stdout,
                    crc_stderr,
                )
            )
            for index, child in enumerate(children, start=1):
                child_stdout, child_stderr = _drain_process_output(child)
                diagnostics.append(
                    _format_process_diagnostics(
                        f"pitch child {index} attempt {attempt + 1} ({selected_launcher_mode})",
                        child_stdout,
                        child_stderr,
                    )
                )
            if isolated_home is not None:
                shutil.rmtree(isolated_home, ignore_errors=True)
            if attempt >= startup_retries:
                break

    detail = "\n\n".join(block for block in diagnostics if block.strip())
    if isinstance(last_exc, BackendUnavailableError):
        raise BackendUnavailableError(f"{last_exc}\n\n{detail}" if detail else str(last_exc)) from last_exc
    if last_exc is not None:
        raise BackendUnavailableError(f"Pitch runtime failed to launch after retries.\n\n{detail}") from last_exc
    raise BackendUnavailableError("Pitch runtime failed to launch for an unknown reason")


__all__ = [
    "PitchRuntime",
    "PitchLicenseRecord",
    "discover_pitch_runtime",
    "list_pitch_licenses",
    "prepare_pitch_user_home",
    "pitch_connect_local_settings_designator",
    "pitch_fedpro_local_settings_designator",
    "launch_pitch_py4j_gateway",
    "launch_pitch_runtime",
    "_parse_pitch_license_list",
]
