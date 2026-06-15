from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest
from tests.typed_json_models import (
    LabeledRecordedCall,
    PitchPreflightOutput,
    RecordedProfile,
    VendorParityArtifactsSummary,
    VendorRuntimeStatusSummary,
)


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class VendorGreenProfileCase:
    name: str
    command: tuple[str, ...]
    profile: str
    bundle: str
    classification: str
    env_factory: Callable[[Path], dict[str, str]]


@dataclass(frozen=True)
class PreflightBlockedCase:
    name: str
    command: tuple[str, ...]
    returncode: int | str
    preflight_file: str
    preflight_tool: str
    bundle: str


def _base_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")
    env["HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE"] = "0"
    env["HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE"] = "0"
    env["HLA2010_CERTI_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(tmp_path / "missing-certi-upstream-prefix")
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(tmp_path / "missing-certi-upstream-build")
    env["HLA2010_PITCH_HOME"] = str(tmp_path / "missing-pitch-home")
    env["PATH"] = os.environ.get("PATH", os.defpath)
    return env


def _assert_report_bundle(tmp_path: Path, profile_dir: str) -> tuple[Path, Path]:
    runtime_summary = tmp_path / "runtime-status" / profile_dir / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert runtime_summary.exists()
    assert parity_summary.exists()
    return runtime_summary, parity_summary


def _make_certi_runnable_env(tmp_path: Path) -> dict[str, str]:
    env = _base_env(tmp_path)
    patched_prefix = tmp_path / "certi-patched-prefix"
    patched_build = tmp_path / "certi-patched-build"
    upstream_prefix = tmp_path / "certi-upstream-prefix"
    upstream_build = tmp_path / "certi-upstream-build"
    for prefix in (patched_prefix, upstream_prefix):
        (prefix / "bin").mkdir(parents=True, exist_ok=True)
        (prefix / "bin" / "rtig").write_text("", encoding="utf-8")
    for build_root in (patched_build, upstream_build):
        (build_root / "libRTI" / "ieee1516-2010").mkdir(parents=True, exist_ok=True)
    env["HLA2010_CERTI_PREFIX"] = str(patched_prefix)
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(patched_prefix)
    env["HLA2010_CERTI_BUILD_ROOT"] = str(patched_build)
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(patched_build)
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(upstream_prefix)
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(upstream_build)
    env["HLA2010_CERTI_PREFLIGHT_ASSUME_LOOPBACK_OK"] = "1"
    return env


def _run_tool(tmp_path: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", *args],
        cwd=ROOT,
        env=env or _base_env(tmp_path),
        capture_output=True,
        text=True,
        check=False,
    )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_parity_suite(parity_summary: Path) -> None:
    payload = VendorParityArtifactsSummary.from_mapping(_load_json(parity_summary))
    assert payload.suite_name == "vendor-parity-artifacts"


def _assert_runtime_classification(runtime_summary: Path, expected: str | set[str]) -> None:
    status_payload = VendorRuntimeStatusSummary.from_mapping(_load_json(runtime_summary))
    if isinstance(expected, str):
        assert status_payload.overall_classification == expected
    else:
        assert status_payload.overall_classification in expected


def _assert_preflight_payload(tmp_path: Path, filename: str, tool_name: str) -> None:
    artifact_path = tmp_path / "preflight" / filename
    assert artifact_path.exists()
    assert _load_json(artifact_path)["tool"] == tool_name


def _assert_recorded_profile(tmp_path: Path, expected_profile: str) -> None:
    payload = RecordedProfile.from_mapping(_load_json(tmp_path / "record" / "profile.json"))
    assert payload.profile == expected_profile


def test_certi_easy_preflight_writes_default_artifact_and_reports(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "./tools/certi-easy", "preflight"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    runtime_summary = tmp_path / "runtime-status" / "vendor_green_certi" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert runtime_summary.exists()
    assert parity_summary.exists()
    status_payload = VendorRuntimeStatusSummary.from_mapping(json.loads(runtime_summary.read_text(encoding="utf-8")))
    assert status_payload.overall_classification in {
        "ready",
        "environment-blocked",
        "missing-artifact",
        "unexpected-preflight-failure",
    }
    artifact_text = result.stdout + result.stderr
    assert "CERTI preflight" in artifact_text


def test_pitch_preflight_writes_default_artifact_and_reports(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "./tools/pitch", "preflight"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_pitch" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert artifact_path.exists()
    assert runtime_summary.exists()
    assert parity_summary.exists()
    payload = PitchPreflightOutput.from_mapping(json.loads(artifact_path.read_text(encoding="utf-8")))
    assert payload.tool == "pitch-preflight"
    status_payload = VendorRuntimeStatusSummary.from_mapping(json.loads(runtime_summary.read_text(encoding="utf-8")))
    assert status_payload.overall_classification in {
        "ready",
        "vendor-green",
        "environment-blocked",
        "unexpected-preflight-failure",
    }


def test_vendor_report_scripts_bootstrap_source_checkout(tmp_path: Path) -> None:
    preflight_dir = tmp_path / "preflight"
    preflight_dir.mkdir()
    (preflight_dir / "certi-preflight.json").write_text(
        json.dumps(
            {
                "tool": "certi-preflight",
                "environment": "ready",
                "result": "ok",
                "checks": [],
                "next_steps": [],
            }
        ),
        encoding="utf-8",
    )
    runtime_dir = tmp_path / "runtime-status"
    parity_dir = tmp_path / "parity"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "classify_vendor_runtime.py"),
            "--project-root",
            str(ROOT),
            "--artifact-dir",
            str(preflight_dir),
            "--output-dir",
            str(runtime_dir),
            "--lane",
            "vendor-green",
            "--vendor",
            "certi",
            "--json",
        ],
        cwd=tmp_path,
        env=_base_env(tmp_path),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = VendorRuntimeStatusSummary.from_mapping(json.loads(result.stdout))
    assert result.returncode == int(payload.exit_code or 0)
    assert payload.suite_name == "vendor-runtime-status"
    assert (runtime_dir / "vendor_runtime_status_summary.json").exists()

    parity = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_vendor_parity_artifacts.py"),
            "--project-root",
            str(ROOT),
            "--output-dir",
            str(parity_dir),
        ],
        cwd=tmp_path,
        env=_base_env(tmp_path),
        capture_output=True,
        text=True,
        check=False,
    )
    assert parity.returncode == 0
    assert (parity_dir / "vendor_parity_artifacts_summary.json").exists()


