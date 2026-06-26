from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/plans/requirements_finish_line.md"


def test_requirements_finish_line_keeps_owner_companion_and_presentation_split_explicit() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "For the canonical bucket owners behind the 2025 surface, use:" in text
    assert "[`requirements_gap_register.md`](requirements_gap_register.md) when you" in text
    assert "owner doc plus owner companion pair" in text
    assert "when a bucket has both a human-facing owner doc and a source or" in text
    assert "backend-resolution companion artifact, keep both explicit" in text
    assert "spreadsheet packets stay downstream of those sources" in text
    assert "Pitch proto HLA 4 / `202X`" in text
