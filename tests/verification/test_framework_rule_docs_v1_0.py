from __future__ import annotations

from pathlib import Path


def test_framework_docs_capture_product_set_scope_and_source_policy():
    root = Path(__file__).resolve().parents[2]
    hierarchy = (root / "docs" / "verification" / "requirements_hierarchy.md").read_text(
        encoding="utf-8"
    )
    reference = (root / "docs" / "reference" / "README.md").read_text(encoding="utf-8")
    source_policy = (root / "docs" / "source_documents_policy.md").read_text(encoding="utf-8")

    assert "IEEE 1516-2010`: framework and rules" in hierarchy
    assert "IEEE 1516.1-2010`: RTI services and MOM behavior" in hierarchy
    assert "IEEE 1516.2-2010`: OMT schema language and FOM/MIM interchange" in hierarchy
    assert "| Framework rules | Framework concepts | `HLA1516-FW-001` |" in hierarchy
    assert "test_framework_docs_capture_product_set_scope_and_source_policy" in hierarchy
    assert "| Framework rules | Object model concepts | `HLA1516-OBJ-001` |" in hierarchy
    assert "test_parse_fom_xml_recognizes_standard_omt_component_tables_across_fom_som_and_mim" in hierarchy
    assert "Canonical working source material for this repo lives under:" in reference
    assert "../../specs/ieee-1516-2010/" in reference
    assert "section anchors through `hla.spec.refs`" in source_policy
    assert "bibliographic and archive-reference material as non-normative source" in source_policy
    assert "../plans/requirements_completion_audit.md" not in hierarchy
    assert "../plans/requirements_remaining_closure.md" not in hierarchy
    assert (
        "[`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md)"
        in hierarchy
    )
    assert "[`../../requirements/2010/README.md`](../../requirements/2010/README.md)" in hierarchy
    assert "requirements/2010/hla1516_framework_detailed_reconciliation.csv" in hierarchy
    assert (
        "test_create_federation_execution_distinguishes_open_read_time_and_inconsistent_fom_errors"
        in hierarchy
    )
