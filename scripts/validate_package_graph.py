#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    import tomllib

    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_repo_internal.package_graph import (  # noqa: E402
    backend_entry_points,
    expected_import_root,
    internal_dependencies,
    load_package_graph,
    load_package_manifests,
    package_backend_names,
    package_role,
    package_source_roots,
)


def main() -> int:
    graph = load_package_graph()
    manifests = load_package_manifests()
    graph_packages = set(graph)
    manifest_packages = set(manifests)
    errors: list[str] = []

    missing_in_graph = sorted(manifest_packages - graph_packages)
    if missing_in_graph:
        errors.append(f"packages missing from package_graph.yaml: {', '.join(missing_in_graph)}")

    missing_on_disk = sorted(graph_packages - manifest_packages)
    if missing_on_disk:
        errors.append(f"package_graph.yaml entries missing pyproject.toml: {', '.join(missing_on_disk)}")

    internal_names = set(manifests)
    for package_name in sorted(graph_packages & manifest_packages):
        graph_entry = graph[package_name]
        manifest = manifests[package_name]
        expected_internal = sorted(str(name) for name in graph_entry.get("may_depend_on", []))
        actual_internal = internal_dependencies(manifest, internal_names)
        if actual_internal != expected_internal:
            errors.append(
                f"{package_name}: internal dependencies {actual_internal!r} do not match graph {expected_internal!r}"
            )

        graph_import_root = str(graph_entry["import_root"])
        if graph_import_root != expected_import_root(package_name):
            errors.append(
                f"{package_name}: import_root {graph_import_root!r} does not match expected root {expected_import_root(package_name)!r}"
            )

        source_roots = package_source_roots(manifest)
        if package_name == "hla2010-spec":
            if "src/hla2010" not in source_roots:
                errors.append(f"{package_name}: expected source root 'src/hla2010', found {source_roots!r}")
        else:
            expected_source_root = f"packages/{package_name}/src/{graph_import_root}"
            if expected_source_root not in source_roots:
                errors.append(f"{package_name}: expected source root {expected_source_root!r}, found {source_roots!r}")

        graph_layer = int(graph_entry["layer"])
        for dep_name in expected_internal:
            dep_layer = int(graph[dep_name]["layer"])
            if dep_layer >= graph_layer:
                errors.append(
                    f"{package_name}: dependency {dep_name} is in layer {dep_layer}, which is not lower than layer {graph_layer}"
                )

        manifest_role = package_role(manifest)
        graph_role = str(graph_entry["role"])
        if manifest_role != graph_role:
            errors.append(f"{package_name}: manifest role {manifest_role!r} does not match graph role {graph_role!r}")

        entry_points = backend_entry_points(manifest)
        manifest_backends = package_backend_names(manifest)
        graph_backends = sorted(str(name) for name in graph_entry.get("backend_names", []))
        if entry_points:
            if not graph_backends:
                errors.append(f"{package_name}: backend entry points exist but package graph has no backend_names")
            if entry_points != graph_backends:
                errors.append(f"{package_name}: entry points {entry_points!r} do not match graph backend_names {graph_backends!r}")
            if manifest_backends != graph_backends:
                errors.append(
                    f"{package_name}: manifest backend_names {manifest_backends!r} do not match graph backend_names {graph_backends!r}"
                )
        elif graph_backends:
            errors.append(f"{package_name}: graph backend_names present but no backend entry points declared")

        if graph_role == "transport":
            forbidden_roles = {"rti-backend", "java-bridge"}
            bad = [dep_name for dep_name in expected_internal if str(graph[dep_name]["role"]) in forbidden_roles]
            if bad:
                errors.append(f"{package_name}: transport packages must not depend on concrete backend packages: {bad!r}")

        if graph_role in {"fom-example", "verification-harness"}:
            forbidden_roles = {"rti-backend", "java-bridge"}
            bad = [dep_name for dep_name in expected_internal if str(graph[dep_name]["role"]) in forbidden_roles]
            if bad:
                errors.append(f"{package_name}: leaf packages must not depend on concrete backend packages: {bad!r}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated package graph for {len(graph)} packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
