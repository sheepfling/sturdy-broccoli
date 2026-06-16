from __future__ import annotations

import ast
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"

OWNED_PREFIX_TO_PACKAGE = {
    "hla.rti": "hla-rti-core",
    "hla.rti1516e": "hla-rti1516e",
    "hla.rti1516_2025": "hla-rti1516-2025",
    "hla.backends.common": "hla-backend-common",
    "hla.backends.inmemory": "hla-backend-inmemory",
    "hla.backends.shim": "hla-backend-shim",
    "hla.backends.certi": "hla-backend-certi",
    "hla.bridges.java.common": "hla-bridge-java-common",
    "hla.bridges.java.jpype": "hla-bridge-java-jpype",
    "hla.bridges.java.py4j": "hla-bridge-java-py4j",
    "hla.vendors.pitch": "hla-vendor-pitch",
    "hla.vendors.pitch.jpype": "hla-vendor-pitch-jpype",
    "hla.vendors.pitch.py4j": "hla-vendor-pitch-py4j",
    "hla.vendors.portico": "hla-vendor-portico",
    "hla.transports.common": "hla-transport-common",
    "hla.transports.grpc": "hla-transport-grpc",
    "hla.transports.rest": "hla-transport-rest",
    "hla.transports.fedpro": "hla-transport-fedpro",
    "hla.foms.target_radar": "hla-fom-target-radar",
    "hla.verification": "hla-verification",
}

ALLOWED_PACKAGE_DEPENDENCIES: dict[str, set[str]] = {
    "hla-rti-core": {"hla-backend-common", "hla-transport-common"},
    "hla-rti1516e": {"hla-rti-core"},
    "hla-rti1516-2025": {"hla-rti-core"},
    "hla-backend-common": {"hla-rti1516e", "hla-rti-core"},
    "hla-backend-shim": {"hla-rti1516-2025", "hla-rti-core"},
    "hla-backend-inmemory": {"hla-rti1516e", "hla-backend-common", "hla-rti-core"},
    "hla-backend-certi": {"hla-rti1516e", "hla-backend-common", "hla-rti-core", "hla-transport-common"},
    "hla-bridge-java-common": {"hla-rti1516e", "hla-backend-common", "hla-rti-core"},
    "hla-bridge-java-jpype": {"hla-rti1516e", "hla-backend-common", "hla-bridge-java-common", "hla-rti-core"},
    "hla-bridge-java-py4j": {"hla-rti1516e", "hla-bridge-java-common", "hla-rti-core"},
    "hla-vendor-pitch": {"hla-rti1516e", "hla-bridge-java-common", "hla-rti-core"},
    "hla-vendor-pitch-jpype": {"hla-rti1516e", "hla-bridge-java-common", "hla-bridge-java-jpype", "hla-rti-core", "hla-vendor-pitch"},
    "hla-vendor-pitch-py4j": {"hla-rti1516e", "hla-bridge-java-common", "hla-bridge-java-py4j", "hla-rti-core", "hla-vendor-pitch"},
    "hla-vendor-portico": {"hla-rti1516e", "hla-bridge-java-common", "hla-bridge-java-jpype", "hla-bridge-java-py4j", "hla-rti-core"},
    "hla-transport-common": {"hla-rti1516e", "hla-backend-common"},
    "hla-transport-grpc": {"hla-rti1516e", "hla-backend-common", "hla-rti-core", "hla-transport-common"},
    "hla-transport-rest": {"hla-rti1516e", "hla-backend-common", "hla-rti-core", "hla-transport-common"},
    "hla-fom-target-radar": {"hla-rti1516e", "hla-rti-core", "hla-verification"},
    "hla-verification": {
        "hla-rti1516e",
        "hla-backend-common",
        "hla-backend-inmemory",
        "hla-bridge-java-common",
        "hla-fom-target-radar",
        "hla-rti-core",
    },
}

FORBIDDEN_IMPORT_PREFIXES = (
    "hla.rti1516e.testing",
    "hla.foms.target_radar.testing",
)


def _load_pyproject(package_name: str) -> dict[str, object]:
    return tomllib.loads((PACKAGES / package_name / "pyproject.toml").read_text(encoding="utf-8"))


def ownership_prefix(module_name: str) -> str | None:
    matches = [
        prefix
        for prefix in OWNED_PREFIX_TO_PACKAGE
        if module_name == prefix or module_name.startswith(prefix + ".")
    ]
    return max(matches, key=len) if matches else None


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
    split = _load_pyproject(package_dir_name)["tool"]["hla"]["package"]  # type: ignore[index]
    source_roots = split["source_roots"]  # type: ignore[index]
    allowed_packages = ALLOWED_PACKAGE_DEPENDENCIES[package_dir_name]
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
                imported_prefix = ownership_prefix(module_name)
                if imported_prefix is None:
                    continue
                imported_package = OWNED_PREFIX_TO_PACKAGE[imported_prefix]
                if imported_package != package_dir_name and imported_package not in allowed_packages:
                    issues.append((path, f"import of sibling package {imported_package!r} via {imported_prefix!r} is not allowed"))
    return issues


def test_installable_package_roots_do_not_cross_import_outside_their_allowlist() -> None:
    issues: list[tuple[Path, str]] = []

    for package_dir in sorted(PACKAGES.iterdir()):
        if not package_dir.is_dir():
            continue
        pyproject = package_dir / "pyproject.toml"
        if not pyproject.exists():
            continue
        if package_dir.name not in ALLOWED_PACKAGE_DEPENDENCIES:
            continue
        issues.extend(_scan_package_source(package_dir.name, package_dir.name))

    assert not issues, "\n".join(f"{path}: {message}" for path, message in issues)
