from __future__ import annotations

import subprocess
import sys
import textwrap
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


def test_ci_test_wrapper_streams_live_pytest_output(tmp_path: Path) -> None:
    test_file = tmp_path / "test_streaming_demo.py"
    test_file.write_text(
        textwrap.dedent(
            """
            import time

            def test_streaming_marker():
                print("STREAM-MARKER", flush=True)
                time.sleep(0.5)
            """
        ),
        encoding="utf-8",
    )

    process = subprocess.Popen(
        ["bash", "scripts/ci/test.sh", "-s", str(test_file)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert process.stdout is not None
    lines: list[str] = []
    while True:
        line = process.stdout.readline()
        if line:
            lines.append(line)
            if "STREAM-MARKER" in line:
                break
        elif process.poll() is not None:
            break

    stderr = ""
    if process.stderr is not None:
        stderr = process.stderr.read()
    returncode = process.wait()

    assert returncode == 0, stderr
    assert any("STREAM-MARKER" in line for line in lines)
