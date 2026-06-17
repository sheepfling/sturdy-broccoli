from __future__ import annotations

import ast
import tomllib
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IMPORT_LINES = (
    "from hla.rti1516e.testing",
    "import hla.rti1516e.testing",
    "from hla.foms.target_radar.testing",
    "import hla.foms.target_radar.testing",
    "from hla.foms.target_radar.scenarios",
    "import hla.foms.target_radar.scenarios",
)
CODE_DIRS = ("src", "packages", "scripts", "tests")
PUBLIC_DOC_DIRS = ("README.md", "docs", "packages")
SKIP_PATH_PARTS = {
    "docs/evidence",
    "packages/hla-verification/src/hla/verification/repo_internal",
    "tests/test_namespace_policy.py",
    "packages/hla-vendor-pitch/src/hla/vendors/pitch/__init__.py",
    "tests/test_rti_python_split_package.py",
    "tests/test_rti_transport_grpc_split_package.py",
}
PACKAGE_CODE_DIRS = ("src/hla2010", "packages")
FORBIDDEN_BOOTSTRAP_PATTERNS = (
    "import _bootstrap",
    "from _bootstrap import",
    "from repo_python_env import",
    "ensure_repo_pythonpath(",
)
FORBIDDEN_SYS_PATH_PATTERNS = (
    "sys.path.insert",
    "sys.path.append",
    "site.addsitedir",
    "os.execv(",
    "os.execve(",
    "os.execvp(",
    "os.execvpe(",
)
FORBIDDEN_DYNAMIC_ALL_PATTERNS = (
    "__all__ = [name for name in globals()",
    "__all__ = [name for name, value in globals()",
    "__all__ = tuple(",
)
FORBIDDEN_WILDCARD_IMPORT_PATTERNS = (
    " import *",
)
FORBIDDEN_REMOVED_COMPAT_IMPORT_PATTERNS = (
    "hla.rti1516e.backends.base",
    "hla.rti1516e.backends.python",
    "hla.rti1516e.backends.conversion",
    "hla.rti1516e.backends.grpc_transport",
    "hla.rti1516e.backends.java_plugins",
    "hla.rti1516e.backends.transport",
    "hla.rti1516e.java_runtime",
    "hla.rti1516e.scenarios.target_radar",
    "hla.rti1516e.transport_registry",
)
PACKAGE_TRANSPORT_REGISTRY_IMPORTS_THROUGH_ROOT = (
    "from hla.rti1516e.rti import register_transport_factory",
    "from hla.rti1516e.rti import _coerce_transport_spec",
)
PACKAGE_RTI_ROOT_IMPORT_PREFIXES = (
    "from hla.rti1516e.rti import",
    "import hla.rti1516e.rti",
)
PACKAGE_ROOT_HELPER_IMPORT_PREFIXES = (
    "from hla.rti1516e.ambassadors import",
    "import hla.rti1516e.ambassadors",
    "from hla.rti1516e.runtime_api import",
    "import hla.rti1516e.runtime_api",
)
SCRIPT_RTI_ROOT_IMPORT_PREFIXES = (
    "from hla.rti1516e.rti import",
    "import hla.rti1516e.rti",
)
FORBIDDEN_ROOT_VERIFICATION_FACADE_IMPORTS = (
    "from hla.rti1516e.conformance import",
    "import hla.rti1516e.conformance",
    "from hla.rti1516e.verification import",
    "import hla.rti1516e.verification",
    "from hla.rti1516e.clause13_conformance import",
    "import hla.rti1516e.clause13_conformance",
    "from hla.rti1516e.requirements_packet import",
    "import hla.rti1516e.requirements_packet",
    "from hla.rti1516e.requirements_backlog import",
    "import hla.rti1516e.requirements_backlog",
)
FORBIDDEN_PACKAGE_ROOT_FACADE_IMPORTS = (
)
FORBIDDEN_RUNTIME_CLASS_INJECTION_PATTERNS = (
    "setattr(RTIambassador",
    "setattr(NullFederateAmbassador",
    "setattr(PythonicRTIAmbassadorMixin",
    "setattr(DelegatingRTIAmbassador",
    "setattr(RecordingFederateAmbassador",
    "setattr(FederateAmbassadorMultiplexer",
    "setattr(PythonFederateAmbassadorDispatcher",
    "setattr(Py4JFederateAmbassadorProxy",
    "setattr(_CERTIJavaFederateAdapter",
)
FORBIDDEN_PACKAGE_WALK_PATTERNS = (
    "__path__",
    "pkgutil.iter_modules",
)
FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS = (
    "Path(__file__).resolve().parents",
    "Path(__file__).resolve().parent.parent",
)


def _iter_python_files() -> list[Path]:
    paths: list[Path] = []
    for root_name in CODE_DIRS:
        root = ROOT / root_name
        if root.is_file():
            paths.append(root)
            continue
        paths.extend(root.rglob("*.py"))
    return sorted(paths)


