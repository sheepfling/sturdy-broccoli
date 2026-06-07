#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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


def _latest_crash_reports(since: float) -> list[str]:
    report_dir = Path.home() / "Library" / "Logs" / "DiagnosticReports"
    if not report_dir.exists():
        return []
    reports: list[tuple[float, str]] = []
    for path in report_dir.glob("java-*.ips"):
        try:
            stat = path.stat()
        except OSError:
            continue
        if stat.st_mtime >= since:
            reports.append((stat.st_mtime, str(path)))
    reports.sort()
    return [path for _, path in reports]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduce the Pitch CRC macOS startup failure.")
    parser.add_argument("--pitch-home", type=Path, default=None)
    parser.add_argument("--java-home", type=Path, default=None)
    parser.add_argument("--java-bin", type=Path, default=None)
    parser.add_argument("--launcher-mode", choices=("raw", "install4j"), default="raw")
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--jvm-arg", action="append", default=[])
    parser.add_argument("--ui-automation", action="store_true")
    args = parser.parse_args()

    runtime = discover_pitch_runtime(args.pitch_home)
    user_home = prepare_pitch_user_home(runtime)
    repo_root = REPO_ROOT
    command = [str(repo_root / "scripts" / "run_pitch_local.sh")]
    env = dict(os.environ)
    env["HLA2010_PITCH_HOME"] = str(runtime.home)
    env["HLA2010_PITCH_USER_HOME"] = str(user_home)
    env["HOME"] = str(user_home)
    env["HLA2010_PITCH_LAUNCHER_MODE"] = args.launcher_mode
    if args.ui_automation:
        env["HLA2010_PITCH_UI_AUTOMATION"] = "1"
    if args.java_home is not None:
        env["HLA2010_PITCH_JAVA_HOME"] = str(args.java_home)
    if args.java_bin is not None:
        env["HLA2010_PITCH_JAVA_BIN"] = str(args.java_bin)
    if args.jvm_arg:
        env["HLA2010_PITCH_JVM_ARGS"] = " ".join(args.jvm_arg)

    started_at = time.time()
    process = subprocess.Popen(
        command,
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    opened_8989 = _wait_for_port("127.0.0.1", 8989, args.timeout)
    poll_code = process.poll()

    try:
        if poll_code is None:
            process.terminate()
            stdout, stderr = process.communicate(timeout=5)
        else:
            stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate(timeout=5)

    result = {
        "launcher_mode": args.launcher_mode,
        "ui_automation": args.ui_automation,
        "pitch_home": str(runtime.home),
        "selected_java_home": env.get("HLA2010_PITCH_JAVA_HOME", str(runtime.java_home)),
        "selected_java_bin": env.get("HLA2010_PITCH_JAVA_BIN", ""),
        "jvm_args": args.jvm_arg,
        "opened_8989": opened_8989,
        "exit_code": process.returncode,
        "stdout_head": stdout.splitlines()[:10],
        "stderr_head": stderr.splitlines()[:30],
        "crash_reports": _latest_crash_reports(started_at),
    }
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
