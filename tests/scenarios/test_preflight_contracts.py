from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from tests.typed_json_models import CertiPreflightOutput, PitchPreflightOutput


ROOT = Path(__file__).resolve().parents[2]
def _fake_docker_bin(tmp_path: Path) -> Path:
    docker = tmp_path / "docker"
    docker.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  info)
    exit 0
    ;;
  ps)
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    return docker


def test_certi_preflight_reports_missing_active_build_root_marker(tmp_path: Path) -> None:
    prefix = tmp_path / "certi-prefix"
    build_root = tmp_path / "certi-build"
    (prefix / "bin").mkdir(parents=True, exist_ok=True)
    (prefix / "bin" / "rtig").write_text("", encoding="utf-8")
    build_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["HLA2010_CERTI_PREFIX"] = str(prefix)
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(prefix)
    env["HLA2010_CERTI_BUILD_ROOT"] = str(build_root)
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(build_root)
    env["HLA2010_CERTI_SOURCE"] = str(ROOT / "CERTI")
    result = subprocess.run(
        [sys.executable, "scripts/check_certi_preflight.py", "--json"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = CertiPreflightOutput.from_mapping(json.loads(result.stdout))
    assert payload.check("active_prefix").ok is True
    assert payload.check("active_build_root").ok is False
    assert "libRTI/ieee1516-2010" in payload.check("active_build_root").message
    assert payload.runtime_profiles.active.build_root.marker_exists is False
    assert payload.required_markers["active_build_root"].endswith("/libRTI/ieee1516-2010")


def test_certi_preflight_shell_json_path_bootstraps_source_checkout(tmp_path: Path) -> None:
    prefix = tmp_path / "certi-prefix"
    build_root = tmp_path / "certi-build"
    (prefix / "bin").mkdir(parents=True, exist_ok=True)
    (prefix / "bin" / "rtig").write_text("", encoding="utf-8")
    build_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["HLA2010_CERTI_PREFIX"] = str(prefix)
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(prefix)
    env["HLA2010_CERTI_BUILD_ROOT"] = str(build_root)
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(build_root)
    env["HLA2010_CERTI_SOURCE"] = str(ROOT / "CERTI")
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        ["bash", "scripts/check_certi_preflight.sh", "--json"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = CertiPreflightOutput.from_mapping(json.loads(result.stdout))
    assert payload.check("active_prefix").ok is True
    assert payload.check("active_build_root").ok is False
    assert "libRTI/ieee1516-2010" in payload.check("active_build_root").message


def test_pitch_preflight_requires_prtifull_marker_in_runtime_home(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    _fake_docker_bin(fake_bin)
    pitch_home = tmp_path / "pitch-home"
    pitch_home.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["HLA2010_PITCH_HOME"] = str(pitch_home)

    result = subprocess.run(
        ["bash", "scripts/check_pitch_preflight.sh", "--json"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = PitchPreflightOutput.from_mapping(json.loads(result.stdout))
    assert payload.check("docker").ok is True
    assert payload.check("pitch_bundle").ok is False
    assert "prtifull.jar" in payload.check("pitch_bundle").detail
    assert payload.runtime.required_marker.endswith("/lib/prtifull.jar")
    assert payload.required_markers["runtime_home"].endswith("/lib/prtifull.jar")
