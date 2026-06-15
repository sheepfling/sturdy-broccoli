from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from conftest import REPO_ROOT, load_json_fixture

ROOT = REPO_ROOT
PACKAGES = ROOT / "packages"


@dataclass(frozen=True)
class PackageExpectation:
    role: str
    entry_points: frozenset[str]
    status: str


@dataclass(frozen=True)
class PackageSplitManifest:
    root_surface: frozenset[str]
    docs_exist: tuple[str, ...]
    policy_modules: dict[str, str]
    test_surfaces: dict[str, tuple[str, ...]]
    docs_readme_fragments: dict[str, tuple[str, ...]]
    package_readme_fragments: dict[str, tuple[str, ...]]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> PackageSplitManifest:
        return cls(
            root_surface=frozenset(str(item) for item in payload["root_surface"]),
            docs_exist=tuple(str(item) for item in payload["docs_exist"]),
            policy_modules={str(key): str(value) for key, value in payload["policy_modules"].items()},
            test_surfaces={
                str(key): tuple(str(item) for item in value)
                for key, value in payload["test_surfaces"].items()
            },
            docs_readme_fragments={
                str(key): tuple(str(item) for item in value)
                for key, value in payload["docs_readme_fragments"].items()
            },
            package_readme_fragments={
                str(key): tuple(str(item) for item in value)
                for key, value in payload["package_readme_fragments"].items()
            },
        )


EXPECTED_PACKAGES = {
    "hla2010-spec": PackageExpectation("core-spec", frozenset(), "implementation-owned"),
    "hla2010-rti-python": PackageExpectation("rti-backend", frozenset({"python"}), "implementation-moved"),
    "hla2010-rti-certi": PackageExpectation(
        "rti-backend",
        frozenset({"certi", "certi-jpype", "certi-py4j"}),
        "implementation-moved",
    ),
    "hla2010-rti-backend-common": PackageExpectation("backend-support", frozenset(), "implementation-moved"),
    "hla2010-rti-java-common": PackageExpectation("java-support", frozenset(), "implementation-moved"),
    "hla2010-rti-runtime-common": PackageExpectation("runtime-support", frozenset(), "implementation-moved"),
    "hla2010-rti-transport-common": PackageExpectation("transport-support", frozenset(), "implementation-moved"),
    "hla2010-rti-java-jpype": PackageExpectation("java-bridge", frozenset({"jpype"}), "implementation-moved"),
    "hla2010-rti-java-py4j": PackageExpectation("java-bridge", frozenset({"py4j"}), "implementation-moved"),
    "hla2010-rti-pitch-common": PackageExpectation("runtime-common", frozenset(), "implementation-moved"),
    "hla2010-rti-pitch-jpype": PackageExpectation("rti-backend", frozenset({"pitch-jpype"}), "implementation-moved"),
    "hla2010-rti-pitch-py4j": PackageExpectation("rti-backend", frozenset({"pitch-py4j"}), "implementation-moved"),
    "hla2010-rti-portico": PackageExpectation(
        "rti-backend",
        frozenset({"portico-jpype", "portico-py4j"}),
        "implementation-moved",
    ),
    "hla2010-rti-transport-grpc": PackageExpectation("transport", frozenset(), "implementation-moved"),
    "hla2010-rti-transport-rest": PackageExpectation("transport", frozenset(), "implementation-moved"),
    "hla2010-fom-target-radar": PackageExpectation("fom-example", frozenset(), "implementation-moved"),
    "hla2010-fom-minimal-demo": PackageExpectation("fom-example", frozenset(), "implementation-owned"),
    "hla2010-verification-harness": PackageExpectation("verification-harness", frozenset(), "implementation-moved"),
}
INTERNAL_PACKAGE_VERSION = "0.13.0"
PACKAGE_SPLIT_MANIFEST = PackageSplitManifest.from_mapping(
    load_json_fixture("package_split_scaffolds_manifest.json")
)


def _load_project(package_name: str) -> dict:
    path = PACKAGES / package_name / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _package_import_roots(package_name: str) -> set[str]:
    source_roots = _load_project(package_name)["tool"]["hla2010"]["package-split"]["source_roots"]
    import_roots: set[str] = set()
    prefix = f"packages/{package_name}/src/"
    for source_root in source_roots:
        assert source_root.startswith(prefix), (package_name, source_root)
        relative = source_root.removeprefix(prefix)
        import_roots.add(relative.split("/", 1)[0])
    return import_roots


def _requirement_name(requirement: str) -> str:
    match = re.match(r"[A-Za-z0-9_.-]+", requirement)
    assert match, requirement
    return match.group(0)


