from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FINAL_REPORT = ROOT / "analysis" / "compliance" / "python_final_requirements_report.md"
BRIEF = ROOT / "analysis" / "compliance" / "python_boss_capability_brief.md"


def test_python_final_requirements_report_keeps_runtime_projection_separate_from_packet_partials() -> None:
    text = FINAL_REPORT.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Python RTI Final Requirements Report" in text
    assert "Python runtime projection has no open runtime-classification states" in normalized
    assert "canonical `2010` backend-compliance packet still contains bounded `partial` rows" in normalized
    assert "`934` matrix rows" in text
    assert "`842` `pass`" in text
    assert "`40` `implemented-slice`" in text
    assert "`1` `implemented-smoke`" in text
    assert "`51` `partial`" in text
    assert "`853` `verified`" in text
    assert "`79` `not-applicable`" in text
    assert "`2` `vendor-divergent`" in text
    assert "do not restate the Python runtime result as \"all `2010` requirements are fully passed\"" in normalized
    assert "`2` rows where Python is `vendor-divergent`" in text
    assert "`13` rows where Python is `not-applicable`" in text
    assert "`36` rows where Python is already `verified`" in text
    assert "2010_python_rti_bounded_family_execution_worklist.md" in text
    assert "requirements_completion_audit.md" in text
    assert "generated summary surface over the canonical matrix and disposition ledgers" in normalized
    assert "not as the canonical owner ledger" in normalized
    assert "requirement_compliance_exports.md" in text


def test_python_boss_capability_brief_keeps_denominator_split_explicit() -> None:
    text = BRIEF.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Python RTI Capability Brief" in text
    assert "leadership should read it through two separate denominators" in normalized
    assert "`934` rows" in text
    assert "`842` `pass`" in text
    assert "`51` `partial`" in text
    assert "`853` `verified`" in text
    assert "`79` `not-applicable`" in text
    assert "`2` `vendor-divergent`" in text
    assert "Python runtime projection inside that packet" in text
    assert "canonical `2010` packet still keeps bounded `partial` rows explicit" in normalized
    assert "this brief is a downstream summary surface, not the canonical owner ledger" in normalized
    assert "canonical requirement status still lives in the owner ledgers" in normalized
    assert "docs/verification/requirement_compliance_exports.md" in text
    assert "packages/hla-backend-python1516e/README.md" in text
    assert "packages/hla-backend-python1516e/src/hla/backends/python1516e/time_queue_delivery.py" in text
    assert "packages/hla-backend-python1516e/src/hla/backends/python1516e/state.py" in text
