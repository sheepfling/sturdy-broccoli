from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"


EXPECTED_PACKAGES = {
    "hla2010-spec": {"role": "core-spec", "entry_points": set()},
    "hla2010-rti-python": {"role": "rti-backend", "entry_points": {"python"}, "status": "implementation-moved"},
    "hla2010-rti-certi": {
        "role": "rti-backend",
        "entry_points": {"certi", "certi-jpype", "certi-py4j"},
        "status": "implementation-moved",
    },
    "hla2010-rti-backend-common": {
        "role": "backend-support",
        "entry_points": set(),
        "status": "implementation-moved",
    },
    "hla2010-rti-java-common": {
        "role": "java-support",
        "entry_points": set(),
        "status": "implementation-moved",
    },
    "hla2010-rti-runtime-common": {
        "role": "runtime-support",
        "entry_points": set(),
        "status": "implementation-moved",
    },
    "hla2010-rti-java-jpype": {
        "role": "java-bridge",
        "entry_points": {"jpype"},
        "status": "implementation-moved",
    },
    "hla2010-rti-java-py4j": {
        "role": "java-bridge",
        "entry_points": {"py4j"},
        "status": "implementation-moved",
    },
    "hla2010-rti-pitch-common": {
        "role": "runtime-common",
        "entry_points": set(),
        "status": "implementation-moved",
    },
    "hla2010-rti-pitch-jpype": {
        "role": "rti-backend",
        "entry_points": {"pitch-jpype"},
        "status": "implementation-moved",
    },
    "hla2010-rti-pitch-py4j": {
        "role": "rti-backend",
        "entry_points": {"pitch-py4j"},
        "status": "implementation-moved",
    },
    "hla2010-rti-portico": {
        "role": "rti-backend",
        "entry_points": {"portico-jpype", "portico-py4j"},
        "status": "implementation-moved",
    },
    "hla2010-fom-target-radar": {"role": "fom-example", "entry_points": set(), "status": "implementation-moved"},
    "hla2010-verification-harness": {"role": "verification-harness", "entry_points": set(), "status": "implementation-moved"},
}


def _load_project(package_name: str) -> dict:
    path = PACKAGES / package_name / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_package_split_scaffolds_are_declared():
    assert (PACKAGES / "README.md").exists()
    actual = {path.name for path in PACKAGES.iterdir() if path.is_dir()}
    assert EXPECTED_PACKAGES.keys() <= actual


def test_split_packages_use_package_owned_src_roots():
    for package_name, expected in EXPECTED_PACKAGES.items():
        split = _load_project(package_name)["tool"]["hla2010"]["package-split"]
        source_roots = split["source_roots"]
        assert source_roots
        if expected.get("status") == "implementation-moved":
            assert any(root.startswith(f"packages/{package_name}/src/") for root in source_roots)


def test_package_split_pyprojects_have_expected_boundaries():
    for package_name, expected in EXPECTED_PACKAGES.items():
        data = _load_project(package_name)
        project = data["project"]
        split = data["tool"]["hla2010"]["package-split"]

        assert project["name"] == package_name
        assert project["requires-python"] == ">=3.10"
        assert split["status"] == expected.get("status", "migration-scaffold")
        assert split["role"] == expected["role"]
        assert split["source_roots"]
        if split["status"] in {"transition-wrapper", "implementation-moved"}:
            assert (PACKAGES / package_name / "MIGRATION.md").exists()

        entry_points = data.get("project", {}).get("entry-points", {}).get("hla2010.rti_backends", {})
        assert set(entry_points) == expected["entry_points"]
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


def test_backend_scaffolds_depend_on_core_spec_package():
    for package_name, expected in EXPECTED_PACKAGES.items():
        if expected["role"] == "core-spec":
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
    assert "hla2010-rti-java-common==0.13.0" in python_dependencies
    assert "hla2010-rti-java-common==0.13.0" in certi_dependencies
    assert "jpype1" not in pitch_jpype_dependencies
    assert "py4j" not in pitch_py4j_dependencies


def test_vendor_runtime_packages_depend_on_runtime_common_package():
    runtime_common_dependencies = set(_load_project("hla2010-rti-runtime-common")["project"].get("dependencies", ()))
    assert "hla2010-rti-java-common==0.13.0" not in runtime_common_dependencies

    certi_dependencies = set(_load_project("hla2010-rti-certi")["project"].get("dependencies", ()))
    pitch_common_dependencies = set(_load_project("hla2010-rti-pitch-common")["project"].get("dependencies", ()))

    assert "hla2010-rti-runtime-common==0.13.0" in certi_dependencies
    assert "hla2010-rti-runtime-common==0.13.0" in pitch_common_dependencies


def test_root_pyproject_declares_workspace_package_roots():
    root_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_roots = root_project["tool"]["setuptools"]["packages"]["find"]["where"]
    pytest_roots = root_project["tool"]["pytest"]["ini_options"]["pythonpath"]

    assert package_roots[0] == "src"
    assert pytest_roots[0] == "src"
    assert "packages/hla2010-rti-python/src" in package_roots
    assert "packages/hla2010-rti-certi/src" in package_roots
    assert "packages/hla2010-rti-java-jpype/src" in package_roots
    assert "packages/hla2010-rti-java-py4j/src" in package_roots
    assert "packages/hla2010-rti-portico/src" in package_roots
    assert "packages/hla2010-fom-target-radar/src" in package_roots
    assert "packages/hla2010-verification-harness/src" in package_roots
    assert package_roots == pytest_roots
