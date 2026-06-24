from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_python_help_describes_example_smoke_commands() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/python smoke-examples --edition 2010" in result.stdout
    assert "./tools/python smoke-examples --edition 2025" in result.stdout
    assert "./tools/python smoke-examples --all" in result.stdout
    assert "./tools/python test-examples" in result.stdout


def test_tools_python_smoke_examples_all_dry_run_lists_both_editions() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "smoke-examples", "--all", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 2
    assert "examples/python_route_federate.py --edition 2010" in lines[0]
    assert "examples/python_route_federate.py --edition 2025" in lines[1]


def test_tools_python_test_examples_dry_run_targets_focused_test_file() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "test-examples", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert lines == ["+ hla2010_shell_run_workspace_python python3 -m pytest -q tests/test_python_route_examples.py"]
