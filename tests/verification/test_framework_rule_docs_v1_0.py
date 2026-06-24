from __future__ import annotations

from pathlib import Path


def test_framework_docs_capture_product_set_scope_and_source_policy():
    hierarchy = (
        Path(__file__).resolve().parents[2] / "docs" / "verification" / "requirements_hierarchy.md"
    ).read_text(encoding="utf-8")
    reference = (
        Path(__file__).resolve().parents[2] / "docs" / "reference" / "README.md"
    ).read_text(encoding="utf-8")
    source_policy = (
        Path(__file__).resolve().parents[2] / "docs" / "source_documents_policy.md"
    ).read_text(encoding="utf-8")

    assert "IEEE 1516-2010`: framework and rules" in hierarchy
    assert "IEEE 1516.1-2010`: RTI services and MOM behavior" in hierarchy
    assert "IEEE 1516.2-2010`: OMT schema language and FOM/MIM interchange" in hierarchy
    assert "| Framework rules | Framework concepts | `HLA1516-FW-001` |" in hierarchy
    assert "Canonical working source material for this repo lives under:" in reference
    assert "../../specs/ieee-1516-2010/" in reference
    assert "section anchors through `hla.spec.refs`" in source_policy
    assert "bibliographic and archive-reference material as non-normative source" in source_policy
