from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import tomllib
from hla.backends.cpp_shim.cpp_intake import CppSdkIntakeRequest, discover_cpp_sdk, generate_cpp_sdk_capsule, load_cpp_sdk_profile
from hla.rti import available_backend_plugins, create_rti_ambassador
from hla.verification.cpp_intake_certification import certify_cpp_sdk_core, certify_cpp_standard_core

CPP_2010_STANDARD_ARTIFACT = Path("build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a")
CPP_2025_STANDARD_ARTIFACT = Path("build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a")


def _write_fake_sdk_profile(tmp_path: Path, *, edition: str = "2010") -> Path:
    include_dir = tmp_path / "include"
    library_dir = tmp_path / "lib"
    header_dir = include_dir / "RTI"
    header_dir.mkdir(parents=True)
    library_dir.mkdir()
    (header_dir / "RTIambassador.h").write_text("// fake standard header\n", encoding="utf-8")
    compiler = shutil.which("c++")
    archiver = shutil.which("ar")
    if compiler is not None and archiver is not None:
        source = tmp_path / "vendor_stub.cpp"
        obj = tmp_path / "vendor_stub.o"
        source.write_text("extern \"C\" int shim_route_vendor_stub() { return 1; }\n", encoding="utf-8")
        subprocess.run([compiler, "-c", str(source), "-o", str(obj)], check=True)
        subprocess.run([archiver, "rcs", str(library_dir / "libvendor_rti1516e.a"), str(obj)], check=True)
    else:
        (library_dir / "libvendor_rti1516e.a").write_text("", encoding="utf-8")
    profile = tmp_path / f"vendor-cpp-{edition}.cpp-sdk.yaml"
    profile.write_text(
        "\n".join(
            [
                "kind: cpp-sdk",
                f"edition: {edition}",
                f"name: vendor-cpp-rti-{edition}",
                "include_dirs:",
                f"  - {include_dir}",
                "library_dirs:",
                f"  - {library_dir}",
                "libraries:",
                "  - vendor_rti1516e",
                "defines:",
                "  - RTI_USES_STD_WSTRING",
                "cxx_standard: 14",
                "runtime_env:",
                f"  LD_LIBRARY_PATH: {library_dir}",
                "factory:",
                "  strategy: standard",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return profile


def test_cpp_sdk_profile_parser_preserves_build_contract(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)

    profile = load_cpp_sdk_profile(profile_path)

    assert profile.kind == "cpp-sdk"
    assert profile.edition == "2010"
    assert profile.name == "vendor-cpp-rti-2010"
    assert profile.include_dirs
    assert profile.library_dirs
    assert profile.libraries == ("vendor_rti1516e",)
    assert profile.factory.strategy == "standard"


def test_cpp_sdk_discovery_reaches_link_green_for_fake_sdk_profile(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)

    report = discover_cpp_sdk(CppSdkIntakeRequest(profile_path=str(profile_path), transport="grpc"))
    checks = {check["name"]: check["status"] for check in report.checks}

    assert report.route == "cpp-2010-sdk-grpc"
    assert report.status == "link-green"
    assert checks["profile"] == "profile-valid"
    assert checks["headers"] == "header-green"
    assert checks["libraries"] == "link-green"
    assert report.errors == ()


def test_cpp_sdk_discovery_reports_missing_profile_without_stack_trace() -> None:
    report = discover_cpp_sdk(CppSdkIntakeRequest(profile_path="missing-vendor-cpp.cpp-sdk.yaml"))

    assert report.status == "failed"
    assert report.errors == ("C++ SDK profile does not exist: missing-vendor-cpp.cpp-sdk.yaml",)
    assert report.checks[0]["name"] == "profile"


@pytest.mark.skipif(not (shutil.which("cmake") and shutil.which("c++") and shutil.which("ar")), reason="C++ capsule build probe requires cmake, c++, and ar")
def test_cpp_sdk_capsule_generation_compiles_adapter_project(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)
    build_root = tmp_path / "capsules"

    report = generate_cpp_sdk_capsule(CppSdkIntakeRequest(profile_path=str(profile_path), transport="grpc"), build_root)
    checks = {check["name"]: check["status"] for check in report.checks}

    assert report.status == "capsule-built"
    assert report.capsule_dir is not None
    capsule_dir = Path(report.capsule_dir)
    assert (capsule_dir / "CMakeLists.txt").exists()
    assert (capsule_dir / "generated/shim_routes_cpp_intake_capsule.hpp").exists()
    assert (capsule_dir / "generated/shim_routes_cpp_intake_capsule.cpp").exists()
    assert checks["capsule_configure"] == "compile-green"
    assert checks["capsule_build"] == "capsule-built"


@pytest.mark.skipif(not (shutil.which("cmake") and shutil.which("c++") and shutil.which("ar")), reason="C++ capsule build probe requires cmake, c++, and ar")
def test_cpp_sdk_certify_core_smokes_capsule_without_claiming_core_green(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)

    report = certify_cpp_sdk_core(CppSdkIntakeRequest(profile_path=str(profile_path), transport="grpc"), tmp_path / "capsules")

    assert report.status == "adapter-smoke-green"
    assert report.capsule_dir is not None
    assert report.connect_status == "connect-green"
    assert report.callback_status == "callback-poll-green"
    assert report.core_scenario_status == "blocked"
    assert report.trace_comparison_status == "blocked"
    assert "full core scenario" in str(report.blocked_reason)


@pytest.mark.skipif(not CPP_2010_STANDARD_ARTIFACT.exists(), reason="C++ 2010 standard shim artifact is not built")
def test_cpp_standard_2010_certify_core_reaches_trace_green_when_built() -> None:
    report = certify_cpp_standard_core("2010", "pybind")

    assert report.status == "trace-green"
    assert report.callback_status == "callback-green"
    assert report.core_scenario_status == "core-exchange-green"


@pytest.mark.skipif(not CPP_2025_STANDARD_ARTIFACT.exists(), reason="C++ 2025 standard shim artifact is not built")
def test_cpp_standard_2025_certify_core_reaches_runtime_capability_when_built() -> None:
    report = certify_cpp_standard_core("2025", "pybind")
    events = {event["event"] for event in report.trace}

    assert report.status == "trace-green"
    assert report.callback_status == "callback-runtime-green"
    assert report.core_scenario_status == "runtime-capability-green"
    assert {
        "resolveFomHandles",
        "registerObjectInstance",
        "attributeOwnershipAcquisitionNotification",
        "timeAdvanceGrant",
        "serializeMOMServiceReport",
    } <= events


def test_generic_cpp_sdk_routes_are_registered_separately_from_standard_shims() -> None:
    plugins = available_backend_plugins()

    assert plugins["cpp-2010-sdk-pybind"].family == "intake/cpp"
    assert plugins["cpp-2010-sdk-grpc"].family == "intake/cpp"
    assert plugins["cpp-2025-sdk-pybind"].family == "intake/cpp"
    assert plugins["cpp-2025-sdk-grpc"].family == "intake/cpp"
    assert plugins["cpp-standard-2010-pybind"].family == "standard/cpp"
    assert plugins["cpp-standard-2025-grpc"].family == "standard/cpp"


def test_cpp_package_metadata_exports_standard_and_sdk_route_entry_points() -> None:
    pyproject = tomllib.loads(Path("packages/hla-backend-cpp-shim/pyproject.toml").read_text(encoding="utf-8"))
    entry_points = pyproject["project"]["entry-points"]["hla.rti_backends"]
    package_metadata = pyproject["tool"]["hla"]["package"]

    for name in (
        "cpp-standard-2010-pybind",
        "cpp-standard-2010-grpc",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
        "cpp-2010-sdk-pybind",
        "cpp-2010-sdk-grpc",
        "cpp-2025-sdk-pybind",
        "cpp-2025-sdk-grpc",
    ):
        assert name in entry_points
        assert name in package_metadata["backend_names"]


def test_generic_cpp_sdk_route_requires_profile() -> None:
    with pytest.raises(ValueError, match="require profile"):
        create_rti_ambassador(spec="rti1516e", backend="cpp-2010-sdk-grpc")


def test_generic_cpp_sdk_route_is_discovery_only_until_capsule_exists(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)

    with pytest.raises(RuntimeError, match="capsule invocation is not implemented yet"):
        create_rti_ambassador(spec="rti1516e", backend="cpp-2010-sdk-grpc", profile=str(profile_path))


def test__cpp_discover_writes_structured_report(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)
    output_dir = tmp_path / "evidence"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/shim_routes.py",
            "cpp",
            "discover",
            "--profile",
            str(profile_path),
            "--edition",
            "2010",
            "--transport",
            "grpc",
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["route"] == "cpp-2010-sdk-grpc"
    assert payload["status"] == "link-green"
    assert payload["evidence_json"].endswith(".json")
    assert payload["evidence_markdown"].endswith(".md")
    assert Path(payload["evidence_json"]).exists()


@pytest.mark.skipif(not (shutil.which("cmake") and shutil.which("c++") and shutil.which("ar")), reason="C++ capsule build probe requires cmake, c++, and ar")
def test__cpp_build_capsule_writes_generated_project(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)
    output_dir = tmp_path / "evidence"
    build_dir = tmp_path / "build-capsules"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/shim_routes.py",
            "cpp",
            "build-capsule",
            "--profile",
            str(profile_path),
            "--edition",
            "2010",
            "--transport",
            "grpc",
            "--build-dir",
            str(build_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["status"] == "capsule-built"
    assert payload["capsule_dir"]
    assert Path(payload["capsule_dir"], "CMakeLists.txt").exists()
    checks = {check["name"]: check["status"] for check in payload["checks"]}
    assert checks["capsule_configure"] == "compile-green"
    assert checks["capsule_build"] == "capsule-built"


@pytest.mark.skipif(not (shutil.which("cmake") and shutil.which("c++") and shutil.which("ar")), reason="C++ capsule smoke requires cmake, c++, and ar")
def test__cpp_smoke_capsule_writes_runtime_backed_report(tmp_path: Path) -> None:
    profile_path = _write_fake_sdk_profile(tmp_path)
    output_dir = tmp_path / "evidence"
    build_dir = tmp_path / "build-capsules"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/shim_routes.py",
            "cpp",
            "smoke-capsule",
            "--profile",
            str(profile_path),
            "--edition",
            "2010",
            "--transport",
            "grpc",
            "--build-dir",
            str(build_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["status"] == "adapter-smoke-green"
    assert payload["runtime"]["process_pid"]
    assert payload["runtime"]["invocation_count"] == 3
    assert payload["runtime"]["callback_count"] == 1
    assert payload["core_scenario_status"] == "not-run"
    assert Path(payload["evidence_json"]).exists()


@pytest.mark.skipif(not CPP_2010_STANDARD_ARTIFACT.exists(), reason="C++ 2010 standard shim artifact is not built")
def test__cpp_certify_core_standard_shim_writes_trace_green_report(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/shim_routes.py",
            "cpp",
            "certify-core",
            "--edition",
            "2010",
            "--artifact",
            "standard-shim",
            "--transports",
            "pybind",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    report = payload["reports"][0]
    assert report["status"] == "trace-green"
    assert report["callback_status"] == "callback-green"
    assert Path(report["evidence_json"]).exists()
