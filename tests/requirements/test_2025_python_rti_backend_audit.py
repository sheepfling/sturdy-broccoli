from __future__ import annotations

from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import build_spec2025_finish_line_snapshot

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
    "HLA2025-MIL-004",
    "HLA2025-MIL-005",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_stays_aligned_with_finish_line_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    audit_path = ROOT / "docs" / "plans" / "2025_python_rti_backend_audit.md"
    audit_text = audit_path.read_text(encoding="utf-8")
    normalized_audit_text = " ".join(audit_text.split())
    normalized_audit_text_lower = normalized_audit_text.lower()

    promotion_split = snapshot["promotion_split_audit"]
    implementation_lane = snapshot["implementation_lane_audit"]
    current_lane_statement = snapshot["current_lane_working_surface_statement"]
    supported_boundary = snapshot["supported_boundary_statement"]
    coherence = snapshot["current_lane_coherence_audit"]

    assert audit_path.exists()
    assert implementation_lane["current_2025_lane"]["backend_package"] == "hla-backend-shim"
    assert implementation_lane["current_2025_lane"]["role"] == "current executable Python 2025 RTI lane"
    assert implementation_lane["dedicated_2025_backend_package_present"] is False
    assert implementation_lane["clean_extraction_still_optional"] is True
    assert promotion_split["ready_for_current_lane_promotion_as_working_surface"] is True
    assert promotion_split["ready_for_permanent_no-split_decision"] is False
    evidence_runs = {run["name"]: run for run in promotion_split["current_evidence_runs"]}
    assert evidence_runs["combined-2025-verification-slice"]["result"] == "467 passed in 78.98s"
    assert evidence_runs["hosted-2025-fedpro-transport-suite"]["result"] == "168 passed in 38.01s"
    assert "strict local FOM/MIM resolution" in evidence_runs["hosted-2025-fedpro-transport-suite"]["scope"]
    assert "directed TSO stale-queue cleanup" in evidence_runs["hosted-2025-fedpro-transport-suite"]["scope"]
    assert current_lane_statement["ready"] is True
    assert supported_boundary["ready"] is True
    assert coherence["ready_for_current_lane_coherent_working_surface_claim"] is True
    assert coherence["ready_for_permanent_no-split_architecture_claim"] is False

    for route in implementation_lane["python_2025_routes"]:
        assert route["is_separate_rti_family"] is False
        assert route["all_route_parity_covered"] is True

    assert "real executable python 2025 rti surface" in normalized_audit_text_lower
    assert "`hla-backend-shim` is the current executable python 2025 rti lane" in normalized_audit_text_lower
    assert "the repo does have a working python 2025 rti lane" in normalized_audit_text_lower
    assert "bounded working-surface claim" in normalized_audit_text_lower
    assert "not a full unqualified ieee 1516.1-2025 conformance claim" in normalized_audit_text_lower
    assert "row-level requirement-by-requirement disposition audit" in normalized_audit_text_lower
    assert "hosted fedpro is still a bounded runtime slice" in normalized_audit_text_lower
    assert "168 passed in 38.01s" in normalized_audit_text_lower
    assert "strict local fom/mim resolution" in normalized_audit_text_lower
    assert "directed tso stale-queue cleanup on restore" in normalized_audit_text_lower
    assert "java and c++ binding evidence remains artifact/runtime-capability bounded" in normalized_audit_text_lower
    assert "promoting the current lane as the working python 2025 rti surface" in normalized_audit_text_lower
    assert "the architecture should still preserve a clean enough seam" in normalized_audit_text_lower
    assert "the repo is not building two duplicate python 2025 rtis" in normalized_audit_text_lower
    assert "extract a dedicated 2025 backend beside a narrower shim only if" in normalized_audit_text_lower
    assert "bounded disposition evidence" in normalized_audit_text_lower
    assert "not merely polishing a fake shim" in normalized_audit_text_lower
