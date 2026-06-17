from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"


@dataclass(frozen=True)
class PackageExpectation:
    role: str
    entry_points: frozenset[str]
    status: str

    def __getitem__(self, key: str):
        return getattr(self, key)

    def get(self, key: str, default=None):
        return getattr(self, key, default)


EXPECTED_PACKAGES = {
    "hla-rti1516e": PackageExpectation("core-spec", frozenset(), "implementation-owned"),
    "hla-rti1516-2025": PackageExpectation("core-spec", frozenset(), "implementation-owned"),
    "hla-backend-inmemory": PackageExpectation("rti-backend", frozenset({"inmemory"}), "implementation-moved"),
    "hla-backend-cpp-shim": PackageExpectation(
        "rti-backend",
        frozenset(
            {
                "cpp-shim-pybind",
                "cpp-shim-grpc",
                "cpp-standard-2010-pybind",
                "cpp-standard-2010-grpc",
                "cpp-standard-2025-pybind",
                "cpp-standard-2025-grpc",
                "cpp-2010-sdk-pybind",
                "cpp-2010-sdk-grpc",
                "cpp-2025-sdk-pybind",
                "cpp-2025-sdk-grpc",
            }
        ),
        "implementation-moved",
    ),
    "hla-backend-shim": PackageExpectation("rti-backend", frozenset({"shim"}), "implementation-owned"),
    "hla-backend-certi": PackageExpectation(
        "rti-backend",
        frozenset({"certi"}),
        "implementation-moved",
    ),
    "hla-backend-common": PackageExpectation("backend-support", frozenset(), "implementation-moved"),
    "hla-bridge-java-common": PackageExpectation("java-support", frozenset(), "implementation-moved"),
    "hla-rti-core": PackageExpectation("runtime-support", frozenset(), "implementation-moved"),
    "hla-transport-common": PackageExpectation("transport-support", frozenset(), "implementation-moved"),
    "hla-bridge-java-jpype": PackageExpectation("java-bridge", frozenset({"jpype"}), "implementation-moved"),
    "hla-bridge-java-py4j": PackageExpectation("java-bridge", frozenset({"py4j"}), "implementation-moved"),
    "hla-vendor-pitch": PackageExpectation("runtime-common", frozenset(), "implementation-moved"),
    "hla-vendor-pitch-jpype": PackageExpectation("rti-backend", frozenset({"pitch-jpype"}), "implementation-moved"),
    "hla-vendor-pitch-py4j": PackageExpectation("rti-backend", frozenset({"pitch-py4j"}), "implementation-moved"),
    "hla-vendor-portico": PackageExpectation(
        "rti-backend",
        frozenset({"portico-jpype", "portico-py4j"}),
        "implementation-moved",
    ),
    "hla-transport-grpc": PackageExpectation("transport", frozenset(), "implementation-moved"),
    "hla-transport-rest": PackageExpectation("transport", frozenset(), "implementation-moved"),
    "hla-fom-target-radar": PackageExpectation("fom-example", frozenset(), "implementation-moved"),
    "hla-fom-hlax-message-test": PackageExpectation("fom-example", frozenset(), "implementation-moved"),
    "hla-fom-hlax-space-lite": PackageExpectation("fom-example", frozenset(), "implementation-moved"),
    "hla-fom-hlax-time-mgmt-test": PackageExpectation("fom-example", frozenset(), "implementation-moved"),
    "hla-verification": PackageExpectation("verification-harness", frozenset(), "implementation-moved"),
}
INTERNAL_PACKAGE_VERSION = "0.13.0"
PACKAGE_PYTHON_REQUIRES = {
    "hla-rti1516-2025": ">=3.11",
    "hla-backend-shim": ">=3.11",
    "hla-backend-cpp-shim": ">=3.10",
}


def _load_project(package_name: str) -> dict:
    path = PACKAGES / package_name / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _package_split(package_name: str) -> dict:
    project = _load_project(package_name)
    tool = project.get("tool", {})
    if "hla2010" in tool and "package" in tool["hla2010"]:
        return tool["hla2010"]["package"]
    if "hla" in tool and "package" in tool["hla"]:
        return tool["hla"]["package"]
    raise KeyError(package_name)


def _package_import_roots(package_name: str) -> set[str]:
    source_roots = _package_split(package_name)["source_roots"]
    import_roots: set[str] = set()
    prefix = f"packages/{package_name}/src/"
    for source_root in source_roots:
        assert source_root.startswith(prefix), (package_name, source_root)
        relative = source_root.removeprefix(prefix)
        import_roots.add(relative.split("/", 1)[0])
    return import_roots


def _package_include_patterns(package_name: str) -> set[str]:
    source_roots = _package_split(package_name)["source_roots"]
    prefix = f"packages/{package_name}/src/"
    return {f"{'.'.join(source_root.removeprefix(prefix).split('/'))}*" for source_root in source_roots}


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
        if dep_name.startswith("hla-")
    }


