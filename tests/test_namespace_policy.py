from __future__ import annotations

import tomllib
from pathlib import Path


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
}
PACKAGE_CODE_DIRS = ("src/hla2010", "packages")
FORBIDDEN_BOOTSTRAP_PATTERNS = (
    "import _bootstrap",
    "from _bootstrap import",
)
FORBIDDEN_SYS_PATH_PATTERNS = (
    "sys.path.insert",
    "sys.path.append",
)
FORBIDDEN_DYNAMIC_ALL_PATTERNS = (
    "__all__ = [name for name in globals()",
    "__all__ = [name for name, value in globals()",
    "__all__ = tuple(",
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
        ROOT / "packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/testing",
    )
    leftovers: list[str] = []
    for root in legacy_roots:
        leftovers.extend(str(path.relative_to(ROOT)) for path in sorted(root.rglob("*.py")))
    assert not leftovers, "\n".join(leftovers)


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
