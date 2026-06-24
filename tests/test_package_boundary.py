from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from setuptools import find_namespace_packages as find_packages


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"
HLA_RTI1516E_SRC = ROOT / "packages/hla-rti1516e/src"
HLA_RTI_CORE_SRC = ROOT / "packages/hla-rti-core/src"
SOURCE_ROOTS = (
    HLA_RTI1516E_SRC,
    ROOT / "packages/hla-backend-inmemory/src",
    ROOT / "packages/hla-backend-common/src",
    HLA_RTI_CORE_SRC,
    ROOT / "packages/hla-transport-common/src",
)
INTERNAL_PACKAGE_SOURCE_ROOTS = {
    "hla-rti1516e": ROOT / "packages/hla-rti1516e/src",
    "hla-rti1516-2025": ROOT / "packages/hla-rti1516-2025/src",
    "hla-backend-inmemory": ROOT / "packages/hla-backend-inmemory/src",
    "hla-backend-common": ROOT / "packages/hla-backend-common/src",
    "hla-bridge-java-common": ROOT / "packages/hla-bridge-java-common/src",
    "hla-rti-core": ROOT / "packages/hla-rti-core/src",
    "hla-transport-common": ROOT / "packages/hla-transport-common/src",
    "hla-transport-rest": ROOT / "packages/hla-transport-rest/src",
    "hla-transport-grpc": ROOT / "packages/hla-transport-grpc/src",
    "hla-bridge-java-jpype": ROOT / "packages/hla-bridge-java-jpype/src",
    "hla-bridge-java-py4j": ROOT / "packages/hla-bridge-java-py4j/src",
    "hla-vendor-pitch": ROOT / "packages/hla-vendor-pitch/src",
    "hla-vendor-pitch-jpype": ROOT / "packages/hla-vendor-pitch-jpype/src",
    "hla-vendor-pitch-py4j": ROOT / "packages/hla-vendor-pitch-py4j/src",
    "hla-backend-certi": ROOT / "packages/hla-backend-certi/src",
    "hla-vendor-portico": ROOT / "packages/hla-vendor-portico/src",
    "hla-verification": ROOT / "packages/hla-verification/src",
    "hla-fom-target-radar": ROOT / "packages/hla-fom-target-radar/src",
    "hla-fom-proto2025-message-test": ROOT / "packages/hla-fom-proto2025-message-test/src",
    "hla-fom-proto2025-space-lite": ROOT / "packages/hla-fom-proto2025-space-lite/src",
    "hla-fom-proto2025-time-mgmt-test": ROOT / "packages/hla-fom-proto2025-time-mgmt-test/src",
}
LIGHTWEIGHT_SPLIT_PACKAGE_IMPORT_SPECS = {
    "hla.backends.inmemory": {
        "manifest_name": "hla-backend-inmemory",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-backend-inmemory/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.backends.common": {
        "manifest_name": "hla-backend-common",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.bridges.java.common": {
        "manifest_name": "hla-bridge-java-common",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.rti": {
        "manifest_name": "hla-rti-core",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.transports.common": {
        "manifest_name": "hla-transport-common",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-transport-common/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.transports.rest": {
        "manifest_name": "hla-transport-rest",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-transport-rest/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.transports.grpc": {
        "manifest_name": "hla-transport-grpc",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-transport-grpc/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.bridges.java.jpype": {
        "manifest_name": "hla-bridge-java-jpype",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-jpype/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.bridges.java.py4j": {
        "manifest_name": "hla-bridge-java-py4j",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-py4j/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.vendors.pitch": {
        "manifest_name": "hla-vendor-pitch",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-vendor-pitch/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla.vendors.portico"),
    },
    "hla.verification": {
        "manifest_name": "hla-verification",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-verification/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.foms.target_radar": {
        "manifest_name": "hla-fom-target-radar",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-verification/src",
            ROOT / "packages/hla-fom-target-radar/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.foms.proto2025_message_test": {
        "manifest_name": "hla-fom-proto2025-message-test",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-rti1516-2025/src",
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-backend-inmemory/src",
            ROOT / "packages/hla-fom-proto2025-message-test/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.foms.proto2025_space_lite": {
        "manifest_name": "hla-fom-proto2025-space-lite",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-rti1516-2025/src",
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-backend-inmemory/src",
            ROOT / "packages/hla-fom-proto2025-space-lite/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.foms.proto2025_time_mgmt_test": {
        "manifest_name": "hla-fom-proto2025-time-mgmt-test",
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-rti1516-2025/src",
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-backend-inmemory/src",
            ROOT / "packages/hla-fom-proto2025-time-mgmt-test/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
}
BACKEND_SPLIT_PACKAGE_IMPORT_SPECS = {
    "hla.backends.inmemory": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-backend-inmemory/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.backends.certi": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-backend-certi/src",
        ),
        "forbidden_prefixes": ("hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla.vendors.pitch.jpype": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-jpype/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-vendor-pitch/src",
            ROOT / "packages/hla-vendor-pitch-jpype/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla.vendors.portico", "hla.vendors.pitch.py4j"),
    },
    "hla.vendors.pitch.py4j": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-py4j/src",
            ROOT / "packages/hla-transport-common/src",
            ROOT / "packages/hla-rti-core/src",
            ROOT / "packages/hla-vendor-pitch/src",
            ROOT / "packages/hla-vendor-pitch-py4j/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla.vendors.portico", "hla.vendors.pitch.jpype"),
    },
    "hla.vendors.portico": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-jpype/src",
            ROOT / "packages/hla-bridge-java-py4j/src",
            ROOT / "packages/hla-vendor-portico/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_"),
    },
}
BACKEND_IMPORT_SPEC_BY_MANIFEST = {
    "hla-backend-inmemory": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla.backends.inmemory"],
    "hla-backend-certi": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla.backends.certi"],
    "hla-bridge-java-jpype": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-jpype/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla-bridge-java-py4j": {
        "source_roots": (
            HLA_RTI1516E_SRC,
            ROOT / "packages/hla-backend-common/src",
            ROOT / "packages/hla-bridge-java-common/src",
            ROOT / "packages/hla-bridge-java-py4j/src",
        ),
        "forbidden_prefixes": ("hla.backends.certi", "hla2010_rti_pitch_", "hla.vendors.portico"),
    },
    "hla-vendor-pitch-jpype": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla.vendors.pitch.jpype"],
    "hla-vendor-pitch-py4j": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla.vendors.pitch.py4j"],
    "hla-vendor-portico": BACKEND_SPLIT_PACKAGE_IMPORT_SPECS["hla.vendors.portico"],
}
INTERNAL_IMPORT_ROOT_TO_PACKAGE = {
    "hla.backends.inmemory": "hla-backend-inmemory",
    "hla.backends.certi": "hla-backend-certi",
    "hla.backends.common": "hla-backend-common",
    "hla.bridges.java.common": "hla-bridge-java-common",
    "hla.rti": "hla-rti-core",
    "hla.transports.common": "hla-transport-common",
    "hla.transports.grpc": "hla-transport-grpc",
    "hla.transports.rest": "hla-transport-rest",
    "hla.bridges.java.jpype": "hla-bridge-java-jpype",
    "hla.bridges.java.py4j": "hla-bridge-java-py4j",
    "hla.vendors.pitch": "hla-vendor-pitch",
    "hla.vendors.pitch.jpype": "hla-vendor-pitch-jpype",
    "hla.vendors.pitch.py4j": "hla-vendor-pitch-py4j",
    "hla.vendors.portico": "hla-vendor-portico",
    "hla.verification": "hla-verification",
    "hla.foms.target_radar": "hla-fom-target-radar",
    "hla.foms.proto2025_message_test": "hla-fom-proto2025-message-test",
    "hla.foms.proto2025_space_lite": "hla-fom-proto2025-space-lite",
    "hla.foms.proto2025_time_mgmt_test": "hla-fom-proto2025-time-mgmt-test",
}


