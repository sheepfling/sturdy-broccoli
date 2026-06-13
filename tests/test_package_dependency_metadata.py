from __future__ import annotations

from pathlib import Path

from hla2010_repo_internal.package_graph import internal_dependencies, load_package_graph, load_package_manifests


ROOT = Path(__file__).resolve().parents[1]


def test_package_dependency_metadata_matches_allowed_internal_graph() -> None:
    graph = load_package_graph(ROOT / "packages" / "package_graph.yaml")
    manifests = load_package_manifests(ROOT / "packages")
    internal_names = set(manifests)
    assert set(graph) == set(manifests)
    for package_name in sorted(graph):
        expected = sorted(str(name) for name in graph[package_name].get("may_depend_on", []))
        assert internal_dependencies(manifests[package_name], internal_names) == expected
