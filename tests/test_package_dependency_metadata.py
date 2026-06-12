from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"

ALLOWED_INTERNAL_DEPENDENCIES: dict[str, set[str]] = {
    "hla2010-spec": set(),
    "hla2010-rti-backend-common": {"hla2010-spec"},
    "hla2010-rti-java-common": {"hla2010-spec", "hla2010-rti-backend-common"},
    "hla2010-rti-python": {"hla2010-spec", "hla2010-rti-backend-common"},
    "hla2010-rti-runtime-common": {"hla2010-spec", "hla2010-rti-backend-common", "hla2010-rti-transport-common"},
    "hla2010-rti-certi": {"hla2010-spec", "hla2010-rti-java-common", "hla2010-rti-runtime-common", "hla2010-rti-transport-common"},
    "hla2010-rti-java-jpype": {"hla2010-spec", "hla2010-rti-java-common"},
    "hla2010-rti-java-py4j": {"hla2010-spec", "hla2010-rti-java-common"},
    "hla2010-rti-pitch-common": {"hla2010-spec", "hla2010-rti-java-common", "hla2010-rti-runtime-common"},
    "hla2010-rti-pitch-jpype": {
        "hla2010-spec",
        "hla2010-rti-java-common",
        "hla2010-rti-java-jpype",
        "hla2010-rti-pitch-common",
    },
    "hla2010-rti-pitch-py4j": {
        "hla2010-spec",
        "hla2010-rti-java-common",
        "hla2010-rti-java-py4j",
        "hla2010-rti-pitch-common",
    },
    "hla2010-rti-portico": {"hla2010-spec", "hla2010-rti-java-common", "hla2010-rti-java-jpype", "hla2010-rti-java-py4j"},
    "hla2010-rti-transport-common": {"hla2010-spec", "hla2010-rti-backend-common"},
    "hla2010-rti-transport-grpc": {
        "hla2010-spec",
        "hla2010-rti-backend-common",
        "hla2010-rti-transport-common",
        "hla2010-rti-runtime-common",
    },
    "hla2010-rti-transport-rest": {
        "hla2010-spec",
        "hla2010-rti-backend-common",
        "hla2010-rti-transport-common",
        "hla2010-rti-runtime-common",
    },
    "hla2010-verification-harness": {"hla2010-spec", "hla2010-rti-backend-common", "hla2010-rti-runtime-common"},
    "hla2010-fom-target-radar": {"hla2010-spec", "hla2010-verification-harness", "hla2010-rti-runtime-common"},
}


def _internal_dependencies(package_name: str) -> set[str]:
    pyproject = PACKAGES / package_name / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"].get("dependencies", [])
    internal = set()
    for dep in deps:
        dep_name = str(dep).split("==", 1)[0]
        if dep_name in ALLOWED_INTERNAL_DEPENDENCIES:
            internal.add(dep_name)
    return internal


def test_package_dependency_metadata_matches_allowed_internal_graph() -> None:
    for package_name, expected in ALLOWED_INTERNAL_DEPENDENCIES.items():
        assert _internal_dependencies(package_name) == expected
