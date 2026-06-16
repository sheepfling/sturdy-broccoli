from __future__ import annotations

import importlib
from pathlib import Path

from hla.backends.common import RTIBackendPlugin


ROOT = Path(__file__).resolve().parents[1]
PYTHON_RTI_SRC = ROOT / "packages" / "hla-backend-inmemory" / "src"


def test_split_python_rti_package_exports_backend_surface():
    assert PYTHON_RTI_SRC.exists()
    import hla.backends.inmemory

    backend = hla.backends.inmemory.create_python_backend()
    assert backend.info.kind == "python/in-memory"
    assert hla.backends.inmemory.rti_ambassador().backend_info.name == "python-inmemory-rti"
    assert hla.backends.inmemory.prepare_python_two_federate_profile().__class__.__name__ == "InMemoryRTIEngine"


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
    from hla.backends.inmemory.backend import PythonRTIBackend
    from hla.backends.inmemory.engine import InMemoryRTIEngine
    from hla.backends.inmemory.factory import create_python_backend
    from hla.backends.inmemory.state import PythonRTIConfig
    from hla.backends.inmemory.testing_policy import prepare_python_two_federate_profile

    backend = create_python_backend(engine=InMemoryRTIEngine(), config=PythonRTIConfig())
    assert isinstance(backend, PythonRTIBackend)
    assert backend.info.kind == "python/in-memory"
    assert isinstance(prepare_python_two_federate_profile(), InMemoryRTIEngine)


def test_split_python_rti_package_plugin_descriptor_creates_backend():
    from hla.backends.inmemory.plugin import backend_plugins, plugin

    descriptor = plugin()
    assert isinstance(descriptor, RTIBackendPlugin)
    assert descriptor.name == "inmemory"
    assert "python" in descriptor.aliases
    assert "in-memory" in descriptor.aliases
    assert descriptor.discover().kind == "python/in-memory"
    assert descriptor.create_backend({}).info.kind == "python/in-memory"
    assert tuple(item.name for item in backend_plugins()) == (descriptor.name,)
