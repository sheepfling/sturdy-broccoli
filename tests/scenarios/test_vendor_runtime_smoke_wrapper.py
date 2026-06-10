from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _base_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_CERTI_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(tmp_path / "missing-certi-upstream-prefix")
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(tmp_path / "missing-certi-upstream-build")
    env["HLA2010_PITCH_HOME"] = str(tmp_path / "missing-pitch-home")
    env["PATH"] = "/usr/bin:/bin"
    return env


def test_vendor_runtime_smoke_writes_certi_preflight_and_skips_cleanly(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "scripts/ci/vendor_runtime_smoke.sh", "certi-patched"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    assert payload["exit_code"] == 1
    assert "real CERTI will skip" in payload["result"]
    assert "runtime_profiles" in payload
    assert payload["runtime_profiles"]["active"]["prefix"]["path"]
    assert payload["runtime_profiles"]["patched"]["prefix"]["marker"].endswith("bin/rtig")
    assert payload["runtime_profiles"]["patched"]["source"]["marker"].endswith("Certi-Test-02.xml")
    assert "skipping runtime smoke for this vendor" in result.stderr


def test_vendor_runtime_smoke_writes_pitch_preflight_and_skips_cleanly(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "scripts/ci/vendor_runtime_smoke.sh", "pitch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    assert payload["exit_code"] == 1
    assert "not ready" in payload["result"]
    assert payload["runtime"]["container_name"] == "hla2010-pitch-crc"
    assert payload["ports"]["crc"]["port"] == 8989
    assert payload["ports"]["fedpro"]["port"] == 15164
    assert any(check["name"] == "crc_port" for check in payload["checks"])
    assert any(check["name"] == "fedpro_port" for check in payload["checks"])
    assert "skipping runtime smoke for this vendor" in result.stderr


def test_vendor_green_fails_strictly_when_pitch_preflight_is_blocked(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch"],
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
    assert payload["exit_code"] == 1
    assert "strict mode" in result.stderr
