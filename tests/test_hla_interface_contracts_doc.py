from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import scripts.generate_hla_interface_contracts as contracts_script


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "reference" / "hla_interface_contracts.md"
BASE_PATH = ROOT / "packages" / "hla-backend-common" / "src" / "hla" / "backends" / "common" / "base.py"


def test_hla_interface_contracts_doc_is_in_sync_with_generator() -> None:
    expected = contracts_script.render_docs()
    actual = DOC_PATH.read_text(encoding="utf-8")
    assert actual == expected


def test_hla_interface_contracts_generate_docs_does_not_rewrite_backend_code() -> None:
    before = BASE_PATH.read_text(encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/generate_hla_interface_contracts.py", "generate-docs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert BASE_PATH.read_text(encoding="utf-8") == before
    assert "docs/reference/hla_interface_contracts.md" in result.stdout
