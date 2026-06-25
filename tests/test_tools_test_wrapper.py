from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_test_help_mentions_fail_fast_usage() -> None:
    result = subprocess.run(
        ["bash", "tools/test", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/test -k ownership --lf" in result.stdout
    assert "./tools/test tests/transport --ff" in result.stdout


def test_ci_test_wrapper_emits_narrow_rerun_hints_on_failure() -> None:
    result = subprocess.run(
        ["bash", "scripts/ci/test.sh", "tests/does_not_exist.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "rerun hints:" in result.stderr
    assert "./tools/test tests/does_not_exist.py" in result.stderr
    assert "./tools/test --lf" in result.stderr
    assert "./tools/test -x" in result.stderr
