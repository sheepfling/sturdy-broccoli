from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.requirements_packet import write_imported_hla_packet_markdown_views


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_imported_hla_packet_markdown_views_are_generated_with_expected_families(tmp_path: Path):
    written = write_imported_hla_packet_markdown_views(tmp_path)

    assert set(written) == {
        "README.md",
        "by_standard.md",
        "by_clause.md",
        "by_capability.md",
        "by_service_group.md",
    }
    assert "engineering baseline" in written["README.md"].read_text(encoding="utf-8")
    assert "Imported Packet Requirements By Standard" in written["by_standard.md"].read_text(encoding="utf-8")
    assert "IEEE 1516.1-2010 Clause 4" in written["by_clause.md"].read_text(encoding="utf-8")
    assert "## CAP-FW" in written["by_capability.md"].read_text(encoding="utf-8")
    assert "By Service Group" in written["by_service_group.md"].read_text(encoding="utf-8")


def test_imported_hla_packet_docs_script_bootstraps_source_checkout(tmp_path: Path):
    output_dir = tmp_path / "imported_packet_requirements_v1_0"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_imported_packet_requirements_docs.py",
            "--output-dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "README.md").exists()
    assert (output_dir / "by_clause.md").exists()
