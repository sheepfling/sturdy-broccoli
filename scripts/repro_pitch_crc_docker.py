#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.vendors.pitch.real_rti_pitch import (
    discover_pitch_runtime,
    prepare_pitch_user_home,
)

REPO_ROOT = SCRIPT_REPO_ROOT


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproduce the Pitch Docker CRC startup path.")
    parser.add_argument("--pitch-home", type=Path, default=None)
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


def _terminate_process_group(process: subprocess.Popen[str], timeout: float) -> tuple[str, str]:
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        return process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        return process.communicate(timeout=timeout)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    runtime = discover_pitch_runtime(args.pitch_home)
    user_home = prepare_pitch_user_home(runtime)
    docker_info = subprocess.run(["docker", "info"], capture_output=True, text=True)
    result: dict[str, object] = {
        "pitch_home": str(runtime.home),
        "pitch_user_home": str(user_home),
        "docker_info_exit_code": docker_info.returncode,
        "docker_info_stderr_head": docker_info.stderr.splitlines()[:20],
    }
    if docker_info.returncode != 0:
        result["opened_8989"] = False
        result["blocked"] = "docker daemon unavailable"
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    env = dict(os.environ)
    env["HLA2010_PITCH_HOME"] = str(runtime.home)
    env["HLA2010_PITCH_USER_HOME"] = str(user_home)
    env.setdefault("HLA2010_PITCH_DOCKER_BUILD", "0")
    process = subprocess.Popen(
        [str(REPO_ROOT / "scripts" / "run_pitch_docker_crc.sh")],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    opened_8989 = _wait_for_port("127.0.0.1", 8989, 45.0)
    stdout, stderr = _terminate_process_group(process, timeout=10)
    result.update(
        {
            "opened_8989": opened_8989,
            "exit_code": process.returncode,
            "stdout_head": stdout.splitlines()[:30],
            "stderr_head": stderr.splitlines()[:30],
        }
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
