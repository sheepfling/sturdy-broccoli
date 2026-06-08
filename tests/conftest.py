from __future__ import annotations

import contextlib
import socket

import pytest


def _can_bind_loopback_server() -> bool:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind(("127.0.0.1", 0))
        except OSError:
            return False
    return True


_LOOPBACK_SERVER_AVAILABLE = _can_bind_loopback_server()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "requires_loopback_server: requires permission to bind a local loopback TCP port",
    )
    config.addinivalue_line(
        "markers",
        "requirements(*requirement_ids): explicit requirement IDs covered by the test",
    )


def pytest_runtest_setup(item: pytest.Item) -> None:
    if "requires_loopback_server" in item.keywords and not _LOOPBACK_SERVER_AVAILABLE:
        pytest.skip("loopback server sockets are unavailable in this environment")