def test_installable_package_excludes_repo_internal_testing_helpers():
    packages = set(
        find_packages(
            where="packages/hla-rti1516e/src",
            include=["hla.rti1516e*"],
            exclude=["hla.rti1516e.testing*"],
        )
    )
    assert "hla.rti1516e" in packages
    assert "hla.rti1516e.backends" not in packages
    assert "hla.rti1516e.testing" not in packages


def _load_project(package_name: str) -> dict:
    return tomllib.loads((PACKAGES / package_name / "pyproject.toml").read_text(encoding="utf-8"))


def _package_import_roots(package_name: str) -> set[str]:
    source_roots = _load_project(package_name)["tool"]["hla"]["package"]["source_roots"]
    import_roots: set[str] = set()
    prefix = f"packages/{package_name}/src/"
    for source_root in source_roots:
        assert source_root.startswith(prefix), (package_name, source_root)
        relative = source_root.removeprefix(prefix)
        import_roots.add(".".join(relative.split("/")))
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

    def owner_for(module_name: str) -> str | None:
        matches = [
            prefix
            for prefix in INTERNAL_IMPORT_ROOT_TO_PACKAGE
            if module_name == prefix or module_name.startswith(prefix + ".")
        ]
        if not matches:
            return None
        prefix = max(matches, key=len)
        if any(prefix == owned or prefix.startswith(owned + ".") or owned.startswith(prefix + ".") for owned in owned_roots):
            return None
        return INTERNAL_IMPORT_ROOT_TO_PACKAGE[prefix]

    for path in sorted(package_src.rglob("*.py")):
        if "repo_internal" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        for node in ast.walk(tree):
            module_name: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    owner = owner_for(alias.name)
                    if owner is not None:
                        imported_packages.add(owner)
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
                owner = owner_for(module_name)
                if owner is not None:
                    imported_packages.add(owner)
    return imported_packages


