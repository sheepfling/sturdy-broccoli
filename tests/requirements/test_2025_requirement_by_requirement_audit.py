from __future__ import annotations

from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import build_spec2025_finish_line_snapshot

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_requirement_by_requirement_audit_stays_aligned_with_finish_line_snapshot() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    audit = snapshot["requirement_by_requirement_audit"]
    audit_path = ROOT / "docs" / "plans" / "2025_requirement_by_requirement_audit.md"
    audit_text = " ".join(audit_path.read_text(encoding="utf-8").split()).lower()

    assert audit_path.exists()
    assert audit["audit_status"] == "row-level-requirement-disposition-audit-captured"
    assert audit["ready_for_row_level_requirement_audit_claim"] is True
    assert audit["ready_for_full_2025_conformance_claim"] is False
    assert audit["row_count"] == 691
    assert audit["disposition_counts"] == {
        "covered": 564,
        "duplicate/umbrella": 22,
        "retired/legacy-only": 24,
        "unsupported-boundary": 81,
    }
    assert audit["area_closure"] == {
        "fi_service_catalog": {"covered": 196},
        "som_fom_service_usage": {"covered": 196},
        "omt_component_conformance": {"covered": 143, "unsupported-boundary": 81},
        "omt_validator_negative_conformance": {"covered": 29},
        "framework_rules": {"duplicate/umbrella": 10},
        "callback_configuration_binding_deltas": {"duplicate/umbrella": 12},
        "retired_replacement_mapping_candidates": {"retired/legacy-only": 24},
    }
    assert audit["rows_with_complete_review_metadata"] == 691
    assert audit["covered_rows_with_evidence_paths"] == 564
    assert audit["unsupported_rows_with_explicit_boundary_flag"] == 81
    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in audit["current_assessment"]
    assert any("unsupported-boundary decisions" in blocker for blocker in audit["full_claim_blockers"])
    assert any("duplicate/umbrella normalization aids" in blocker for blocker in audit["full_claim_blockers"])

    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in audit_text
    assert "covered rows: `564`" in audit_text
    assert "unsupported-boundary rows: `81`" in audit_text
    assert "duplicate/umbrella rows: `22`" in audit_text
    assert "the repo no longer lacks a row-level 2025 audit" in audit_text
    assert "still not a full unconditional 2025 conformance pass" in audit_text
