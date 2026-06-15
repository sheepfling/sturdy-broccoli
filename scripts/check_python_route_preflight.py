#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


def _loopback_probe() -> tuple[bool, str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        host, port = sock.getsockname()
        return True, f"loopback-ok:{host}:{port}"
    except OSError as exc:
        return False, f"loopback-blocked:{type(exc).__name__}: {exc}"
    finally:
        sock.close()


def _grpc_probe() -> tuple[bool, str]:
    try:
        import grpc  # noqa: F401
    except Exception as exc:
        return False, f"grpc-import-failed:{type(exc).__name__}: {exc}"
    return True, "grpc-import-ok"


def _python_grpc_probe() -> tuple[str, str]:
    grpc_ok, grpc_detail = _grpc_probe()
    if not grpc_ok:
        return "blocked", grpc_detail
    loopback_ok, loopback_detail = _loopback_probe()
    if not loopback_ok:
        return "blocked", loopback_detail
    return "runnable", "python-grpc-runnable"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report whether Python direct and hosted gRPC routes are runnable here.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    loopback_ok, loopback_detail = _loopback_probe()
    grpc_ok, grpc_detail = _grpc_probe()
    python_grpc_status, python_grpc_detail = _python_grpc_probe()
    payload = {
        "tool": "python-verify-routes-preflight",
        "python_direct": "runnable",
        "loopback": {
            "status": "ok" if loopback_ok else "blocked",
            "detail": loopback_detail,
        },
        "grpc_import": {
            "status": "ok" if grpc_ok else "blocked",
            "detail": grpc_detail,
        },
        "python_grpc": {
            "status": python_grpc_status,
            "detail": python_grpc_detail,
        },
        "recommended_next_steps": []
        if python_grpc_status == "runnable"
        else ["Whitelist local loopback bind/connect for 127.0.0.1 ephemeral ports in the runner policy."],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"python-direct: {payload['python_direct']}")
        print(f"loopback: {payload['loopback']['status']} ({payload['loopback']['detail']})")
        print(f"grpc-import: {payload['grpc_import']['status']} ({payload['grpc_import']['detail']})")
        print(f"python-grpc: {payload['python_grpc']['status']} ({payload['python_grpc']['detail']})")
        if payload["recommended_next_steps"]:
            print(f"next: {payload['recommended_next_steps'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
