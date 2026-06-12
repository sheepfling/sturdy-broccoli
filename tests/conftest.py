from __future__ import annotations

import contextlib
import importlib
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


SOURCE_CHECKOUT_PLUGIN_MODULES = (
    "hla2010_rti_python.plugin",
    "hla2010_rti_java_jpype.plugin",
    "hla2010_rti_java_py4j.plugin",
    "hla2010_rti_pitch_jpype.plugin",
    "hla2010_rti_pitch_py4j.plugin",
    "hla2010_rti_portico.plugin",
    "hla2010_rti_certi.certi.plugin",
)


def _register_source_checkout_backend_plugins() -> None:
    from hla2010_rti_runtime_common import register_backend_plugin

    for module_name in SOURCE_CHECKOUT_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                continue
            raise
        for plugin in getattr(module, "backend_plugins", lambda: ())():
            register_backend_plugin(plugin)


def pytest_configure(config: pytest.Config) -> None:
    _register_source_checkout_backend_plugins()
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
