"""Shared runtime process helpers for CERTI and Pitch launches."""
from __future__ import annotations

import socket
import shutil
import subprocess
import time
import importlib
from dataclasses import dataclass, field
from pathlib import Path


def _loopback_remediation(host: str, port: int | None = None) -> str:
    target = f"{host}:{port}" if port is not None else host
    return (
        f"Run `./tools/certi-easy preflight` to verify local CERTI prerequisites. "
        f"Real RTI smoke needs loopback TCP bind/connect permission for {target}."
    )


def _backend_unavailable_error() -> type[Exception]:
    return importlib.import_module("hla.backends.common").BackendUnavailableError


@dataclass
class RuntimeProcess:
    name: str
    process: subprocess.Popen[str]
    env: dict[str, str] = field(default_factory=dict)
    host: str | None = None
    tcp_port: int | None = None
    children: tuple[subprocess.Popen[str], ...] = ()
    cleanup_paths: tuple[Path, ...] = ()

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
        for path in self.cleanup_paths:
            shutil.rmtree(path, ignore_errors=True)


def reserve_tcp_port(host: str = "127.0.0.1") -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, 0))
            sock.listen(1)
            return int(sock.getsockname()[1])
    except PermissionError as exc:
        raise _backend_unavailable_error()(
            f"Local socket bind is not permitted for {host}. {_loopback_remediation(host)}"
        ) from exc


def wait_for_tcp_listener(host: str, port: int, *, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.25)
                if sock.connect_ex((host, port)) == 0:
                    return
        except PermissionError as exc:
            raise _backend_unavailable_error()(
                f"Local socket connect is not permitted for {host}:{port}. {_loopback_remediation(host, port)}"
            ) from exc
        time.sleep(0.1)
    raise _backend_unavailable_error()(f"Timed out waiting for listener on {host}:{port}")


def wait_for_process_boot(process: subprocess.Popen[str], *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise _backend_unavailable_error()(f"Runtime process exited early with code {process.returncode}")
        time.sleep(0.1)
