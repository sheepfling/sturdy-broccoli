from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from setuptools import find_packages


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"
SOURCE_ROOTS = (
    ROOT / "src",
    ROOT / "packages/hla2010-rti-python/src",
    ROOT / "packages/hla2010-rti-backend-common/src",
    ROOT / "packages/hla2010-rti-runtime-common/src",
    ROOT / "packages/hla2010-rti-transport-common/src",
)
INTERNAL_PACKAGE_SOURCE_ROOTS = {
    "hla2010-spec": ROOT / "src",
    "hla2010-rti-python": ROOT / "packages/hla2010-rti-python/src",
    "hla2010-rti-backend-common": ROOT / "packages/hla2010-rti-backend-common/src",
    "hla2010-rti-java-common": ROOT / "packages/hla2010-rti-java-common/src",
    "hla2010-rti-runtime-common": ROOT / "packages/hla2010-rti-runtime-common/src",
    "hla2010-rti-transport-common": ROOT / "packages/hla2010-rti-transport-common/src",
    "hla2010-rti-transport-rest": ROOT / "packages/hla2010-rti-transport-rest/src",
    "hla2010-rti-transport-grpc": ROOT / "packages/hla2010-rti-transport-grpc/src",
    "hla2010-rti-java-jpype": ROOT / "packages/hla2010-rti-java-jpype/src",
    "hla2010-rti-java-py4j": ROOT / "packages/hla2010-rti-java-py4j/src",
    "hla2010-rti-pitch-common": ROOT / "packages/hla2010-rti-pitch-common/src",
    "hla2010-rti-pitch-jpype": ROOT / "packages/hla2010-rti-pitch-jpype/src",
    "hla2010-rti-pitch-py4j": ROOT / "packages/hla2010-rti-pitch-py4j/src",
    "hla2010-rti-certi": ROOT / "packages/hla2010-rti-certi/src",
    "hla2010-rti-portico": ROOT / "packages/hla2010-rti-portico/src",
    "hla2010-verification-harness": ROOT / "packages/hla2010-verification-harness/src",
    "hla2010-fom-target-radar": ROOT / "packages/hla2010-fom-target-radar/src",
    "hla2010-fom-minimal-demo": ROOT / "packages/hla2010-fom-minimal-demo/src",
}
LIGHTWEIGHT_SPLIT_PACKAGE_IMPORT_SPECS = {
    "hla2010_rti_python": {
        "manifest_name": "hla2010-rti-python",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-python/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_backend_common": {
        "manifest_name": "hla2010-rti-backend-common",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_java_common": {
        "manifest_name": "hla2010-rti-java-common",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_runtime_common": {
        "manifest_name": "hla2010-rti-runtime-common",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_transport_common": {
        "manifest_name": "hla2010-rti-transport-common",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_transport_rest": {
        "manifest_name": "hla2010-rti-transport-rest",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-rti-transport-rest/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_transport_grpc": {
        "manifest_name": "hla2010-rti-transport-grpc",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-rti-transport-grpc/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_java_jpype": {
        "manifest_name": "hla2010-rti-java-jpype",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-jpype/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_java_py4j": {
        "manifest_name": "hla2010-rti-java-py4j",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-py4j/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_pitch_common": {
        "manifest_name": "hla2010-rti-pitch-common",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-rti-pitch-common/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_portico"),
    },
    "hla2010_verification_harness": {
        "manifest_name": "hla2010-verification-harness",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-verification-harness/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_fom_target_radar": {
        "manifest_name": "hla2010-fom-target-radar",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-verification-harness/src",
            ROOT / "packages/hla2010-fom-target-radar/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_fom_minimal_demo": {
        "manifest_name": "hla2010-fom-minimal-demo",
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-fom-minimal-demo/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
}
BACKEND_SPLIT_PACKAGE_IMPORT_SPECS = {
    "hla2010_rti_python": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-python/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_certi": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-rti-certi/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010_rti_pitch_jpype": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-jpype/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-rti-pitch-common/src",
            ROOT / "packages/hla2010-rti-pitch-jpype/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_portico", "hla2010_rti_pitch_py4j"),
    },
    "hla2010_rti_pitch_py4j": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-py4j/src",
            ROOT / "packages/hla2010-rti-transport-common/src",
            ROOT / "packages/hla2010-rti-runtime-common/src",
            ROOT / "packages/hla2010-rti-pitch-common/src",
            ROOT / "packages/hla2010-rti-pitch-py4j/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_portico", "hla2010_rti_pitch_jpype"),
    },
    "hla2010_rti_portico": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-jpype/src",
            ROOT / "packages/hla2010-rti-java-py4j/src",
            ROOT / "packages/hla2010-rti-portico/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_"),
    },
}
BACKEND_IMPORT_SPEC_BY_MANIFEST = {
    "hla2010-rti-python": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla2010_rti_python"],
    "hla2010-rti-certi": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla2010_rti_certi"],
    "hla2010-rti-java-jpype": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-jpype/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010-rti-java-py4j": {
        "source_roots": (
            ROOT / "src",
            ROOT / "packages/hla2010-rti-backend-common/src",
            ROOT / "packages/hla2010-rti-java-common/src",
            ROOT / "packages/hla2010-rti-java-py4j/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_certi", "hla2010_rti_pitch_", "hla2010_rti_portico"),
    },
    "hla2010-rti-pitch-jpype": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla2010_rti_pitch_jpype"],
    "hla2010-rti-pitch-py4j": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla2010_rti_pitch_py4j"],
    "hla2010-rti-portico": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla2010_rti_portico"],
}
INTERNAL_IMPORT_ROOT_TO_PACKAGE = {
    "hla2010_rti_python": "hla2010-rti-python",
    "hla2010_rti_certi": "hla2010-rti-certi",
    "hla2010_rti_backend_common": "hla2010-rti-backend-common",
    "hla2010_rti_java_common": "hla2010-rti-java-common",
    "hla2010_rti_runtime_common": "hla2010-rti-runtime-common",
    "hla2010_rti_transport_common": "hla2010-rti-transport-common",
    "hla2010_rti_transport_grpc": "hla2010-rti-transport-grpc",
    "hla2010_rti_transport_rest": "hla2010-rti-transport-rest",
    "hla2010_rti_java_jpype": "hla2010-rti-java-jpype",
    "hla2010_rti_java_py4j": "hla2010-rti-java-py4j",
    "hla2010_rti_pitch_common": "hla2010-rti-pitch-common",
    "hla2010_rti_pitch_jpype": "hla2010-rti-pitch-jpype",
    "hla2010_rti_pitch_py4j": "hla2010-rti-pitch-py4j",
    "hla2010_rti_portico": "hla2010-rti-portico",
    "hla2010_verification_harness": "hla2010-verification-harness",
    "hla2010_fom_target_radar": "hla2010-fom-target-radar",
    "hla2010_fom_minimal_demo": "hla2010-fom-minimal-demo",
}


