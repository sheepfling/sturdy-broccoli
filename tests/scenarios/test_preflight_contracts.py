from __future__ import annotations

import json
import os
import socket
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


def _fake_running_container_docker_bin(tmp_path: Path, *, container_name: str, crc_port: int, fedpro_port: int) -> Path:
    docker = tmp_path / "docker"
    docker.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail
if [[ "${{1:-}}" == "info" ]]; then
  exit 0
fi
if [[ "${{1:-}}" == "ps" ]]; then
  printf '%s\\n' '{container_name}'
  exit 0
fi
if [[ "${{1:-}}" == "port" ]]; then
  if [[ "${{3:-}}" == "8989/tcp" ]]; then
    printf '127.0.0.1:{crc_port}\\n'
    exit 0
  fi
  if [[ "${{3:-}}" == "15164/tcp" ]]; then
    printf '127.0.0.1:{fedpro_port}\\n'
    exit 0
  fi
  exit 1
fi
exit 0
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


def test_pitch_preflight_reuses_running_managed_container_ports(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    _fake_running_container_docker_bin(
        fake_bin,
        container_name="hla2010-pitch-crc",
        crc_port=37477,
        fedpro_port=37478,
    )
    pitch_home = tmp_path / "pitch-home"
    (pitch_home / "lib").mkdir(parents=True, exist_ok=True)
    (pitch_home / "lib" / "prtifull.jar").write_text("", encoding="utf-8")

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

    assert result.returncode == 0
    payload = PitchPreflightOutput.from_mapping(json.loads(result.stdout))
    assert payload.check("docker").ok is True
    assert payload.ports.crc.port == 37477
    assert payload.ports.fedpro.port == 37478


def test_pitch_port_resolver_selects_fallback_ports_when_preferred_pair_is_busy(tmp_path: Path) -> None:
    listeners: list[socket.socket] = []
    preferred_ports: list[int] = []
    for _ in range(2):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        preferred_ports.append(int(sock.getsockname()[1]))
        listeners.append(sock)
    try:
        env = os.environ.copy()
        env.pop("HLA2010_PITCH_CRC_PORT", None)
        env.pop("HLA2010_PITCH_FEDPRO_PORT", None)
        result = subprocess.run(
            [
                sys.executable,
                "scripts/resolve_pitch_runtime_ports.py",
                "--json",
                "--preferred-crc-port",
                str(preferred_ports[0]),
                "--preferred-fedpro-port",
                str(preferred_ports[1]),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        for sock in listeners:
            sock.close()

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["crc_preferred_port"] == preferred_ports[0]
    assert payload["fedpro_preferred_port"] == preferred_ports[1]
    assert payload["crc_port_source"] == "fallback"
    assert payload["fedpro_port_source"] == "fallback"
    assert payload["crc_port"] != preferred_ports[0]
    assert payload["fedpro_port"] != preferred_ports[1]


def test_pitch_port_resolver_reuses_running_managed_container_ports(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    _fake_running_container_docker_bin(
        fake_bin,
        container_name="hla2010-pitch-crc",
        crc_port=36477,
        fedpro_port=36478,
    )
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/resolve_pitch_runtime_ports.py",
            "--json",
            "--preferred-crc-port",
            "18889",
            "--preferred-fedpro-port",
            "25164",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["crc_port"] == 36477
    assert payload["fedpro_port"] == 36478
    assert payload["crc_port_source"] == "managed-container"
    assert payload["fedpro_port_source"] == "managed-container"
