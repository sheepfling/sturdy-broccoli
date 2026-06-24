from __future__ import annotations

import re
from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import build_spec2025_finish_line_snapshot

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_requirement_by_requirement_audit_stays_aligned_with_finish_line_snapshot() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    audit = snapshot["requirement_by_requirement_audit"]
    audit_path = ROOT / "docs" / "plans" / "2025_requirement_by_requirement_audit.md"
    audit_markdown = audit_path.read_text(encoding="utf-8")
    audit_text = " ".join(audit_markdown.split()).lower()

    assert audit_path.exists()
    assert audit["audit_status"] == "row-level-requirement-disposition-audit-captured"
    assert audit["ready_for_row_level_requirement_audit_claim"] is True
    assert audit["ready_for_full_2025_conformance_claim"] is False
    assert audit["row_count"] == 691
    assert audit["disposition_counts"] == {
        "covered": 645,
        "duplicate/umbrella": 22,
        "retired/legacy-only": 24,
    }
    assert audit["area_closure"] == {
        "fi_service_catalog": {"covered": 196},
        "som_fom_service_usage": {"covered": 196},
        "omt_component_conformance": {"covered": 224},
        "omt_validator_negative_conformance": {"covered": 29},
        "framework_rules": {"duplicate/umbrella": 10},
        "callback_configuration_binding_deltas": {"duplicate/umbrella": 12},
        "retired_replacement_mapping_candidates": {"retired/legacy-only": 24},
    }
    assert audit["rows_with_complete_review_metadata"] == 691
    assert audit["covered_rows_with_evidence_paths"] == 645
    assert audit["unsupported_rows_with_explicit_boundary_flag"] == 0
    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in audit["current_assessment"]
    assert "strengthens the bounded main-implementation claim for hla-backend-python1516-2025" in audit["current_assessment"]
    assert "hla-backend-shim in a wrapper-only compatibility role" in audit["current_assessment"]
    assert any("third-party extension execution semantics" in blocker for blocker in audit["full_claim_blockers"])
    assert any("duplicate/umbrella normalization aids" in blocker for blocker in audit["full_claim_blockers"])

    assert "row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows" in audit_text
    assert "covered rows: `645`" in audit_text
    assert "unsupported-boundary rows: `0`" in audit_text
    assert "duplicate/umbrella rows: `22`" in audit_text
    assert "the repo no longer lacks a row-level 2025 audit" in audit_text
    assert "strengthens the bounded main-implementation claim for `hla-backend-python1516-2025`" in audit_text
    assert "`hla-backend-shim` stays in a compatibility-wrapper role" in audit_text
    assert "still not a full unconditional 2025 conformance pass" in audit_text
    assert "hla2025-omt-comp-041" in audit_text
    assert "hla2025-omt-comp-192" in audit_text
    assert "2025-omt-dimension-metadata-roundtrip" in audit_text
    assert "hla2025-omt-comp-133" in audit_text
    assert "2025-omt-class-parameter-metadata-roundtrip" in audit_text
    assert "hla2025-omt-comp-170" in audit_text
    assert "additional 2025 switch metadata preservation" in audit_text
    assert "hla2025-omt-comp-044" in audit_text
    assert "2025 dimension input/output metadata preservation" in audit_text
    assert "hla2025-omt-comp-083" in audit_text
    assert "keyword taxonomy metadata preservation" in audit_text
    assert "hla2025-omt-comp-048" in audit_text
    assert "2025-omt-association-metadata-roundtrip" in audit_text
    assert "object/interaction dimension association metadata preservation" in audit_text
    assert "2025-omt-xs-any-extension-tolerance" in audit_text
    assert "preserves their xml payloads across" in audit_text
    assert "arbitrary third-party extension execution semantics remain outside" in audit_text
    assert "logical-time semantics proof" in audit_text

    expected_summary_lines = [
        "- Total tracked rows: `691`",
        "- Covered rows: `645`",
        "- Unsupported-boundary rows: `0`",
        "- Retired/legacy-only rows: `24`",
        "- Duplicate/umbrella rows: `22`",
        "- Federate Interface service catalog: `covered=196`",
        "- SOM/FOM service-usage requirements: `covered=196`",
        "- OMT component-level conformance: `covered=224`",
        "- OMT validator-negative conformance: `covered=29`",
        "- Framework and Rules: `duplicate/umbrella=10`",
        "- Callback/configuration/binding deltas: `duplicate/umbrella=12`",
        "- Retired / replacement mapping candidates: `retired/legacy-only=24`",
    ]
    for line in expected_summary_lines:
        assert line in audit_markdown


@pytest.mark.requirements("HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_requirement_by_requirement_audit_summary_block_matches_snapshot_counts() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    audit = snapshot["requirement_by_requirement_audit"]
    audit_path = ROOT / "docs" / "plans" / "2025_requirement_by_requirement_audit.md"
    markdown = audit_path.read_text(encoding="utf-8")

    def extract(label: str) -> int:
        match = re.search(rf"- {re.escape(label)}: `(\d+)`", markdown)
        assert match, label
        return int(match.group(1))

    assert extract("Total tracked rows") == audit["row_count"]
    assert extract("Covered rows") == audit["disposition_counts"]["covered"]
    assert extract("Unsupported-boundary rows") == audit["unsupported_rows_with_explicit_boundary_flag"]
    assert extract("Retired/legacy-only rows") == audit["disposition_counts"]["retired/legacy-only"]
    assert extract("Duplicate/umbrella rows") == audit["disposition_counts"]["duplicate/umbrella"]
