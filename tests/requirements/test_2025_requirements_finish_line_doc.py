from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/plans/2025_requirements_finish_line.md"


def test_2025_requirements_finish_line_lists_current_boundary_owner_docs() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "Canonical boundary owner reading order:" in text
    assert "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md" in text
    assert "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md" in text
    assert "hla_2025_pitch_202x_group_resolution.csv" in text
    assert "hla_2025_pitch_202x_row_resolution.csv" in text
    assert "use the owner docs above for the boundary narrative, and use the linked" in text.lower()
