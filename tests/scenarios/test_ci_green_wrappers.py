from __future__ import annotations

import json
import os
import subprocess
import tomllib
from pathlib import Path

from tests.typed_json_models import (
    RecordedArgvCall,
    VendorRuntimeCiStateSummary,
    VendorRuntimeStatusSummary,
)


ROOT = Path(__file__).resolve().parents[2]


def test_repo_green_default_suite_includes_2010_and_2025_grpc_route_tests() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    testpaths = pyproject["tool"]["pytest"]["ini_options"]["testpaths"]
    assert "tests" in testpaths

    full_sequence = (ROOT / "scripts/ci/full_sequence.sh").read_text(encoding="utf-8")
    assert 'run_step "standard shim route artifacts" "$ROOT_DIR/scripts/ci/build_standard_shims_if_available.sh"' in full_sequence
    assert 'run_step "unit tests" "$ROOT_DIR/scripts/ci/test.sh"' in full_sequence

    test_script = (ROOT / "scripts/ci/test.sh").read_text(encoding="utf-8")
    assert "python -m pytest -q" in test_script

    default_suite_files = [
        ROOT / "tests/transport/test_grpc_transport.py",
        ROOT / "tests/transport/test_grpc_transport_2025.py",
        ROOT / "tests/backends/test_standard_shim_artifacts.py",
        ROOT / "tests/backends/test_standard_java_shim_routes.py",
    ]
    for path in default_suite_files:
        assert path.exists(), path.relative_to(ROOT)