def _declared_internal_dependency_closure(package_name: str) -> tuple[Path, ...]:
    seen: set[str] = set()
    ordered_packages: list[str] = []

    def visit(current: str) -> None:
        if current in seen:
            return
        seen.add(current)
        if current == "hla-rti1516e":
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
    return tuple(ordered_paths)


def test_non_spec_split_package_manifests_publish_only_their_owned_namespace() -> None:
    expected_roots = {
        "hla-backend-inmemory": "hla.backends.inmemory",
        "hla-backend-certi": "hla.backends.certi",
        "hla-backend-common": "hla.backends.common",
        "hla-bridge-java-common": "hla.bridges.java.common",
        "hla-rti-core": ("hla.rti", "hla.runtime", "hla.fom", "hla.spec"),
        "hla-bridge-java-jpype": "hla.bridges.java.jpype",
        "hla-bridge-java-py4j": "hla.bridges.java.py4j",
        "hla-vendor-pitch": "hla.vendors.pitch",
        "hla-vendor-pitch-jpype": "hla.vendors.pitch.jpype",
        "hla-vendor-pitch-py4j": "hla.vendors.pitch.py4j",
        "hla-vendor-portico": "hla.vendors.portico",
        "hla-transport-common": "hla.transports.common",
        "hla-transport-grpc": "hla.transports.grpc",
        "hla-transport-rest": "hla.transports.rest",
        "hla-fom-target-radar": "hla.foms.target_radar",
        "hla-fom-proto2025-message-test": "hla.foms.proto2025_message_test",
        "hla-fom-proto2025-space-lite": "hla.foms.proto2025_space_lite",
        "hla-fom-proto2025-time-mgmt-test": "hla.foms.proto2025_time_mgmt_test",
        "hla-verification": "hla.verification",
    }

    for package_name, import_root in expected_roots.items():
        include_patterns = _load_project(package_name)["tool"]["setuptools"]["packages"]["find"]["include"]
        expected_patterns = [f"{root}*" for root in import_root] if isinstance(import_root, tuple) else [f"{import_root}*"]
        assert include_patterns == expected_patterns, package_name
        assert all(not pattern.startswith("hla2010*") for pattern in include_patterns), package_name


