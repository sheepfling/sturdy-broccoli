from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from hla.backends.common import RTIBackendPlugin
from hla.rti.plugin_api import BackendRequest


ROOT = Path(__file__).resolve().parents[1]
PYTHON2025_RTI_SRC = ROOT / "packages" / "hla-backend-python2025" / "src"


def _backend_request() -> BackendRequest:
    from hla.runtime.rti1516_2025_plugin import plugin as spec_plugin

    return BackendRequest(spec=spec_plugin().spec)


def test_split_python2025_rti_package_exports_backend_surface() -> None:
    assert PYTHON2025_RTI_SRC.exists()

    import hla.backends.python2025

    backend = hla.backends.python2025.create_python2025_backend(_backend_request())
    assert backend.info.name == "python1516_2025-rti"
    assert backend.info.kind == "python/2025"
    assert backend.info.details["provider"] == "python1516_2025"
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
    assert descriptor.name == "python1516_2025"
    assert descriptor.family == "python-rti-2025"
    assert descriptor.aliases == ("python-1516-2025", "python-1516-2025")
    assert descriptor.description == "Primary Python 2025 RTI implementation package."
    assert discovery.name == "python1516_2025"
    assert discovery.info.kind == "python/2025"
    assert discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert discovery.info.details["counts_as_python_2025_rti"] is True
    assert "wrapper_only" not in discovery.info.details
    assert backend.info.kind == "python/2025"
    assert backend.info.details["provider"] == "python1516_2025"
    assert tuple(item.name for item in backend_plugins()) == (descriptor.name,)


def test_split_python2025_runtime_can_spawn_verification_sibling_without_shim_route() -> None:
    from hla.runtime.rti1516_2025_factory import create_rti_ambassador

    runtime_rti = create_rti_ambassador(backend="python1516_2025")
    sibling = runtime_rti._verification_spawn_like()

    assert type(sibling) is type(runtime_rti)
    assert sibling is not runtime_rti
    assert sibling.backend_info.details["provider"] == "python1516_2025"
    assert sibling.backend_info.details["implementation_lane"] == "hla-backend-python2025"
    assert sibling.backend_info.details["counts_as_python_2025_rti"] is True
    assert sibling._logical_time_implementation_name == runtime_rti._logical_time_implementation_name


def test_split_python2025_rti_package_does_not_import_back_through_shim_modules() -> None:
    runtime_root = ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python1516_2025"

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


def test_split_python2025_runtime_backend_imports_runtime_modules_directly() -> None:
    backend_path = (
        ROOT
        / "packages"
        / "hla-backend-python2025"
        / "src"
        / "hla"
        / "backends"
        / "python1516_2025"
        / "backend.py"
    )
    tree = ast.parse(backend_path.read_text(encoding="utf-8"), filename=str(backend_path))

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            imported_modules.add(node.module)

    forbidden_alias_modules = {
        "attribute_policy",
        "declaration_management",
        "federation_management",
        "interaction_policy",
        "save_restore",
        "support_lookup",
        "support_policy",
        "attribute_scope",
        "object_model",
        "object_reflection",
        "time_management",
        "update_rate",
    }
    required_runtime_modules = {
        "attribute_policy_runtime",
        "catalog_access_runtime",
        "declaration_ddm_surface_mixin",
        "delivery_state_runtime",
        "federation_bootstrap_runtime",
        "federation_management_runtime",
        "federation_state_runtime",
        "federation_time_surface_mixin",
        "input_guard_runtime",
        "interaction_policy_runtime",
        "mom_surface_mixin",
        "object_ownership_surface_mixin",
        "runtime_helper_surface_mixin",
        "save_restore_lifecycle",
        "support_surface_mixin",
        "attribute_scope_runtime",
        "object_model_runtime",
        "object_reflection_runtime",
        "time_management_runtime",
        "update_rate_runtime",
    }

    assert forbidden_alias_modules.isdisjoint(imported_modules)
    assert required_runtime_modules <= imported_modules


