from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_rosetta_standard_shim_contract_names_four_standard_backed_artifacts() -> None:
    from hla.rti.standard_shims import iter_standard_shim_artifacts

    artifacts = iter_standard_shim_artifacts()
    by_key = {artifact.key: artifact for artifact in artifacts}

    assert set(by_key) == {"java-2010", "java-2025", "cpp-2010", "cpp-2025"}
    assert by_key["java-2010"].spec_name == "rti1516e"
    assert by_key["cpp-2010"].spec_name == "rti1516e"
    assert by_key["java-2025"].spec_name == "rti1516_2025"
    assert by_key["cpp-2025"].spec_name == "rti1516_2025"


def test_rosetta_standard_route_names_are_reserved_and_standard_plugins_are_distinct() -> None:
    from hla.rti import available_backend_plugins
    from hla.rti.standard_shims import standard_shim_route_names

    routes = set(standard_shim_route_names())
    assert routes == {
        "java-standard-2010-jpype",
        "java-standard-2010-py4j",
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2010-pybind",
        "cpp-standard-2010-grpc",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    }

    registered_plugins = available_backend_plugins()
    assert registered_plugins["java-standard-2010-jpype"].family == "standard/java"
    assert registered_plugins["java-standard-2010-py4j"].family == "standard/java"
    assert registered_plugins["java-standard-2025-jpype"].family == "standard/java"
    assert registered_plugins["java-standard-2025-py4j"].family == "standard/java"
    assert registered_plugins["cpp-standard-2010-pybind"].family == "standard/cpp"
    assert registered_plugins["cpp-standard-2010-grpc"].family == "standard/cpp"
    assert registered_plugins["cpp-standard-2025-pybind"].family == "standard/cpp"
    assert registered_plugins["cpp-standard-2025-grpc"].family == "standard/cpp"
    assert "java-standard-shim-jpype" not in registered_plugins
    assert "java-standard-shim-py4j" not in registered_plugins


def test_standard_shim_contract_points_at_checked_in_official_api_bundles() -> None:
    from hla.rti.standard_shims import official_api_bundle_paths

    paths = official_api_bundle_paths(ROOT)

    assert paths["java-2010"].name == "IEEE1516-2010_Java_API.zip"
    assert paths["cpp-2010"].name == "IEEE1516-2010_C++_API.zip"
    assert paths["java-2025"].name == "1516.1-2025_downloads.zip"
    assert paths["cpp-2025"].name == "1516.1-2025_downloads.zip"
    assert all(path.exists() for path in paths.values())
