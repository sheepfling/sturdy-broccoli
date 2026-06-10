from __future__ import annotations

import os
import json
import socket
import time
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence

import pytest

from hla2010.enums import ResignAction


_VENDOR_PREFLIGHT_ENV = {
    "certi": "HLA2010_CERTI_PREFLIGHT_OK",
    "pitch": "HLA2010_PITCH_PREFLIGHT_OK",
}

_VENDOR_PREFLIGHT_ARTIFACT = {
    "certi": "certi-preflight.json",
    "pitch": "pitch-preflight.json",
}

_VENDOR_PREFLIGHT_TOOL = {
    "certi": "certi-preflight",
    "pitch": "pitch-preflight",
}

_VENDOR_PREFLIGHT_ENVIRONMENT = {
    "certi": "loopback-ok",
    "pitch": "ready",
}

_VENDOR_PREFLIGHT_RESULT = {
    "certi": "real CERTI runnable",
    "pitch": "ready to run ./scripts/pitch_docker_easy.sh install or ./scripts/pitch_docker_easy.sh all",
}


@dataclass
class ReservedUDPPorts(AbstractContextManager["ReservedUDPPorts"]):
    host: str
    ports: tuple[int, ...]
    _sockets: tuple[socket.socket, ...]

    def close(self) -> None:
        for sock in self._sockets:
            try:
                sock.close()
            except OSError:
                pass
        self._sockets = ()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
        return None


def reserve_udp_ports(count: int, *, host: str = "127.0.0.1") -> ReservedUDPPorts:
    sockets: list[socket.socket] = []
    ports: list[int] = []
    try:
        for _ in range(count):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((host, 0))
            sockets.append(sock)
            ports.append(int(sock.getsockname()[1]))
    except Exception:
        for sock in sockets:
            try:
                sock.close()
            except OSError:
                pass
        raise
    return ReservedUDPPorts(host=host, ports=tuple(ports), _sockets=tuple(sockets))


def reserve_udp_pair(*, host: str = "127.0.0.1") -> ReservedUDPPorts:
    return reserve_udp_ports(2, host=host)


def _default_preflight_artifact_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "analysis" / "preflight_artifacts"


def _preflight_artifact_path(vendor: str) -> Path:
    artifact_dir = Path(
        os.environ.get("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(_default_preflight_artifact_dir()))
    )
    return artifact_dir / _VENDOR_PREFLIGHT_ARTIFACT[vendor]


def _artifact_confirms_vendor_preflight(vendor: str) -> bool:
    path = _preflight_artifact_path(vendor)
    if not path.exists():
        return False
    max_age_seconds = float(os.environ.get("HLA2010_PREFLIGHT_MAX_AGE_SECONDS", "43200"))
    if max_age_seconds > 0:
        try:
            age_seconds = time.time() - path.stat().st_mtime
        except OSError:
            return False
        if age_seconds > max_age_seconds:
            return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    expected_tool = _VENDOR_PREFLIGHT_TOOL[vendor]
    expected_environment = _VENDOR_PREFLIGHT_ENVIRONMENT[vendor]
    expected_result = _VENDOR_PREFLIGHT_RESULT[vendor]
    return (
        str(payload.get("tool", "")) == expected_tool
        and int(payload.get("exit_code", 1)) == 0
        and str(payload.get("environment", "")) == expected_environment
        and str(payload.get("result", "")) == expected_result
    )


def require_vendor_preflight(vendor: str, *, operator_hint: str) -> None:
    env_var = _VENDOR_PREFLIGHT_ENV.get(vendor)
    if env_var is None:
        raise ValueError(f"unsupported vendor preflight guard: {vendor}")
    if os.environ.get(env_var) == "1" or _artifact_confirms_vendor_preflight(vendor):
        return
    if os.environ.get(env_var) != "1":
        pytest.skip(
            f"{vendor} preflight not confirmed; run the supported operator path or rerun after `{operator_hint}`"
        )


@contextmanager
def udp_port_pair(udp_base: int | None = None, *, host: str = "127.0.0.1") -> Iterator[tuple[int, int]]:
    if udp_base is not None:
        yield (udp_base, udp_base + 1)
        return
    with reserve_udp_pair(host=host) as lease:
        yield (lease.ports[0], lease.ports[1])


def cleanup_federation(
    federation_name: str,
    *,
    destroyer: Any | None = None,
    destroyer_resign_action: ResignAction | None = None,
    remaining_resignations: Sequence[tuple[Any | None, ResignAction]] = (),
    disconnect_rtis: Sequence[Any | None] = (),
) -> None:
    if destroyer is not None and destroyer_resign_action is not None:
        try:
            destroyer.resign_federation_execution(destroyer_resign_action)
        except BaseException:
            pass
    for rti, action in remaining_resignations:
        if rti is None:
            continue
        try:
            rti.resign_federation_execution(action)
        except BaseException:
            pass
    if destroyer is not None:
        try:
            destroyer.destroy_federation_execution(federation_name)
        except BaseException:
            pass
    for rti in disconnect_rtis:
        if rti is None:
            continue
        try:
            rti.disconnect()
        except BaseException:
            pass


def close_all(*resources: Any | None) -> None:
    for resource in resources:
        if resource is None:
            continue
        try:
            resource.close()
        except BaseException:
            pass


def terminate_all(*resources: Any | None) -> None:
    for resource in resources:
        if resource is None:
            continue
        try:
            resource.terminate()
        except BaseException:
            pass


def shutdown_runtime_resources(
    *,
    close_resources: Sequence[Any | None] = (),
    runtime_resources: Sequence[Any | None] = (),
    timeout: float = 5.0,
) -> None:
    close_all(*close_resources)
    terminate_all(*runtime_resources)
    assert_all_terminated(*runtime_resources, timeout=timeout)


def wait_for_tcp_listener_closed(host: str, port: int, *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            if sock.connect_ex((host, port)) != 0:
                return
        time.sleep(0.1)
    raise AssertionError(f"Timed out waiting for listener shutdown on {host}:{port}")


def assert_runtime_process_stopped(resource: Any | None, *, timeout: float = 5.0) -> None:
    if resource is None:
        return

    poll = getattr(resource, "poll", None)
    if callable(poll):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if poll() is not None:
                break
            time.sleep(0.1)
        else:
            raise AssertionError(f"Timed out waiting for runtime process shutdown: {resource!r}")

    host = getattr(resource, "host", None)
    tcp_port = getattr(resource, "tcp_port", None)
    if host is not None and tcp_port is not None:
        wait_for_tcp_listener_closed(str(host), int(tcp_port), timeout=timeout)


def assert_all_terminated(*resources: Any | None, timeout: float = 5.0) -> None:
    for resource in resources:
        assert_runtime_process_stopped(resource, timeout=timeout)