def test_split_package_python_namespaces_do_not_overlap() -> None:
    package_roots = {
        "hla-backend-inmemory": ("packages/hla-backend-inmemory/src", "hla.backends.inmemory*"),
        "hla-backend-certi": ("packages/hla-backend-certi/src", "hla.backends.certi*"),
        "hla-backend-common": ("packages/hla-backend-common/src", "hla.backends.common*"),
        "hla-bridge-java-common": ("packages/hla-bridge-java-common/src", "hla.bridges.java.common*"),
        "hla-rti-core": ("packages/hla-rti-core/src", ("hla.rti*", "hla.runtime*", "hla.fom*", "hla.spec*")),
        "hla-bridge-java-jpype": ("packages/hla-bridge-java-jpype/src", "hla.bridges.java.jpype*"),
        "hla-bridge-java-py4j": ("packages/hla-bridge-java-py4j/src", "hla.bridges.java.py4j*"),
        "hla-vendor-pitch": ("packages/hla-vendor-pitch/src", "hla.vendors.pitch*"),
        "hla-vendor-pitch-jpype": ("packages/hla-vendor-pitch-jpype/src", "hla.vendors.pitch.jpype*"),
        "hla-vendor-pitch-py4j": ("packages/hla-vendor-pitch-py4j/src", "hla.vendors.pitch.py4j*"),
        "hla-vendor-portico": ("packages/hla-vendor-portico/src", "hla.vendors.portico*"),
        "hla-transport-common": ("packages/hla-transport-common/src", "hla.transports.common*"),
        "hla-transport-grpc": ("packages/hla-transport-grpc/src", "hla.transports.grpc*"),
        "hla-transport-rest": ("packages/hla-transport-rest/src", "hla.transports.rest*"),
        "hla-fom-target-radar": ("packages/hla-fom-target-radar/src", "hla.foms.target_radar*"),
        "hla-fom-proto2025-message-test": ("packages/hla-fom-proto2025-message-test/src", "hla.foms.proto2025_message_test*"),
        "hla-fom-proto2025-space-lite": ("packages/hla-fom-proto2025-space-lite/src", "hla.foms.proto2025_space_lite*"),
        "hla-fom-proto2025-time-mgmt-test": ("packages/hla-fom-proto2025-time-mgmt-test/src", "hla.foms.proto2025_time_mgmt_test*"),
        "hla-verification": ("packages/hla-verification/src", "hla.verification*"),
    }

    discovered: dict[str, set[str]] = {
        package_name: set(find_packages(where=where, include=list(include) if isinstance(include, tuple) else [include]))
        for package_name, (where, include) in package_roots.items()
    }

    for package_name, packages in discovered.items():
        assert packages, package_name
        assert all(not name.startswith("hla.rti1516e.") for name in packages), package_name

    names = list(discovered.items())
    for index, (left_name, left_packages) in enumerate(names):
        for right_name, right_packages in names[index + 1 :]:
            overlap = left_packages & right_packages
            assert not overlap, (left_name, right_name, sorted(overlap))


def test_split_package_manifests_declare_direct_internal_import_dependencies() -> None:
    package_names = sorted(
        package_name
        for package_name in INTERNAL_PACKAGE_SOURCE_ROOTS
        if package_name != "hla-rti1516e"
    )
    for package_name in package_names:
        imported_packages = _direct_internal_imported_packages(package_name)
        declared_dependencies = _declared_dependency_names(package_name)
        missing = sorted(imported_packages - declared_dependencies)
        assert not missing, (package_name, missing)


def test_lightweight_split_package_import_specs_match_declared_internal_dependency_closure() -> None:
    for package_name, spec in LIGHTWEIGHT_SPLIT_PACKAGE_IMPORT_SPECS.items():
        expected = _declared_internal_dependency_closure(spec["manifest_name"])
        assert all(path.exists() for path in expected), package_name