def _declared_internal_dependency_names(package_name: str) -> set[str]:
    project = _load_project(package_name).get("project", {})
    dependency_groups = {"dependencies": project.get("dependencies", [])}
    dependency_groups.update(project.get("optional-dependencies", {}))
    return {
        dep_name
        for requirements in dependency_groups.values()
        for requirement in requirements
        for dep_name in [_requirement_name(requirement)]
        if dep_name.startswith("hla2010-")
    }


def _live_root_python_files() -> set[str]:
    root = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010"
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    }


def test_package_split_scaffolds_are_declared():
    assert (PACKAGES / "README.md").exists()
    actual = {path.name for path in PACKAGES.iterdir() if path.is_dir()}
    assert EXPECTED_PACKAGES.keys() <= actual


def test_split_packages_use_package_owned_src_roots():
    for package_name, expected in EXPECTED_PACKAGES.items():
        split = _load_project(package_name)["tool"]["hla2010"]["package-split"]
        source_roots = split["source_roots"]
        assert source_roots
        if expected.status == "implementation-moved":
            assert all(root.startswith(f"packages/{package_name}/src/") for root in source_roots)
        assert all("src/hla2010/testing/" not in root for root in source_roots)
        assert all("hla2010_fom_target_radar/testing/" not in root for root in source_roots)


def test_split_package_source_roots_resolve_to_real_package_owned_paths() -> None:
    for package_name in EXPECTED_PACKAGES:
        split = _load_project(package_name)["tool"]["hla2010"]["package-split"]
        source_roots = split["source_roots"]
        if package_name == "hla2010-spec":
            assert source_roots == ["packages/hla2010-spec/src/hla2010"]
            assert (ROOT / "packages" / "hla2010-spec" / "src" / "hla2010").is_dir()
            continue

        expected_prefix = f"packages/{package_name}/src/"
        owned_roots = _package_import_roots(package_name)
        for source_root in source_roots:
            assert source_root.startswith(expected_prefix), (package_name, source_root)
            path = ROOT / source_root
            assert path.exists(), (package_name, source_root)
            relative = source_root.removeprefix(expected_prefix)
            assert any(
                relative == owned_root or relative.startswith(f"{owned_root}/")
                for owned_root in owned_roots
            ), (package_name, source_root)
            if path.is_dir():
                assert (path / "__init__.py").exists(), (package_name, source_root)
                continue
            assert path.is_file(), (package_name, source_root)
            if path.suffix == ".py":
                continue
            else:
                assert package_name == "hla2010-fom-target-radar", (package_name, source_root)
                assert path.suffix == ".xml", (package_name, source_root)


def test_split_package_source_roots_use_single_owned_directory_root() -> None:
    for package_name in EXPECTED_PACKAGES:
        split = _load_project(package_name)["tool"]["hla2010"]["package-split"]
        source_roots = split["source_roots"]
        assert len(source_roots) == 1, package_name
        source_root = source_roots[0]
        if package_name == "hla2010-spec":
            assert source_root == "packages/hla2010-spec/src/hla2010"
            continue
        expected_import_roots = _package_import_roots(package_name)
        assert len(expected_import_roots) == 1, package_name
        expected_import_root = next(iter(expected_import_roots))
        assert source_root == f"packages/{package_name}/src/{expected_import_root}", package_name


def test_internal_split_package_dependencies_resolve_to_repo_packages_and_exact_repo_version() -> None:
    known_packages = set(EXPECTED_PACKAGES)
    failures: list[str] = []
    for package_name in EXPECTED_PACKAGES:
        project = _load_project(package_name).get("project", {})
        dependency_groups = {"dependencies": project.get("dependencies", [])}
        dependency_groups.update(project.get("optional-dependencies", {}))
        for group_name, requirements in dependency_groups.items():
            for requirement in requirements:
                dep_name = _requirement_name(requirement)
                if not dep_name.startswith("hla2010-"):
                    continue
                if dep_name not in known_packages:
                    failures.append(f"{package_name}:{group_name}: unknown internal dependency {requirement!r}")
                    continue
                expected = f"{dep_name}=={INTERNAL_PACKAGE_VERSION}"
                if requirement != expected:
                    failures.append(
                        f"{package_name}:{group_name}: expected {expected!r} but found {requirement!r}"
                    )
    assert not failures, "\n".join(failures)


