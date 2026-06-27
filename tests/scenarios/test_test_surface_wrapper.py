from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_tools_test_surface_help_describes_inventory_and_run_lanes() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/test-surface inventory" in result.stdout
    assert "./tools/test-surface validate" in result.stdout
    assert "./tools/test-surface recommend" in result.stdout
    assert "./tools/test-surface run smoke" in result.stdout
    assert "./tools/test-surface run fast" in result.stdout
    assert "./tools/test-surface run repo-green-units" in result.stdout
    assert "./tools/test-surface run unit-foundation" in result.stdout
    assert "./tools/test-surface run unit-python-core" in result.stdout
    assert "./tools/test-surface run unit-federate-examples" in result.stdout
    assert "./tools/test-surface run unit-vendor-onboarding" in result.stdout
    assert "./tools/test-surface run unit-shim-tooling" in result.stdout
    assert "./tools/test-surface run onboarding" in result.stdout
    assert "./tools/test-surface run shim-tooling" in result.stdout
    assert "./tools/test-surface run transport" in result.stdout
    assert "./tools/test-surface run unit-fom-tooling" in result.stdout
    assert "./tools/test-surface run unit-python-2025-core" in result.stdout
    assert "./tools/test-surface run unit-transport-local" in result.stdout
    assert "./tools/test-surface run unit-scenarios-light" in result.stdout
    assert "./tools/test-surface run python1516_2025-main" in result.stdout
    assert "./tools/test-surface run python-routes" in result.stdout
    assert "./tools/test-surface run python1516_2025-routes" in result.stdout
    assert "./tools/test-surface run matrix" in result.stdout


def test_tools_test_surface_inventory_json_lists_canonical_lanes() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "inventory", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    lane_ids = [row["id"] for row in payload["lanes"]]
    assert lane_ids == [
        "smoke",
        "fast",
        "repo-green",
        "repo-green-units",
        "unit-foundation",
        "unit-python-core",
        "unit-federate-examples",
        "unit-vendor-onboarding",
        "unit-shim-tooling",
        "unit-fom-tooling",
        "unit-python-2025-core",
        "unit-transport-local",
        "unit-scenarios-light",
        "python1516_2025-main",
        "python-routes",
        "python1516_2025-routes",
        "vendor",
        "matrix",
    ]
    alias_map = {row["id"]: row["aliases"] for row in payload["lanes"]}
    assert alias_map["repo-green-units"] == ["repo-units"]
    assert alias_map["unit-vendor-onboarding"] == ["onboarding"]
    assert alias_map["unit-shim-tooling"] == ["shim-tooling"]
    assert alias_map["unit-transport-local"] == ["transport"]


def test_tools_test_surface_validate_json_reports_manifest_path() -> None:
    clean_root = ROOT / "artifacts" / "test_surface_validate_clean_root"
    clean_root.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["bash", "tools/test-surface", "validate", "--json"],
        cwd=ROOT,
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "HLA2010_DUPLICATE_AUDIT_ROOT": str(clean_root),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert payload["manifest"].endswith("testing/test_surface_manifest.json")
    assert payload["errors"] == []
    assert payload["duplicate_audit"]["duplicate_count"] >= 0


def test_tools_test_surface_validate_fails_when_duplicate_audit_finds_workspace_copy(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "demo.py").write_text("print('a')\n", encoding="utf-8")
    (workspace / "demo 2.py").write_text("print('a')\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", "tools/test-surface", "validate", "--json"],
        cwd=ROOT,
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "HLA2010_DUPLICATE_AUDIT_ROOT": str(workspace),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["duplicate_audit"]["duplicate_count"] == 1
    assert "workspace duplicate candidate:" in payload["errors"][0]


