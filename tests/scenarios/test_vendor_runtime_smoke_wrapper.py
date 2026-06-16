from __future__ import annotations

import json
import os
import socket
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
    env["PATH"] = os.pathsep.join(("/usr/bin", "/bin"))
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


def test_vendor_runtime_smoke_skips_cleanly_without_repo_venv(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    env["HLA2010_VENV_DIR"] = str(tmp_path / "missing-venv")
    env["HLA2010_VENDOR_AUTO_BOOTSTRAP_PYTHON"] = "0"
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
    assert "python test environment is missing" not in result.stderr
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
    assert isinstance(payload["ports"]["crc"]["port"], int)
    assert isinstance(payload["ports"]["fedpro"]["port"], int)
    assert payload["ports"]["crc"]["port"] > 0
    assert payload["ports"]["fedpro"]["port"] > 0
    assert any(check["name"] == "crc_port" for check in payload["checks"])
    assert any(check["name"] == "fedpro_port" for check in payload["checks"])
    assert "skipping runtime smoke for this vendor" in result.stderr


def test_pitch_preflight_selects_alternate_ports_when_defaults_are_busy(tmp_path: Path) -> None:
    pitch_home = tmp_path / "pitch"
    (pitch_home / "lib").mkdir(parents=True)
    (pitch_home / "lib" / "prtifull.jar").write_text("stub", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_docker = fake_bin / "docker"
    fake_docker.write_text(
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
    fake_docker.chmod(0o755)

    held_sockets: list[socket.socket] = []
    for port in (8989, 15164):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
            sock.listen(1)
            held_sockets.append(sock)
        except OSError:
            sock.close()

    env = os.environ.copy()
    env["HLA2010_PITCH_HOME"] = str(pitch_home)
    env["PATH"] = os.pathsep.join((str(fake_bin), "/usr/bin", "/bin"))
    artifact_path = tmp_path / "pitch-preflight.json"
    try:
        result = subprocess.run(
            ["bash", "scripts/check_pitch_preflight.sh", "--json-file", str(artifact_path)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        for sock in held_sockets:
            sock.close()

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["environment"] == "ready"
    assert payload["ports"]["crc"]["status"] == "ok"
    assert payload["ports"]["fedpro"]["status"] == "ok"
    assert payload["ports"]["crc"]["port"] != 8989
    assert payload["ports"]["fedpro"]["port"] != 15164
    assert "selected alternate" in payload["ports"]["crc"]["detail"]
    assert "selected alternate" in payload["ports"]["fedpro"]["detail"]


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
