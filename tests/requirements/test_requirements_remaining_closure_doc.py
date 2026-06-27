from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/plans/requirements_remaining_closure.md"


def test_requirements_remaining_closure_uses_current_2010_large_family_story() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "`CAP-XML`: `364 partial`" in text
    assert "`CAP-OM`: `98 partial`" in text
    assert "`CAP-OMT`: `2 partial`" in text
    assert "`CAP-API`: `394 partial`" not in text
    assert "omt_xml_bounded_family.md" in text
    assert "There are also no remaining active `2010` closeout buckets in this note." in text
    assert "`0` `partial` rows where Python is still `vendor-divergent`" in text
    assert "`12` `partial` rows where Python is already `verified`" in text
    assert "`13` `partial` rows where Python is `not-applicable`" in text
    assert "`0` supported-subset policy parents" in text
    assert "hla1516_framework_detailed_reconciliation.csv" in text


def test_requirements_remaining_closure_keeps_owner_companion_split_explicit() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "| Requirement family | Owner doc | Owner companion |" in text
    assert "mixed_backend_priority_boundaries.md" in text
    assert "hla1516_1_priority_backend_resolution.csv" in text
    assert "binding_and_hosted_route_boundaries.md" in text
    assert "pitch_202x_bounded_comparison.md" in text
    assert "hla_2025_pitch_202x_group_resolution.csv" in text
    assert "There are no remaining active `2025` closeout buckets in this note." in text
