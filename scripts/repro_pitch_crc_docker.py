#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time

import _bootstrap  # noqa: F401

from hla2010.real_rti import discover_pitch_runtime, prepare_pitch_user_home


def _wait_for_port(host: str, port: int, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.2)
    return False


def main() -> int:
    runtime = discover_pitch_runtime()
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
    process = subprocess.Popen(
        [str(REPO_ROOT / "scripts" / "run_pitch_docker_crc.sh")],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    opened_8989 = _wait_for_port("127.0.0.1", 8989, 45.0)
    try:
        process.terminate()
        stdout, stderr = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate(timeout=10)
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
