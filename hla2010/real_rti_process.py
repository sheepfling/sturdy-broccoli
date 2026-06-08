"""Shared runtime process helpers for CERTI and Pitch launches."""
from __future__ import annotations

import socket
import subprocess
import time
from dataclasses import dataclass, field

from .backends.base import BackendUnavailableError


def _loopback_remediation(host: str, port: int | None = None) -> str:
    target = f"{host}:{port}" if port is not None else host
    return (
        f"Run `./certi-easy preflight` to verify local CERTI prerequisites. "
        f"Real RTI smoke needs loopback TCP bind/connect permission for {target}."
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
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, 0))
            sock.listen(1)
            return int(sock.getsockname()[1])
    except PermissionError as exc:
        raise BackendUnavailableError(
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
            raise BackendUnavailableError(
                f"Local socket connect is not permitted for {host}:{port}. {_loopback_remediation(host, port)}"
            ) from exc
        time.sleep(0.1)
    raise BackendUnavailableError(f"Timed out waiting for listener on {host}:{port}")


def wait_for_process_boot(process: subprocess.Popen[str], *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise BackendUnavailableError(f"Runtime process exited early with code {process.returncode}")
        time.sleep(0.1)