def _write_vendor_green_delegate(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

profile = sys.argv[1]
out_dir = Path(os.environ["HLA2010_TEST_RECORD_DIR"])
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "profile.json").write_text(json.dumps({"profile": profile}) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _write_probe_review_recorder(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

label = sys.argv[1]
payload = {"label": label, "argv": sys.argv[2:]}
record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
record_path.parent.mkdir(parents=True, exist_ok=True)
rows = []
if record_path.exists():
    rows = json.loads(record_path.read_text(encoding="utf-8"))
rows.append(payload)
record_path.write_text(json.dumps(rows, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_pitch_smoke_uses_vendor_green_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = _run_tool(tmp_path, "./tools/pitch", "smoke", env=env)

    assert result.returncode == 0
    _assert_recorded_profile(tmp_path, "pitch-smoke")
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_smoke")
    _assert_runtime_classification(runtime_summary, "missing-artifact")
    _assert_parity_suite(parity_summary)


def test_certi_ddm_review_uses_probe_review_wrapper(tmp_path: Path) -> None:
    recorder = tmp_path / "probe_review_recorder.py"
    _write_probe_review_recorder(recorder)
    env = _base_env(tmp_path)
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record" / "rows.json")
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = str(recorder)
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f"python3 {recorder} promotion"
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f"python3 {recorder} parity"

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "ddm-review", "7"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    rows = [
        LabeledRecordedCall.from_mapping(row)
        for row in json.loads((tmp_path / "record" / "rows.json").read_text(encoding="utf-8"))
    ]
    assert rows == [
        LabeledRecordedCall(label="certi-ddm-probe", argv=("7",)),
        LabeledRecordedCall(label="promotion", argv=()),
        LabeledRecordedCall(label="parity", argv=()),
    ]


def test_pitch_negotiated_review_uses_probe_review_wrapper(tmp_path: Path) -> None:
    recorder = tmp_path / "probe_review_recorder.py"
    _write_probe_review_recorder(recorder)
    env = _base_env(tmp_path)
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record" / "rows.json")
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = str(recorder)
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f"python3 {recorder} promotion"
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f"python3 {recorder} parity"

    result = subprocess.run(
        ["bash", "./tools/pitch", "negotiated-review", "7"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    rows = [
        LabeledRecordedCall.from_mapping(row)
        for row in json.loads((tmp_path / "record" / "rows.json").read_text(encoding="utf-8"))
    ]
    assert rows == [
        LabeledRecordedCall(label="pitch-negotiated-probe", argv=("7",)),
        LabeledRecordedCall(label="promotion", argv=()),
        LabeledRecordedCall(label="parity", argv=()),
    ]

VENDOR_GREEN_PROFILE_CASES = [
    {
        "name": "pitch_smoke",
        "command": ("./tools/pitch", "smoke"),
        "profile": "pitch-smoke",
        "bundle": "vendor_green_pitch_smoke",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "certi_smoke_compare",
        "command": ("./tools/certi-easy", "smoke", "compare"),
        "profile": "certi-compare",
        "bundle": "vendor_green_certi_compare",
        "classification": "vendor-green",
        "env_factory": _make_certi_runnable_env,
    },
    {
        "name": "certi_smoke_patched",
        "command": ("./tools/certi-easy", "smoke", "patched"),
        "profile": "certi-patched",
        "bundle": "vendor_green_certi_patched",
        "classification": "vendor-green",
        "env_factory": _make_certi_runnable_env,
    },
    {
        "name": "certi_smoke_upstream",
        "command": ("./tools/certi-easy", "smoke", "upstream"),
        "profile": "certi-upstream",
        "bundle": "vendor_green_certi_upstream",
        "classification": "vendor-green",
        "env_factory": _make_certi_runnable_env,
    },
    {
        "name": "pitch_verify",
        "command": ("./tools/pitch", "verify"),
        "profile": "pitch-verify",
        "bundle": "vendor_green_pitch_verify",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "certi_save_restore_probe",
        "command": ("./tools/certi-easy", "save-restore-probe"),
        "profile": "certi-save-restore-probe",
        "bundle": "vendor_green_certi_save_restore_probe",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "pitch_save_restore_probe",
        "command": ("./tools/pitch", "save-restore-probe"),
        "profile": "pitch-save-restore-probe",
        "bundle": "vendor_green_pitch_save_restore_probe",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "certi_ddm_probe",
        "command": ("./tools/certi-easy", "ddm-probe"),
        "profile": "certi-ddm-probe",
        "bundle": "vendor_green_certi_ddm_probe",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "pitch_ddm_probe",
        "command": ("./tools/pitch", "ddm-probe"),
        "profile": "pitch-ddm-probe",
        "bundle": "vendor_green_pitch_ddm_probe",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "pitch_negotiated_probe",
        "command": ("./tools/pitch", "negotiated-probe"),
        "profile": "pitch-negotiated-probe",
        "bundle": "vendor_green_pitch_negotiated_probe",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
    {
        "name": "pitch_lost_federate_probe",
        "command": ("./tools/pitch", "lost-federate-probe"),
        "profile": "pitch-lost-federate-probe",
        "bundle": "vendor_green_pitch_lost_federate_probe",
        "classification": "missing-artifact",
        "env_factory": _base_env,
    },
]


VENDOR_GREEN_PROFILE_CASES = [
    VendorGreenProfileCase(
        name=case["name"],
        command=case["command"],
        profile=case["profile"],
        bundle=case["bundle"],
        classification=case["classification"],
        env_factory=case["env_factory"],
    )
    for case in VENDOR_GREEN_PROFILE_CASES
]


@pytest.mark.parametrize("case", VENDOR_GREEN_PROFILE_CASES, ids=lambda case: case.name)
def test_vendor_green_commands_use_expected_profiles_and_emit_reports(
    tmp_path: Path, case: VendorGreenProfileCase
) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = case.env_factory(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = _run_tool(tmp_path, *case.command, env=env)

    assert result.returncode == 0
    _assert_recorded_profile(tmp_path, case.profile)
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, case.bundle)
    _assert_runtime_classification(runtime_summary, case.classification)
    _assert_parity_suite(parity_summary)


PREFLIGHT_BLOCKED_CASES = [
    {
        "name": "certi_smoke_compare",
        "command": ("./tools/certi-easy", "smoke", "compare"),
        "returncode": "nonzero",
        "preflight_file": "certi-preflight.json",
        "preflight_tool": "certi-preflight",
        "bundle": "vendor_green_certi_compare",
    },
    {
        "name": "certi_verify_best_effort",
        "command": ("./tools/certi-easy", "verify-best-effort"),
        "returncode": 0,
        "preflight_file": "certi-preflight.json",
        "preflight_tool": "certi-preflight",
        "bundle": "vendor_green_certi_compare",
    },
    {
        "name": "pitch_smoke",
        "command": ("./tools/pitch", "smoke"),
        "returncode": "any",
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_smoke",
    },
    {
        "name": "pitch_verify",
        "command": ("./tools/pitch", "verify"),
        "returncode": "nonzero",
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_verify",
    },
    {
        "name": "pitch_verify_best_effort",
        "command": ("./tools/pitch", "verify-best-effort"),
        "returncode": 0,
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_verify",
    },
    {
        "name": "certi_save_restore",
        "command": ("./tools/certi-easy", "save-restore"),
        "returncode": "nonzero",
        "preflight_file": "certi-preflight.json",
        "preflight_tool": "certi-preflight",
        "bundle": "vendor_green_certi_save_restore",
    },
    {
        "name": "pitch_save_restore",
        "command": ("./tools/pitch", "save-restore"),
        "returncode": "nonzero",
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_save_restore",
    },
    {
        "name": "certi_ddm",
        "command": ("./tools/certi-easy", "ddm"),
        "returncode": "nonzero",
        "preflight_file": "certi-preflight.json",
        "preflight_tool": "certi-preflight",
        "bundle": "vendor_green_certi_ddm",
    },
    {
        "name": "pitch_ddm",
        "command": ("./tools/pitch", "ddm"),
        "returncode": "nonzero",
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_ddm",
    },
    {
        "name": "pitch_negotiated",
        "command": ("./tools/pitch", "negotiated"),
        "returncode": "nonzero",
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_negotiated",
    },
    {
        "name": "pitch_lost_federate",
        "command": ("./tools/pitch", "lost-federate"),
        "returncode": "nonzero",
        "preflight_file": "pitch-preflight.json",
        "preflight_tool": "pitch-preflight",
        "bundle": "vendor_green_pitch_lost_federate",
    },
]


PREFLIGHT_BLOCKED_CASES = [
    PreflightBlockedCase(
        name=case["name"],
        command=case["command"],
        returncode=case["returncode"],
        preflight_file=case["preflight_file"],
        preflight_tool=case["preflight_tool"],
        bundle=case["bundle"],
    )
    for case in PREFLIGHT_BLOCKED_CASES
]


@pytest.mark.parametrize("case", PREFLIGHT_BLOCKED_CASES, ids=lambda case: case.name)
def test_preflight_blocked_commands_still_emit_reports(tmp_path: Path, case: PreflightBlockedCase) -> None:
    result = _run_tool(tmp_path, *case.command)

    if case.returncode == "nonzero":
        assert result.returncode != 0
    elif case.returncode == "any":
        assert isinstance(result.returncode, int)
    else:
        assert result.returncode == case.returncode
    _assert_preflight_payload(tmp_path, case.preflight_file, case.preflight_tool)
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, case.bundle)
    _assert_runtime_classification(
        runtime_summary,
        {"environment-blocked", "unexpected-preflight-failure"},
    )
    _assert_parity_suite(parity_summary)
