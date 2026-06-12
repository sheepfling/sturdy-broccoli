from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _make_fake_pitch_home(path: Path) -> Path:
    (path / "lib").mkdir(parents=True, exist_ok=True)
    (path / "lib" / "prtifull.jar").write_text("", encoding="utf-8")
    (path / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True, exist_ok=True)
    (path / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("", encoding="utf-8")
    return path


def test_pitch_jpype_lost_federate_child_bootstraps_source_checkout() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.vendors.pitch_jpype_lost_federate_child",
            "--help",
        ],
        cwd=ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--federation-name" in result.stdout
    assert "--automatic-resign-directive" in result.stdout


def test_diagnose_pitch_exchange_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "diagnose_pitch_exchange.py"),
            "--help",
        ],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Backend identifier to exercise during the diagnostic run" in result.stdout


def test_diagnose_pitch_negotiated_ownership_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "diagnose_pitch_negotiated_ownership.py"),
            "--help",
        ],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--mode" in result.stdout
    assert "--tail-lines" in result.stdout


def test_repro_pitch_crc_docker_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    pitch_home = _make_fake_pitch_home(tmp_path / "fake-pitch-home")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "repro_pitch_crc_docker.py"),
            "--pitch-home",
            str(pitch_home),
        ],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert f"\"pitch_home\": \"{pitch_home}\"" in result.stdout


def test_repro_pitch_crc_macos_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "repro_pitch_crc_macos.py"),
            "--help",
        ],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--launcher-mode" in result.stdout
