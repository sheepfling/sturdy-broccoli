from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


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


def _assert_status_packet(base_dir: Path, profile_dir: str) -> tuple[dict[str, object], Path, Path]:
    summary_path = base_dir / profile_dir / "vendor_runtime_status_summary.json"
    report_path = base_dir / profile_dir / "vendor_runtime_status_report.md"
    assert summary_path.exists()
    assert report_path.exists()
    return json.loads(summary_path.read_text(encoding="utf-8")), summary_path, report_path


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
    runtime_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert runtime_payload["overall_classification"] == "repo-green"
    assert runtime_payload["lane"] == "repo-green"
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
    runtime_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert runtime_payload["overall_classification"] == "repo-green"
    assert runtime_payload["lane"] == "repo-green"


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
    runtime_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert runtime_payload["overall_classification"] == "repo-green"
    assert runtime_payload["lane"] == "repo-green"


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
    runtime_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert runtime_payload["overall_classification"] == "environment-blocked"
    assert runtime_payload["lane"] == "vendor-green"
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
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch"
    assert payload["classification"] == "invalid-runtime-state"


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
    payload = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert payload == [{"argv": ["pitch"]}]
    summary_path = tmp_path / "runtime-ci-state" / "pitch" / "vendor_runtime_ci_state_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["classification"] == "ready"


def test_vendor_green_pitch_smoke_uses_profile_named_status_directory(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_delegate.py"
    _write_delegate_script(
        delegate,
        payloads={},
        exit_code=0,
    )
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
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
    assert runtime_payload["lane"] == "vendor-green"
    assert runtime_payload["overall_classification"] == "missing-artifact"
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
    assert runtime_payload["lane"] == "vendor-green"
    assert runtime_payload["overall_classification"] == "missing-artifact"
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
    payload = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert payload == [
        {"argv": ["certi-compare"]},
        {"argv": ["pitch-negotiated-probe"]},
        {"argv": ["generate-compliance-artifacts"]},
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
    payload = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert payload == [
        {"argv": ["certi-compare"]},
        {"argv": ["pitch-smoke"]},
        {"argv": ["certi-compare"]},
        {"argv": ["pitch-negotiated-probe"]},
        {"argv": ["certi-save-restore-probe"]},
        {"argv": ["pitch-save-restore-probe"]},
        {"argv": ["certi-ddm-probe"]},
        {"argv": ["pitch-ddm-probe"]},
        {"argv": ["generate-compliance-artifacts"]},
    ]
