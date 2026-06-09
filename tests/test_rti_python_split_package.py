from __future__ import annotations

import sys
from pathlib import Path

from hla2010.rti import RTIBackendPlugin


ROOT = Path(__file__).resolve().parents[1]
PYTHON_RTI_SRC = ROOT / "packages" / "hla2010-rti-python" / "src"


def test_split_python_rti_package_exports_backend_surface():
    sys.path.insert(0, str(PYTHON_RTI_SRC))
    try:
        import hla2010_rti_python
        from hla2010.backends.python import InMemoryRTIEngine as OldEngine
        from hla2010.backends.python import PythonRTIBackend as OldBackend
        from hla2010.backends.python import PythonRTIConfig as OldConfig

        backend = hla2010_rti_python.create_python_backend()
        assert backend.info.kind == "python/in-memory"
        assert hla2010_rti_python.rti_ambassador().backend_info.name == "python-inmemory-rti"
        assert hla2010_rti_python.InMemoryRTIEngine is OldEngine
        assert hla2010_rti_python.PythonRTIBackend is OldBackend
        assert hla2010_rti_python.PythonRTIConfig is OldConfig
    finally:
        sys.path.remove(str(PYTHON_RTI_SRC))


def test_legacy_python_backend_modules_are_compatibility_facades():
    sys.path.insert(0, str(PYTHON_RTI_SRC))
    try:
        from hla2010.backends.python.backend import PythonRTIBackend as OldBackend
        from hla2010.backends.python.engine import InMemoryRTIEngine as OldEngine
        from hla2010.backends.python.factory import create_python_backend as old_create_backend
        from hla2010.backends.python.state import MOM_FEDERATE_CLASS, PythonRTIConfig as OldConfig
        from hla2010_rti_python.backend import PythonRTIBackend
        from hla2010_rti_python.engine import InMemoryRTIEngine
        from hla2010_rti_python.factory import create_python_backend
        from hla2010_rti_python.state import PythonRTIConfig

        assert OldBackend is PythonRTIBackend
        assert OldEngine is InMemoryRTIEngine
        assert OldConfig is PythonRTIConfig
        assert old_create_backend is create_python_backend
        assert MOM_FEDERATE_CLASS == "HLAobjectRoot.HLAmanager.HLAfederate"
    finally:
        sys.path.remove(str(PYTHON_RTI_SRC))


def test_split_python_rti_package_submodules_are_public():
    sys.path.insert(0, str(PYTHON_RTI_SRC))
    try:
        from hla2010_rti_python.backend import PythonRTIBackend
        from hla2010_rti_python.engine import InMemoryRTIEngine
        from hla2010_rti_python.factory import create_python_backend
        from hla2010_rti_python.state import PythonRTIConfig

        backend = create_python_backend(engine=InMemoryRTIEngine(), config=PythonRTIConfig())
        assert isinstance(backend, PythonRTIBackend)
        assert backend.info.kind == "python/in-memory"
    finally:
        sys.path.remove(str(PYTHON_RTI_SRC))


def test_split_python_rti_package_plugin_descriptor_creates_backend():
    sys.path.insert(0, str(PYTHON_RTI_SRC))
    try:
        from hla2010_rti_python.plugin import backend_plugins, plugin

        descriptor = plugin()
        assert isinstance(descriptor, RTIBackendPlugin)
        assert descriptor.name == "python"
        assert "in-memory" in descriptor.aliases
        assert descriptor.discover().kind == "python/in-memory"
        assert descriptor.create_backend({}).info.kind == "python/in-memory"
        assert tuple(item.name for item in backend_plugins()) == (descriptor.name,)
    finally:
        sys.path.remove(str(PYTHON_RTI_SRC))
