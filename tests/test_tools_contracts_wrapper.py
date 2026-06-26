from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_contracts_help_describes_generate_and_check_commands() -> None:
    result = subprocess.run(
        ["bash", "tools/contracts", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/contracts generate" in result.stdout
    assert "./tools/contracts check" in result.stdout
    assert "generate_hla_interface_contracts.py" in result.stdout


def test_tools_contracts_check_passes_when_doc_is_in_sync() -> None:
    result = subprocess.run(
        ["bash", "tools/contracts", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert "HLA interface contract docs are current" in result.stdout
