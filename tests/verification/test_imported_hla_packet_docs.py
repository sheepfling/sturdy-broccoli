from __future__ import annotations

from pathlib import Path

from hla2010.requirements_packet import write_imported_hla_packet_markdown_views


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
