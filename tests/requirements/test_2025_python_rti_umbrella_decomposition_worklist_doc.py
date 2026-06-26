from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "plans" / "2025_python_rti_umbrella_decomposition_worklist.md"


def test_2025_umbrella_decomposition_worklist_lists_all_current_umbrella_rows() -> None:
    text = DOC.read_text(encoding="utf-8")

    for requirement_id in (
        "HLA2025-FR-001",
        "HLA2025-FR-010",
        "HLA2025-FI-CB-001",
        "HLA2025-FI-CB-008",
        "HLA2025-FI-CFG-001",
        "HLA2025-FI-AUTH-001",
        "HLA2025-BIND-FEDPRO-001",
        "HLA2025-BIND-JAVA-CPP-001",
    ):
        assert f"`{requirement_id}`" in text

    assert "`22` rows in `duplicate/umbrella`" in text
    assert "`10` framework umbrella rows" in text
    assert "`12` callback/configuration/binding delta umbrella rows" in text


def test_2025_umbrella_decomposition_worklist_keeps_shard_owner_and_conversion_rules_explicit() -> None:
    text = DOC.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Decomposition Rule" in text
    assert "## Framework Umbrella Rows" in text
    assert "## Callback, Configuration, and Binding Umbrella Rows" in text
    assert "Primary shard now" in text
    assert "Backend resolution now" in text
    assert "Stay umbrella when" in text
    assert "Convert only if" in text
    assert "## Latest Investigated Decision" in text
    assert "The framework umbrella slice was re-audited on `2026-06-26`" in text
    assert "no narrower standalone framework claim was identified" in text
    assert "keep these rows as `duplicate/umbrella`" in text
    assert "double-count the existing child proof" in text
    assert "keep this row as `duplicate/umbrella`" in text
    assert "no narrower standalone directed-interaction callback-parameterization claim was identified" in normalized
    assert "no narrower standalone Java/C++ binding-capability claim was identified" in normalized
    assert "no narrower standalone protocol-capability claim was identified" in text
    assert "no narrower standalone configuration-result or authorization-credentials" in text
    assert "configuration and authorization slice remains a maintained umbrella" in text
    assert "wrapper-only Java/C++ binding surfaces over the direct `python1516_2025` runtime" in text
    assert "bounded hosted FedPro route over `hla-backend-python1516-2025`; not an independent RTI owner" in text
    assert "verification/shard_registry.md" in text
    assert "verification/view_registry.md" in text
