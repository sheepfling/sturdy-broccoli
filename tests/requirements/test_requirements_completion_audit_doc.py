from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/plans/requirements_completion_audit.md"


def test_requirements_completion_audit_keeps_owner_vs_presentation_split_explicit() -> None:
    text = DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "use this page for the honest current answer to \"are we done?\"" in text
    assert "requirement_compliance_exports.md" in text
    assert "spreadsheet packets are downstream presentation outputs" in text
    assert "canonical requirement status lives in the owner ledgers" in text
    assert "backend-specific support must stay in explicit backend-resolution columns" in text
    assert "analysis/compliance/compliance.before/" in text
    assert "historical restore or diff surfaces" in normalized
    assert "hla1516_1_priority_backend_resolution.csv" in text
    assert "pitch_202x_resolution" in text
    assert "2025_python_rti_umbrella_decomposition_worklist.md" in text
    assert "2010_python_rti_bounded_family_execution_worklist.md" in text
    assert "framework_rules.md" in text
    assert "callback_binding_deltas.md" in text
    assert "../verification/shard_registry.md" in text
    assert "row-level tracked universe: `691`" in text
    assert "current direct coverage on that active denominator: `645 / 645 = 100%`" in text
    assert "backend-compliance packet denominator: `934` matrix rows" in text
    assert "do not collapse those two denominators into one cross-edition completion" in text
    assert "`54` `partial`" in text
    assert "`5` `partial` rows with Python still `vendor-divergent`" in text
    assert "`5` rows now fall into explicit owner buckets" in text
    assert "`1` federation-management effect-vector row" in text
    assert "`2` framework or architecture rows owned by" in text
    assert "hla1516_framework_detailed_reconciliation.csv" in text
    assert "the `2010` packet no longer contains any `planned` inventory rows" in text
    assert "`20` `pass` OMT/XML area rows" in text
    assert "`3` `implemented-slice` OMT/XML execution witnesses" in text
    assert "`0` remaining OMT/XML area partial placeholders" in text
    assert "current bounded reading is already explicit for the `109` remaining rows" in text
    assert "No separate `2010` `planned` inventory remains in the current packet." in text
    assert "whether the repo wants to tighten the remaining bounded" in text
    assert "the remaining `2010` Python `vendor-divergent` packet rows are no longer one undifferentiated blocker class" in text
    assert "the `22` umbrella rows are not missing-owner rows" in text
    assert "the 2025 federation-management closeout is now owner-clean" in text
    assert "`HLA2025-FI-SVC-005`" in text
    assert "`HLA2025-FI-SVC-008`" in text
    assert "`HLA2025-FI-SVC-010`" in text
    assert "`HLA2025-FI-SVC-011`" in text
    assert "REST-hosted Python route is intentionally kept in the narrower execution-membership slice only" in normalized
    assert "`FederationExecutionDoesNotExist` after destroy succeeds" in text
    assert "replace them with narrower direct executable" in text
    assert "claims?" in text
    assert "should the bounded rows stay in their current explicit final-state reading" in text
    assert "remaining blockers to a stronger all-covered" in text
