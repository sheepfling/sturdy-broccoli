from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from hla2010_repo_internal.package_graph import load_package_graph, package_import_allowlists


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"
PACKAGE_IMPORT_ALLOWLISTS = package_import_allowlists(load_package_graph(ROOT / "packages" / "package_graph.yaml"))

FORBIDDEN_IMPORT_PREFIXES = (
    "hla2010.testing",
    "hla2010_repo_internal",
    "hla2010_fom_target_radar.testing",
    "hla2010_fom_minimal_demo.testing",
)


def _load_pyproject(package_name: str) -> dict[str, object]:
    return tomllib.loads((PACKAGES / package_name / "pyproject.toml").read_text(encoding="utf-8"))


def _import_root(module_name: str) -> str:
    return module_name.split(".", 1)[0]


def _iter_imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.append(node.module)
    return modules


def _scan_package_source(package_dir_name: str, package_import_root: str) -> list[tuple[Path, str]]:
    split = _load_pyproject(package_dir_name)["tool"]["hla2010"]["package-split"]  # type: ignore[index]
    source_roots = split["source_roots"]  # type: ignore[index]
    allowed_roots = PACKAGE_IMPORT_ALLOWLISTS[package_import_root]
    issues: list[tuple[Path, str]] = []
    seen_paths: set[Path] = set()
    for source_root in source_roots:
        root_path = ROOT / str(source_root)
        if not root_path.exists():
            continue
        if root_path.is_file():
            candidate_paths = [root_path] if root_path.suffix == ".py" else []
        else:
            candidate_paths = sorted(root_path.rglob("*.py"))
        for path in candidate_paths:
            if path in seen_paths:
                continue
            seen_paths.add(path)
            for module_name in _iter_imported_modules(path):
                if any(module_name == prefix or module_name.startswith(f"{prefix}.") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    issues.append((path, f"forbidden import of {module_name!r}"))
                    continue
                root = _import_root(module_name)
                if root in PACKAGE_IMPORT_ALLOWLISTS and root not in allowed_roots and root != package_import_root:
                    issues.append((path, f"import of sibling package root {root!r} is not allowed"))
    return issues


def test_installable_package_roots_do_not_cross_import_outside_their_allowlist() -> None:
    issues: list[tuple[Path, str]] = []

    for package_dir in sorted(PACKAGES.iterdir()):
        if not package_dir.is_dir():
            continue
        pyproject = package_dir / "pyproject.toml"
        if not pyproject.exists():
            continue
        package_import_root = package_dir.name.replace("-", "_")
        if package_import_root not in PACKAGE_IMPORT_ALLOWLISTS:
            continue
        issues.extend(_scan_package_source(package_dir.name, package_import_root))

    assert not issues, "\n".join(f"{path}: {message}" for path, message in issues)
