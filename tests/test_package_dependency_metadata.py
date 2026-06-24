from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"

ALLOWED_INTERNAL_DEPENDENCIES: dict[str, set[str]] = {
    "hla-rti1516e": set(),
    "hla-rti1516-2025": {"hla-rti-core"},
    "hla-backend-common": {"hla-rti1516e", "hla-rti-core"},
    "hla-backend-python1516-2025": {"hla-backend-common", "hla-rti1516-2025", "hla-rti-core", "hla-transport-common"},
    "hla-backend-shim": {"hla-backend-python1516-2025", "hla-rti1516-2025", "hla-rti-core"},
    "hla-bridge-java-common": {"hla-rti1516e", "hla-rti1516-2025", "hla-rti-core", "hla-backend-common"},
    "hla-backend-python1516e": {"hla-rti1516e", "hla-rti-core", "hla-backend-common"},
    "hla-backend-cpp-shim": {"hla-rti1516e", "hla-rti1516-2025", "hla-rti-core", "hla-backend-common", "hla-backend-python1516e"},
    "hla-rti-core": set(),
    "hla-backend-certi": {"hla-rti1516e", "hla-backend-common", "hla-rti-core", "hla-transport-common"},
    "hla-bridge-java-jpype": {"hla-rti1516e", "hla-rti-core", "hla-backend-common", "hla-bridge-java-common"},
    "hla-bridge-java-py4j": {"hla-rti1516e", "hla-rti-core", "hla-bridge-java-common"},
    "hla-vendor-pitch": {"hla-rti1516e", "hla-bridge-java-common", "hla-rti-core"},
    "hla-vendor-pitch-jpype": {
        "hla-rti1516e",
        "hla-rti-core",
        "hla-bridge-java-common",
        "hla-bridge-java-jpype",
        "hla-vendor-pitch",
        "hla-backend-python1516-2025",
    },
    "hla-vendor-pitch-py4j": {
        "hla-rti1516e",
        "hla-rti-core",
        "hla-bridge-java-common",
        "hla-bridge-java-py4j",
        "hla-vendor-pitch",
        "hla-backend-python1516-2025",
    },
    "hla-vendor-portico": {
        "hla-rti1516e",
        "hla-rti-core",
        "hla-bridge-java-common",
        "hla-bridge-java-jpype",
        "hla-bridge-java-py4j",
    },
    "hla-transport-common": {"hla-rti1516e", "hla-backend-common"},
    "hla-transport-grpc": {
        "hla-rti1516e",
        "hla-backend-common",
        "hla-transport-common",
        "hla-rti-core",
    },
    "hla-transport-rest": {
        "hla-rti1516e",
        "hla-backend-common",
        "hla-transport-common",
        "hla-rti-core",
    },
    "hla-verification": {"hla-rti1516e", "hla-rti1516-2025", "hla-backend-common", "hla-backend-python1516e", "hla-backend-cpp-shim", "hla-bridge-java-common", "hla-fom-target-radar", "hla-fom-proto2025-message-test", "hla-fom-proto2025-space-lite", "hla-fom-proto2025-time-mgmt-test", "hla-rti-core"},
    "hla-fom-target-radar": {"hla-rti1516e", "hla-rti1516-2025", "hla-rti-core"},
    "hla-fom-proto2025-message-test": {"hla-rti1516e", "hla-rti1516-2025", "hla-backend-common", "hla-backend-python1516e"},
    "hla-fom-proto2025-space-lite": {"hla-rti1516e", "hla-rti1516-2025", "hla-backend-common", "hla-backend-python1516e"},
    "hla-fom-proto2025-time-mgmt-test": {"hla-rti1516e", "hla-rti1516-2025", "hla-backend-common", "hla-backend-python1516e"},
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
