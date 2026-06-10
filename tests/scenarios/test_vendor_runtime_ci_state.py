from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from hla2010_repo_internal.verification.vendor_runtime_ci_state import (
    build_vendor_runtime_ci_state,
    vendor_runtime_ci_profiles,
    vendor_runtime_ci_profile_spec,
    write_vendor_runtime_ci_state,
)


ROOT = Path(__file__).resolve().parents[2]


def test_certi_ci_state_requires_explicit_patched_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HLA2010_CERTI_PATCHED_PREFIX", str(tmp_path / "patched-prefix"))
    monkeypatch.setenv("HLA2010_CERTI_PATCHED_BUILD_ROOT", str(tmp_path / "patched-build"))

    summary = build_vendor_runtime_ci_state("certi")

    assert summary["classification"] == "invalid-runtime-state"
    assert summary["required_vars"] == [
        "HLA2010_CERTI_PATCHED_PREFIX",
        "HLA2010_CERTI_PATCHED_BUILD_ROOT",
    ]
    assert summary["compatibility_vars"]["HLA2010_CERTI_PREFIX"] == "HLA2010_CERTI_PATCHED_PREFIX"
    assert summary["checks"][0]["name"] == "certi-patched-prefix"
    assert summary["checks"][0]["ok"] is False
    assert "HLA2010_CERTI_PATCHED_PREFIX" in summary["checks"][0]["detail"]


def test_ci_state_profile_inventory_matches_expected_profiles() -> None:
    assert vendor_runtime_ci_profiles() == ("certi", "pitch", "matrix", "vendor-edge", "all")
    assert vendor_runtime_ci_profile_spec("vendor-edge")["required_vars"] == (
        "HLA2010_CERTI_PATCHED_PREFIX",
        "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        "HLA2010_CERTI_UPSTREAM_PREFIX",
        "HLA2010_CERTI_UPSTREAM_BUILD_ROOT",
        "HLA2010_PITCH_HOME",
        "HLA2010_PITCH_USER_HOME",
    )


def test_matrix_ci_state_is_ready_when_all_required_markers_exist(monkeypatch, tmp_path: Path) -> None:
    patched_prefix = tmp_path / "patched-prefix"
    patched_build = tmp_path / "patched-build"
    upstream_prefix = tmp_path / "upstream-prefix"
    upstream_build = tmp_path / "upstream-build"
    pitch_home = tmp_path / "pitch-home"
    pitch_user_home = tmp_path / "pitch-user-home"
    for prefix in (patched_prefix, upstream_prefix):
        (prefix / "bin").mkdir(parents=True)
        (prefix / "bin" / "rtig").write_text("")
    for build_root in (patched_build, upstream_build):
        (build_root / "libRTI" / "ieee1516-2010").mkdir(parents=True)
    (pitch_home / "lib").mkdir(parents=True)
    (pitch_home / "lib" / "prtifull.jar").write_text("")
    pitch_user_home.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("HLA2010_CERTI_PATCHED_PREFIX", str(patched_prefix))
    monkeypatch.setenv("HLA2010_CERTI_PATCHED_BUILD_ROOT", str(patched_build))
    monkeypatch.setenv("HLA2010_CERTI_UPSTREAM_PREFIX", str(upstream_prefix))
    monkeypatch.setenv("HLA2010_CERTI_UPSTREAM_BUILD_ROOT", str(upstream_build))
    monkeypatch.setenv("HLA2010_PITCH_HOME", str(pitch_home))
    monkeypatch.setenv("HLA2010_PITCH_USER_HOME", str(pitch_user_home))

    summary = build_vendor_runtime_ci_state("matrix")

    assert summary["classification"] == "ready"
    assert summary["exit_code"] == 0
    assert all(check["ok"] for check in summary["checks"])


def test_write_vendor_runtime_ci_state_emits_artifacts(monkeypatch, tmp_path: Path) -> None:
    pitch_home = tmp_path / "pitch-home"
    pitch_user_home = tmp_path / "pitch-user-home"
    (pitch_home / "lib").mkdir(parents=True)
    (pitch_home / "lib" / "prtifull.jar").write_text("")
    pitch_user_home.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HLA2010_PITCH_HOME", str(pitch_home))
    monkeypatch.setenv("HLA2010_PITCH_USER_HOME", str(pitch_user_home))

    paths = write_vendor_runtime_ci_state(tmp_path / "state", profile="pitch")

    payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch"
    assert payload["classification"] == "ready"
    assert payload["required_markers"] == ["${HLA2010_PITCH_HOME}/lib/prtifull.jar"]
    report = paths.report_markdown.read_text(encoding="utf-8")
    assert "Vendor Runtime CI State" in report
    assert "## Contract" in report
    assert "Required markers:" in report
    assert "pitch-home" in report


def test_ci_state_script_returns_nonzero_for_missing_runtime_state(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            "scripts/ci/check_vendor_runtime_ci_state.py",
            "--profile",
            "all",
            "--output-dir",
            str(tmp_path / "state"),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["classification"] == "invalid-runtime-state"


def test_ci_state_script_writes_profile_specific_output_directory(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            "scripts/ci/check_vendor_runtime_ci_state.py",
            "--profile",
            "vendor-edge",
            "--output-dir",
            str(tmp_path / "state"),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )

    assert result.returncode == 1
    summary_path = tmp_path / "state" / "vendor_edge" / "vendor_runtime_ci_state_summary.json"
    report_path = tmp_path / "state" / "vendor_edge" / "vendor_runtime_ci_state_report.md"
    assert summary_path.exists()
    assert report_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["profile"] == "vendor-edge"