def _live_rti1516e_python_files() -> set[str]:
    root = ROOT / "packages" / "hla-rti1516e" / "src" / "hla" / "rti1516e"
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    }


def _live_rti1516e_package_files() -> set[str]:
    root = ROOT / "packages" / "hla-rti1516e" / "src" / "hla" / "rti1516e"
    return {
        path.relative_to(root).as_posix()
        for path in root.iterdir()
        if path.is_file()
    }


def _live_rti1516_2025_package_files() -> set[str]:
    root = ROOT / "packages" / "hla-rti1516-2025" / "src" / "hla" / "rti1516_2025"
    return {
        path.relative_to(root).as_posix()
        for path in root.iterdir()
        if path.is_file()
    }


def test_package_split_scaffolds_are_declared():
    assert (PACKAGES / "README.md").exists()
    actual = {path.name for path in PACKAGES.iterdir() if path.is_dir()}
    assert EXPECTED_PACKAGES.keys() <= actual


def test_split_packages_use_package_owned_src_roots():
    for package_name, expected in EXPECTED_PACKAGES.items():
        split = _package_split(package_name)
        source_roots = split["source_roots"]
        assert source_roots
        if expected.get("status") == "implementation-moved":
            assert all(root.startswith(f"packages/{package_name}/src/") for root in source_roots)
        assert all("src/hla2010/testing/" not in root for root in source_roots)
        assert all("hla.foms.target_radar/testing/" not in root for root in source_roots)


def test_split_package_source_roots_resolve_to_real_package_owned_paths() -> None:
    for package_name in EXPECTED_PACKAGES:
        split = _package_split(package_name)
        source_roots = split["source_roots"]
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
                assert package_name == "hla-fom-target-radar", (package_name, source_root)
                assert path.suffix == ".xml", (package_name, source_root)


def test_split_package_source_roots_use_single_owned_directory_root() -> None:
    for package_name in EXPECTED_PACKAGES:
        split = _package_split(package_name)
        source_roots = split["source_roots"]
        assert len(source_roots) == 1, package_name
        source_root = source_roots[0]
        assert source_root.startswith(f"packages/{package_name}/src/"), package_name
        assert (ROOT / source_root).exists(), package_name


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
                if not dep_name.startswith("hla-"):
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


def test_no_split_package_manifest_depends_on_verification_harness_manifest() -> None:
    dependents = sorted(
        package_name
        for package_name in EXPECTED_PACKAGES
        if "hla-verification" in _declared_internal_dependency_names(package_name)
    )
    assert not dependents, dependents


def test_no_split_package_manifest_depends_on_target_radar_example_package() -> None:
    dependents = sorted(
        package_name
        for package_name in EXPECTED_PACKAGES
        if "hla-fom-target-radar" in _declared_internal_dependency_names(package_name)
    )
    assert dependents == ["hla-verification"]


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


def test_rti1516e_spec_manifest_owns_exact_root_package_tree() -> None:
    split = _package_split("hla-rti1516e")
    assert split["source_roots"] == ["packages/hla-rti1516e/src/hla/rti1516e"]

    package_dir = _load_project("hla-rti1516e")["tool"]["setuptools"]["package-dir"]
    assert package_dir == {"": "src"}

    package_find = _load_project("hla-rti1516e")["tool"]["setuptools"]["packages"]["find"]
    assert package_find["where"] == ["src"]
    assert package_find["include"] == ["hla.rti1516e*"]

    expected_root_surface = {
        "__init__.py",
        "_byte_wrapper.py",
        "ambassadors.py",
        "api.py",
        "datatypes.py",
        "encoding.py",
        "enums.py",
        "exceptions.py",
        "federate_ambassador.py",
        "fom.py",
        "handle_factory.py",
        "handles.py",
        "logical_time.py",
        "mom.py",
        "raw_api.py",
        "rti.py",
        "rti_ambassador.py",
        "spec_inventory.py",
        "spec_refs.py",
        "spec_sources.py",
        "factory.py",
        "plugin.py",
        "time.py",
    }
    assert _live_rti1516e_python_files() == expected_root_surface

    package_files = _live_rti1516e_package_files()
    assert "encoding.pyi" in package_files
    assert "federate_ambassador.pyi" in package_files
    assert "rti_ambassador.pyi" in package_files
    assert "py.typed" in package_files
    assert "api_metadata.json" in package_files

    package_data = _load_project("hla-rti1516e")["tool"]["setuptools"]["package-data"]["hla.rti1516e"]
    assert "*.json" in package_data
    assert "*.pyi" in package_data
    assert "py.typed" in package_data


def test_rti1516_2025_spec_manifest_packages_typed_surface() -> None:
    split = _package_split("hla-rti1516-2025")
    assert split["source_roots"] == ["packages/hla-rti1516-2025/src/hla/rti1516_2025"]

    project = _load_project("hla-rti1516-2025")
    package_dir = project["tool"]["setuptools"]["package-dir"]
    assert package_dir == {"": "src"}

    package_find = project["tool"]["setuptools"]["packages"]["find"]
    assert package_find["where"] == ["src"]
    assert package_find["include"] == ["hla.rti1516_2025*"]

    package_files = _live_rti1516_2025_package_files()
    assert "encoding.pyi" in package_files
    assert "federate_ambassador.pyi" in package_files
    assert "rti_ambassador.pyi" in package_files
    assert "py.typed" in package_files

    package_data = project["tool"]["setuptools"]["package-data"]["hla.rti1516_2025"]
    assert "*.pyi" in package_data
    assert "py.typed" in package_data


