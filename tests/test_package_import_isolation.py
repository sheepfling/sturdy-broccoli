from __future__ import annotations

import ast
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"

# Installable package families are allowed to depend on a small, explicit set
# of sibling package roots. This keeps the split packages honest while still
# allowing the transitional spec/runtime facade under `hla2010`.
PACKAGE_IMPORT_ALLOWLISTS: dict[str, set[str]] = {
    "hla2010_rti_java_common": {"hla2010"},
    "hla2010_rti_java_jpype": {"hla2010", "hla2010_rti_java_common"},
    "hla2010_rti_java_py4j": {"hla2010", "hla2010_rti_java_common"},
    "hla2010_rti_python": {"hla2010"},
    "hla2010_rti_certi": {"hla2010", "hla2010_rti_java_common"},
    "hla2010_rti_pitch_common": {"hla2010", "hla2010_rti_java_jpype"},
    "hla2010_rti_pitch_jpype": {
        "hla2010",
        "hla2010_rti_java_common",
        "hla2010_rti_java_jpype",
        "hla2010_rti_pitch_common",
    },
    "hla2010_rti_pitch_py4j": {
        "hla2010",
        "hla2010_rti_java_common",
        "hla2010_rti_java_py4j",
        "hla2010_rti_pitch_common",
    },
    "hla2010_rti_portico": {
        "hla2010",
        "hla2010_rti_java_common",
        "hla2010_rti_java_jpype",
        "hla2010_rti_java_py4j",
    },
    "hla2010_rti_transport_grpc": {"hla2010", "hla2010_rti_certi", "hla2010_rti_python"},
    "hla2010_rti_transport_rest": {"hla2010", "hla2010_rti_certi", "hla2010_rti_python", "hla2010_rti_transport_grpc"},
    "hla2010_fom_target_radar": {"hla2010", "hla2010_rti_certi", "hla2010_rti_pitch_common"},
    "hla2010_verification_harness": {"hla2010"},
}

FORBIDDEN_IMPORT_PREFIXES = ("hla2010.testing",)


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


def _scan_package_source(package_name: str) -> list[tuple[Path, str]]:
    src_root = PACKAGES / package_name / "src"
    if not src_root.exists():
        return []
    allowed_roots = PACKAGE_IMPORT_ALLOWLISTS[package_name]
    issues: list[tuple[Path, str]] = []
    for path in src_root.rglob("*.py"):
        for module_name in _iter_imported_modules(path):
            if any(module_name == prefix or module_name.startswith(f"{prefix}.") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                issues.append((path, f"forbidden import of {module_name!r}"))
                continue
            root = _import_root(module_name)
            if root in PACKAGE_IMPORT_ALLOWLISTS and root not in allowed_roots and root != package_name:
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
        data = _load_pyproject(package_dir.name)
        project = data["project"]  # type: ignore[index]
        package_name = project["name"]  # type: ignore[index]
        if package_name not in PACKAGE_IMPORT_ALLOWLISTS:
            continue
        issues.extend(_scan_package_source(package_dir.name))

    assert not issues, "\n".join(f"{path}: {message}" for path, message in issues)
