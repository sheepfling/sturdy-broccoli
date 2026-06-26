from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "plans" / "2025_python_rti_100_percent_worklist.md"


def test_2025_python_rti_100_percent_worklist_doc_pins_current_denominator_rule() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "total tracked rows: `691`" in text
    assert "directly `covered`: `645`" in text
    assert "`duplicate/umbrella`: `22`" in text
    assert "`retired/legacy-only`: `24`" in text
    assert "active normative non-retired non-umbrella rows: `645`" in text
    assert "645 / 645 = 100%" in text


def test_2025_python_rti_100_percent_worklist_doc_names_all_current_non_covered_classes() -> None:
    text = DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for requirement_id in (
        "HLA2025-FR-001",
        "HLA2025-FR-010",
        "HLA2025-FI-CB-001",
        "HLA2025-BIND-JAVA-CPP-001",
        "HLA2025-FI-RET-001",
        "HLA2025-FI-RET-011",
        "HLA2025-OMT-RET-001",
        "HLA2025-OMT-RET-013",
    ):
        assert f"`{requirement_id}`" in text

    assert "These `10` rows are already owned by" in text
    assert "Backend resolution now" in text
    assert "maintained boundary rows, not active direct-support targets" in normalized
    assert "Latest investigated no-convert result for the framework-umbrella class" in text
    assert "re-audited on `2026-06-26`" in text
    assert "These `24` rows are already owned by" in text
    assert "maintained exclusion boundaries, not active direct-support targets" in normalized
    assert "wrapper-only Java/C++ binding surfaces over the direct `python1516_2025` runtime; no alternate RTI owner" in text
    assert "no active 2025 backend owner; explicit legacy-only exclusion" in text
    assert "Latest investigated no-convert result for the retired/legacy-only class" in text
