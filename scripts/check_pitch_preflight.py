#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

DEFAULT_PROJECT_ROOT = Path.cwd()
SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _log(script_name: str, title: str, detail: str) -> None:
    print(f"[{script_name}] {title}: {detail}")


def _docker_cli_path() -> str | None:
    return shutil.which("docker")


def _docker_available() -> tuple[str, str, bool]:
    docker_bin = _docker_cli_path()
    if not docker_bin:
        return ("missing", "missing: install Docker Desktop or Docker Engine first", False)
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ("blocked", "blocked: Docker CLI exists but the daemon is not reachable", False)
    return ("ok", f"ok: {docker_bin}", True)


def _docker_container_running(container_name: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and container_name in result.stdout.splitlines()


def _resolve_managed_container_port(container_name: str, internal_port: int) -> int | None:
    result = subprocess.run(
        ["docker", "port", container_name, f"{internal_port}/tcp"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    mapping = next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")
    if ":" not in mapping:
        return None
    try:
        return int(mapping.rsplit(":", 1)[1])
    except ValueError:
        return None


def _extract_pitch_zip(zip_path: Path, destination: Path) -> bool:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(destination)
    except (OSError, zipfile.BadZipFile):
        return False
    return True


def _resolve_pitch_home(root_dir: Path) -> Path | None:
    env_home = os.environ.get("HLA2010_PITCH_HOME")
    if env_home:
        candidate = Path(env_home)
        return candidate if candidate.is_dir() else None

    bundled = root_dir / "third_party" / "pitch" / "PITCH-prti1516e-manual"
    if bundled.is_dir():
        return bundled

    zip_path = root_dir / "third_party" / "pitch" / "HLA_PITCH_linux.zip"
    local_archive = root_dir / "third_party" / "pitch" / "HLA_PITCH_linux"
    if zip_path.is_file():
        _extract_pitch_zip(zip_path, root_dir / "third_party" / "pitch")
    elif (local_archive / "PITCH-prti1516e-manual").is_dir():
        shutil.copytree(local_archive / "PITCH-prti1516e-manual", bundled, dirs_exist_ok=True)

    return bundled if bundled.is_dir() else None


def _tmp_roots() -> tuple[Path, ...]:
    tmpdir = Path(tempfile.gettempdir()).resolve()
    roots = [
        tmpdir,
        Path("/tmp"),
        Path("/private/tmp"),
        Path("/var/tmp"),
    ]
    if str(tmpdir).startswith("/var/"):
        roots.append(Path("/private") / tmpdir.relative_to("/"))
    deduped: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            deduped.append(root)
            seen.add(key)
    return tuple(deduped)


def _render_path(repo_root: Path, raw: str | None) -> str | None:
    if not raw:
        return raw
    path = Path(raw).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError:
        pass
    for root in _tmp_roots():
        try:
            return f"<tmp>/{resolved.relative_to(root).as_posix()}"
        except ValueError:
            continue
    return resolved.as_posix()


def _sanitize_text(repo_root: Path, raw: str | None) -> str | None:
    if raw is None:
        return None
    return raw.replace(str(repo_root), "<repo>")


def _check_port_available(port: int) -> tuple[bool, str]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            sock.listen(1)
        except OSError as exc:
            return (False, str(exc))
    return (True, "")


def _find_available_port(*forbidden: int) -> int:
    blocked = {int(item) for item in forbidden}
    for _ in range(128):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = int(sock.getsockname()[1])
        if port not in blocked:
            return port
    raise RuntimeError("unable to find an available loopback port")


def _build_payload(
    *,
    repo_root: Path,
    platform: str,
    environment: str,
    result: str,
    docker_status: str,
    docker_detail: str,
    bundle_status: str,
    bundle_detail: str,
    user_home_detail: str,
    runtime_home_detail: str,
    runtime_marker_detail: str,
    container_name: str,
    image_name: str,
    crc_port: int,
    crc_port_status: str,
    crc_port_detail: str,
    fedpro_port: int,
    fedpro_port_status: str,
    fedpro_port_detail: str,
    next_step: str,
    exit_code: int,
) -> dict[str, object]:
    return {
        "tool": "pitch-preflight",
        "platform": platform,
        "environment": environment,
        "result": result,
        "checks": [
            {
                "name": "docker",
                "ok": docker_status == "ok",
                "status": docker_status,
                "detail": docker_detail,
            },
            {
                "name": "pitch_bundle",
                "ok": bundle_status == "ok",
                "status": bundle_status,
                "detail": _sanitize_text(repo_root, bundle_detail),
            },
            {
                "name": "pitch_user_home",
                "ok": bool(user_home_detail),
                "status": "ok" if user_home_detail else "missing",
                "detail": _render_path(repo_root, user_home_detail) or "missing user.home",
            },
            {
                "name": "crc_port",
                "ok": crc_port_status == "ok",
                "status": crc_port_status,
                "detail": crc_port_detail,
            },
            {
                "name": "fedpro_port",
                "ok": fedpro_port_status == "ok",
                "status": fedpro_port_status,
                "detail": fedpro_port_detail,
            },
        ],
        "runtime": {
            "home": _render_path(repo_root, runtime_home_detail),
            "required_marker": _render_path(repo_root, runtime_marker_detail),
            "user_home": _render_path(repo_root, user_home_detail),
            "image_name": image_name,
            "container_name": container_name,
        },
        "required_markers": {
            "runtime_home": _render_path(repo_root, runtime_marker_detail),
        },
        "ports": {
            "crc": {
                "host": "127.0.0.1",
                "port": crc_port,
                "status": crc_port_status,
                "detail": crc_port_detail,
            },
            "fedpro": {
                "host": "127.0.0.1",
                "port": fedpro_port,
                "status": fedpro_port_status,
                "detail": fedpro_port_detail,
            },
        },
        "next_step": next_step,
        "exit_code": exit_code,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Docker and bundled Pitch runtime readiness.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=DEFAULT_PROJECT_ROOT,
        help="Repository root used for bundled Pitch runtime discovery.",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--json-file", type=Path, help="write machine-readable JSON to this file")
    args = parser.parse_args()

    root_dir = args.project_root.resolve()
    script_name = os.environ.get("HLA2010_SCRIPT_NAME", Path(__file__).name)
    platform = " ".join(os.uname())
    container_name = os.environ.get("HLA2010_PITCH_DOCKER_NAME", "hla2010-pitch-crc")
    image_name = os.environ.get("HLA2010_PITCH_DOCKER_IMAGE", "hla2010-pitch-prti-free-crc:5.5.10")
    crc_port_explicit = "HLA2010_PITCH_CRC_PORT" in os.environ
    fedpro_port_explicit = "HLA2010_PITCH_FEDPRO_PORT" in os.environ
    crc_port = int(os.environ.get("HLA2010_PITCH_CRC_PORT", "8989"))
    fedpro_port = int(os.environ.get("HLA2010_PITCH_FEDPRO_PORT", "15164"))
    auto_ports = os.environ.get("HLA2010_PITCH_AUTO_PORTS", "1") == "1"

    status = 0
    docker_status, docker_detail, docker_ok = _docker_available()
    bundle_status = "ok"
    bundle_detail = "ok"
    user_home_detail = ""
    runtime_home_detail = ""
    runtime_marker_detail = ""
    crc_port_status = "ok"
    crc_port_detail = "ok"
    fedpro_port_status = "ok"
    fedpro_port_detail = "ok"
    managed_container_running = docker_ok and _docker_container_running(container_name)

    if not args.json:
        _log(script_name, "Pitch preflight", "starting")
        _log(script_name, "platform", platform)
        _log(script_name, "docker", docker_detail)

    if docker_status != "ok":
        status = 1

    resolved_home = _resolve_pitch_home(root_dir)
    if resolved_home is not None:
        runtime_home_detail = str(resolved_home)
        runtime_marker_detail = str(resolved_home / "lib" / "prtifull.jar")
        if Path(runtime_marker_detail).is_file():
            bundle_detail = f"ok: {resolved_home}"
            user_home_detail = os.environ.get(
                "HLA2010_PITCH_USER_HOME",
                str(root_dir / ".local" / "pitch" / "user-home"),
            )
        else:
            status = 1
            bundle_status = "blocked"
            bundle_detail = f"blocked: required runtime marker is missing: {runtime_marker_detail}"
    else:
        status = 1
        if os.environ.get("HLA2010_PITCH_HOME"):
            bundle_status = "blocked"
            bundle_detail = (
                "blocked: HLA2010_PITCH_HOME does not point at a Pitch runtime directory: "
                f"{os.environ['HLA2010_PITCH_HOME']}"
            )
        elif (root_dir / "third_party" / "pitch" / "HLA_PITCH_linux.zip").is_file():
            bundle_status = "blocked"
            bundle_detail = (
                f"blocked: archive exists at {root_dir / 'third_party' / 'pitch' / 'HLA_PITCH_linux.zip'} "
                "but extraction failed"
            )
        elif (root_dir / "third_party" / "pitch" / "HLA_PITCH_linux").is_dir():
            bundle_status = "blocked"
            bundle_detail = (
                f"blocked: extracted archive exists at {root_dir / 'third_party' / 'pitch' / 'HLA_PITCH_linux'} "
                "but third_party/pitch/PITCH-prti1516e-manual is missing"
            )
        else:
            bundle_status = "missing"
            bundle_detail = (
                "missing: set HLA2010_PITCH_HOME or place HLA_PITCH_linux.zip, "
                "HLA_PITCH_linux/, or PITCH-prti1516e-manual/ under third_party/pitch/"
            )

    if not args.json:
        _log(script_name, "pitch bundle", bundle_detail)
        if user_home_detail:
            _log(script_name, "pitch user home", f"ok: {user_home_detail}")
        elif bundle_status != "ok":
            _log(
                script_name,
                "next step",
                "set HLA2010_PITCH_HOME, or place HLA_PITCH_linux.zip, HLA_PITCH_linux/, or "
                "PITCH-prti1516e-manual/ under third_party/pitch/",
            )

    if managed_container_running:
        crc_port = _resolve_managed_container_port(container_name, 8989) or crc_port
        fedpro_port = _resolve_managed_container_port(container_name, 15164) or fedpro_port
        crc_port_detail = (
            f"ok: managed container {container_name} is already running on 127.0.0.1:{crc_port}"
        )
        fedpro_port_detail = (
            f"ok: managed container {container_name} is already running on 127.0.0.1:{fedpro_port}"
        )
    else:
        crc_ok, crc_error = _check_port_available(crc_port)
        if crc_ok:
            crc_port_detail = f"ok: 127.0.0.1:{crc_port} is available"
        elif auto_ports and not crc_port_explicit:
            old_crc_port = crc_port
            crc_port = _find_available_port(fedpro_port)
            crc_port_detail = (
                f"ok: 127.0.0.1:{old_crc_port} was unavailable ({crc_error}); "
                f"selected alternate 127.0.0.1:{crc_port}"
            )
        else:
            status = 1
            crc_port_status = "blocked"
            crc_port_detail = f"blocked: 127.0.0.1:{crc_port} is not available: {crc_error}"

        fedpro_ok, fedpro_error = _check_port_available(fedpro_port)
        if fedpro_ok:
            fedpro_port_detail = f"ok: 127.0.0.1:{fedpro_port} is available"
        elif auto_ports and not fedpro_port_explicit:
            old_fedpro_port = fedpro_port
            fedpro_port = _find_available_port(crc_port)
            fedpro_port_detail = (
                f"ok: 127.0.0.1:{old_fedpro_port} was unavailable ({fedpro_error}); "
                f"selected alternate 127.0.0.1:{fedpro_port}"
            )
        else:
            status = 1
            fedpro_port_status = "blocked"
            fedpro_port_detail = (
                f"blocked: 127.0.0.1:{fedpro_port} is not available: {fedpro_error}"
            )

    if not args.json:
        _log(script_name, "crc port", crc_port_detail)
        _log(script_name, "fedpro port", fedpro_port_detail)

    environment = "ready"
    if docker_status != "ok":
        environment = "docker-blocked"
    elif bundle_status != "ok":
        environment = "bundle-blocked"
    elif crc_port_status != "ok" or fedpro_port_status != "ok":
        environment = "ports-blocked"

    result = "not ready; fix the blocked prerequisite(s) above and rerun"
    next_step = "fix the blocked prerequisite(s) above and rerun"
    if status == 0:
        result = "ready to run ./tools/pitch install or ./tools/pitch all"
        next_step = "./tools/pitch install or ./tools/pitch all"

    payload = _build_payload(
        repo_root=root_dir,
        platform=platform,
        environment=environment,
        result=result,
        docker_status=docker_status,
        docker_detail=docker_detail,
        bundle_status=bundle_status,
        bundle_detail=bundle_detail,
        user_home_detail=user_home_detail,
        runtime_home_detail=runtime_home_detail,
        runtime_marker_detail=runtime_marker_detail,
        container_name=container_name,
        image_name=image_name,
        crc_port=crc_port,
        crc_port_status=crc_port_status,
        crc_port_detail=crc_port_detail,
        fedpro_port=fedpro_port,
        fedpro_port_status=fedpro_port_status,
        fedpro_port_detail=fedpro_port_detail,
        next_step=next_step,
        exit_code=status,
    )

    if args.json_file is not None:
        args.json_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return status

    _log(script_name, "environment", environment)
    _log(script_name, "result", result)
    if status == 0:
        _log(script_name, "next step", next_step)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
