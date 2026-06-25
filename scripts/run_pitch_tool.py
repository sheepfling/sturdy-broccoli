#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()
TOOL_LABEL = "./tools/pitch"


def _python_bin() -> str:
    venv_python = SCRIPT_REPO_ROOT / ".venv" / "bin" / "python"
    if venv_python.is_file() and os.access(venv_python, os.X_OK):
        return str(venv_python)
    python3 = shutil.which("python3")
    if python3:
        return python3
    python = shutil.which("python")
    if python:
        return python
    raise SystemExit("error: python3 or python not found")


def _env_with_script_name(env: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(os.environ if env is None else env)
    merged.setdefault("HLA2010_SCRIPT_NAME", TOOL_LABEL)
    return merged


def _run(
    args: Sequence[str | Path],
    *,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=PROJECT_ROOT,
        env=_env_with_script_name(env),
        capture_output=capture_output,
        text=True,
        check=check,
    )


def _shell_script(path: Path, *args: str) -> list[str]:
    return ["bash", str(path), *args]


def _log(message: str) -> None:
    print(f"[{TOOL_LABEL}] {message}")


def _warn(message: str) -> None:
    print(f"[{TOOL_LABEL}] warning: {message}", file=sys.stderr)


def _preflight_artifact_dir() -> Path:
    return Path(os.environ.get("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(PROJECT_ROOT / "artifacts" / "preflight_artifacts")))


def _preflight_artifact_path() -> Path:
    return _preflight_artifact_dir() / "pitch-preflight.json"


def _preflight_has_json_file(args: Sequence[str]) -> bool:
    return any(arg == "--json-file" or arg.startswith("--json-file=") for arg in args)


def _run_persisted_preflight(extra_args: Sequence[str]) -> int:
    _preflight_artifact_dir().mkdir(parents=True, exist_ok=True)
    command = _shell_script(SCRIPT_REPO_ROOT / "scripts" / "check_pitch_preflight.sh", *extra_args)
    if not _preflight_has_json_file(extra_args):
        command.extend(["--json-file", str(_preflight_artifact_path())])
    return _run(command).returncode


def _emit_runtime_reports(profile: str = "pitch") -> None:
    _run(_shell_script(SCRIPT_REPO_ROOT / "scripts" / "ci" / "emit_vendor_runtime_reports.sh", "vendor-green", profile))


def _apply_pitch_preflight_runtime_env(artifact_path: Path) -> None:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    ports = payload.get("ports") or {}
    runtime = payload.get("runtime") or {}
    crc = ports.get("crc") or {}
    fedpro = ports.get("fedpro") or {}
    if "port" in crc:
        os.environ["HLA2010_PITCH_CRC_PORT"] = str(crc["port"])
    if "port" in fedpro:
        os.environ["HLA2010_PITCH_FEDPRO_PORT"] = str(fedpro["port"])
    if runtime.get("container_name"):
        os.environ["HLA2010_PITCH_DOCKER_NAME"] = str(runtime["container_name"])


def _require_preflight() -> bool:
    _preflight_artifact_dir().mkdir(parents=True, exist_ok=True)
    result = _run(
        [
            *_shell_script(SCRIPT_REPO_ROOT / "scripts" / "check_pitch_preflight.sh"),
            "--json-file",
            str(_preflight_artifact_path()),
        ]
    )
    if result.returncode != 0:
        return False
    _apply_pitch_preflight_runtime_env(_preflight_artifact_path())
    return True


def _enable_pitch_docker_runtime_mode() -> None:
    os.environ["HLA2010_PITCH_CRC_MODE"] = "docker"
    os.environ["HLA2010_PITCH_DOCKER_BUILD"] = "0"
    os.environ["HLA2010_PITCH_DOCKER_ATTACH_EXISTING"] = "1"
    os.environ["HLA2010_PITCH_DOCKER_NAME"] = _container_name()
    os.environ["HLA2010_PITCH_CRC_PORT"] = str(_crc_port())
    os.environ["HLA2010_PITCH_FEDPRO_PORT"] = str(_fedpro_port())


def _run_with_preflight(profile: str, command: Sequence[str | Path]) -> int:
    if _require_preflight():
        _enable_pitch_docker_runtime_mode()
        return _run(command).returncode
    _emit_runtime_reports(profile)
    return 1


def _container_name() -> str:
    return os.environ.get("HLA2010_PITCH_DOCKER_NAME", "hla2010-pitch-crc")


def _image_name() -> str:
    return os.environ.get("HLA2010_PITCH_DOCKER_IMAGE", "hla2010-pitch-prti-free-crc:5.5.10")


def _crc_port() -> int:
    return int(os.environ.get("HLA2010_PITCH_CRC_PORT", "8989"))


def _fedpro_port() -> int:
    return int(os.environ.get("HLA2010_PITCH_FEDPRO_PORT", "15164"))


def _resolve_pitch_home() -> Path:
    env_home = os.environ.get("HLA2010_PITCH_HOME")
    if env_home:
        candidate = Path(env_home)
        if candidate.is_dir():
            return candidate
        raise SystemExit(f"error: HLA2010_PITCH_HOME does not point at a Pitch runtime directory: {env_home}")
    bundled = SCRIPT_REPO_ROOT / "third_party" / "pitch" / "PITCH-prti1516e-manual"
    if bundled.is_dir():
        return bundled
    zip_path = SCRIPT_REPO_ROOT / "third_party" / "pitch" / "HLA_PITCH_linux.zip"
    expanded_root = SCRIPT_REPO_ROOT / "third_party" / "pitch" / "HLA_PITCH_linux" / "PITCH-prti1516e-manual"
    if zip_path.is_file():
        _run([_python_bin(), "-m", "zipfile", "-e", str(zip_path), str(SCRIPT_REPO_ROOT / "third_party" / "pitch")], check=True)
    elif expanded_root.is_dir():
        shutil.copytree(expanded_root, bundled, dirs_exist_ok=True)
    if bundled.is_dir():
        return bundled
    raise SystemExit(
        "error: Pitch runtime bundle not found.\n"
        "Put the extracted vendor runtime at third_party/pitch/PITCH-prti1516e-manual\n"
        "or set HLA2010_PITCH_HOME."
    )


def _resolve_pitch_user_home() -> str:
    env = _env_with_script_name()
    env["HLA2010_PITCH_HOME"] = str(_resolve_pitch_home())
    result = _run(_shell_script(SCRIPT_REPO_ROOT / "scripts" / "setup_pitch_state.sh"), env=env, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def _wait_for_port(host: str, port: int, timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.2)
    raise SystemExit(1)


def _ensure_docker() -> None:
    if not shutil.which("docker"):
        raise SystemExit("error: docker CLI not found")
    result = _run(["docker", "info"])
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _docker_container_exists() -> bool:
    result = _run(["docker", "ps", "-a", "--format", "{{.Names}}"], capture_output=True)
    return result.returncode == 0 and _container_name() in result.stdout.splitlines()


def _docker_container_running() -> bool:
    result = _run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True)
    return result.returncode == 0 and _container_name() in result.stdout.splitlines()


def _install_pitch_docker() -> int:
    if not _require_preflight():
        return 1
    pitch_home = _resolve_pitch_home()
    pitch_user_home = _resolve_pitch_user_home()
    _log(f"Pitch runtime: {pitch_home}")
    _log(f"Pitch user home: {pitch_user_home}")
    _ensure_docker()
    result = _run(
        [
            "docker",
            "build",
            "-t",
            _image_name(),
            "-f",
            str(SCRIPT_REPO_ROOT / "scripts" / "pitch_crc_free.Dockerfile"),
            str(pitch_home),
        ]
    )
    if result.returncode != 0:
        return result.returncode
    inspect = _run(["docker", "image", "inspect", _image_name()])
    if inspect.returncode == 0:
        _log(f"Pitch Docker image ready: {_image_name()}")
    return inspect.returncode


def _start_pitch_docker() -> int:
    if not _require_preflight():
        return 1
    pitch_home = _resolve_pitch_home()
    pitch_user_home = _resolve_pitch_user_home()
    _ensure_docker()
    if _run(["docker", "image", "inspect", _image_name()]).returncode != 0:
        install_status = _install_pitch_docker()
        if install_status != 0:
            return install_status
    if _docker_container_running():
        _log(f"Pitch Docker already running: {_container_name()}")
        return 0
    if _docker_container_exists():
        _run(["docker", "rm", "-f", _container_name()])
    env = _env_with_script_name()
    env.update(
        {
            "HLA2010_PITCH_HOME": str(pitch_home),
            "HLA2010_PITCH_USER_HOME": pitch_user_home,
            "HLA2010_PITCH_CRC_MODE": "docker",
            "HLA2010_PITCH_DOCKER_IMAGE": _image_name(),
            "HLA2010_PITCH_DOCKER_BUILD": "0",
            "HLA2010_PITCH_DOCKER_NAME": _container_name(),
            "HLA2010_PITCH_DOCKER_DETACH": "1",
        }
    )
    if _run(_shell_script(SCRIPT_REPO_ROOT / "scripts" / "run_pitch_docker_crc.sh"), env=env).returncode != 0:
        return 1
    _wait_for_port("127.0.0.1", _crc_port(), 45)
    _wait_for_port("127.0.0.1", _fedpro_port(), 45)
    _log(f"Pitch Docker running: {_container_name()}")
    _log(f"CRC:    127.0.0.1:{_crc_port()}")
    _log(f"FedPro: 127.0.0.1:{_fedpro_port()}")
    return 0


def _stop_pitch_docker() -> int:
    _ensure_docker()
    if _docker_container_exists():
        _run(["docker", "rm", "-f", _container_name()])
        _log(f"Stopped: {_container_name()}")
    else:
        _log("Pitch Docker is not running.")
    return 0


def _status_pitch_docker() -> int:
    pitch_home = _resolve_pitch_home()
    pitch_user_home = _resolve_pitch_user_home()
    _log(f"Pitch runtime: {pitch_home}")
    _log(f"Pitch user home: {pitch_user_home}")
    _log(f"Image: {_image_name()}")
    _log(f"Container: {_container_name()}")
    if _docker_container_running():
        _log("Status: running")
        _run(["docker", "ps", "--filter", f"name=^{_container_name()}$", "--format", "Ports: {{.Ports}}"])
    elif _docker_container_exists():
        _log("Status: stopped")
    else:
        _log("Status: not created")
    return 0


def _logs_pitch_docker() -> int:
    _ensure_docker()
    if not _docker_container_exists():
        _warn("Pitch Docker container does not exist.")
        return 1
    return _run(["docker", "logs", _container_name()]).returncode


def _run_best_effort(profile: str) -> int:
    status = _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_runtime_smoke.py"), profile]).returncode
    _emit_runtime_reports(profile)
    return status


def _doctor_pitch_docker() -> int:
    preflight = _run(_shell_script(SCRIPT_REPO_ROOT / "scripts" / "check_pitch_preflight.sh", "--json"), capture_output=True)
    pitch_home = _resolve_pitch_home()
    pitch_user_home = _resolve_pitch_user_home()
    _log(f"Pitch runtime: {pitch_home}")
    _log(f"Pitch user home: {pitch_user_home}")
    docker_ready = False
    docker_bin = shutil.which("docker")
    if docker_bin:
        _log(f"Docker CLI: {docker_bin}")
        if _run(["docker", "info"]).returncode == 0:
            _log("Docker daemon: reachable")
            docker_ready = True
        else:
            _warn("Docker daemon: not reachable")
    else:
        _warn("Docker CLI: missing")
    preflight_json = preflight.stdout.strip()
    if preflight_json:
        payload = json.loads(preflight_json)
        print(f"environment: {payload.get('environment', 'unknown')}")
        print(f"result: {payload.get('result', 'unknown')}")
        print(f"next step: {payload.get('next_step', './tools/pitch preflight')}")
    if docker_ready:
        if _run(["docker", "image", "inspect", _image_name()]).returncode == 0:
            _log(f"Image: present ({_image_name()})")
        else:
            _warn(f"Image: missing ({_image_name()})")
        if _docker_container_running():
            _log(f"Container: running ({_container_name()})")
        elif _docker_container_exists():
            _log(f"Container: stopped ({_container_name()})")
        else:
            _log(f"Container: absent ({_container_name()})")
    else:
        _warn("Skipping container/image checks because Docker is unavailable")
    return 0


def _usage() -> str:
    return f"""usage: {TOOL_LABEL} [preflight|install|start|stop|restart|status|logs|smoke|smoke-best-effort|verify|verify-best-effort|202x-certify|202x-micro-certify|fom-smoke|fom-smoke-compare|all|doctor]

Simple Pitch Docker workflow:
  {TOOL_LABEL} preflight [--json] # check Docker and Pitch runtime prerequisites
  {TOOL_LABEL} install   # discover runtime, seed user.home, build the image
  {TOOL_LABEL} start     # start CRC + FedPro in Docker and wait for ports
  {TOOL_LABEL} smoke     # run the real Pitch smoke test
  {TOOL_LABEL} smoke-best-effort # run Pitch smoke and treat blocked local preflight as report-only
  {TOOL_LABEL} verify    # run the full real Pitch backend matrix
  {TOOL_LABEL} verify-best-effort # run Pitch verify and treat blocked local preflight as report-only
  {TOOL_LABEL} 202x-certify # run the 202X surface audit plus trial-safe real-runtime credence packet
  {TOOL_LABEL} 202x-micro-certify # run the bounded three-family micro comparison across real Pitch 2010 and pitch-202x adapter routes
  {TOOL_LABEL} fom-smoke [--kind ...] [--packet ...] # probe example-FOM load/lookup support across the two Pitch runtimes and the explicit pitch-202x-* adapter routes
  {TOOL_LABEL} fom-smoke-compare # generate a side-by-side packet over the real Pitch 2010 and pitch-202x adapter smoke artifacts
  {TOOL_LABEL} save-restore # report the current real Pitch save/restore gap profile
  {TOOL_LABEL} save-restore-probe # run the current narrow real Pitch save/restore probe
  {TOOL_LABEL} save-restore-review [repeat-count] # run repeated review for the real Pitch save/restore probe
  {TOOL_LABEL} ddm       # report the current real Pitch DDM gap profile
  {TOOL_LABEL} ddm-probe # run the current narrow real Pitch DDM probe
  {TOOL_LABEL} ddm-review [repeat-count] # run repeated review for the real Pitch DDM probe
  {TOOL_LABEL} negotiated # report the current real Pitch negotiated-ownership gap profile
  {TOOL_LABEL} negotiated-probe # run the current narrow real Pitch negotiated-ownership probe
  {TOOL_LABEL} negotiated-review [repeat-count] # run repeated review for the real Pitch negotiated-ownership probe
  {TOOL_LABEL} time-window-probe # run the Pitch-safe two-federate time-window future-exclusion probe
  {TOOL_LABEL} time-window-review [repeat-count] # run repeated review for the Pitch-safe time-window future-exclusion probe
  {TOOL_LABEL} time-window-restore-state-probe # run the Pitch-safe two-federate time-window restore-state probe
  {TOOL_LABEL} time-window-restore-state-review [repeat-count] # run repeated review for the Pitch-safe time-window restore-state probe
  {TOOL_LABEL} lost-federate # report the current real Pitch lost-federate gap profile
  {TOOL_LABEL} lost-federate-probe # run the current narrow real Pitch lost-federate probe
  {TOOL_LABEL} lost-federate-review [repeat-count] # run repeated review for the real Pitch lost-federate probe
  {TOOL_LABEL} crc-macos-repro [args...] # run the macOS CRC startup reproducer
  {TOOL_LABEL} crc-docker-repro # run the Docker CRC startup reproducer
  {TOOL_LABEL} all       # install, then smoke, then verify
  {TOOL_LABEL} logs      # show container logs
  {TOOL_LABEL} stop      # stop and remove the container
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ["start"]
    command = args[0]
    rest = args[1:]

    if command in {"help", "-h", "--help"}:
        print(_usage(), end="")
        return 0
    if command == "preflight":
        status = _run_persisted_preflight(rest)
        _emit_runtime_reports("pitch")
        return status
    if command == "install":
        return _install_pitch_docker()
    if command == "start":
        return _start_pitch_docker()
    if command == "stop":
        return _stop_pitch_docker()
    if command == "restart":
        _stop_pitch_docker()
        return _start_pitch_docker()
    if command == "status":
        return _status_pitch_docker()
    if command == "logs":
        return _logs_pitch_docker()
    if command == "smoke":
        _log("running Pitch smoke")
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-smoke"]).returncode
    if command == "smoke-best-effort":
        _log("running Pitch smoke (best-effort)")
        return _run_best_effort("pitch-smoke")
    if command == "verify":
        _log("running Pitch verify")
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-verify"]).returncode
    if command == "verify-best-effort":
        _log("running Pitch verify (best-effort)")
        return _run_best_effort("pitch-verify")
    if command == "202x-certify":
        return _run_with_preflight("pitch-verify", [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "run_pitch_202x_certification.py")])
    if command == "202x-micro-certify":
        return _run_with_preflight(
            "pitch-verify",
            [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "run_pitch_202x_micro_certification.py")],
        )
    if command == "fom-smoke":
        if not _require_preflight():
            return 1
        _enable_pitch_docker_runtime_mode()
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "run_pitch_fom_smoke.py"), *rest]).returncode
    if command == "fom-smoke-compare":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "generate_pitch_fom_smoke_comparison.py"), *rest]).returncode
    if command == "save-restore":
        return _run_with_preflight("pitch-save-restore", [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-save-restore"])
    if command == "save-restore-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-save-restore-probe"]).returncode
    if command == "save-restore-review":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), "pitch-save-restore-probe", rest[0] if rest else "5"]).returncode
    if command == "ddm":
        return _run_with_preflight("pitch-ddm", [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-ddm"])
    if command == "ddm-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-ddm-probe"]).returncode
    if command == "ddm-review":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), "pitch-ddm-probe", rest[0] if rest else "5"]).returncode
    if command == "negotiated":
        return _run_with_preflight("pitch-negotiated", [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-negotiated"])
    if command == "negotiated-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-negotiated-probe"]).returncode
    if command == "negotiated-review":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), "pitch-negotiated-probe", rest[0] if rest else "5"]).returncode
    if command == "time-window-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-time-window-probe"]).returncode
    if command == "time-window-review":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), "pitch-time-window-probe", rest[0] if rest else "5"]).returncode
    if command == "time-window-restore-state-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-time-window-restore-state-probe"]).returncode
    if command == "time-window-restore-state-review":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), "pitch-time-window-restore-state-probe", rest[0] if rest else "5"]).returncode
    if command == "lost-federate":
        return _run_with_preflight("pitch-lost-federate", [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-lost-federate"])
    if command == "lost-federate-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-lost-federate-probe"]).returncode
    if command == "lost-federate-review":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), "pitch-lost-federate-probe", rest[0] if rest else "5"]).returncode
    if command == "crc-macos-repro":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "repro_pitch_crc_macos.py"), *rest]).returncode
    if command == "crc-docker-repro":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "repro_pitch_crc_docker.py"), *rest]).returncode
    if command == "all":
        install_status = _install_pitch_docker()
        if install_status != 0:
            return install_status
        smoke_status = _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-smoke"]).returncode
        if smoke_status != 0:
            return smoke_status
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "pitch-verify"]).returncode
    if command == "doctor":
        return _doctor_pitch_docker()
    print(_usage(), end="")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
