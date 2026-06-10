from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _base_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")
    env["HLA2010_CERTI_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(tmp_path / "missing-certi-upstream-prefix")
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(tmp_path / "missing-certi-upstream-build")
    env["HLA2010_PITCH_HOME"] = str(tmp_path / "missing-pitch-home")
    env["PATH"] = "/usr/bin:/bin"
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

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_certi" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert artifact_path.exists()
    assert runtime_summary.exists()
    assert parity_summary.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}


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

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_pitch" / "vendor_runtime_status_summary.json"
    parity_summary = tmp_path / "parity" / "vendor_parity_artifacts_summary.json"
    assert artifact_path.exists()
    assert runtime_summary.exists()
    assert parity_summary.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}


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

    result = subprocess.run(
        ["bash", "./tools/pitch", "smoke"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-smoke"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_smoke")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_smoke_compare_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _make_certi_runnable_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "smoke", "compare"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-compare"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_compare")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "vendor-green"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_smoke_patched_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _make_certi_runnable_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "smoke", "patched"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-patched"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_patched")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "vendor-green"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_smoke_upstream_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _make_certi_runnable_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "smoke", "upstream"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-upstream"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_upstream")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "vendor-green"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_verify_uses_vendor_green_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "verify"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-verify"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_verify")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


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
    rows = json.loads((tmp_path / "record" / "rows.json").read_text(encoding="utf-8"))
    assert rows == [
        {"label": "certi-ddm-probe", "argv": ["7"]},
        {"label": "promotion", "argv": []},
        {"label": "parity", "argv": []},
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
    rows = json.loads((tmp_path / "record" / "rows.json").read_text(encoding="utf-8"))
    assert rows == [
        {"label": "pitch-negotiated-probe", "argv": ["7"]},
        {"label": "promotion", "argv": []},
        {"label": "parity", "argv": []},
    ]


def test_certi_smoke_compare_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "smoke", "compare"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_compare")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_smoke_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/pitch", "smoke"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_smoke")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_verify_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/pitch", "verify"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_verify")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_save_restore_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "save-restore"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_save_restore")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_save_restore_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/pitch", "save-restore"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_save_restore")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_save_restore_probe_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "save-restore-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-save-restore-probe"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_save_restore_probe")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_save_restore_probe_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "save-restore-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-save-restore-probe"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_save_restore_probe")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_easy_ddm_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "ddm"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_ddm")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_ddm_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/pitch", "ddm"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_ddm")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_negotiated_writes_reports_when_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/pitch", "negotiated"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_negotiated")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] in {"environment-blocked", "unexpected-preflight-failure"}
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_certi_ddm_probe_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-ddm-probe"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_certi_ddm_probe")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_ddm_probe_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-ddm-probe"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_ddm_probe")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"


def test_pitch_negotiated_probe_uses_vendor_green_profile_and_emits_reports(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "negotiated-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-negotiated-probe"
    runtime_summary, parity_summary = _assert_report_bundle(tmp_path, "vendor_green_pitch_negotiated_probe")
    status_payload = json.loads(runtime_summary.read_text(encoding="utf-8"))
    assert status_payload["overall_classification"] == "missing-artifact"
    assert json.loads(parity_summary.read_text(encoding="utf-8"))["suite_name"] == "vendor-parity-artifacts"
