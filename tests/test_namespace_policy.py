from __future__ import annotations

import ast
import tomllib
from pathlib import Path
import subprocess
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IMPORT_LINES = (
    "from hla2010.testing",
    "import hla2010.testing",
    "from hla2010_fom_target_radar.testing",
    "import hla2010_fom_target_radar.testing",
)
CODE_DIRS = ("src", "packages", "scripts", "tests")
PUBLIC_DOC_DIRS = ("README.md", "docs", "packages")
SKIP_PATH_PARTS = {
    "docs/evidence",
    "src/hla2010_repo_internal",
    "tests/test_namespace_policy.py",
    "packages/hla2010-rti-transport-grpc/src/hla2010_rti_transport_grpc/rti_transport_pb2.py",
    "packages/hla2010-rti-transport-grpc/src/hla2010_rti_transport_grpc/rti_transport_pb2_grpc.py",
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
    "hla2010.backends.base",
    "hla2010.backends.python",
    "hla2010.backends.conversion",
    "hla2010.backends.grpc_transport",
    "hla2010.backends.java_plugins",
    "hla2010.backends.transport",
    "hla2010.java_runtime",
    "hla2010.scenarios.target_radar",
    "hla2010.transport_registry",
)
PACKAGE_TRANSPORT_REGISTRY_IMPORTS_THROUGH_ROOT = (
    "from hla2010.rti import register_transport_factory",
    "from hla2010.rti import _coerce_transport_spec",
)
PACKAGE_RTI_ROOT_IMPORT_PREFIXES = (
    "from hla2010.rti import",
    "import hla2010.rti",
)
PACKAGE_ROOT_HELPER_IMPORT_PREFIXES = (
    "from hla2010.runtime_api import",
    "import hla2010.runtime_api",
)
SCRIPT_RTI_ROOT_IMPORT_PREFIXES = (
    "from hla2010.rti import",
    "import hla2010.rti",
)
FORBIDDEN_ROOT_VERIFICATION_FACADE_IMPORTS = (
    "from hla2010.conformance import",
    "import hla2010.conformance",
    "from hla2010.verification import",
    "import hla2010.verification",
    "from hla2010.clause13_conformance import",
    "import hla2010.clause13_conformance",
    "from hla2010.requirements_packet import",
    "import hla2010.requirements_packet",
    "from hla2010.requirements_backlog import",
    "import hla2010.requirements_backlog",
)
FORBIDDEN_PACKAGE_ROOT_FACADE_IMPORTS = (
)
FORBIDDEN_RUNTIME_CLASS_INJECTION_PATTERNS = (
    "setattr(RTIambassadorSpec",
    "setattr(FederateAmbassadorSpec",
    "setattr(DelegatingRTIAmbassador",
    "setattr(RecordingFederateAmbassador",
    "setattr(FederateAmbassadorMultiplexer",
    "setattr(PythonFederateAmbassadorDispatcher",
    "setattr(Py4JFederateAmbassadorProxy",
)
FORBIDDEN_PACKAGE_WALK_PATTERNS = (
    "__path__",
    "pkgutil.iter_modules",
)
FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS = (
    "Path(__file__).resolve().parents",
    "Path(__file__).resolve().parent.parent",
)
ALLOWLISTED_SELF_LOCATING_SCRIPTS = {
    "scripts/check_python_route_preflight.py",
    "scripts/check_certi_preflight.py",
    "scripts/check_vendor_runner_template_drift.py",
    "scripts/ci/check_doc_links.py",
    "scripts/ci/check_vendor_runtime_ci_state.py",
    "scripts/ci/write_vendor_probe_promotion_review.py",
    "scripts/ci/write_vendor_probe_stability.py",
    "scripts/ci/write_vendor_runtime_job_summary.py",
    "scripts/classify_vendor_runtime.py",
    "scripts/diagnose_pitch_exchange.py",
    "scripts/diagnose_pitch_negotiated_ownership.py",
    "scripts/discover_backend_compliance.py",
    "scripts/doctor.py",
    "scripts/generate_api_metadata.py",
    "scripts/generate_clause13_conformance_packet.py",
    "scripts/generate_compliance_artifacts.py",
    "scripts/generate_fom_overview.py",
    "scripts/generate_hla_interface_contracts.py",
    "scripts/generate_imported_packet_backlog.py",
    "scripts/generate_imported_packet_requirements_docs.py",
    "scripts/generate_master_harmonization_index.py",
    "scripts/generate_package_dependency_tree.py",
    "scripts/generate_python_rti_service_map.py",
    "scripts/generate_runtime_method_index.py",
    "scripts/human_editability.py",
    "scripts/new_fom_package.py",
    "scripts/probe_pitch_native_local.py",
    "scripts/repro_pitch_crc_docker.py",
    "scripts/repro_pitch_crc_macos.py",
    "scripts/run_python_route_parity_matrix.py",
    "scripts/run_target_radar_backend_matrix.py",
    "scripts/run_target_radar_proof.py",
    "scripts/run_two_federate_suite.py",
    "scripts/run_vendor_parity_artifacts.py",
    "scripts/test_surface.py",
    "scripts/update_rti_options_matrix.py",
    "scripts/validate_package_graph.py",
    "scripts/write_vendor_gap_profile.py",
}


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


