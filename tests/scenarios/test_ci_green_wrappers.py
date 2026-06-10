from __future__ import annotations

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