def test_split_python2025_runtime_modules_do_not_import_compatibility_export_modules() -> None:
    runtime_root = ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python1516_2025"
    compatibility_export_modules = {
        "attribute_policy",
        "attribute_scope",
        "declaration_management",
        "federation_management",
        "interaction_policy",
        "object_model",
        "object_reflection",
        "save_restore",
        "support_lookup",
        "support_policy",
        "time_management",
        "update_rate",
    }
    exempt_files = {
        "__init__.py",
        "backend.py",
        "compatibility_wrapper.py",
        "plugin.py",
        *(f"{name}.py" for name in compatibility_export_modules),
    }

    violations: list[str] = []
    for path in sorted(runtime_root.glob("*.py")):
        if path.name in exempt_files:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 1 and (node.module or "") in compatibility_export_modules:
                violations.append(
                    f"{path.relative_to(ROOT).as_posix()}: unexpected compatibility import {(node.module or '')!r}"
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("hla.backends.python2025."):
                        module = alias.name.rsplit(".", 1)[-1]
                        if module in compatibility_export_modules:
                            violations.append(
                                f"{path.relative_to(ROOT).as_posix()}: unexpected compatibility import {alias.name!r}"
                            )

    assert violations == []


def test_split_shim_helper_modules_remain_thin_python2025_reexports() -> None:
    shim_root = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    exempt_files = {"__init__.py", "backend.py", "plugin.py"}
    violations: list[str] = []

    for path in sorted(shim_root.glob("*.py")):
        if path.name in exempt_files:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    continue
                violations.append(f"{path.relative_to(ROOT).as_posix()}: unexpected expression")
                continue
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level != 0 or module == "__future__":
                    continue
                if not module.startswith("hla.backends.python2025"):
                    violations.append(
                        f"{path.relative_to(ROOT).as_posix()}: unexpected import-from {module!r}"
                    )
                continue
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name != "__future__":
                        violations.append(
                            f"{path.relative_to(ROOT).as_posix()}: unexpected import {alias.name!r}"
                        )
                continue
            if isinstance(node, ast.Assign):
                if any(not isinstance(target, ast.Name) or target.id != "__all__" for target in node.targets):
                    violations.append(f"{path.relative_to(ROOT).as_posix()}: unexpected assignment")
                continue
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                violations.append(f"{path.relative_to(ROOT).as_posix()}: local runtime symbol {node.name!r}")
                continue
            violations.append(
                f"{path.relative_to(ROOT).as_posix()}: unexpected top-level node {type(node).__name__}"
            )

    assert violations == []


def test_split_python2025_compatibility_export_modules_remain_thin_runtime_reexports() -> None:
    runtime_root = ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python1516_2025"
    expected_targets = {
        "attribute_policy.py": "attribute_policy_runtime",
        "attribute_scope.py": "attribute_scope_runtime",
        "declaration_management.py": "declaration_management_runtime",
        "federation_management.py": "federation_management_runtime",
        "interaction_policy.py": "interaction_policy_runtime",
        "object_model.py": "object_model_runtime",
        "object_reflection.py": "object_reflection_runtime",
        "save_restore.py": "save_restore_lifecycle",
        "support_lookup.py": "support_lookup_runtime",
        "support_policy.py": "support_policy_runtime",
        "time_management.py": "time_management_runtime",
        "update_rate.py": "update_rate_runtime",
    }
    violations: list[str] = []

    for filename, target_module in expected_targets.items():
        path = runtime_root / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        found_target = False
        for node in tree.body:
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    continue
                violations.append(f"{path.relative_to(ROOT).as_posix()}: unexpected expression")
                continue
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "__all__"
            ):
                continue
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level != 0 or module == "__future__":
                    if node.level == 1 and module == target_module:
                        found_target = True
                        continue
                    continue
                if module != target_module:
                    violations.append(
                        f"{path.relative_to(ROOT).as_posix()}: unexpected import-from {module!r}"
                    )
                else:
                    found_target = True
                continue
            violations.append(
                f"{path.relative_to(ROOT).as_posix()}: unexpected top-level node {type(node).__name__}"
            )
        if not found_target:
            violations.append(f"{path.relative_to(ROOT).as_posix()}: missing runtime reexport {target_module!r}")

    assert violations == []