def test_backend_import_specs_match_declared_internal_dependency_closure() -> None:
    manifest_by_module = {
        "hla.backends.inmemory": "hla-backend-inmemory",
        "hla.backends.certi": "hla-backend-certi",
        "hla.vendors.pitch.jpype": "hla-vendor-pitch-jpype",
        "hla.vendors.pitch.py4j": "hla-vendor-pitch-py4j",
        "hla.vendors.portico": "hla-vendor-portico",
    }
    for package_name, spec in BACKEND_SPLIT_PACKAGE_IMPORT_SPECS.items():
        expected = _declared_internal_dependency_closure(manifest_by_module[package_name])
        assert all(path.exists() for path in expected), package_name


def test_backend_entrypoint_import_specs_match_declared_internal_dependency_closure() -> None:
    for manifest_name, spec in BACKEND_IMPORT_SPEC_BY_MANIFEST.items():
        expected = _declared_internal_dependency_closure(manifest_name)
        assert all(path.exists() for path in expected), manifest_name


def test_transitional_mega_package_includes_split_python_rti_package():
    python_packages = set(find_packages(where="packages/hla-backend-inmemory/src", include=["hla.backends.inmemory*"]))
    certi_packages = set(find_packages(where="packages/hla-backend-certi/src", include=["hla.backends.certi*"]))
    backend_common_packages = set(find_packages(where="packages/hla-backend-common/src", include=["hla.backends.common*"]))
    java_common_packages = set(find_packages(where="packages/hla-bridge-java-common/src", include=["hla.bridges.java.common*"]))
    runtime_common_packages = set(find_packages(where="packages/hla-rti-core/src", include=["hla.rti*", "hla.runtime*", "hla.fom*", "hla.spec*"]))
    java_jpype_packages = set(find_packages(where="packages/hla-bridge-java-jpype/src", include=["hla.bridges.java.jpype*"]))
    java_py4j_packages = set(find_packages(where="packages/hla-bridge-java-py4j/src", include=["hla.bridges.java.py4j*"]))
    pitch_common_packages = set(find_packages(where="packages/hla-vendor-pitch/src", include=["hla.vendors.pitch*"]))
    pitch_jpype_packages = set(find_packages(where="packages/hla-vendor-pitch-jpype/src", include=["hla.vendors.pitch.jpype*"]))
    pitch_py4j_packages = set(find_packages(where="packages/hla-vendor-pitch-py4j/src", include=["hla.vendors.pitch.py4j*"]))
    portico_packages = set(find_packages(where="packages/hla-vendor-portico/src", include=["hla.vendors.portico*"]))
    grpc_transport_packages = set(find_packages(where="packages/hla-transport-grpc/src", include=["hla.transports.grpc*"]))
    rest_transport_packages = set(find_packages(where="packages/hla-transport-rest/src", include=["hla.transports.rest*"]))
    target_radar_packages = set(find_packages(where="packages/hla-fom-target-radar/src", include=["hla.foms.target_radar*"]))
    message_test_packages = set(find_packages(where="packages/hla-fom-proto2025-message-test/src", include=["hla.foms.proto2025_message_test*"]))
    space_lite_packages = set(find_packages(where="packages/hla-fom-proto2025-space-lite/src", include=["hla.foms.proto2025_space_lite*"]))
    time_mgmt_packages = set(find_packages(where="packages/hla-fom-proto2025-time-mgmt-test/src", include=["hla.foms.proto2025_time_mgmt_test*"]))
    verification_harness_packages = set(find_packages(where="packages/hla-verification/src", include=["hla.verification*"]))

    assert "hla.backends.inmemory" in python_packages
    assert "hla.backends.certi" in certi_packages
    assert "hla.backends.certi.certi" in certi_packages
    assert "hla.backends.common" in backend_common_packages
    assert "hla.bridges.java.common" in java_common_packages
    assert "hla.rti" in runtime_common_packages
    assert "hla.runtime" in runtime_common_packages
    assert "hla.fom" in runtime_common_packages
    assert "hla.spec" in runtime_common_packages
    assert "hla.bridges.java.jpype" in java_jpype_packages
    assert "hla.bridges.java.py4j" in java_py4j_packages
    assert "hla.vendors.pitch" in pitch_common_packages
    assert "hla.vendors.pitch.jpype" in pitch_jpype_packages
    assert "hla.vendors.pitch.py4j" in pitch_py4j_packages
    assert "hla.vendors.portico" in portico_packages
    assert "hla.transports.grpc" in grpc_transport_packages
    assert "hla.transports.rest" in rest_transport_packages
    assert "hla.foms.target_radar" in target_radar_packages
    assert "hla.foms.target_radar._internal" in target_radar_packages
    assert "hla.foms.target_radar.scenarios" not in target_radar_packages
    assert "hla.foms.target_radar.testing" not in target_radar_packages
    assert "hla.foms.proto2025_message_test" in message_test_packages
    assert "hla.foms.proto2025_message_test._internal" in message_test_packages
    assert "hla.foms.proto2025_space_lite" in space_lite_packages
    assert "hla.foms.proto2025_space_lite._internal" in space_lite_packages
    assert "hla.foms.proto2025_time_mgmt_test" in time_mgmt_packages
    assert "hla.foms.proto2025_time_mgmt_test._internal" in time_mgmt_packages
    assert "hla.verification" in verification_harness_packages


