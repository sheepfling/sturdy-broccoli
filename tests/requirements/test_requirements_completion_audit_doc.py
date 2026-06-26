from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/plans/requirements_completion_audit.md"


def test_requirements_completion_audit_keeps_owner_vs_presentation_split_explicit() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "use this page for the honest current answer to \"are we done?\"" in text
    assert "requirement_compliance_exports.md" in text
    assert "spreadsheet packets are downstream presentation outputs" in text
    assert "canonical requirement status lives in the owner ledgers" in text
    assert "backend-specific support must stay in explicit backend-resolution columns" in text
    assert "hla1516_1_priority_backend_resolution.csv" in text
    assert "pitch_202x_resolution" in text
