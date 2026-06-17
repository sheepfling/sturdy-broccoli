from __future__ import annotations

from pathlib import Path

from hla.backends.common import RTIBackendPlugin
from hla.rti import available_backend_plugins, resolve_spec
from hla.rti.plugin_api import BackendRequest

from hla.backends.cpp_shim import backend_plugins, create_cpp_shim_backend, load_pybind_binding


def test_cpp_shim_package_exposes_two_route_plugins() -> None:
    plugins = backend_plugins()
    names = {plugin.name for plugin in plugins}

    assert {
        "cpp-shim-pybind",
        "cpp-shim-grpc",
        "cpp-standard-2010-pybind",
        "cpp-standard-2010-grpc",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    } <= names
    assert all(isinstance(plugin, RTIBackendPlugin) for plugin in plugins)
    assert {plugin.name: plugin.supports for plugin in plugins}["cpp-shim-pybind"] == ("rti1516e", "rti1516_2025")
    assert {plugin.name: plugin.supports for plugin in plugins}["cpp-standard-2010-pybind"] == ("rti1516e",)
    assert {plugin.name: plugin.supports for plugin in plugins}["cpp-standard-2025-pybind"] == ("rti1516_2025",)


def test_cpp_shim_routes_are_registered_for_source_checkout_discovery() -> None:
    plugins = available_backend_plugins()

    assert plugins["cpp-shim-pybind"].family == "cpp-shim"
    assert plugins["cpp-shim-grpc"].family == "cpp-shim"
    assert plugins["cpp-standard-2010-pybind"].family == "standard/cpp"
    assert plugins["cpp-standard-2025-grpc"].family == "standard/cpp"
    assert plugins["cpp-shim"].name == "cpp-shim-pybind"


def test_cpp_shim_backend_creation_records_route_metadata() -> None:
    spec = resolve_spec("rti1516e")
    plugin = next(plugin for plugin in backend_plugins() if plugin.name == "cpp-shim-pybind")
    backend = plugin.create_backend(BackendRequest(spec=spec))

    assert backend.info.name == "cpp-shim-pybind"
    assert backend.info.kind == "cpp/pybind/shim"
    assert backend.info.details["route"] == "pybind"


def test_cpp_shim_routes_create_2025_native_ambassadors() -> None:
    from hla.rti import create_rti_ambassador

    for backend_name, expected_kind in (
        ("cpp-shim-pybind", "cpp/pybind/shim"),
        ("cpp-shim-grpc", "cpp/grpc/shim"),
    ):
        rti = create_rti_ambassador(spec="2025", backend=backend_name)
        assert rti.backend_info.kind == expected_kind
        assert rti.backend_info.details["spec"] == "rti1516_2025"
        assert rti.getHLAversion() == "IEEE 1516.1-2025"


def test_cpp_shim_backend_can_load_python_module_binding(tmp_path: Path) -> None:
    module_path = tmp_path / "_hla_cpp_shim.py"
    module_path.write_text(
        "VALUE = 'loaded'\n"
        "def create_backend(request=None):\n"
        "    return {'kind': 'dummy', 'request_present': request is not None}\n",
        encoding="utf-8",
    )

    spec = resolve_spec("rti1516e")
    request = BackendRequest(spec=spec, options={"module_path": str(module_path)})
    backend = create_cpp_shim_backend("pybind", request)
    binding = load_pybind_binding(request)

    assert backend.info.details["binding_kind"] == "python-module-file"
    assert backend.info.details["binding"]["module_name"] == "_hla_cpp_shim"
    assert binding is not None
    assert binding.kind == "python-module-file"
    assert callable(binding.resolve_callable("create_backend"))
