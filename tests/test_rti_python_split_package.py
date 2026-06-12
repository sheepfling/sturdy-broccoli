from __future__ import annotations

import importlib
from pathlib import Path

from hla2010_rti_backend_common import RTIBackendPlugin


ROOT = Path(__file__).resolve().parents[1]
PYTHON_RTI_SRC = ROOT / "packages" / "hla2010-rti-python" / "src"


def test_split_python_rti_package_exports_backend_surface():
    assert PYTHON_RTI_SRC.exists()
    import hla2010_rti_python

    backend = hla2010_rti_python.create_python_backend()
    assert backend.info.kind == "python/in-memory"
    assert hla2010_rti_python.rti_ambassador().backend_info.name == "python-inmemory-rti"
    assert hla2010_rti_python.prepare_python_two_federate_profile().__class__.__name__ == "InMemoryRTIEngine"


def test_legacy_python_backend_modules_are_removed():
    for module_name in (
        "hla2010.backends.python",
        "hla2010.backends.python.backend",
        "hla2010.backends.python.engine",
        "hla2010.backends.python.factory",
        "hla2010.backends.python.state",
    ):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"legacy compatibility module still imports: {module_name}")


def test_split_python_rti_package_submodules_are_public():
    from hla2010_rti_python.backend import PythonRTIBackend
    from hla2010_rti_python.engine import InMemoryRTIEngine
    from hla2010_rti_python.factory import create_python_backend
    from hla2010_rti_python.state import PythonRTIConfig
    from hla2010_rti_python.testing_policy import prepare_python_two_federate_profile

    backend = create_python_backend(engine=InMemoryRTIEngine(), config=PythonRTIConfig())
    assert isinstance(backend, PythonRTIBackend)
    assert backend.info.kind == "python/in-memory"
    assert isinstance(prepare_python_two_federate_profile(), InMemoryRTIEngine)


def test_split_python_rti_package_plugin_descriptor_creates_backend():
    from hla2010_rti_python.plugin import backend_plugins, plugin

    descriptor = plugin()
    assert isinstance(descriptor, RTIBackendPlugin)
    assert descriptor.name == "python"
    assert "in-memory" in descriptor.aliases
    assert descriptor.discover().kind == "python/in-memory"
    assert descriptor.create_backend({}).info.kind == "python/in-memory"
    assert tuple(item.name for item in backend_plugins()) == (descriptor.name,)