def test_backend_family_packages_own_docs_and_verification_policy_surfaces() -> None:
    expected_docs = {
        "hla-backend-inmemory": PACKAGES / "hla-backend-inmemory" / "docs" / "README.md",
        "hla-backend-certi": PACKAGES / "hla-backend-certi" / "docs" / "README.md",
        "hla-vendor-pitch": PACKAGES / "hla-vendor-pitch" / "docs" / "README.md",
        "hla-vendor-pitch-jpype": PACKAGES / "hla-vendor-pitch-jpype" / "docs" / "README.md",
        "hla-vendor-pitch-py4j": PACKAGES / "hla-vendor-pitch-py4j" / "docs" / "README.md",
        "hla-vendor-portico": PACKAGES / "hla-vendor-portico" / "docs" / "README.md",
    }
    expected_policy_modules = {
        "hla-backend-inmemory": PACKAGES / "hla-backend-inmemory" / "src" / "hla" / "backends" / "inmemory" / "testing_policy.py",
        "hla-backend-certi": PACKAGES / "hla-backend-certi" / "src" / "hla" / "backends" / "certi" / "testing_policy.py",
        "hla-vendor-pitch": PACKAGES / "hla-vendor-pitch" / "src" / "hla" / "vendors" / "pitch" / "testing_policy.py",
        "hla-vendor-portico": PACKAGES / "hla-vendor-portico" / "src" / "hla" / "vendors" / "portico" / "testing_policy.py",
    }

    for package_name, path in expected_docs.items():
        assert path.exists(), package_name

    for package_name, path in expected_policy_modules.items():
        assert path.exists(), package_name