def _scan_lines(
    paths: list[Path],
    *,
    skip: Callable[[str, Path], bool] | None = None,
    line_matches: Callable[[str, Path, str], bool] | None = None,
) -> list[str]:
    violations: list[str] = []
    for path in paths:
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if skip is not None and skip(rel, path):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if line_matches is not None and line_matches(rel, path, stripped):
                violations.append(f"{rel}:{lineno}: {stripped}")
    return violations

def _contains_any_pattern(patterns: tuple[str, ...], stripped: str) -> bool:
    return any(pattern in stripped for pattern in patterns)


def _starts_with_any_prefix(prefixes: tuple[str, ...], stripped: str) -> bool:
    return stripped.startswith(prefixes)


def test_repo_code_does_not_import_removed_public_testing_namespaces() -> None:
    violations = _find_forbidden_lines(_iter_python_files())
    assert not violations, "\n".join(violations)


def test_public_docs_do_not_recommend_removed_testing_namespaces() -> None:
    violations = _find_forbidden_lines(_iter_public_docs())
    assert not violations, "\n".join(violations)


def test_removed_testing_source_trees_have_no_python_modules() -> None:
    legacy_roots = (
        ROOT / "src/hla2010/testing",
        ROOT / "packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/testing",
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
    violations = _scan_lines(
        _iter_python_files(),
        skip=lambda rel, path: rel.startswith("scripts/") or rel == "tests/vendors/pitch_jpype_lost_federate_child.py",
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_BOOTSTRAP_PATTERNS + FORBIDDEN_SYS_PATH_PATTERNS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_public_packages_do_not_use_dynamic_exports_or_package_walking() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_DYNAMIC_ALL_PATTERNS + FORBIDDEN_PACKAGE_WALK_PATTERNS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_maintained_package_code_does_not_use_wildcard_facades_or_runtime_class_injection() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_WILDCARD_IMPORT_PATTERNS + FORBIDDEN_RUNTIME_CLASS_INJECTION_PATTERNS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_maintained_code_does_not_import_removed_compatibility_paths() -> None:
    violations = _scan_lines(
        _iter_python_files(),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_REMOVED_COMPAT_IMPORT_PATTERNS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_public_packages_do_not_sniff_repo_root_from_file_paths() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_installable_package_code_does_not_depend_on_root_backend_or_transport_facades() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_PACKAGE_ROOT_FACADE_IMPORTS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_repo_aware_scripts_that_self_locate_are_explicitly_allowlisted() -> None:
    actual: set[str] = set()
    for path in _iter_script_python_files():
        if _should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if any(pattern in text for pattern in FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS):
            actual.add(rel)
    assert actual == ALLOWLISTED_SELF_LOCATING_SCRIPTS


def test_non_allowlisted_scripts_do_not_sniff_repo_root_from_file_paths() -> None:
    violations = _scan_lines(
        _iter_script_python_files(),
        skip=lambda rel, path: rel in ALLOWLISTED_SELF_LOCATING_SCRIPTS,
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_PACKAGE_REPO_ROOT_PATTERNS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_package_owned_transport_helpers_do_not_import_transport_registry_through_root_facade() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        skip=lambda rel, path: not rel.startswith("packages/"),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            PACKAGE_TRANSPORT_REGISTRY_IMPORTS_THROUGH_ROOT,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_package_owned_code_does_not_import_root_rti_factory_facade() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        skip=lambda rel, path: not rel.startswith("packages/"),
        line_matches=lambda rel, path, stripped: _starts_with_any_prefix(
            PACKAGE_RTI_ROOT_IMPORT_PREFIXES,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_package_owned_code_does_not_import_root_callback_helper_facades() -> None:
    violations = _scan_lines(
        _iter_package_python_files(),
        skip=lambda rel, path: not rel.startswith("packages/"),
        line_matches=lambda rel, path, stripped: _starts_with_any_prefix(
            PACKAGE_ROOT_HELPER_IMPORT_PREFIXES,
            stripped,
        ),
    )
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
    violations = _scan_lines(
        sorted((ROOT / "scripts").rglob("*.py")),
        line_matches=lambda rel, path, stripped: _contains_any_pattern(
            FORBIDDEN_ROOT_VERIFICATION_FACADE_IMPORTS,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_repo_scripts_do_not_import_root_rti_factory_facade() -> None:
    violations = _scan_lines(
        _iter_script_python_files(),
        line_matches=lambda rel, path, stripped: _starts_with_any_prefix(
            SCRIPT_RTI_ROOT_IMPORT_PREFIXES,
            stripped,
        ),
    )
    assert not violations, "\n".join(violations)


def test_repo_scripts_do_not_import_root_runtime_callback_facades() -> None:
    violations = _scan_lines(
        _iter_script_python_files(),
        line_matches=lambda rel, path, stripped: (
            stripped.startswith("from hla2010.runtime_api import FederateAmbassador")
            or stripped.startswith("from hla2010.ambassadors import")
            or stripped.startswith("import hla2010.ambassadors")
        ),
    )
    assert not violations, "\n".join(violations)


def test_examples_do_not_import_removed_root_scenario_facades() -> None:
    violations = _scan_lines(
        sorted((ROOT / "examples").rglob("*.py")),
        line_matches=lambda rel, path, stripped: (
            "from hla2010.scenarios" in stripped or "import hla2010.scenarios" in stripped
        ),
    )
    assert not violations, "\n".join(violations)


def test_examples_do_not_import_removed_root_backend_facades() -> None:
    violations = _scan_lines(
        sorted((ROOT / "examples").rglob("*.py")),
        line_matches=lambda rel, path, stripped: (
            "from hla2010.backends." in stripped or "import hla2010.backends." in stripped
        ),
    )
    assert not violations, "\n".join(violations)


def test_examples_and_public_docs_do_not_promote_root_rti_import_form() -> None:
    paths = sorted((ROOT / "examples").rglob("*.py")) + _iter_public_docs()
    violations = _scan_lines(
        paths,
        line_matches=lambda rel, path, stripped: (
            stripped.startswith("from hla2010.rti import") or stripped.startswith("import hla2010.rti")
        ),
    )
    assert not violations, "\n".join(violations)


def test_examples_do_not_import_root_runtime_callback_facades() -> None:
    violations = _scan_lines(
        sorted((ROOT / "examples").rglob("*.py")),
        line_matches=lambda rel, path, stripped: (
            stripped.startswith("from hla2010.runtime_api import FederateAmbassador")
            or stripped.startswith("from hla2010.ambassadors import")
            or stripped.startswith("import hla2010.ambassadors")
        ),
    )
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
    root_package = ROOT / "packages/hla2010-spec/src/hla2010"
    violations: list[str] = []
    allowed_rti_import = "hla2010_rti_runtime_common"
    forbidden_prefixes = (
        "hla2010_rti_",
        "hla2010_verification_harness",
        "hla2010_fom_target_radar",
        "hla2010_repo_internal",
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
        if rel == "packages/hla2010-spec/src/hla2010/rti.py":
            unexpected = [name for name in forbidden if name != allowed_rti_import]
            if unexpected:
                violations.append(f"{rel}: unexpected split-package import(s): {', '.join(sorted(unexpected))}")
            if allowed_rti_import not in imported_modules:
                violations.append(f"{rel}: expected temporary runtime-common facade import is missing")
            continue
        if forbidden:
            violations.append(f"{rel}: {', '.join(sorted(forbidden))}")
    assert not violations, "\n".join(violations)
