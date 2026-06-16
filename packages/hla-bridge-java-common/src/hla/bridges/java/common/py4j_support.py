"""Shared Py4J runtime helpers for Java-backed RTI packages."""
from __future__ import annotations

from typing import Any


def reset_py4j_callback_client(gateway: Any) -> None:
    """Advertise Py4J's actual ephemeral Python callback port to Java."""

    callback_server = gateway.get_callback_server()
    if callback_server is None:
        return
    listening_port = getattr(callback_server, "get_listening_port", lambda: None)()
    if not listening_port or listening_port < 0:
        return
    java_gateway_server = getattr(gateway, "java_gateway_server", None)
    if java_gateway_server is None:
        return
    callback_client = java_gateway_server.getCallbackClient()
    java_gateway_server.resetCallbackClient(callback_client.getAddress(), int(listening_port))


__all__ = ["reset_py4j_callback_client"]
