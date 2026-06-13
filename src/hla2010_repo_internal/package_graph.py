from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = ROOT / "packages"
PACKAGE_GRAPH_PATH = PACKAGES_DIR / "package_graph.yaml"
BACKEND_ENTRY_POINT_GROUP = "hla2010.rti_backends"
DEP_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")


def parse_dependency_name(spec: str) -> str:
    match = DEP_NAME_RE.match(spec.strip())
    if not match:
        return spec.strip()
    return match.group(1)


def load_package_graph(path: Path | None = None) -> dict[str, dict[str, object]]:
    graph_path = path or PACKAGE_GRAPH_PATH
    payload = json.loads(graph_path.read_text(encoding="utf-8"))
    packages = payload.get("packages")
    if not isinstance(packages, dict):
        raise ValueError(f"{graph_path} must define a top-level 'packages' object")
    return {str(name): dict(entry) for name, entry in packages.items()}


def load_package_manifests(packages_dir: Path | None = None) -> dict[str, dict[str, object]]:
    root = packages_dir or PACKAGES_DIR
    manifests: dict[str, dict[str, object]] = {}
    for pyproject in sorted(root.glob("*/pyproject.toml")):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        manifests[str(data["project"]["name"])] = data
    return manifests


def internal_dependencies(manifest: dict[str, object], internal_names: set[str]) -> list[str]:
    project = manifest["project"]  # type: ignore[index]
    deps = project.get("dependencies", [])  # type: ignore[assignment]
    internal = [parse_dependency_name(str(dep)) for dep in deps]
    return sorted(name for name in internal if name in internal_names)


def external_dependencies(manifest: dict[str, object], internal_names: set[str]) -> list[str]:
    project = manifest["project"]  # type: ignore[index]
    deps = project.get("dependencies", [])  # type: ignore[assignment]
    external = [parse_dependency_name(str(dep)) for dep in deps]
    return sorted(name for name in external if name not in internal_names)


def import_root_to_package(graph: dict[str, dict[str, object]]) -> dict[str, str]:
    return {
        str(entry["import_root"]): package_name
        for package_name, entry in graph.items()
    }


def package_import_allowlists(graph: dict[str, dict[str, object]]) -> dict[str, set[str]]:
    import_roots = {
        package_name: str(entry["import_root"])
        for package_name, entry in graph.items()
    }
    allowlists: dict[str, set[str]] = {}
    for package_name, entry in graph.items():
        allowlists[import_roots[package_name]] = {
            import_roots[dep_name]
            for dep_name in entry.get("may_depend_on", [])
        }
    return allowlists


def package_source_roots(manifest: dict[str, object]) -> list[str]:
    split = manifest["tool"]["hla2010"]["package-split"]  # type: ignore[index]
    return [str(path) for path in split["source_roots"]]  # type: ignore[index]


def package_role(manifest: dict[str, object]) -> str:
    split = manifest["tool"]["hla2010"]["package-split"]  # type: ignore[index]
    return str(split["role"])


def package_status(manifest: dict[str, object]) -> str:
    split = manifest["tool"]["hla2010"]["package-split"]  # type: ignore[index]
    return str(split["status"])


def package_backend_names(manifest: dict[str, object]) -> list[str]:
    split = manifest["tool"]["hla2010"]["package-split"]  # type: ignore[index]
    return sorted(str(name) for name in split.get("backend_names", []))  # type: ignore[union-attr]


def backend_entry_points(manifest: dict[str, object]) -> list[str]:
    project = manifest["project"]  # type: ignore[index]
    groups = project.get("entry-points", {})  # type: ignore[assignment]
    backends = groups.get(BACKEND_ENTRY_POINT_GROUP, {}) if isinstance(groups, dict) else {}
    if not isinstance(backends, dict):
        return []
    return sorted(str(name) for name in backends)


def expected_import_root(package_name: str) -> str:
    if package_name == "hla2010-spec":
        return "hla2010"
    return package_name.replace("-", "_")


def build_analysis_payload(graph_path: Path | None = None, packages_dir: Path | None = None) -> dict[str, object]:
    graph = load_package_graph(graph_path)
    manifests = load_package_manifests(packages_dir)
    internal_names = set(manifests)
    packages: dict[str, object] = {}
    for package_name in sorted(graph):
        manifest = manifests[package_name]
        graph_entry = graph[package_name]
        packages[package_name] = {
            "import_root": graph_entry["import_root"],
            "layer": graph_entry["layer"],
            "role": graph_entry["role"],
            "backend_names": sorted(str(name) for name in graph_entry.get("backend_names", [])),
            "may_depend_on": sorted(str(name) for name in graph_entry.get("may_depend_on", [])),
            "declared_internal_dependencies": internal_dependencies(manifest, internal_names),
            "declared_external_dependencies": external_dependencies(manifest, internal_names),
            "manifest_role": package_role(manifest),
            "manifest_status": package_status(manifest),
            "manifest_backend_names": package_backend_names(manifest),
            "source_roots": package_source_roots(manifest),
        }
    return {
        "source": str((graph_path or PACKAGE_GRAPH_PATH).relative_to(ROOT)),
        "package_count": len(packages),
        "packages": packages,
    }