def test_backend_doc_indexes_describe_owned_policy_and_operator_surfaces() -> None:
    required_fragments = {
        "hla-backend-inmemory": (
            "Package-owned notes",
            "testing_policy.py",
            "./tools/python verify",
            "thin wrappers",
            "tests/test_rti_python_split_package.py",
            "tests/test_python_matrix_policy.py",
        ),
        "hla-backend-certi": (
            "This package owns:",
            "testing_policy.py",
            "./tools/certi-easy",
            "plugin code",
            "tests/test_rti_certi_split_package.py",
            "tests/vendors/test_certi_real_backend_exchange_matrix.py",
            "tests/vendors/test_certi_real_backend_ownership_matrix.py",
            "tests/vendors/test_certi_real_backend_time_matrix.py",
        ),
        "hla-vendor-pitch": (
            "This package owns:",
            "testing_policy.py",
            "./tools/pitch",
            "runtime discovery and launch policy",
            "pitch_clause4_lost_federate_gap_2026-06-11.md",
            "tests/test_rti_pitch_split_packages.py",
            "tests/vendors/test_pitch_real_backend_matrix.py",
        ),
        "hla-vendor-pitch-jpype": (
            "src/hla.vendors.pitch.jpype/",
            "hla.vendors.pitch.testing_policy",
            "./tools/pitch",
            "plugin descriptor",
            "tests/test_rti_pitch_split_packages.py",
            "tests/vendors/test_pitch_real_backend_matrix.py",
        ),
        "hla-vendor-pitch-py4j": (
            "src/hla.vendors.pitch.py4j/",
            "hla.vendors.pitch.testing_policy",
            "./tools/pitch",
            "plugin descriptor",
            "tests/test_rti_pitch_split_packages.py",
            "tests/vendors/test_pitch_real_backend_matrix.py",
        ),
        "hla-vendor-portico": (
            "This package owns:",
            "testing_policy.py",
            "./tools/vendor-green",
            "runtime discovery and plugin code",
            "tests/test_rti_portico_split_package.py",
            "tests/vendors/test_portico_real_backend_matrix.py",
        ),
    }

    for package_name, fragments in required_fragments.items():
        text = (PACKAGES / package_name / "docs" / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_package_root_readmes_describe_canonical_import_and_operator_boundary() -> None:
    required_fragments = {
        "hla-rti1516e": (
            "canonical `hla.rti1516e` standard-facing API",
            "`hla.rti1516e.RTIambassador`",
            "`hla.rti1516e.rti` for version-local backend discovery and ambassador creation",
            "`tests/test_package_split_scaffolds.py`",
            "`tests/test_root_facade_policy.py`",
            "`tests/test_namespace_policy.py`",
            "`tests/test_python_api_spec.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-backend-inmemory": (
            "`src/hla.backends.inmemory/`",
            "`src/hla.backends.inmemory/testing_policy.py`",
            "`tests/test_rti_python_split_package.py`",
            "`tests/test_python_matrix_policy.py`",
            "`./tools/python`",
            "package-local command",
        ),
        "hla-backend-certi": (
            "`hla.backends.certi`",
            "`src/hla.backends.certi/testing_policy.py`",
            "`tests/test_rti_certi_split_package.py`",
            "`tests/vendors/test_certi_real_backend_exchange_matrix.py`",
            "`tests/vendors/test_certi_real_backend_ownership_matrix.py`",
            "`tests/vendors/test_certi_real_backend_time_matrix.py`",
            "`./tools/certi-easy`",
            "package-local command",
        ),
        "hla-backend-common": (
            "`hla.backends.common`",
            "`tests/test_rti_backend_common_split_package.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-bridge-java-common": (
            "`hla.bridges.java.common`",
            "`tests/test_rti_java_common_split_package.py`",
            "`tests/test_rti_java_runtime_split_package.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-rti-core": (
            "`hla.rti`",
            "`tests/test_rti_runtime_common_split_package.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-transport-common": (
            "`hla.transports.common`",
            "`tests/test_rti_transport_common_split_package.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-bridge-java-jpype": (
            "`hla.bridges.java.jpype`",
            "`tests/test_rti_java_plugin_split_packages.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-bridge-java-py4j": (
            "`hla.bridges.java.py4j`",
            "`tests/test_rti_java_plugin_split_packages.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-vendor-pitch": (
            "`hla.vendors.pitch`",
            "`src/hla.vendors.pitch/testing_policy.py`",
            "`tests/test_rti_pitch_split_packages.py`",
            "`tests/vendors/test_pitch_real_backend_matrix.py`",
            "`./tools/pitch`",
            "package-local command",
        ),
        "hla-vendor-pitch-jpype": (
            "`hla.vendors.pitch.jpype`",
            "`hla.vendors.pitch.testing_policy`",
            "`tests/test_rti_pitch_split_packages.py`",
            "`tests/vendors/test_pitch_real_backend_matrix.py`",
            "`./tools/pitch`",
            "package-local command",
        ),
        "hla-vendor-pitch-py4j": (
            "`hla.vendors.pitch.py4j`",
            "`hla.vendors.pitch.testing_policy`",
            "`tests/test_rti_pitch_split_packages.py`",
            "`tests/vendors/test_pitch_real_backend_matrix.py`",
            "`./tools/pitch`",
            "package-local command",
        ),
        "hla-vendor-portico": (
            "`hla.vendors.portico`",
            "`src/hla.vendors.portico/testing_policy.py`",
            "`tests/test_rti_portico_split_package.py`",
            "`tests/vendors/test_portico_real_backend_matrix.py`",
            "`./tools/vendor-green`",
            "package-local command",
        ),
        "hla-transport-grpc": (
            "`hla.transports.grpc.fedpro2010`",
            "`tests/test_rti_transport_grpc_split_package.py`",
            "`tests/test_package_boundary.py`",
            "`tests/test_backend_wrapper_policy.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-transport-rest": (
            "REST/HTTP JSON transport package",
            "`tests/test_rti_transport_rest_split_package.py`",
            "`tests/test_package_boundary.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
        "hla-fom-target-radar": (
            "`hla.foms.target_radar`",
            "`tests/test_fom_target_radar_split_package.py`",
            "`./tools/target-radar`",
            "does not expose a supported public Python import surface",
        ),
        "hla-fom-hlax-message-test": (
            "`hla.foms.hlax_message_test`",
            "`tests/test_fom_hlax_message_test_split_package.py`",
            "`./tools/hla-x demo fom-showcase`",
            "does not expose a supported public Python import surface",
        ),
        "hla-fom-hlax-space-lite": (
            "`hla.foms.hlax_space_lite`",
            "`tests/test_fom_hlax_space_lite_split_package.py`",
            "`./tools/hla-x demo fom-showcase`",
            "does not expose a supported public Python import surface",
        ),
        "hla-fom-hlax-time-mgmt-test": (
            "`hla.foms.hlax_time_mgmt_test`",
            "`tests/test_fom_hlax_time_mgmt_test_split_package.py`",
            "`./tools/hla-x demo fom-showcase`",
            "does not expose a supported public Python import surface",
        ),
        "hla-verification": (
            "`hla.verification`",
            "`tests/test_verification_harness_split_package.py`",
            "`tests/test_backend_wrapper_policy.py`",
            "does not own human operator entrypoints",
            "`./tools/`",
        ),
    }

    for package_name, fragments in required_fragments.items():
        text = (PACKAGES / package_name / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_transport_packages_own_explicit_docs_and_split_test_surfaces() -> None:
    expected_docs = {
        "hla-transport-common": PACKAGES / "hla-transport-common" / "docs" / "README.md",
        "hla-transport-grpc": PACKAGES / "hla-transport-grpc" / "docs" / "README.md",
        "hla-transport-rest": PACKAGES / "hla-transport-rest" / "docs" / "README.md",
    }
    expected_test_surfaces = {
        "hla-transport-common": {ROOT / "tests" / "test_rti_transport_common_split_package.py"},
        "hla-transport-grpc": {ROOT / "tests" / "test_rti_transport_grpc_split_package.py"},
        "hla-transport-rest": {ROOT / "tests" / "test_rti_transport_rest_split_package.py"},
    }

    for package_name, path in expected_docs.items():
        assert path.exists(), package_name

    for package_name, paths in expected_test_surfaces.items():
        for path in paths:
            assert path.exists(), (package_name, path.relative_to(ROOT).as_posix())


def test_transport_doc_indexes_describe_owned_code_and_operator_boundaries() -> None:
    required_fragments = {
        "hla-transport-common": (
            "This package owns backend-neutral transport primitives",
            "hla.transports.common.transport",
            "hla.transports.common.transport_registry",
            "not a backend, operator entrypoint",
            "tests/test_rti_transport_common_split_package.py",
            "tests/test_package_boundary.py",
        ),
        "hla-transport-grpc": (
            "installable gRPC transport implementation",
            "hla.transports.grpc.transport",
            "python_server",
            "Human operator entrypoints remain in `./tools/`",
            "tests/test_rti_transport_grpc_split_package.py",
            "tests/test_package_boundary.py",
            "tests/test_backend_wrapper_policy.py",
        ),
        "hla-transport-rest": (
            "installable REST/HTTP JSON transport implementation",
            "hla.transports.rest.client",
            "rest_transport_host",
            "Human operator entrypoints remain in `./tools/`",
            "tests/test_rti_transport_rest_split_package.py",
            "tests/test_package_boundary.py",
        ),
    }

    for package_name, fragments in required_fragments.items():
        text = (PACKAGES / package_name / "docs" / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_support_packages_own_explicit_docs_and_split_test_surfaces() -> None:
    expected_docs = {
        "hla-backend-common": PACKAGES / "hla-backend-common" / "docs" / "README.md",
        "hla-bridge-java-common": PACKAGES / "hla-bridge-java-common" / "docs" / "README.md",
        "hla-rti-core": PACKAGES / "hla-rti-core" / "docs" / "README.md",
    }
    expected_test_surfaces = {
        "hla-backend-common": {ROOT / "tests" / "test_rti_backend_common_split_package.py"},
        "hla-bridge-java-common": {
            ROOT / "tests" / "test_rti_java_common_split_package.py",
            ROOT / "tests" / "test_rti_java_runtime_split_package.py",
        },
        "hla-rti-core": {ROOT / "tests" / "test_rti_runtime_common_split_package.py"},
    }

    for package_name, path in expected_docs.items():
        assert path.exists(), package_name

    for package_name, paths in expected_test_surfaces.items():
        for path in paths:
            assert path.exists(), (package_name, path.relative_to(ROOT).as_posix())


def test_support_doc_indexes_describe_owned_code_and_no_operator_surface() -> None:
    required_fragments = {
        "hla-backend-common": (
            "backend-neutral support code",
            "hla.backends.common.plugin_api",
            "not itself a backend or operator entrypoint",
            "tests/test_rti_backend_common_split_package.py",
            "tests/test_package_boundary.py",
        ),
        "hla-bridge-java-common": (
            "bridge-independent Java support code",
            "hla.bridges.java.common.java_common",
            "not a vendor backend or operator",
            "tests/test_rti_java_common_split_package.py",
            "tests/test_rti_java_runtime_split_package.py",
            "tests/test_package_boundary.py",
        ),
        "hla-rti-core": (
            "shared vendor-runtime process and backend-discovery helpers",
            "hla.rti.factory",
            "not a backend implementation or operator",
            "tests/test_rti_runtime_common_split_package.py",
            "tests/test_package_boundary.py",
        ),
    }

    for package_name, fragments in required_fragments.items():
        text = (PACKAGES / package_name / "docs" / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_java_bridge_packages_own_explicit_docs_and_split_test_surfaces() -> None:
    expected_docs = {
        "hla-bridge-java-jpype": PACKAGES / "hla-bridge-java-jpype" / "docs" / "README.md",
        "hla-bridge-java-py4j": PACKAGES / "hla-bridge-java-py4j" / "docs" / "README.md",
    }
    expected_test_surfaces = {
        "hla-bridge-java-jpype": {ROOT / "tests" / "test_rti_java_plugin_split_packages.py"},
        "hla-bridge-java-py4j": {ROOT / "tests" / "test_rti_java_plugin_split_packages.py"},
    }

    for package_name, path in expected_docs.items():
        assert path.exists(), package_name

    for package_name, paths in expected_test_surfaces.items():
        for path in paths:
            assert path.exists(), (package_name, path.relative_to(ROOT).as_posix())


def test_java_bridge_doc_indexes_describe_owned_bridge_code_and_no_vendor_surface() -> None:
    required_fragments = {
        "hla-bridge-java-jpype": (
            "installable generic JPype Java bridge",
            "hla.bridges.java.jpype.runtime",
            "factory` and `.plugin",
            "not a vendor-specific RTI package or",
            "operator entrypoint",
            "tests/test_rti_java_plugin_split_packages.py",
            "tests/test_package_boundary.py",
        ),
        "hla-bridge-java-py4j": (
            "installable generic Py4J Java bridge",
            "hla.bridges.java.py4j.runtime",
            "factory` and `.plugin",
            "not a vendor-specific RTI package or",
            "operator entrypoint",
            "tests/test_rti_java_plugin_split_packages.py",
            "tests/test_package_boundary.py",
        ),
    }

    for package_name, fragments in required_fragments.items():
        text = (PACKAGES / package_name / "docs" / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_verification_and_fom_packages_own_explicit_docs_and_split_test_surfaces() -> None:
    expected_docs = {
        "hla-verification": PACKAGES / "hla-verification" / "docs" / "README.md",
        "hla-fom-target-radar": PACKAGES / "hla-fom-target-radar" / "docs" / "README.md",
        "hla-fom-hlax-message-test": PACKAGES / "hla-fom-hlax-message-test" / "docs" / "README.md",
        "hla-fom-hlax-space-lite": PACKAGES / "hla-fom-hlax-space-lite" / "docs" / "README.md",
        "hla-fom-hlax-time-mgmt-test": PACKAGES / "hla-fom-hlax-time-mgmt-test" / "docs" / "README.md",
    }
    expected_test_surfaces = {
        "hla-verification": {ROOT / "tests" / "test_verification_harness_split_package.py"},
        "hla-fom-target-radar": {ROOT / "tests" / "test_fom_target_radar_split_package.py"},
        "hla-fom-hlax-message-test": {ROOT / "tests" / "test_fom_hlax_message_test_split_package.py"},
        "hla-fom-hlax-space-lite": {ROOT / "tests" / "test_fom_hlax_space_lite_split_package.py"},
        "hla-fom-hlax-time-mgmt-test": {ROOT / "tests" / "test_fom_hlax_time_mgmt_test_split_package.py"},
    }

    for package_name, path in expected_docs.items():
        assert path.exists(), package_name

    for package_name, paths in expected_test_surfaces.items():
        for path in paths:
            assert path.exists(), (package_name, path.relative_to(ROOT).as_posix())


def test_verification_and_fom_doc_indexes_describe_owned_non_backend_surfaces() -> None:
    required_fragments = {
        "hla-verification": (
            "backend-neutral shared verification scenarios",
            "scenario_*",
            "backend wrapper tests and compliance artifacts",
            "does not own vendor runtime policy",
            "tests/test_verification_harness_split_package.py",
            "tests/test_backend_wrapper_policy.py",
        ),
        "hla-fom-target-radar": (
            "concrete Target/Radar example FOM",
            "resources.foms",
            "example/FOM support reused by repo-internal proof",
            "does not own RTI backend implementations",
            "tests/test_fom_target_radar_split_package.py",
        ),
        "hla-fom-hlax-message-test": (
            "MessageTest internal showcase runner",
            "repo-internal combined HLA-X showcase orchestration layer",
            "does not own RTI backend implementations",
            "tests/test_fom_hlax_message_test_split_package.py",
        ),
        "hla-fom-hlax-space-lite": (
            "SpaceLite internal showcase runner",
            "repo-internal combined HLA-X showcase orchestration layer",
            "does not own RTI backend implementations",
            "tests/test_fom_hlax_space_lite_split_package.py",
        ),
        "hla-fom-hlax-time-mgmt-test": (
            "TimeMgmtTest internal showcase runner",
            "repo-internal combined HLA-X showcase orchestration layer",
            "does not own RTI backend implementations",
            "tests/test_fom_hlax_time_mgmt_test_split_package.py",
        ),
    }

    for package_name, fragments in required_fragments.items():
        text = (PACKAGES / package_name / "docs" / "README.md").read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (package_name, fragment)


def test_core_spec_package_owns_explicit_docs_and_split_test_surfaces() -> None:
    expected_docs = {
        "hla-rti1516e": PACKAGES / "hla-rti1516e" / "docs" / "README.md",
    }
    expected_test_surfaces = {
        "hla-rti1516e": {
            ROOT / "tests" / "test_package_split_scaffolds.py",
            ROOT / "tests" / "test_root_facade_policy.py",
            ROOT / "tests" / "test_namespace_policy.py",
            ROOT / "tests" / "test_python_api_spec.py",
        },
    }

    for package_name, path in expected_docs.items():
        assert path.exists(), package_name

    for package_name, paths in expected_test_surfaces.items():
        for path in paths:
            assert path.exists(), (package_name, path.relative_to(ROOT).as_posix())


def test_core_spec_doc_index_describes_the_only_root_facade_boundary() -> None:
    text = (PACKAGES / "hla-rti1516e" / "docs" / "README.md").read_text(encoding="utf-8")

    assert "abstract HLA 2010 spec and core API surface" in text
    assert "`hla.rti1516e.rti`" in text
    assert "version-local backend-discovery and ambassador" in text
    assert "tests/test_package_split_scaffolds.py" in text
    assert "tests/test_root_facade_policy.py" in text
    assert "tests/test_namespace_policy.py" in text
    assert "tests/test_python_api_spec.py" in text
    assert "must not own concrete RTI backend implementations" in text


def test_backend_family_packages_have_explicit_split_package_test_surfaces() -> None:
    expected_test_surfaces = {
        "hla-backend-inmemory": {ROOT / "tests" / "test_rti_python_split_package.py"},
        "hla-backend-certi": {ROOT / "tests" / "test_rti_certi_split_package.py"},
        "hla-vendor-pitch": {ROOT / "tests" / "test_rti_pitch_common_split_package.py"},
        "hla-vendor-pitch-jpype": {ROOT / "tests" / "test_rti_pitch_split_packages.py"},
        "hla-vendor-pitch-py4j": {ROOT / "tests" / "test_rti_pitch_split_packages.py"},
        "hla-vendor-portico": {
            ROOT / "tests" / "test_rti_portico_split_package.py",
            ROOT / "tests" / "vendors" / "test_portico_real_backend_matrix.py",
        },
    }

    for package_name, paths in expected_test_surfaces.items():
        for path in paths:
            assert path.exists(), (package_name, path.relative_to(ROOT).as_posix())


def test_package_split_pyprojects_have_expected_boundaries():
    for package_name, expected in EXPECTED_PACKAGES.items():
        data = _load_project(package_name)
        project = data["project"]
        split = _package_split(package_name)

        assert project["name"] == package_name
        assert project["requires-python"] == PACKAGE_PYTHON_REQUIRES.get(package_name, ">=3.10")
        assert split["status"] == expected.get("status", "migration-scaffold")
        assert split["role"] == expected["role"]
        assert split["source_roots"]
        if split["status"] in {"transition-wrapper"}:
            assert (PACKAGES / package_name / "MIGRATION.md").exists()

        entry_points = data.get("project", {}).get("entry-points", {}).get("hla.rti_backends", {})
        assert set(entry_points) == expected["entry_points"]
        if package_name == "hla-backend-inmemory":
            assert entry_points["inmemory"] == "hla.backends.inmemory.plugin:plugin"
        if package_name == "hla-backend-certi":
            assert entry_points["certi"] == "hla.backends.certi.certi.plugin:plugin"
        if package_name == "hla-bridge-java-jpype":
            assert entry_points["jpype"] == "hla.bridges.java.jpype.plugin:plugin"
        if package_name == "hla-bridge-java-py4j":
            assert entry_points["py4j"] == "hla.bridges.java.py4j.plugin:plugin"
        if package_name == "hla-vendor-pitch-jpype":
            assert entry_points["pitch-jpype"] == "hla.vendors.pitch.jpype.plugin:plugin"
        if package_name == "hla-vendor-pitch-py4j":
            assert entry_points["pitch-py4j"] == "hla.vendors.pitch.py4j.plugin:plugin"
        if package_name == "hla-vendor-portico":
            assert entry_points["portico-jpype"] == "hla.vendors.portico.plugin:portico_jpype_plugin"
            assert entry_points["portico-py4j"] == "hla.vendors.portico.plugin:portico_py4j_plugin"


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
        data = _load_project(package_name)
        package_dir = data["tool"]["setuptools"]["package-dir"]
        package_find = data["tool"]["setuptools"]["packages"]["find"]
        expected_include_patterns = _package_include_patterns(package_name)

        assert package_dir == {"": "src"}, package_name
        assert package_find["where"] == ["src"], package_name
        assert set(package_find["include"]) == expected_include_patterns, package_name


def test_backend_scaffolds_depend_on_their_edition_spec_package():
    for package_name, expected in EXPECTED_PACKAGES.items():
        if expected["role"] in {"core-spec", "runtime-support"}:
            continue
        dependencies = set(_load_project(package_name)["project"].get("dependencies", ()))
        if package_name == "hla-backend-shim":
            assert "hla-rti1516-2025==0.13.0" in dependencies
            assert "hla-rti1516e==0.13.0" not in dependencies
            continue
        assert "hla-rti1516e==0.13.0" in dependencies


def test_pitch_backend_packages_depend_on_common_runtime_package():
    common_dependencies = set(_load_project("hla-vendor-pitch")["project"].get("dependencies", ()))
    assert "hla-vendor-pitch-jpype==0.13.0" not in common_dependencies
    assert "hla-vendor-pitch-py4j==0.13.0" not in common_dependencies

    for package_name in ("hla-vendor-pitch-jpype", "hla-vendor-pitch-py4j"):
        dependencies = set(_load_project(package_name)["project"].get("dependencies", ()))
        assert "hla-vendor-pitch==0.13.0" in dependencies


def test_vendor_java_backend_packages_depend_on_generic_bridge_packages():
    backend_common_dependencies = set(_load_project("hla-backend-common")["project"].get("dependencies", ()))
    assert "jpype1" not in backend_common_dependencies
    assert "py4j" not in backend_common_dependencies

    java_common_dependencies = set(_load_project("hla-bridge-java-common")["project"].get("dependencies", ()))
    assert "jpype1" not in java_common_dependencies
    assert "py4j" not in java_common_dependencies
    assert "hla-backend-common==0.13.0" in java_common_dependencies

    java_jpype_dependencies = set(_load_project("hla-bridge-java-jpype")["project"].get("dependencies", ()))
    java_py4j_dependencies = set(_load_project("hla-bridge-java-py4j")["project"].get("dependencies", ()))

    assert "jpype1" in java_jpype_dependencies
    assert "py4j" in java_py4j_dependencies
    assert "hla-bridge-java-common==0.13.0" in java_jpype_dependencies
    assert "hla-bridge-java-common==0.13.0" in java_py4j_dependencies

    pitch_jpype_dependencies = set(_load_project("hla-vendor-pitch-jpype")["project"].get("dependencies", ()))
    pitch_py4j_dependencies = set(_load_project("hla-vendor-pitch-py4j")["project"].get("dependencies", ()))
    portico_dependencies = set(_load_project("hla-vendor-portico")["project"].get("dependencies", ()))
    python_dependencies = set(_load_project("hla-backend-inmemory")["project"].get("dependencies", ()))
    certi_dependencies = set(_load_project("hla-backend-certi")["project"].get("dependencies", ()))

    assert "hla-bridge-java-jpype==0.13.0" in pitch_jpype_dependencies
    assert "hla-bridge-java-py4j==0.13.0" in pitch_py4j_dependencies
    assert "hla-bridge-java-jpype==0.13.0" in portico_dependencies
    assert "hla-bridge-java-py4j==0.13.0" in portico_dependencies
    assert "hla-backend-common==0.13.0" in python_dependencies
    assert "hla-bridge-java-common==0.13.0" not in python_dependencies
    assert "hla-backend-common==0.13.0" in certi_dependencies
    assert "hla-bridge-java-common==0.13.0" not in certi_dependencies
    assert "hla-transport-common==0.13.0" in certi_dependencies
    assert "jpype1" not in pitch_jpype_dependencies
    assert "py4j" not in pitch_py4j_dependencies


def test_vendor_runtime_packages_depend_on_runtime_common_package():
    runtime_common_dependencies = set(_load_project("hla-rti-core")["project"].get("dependencies", ()))
    assert "hla-bridge-java-common==0.13.0" not in runtime_common_dependencies

    certi_dependencies = set(_load_project("hla-backend-certi")["project"].get("dependencies", ()))
    pitch_common_dependencies = set(_load_project("hla-vendor-pitch")["project"].get("dependencies", ()))
    portico_dependencies = set(_load_project("hla-vendor-portico")["project"].get("dependencies", ()))

    assert "hla-rti-core==0.13.0" in certi_dependencies
    assert "hla-rti-core==0.13.0" in pitch_common_dependencies
    assert "hla-bridge-java-common==0.13.0" in pitch_common_dependencies
    assert "hla-bridge-java-common==0.13.0" in portico_dependencies


def test_transport_packages_depend_only_on_spec_and_transport_common():
    transport_common_dependencies = set(_load_project("hla-transport-common")["project"].get("dependencies", ()))
    grpc_dependencies = set(_load_project("hla-transport-grpc")["project"].get("dependencies", ()))
    rest_dependencies = set(_load_project("hla-transport-rest")["project"].get("dependencies", ()))

    assert transport_common_dependencies == {
        "hla-rti1516e==0.13.0",
        "hla-backend-common==0.13.0",
    }
    assert "hla-transport-common==0.13.0" in grpc_dependencies
    assert "hla-transport-common==0.13.0" in rest_dependencies
    assert "hla-backend-inmemory==0.13.0" not in grpc_dependencies
    assert "hla-backend-inmemory==0.13.0" not in rest_dependencies
    assert "hla-backend-certi==0.13.0" not in grpc_dependencies
    assert "hla-backend-certi==0.13.0" not in rest_dependencies


def test_leaf_packages_depend_only_on_spec_and_shared_runtime_support():
    target_radar_dependencies = set(_load_project("hla-fom-target-radar")["project"].get("dependencies", ()))
    assert target_radar_dependencies == {
        "hla-rti1516e==0.13.0",
        "hla-rti-core==0.13.0",
    }


def test_root_pyproject_declares_workspace_package_roots():
    root_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_roots = root_project["tool"]["pytest"]["ini_options"]["pythonpath"]
    expected_roots = {f"packages/{package_name}/src" for package_name in EXPECTED_PACKAGES}

    assert pytest_roots[0] == "packages/hla-rti1516e/src"
    assert set(pytest_roots) == expected_roots


def test_root_pyproject_stays_tooling_only_and_not_installable() -> None:
    root_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "project" not in root_project
    assert "build-system" not in root_project
    assert "tool" in root_project

    root_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "Root pyproject is intentionally tooling-only." in root_text
    assert "Installable distributions live" in root_text