def test_installable_package_excludes_repo_internal_testing_helpers():
    packages = set(
        find_packages(
            where="src",
            include=["hla2010*"],
            exclude=["hla2010.testing*"],
        )
    )
    assert "hla2010" in packages
    assert "hla2010.backends" not in packages
    assert "hla2010.testing" not in packages


def _load_project(package_name: str) -> dict:
    return tomllib.loads((PACKAGES / package_name / "pyproject.toml").read_text(encoding="utf-8"))


def _package_import_roots(package_name: str) -> set[str]:
    source_roots = _load_project(package_name)["tool"]["hla2010"]["package-split"]["source_roots"]
    import_roots: set[str] = set()
    prefix = f"packages/{package_name}/src/"
    for source_root in source_roots:
        assert source_root.startswith(prefix), (package_name, source_root)
        relative = source_root.removeprefix(prefix)
        import_roots.add(relative.split("/", 1)[0])
    return import_roots


def _dependency_name(requirement: str) -> str:
    match = re.match(r"[A-Za-z0-9_.-]+", requirement)
    assert match, requirement
    return match.group(0)


def _declared_dependency_names(package_name: str) -> set[str]:
    project = _load_project(package_name)["project"]
    return {_dependency_name(requirement) for requirement in project.get("dependencies", [])}


def _owned_import_roots(package_name: str) -> set[str]:
    return set(_package_import_roots(package_name))


