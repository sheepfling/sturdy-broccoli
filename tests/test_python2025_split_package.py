from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from hla.backends.common import RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest


ROOT = Path(__file__).resolve().parents[1]
PYTHON2025_RTI_SRC = ROOT / "packages" / "hla-backend-python2025" / "src"


def _backend_request() -> BackendRequest:
    from hla.rti1516_2025.plugin import plugin as spec_plugin

    return BackendRequest(spec=spec_plugin().spec)


def test_split_python2025_rti_package_exports_backend_surface() -> None:
    assert PYTHON2025_RTI_SRC.exists()

    import hla.backends.python2025

    backend = hla.backends.python2025.create_python2025_backend(_backend_request())
    assert backend.info.name == "python2025-rti"
    assert backend.info.kind == "python/2025"
    assert backend.info.details["provider"] == "python2025"
    assert backend.info.details["implementation_lane"] == "hla-backend-python2025"
    assert backend.info.details["counts_as_python_2025_rti"] is True


def test_split_python2025_rti_package_submodules_are_public() -> None:
    from hla.backends.python2025 import create_python2025_backend
    from hla.backends.python2025.backend import Python2025Backend, Python2025BackendInfo, Python2025RTIAmbassador
    from hla.backends.python2025.plugin import plugin

    backend = create_python2025_backend(_backend_request())
    descriptor = plugin()

    assert isinstance(backend, Python2025Backend)
    assert isinstance(backend.info, Python2025BackendInfo)
    assert issubclass(Python2025RTIAmbassador, object)
    assert descriptor.create_backend.__module__ == "hla.backends.python2025.backend"


def test_split_python2025_rti_package_plugin_descriptor_creates_backend() -> None:
    from hla.backends.python2025.plugin import backend_plugins, plugin

    descriptor = plugin()
    discovery = descriptor.discover()
    backend = descriptor.create_backend(_backend_request())

    assert isinstance(descriptor, RTIBackendPlugin)
    assert descriptor.name == "python2025"
    assert descriptor.family == "inmemory-2025"
    assert descriptor.aliases == ("python-2025", "python-2025-backend")
    assert descriptor.description == "Primary Python 2025 RTI implementation package."
    assert discovery.name == "python2025"
    assert discovery.info.kind == "python/2025"
    assert discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert discovery.info.details["counts_as_python_2025_rti"] is True
    assert "wrapper_only" not in discovery.info.details
    assert backend.info.kind == "python/2025"
    assert backend.info.details["provider"] == "python2025"
    assert tuple(item.name for item in backend_plugins()) == (descriptor.name,)