def test_core_and_python_backend_import_without_repo_root_on_pythonpath(tmp_path: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in SOURCE_ROOTS)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import hla.rti1516e; import hla.runtime.rti1516e as rti; from hla.backends.inmemory.plugin import plugin; rti.register_backend_plugin(plugin()); ambassador = rti.create_rti_ambassador('python'); print(hla.rti1516e.__version__, ambassador.backend_info.kind)",
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
            "import json, sys; import hla.rti1516e; print(json.dumps(sorted(name for name in sys.modules if name == 'hla.runtime.rti1516e' or name.startswith(('hla2010_rti_', 'hla.rti1516e.backends')))))",
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
        env["PYTHONPATH"] = os.pathsep.join(
            str(path) for path in _declared_internal_dependency_closure(spec["manifest_name"])
        )
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
                    "'root_rti_loaded': 'hla.runtime.rti1516e' in sys.modules, "
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
    manifest_by_module = {
        "hla.backends.inmemory": "hla-backend-inmemory",
        "hla.backends.certi": "hla-backend-certi",
        "hla.vendors.pitch.jpype": "hla-vendor-pitch-jpype",
        "hla.vendors.pitch.py4j": "hla-vendor-pitch-py4j",
        "hla.vendors.portico": "hla-vendor-portico",
    }
    for package_name, spec in BACKEND_SPLIT_PACKAGE_IMPORT_SPECS.items():
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            str(path) for path in _declared_internal_dependency_closure(manifest_by_module[package_name])
        )
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
                    "'root_rti_loaded': 'hla.runtime.rti1516e' in sys.modules, "
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
        entry_points = manifest["project"]["entry-points"]["hla.rti_backends"]

        for backend_name, target in entry_points.items():
            module_name, symbol_name = target.split(":", 1)
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join(
                str(path) for path in _declared_internal_dependency_closure(manifest_name)
            )
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
                        "'root_rti_loaded': 'hla.runtime.rti1516e' in sys.modules, "
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
            "import json, sys; import hla.backends.inmemory.plugin; print(json.dumps('hla.runtime.rti1516e' in sys.modules))",
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
            str(HLA_RTI1516E_SRC),
            str(HLA_RTI_CORE_SRC),
            str(ROOT / "packages/hla-backend-common/src"),
            str(ROOT / "packages/hla-transport-common/src"),
        )
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; "
                "from hla.transports.common import coerce_transport_spec; "
                "transport = coerce_transport_spec({'kind': 'subprocess-line', 'command': ['/bin/echo']}); "
                "print(json.dumps({'transport_module': type(transport).__module__, "
                "'backend_modules': sorted(name for name in sys.modules if name.startswith('hla.backends.certi'))}))"
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
    assert payload["transport_module"] == "hla.transports.common.transport"
    assert "hla.backends.certi" not in payload["backend_modules"]
