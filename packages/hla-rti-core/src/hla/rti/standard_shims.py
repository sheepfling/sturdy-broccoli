"""Rosetta standard-shim artifact and route contract.

This module names the standard-backed artifacts that must exist before a route
can claim to be a Java or C++ standard shim. The existing in-process Java shim
and C++ skeleton routes are useful development fixtures, but they are not these
artifacts until they compile against the official IEEE API bundles.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StandardShimRoute:
    """One Python-visible bridge/transport route for a standard shim artifact."""

    name: str
    bridge: str
    transport: str


@dataclass(frozen=True, slots=True)
class StandardShimArtifact:
    """Buildable Java or C++ RTI shim that is backed by official API inputs."""

    key: str
    language: str
    edition: str
    spec_name: str
    artifact_name: str
    official_api_bundle: str
    standard_surface: str
    routes: tuple[StandardShimRoute, ...]
    status: str = "planned"


STANDARD_SHIM_ARTIFACTS: tuple[StandardShimArtifact, ...] = (
    StandardShimArtifact(
        key="java-2010",
        language="java",
        edition="2010",
        spec_name="rti1516e",
        artifact_name="hla-x-rti1516e-java-shim.jar",
        official_api_bundle="specs/ieee-1516-2010/hla_specs/1516.1-2010_downloads/IEEE1516-2010_Java_API.zip",
        standard_surface="hla.rti1516e Java API",
        routes=(
            StandardShimRoute("java-standard-2010-jpype", "jpype", "in-process-jvm"),
            StandardShimRoute("java-standard-2010-py4j", "py4j", "gateway-jvm"),
        ),
    ),
    StandardShimArtifact(
        key="java-2025",
        language="java",
        edition="2025",
        spec_name="rti1516_2025",
        artifact_name="hla-x-rti1516-2025-java-shim.jar",
        official_api_bundle="specs/ieee-1516-2025/1516.1-2025_downloads.zip",
        standard_surface="1516.1-2025 Java API",
        routes=(
            StandardShimRoute("java-standard-2025-jpype", "jpype", "in-process-jvm"),
            StandardShimRoute("java-standard-2025-py4j", "py4j", "gateway-jvm"),
        ),
    ),
    StandardShimArtifact(
        key="cpp-2010",
        language="cpp",
        edition="2010",
        spec_name="rti1516e",
        artifact_name="libhla_x_rti1516e_cpp_shim",
        official_api_bundle="specs/ieee-1516-2010/hla_specs/1516.1-2010_downloads/IEEE1516-2010_C++_API.zip",
        standard_surface="rti1516e C++ namespace",
        routes=(
            StandardShimRoute("cpp-standard-2010-pybind", "pybind", "in-process-extension"),
            StandardShimRoute("cpp-standard-2010-grpc", "grpc", "sidecar-process"),
        ),
    ),
    StandardShimArtifact(
        key="cpp-2025",
        language="cpp",
        edition="2025",
        spec_name="rti1516_2025",
        artifact_name="libhla_x_rti1516_2025_cpp_shim",
        official_api_bundle="specs/ieee-1516-2025/1516.1-2025_downloads.zip",
        standard_surface="rti1516_2025 C++ namespace",
        routes=(
            StandardShimRoute("cpp-standard-2025-pybind", "pybind", "in-process-extension"),
            StandardShimRoute("cpp-standard-2025-grpc", "grpc", "sidecar-process"),
        ),
    ),
)


def iter_standard_shim_artifacts() -> tuple[StandardShimArtifact, ...]:
    """Return the standard shim artifacts in stable build order."""

    return STANDARD_SHIM_ARTIFACTS


def iter_standard_shim_routes() -> tuple[StandardShimRoute, ...]:
    """Return all route names reserved for standard-backed shims."""

    return tuple(route for artifact in STANDARD_SHIM_ARTIFACTS for route in artifact.routes)


def standard_shim_route_names() -> tuple[str, ...]:
    """Return all Python backend route names reserved for standard-backed shims."""

    return tuple(route.name for route in iter_standard_shim_routes())


def official_api_bundle_paths(root: str | Path) -> dict[str, Path]:
    """Return the official API bundle path required by each artifact key."""

    root_path = Path(root)
    return {artifact.key: root_path / artifact.official_api_bundle for artifact in STANDARD_SHIM_ARTIFACTS}


__all__ = [
    "STANDARD_SHIM_ARTIFACTS",
    "StandardShimArtifact",
    "StandardShimRoute",
    "iter_standard_shim_artifacts",
    "iter_standard_shim_routes",
    "official_api_bundle_paths",
    "standard_shim_route_names",
]
