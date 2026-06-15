#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_rti_backend_common import BackendUnavailableError
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_rti_pitch_common.real_rti_pitch import (
    discover_pitch_runtime,
    pitch_fedpro_local_settings_designator,
    prepare_pitch_user_home,
)

REPO_ROOT = SCRIPT_REPO_ROOT


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe the native local Pitch CRC/FedPro path.")
    parser.add_argument("--pitch-home", type=Path, default=None)
    parser.add_argument("--java-home", type=Path, default=None)
    parser.add_argument("--launcher-mode", choices=("raw", "install4j"), default="raw")
    parser.add_argument("--crc-port", type=int, default=8989)
    parser.add_argument("--fedpro-port", type=int, default=15164)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--dwell-seconds", type=float, default=2.0)
    parser.add_argument("--bridge", choices=("none", "py4j", "jpype"), default="none")
    return parser.parse_args(argv)


def _wait_for_port(host: str, port: int, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.2)
    return False


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _wait_for_port_stable(host: str, port: int, *, timeout: float, dwell_seconds: float) -> bool:
    if not _wait_for_port(host, port, timeout):
        return False
    deadline = time.time() + dwell_seconds
    while time.time() < deadline:
        if not _port_open(host, port):
            return False
        time.sleep(0.2)
    return True


def _drain_process(process: subprocess.Popen[str]) -> dict[str, Any]:
    try:
        stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
    return {
        "exit_code": process.returncode,
        "stdout_head": stdout.splitlines()[:30],
        "stderr_head": stderr.splitlines()[:40],
    }


def _terminate_process(process: subprocess.Popen[str] | None) -> dict[str, Any] | None:
    if process is None:
        return None
    if process.poll() is None:
        process.terminate()
    return _drain_process(process)


def _fedpro_command(runtime_home: Path, java_bin: Path, java_library_path: tuple[Path, ...], user_home: Path, fedpro_port: int) -> list[str]:
    fedpro_classpath = os.pathsep.join(str(path) for path in sorted((runtime_home / "lib").glob("*.jar")))
    return [
        str(java_bin),
        f"-Djava.util.logging.config.file={user_home / 'prti1516e' / 'FedProServer.logging'}",
        "-Dse.pitch.prti1516e.useSystemWideLicenseFile=true",
        "-Dse.pitch.fedpro.acceptRtiAddressFromClient=true",
        "-Dse.pitch.fedpro.acceptAdditionalSettingsFromClient=true",
        f"-Duser.home={user_home}",
        f"-Djava.library.path={os.pathsep.join(str(item) for item in java_library_path)}",
        "-classpath",
        fedpro_classpath,
        "se.pitch.fedpro.server.hla.FedProServerApp",
        "-p",
        str(fedpro_port),
    ]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    runtime = discover_pitch_runtime(args.pitch_home)
    user_home = prepare_pitch_user_home(runtime, crc_mode="local")
    java_home = args.java_home or runtime.java_home

    env = dict(os.environ)
    env["HLA2010_PITCH_HOME"] = str(runtime.home)
    env["HLA2010_PITCH_USER_HOME"] = str(user_home)
    env["HOME"] = str(user_home)
    env["HLA2010_PITCH_CRC_MODE"] = "local"
    env["HLA2010_PITCH_LAUNCHER_MODE"] = args.launcher_mode
    env["HLA2010_PITCH_CRC_PORT"] = str(args.crc_port)
    env["HLA2010_PITCH_FEDPRO_PORT"] = str(args.fedpro_port)
    env["HLA2010_PITCH_JAVA_HOME"] = str(java_home)
    env["JAVA_HOME"] = str(java_home)
    env["JDK_HOME"] = str(java_home)

    old_env = {name: os.environ.get(name) for name in env}
    os.environ.update(env)

    crc_process: subprocess.Popen[str] | None = None
    fedpro_process: subprocess.Popen[str] | None = None
    rti = None
    result: dict[str, Any] = {
        "probe": "pitch-native-local",
        "launcher_mode": args.launcher_mode,
        "pitch_home": str(runtime.home),
        "pitch_user_home": str(user_home),
        "java_home": str(java_home),
        "crc_port": args.crc_port,
        "fedpro_port": args.fedpro_port,
        "bridge": args.bridge,
        "designator": pitch_fedpro_local_settings_designator(),
    }
    try:
        crc_process = subprocess.Popen(
            [str(REPO_ROOT / "scripts" / "run_pitch_local.sh"), "-nogui", "-verbose"],
            cwd=REPO_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        result["crc"] = {
            "opened": _wait_for_port("127.0.0.1", args.crc_port, args.timeout),
        }
        result["crc"]["stable"] = bool(result["crc"]["opened"]) and _wait_for_port_stable(
            "127.0.0.1",
            args.crc_port,
            timeout=0.5,
            dwell_seconds=args.dwell_seconds,
        )

        try:
            fedpro_process = subprocess.Popen(
                _fedpro_command(runtime.home, java_home / "bin" / "java", runtime.java_library_path, user_home, args.fedpro_port),
                cwd=runtime.home,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            result["fedpro"] = {
                "opened": _wait_for_port("127.0.0.1", args.fedpro_port, args.timeout),
            }
            result["fedpro"]["stable"] = bool(result["fedpro"]["opened"]) and _wait_for_port_stable(
                "127.0.0.1",
                args.fedpro_port,
                timeout=0.5,
                dwell_seconds=args.dwell_seconds,
            )
        except OSError as exc:
            result["fedpro"] = {
                "opened": False,
                "stable": False,
                "launch_error": f"{type(exc).__name__}: {exc}",
            }

        if args.bridge != "none":
            kind = f"pitch-{args.bridge}"
            try:
                rti = create_rti_ambassador(kind)
                result["bridge_result"] = {
                    "kind": kind,
                    "created": True,
                    "hla_version": rti.getHLAversion(),
                }
            except BackendUnavailableError as exc:
                result["bridge_result"] = {
                    "kind": kind,
                    "created": False,
                    "error": str(exc),
                }
    finally:
        if rti is not None:
            try:
                rti.close()
            except BaseException:
                pass
        result["fedpro_process"] = _terminate_process(fedpro_process)
        result["crc_process"] = _terminate_process(crc_process)
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
