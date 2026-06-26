from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from hla.backends.cpp_shim.cpp_toolchain import CppToolchainArtifact, CppToolchainInventory


ROOT = Path(__file__).resolve().parents[1]


def _load_doctor_module():
    spec = importlib.util.spec_from_file_location("doctor_module_for_tests", ROOT / "scripts" / "doctor.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_cpp_toolchain_check_reports_warn_when_artifacts_are_missing(monkeypatch) -> None:
    inventory = CppToolchainInventory(
        cxx="/usr/bin/c++",
        ar="/usr/bin/ar",
        cmake=None,
        cxx_ok=True,
        ar_ok=True,
        cmake_ok=False,
        status="degraded",
        artifacts=(
            CppToolchainArtifact(
                key="cpp-standard-2010",
                label="C++ 2010 standard shim archive",
                path="build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a",
                exists=False,
                build_command="./tools/shim-routes build cpp-standard-2010",
            ),
            CppToolchainArtifact(
                key="cpp-standard-2025",
                label="C++ 2025 standard shim archive",
                path="build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a",
                exists=True,
                build_command="./tools/shim-routes build cpp-standard-2025",
            ),
        ),
    )

    from hla.backends import cpp_shim

    monkeypatch.setattr(cpp_shim, "discover_cpp_toolchain", lambda repo_root_arg: inventory)

    module = _load_doctor_module()
    check = module.check_cpp_toolchain()
    assert check.name == "cpp_toolchain"
    assert check.status == "warn"
    assert "C++ routes are not fully prepared" == check.summary
    assert "missing artifacts: cpp-standard-2010" in (check.detail or "")
    assert "./tools/shim-routes cpp doctor" in (check.detail or "")


def test_workspace_duplicates_check_reports_fail_when_copy_suffix_file_exists(monkeypatch) -> None:
    module = _load_doctor_module()

    class _Row:
        path = "docs/example 2.md"
        canonical_path = "docs/example.md"
        status = "same-content-copy"

    class _Report:
        duplicate_count = 1
        duplicates = (_Row(),)

    monkeypatch.setattr(module, "build_duplicate_audit", lambda root=None: _Report())
    monkeypatch.setattr(module, "strict_duplicate_candidates", lambda report: report.duplicates)

    check = module.check_workspace_duplicates()
    assert check.name == "workspace_duplicates"
    assert check.status == "fail"
    assert check.summary == "duplicate workspace files detected"
    assert "docs/example 2.md -> docs/example.md (same-content-copy)" in (check.detail or "")
    assert "./tools/duplicate-audit" in (check.detail or "")


def test_workspace_duplicates_check_ignores_generated_only_duplicates(monkeypatch) -> None:
    module = _load_doctor_module()

    class _GeneratedRow:
        path = "artifacts/report 2.json"
        canonical_path = "artifacts/report.json"
        status = "different-content-copy"

    class _Report:
        duplicate_count = 1
        duplicates = (_GeneratedRow(),)

    monkeypatch.setattr(module, "build_duplicate_audit", lambda root=None: _Report())
    monkeypatch.setattr(module, "strict_duplicate_candidates", lambda report: ())

    check = module.check_workspace_duplicates()
    assert check.name == "workspace_duplicates"
    assert check.status == "ok"