def test_tools_test_surface_validate_passes_when_duplicates_exist_only_under_generated_artifacts(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "artifacts").mkdir(parents=True, exist_ok=True)
    (workspace / "artifacts" / "report.json").write_text("{}\n", encoding="utf-8")
    (workspace / "artifacts" / "report 2.json").write_text("{\"dirty\": true}\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", "tools/test-surface", "validate", "--json"],
        cwd=ROOT,
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "HLA2010_DUPLICATE_AUDIT_ROOT": str(workspace),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert payload["duplicate_audit"]["duplicate_count"] == 1
    assert payload["duplicate_audit"]["strict_duplicate_count"] == 0
    assert payload["errors"] == []


def test_tools_test_surface_inventory_fails_fast_on_invalid_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "invalid_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "lanes": [
                    {
                        "id": "broken",
                        "title": "broken",
                        "description": "broken",
                        "owner_command": ["./tools/test-surface", "run", "broken"],
                        "include_lanes": ["missing", "missing"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", "tools/test-surface", "inventory", "--json"],
        cwd=ROOT,
        env={
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "HLA2010_TEST_SURFACE_MANIFEST": str(manifest_path),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "test surface manifest invalid:" in result.stderr
    assert "includes 'missing' more than once" in result.stderr
    assert "includes unknown lane 'missing'" in result.stderr


def test_tools_test_surface_run_smoke_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "smoke", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "smoke"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-smoke"]
    assert payload["steps"][0]["status"] == "planned"
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_fast_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "fast", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "fast"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["status"] == "planned"
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_unit_vendor_onboarding_emits_live_progress_to_stderr() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-vendor-onboarding"],
        cwd=ROOT,
        env={
            **os.environ,
            "HLA2010_TEST_SURFACE_UNIT_VENDOR_ONBOARDING_CMD": ":",
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert "unit-vendor-onboarding: passed" in result.stdout
    assert "[test-surface] lane unit-vendor-onboarding: running sh -c :" in result.stderr
    assert "[test-surface] lane unit-vendor-onboarding: sh -c : -> passed" in result.stderr


def test_tools_test_surface_run_repo_green_units_emits_nested_progress_without_nested_stdout() -> None:
    env = {
        **os.environ,
        "HLA2010_TEST_SURFACE_UNIT_FOUNDATION_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_PYTHON_CORE_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_FEDERATE_EXAMPLES_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_VENDOR_ONBOARDING_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_SHIM_TOOLING_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_FOM_TOOLING_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_PYTHON_2025_CORE_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_TRANSPORT_LOCAL_CMD": ":",
        "HLA2010_TEST_SURFACE_UNIT_SCENARIOS_LIGHT_CMD": ":",
    }
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "repo-green-units"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert "repo-green-units: passed" in result.stdout
    assert "\nunit-foundation: passed\n" not in result.stdout
    assert "[test-surface] lane repo-green-units: starting nested lane unit-foundation" in result.stderr
    assert "[test-surface] lane repo-green-units: nested lane unit-scenarios-light -> passed" in result.stderr


def test_tools_test_surface_run_unit_foundation_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-foundation", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-foundation"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/test-focus", "run", "foundation"]
    assert payload["steps"][1]["argv"] == [
        "./tools/test",
        "tests/test_operator_surface_policy.py",
        "tests/test_documentation_policy.py",
        "tests/test_tools_test_wrapper.py",
        "tests/test_tools_python_wrapper.py",
        "tests/scenarios/test_test_surface_wrapper.py",
        "tests/scenarios/test_ci_green_wrappers.py",
        "tests/test_backend_wrapper_policy.py",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_unit_foundation_uses_bash_for_non_executable_wrapper() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-foundation", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["steps"][0]["argv"] == ["./tools/test-focus", "run", "foundation"]


def test_tools_test_surface_run_unit_federate_examples_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-federate-examples", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-federate-examples"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == [
        "./tools/test",
        "tests/test_tools_federate_cli_wrapper.py",
        "tests/test_operator_surface_policy.py",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_unit_vendor_onboarding_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-vendor-onboarding", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-vendor-onboarding"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/certi-easy", "preflight"]
    assert payload["steps"][1]["argv"] == ["./tools/pitch", "doctor"]
    assert payload["steps"][2]["argv"] == ["./tools/pitch", "preflight"]
    assert payload["steps"][3]["argv"] == [
        "./tools/test",
        "tests/test_pitch_docker_first_run_doc.py",
        "tests/scenarios/test_easy_preflight_reports.py",
        "tests/scenarios/test_preflight_contracts.py",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_root_vendor_wrappers_removed_and_tools_wrappers_present",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_duplicate_audit_top_level_wrapper_bootstraps_source_checkout",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_bootstrap_top_level_wrapper_doctor_bootstraps_source_checkout",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_certi_easy_top_level_wrapper_runs_preflight",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_certi_easy_top_level_wrapper_preflight_is_reachable_from_outside_repo",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_runs_preflight",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_preflight_is_reachable_from_outside_repo",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_help_lists_best_effort_routes",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_crc_macos_repro_is_reachable_from_outside_repo",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_crc_docker_repro_is_reachable_from_outside_repo",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_runs_smoke",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_runs_verify_best_effort",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_verify_best_effort_is_reachable_from_outside_repo",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_verify_is_reachable_from_outside_repo",
        "tests/scenarios/test_top_level_vendor_wrappers.py::test_pitch_top_level_wrapper_runs_probe_route",
        "tests/scenarios/test_pitch_tool_router.py",
        "tests/test_documentation_policy.py",
        "tests/test_operator_surface_policy.py",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_unit_shim_tooling_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "unit-shim-tooling", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-shim-tooling"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == [
        "./tools/test",
        "tests/runtime/test_java_toolchain.py",
        "tests/runtime/test_cpp_toolchain.py",
        "tests/test_tools_java_wrapper.py",
        "tests/test_tools_shim_routes_wrapper.py",
        "tests/test_documentation_policy.py",
        "tests/test_operator_surface_policy.py",
        "tests/backends/test_standard_shim_artifacts.py",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_onboarding_alias_dry_run_resolves_to_vendor_onboarding() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "onboarding", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "unit-vendor-onboarding"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True


def test_tools_test_surface_run_repo_green_units_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "repo-green-units", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "repo-green-units"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert [step["lane"] for step in payload["steps"]] == [
        "unit-foundation",
        "unit-python-core",
        "unit-federate-examples",
        "unit-vendor-onboarding",
        "unit-shim-tooling",
        "unit-fom-tooling",
        "unit-python-2025-core",
        "unit-transport-local",
        "unit-scenarios-light",
    ]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_python_routes_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "python-routes", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "python-routes"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-routes-preflight"]
    assert payload["steps"][1]["argv"] == ["./tools/python", "verify-routes"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_python_main_2025_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "python1516_2025-main", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "python1516_2025-main"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-main-2025"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_python_routes_2025_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "python1516_2025-routes", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "python1516_2025-routes"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/python", "verify-routes-preflight"]
    assert payload["steps"][1]["argv"] == ["./tools/python", "verify-routes-2025"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_surface_run_matrix_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-surface", "run", "matrix", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["lane"] == "matrix"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == ["./tools/compliance", "generate"]
    assert payload["steps"][1]["argv"] == [
        "./tools/fom-siso-runtime-surface-matrix",
        "--preset",
        "micro-bridge-smoke",
        "--with-screenshots",
    ]
    assert payload["steps"][2]["argv"] == [
        "./tools/fom-siso-runtime-surface-matrix",
        "--preset",
        "showcase-hydrated",
        "--with-screenshots",
    ]
    assert payload["steps"][3]["argv"] == ["python3", "scripts/run_spec2025_finish_line.py"]
    assert payload["steps"][4]["argv"] == ["./tools/compliance", "discover", "--show-backlog"]
    assert payload["steps"][5]["argv"] == ["./tools/section8-gate"]
    assert all(step["status"] == "planned" for step in payload["steps"])
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()