def test_split_python2025_rti_package_does_not_import_back_through_shim_modules() -> None:
    runtime_root = ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025"

    violations: list[tuple[str, str]] = []
    for path in sorted(runtime_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("hla.backends.shim"):
                        violations.append((path.relative_to(ROOT).as_posix(), alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("hla.backends.shim"):
                    violations.append((path.relative_to(ROOT).as_posix(), module))

    assert violations == []


def test_split_python2025_compatibility_wrapper_owns_wrapper_symbols() -> None:
    import hla.backends.python2025 as python2025_package
    import hla.backends.python2025.backend as runtime_backend
    from hla.backends.python2025.compatibility_wrapper import (
        ShimBackendInfo,
        Shim2025Backend,
        Shim2025RTIAmbassador,
        create_shim_backend,
    )
    from hla.backends.shim import runtime_aliases as shim_runtime_aliases
    from hla.backends.shim.backend import (
        Shim2025Backend as shim_package_backend,
        Shim2025RTIAmbassador as shim_package_rti,
        create_shim_backend as shim_package_create_shim_backend,
    )

    assert Shim2025Backend.__module__ == "hla.backends.python2025.compatibility_wrapper"
    assert Shim2025RTIAmbassador.__module__ == "hla.backends.python2025.compatibility_wrapper"
    assert create_shim_backend.__module__ == "hla.backends.python2025.compatibility_wrapper"
    assert ShimBackendInfo.__module__ == "hla.backends.python2025.compatibility_wrapper"

    assert not hasattr(runtime_backend, "ShimBackendInfo")
    assert not hasattr(runtime_backend, "Shim2025Backend")
    assert not hasattr(runtime_backend, "Shim2025RTIAmbassador")
    assert not hasattr(runtime_backend, "create_shim_backend")
    assert not hasattr(python2025_package, "Shim2025Backend")
    assert not hasattr(python2025_package, "Shim2025RTIAmbassador")
    assert not hasattr(python2025_package, "create_shim_backend")
    assert shim_runtime_aliases.Python2025Backend.__module__ == "hla.backends.python2025.backend"
    assert shim_runtime_aliases.Python2025RTIAmbassador.__module__ == "hla.backends.python2025.backend"
    assert shim_runtime_aliases.create_python2025_backend.__module__ == "hla.backends.python2025.backend"

    assert shim_package_backend is Shim2025Backend
    assert shim_package_rti is Shim2025RTIAmbassador
    assert shim_package_create_shim_backend is create_shim_backend


def test_split_python2025_packages_publish_primary_runtime_and_wrapper_metadata() -> None:
    python2025_pyproject = tomllib.loads((ROOT / "packages" / "hla-backend-python2025" / "pyproject.toml").read_text(encoding="utf-8"))
    shim_pyproject = tomllib.loads((ROOT / "packages" / "hla-backend-shim" / "pyproject.toml").read_text(encoding="utf-8"))

    python2025_project = python2025_pyproject["project"]
    shim_project = shim_pyproject["project"]

    assert python2025_project["name"] == "hla-backend-python2025"
    assert python2025_project["description"] == "Main full Python RTI backend package for HLA 1516.1-2025"
    assert python2025_project["dependencies"] == [
        "hla-backend-common==0.13.0",
        "hla-rti-core==0.13.0",
        "hla-rti1516-2025==0.13.0",
        "hla-transport-common==0.13.0",
    ]
    assert python2025_pyproject["project"]["entry-points"]["hla.rti_backends"] == {
        "python2025": "hla.backends.python2025.plugin:plugin"
    }
    assert python2025_pyproject["tool"]["hla"]["package"] == {
        "status": "implementation-owned",
        "role": "rti-backend",
        "backend_names": ["python2025"],
        "backend_aliases": ["python-2025", "python-2025-backend"],
        "source_roots": ["packages/hla-backend-python2025/src/hla/backends/python2025"],
    }

    assert shim_project["name"] == "hla-backend-shim"
    assert shim_project["description"] == "Legacy compatibility-wrapper package for the main full Python 2025 RTI"
    assert shim_project["dependencies"] == [
        "hla-backend-python2025==0.13.0",
        "hla-rti-core==0.13.0",
        "hla-rti1516-2025==0.13.0",
    ]
    assert "entry-points" not in shim_pyproject["project"]
    assert shim_pyproject["tool"]["hla"]["package"] == {
        "status": "compatibility-maintained",
        "role": "compatibility-wrapper",
        "backend_names": [],
        "backend_aliases": [],
        "source_roots": ["packages/hla-backend-shim/src/hla/backends/shim"],
    }


def test_split_python2025_wrapper_plugin_and_readmes_keep_runtime_wrapper_boundary_explicit() -> None:
    from hla.backends.python2025.plugin import plugin as python2025_plugin
    from hla.backends.shim.plugin import plugin as shim_plugin

    python2025_readme = (ROOT / "packages" / "hla-backend-python2025" / "README.md").read_text(encoding="utf-8")
    shim_readme = (ROOT / "packages" / "hla-backend-shim" / "README.md").read_text(encoding="utf-8")
    normalized_python2025_readme = " ".join(python2025_readme.split())
    normalized_shim_readme = " ".join(shim_readme.split())

    runtime_plugin = python2025_plugin()
    wrapper_plugin = shim_plugin()
    runtime_discovery = runtime_plugin.discover()
    wrapper_discovery = wrapper_plugin.discover()

    assert runtime_plugin.description == "Primary Python 2025 RTI implementation package."
    assert runtime_discovery.description == "Primary Python 2025 RTI implementation package."
    assert runtime_discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert runtime_discovery.info.details["counts_as_python_2025_rti"] is True
    assert "wrapper_only" not in runtime_discovery.info.details

    assert wrapper_plugin.description == "Legacy compatibility-wrapper alias over the primary IEEE 1516.1-2025 Python RTI implementation."
    assert wrapper_discovery.description == "Legacy compatibility-wrapper alias over the primary IEEE 1516.1-2025 Python RTI implementation."
    assert type(wrapper_discovery.info).__module__ == "hla.backends.python2025.compatibility_wrapper"
    assert wrapper_discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert wrapper_discovery.info.details["counts_as_python_2025_rti"] is False
    assert wrapper_discovery.info.details["wrapper_only"] is True

    assert "owns the main full Python 2025 RTI runtime" in normalized_python2025_readme
    assert "must not delegate back to `hla.backends.shim.backend.create_shim_backend`" in normalized_python2025_readme
    assert "promoted Python-owned 2025 RTI implementation lane" in normalized_python2025_readme
    assert "legacy compatibility-wrapper package" in normalized_shim_readme
    assert "import-level compatibility surface" in normalized_shim_readme or "compatibility-wrapper" in normalized_shim_readme
    assert "the main full Python 2025 RTI implementation executes from `hla-backend-python2025`" in normalized_shim_readme
    assert "package root, the shim-specific surface is only `Shim2025Backend`, `Shim2025RTIAmbassador`, and `create_shim_backend`" in normalized_shim_readme
    assert "`hla.backends.shim.runtime_aliases`" in shim_readme
