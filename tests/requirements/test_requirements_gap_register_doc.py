from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GAP_DOC = ROOT / "docs/plans/requirements_gap_register.md"
QUEUE_DOC = ROOT / "docs/plans/requirements_execution_queue.md"


def test_gap_register_and_queue_keep_owner_companion_split_explicit() -> None:
    gap_text = GAP_DOC.read_text(encoding="utf-8")
    queue_text = QUEUE_DOC.read_text(encoding="utf-8")

    assert "`Owner companion`" in gap_text
    assert "use the owner doc to explain the bounded or still-open claim honestly" in gap_text
    assert "use the owner companion to carry canonical row state or backend-resolution" in gap_text
    assert "hla1516_1_priority_backend_resolution.csv" in gap_text
    assert "hla_2025_pitch_202x_group_resolution.csv" in gap_text
    assert "hla_2025_pitch_202x_row_resolution.csv" in gap_text

    assert "use this queue for ordering" in queue_text
    assert "use `requirements_gap_register.md` for the exact owner doc, owner companion" in queue_text
    assert "There are no active `2010` open buckets in this register." in gap_text
    assert "There are no active `2025` open buckets in this register." in gap_text
    assert "2010 CAP-XML / CAP-OMT bounded family" in queue_text
    assert "2025 OMT `xs:any` extension-tolerance boundary" in queue_text
    assert "2010 CAP-XML / CAP-OMT partial families" not in queue_text
    assert "2025 Pitch proto HLA 4 / `202X` backend-resolution lane" in queue_text