def _iter_package_python_files() -> list[Path]:
    paths: list[Path] = []
    for root_name in PACKAGE_CODE_DIRS:
        root = ROOT / root_name
        if root.exists():
            paths.extend(root.rglob("*.py"))
    return sorted(paths)


def _iter_script_python_files() -> list[Path]:
    root = ROOT / "scripts"
    return sorted(root.rglob("*.py")) if root.exists() else []


def _iter_public_docs() -> list[Path]:
    paths: list[Path] = []
    for root_name in PUBLIC_DOC_DIRS:
        root = ROOT / root_name
        if root.is_file():
            paths.append(root)
            continue
        paths.extend(root.rglob("*.md"))
    return sorted(paths)


def _should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(rel == skip or rel.startswith(f"{skip}/") for skip in SKIP_PATH_PARTS)


def _find_forbidden_lines(paths: list[Path]) -> list[str]:
    violations: list[str] = []
    for path in paths:
        if _should_skip(path):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(stripped.startswith(prefix) for prefix in FORBIDDEN_IMPORT_LINES):
                rel = path.relative_to(ROOT).as_posix()
                violations.append(f"{rel}:{lineno}: {stripped}")
    return violations


def test_repo_code_does_not_import_removed_public_testing_namespaces() -> None:
    violations = _find_forbidden_lines(_iter_python_files())
    assert not violations, "\n".join(violations)


def test_public_docs_do_not_recommend_removed_testing_namespaces() -> None:
    violations = _find_forbidden_lines(_iter_public_docs())
    assert not violations, "\n".join(violations)


def test_removed_testing_source_trees_have_no_python_modules() -> None:
    legacy_roots = (
        ROOT / "src/hla2010/testing",
        ROOT / "packages/hla-fom-target-radar/src/hla.foms.target_radar/testing",
    )
    leftovers: list[str] = []
    for root in legacy_roots:
        leftovers.extend(str(path.relative_to(ROOT)) for path in sorted(root.rglob("*.py")))
    assert not leftovers, "\n".join(leftovers)