def test_repo_green_help_describes_repo_green_lane() -> None:
    result = subprocess.run(
        ["bash", "scripts/ci/repo_green.sh", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "repo-green" in result.stdout
    assert "./scripts/ci/full_sequence.sh" in result.stdout
    assert "./scripts/ci/vendor_green.sh" in result.stdout


def test_tools_python_help_describes_repo_green_operator_lane() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/python verify" in result.stdout
    assert "./tools/python verify-routes" in result.stdout
    assert "./tools/python verify-routes-preflight" in result.stdout
    assert "./scripts/ci/repo_green.sh" in result.stdout
    assert "./tools/certi-easy" in result.stdout
    assert "./tools/pitch" in result.stdout


def test_vendor_green_help_describes_strict_vendor_lane() -> None:
    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "vendor-green" in result.stdout
    assert "HLA2010_VENDOR_PREFLIGHT_STRICT=1" in result.stdout
    assert "./scripts/ci/repo_green.sh" in result.stdout


def test_github_ci_local_help_describes_modes() -> None:
    result = subprocess.run(
        ["bash", "scripts/ci/github_ci_local.sh", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "default" in result.stdout
    assert "vendor-required" in result.stdout
    assert "vendor-edge" in result.stdout
    assert "probe-review" in result.stdout
    assert "vendor-smoke" in result.stdout
    assert "all" in result.stdout
    assert "vendor-runner-contract" in result.stdout or "contract guard" in result.stdout


def _recording_override_env(log_path: Path, lane_names: list[str]) -> dict[str, str]:
    env = os.environ.copy()
    for lane_name in lane_names:
        env[f"HLA2010_GITHUB_CI_LOCAL_{lane_name}_CMD"] = f"printf '%s\\n' '{lane_name}' >> '{log_path}'"
    return env


def test_github_ci_local_default_mode_runs_expected_lanes_in_order(tmp_path: Path) -> None:
    log_path = tmp_path / "lanes.log"
    lane_names = [
        "VENDOR_RUNNER_CONTRACT",
        "INSTALL_PYTHON",
        "REPO_GREEN",
        "SEED_SUITE",
        "OPTIONAL_JAVA_BRIDGES",
        "TARGET_RADAR_BACKEND_MATRIX",
        "TARGET_RADAR_PROOF",
    ]
    env = _recording_override_env(log_path, lane_names)

    result = subprocess.run(
        ["bash", "scripts/ci/github_ci_local.sh"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert log_path.read_text(encoding="utf-8").splitlines() == lane_names


def test_github_ci_local_all_mode_runs_every_lane_family_in_order(tmp_path: Path) -> None:
    log_path = tmp_path / "lanes.log"
    lane_names = [
        "VENDOR_RUNNER_CONTRACT",
        "INSTALL_PYTHON",
        "REPO_GREEN",
        "SEED_SUITE",
        "OPTIONAL_JAVA_BRIDGES",
        "TARGET_RADAR_BACKEND_MATRIX",
        "TARGET_RADAR_PROOF",
        "INSTALL_PYTHON",
        "CERTI_RUNTIME_REQUIRED",
        "PITCH_RUNTIME_REQUIRED",
        "REAL_PROFILE_MATRIX_REQUIRED",
        "INSTALL_PYTHON",
        "VENDOR_EDGE_MATRIX_VALIDATE",
        "VENDOR_EDGE_TIME_QUERY",
        "VENDOR_EDGE_NEGOTIATED_OWNERSHIP",
        "VENDOR_EDGE_SAVE_RESTORE",
        "VENDOR_EDGE_DDM",
        "INSTALL_PYTHON",
        "VENDOR_PROBE_REVIEW_VALIDATE",
        "PROBE_REVIEW_CERTI_SAVE_RESTORE_PROBE",
        "PROBE_REVIEW_CERTI_DDM_PROBE",
        "PROBE_REVIEW_PITCH_SAVE_RESTORE_PROBE",
        "PROBE_REVIEW_PITCH_DDM_PROBE",
        "PROBE_REVIEW_PITCH_NEGOTIATED_PROBE",
        "PROBE_REVIEW_PITCH_LOST_FEDERATE_PROBE",
        "INSTALL_PYTHON",
        "VENDOR_SMOKE_VALIDATE_ALL",
        "VENDOR_SMOKE_ALL",
        "VENDOR_SMOKE_VALIDATE_CERTI_SAVE_RESTORE_PROBE",
        "VENDOR_SMOKE_CERTI_SAVE_RESTORE_PROBE",
        "VENDOR_SMOKE_VALIDATE_CERTI_DDM_PROBE",
        "VENDOR_SMOKE_CERTI_DDM_PROBE",
        "VENDOR_SMOKE_VALIDATE_PITCH_SAVE_RESTORE_PROBE",
        "VENDOR_SMOKE_PITCH_SAVE_RESTORE_PROBE",
        "VENDOR_SMOKE_VALIDATE_PITCH_DDM_PROBE",
        "VENDOR_SMOKE_PITCH_DDM_PROBE",
        "VENDOR_SMOKE_VALIDATE_PITCH_NEGOTIATED_PROBE",
        "VENDOR_SMOKE_PITCH_NEGOTIATED_PROBE",
        "VENDOR_SMOKE_VALIDATE_PITCH_LOST_FEDERATE_PROBE",
        "VENDOR_SMOKE_PITCH_LOST_FEDERATE_PROBE",
    ]
    env = _recording_override_env(log_path, lane_names)

    result = subprocess.run(
        ["bash", "scripts/ci/github_ci_local.sh", "all"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert log_path.read_text(encoding="utf-8").splitlines() == lane_names


def test_check_generated_docs_shell_bootstraps_source_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "ci" / "check_generated_docs.sh")],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr


def _write_delegate_script(path: Path, *, payloads: dict[str, dict[str, object]], exit_code: int) -> None:
    script = """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

payloads = PAYLOADS
artifact_dir = Path(os.environ["HLA2010_PREFLIGHT_ARTIFACT_DIR"])
artifact_dir.mkdir(parents=True, exist_ok=True)
for name, payload in payloads.items():
    (artifact_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
raise SystemExit(EXIT_CODE)
"""
    script = script.replace("PAYLOADS", repr(payloads)).replace("EXIT_CODE", str(exit_code))
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)


def _assert_status_packet(base_dir: Path, profile_dir: str) -> tuple[VendorRuntimeStatusSummary, Path, Path]:
    summary_path = base_dir / profile_dir / "vendor_runtime_status_summary.json"
    report_path = base_dir / profile_dir / "vendor_runtime_status_report.md"
    assert summary_path.exists()
    assert report_path.exists()
    return VendorRuntimeStatusSummary.from_mapping(json.loads(summary_path.read_text(encoding="utf-8"))), summary_path, report_path


def test_repo_green_emits_runtime_status_and_parity_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "repo_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={
            "certi-preflight.json": {
                "tool": "certi-preflight",
                "environment": "loopback-blocked",
                "result": "real CERTI will skip",
                "exit_code": 1,
            },
            "pitch-preflight.json": {
                "tool": "pitch-preflight",
                "environment": "docker-blocked",
                "result": "Pitch runtime is not ready",
                "exit_code": 1,
            },
        },
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_REPO_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "scripts/ci/repo_green.sh"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    runtime_summary = tmp_path / "runtime-status" / "repo_green" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert runtime_summary.exists()
    assert parity_summary.exists()
    runtime_payload = VendorRuntimeStatusSummary.from_mapping(json.loads(runtime_summary.read_text(encoding="utf-8")))
    assert runtime_payload.overall_classification == "repo-green"
    assert runtime_payload.lane == "repo-green"
    report_path = tmp_path / "runtime-status" / "repo_green" / "vendor_runtime_status_report.md"
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "# Vendor Runtime Status" in report_text
    assert "repo-green" in report_text


def test_tools_python_verify_delegates_to_repo_green_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "repo_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={
            "certi-preflight.json": {
                "tool": "certi-preflight",
                "environment": "loopback-blocked",
                "result": "real CERTI will skip",
                "exit_code": 1,
            },
            "pitch-preflight.json": {
                "tool": "pitch-preflight",
                "environment": "docker-blocked",
                "result": "Pitch runtime is not ready",
                "exit_code": 1,
            },
        },
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_REPO_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "tools/python", "verify"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    runtime_summary = tmp_path / "runtime-status" / "repo_green" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert runtime_summary.exists()
    assert parity_summary.exists()
    runtime_payload = VendorRuntimeStatusSummary.from_mapping(json.loads(runtime_summary.read_text(encoding="utf-8")))
    assert runtime_payload.overall_classification == "repo-green"
    assert runtime_payload.lane == "repo-green"


def test_tools_python_verify_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    delegate = tmp_path / "repo_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={
            "certi-preflight.json": {
                "tool": "certi-preflight",
                "environment": "loopback-blocked",
                "result": "real CERTI will skip",
                "exit_code": 1,
            },
            "pitch-preflight.json": {
                "tool": "pitch-preflight",
                "environment": "docker-blocked",
                "result": "Pitch runtime is not ready",
                "exit_code": 1,
            },
        },
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_REPO_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "python"), "verify"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    runtime_summary = tmp_path / "runtime-status" / "repo_green" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert runtime_summary.exists()
    assert parity_summary.exists()
    runtime_payload = VendorRuntimeStatusSummary.from_mapping(json.loads(runtime_summary.read_text(encoding="utf-8")))
    assert runtime_payload.overall_classification == "repo-green"
    assert runtime_payload.lane == "repo-green"


def test_tools_python_verify_routes_can_delegate(tmp_path: Path) -> None:
    delegate = tmp_path / "verify_routes_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={"verify-routes.json": {"tool": "python-verify-routes", "result": "ok"}},
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_PYTHON_VERIFY_ROUTES_DELEGATE"] = str(delegate)
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "artifacts")

    result = subprocess.run(
        ["bash", "tools/python", "verify-routes"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (tmp_path / "artifacts" / "verify-routes.json").exists()


def test_tools_python_verify_routes_bootstraps_workspace_pythonpath(tmp_path: Path) -> None:
    fake_python = tmp_path / "fake_python.py"
    log_path = tmp_path / "calls.jsonl"
    fake_python.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

log_path = Path(os.environ["HLA2010_TEST_LOG_PATH"])
argv = sys.argv[1:]
log_path.parent.mkdir(parents=True, exist_ok=True)
with log_path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({"argv": argv, "pythonpath": os.environ.get("PYTHONPATH", "")}) + "\\n")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    env = os.environ.copy()
    env["HLA2010_PYTHON_VERIFY_ROUTES_PYTHON"] = str(fake_python)
    env["HLA2010_TEST_LOG_PATH"] = str(log_path)

    result = subprocess.run(
        ["bash", "tools/python", "verify-routes"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    calls = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert len(calls) == 5
    expected_suffixes = [
        ["-m", "pytest", "-q", "tests/scenarios/test_python_route_parity.py"],
        ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_python_server.py"],
        ["scripts/run_python_route_parity_matrix.py"],
        ["examples/target_radar_simulation.py", "--backend", "python", "--steps", "5"],
        ["examples/target_radar_simulation.py", "--backend", "python-grpc", "--steps", "5"],
    ]
    for call, expected_argv in zip(calls, expected_suffixes, strict=True):
        assert call["argv"] == expected_argv
        pythonpath = call["pythonpath"]
        assert str(ROOT / "packages/hla-rti1516e/src") in pythonpath
        assert str(ROOT / "packages/hla-fom-target-radar/src") in pythonpath
        assert str(ROOT / "packages/hla-transport-grpc/src") in pythonpath


def test_tools_python_verify_routes_preflight_can_delegate(tmp_path: Path) -> None:
    delegate = tmp_path / "verify_routes_preflight_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={"verify-routes-preflight.json": {"tool": "python-verify-routes-preflight", "result": "ok"}},
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_PYTHON_VERIFY_ROUTES_PREFLIGHT_DELEGATE"] = str(delegate)
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "artifacts")

    result = subprocess.run(
        ["bash", "tools/python", "verify-routes-preflight"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (tmp_path / "artifacts" / "verify-routes-preflight.json").exists()


def test_vendor_green_emits_runtime_status_and_preserves_delegate_failure(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={
            "pitch-preflight.json": {
                "tool": "pitch-preflight",
                "environment": "docker-blocked",
                "result": "Pitch runtime is not ready",
                "exit_code": 1,
            }
        },
        exit_code=7,
    )
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE"] = "0"
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 7
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_pitch" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert runtime_summary.exists()
    assert parity_summary.exists()
    runtime_payload = VendorRuntimeStatusSummary.from_mapping(json.loads(runtime_summary.read_text(encoding="utf-8")))
    assert runtime_payload.overall_classification == "environment-blocked"
    assert runtime_payload.lane == "vendor-green"
    report_path = tmp_path / "runtime-status" / "vendor_green_pitch" / "vendor_runtime_status_report.md"
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "# Vendor Runtime Status" in report_text
    assert "vendor-green" in report_text
    assert "pitch" in report_text


def test_vendor_green_ci_auto_validation_blocks_delegate_on_invalid_runtime_state(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_delegate.py"
    _write_vendor_edge_delegate(delegate)
    env = os.environ.copy()
    for name in (
        "HLA2010_PITCH_HOME",
        "HLA2010_PITCH_USER_HOME",
        "HLA2010_CERTI_PREFIX",
        "HLA2010_CERTI_BUILD_ROOT",
        "HLA2010_CERTI_PATCHED_PREFIX",
        "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        "HLA2010_CERTI_UPSTREAM_PREFIX",
        "HLA2010_CERTI_UPSTREAM_BUILD_ROOT",
    ):
        env.pop(name, None)
    env["GITHUB_ACTIONS"] = "true"
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_CI_STATE_DIR"] = str(tmp_path / "runtime-ci-state")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert not (tmp_path / "record.json").exists()
    summary_path = tmp_path / "runtime-ci-state" / "pitch" / "vendor_runtime_ci_state_summary.json"
    assert summary_path.exists()
    payload = VendorRuntimeCiStateSummary.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert payload.profile == "pitch"
    assert payload.classification == "invalid-runtime-state"


def test_vendor_green_ci_auto_validation_allows_delegate_with_valid_runtime_state(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_delegate.py"
    _write_vendor_edge_delegate(delegate)
    pitch_home = tmp_path / "pitch-home"
    pitch_user_home = tmp_path / "pitch-user-home"
    (pitch_home / "lib").mkdir(parents=True)
    (pitch_home / "lib" / "prtifull.jar").write_text("", encoding="utf-8")
    pitch_user_home.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["GITHUB_ACTIONS"] = "true"
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_PITCH_HOME"] = str(pitch_home)
    env["HLA2010_PITCH_USER_HOME"] = str(pitch_user_home)
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_CI_STATE_DIR"] = str(tmp_path / "runtime-ci-state")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = [
        RecordedArgvCall.from_mapping(row)
        for row in json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    ]
    assert payload == [RecordedArgvCall(argv=("pitch",))]
    summary_path = tmp_path / "runtime-ci-state" / "pitch" / "vendor_runtime_ci_state_summary.json"
    assert summary_path.exists()
    summary = VendorRuntimeCiStateSummary.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert summary.classification == "ready"


def test_vendor_green_pitch_smoke_uses_profile_named_status_directory(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={},
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE"] = "0"
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch-smoke"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    runtime_payload, _, report_path = _assert_status_packet(tmp_path / "runtime-status", "vendor_green_pitch_smoke")
    assert runtime_payload.lane == "vendor-green"
    assert runtime_payload.overall_classification == "missing-artifact"
    assert "pitch" in report_path.read_text(encoding="utf-8")


def test_vendor_green_certi_ddm_probe_uses_profile_named_status_directory(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={},
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE"] = "0"
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "certi-ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    runtime_payload, _, report_path = _assert_status_packet(tmp_path / "runtime-status", "vendor_green_certi_ddm_probe")
    assert runtime_payload.lane == "vendor-green"
    assert runtime_payload.overall_classification == "missing-artifact"
    assert "certi" in report_path.read_text(encoding="utf-8")


def _write_vendor_edge_delegate(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
payload = {"argv": sys.argv[1:]}
record_path.parent.mkdir(parents=True, exist_ok=True)
existing = []
if record_path.exists():
    existing = json.loads(record_path.read_text(encoding="utf-8"))
existing.append(payload)
record_path.write_text(json.dumps(existing, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _write_compliance_generator_stub(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
existing = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
existing.append({"argv": ["generate-compliance-artifacts"]})
record_path.write_text(json.dumps(existing, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_vendor_edge_negotiated_ownership_uses_explicit_probe_profiles(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    generator = tmp_path / "generate_compliance_artifacts_stub.py"
    _write_vendor_edge_delegate(delegate)
    _write_compliance_generator_stub(generator)
    env = os.environ.copy()
    env["HLA2010_VENDOR_EDGE_VENDOR_GREEN"] = str(delegate)
    env["HLA2010_VENDOR_EDGE_COMPLIANCE_GENERATOR"] = f"python3 {generator}"
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_edge_matrix.sh", "negotiated-ownership"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = [
        RecordedArgvCall.from_mapping(row)
        for row in json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    ]
    assert payload == [
        RecordedArgvCall(argv=("certi-compare",)),
        RecordedArgvCall(argv=("pitch-negotiated-probe",)),
        RecordedArgvCall(argv=("generate-compliance-artifacts",)),
    ]


def test_vendor_edge_all_runs_all_explicit_probe_profiles(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    generator = tmp_path / "generate_compliance_artifacts_stub.py"
    _write_vendor_edge_delegate(delegate)
    _write_compliance_generator_stub(generator)
    env = os.environ.copy()
    env["HLA2010_VENDOR_EDGE_VENDOR_GREEN"] = str(delegate)
    env["HLA2010_VENDOR_EDGE_COMPLIANCE_GENERATOR"] = f"python3 {generator}"
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_edge_matrix.sh", "all"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = [
        RecordedArgvCall.from_mapping(row)
        for row in json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    ]
    assert payload == [
        RecordedArgvCall(argv=("certi-compare",)),
        RecordedArgvCall(argv=("pitch-smoke",)),
        RecordedArgvCall(argv=("certi-compare",)),
        RecordedArgvCall(argv=("pitch-negotiated-probe",)),
        RecordedArgvCall(argv=("certi-save-restore-probe",)),
        RecordedArgvCall(argv=("pitch-save-restore-probe",)),
        RecordedArgvCall(argv=("certi-ddm-probe",)),
        RecordedArgvCall(argv=("pitch-ddm-probe",)),
        RecordedArgvCall(argv=("generate-compliance-artifacts",)),
    ]