def test_split_python2025_runtime_centralizes_shim_specific_ownership_in_compatibility_wrapper() -> None:
    runtime_root = ROOT / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python1516_2025"
    wrapper_path = runtime_root / "compatibility_wrapper.py"
    violations: list[str] = []
    shim_markers = ("Shim2025", "create_shim_backend", '"provider": "shim"', '"wrapper_only": True')

    for path in sorted(runtime_root.glob("*.py")):
        if path == wrapper_path:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in shim_markers:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: leaked shim marker {marker!r}")

        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.endswith("compatibility_wrapper"):
                    violations.append(
                        f"{path.relative_to(ROOT).as_posix()}: imports compatibility_wrapper via {module!r}"
                    )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.endswith("compatibility_wrapper"):
                        violations.append(
                            f"{path.relative_to(ROOT).as_posix()}: imports compatibility_wrapper via {alias.name!r}"
                        )

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
        "python1516_2025": "hla.backends.python2025.plugin:plugin"
    }
    assert python2025_pyproject["tool"]["hla"]["package"] == {
        "status": "implementation-owned",
        "role": "rti-backend",
        "backend_names": ["python1516_2025"],
        "backend_aliases": ["python-1516-2025", "python-1516-2025"],
        "source_roots": ["packages/hla-backend-python2025/src/hla/backends/python2025"],
    }

    assert shim_project["name"] == "hla-backend-shim"
    assert shim_project["description"] == "Temporary import-compatibility scaffolding package for the main full Python 2025 RTI"
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
    assert runtime_plugin.family == "python-rti-2025"
    assert runtime_discovery.description == "Primary Python 2025 RTI implementation package."
    assert runtime_discovery.family == "python-rti-2025"
    assert runtime_discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert runtime_discovery.info.details["counts_as_python_2025_rti"] is True
    assert "wrapper_only" not in runtime_discovery.info.details

    assert wrapper_plugin.description == "Deprecated compatibility-wrapper alias over the primary IEEE 1516.1-2025 Python RTI implementation; slated for removal."
    assert wrapper_plugin.family == "compatibility-wrapper-2025"
    assert wrapper_discovery.description == "Deprecated compatibility-wrapper alias over the primary IEEE 1516.1-2025 Python RTI implementation; slated for removal."
    assert wrapper_discovery.family == "compatibility-wrapper-2025"
    assert type(wrapper_discovery.info).__module__ == "hla.backends.python2025.compatibility_wrapper"
    assert wrapper_discovery.info.details["implementation_lane"] == "hla-backend-python2025"
    assert wrapper_discovery.info.details["counts_as_python_2025_rti"] is False
    assert wrapper_discovery.info.details["wrapper_only"] is True

    assert "owns the main full Python 2025 RTI runtime" in normalized_python2025_readme
    assert "public `hla.backends.python2025.backend` shell now fronts a split package layout" in normalized_python2025_readme
    assert "`backend_factory_runtime.py`" in python2025_readme
    assert "`runtime_state.py`" in python2025_readme
    assert "`federation_management_runtime.py`" in python2025_readme
    assert "`time_management_runtime.py`" in python2025_readme
    assert "`*_surface_mixin.py`" in python2025_readme
    assert "must not delegate back to `hla.backends.shim.backend.create_shim_backend`" in normalized_python2025_readme
    assert "promoted Python-owned 2025 RTI implementation lane" in normalized_python2025_readme
    assert "legacy compatibility-wrapper package and temporary import-compatibility scaffolding" in normalized_shim_readme
    assert "import-level compatibility surface" in normalized_shim_readme or "compatibility-wrapper" in normalized_shim_readme
    assert "the main full Python 2025 RTI implementation executes from `hla-backend-python2025`" in normalized_shim_readme
    assert "package root, the shim-specific surface is only `Shim2025Backend`, `Shim2025RTIAmbassador`, and `create_shim_backend`" in normalized_shim_readme
    assert "the other `hla.backends.shim.*` modules outside the package root: they are forwarders, not implementation owners" in normalized_shim_readme
    assert "`hla.backends.shim.runtime_aliases`" in shim_readme
