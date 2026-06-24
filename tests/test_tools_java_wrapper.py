from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_java_help_describes_smoke_and_bridge_test_commands() -> None:
    result = subprocess.run(
        ["bash", "tools/java", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/java smoke --bridge jpype --edition 2010" in result.stdout
    assert "./tools/java smoke --all" in result.stdout
    assert "./tools/java smoke --bridge jpype --real-shim" in result.stdout
    assert "./tools/java test-bridges" in result.stdout


def test_tools_java_smoke_all_dry_run_lists_isolated_matrix() -> None:
    result = subprocess.run(
        ["bash", "tools/java", "smoke", "--all", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 4
    assert "--edition 2010 --bridge jpype" in lines[0]
    assert "--edition 2010 --bridge py4j" in lines[1]
    assert "--edition 2025 --bridge jpype" in lines[2]
    assert "--edition 2025 --bridge py4j" in lines[3]


def test_tools_java_smoke_real_shim_dry_run_builds_then_runs() -> None:
    result = subprocess.run(
        ["bash", "tools/java", "smoke", "--bridge", "py4j", "--edition", "2025", "--real-shim", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 2
    assert "java_shims/hla-rti1516e-shim/tools/build_java_shim.py" in lines[0]
    assert "--output" in lines[0]
    assert "examples/java_shim_federate.py" in lines[1]
    assert "--edition 2025 --bridge py4j --real-java-shim" in lines[1]


def test_tools_java_test_bridges_dry_run_targets_focused_test_files() -> None:
    result = subprocess.run(
        ["bash", "tools/java", "test-bridges", "--real-shim", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 2
    assert "tests/test_java_bridge_examples.py" in lines[0]
    assert "tests/runtime/test_optional_real_java_bridges.py" in lines[1]
