from __future__ import annotations

import importlib
from pathlib import Path

from hla.backends.common import RTIBackendPlugin


ROOT = Path(__file__).resolve().parents[1]
PYTHON_RTI_SRC = ROOT / "packages" / "hla-backend-python1516e" / "src"


def test_split_python_rti_package_exports_backend_surface():
    assert PYTHON_RTI_SRC.exists()
    import hla.backends.python1516e

    backend = hla.backends.python1516e.create_python_backend()
    assert backend.info.kind == "python/1516e"
    assert hla.backends.python1516e.rti_ambassador().backend_info.name == "python1516e-rti"
    assert hla.backends.python1516e.prepare_python_two_federate_profile().__class__.__name__ == "InMemoryRTIEngine"


def test_legacy_python_backend_modules_are_removed():
    for module_name in (
        "hla.rti1516e.backends.python",
        "hla.rti1516e.backends.python.backend",
        "hla.rti1516e.backends.python.engine",
        "hla.rti1516e.backends.python.factory",
        "hla.rti1516e.backends.python.state",
    ):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"legacy compatibility module still imports: {module_name}")


def test_split_python_rti_package_submodules_are_public():
    from hla.backends.python1516e.backend import PythonRTIBackend
    from hla.backends.python1516e.engine import InMemoryRTIEngine
    from hla.backends.python1516e.factory import create_python_backend
    from hla.backends.python1516e.state import PythonRTIConfig
    from hla.backends.python1516e.testing_policy import prepare_python_two_federate_profile

    backend = create_python_backend(engine=InMemoryRTIEngine(), config=PythonRTIConfig())
    assert isinstance(backend, PythonRTIBackend)
    assert backend.info.kind == "python/1516e"
    assert isinstance(prepare_python_two_federate_profile(), InMemoryRTIEngine)


def test_split_python_rti_package_plugin_descriptor_creates_backend():
    from hla.backends.python1516e.plugin import backend_plugins, plugin

    descriptor = plugin()
    assert isinstance(descriptor, RTIBackendPlugin)
    assert descriptor.name == "python1516e"
    assert "python-1516e" in descriptor.aliases
    assert descriptor.discover().kind == "python/1516e"
    assert descriptor.create_backend({}).info.kind == "python/1516e"
    assert tuple(item.name for item in backend_plugins()) == (descriptor.name,)