def test_internal_split_package_dependency_graph_is_acyclic() -> None:
    graph = {
        package_name: _declared_internal_dependency_names(package_name) & set(EXPECTED_PACKAGES)
        for package_name in EXPECTED_PACKAGES
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[str] = []

    def visit(package_name: str, trail: tuple[str, ...]) -> None:
        if package_name in visited:
            return
        if package_name in visiting:
            cycle_start = trail.index(package_name)
            cycles.append(" -> ".join((*trail[cycle_start:], package_name)))
            return
        visiting.add(package_name)
        for dependency in sorted(graph[package_name]):
            visit(dependency, (*trail, package_name))
        visiting.remove(package_name)
        visited.add(package_name)

    for package_name in sorted(graph):
        visit(package_name, ())

    assert not cycles, "\n".join(cycles)


def test_only_target_radar_package_depends_on_verification_harness_manifest() -> None:
    dependents = sorted(
        package_name
        for package_name in EXPECTED_PACKAGES
        if "hla2010-verification-harness" in _declared_internal_dependency_names(package_name)
    )
    assert dependents == ["hla2010-fom-target-radar"]


def test_no_split_package_manifest_depends_on_target_radar_example_package() -> None:
    dependents = sorted(
        package_name
        for package_name in EXPECTED_PACKAGES
        if "hla2010-fom-target-radar" in _declared_internal_dependency_names(package_name)
    )
    assert not dependents, dependents


def test_split_packages_do_not_publish_package_local_cli_entrypoints() -> None:
    failures: list[str] = []
    for package_name in EXPECTED_PACKAGES:
        project = _load_project(package_name).get("project", {})
        if project.get("scripts"):
            failures.append(f"{package_name}: unexpected [project.scripts] {sorted(project['scripts'])}")
        if project.get("gui-scripts"):
            failures.append(f"{package_name}: unexpected [project.gui-scripts] {sorted(project['gui-scripts'])}")
        entry_points = project.get("entry-points", {})
        forbidden_groups = {
            name: sorted(values)
            for name, values in entry_points.items()
            if name in {"console_scripts", "gui_scripts"}
        }
        if forbidden_groups:
            failures.append(f"{package_name}: unexpected entry-point groups {forbidden_groups}")
    assert not failures, "\n".join(failures)


def test_hla2010_spec_manifest_owns_exact_root_package_tree() -> None:
    split = _load_project("hla2010-spec")["tool"]["hla2010"]["package-split"]
    assert split["source_roots"] == ["packages/hla2010-spec/src/hla2010"]

    package_dir = _load_project("hla2010-spec")["tool"]["setuptools"]["package-dir"]
    assert package_dir == {"": "src"}

    package_find = _load_project("hla2010-spec")["tool"]["setuptools"]["packages"]["find"]
    assert package_find["where"] == ["src"]
    assert package_find["include"] == ["hla2010*"]
    assert "hla2010_repo_internal*" in package_find["exclude"]
    assert _live_root_python_files() == PACKAGE_SPLIT_MANIFEST.root_surface


def test_split_packages_own_declared_docs_test_surfaces_and_policy_modules() -> None:
    for package_name in PACKAGE_SPLIT_MANIFEST.docs_exist:
        path = PACKAGES / package_name / "docs" / "README.md"
        assert path.exists(), package_name

    for package_name, relative_path in PACKAGE_SPLIT_MANIFEST.policy_modules.items():
        assert (ROOT / relative_path).exists(), package_name

    for package_name, relative_paths in PACKAGE_SPLIT_MANIFEST.test_surfaces.items():
        for relative_path in relative_paths:
            path = ROOT / relative_path
            assert path.exists(), (package_name, relative_path)


def test_split_package_docs_readmes_describe_owned_surfaces() -> None:
    for package_name, fragments in PACKAGE_SPLIT_MANIFEST.docs_readme_fragments.items():
        text = (PACKAGES / package_name / "docs" / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_split_package_root_readmes_describe_import_and_operator_boundaries() -> None:
    for package_name, fragments in PACKAGE_SPLIT_MANIFEST.package_readme_fragments.items():
        text = (PACKAGES / package_name / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_package_split_pyprojects_have_expected_boundaries():
    for package_name, expected in EXPECTED_PACKAGES.items():
        data = _load_project(package_name)
        project = data["project"]
        split = data["tool"]["hla2010"]["package-split"]

        assert project["name"] == package_name
        assert project["requires-python"] == ">=3.10"
        assert split["status"] == expected.status
        assert split["role"] == expected.role
        assert split["source_roots"]
        if split["status"] in {"transition-wrapper", "implementation-moved"}:
            assert (PACKAGES / package_name / "MIGRATION.md").exists()

        entry_points = data.get("project", {}).get("entry-points", {}).get("hla2010.rti_backends", {})
        assert set(entry_points) == expected.entry_points
        if package_name == "hla2010-rti-python":
            assert entry_points["python"] == "hla2010_rti_python.plugin:plugin"
        if package_name == "hla2010-rti-certi":
            assert entry_points["certi"] == "hla2010_rti_certi.certi.plugin:plugin"
        if package_name == "hla2010-rti-java-jpype":
            assert entry_points["jpype"] == "hla2010_rti_java_jpype.plugin:plugin"
        if package_name == "hla2010-rti-java-py4j":
            assert entry_points["py4j"] == "hla2010_rti_java_py4j.plugin:plugin"
        if package_name == "hla2010-rti-pitch-jpype":
            assert entry_points["pitch-jpype"] == "hla2010_rti_pitch_jpype.plugin:plugin"
        if package_name == "hla2010-rti-pitch-py4j":
            assert entry_points["pitch-py4j"] == "hla2010_rti_pitch_py4j.plugin:plugin"
        if package_name == "hla2010-rti-portico":
            assert entry_points["portico-jpype"] == "hla2010_rti_portico.plugin:portico_jpype_plugin"
            assert entry_points["portico-py4j"] == "hla2010_rti_portico.plugin:portico_py4j_plugin"


def test_split_packages_publish_standalone_build_metadata() -> None:
    for package_name in EXPECTED_PACKAGES:
        data = _load_project(package_name)

        assert data["build-system"] == {
            "requires": ["setuptools>=68", "wheel"],
            "build-backend": "setuptools.build_meta",
        }, package_name

        project = data["project"]
        assert project["readme"] == "README.md", package_name
        assert (PACKAGES / package_name / "README.md").exists(), package_name
        assert set(project.get("optional-dependencies", {})).issuperset({"test"}), package_name
        assert project["optional-dependencies"]["test"] == ["pytest"], package_name


def test_non_spec_split_packages_build_from_their_own_src_roots() -> None:
    for package_name in EXPECTED_PACKAGES:
        if package_name == "hla2010-spec":
            continue

        data = _load_project(package_name)
        package_dir = data["tool"]["setuptools"]["package-dir"]
        package_find = data["tool"]["setuptools"]["packages"]["find"]
        expected_import_roots = _package_import_roots(package_name)

        assert package_dir == {"": "src"}, package_name
        assert package_find["where"] == ["src"], package_name
        assert set(package_find["include"]) == {f"{import_root}*" for import_root in expected_import_roots}, package_name


def test_backend_scaffolds_depend_on_core_spec_package():
    for package_name, expected in EXPECTED_PACKAGES.items():
        if expected.role == "core-spec":
            continue
        dependencies = set(_load_project(package_name)["project"].get("dependencies", ()))
        assert "hla2010-spec==0.13.0" in dependencies


def test_pitch_backend_packages_depend_on_common_runtime_package():
    common_dependencies = set(_load_project("hla2010-rti-pitch-common")["project"].get("dependencies", ()))
    assert "hla2010-rti-pitch-jpype==0.13.0" not in common_dependencies
    assert "hla2010-rti-pitch-py4j==0.13.0" not in common_dependencies

    for package_name in ("hla2010-rti-pitch-jpype", "hla2010-rti-pitch-py4j"):
        dependencies = set(_load_project(package_name)["project"].get("dependencies", ()))
        assert "hla2010-rti-pitch-common==0.13.0" in dependencies


def test_vendor_java_backend_packages_depend_on_generic_bridge_packages():
    backend_common_dependencies = set(_load_project("hla2010-rti-backend-common")["project"].get("dependencies", ()))
    assert "jpype1" not in backend_common_dependencies
    assert "py4j" not in backend_common_dependencies

    java_common_dependencies = set(_load_project("hla2010-rti-java-common")["project"].get("dependencies", ()))
    assert "jpype1" not in java_common_dependencies
    assert "py4j" not in java_common_dependencies
    assert "hla2010-rti-backend-common==0.13.0" in java_common_dependencies

    java_jpype_dependencies = set(_load_project("hla2010-rti-java-jpype")["project"].get("dependencies", ()))
    java_py4j_dependencies = set(_load_project("hla2010-rti-java-py4j")["project"].get("dependencies", ()))

    assert "jpype1" in java_jpype_dependencies
    assert "py4j" in java_py4j_dependencies
    assert "hla2010-rti-java-common==0.13.0" in java_jpype_dependencies
    assert "hla2010-rti-java-common==0.13.0" in java_py4j_dependencies

    pitch_jpype_dependencies = set(_load_project("hla2010-rti-pitch-jpype")["project"].get("dependencies", ()))
    pitch_py4j_dependencies = set(_load_project("hla2010-rti-pitch-py4j")["project"].get("dependencies", ()))
    portico_dependencies = set(_load_project("hla2010-rti-portico")["project"].get("dependencies", ()))
    python_dependencies = set(_load_project("hla2010-rti-python")["project"].get("dependencies", ()))
    certi_dependencies = set(_load_project("hla2010-rti-certi")["project"].get("dependencies", ()))

    assert "hla2010-rti-java-jpype==0.13.0" in pitch_jpype_dependencies
    assert "hla2010-rti-java-py4j==0.13.0" in pitch_py4j_dependencies
    assert "hla2010-rti-java-jpype==0.13.0" in portico_dependencies
    assert "hla2010-rti-java-py4j==0.13.0" in portico_dependencies
    assert "hla2010-rti-backend-common==0.13.0" in python_dependencies
    assert "hla2010-rti-java-common==0.13.0" not in python_dependencies
    assert "hla2010-rti-java-common==0.13.0" in certi_dependencies
    assert "hla2010-rti-transport-common==0.13.0" in certi_dependencies
    assert "jpype1" not in pitch_jpype_dependencies
    assert "py4j" not in pitch_py4j_dependencies


def test_vendor_runtime_packages_depend_on_runtime_common_package():
    runtime_common_dependencies = set(_load_project("hla2010-rti-runtime-common")["project"].get("dependencies", ()))
    assert "hla2010-rti-java-common==0.13.0" not in runtime_common_dependencies

    certi_dependencies = set(_load_project("hla2010-rti-certi")["project"].get("dependencies", ()))
    pitch_common_dependencies = set(_load_project("hla2010-rti-pitch-common")["project"].get("dependencies", ()))
    portico_dependencies = set(_load_project("hla2010-rti-portico")["project"].get("dependencies", ()))

    assert "hla2010-rti-runtime-common==0.13.0" in certi_dependencies
    assert "hla2010-rti-runtime-common==0.13.0" in pitch_common_dependencies
    assert "hla2010-rti-java-common==0.13.0" in pitch_common_dependencies
    assert "hla2010-rti-java-common==0.13.0" in portico_dependencies


def test_transport_packages_depend_only_on_spec_and_transport_common():
    transport_common_dependencies = set(_load_project("hla2010-rti-transport-common")["project"].get("dependencies", ()))
    grpc_dependencies = set(_load_project("hla2010-rti-transport-grpc")["project"].get("dependencies", ()))
    rest_dependencies = set(_load_project("hla2010-rti-transport-rest")["project"].get("dependencies", ()))

    assert transport_common_dependencies == {
        "hla2010-spec==0.13.0",
        "hla2010-rti-backend-common==0.13.0",
    }
    assert "hla2010-rti-transport-common==0.13.0" in grpc_dependencies
    assert "hla2010-rti-transport-common==0.13.0" in rest_dependencies
    assert "hla2010-rti-python==0.13.0" not in grpc_dependencies
    assert "hla2010-rti-python==0.13.0" not in rest_dependencies
    assert "hla2010-rti-certi==0.13.0" not in grpc_dependencies
    assert "hla2010-rti-certi==0.13.0" not in rest_dependencies


def test_leaf_packages_depend_only_on_spec_and_verification_harness():
    target_radar_dependencies = set(_load_project("hla2010-fom-target-radar")["project"].get("dependencies", ()))
    minimal_demo_dependencies = set(_load_project("hla2010-fom-minimal-demo")["project"].get("dependencies", ()))
    assert target_radar_dependencies == {
        "hla2010-spec==0.13.0",
        "hla2010-rti-runtime-common==0.13.0",
        "hla2010-verification-harness==0.13.0",
    }
    assert minimal_demo_dependencies == {
        "hla2010-spec==0.13.0",
        "hla2010-rti-runtime-common==0.13.0",
    }


def test_root_pyproject_declares_workspace_package_roots():
    root_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_roots = root_project["tool"]["pytest"]["ini_options"]["pythonpath"]
    expected_roots = {"src", "packages/hla2010-spec/src"} | {
        f"packages/{package_name}/src" for package_name in EXPECTED_PACKAGES if package_name != "hla2010-spec"
    }

    assert pytest_roots[0] == "src"
    assert set(pytest_roots) == expected_roots


def test_root_pyproject_stays_tooling_only_and_not_installable() -> None:
    root_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "project" not in root_project
    assert "build-system" not in root_project
    assert "tool" in root_project

    root_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "Root pyproject is intentionally tooling-only." in root_text
    assert "Installable distributions live" in root_text