def _direct_internal_imported_packages(package_name: str) -> set[str]:
    imported_packages: set[str] = set()
    owned_roots = _owned_import_roots(package_name)
    package_src = PACKAGES / package_name / "src"
    for path in sorted(package_src.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        for node in ast.walk(tree):
            module_name: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in INTERNAL_IMPORT_ROOT_TO_PACKAGE and root not in owned_roots:
                        imported_packages.add(INTERNAL_IMPORT_ROOT_TO_PACKAGE[root])
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
                root = module_name.split(".", 1)[0]
                if root in INTERNAL_IMPORT_ROOT_TO_PACKAGE and root not in owned_roots:
                    imported_packages.add(INTERNAL_IMPORT_ROOT_TO_PACKAGE[root])
    return imported_packages


def _declared_internal_dependency_closure(package_name: str) -> tuple[Path, ...]:
    seen: set[str] = set()
    ordered_packages: list[str] = []

    def visit(current: str) -> None:
        if current in seen:
            return
        seen.add(current)
        if current == "hla2010-spec":
            ordered_packages.append(current)
            return
        project = _load_project(current)["project"]
        for requirement in project.get("dependencies", []):
            dependency_name = _dependency_name(requirement)
            if dependency_name in INTERNAL_PACKAGE_SOURCE_ROOTS:
                visit(dependency_name)
        ordered_packages.append(current)

    visit(package_name)
    ordered_paths = [INTERNAL_PACKAGE_SOURCE_ROOTS[name] for name in ordered_packages]
    ordered_without_spec = [path for path in ordered_paths if path != ROOT / "src"]
    return (ROOT / "src", *ordered_without_spec)


def test_non_spec_split_package_manifests_publish_only_their_owned_namespace() -> None:
    expected_roots = {
        "hla2010-rti-python": "hla2010_rti_python",
        "hla2010-rti-certi": "hla2010_rti_certi",
        "hla2010-rti-backend-common": "hla2010_rti_backend_common",
        "hla2010-rti-java-common": "hla2010_rti_java_common",
        "hla2010-rti-runtime-common": "hla2010_rti_runtime_common",
        "hla2010-rti-java-jpype": "hla2010_rti_java_jpype",
        "hla2010-rti-java-py4j": "hla2010_rti_java_py4j",
        "hla2010-rti-pitch-common": "hla2010_rti_pitch_common",
        "hla2010-rti-pitch-jpype": "hla2010_rti_pitch_jpype",
        "hla2010-rti-pitch-py4j": "hla2010_rti_pitch_py4j",
        "hla2010-rti-portico": "hla2010_rti_portico",
        "hla2010-rti-transport-common": "hla2010_rti_transport_common",
        "hla2010-rti-transport-grpc": "hla2010_rti_transport_grpc",
        "hla2010-rti-transport-rest": "hla2010_rti_transport_rest",
        "hla2010-fom-target-radar": "hla2010_fom_target_radar",
        "hla2010-fom-minimal-demo": "hla2010_fom_minimal_demo",
        "hla2010-verification-harness": "hla2010_verification_harness",
    }

    for package_name, import_root in expected_roots.items():
        include_patterns = _load_project(package_name)["tool"]["setuptools"]["packages"]["find"]["include"]
        assert include_patterns == [f"{import_root}*"], package_name
        assert all(not pattern.startswith("hla2010*") for pattern in include_patterns), package_name


def test_split_package_python_namespaces_do_not_overlap() -> None:
    package_roots = {
        "hla2010-rti-python": ("packages/hla2010-rti-python/src", "hla2010_rti_python*"),
        "hla2010-rti-certi": ("packages/hla2010-rti-certi/src", "hla2010_rti_certi*"),
        "hla2010-rti-backend-common": ("packages/hla2010-rti-backend-common/src", "hla2010_rti_backend_common*"),
        "hla2010-rti-java-common": ("packages/hla2010-rti-java-common/src", "hla2010_rti_java_common*"),
        "hla2010-rti-runtime-common": ("packages/hla2010-rti-runtime-common/src", "hla2010_rti_runtime_common*"),
        "hla2010-rti-java-jpype": ("packages/hla2010-rti-java-jpype/src", "hla2010_rti_java_jpype*"),
        "hla2010-rti-java-py4j": ("packages/hla2010-rti-java-py4j/src", "hla2010_rti_java_py4j*"),
        "hla2010-rti-pitch-common": ("packages/hla2010-rti-pitch-common/src", "hla2010_rti_pitch_common*"),
        "hla2010-rti-pitch-jpype": ("packages/hla2010-rti-pitch-jpype/src", "hla2010_rti_pitch_jpype*"),
        "hla2010-rti-pitch-py4j": ("packages/hla2010-rti-pitch-py4j/src", "hla2010_rti_pitch_py4j*"),
        "hla2010-rti-portico": ("packages/hla2010-rti-portico/src", "hla2010_rti_portico*"),
        "hla2010-rti-transport-common": ("packages/hla2010-rti-transport-common/src", "hla2010_rti_transport_common*"),
        "hla2010-rti-transport-grpc": ("packages/hla2010-rti-transport-grpc/src", "hla2010_rti_transport_grpc*"),
        "hla2010-rti-transport-rest": ("packages/hla2010-rti-transport-rest/src", "hla2010_rti_transport_rest*"),
        "hla2010-fom-target-radar": ("packages/hla2010-fom-target-radar/src", "hla2010_fom_target_radar*"),
        "hla2010-fom-minimal-demo": ("packages/hla2010-fom-minimal-demo/src", "hla2010_fom_minimal_demo*"),
        "hla2010-verification-harness": ("packages/hla2010-verification-harness/src", "hla2010_verification_harness*"),
    }

    discovered: dict[str, set[str]] = {
        package_name: set(find_packages(where=where, include=[include]))
        for package_name, (where, include) in package_roots.items()
    }

    for package_name, packages in discovered.items():
        assert packages, package_name
        assert all(not name.startswith("hla2010.") for name in packages), package_name

    names = list(discovered.items())
    for index, (left_name, left_packages) in enumerate(names):
        for right_name, right_packages in names[index + 1 :]:
            overlap = left_packages & right_packages
            assert not overlap, (left_name, right_name, sorted(overlap))


def test_split_package_manifests_declare_direct_internal_import_dependencies() -> None:
    package_names = sorted(
        package_name
        for package_name in INTERNAL_PACKAGE_SOURCE_ROOTS
        if package_name != "hla2010-spec"
    )
    for package_name in package_names:
        imported_packages = _direct_internal_imported_packages(package_name)
        declared_dependencies = _declared_dependency_names(package_name)
        missing = sorted(imported_packages - declared_dependencies)
        assert not missing, (package_name, missing)


def test_lightweight_split_package_import_specs_match_declared_internal_dependency_closure() -> None:
    for package_name, spec in LIGHTWEIGHT_SPLIT_PACKAGE_IMPORT_SPECS.items():
        expected = _declared_internal_dependency_closure(spec["manifest_name"])
        assert spec["source_roots"] == expected, package_name


def test_backend_import_specs_match_declared_internal_dependency_closure() -> None:
    manifest_by_module = {
        "hla2010_rti_python": "hla2010-rti-python",
        "hla2010_rti_certi": "hla2010-rti-certi",
        "hla2010_rti_pitch_jpype": "hla2010-rti-pitch-jpype",
        "hla2010_rti_pitch_py4j": "hla2010-rti-pitch-py4j",
        "hla2010_rti_portico": "hla2010-rti-portico",
    }
    for package_name, spec in BACKEND_SPLIT_PACKAGE_IMPORT_SPECS.items():
        expected = _declared_internal_dependency_closure(manifest_by_module[package_name])
        assert spec["source_roots"] == expected, package_name


def test_backend_entrypoint_import_specs_match_declared_internal_dependency_closure() -> None:
    for manifest_name, spec in BACKEND_IMPORT_SPEC_BY_MANIFEST.items():
        expected = _declared_internal_dependency_closure(manifest_name)
        assert spec["source_roots"] == expected, manifest_name


def test_transitional_mega_package_includes_split_python_rti_package():
    python_packages = set(find_packages(where="packages/hla2010-rti-python/src", include=["hla2010_rti_python*"]))
    certi_packages = set(find_packages(where="packages/hla2010-rti-certi/src", include=["hla2010_rti_certi*"]))
    backend_common_packages = set(find_packages(where="packages/hla2010-rti-backend-common/src", include=["hla2010_rti_backend_common*"]))
    java_common_packages = set(find_packages(where="packages/hla2010-rti-java-common/src", include=["hla2010_rti_java_common*"]))
    runtime_common_packages = set(find_packages(where="packages/hla2010-rti-runtime-common/src", include=["hla2010_rti_runtime_common*"]))
    java_jpype_packages = set(find_packages(where="packages/hla2010-rti-java-jpype/src", include=["hla2010_rti_java_jpype*"]))
    java_py4j_packages = set(find_packages(where="packages/hla2010-rti-java-py4j/src", include=["hla2010_rti_java_py4j*"]))
    pitch_common_packages = set(find_packages(where="packages/hla2010-rti-pitch-common/src", include=["hla2010_rti_pitch_common*"]))
    pitch_jpype_packages = set(find_packages(where="packages/hla2010-rti-pitch-jpype/src", include=["hla2010_rti_pitch_jpype*"]))
    pitch_py4j_packages = set(find_packages(where="packages/hla2010-rti-pitch-py4j/src", include=["hla2010_rti_pitch_py4j*"]))
    portico_packages = set(find_packages(where="packages/hla2010-rti-portico/src", include=["hla2010_rti_portico*"]))
    grpc_transport_packages = set(find_packages(where="packages/hla2010-rti-transport-grpc/src", include=["hla2010_rti_transport_grpc*"]))
    rest_transport_packages = set(find_packages(where="packages/hla2010-rti-transport-rest/src", include=["hla2010_rti_transport_rest*"]))
    target_radar_packages = set(find_packages(where="packages/hla2010-fom-target-radar/src", include=["hla2010_fom_target_radar*"]))
    minimal_demo_packages = set(find_packages(where="packages/hla2010-fom-minimal-demo/src", include=["hla2010_fom_minimal_demo*"]))
    verification_harness_packages = set(find_packages(where="packages/hla2010-verification-harness/src", include=["hla2010_verification_harness*"]))

    assert "hla2010_rti_python" in python_packages
    assert "hla2010_rti_certi" in certi_packages
    assert "hla2010_rti_certi.certi" in certi_packages
    assert "hla2010_rti_certi.certi_java" in certi_packages
    assert "hla2010_rti_backend_common" in backend_common_packages
    assert "hla2010_rti_java_common" in java_common_packages
    assert "hla2010_rti_runtime_common" in runtime_common_packages
    assert "hla2010_rti_java_jpype" in java_jpype_packages
    assert "hla2010_rti_java_py4j" in java_py4j_packages
    assert "hla2010_rti_pitch_common" in pitch_common_packages
    assert "hla2010_rti_pitch_jpype" in pitch_jpype_packages
    assert "hla2010_rti_pitch_py4j" in pitch_py4j_packages
    assert "hla2010_rti_portico" in portico_packages
    assert "hla2010_rti_transport_grpc" in grpc_transport_packages
    assert "hla2010_rti_transport_rest" in rest_transport_packages
    assert "hla2010_fom_target_radar" in target_radar_packages
    assert "hla2010_fom_target_radar.scenarios" in target_radar_packages
    assert "hla2010_fom_target_radar.testing" not in target_radar_packages
    assert "hla2010_fom_minimal_demo" in minimal_demo_packages
    assert "hla2010_fom_minimal_demo.scenarios" in minimal_demo_packages
    assert "hla2010_fom_minimal_demo.testing" not in minimal_demo_packages
    assert "hla2010_verification_harness" in verification_harness_packages


def test_core_and_python_backend_import_without_repo_root_on_pythonpath(tmp_path: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in SOURCE_ROOTS)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import hla2010; from hla2010 import rti; from hla2010_rti_python.plugin import plugin; rti.register_backend_plugin(plugin()); ambassador = rti.create_rti_ambassador('python'); print(hla2010.__version__, ambassador.backend_info.kind)",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "python/in-memory" in result.stdout


def test_top_level_hla2010_import_is_lightweight(tmp_path: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in SOURCE_ROOTS)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, sys; import hla2010; print(json.dumps(sorted(name for name in sys.modules if name == 'hla2010.rti' or name.startswith(('hla2010_rti_', 'hla2010.backends')))))",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"


def test_shared_split_packages_import_cleanly_without_vendor_package_leakage(tmp_path: Path):
    for package_name, spec in LIGHTWEIGHT_SPLIT_PACKAGE_IMPORT_SPECS.items():
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(str(path) for path in spec["source_roots"])
        forbidden_prefixes = spec["forbidden_prefixes"]
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import json, sys; "
                    f"import {package_name}; "
                    "print(json.dumps({"
                    f"'module': {package_name}.__name__, "
                    "'root_rti_loaded': 'hla2010.rti' in sys.modules, "
                    "'vendor_modules': sorted("
                    "name for name in sys.modules "
                    f"if name.startswith({forbidden_prefixes!r})"
                    ")"
                    "}))"
                ),
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (package_name, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["module"] == package_name
        assert payload["root_rti_loaded"] is False, package_name
        assert payload["vendor_modules"] == [], package_name


def test_backend_split_packages_import_cleanly_without_unrelated_vendor_family_leakage(tmp_path: Path):
    for package_name, spec in BACKEND_SPLIT_PACKAGE_IMPORT_SPECS.items():
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(str(path) for path in spec["source_roots"])
        forbidden_prefixes = spec["forbidden_prefixes"]
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import json, sys; "
                    f"import {package_name}; "
                    "print(json.dumps({"
                    f"'module': {package_name}.__name__, "
                    "'root_rti_loaded': 'hla2010.rti' in sys.modules, "
                    "'forbidden_modules': sorted("
                    "name for name in sys.modules "
                    f"if name.startswith({forbidden_prefixes!r})"
                    ")"
                    "}))"
                ),
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (package_name, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["module"] == package_name
        assert payload["root_rti_loaded"] is False, package_name
        assert payload["forbidden_modules"] == [], package_name


def test_declared_backend_entrypoint_modules_import_under_declared_split_package_closure(tmp_path: Path):
    for manifest_name, spec in BACKEND_IMPORT_SPEC_BY_MANIFEST.items():
        manifest = _load_project(manifest_name)
        entry_points = manifest["project"]["entry-points"]["hla2010.rti_backends"]

        for backend_name, target in entry_points.items():
            module_name, symbol_name = target.split(":", 1)
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join(str(path) for path in spec["source_roots"])
            forbidden_prefixes = spec["forbidden_prefixes"]
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import importlib, json, sys; "
                        f"module = importlib.import_module({module_name!r}); "
                        f"symbol = getattr(module, {symbol_name!r}); "
                        "print(json.dumps({"
                        f"'backend_name': {backend_name!r}, "
                        f"'module': module.__name__, "
                        "'symbol_name': getattr(symbol, '__name__', None), "
                        "'root_rti_loaded': 'hla2010.rti' in sys.modules, "
                        "'forbidden_modules': sorted("
                        "name for name in sys.modules "
                        f"if name.startswith({forbidden_prefixes!r})"
                        ")"
                        "}))"
                    ),
                ],
                cwd=tmp_path,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, (manifest_name, backend_name, result.stderr)
            payload = json.loads(result.stdout)
            assert payload["backend_name"] == backend_name
            assert payload["module"] == module_name
            assert payload["symbol_name"] == symbol_name
            assert payload["root_rti_loaded"] is False, (manifest_name, backend_name)
            assert payload["forbidden_modules"] == [], (manifest_name, backend_name)


def test_backend_plugin_contract_import_does_not_import_rti_factory(tmp_path: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in SOURCE_ROOTS)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, sys; import hla2010_rti_python.plugin; print(json.dumps('hla2010.rti' in sys.modules))",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "false"


def test_core_transport_registry_does_not_import_certi_package_for_subprocess_line(tmp_path: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        (
            str(ROOT / "src"),
            str(ROOT / "packages/hla2010-rti-backend-common/src"),
            str(ROOT / "packages/hla2010-rti-transport-common/src"),
        )
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; "
                "from hla2010_rti_transport_common import coerce_transport_spec; "
                "transport = coerce_transport_spec({'kind': 'subprocess-line', 'command': ['/bin/echo']}); "
                "print(json.dumps({'transport_module': type(transport).__module__, "
                "'backend_modules': sorted(name for name in sys.modules if name.startswith('hla2010_rti_'))}))"
            ),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["transport_module"] == "hla2010_rti_transport_common.transport"
    assert "hla2010_rti_certi" not in payload["backend_modules"]