def test_core_source_tree_contains_no_cached_or_desktop_artifacts() -> None:
    tracked_noise_patterns = (
        "src/**/*.pyc",
        "src/**/__pycache__/*",
        "packages/**/*.pyc",
        "packages/**/__pycache__/*",
        "scripts/**/*.pyc",
        "scripts/**/__pycache__/*",
        "tests/**/*.pyc",
        "tests/**/__pycache__/*",
        "tools/**/*.pyc",
        "tools/**/__pycache__/*",
        "src/.DS_Store",
        "packages/.DS_Store",
        "scripts/.DS_Store",
        "tests/.DS_Store",
        "tools/.DS_Store",
    )
    result = subprocess.run(
        [
            "git",
            "ls-files",
            *tracked_noise_patterns,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    leftovers = [line for line in result.stdout.splitlines() if line]
    assert not leftovers, "\n".join(sorted(leftovers))


def test_root_pyproject_is_tooling_only() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "build-system" not in data
    assert "project" not in data
    assert "setuptools" not in data.get("tool", {})
    assert "pytest" in data.get("tool", {})


def test_repo_code_does_not_use_import_bootstrap_or_sys_path_mutation() -> None:
    violations: list[str] = []
    for path in _iter_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("scripts/") or rel == "tests/vendors/pitch_jpype_lost_federate_child.py":
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_BOOTSTRAP_PATTERNS + FORBIDDEN_SYS_PATH_PATTERNS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_public_packages_do_not_use_dynamic_exports_or_package_walking() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_DYNAMIC_ALL_PATTERNS + FORBIDDEN_PACKAGE_WALK_PATTERNS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_maintained_package_code_does_not_use_wildcard_facades_or_runtime_class_injection() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_WILDCARD_IMPORT_PATTERNS + FORBIDDEN_RUNTIME_CLASS_INJECTION_PATTERNS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_maintained_code_does_not_import_removed_compatibility_paths() -> None:
    violations: list[str] = []
    for path in _iter_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_REMOVED_COMPAT_IMPORT_PATTERNS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_public_packages_do_not_sniff_repo_root_from_file_paths() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_installable_package_code_does_not_depend_on_root_backend_or_transport_facades() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_PACKAGE_ROOT_FACADE_IMPORTS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_scripts_do_not_sniff_repo_root_from_file_paths() -> None:
    violations: list[str] = []
    for path in _iter_script_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        # The canonical operator scripts intentionally self-locate the checkout
        # so they can bootstrap from a clean outside-checkout invocation.
        # Their behavior is covered by direct wrapper tests instead.
        continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_package_owned_transport_helpers_do_not_import_transport_registry_through_root_facade() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if not rel.startswith("packages/"):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in PACKAGE_TRANSPORT_REGISTRY_IMPORTS_THROUGH_ROOT):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_package_owned_code_does_not_import_root_rti_factory_facade() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if not rel.startswith("packages/"):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith(PACKAGE_RTI_ROOT_IMPORT_PREFIXES):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_package_owned_code_does_not_import_root_callback_helper_facades() -> None:
    violations: list[str] = []
    for path in _iter_package_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if not rel.startswith("packages/"):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith(PACKAGE_ROOT_HELPER_IMPORT_PREFIXES):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_core_package_contains_no_argparse_cli_surface() -> None:
    violations: list[str] = []
    root = ROOT / "src/hla2010"
    for path in sorted(root.rglob("*.py")):
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped == "import argparse" or stripped.startswith("import argparse ") or "argparse.ArgumentParser(" in stripped:
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_installable_packages_do_not_expose_cli_named_modules() -> None:
    violations: list[str] = []
    packages_root = ROOT / "packages"
    for path in sorted(packages_root.rglob("*.py")):
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.name.endswith("_cli.py"):
            violations.append(rel)
    assert not violations, "\n".join(violations)


def test_repo_scripts_do_not_import_root_verification_facade() -> None:
    violations: list[str] = []
    for path in sorted((ROOT / "scripts").rglob("*.py")):
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if any(pattern in stripped for pattern in FORBIDDEN_ROOT_VERIFICATION_FACADE_IMPORTS):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_repo_scripts_do_not_import_root_rti_factory_facade() -> None:
    violations: list[str] = []
    for path in _iter_script_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith(SCRIPT_RTI_ROOT_IMPORT_PREFIXES):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_repo_scripts_do_not_import_root_runtime_callback_facades() -> None:
    violations: list[str] = []
    for path in _iter_script_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if (
                stripped.startswith("from hla.rti1516e.runtime_api import FederateAmbassador")
                or stripped.startswith("from hla.rti1516e.ambassadors import")
                or stripped.startswith("import hla.rti1516e.ambassadors")
            ):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_examples_do_not_import_removed_root_scenario_facades() -> None:
    violations: list[str] = []
    for path in sorted((ROOT / "examples").rglob("*.py")):
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if "from hla.rti1516e.scenarios" in stripped or "import hla.rti1516e.scenarios" in stripped:
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_examples_do_not_import_removed_root_backend_facades() -> None:
    violations: list[str] = []
    for path in sorted((ROOT / "examples").rglob("*.py")):
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if "from hla.rti1516e.backends." in stripped or "import hla.rti1516e.backends." in stripped:
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_examples_and_public_docs_do_not_promote_root_rti_import_form() -> None:
    violations: list[str] = []
    paths = sorted((ROOT / "examples").rglob("*.py")) + _iter_public_docs()
    for path in paths:
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("from hla.rti1516e.rti import") or stripped.startswith("import hla.rti1516e.rti"):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_examples_do_not_import_root_runtime_callback_facades() -> None:
    violations: list[str] = []
    for path in sorted((ROOT / "examples").rglob("*.py")):
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if (
                stripped.startswith("from hla.rti1516e.runtime_api import FederateAmbassador")
                or stripped.startswith("from hla.rti1516e.ambassadors import")
                or stripped.startswith("import hla.rti1516e.ambassadors")
            ):
                violations.append(f"{rel}:{lineno}: {stripped}")
    assert not violations, "\n".join(violations)


def test_core_package_contains_no_root_verification_or_work_packet_facades() -> None:
    removed = (
        ROOT / "src/hla2010/conformance.py",
        ROOT / "src/hla2010/verification.py",
        ROOT / "src/hla2010/clause13_conformance.py",
        ROOT / "src/hla2010/requirements_packet.py",
        ROOT / "src/hla2010/requirements_backlog.py",
        ROOT / "src/hla2010/fom_overview.py",
        ROOT / "src/hla2010/mom_negative_testing.py",
        ROOT / "src/hla2010/mom_catalog.py",
        ROOT / "src/hla2010/startup.py",
        ROOT / "src/hla2010/service_reporting.py",
        ROOT / "src/hla2010/time_management.py",
        ROOT / "src/hla2010/plugin_api.py",
        ROOT / "src/hla2010/transport_codecs.py",
    )
    leftovers = [path.relative_to(ROOT).as_posix() for path in removed if path.exists()]
    assert not leftovers, "\n".join(leftovers)


def test_root_hla2010_package_stays_split_package_free_except_for_hla2010_rti() -> None:
    root_package = ROOT / "src/hla2010"
    violations: list[str] = []
    allowed_rti_import = "hla.rti"
    forbidden_prefixes = (
        "hla2010_rti_",
        "hla.verification",
        "hla.foms.target_radar",
        "hla.verification.repo_internal",
    )
    for path in sorted(root_package.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        forbidden = [name for name in imported_modules if name.startswith(forbidden_prefixes)]
        if rel == "src/hla2010/rti.py":
            unexpected = [name for name in forbidden if name != allowed_rti_import]
            if unexpected:
                violations.append(f"{rel}: unexpected split-package import(s): {', '.join(sorted(unexpected))}")
            if allowed_rti_import not in imported_modules:
                violations.append(f"{rel}: expected temporary runtime-common facade import is missing")
            continue
        if forbidden:
            violations.append(f"{rel}: {', '.join(sorted(forbidden))}")
    assert not violations, "\n".join(violations)
