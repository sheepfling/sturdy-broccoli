from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.fom_corpus_classification import build_fom_corpus_classification, classify_fom_inventory_record
from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord


def test_classify_fom_inventory_record_separates_repo_owned_support_and_standard_corpus() -> None:
    repo_owned = FOMInventoryRecord(
        id="repo-2010-demo",
        path="packages/hla-rti1516e/src/hla/rti1516e/resources/foms/DemoFOMmodule.xml",
        edition_class="2010",
        load_mode="standalone",
        baseline_kind="repo-owned",
        scenario_family="demo",
        notes="Demo smoke baseline.",
    )
    authoritative = FOMInventoryRecord(
        id="third-party-rpr-foundation",
        path="third_party/fom_baseline/upstream/mcgredonps/HLAGenerator/rpr2.0/Annex_A_Files_Normative/RPR-Foundation_v2.0.xml",
        edition_class="2010",
        load_mode="ordered-family",
        baseline_kind="third-party",
        scenario_family="rpr-normative",
        notes="Ordered family member of the public RPR baseline.",
    )
    support_only = FOMInventoryRecord(
        id="third-party-ieee1516-omt",
        path="analysis/siso_downloads/_expanded/example/IEEE1516-OMT-2010.xsd.xml",
        edition_class="2010",
        load_mode="standalone",
        baseline_kind="third-party",
        scenario_family="siso-omt",
        notes="Schema support artifact.",
    )

    assert classify_fom_inventory_record(repo_owned)[0] == "repo-owned-smoke"
    assert classify_fom_inventory_record(authoritative)[0] == "authoritative-standard"
    assert classify_fom_inventory_record(support_only)[0] == "support-only"

    report = build_fom_corpus_classification((repo_owned, authoritative, support_only))
    assert report.bucket_counts["repo-owned-smoke"] == 1
    assert report.bucket_counts["authoritative-standard"] == 1
    assert report.bucket_counts["support-only"] == 1
    assert any(row.id == "repo-2010-demo" for row in report.bucket_rows)
    assert any(row.edition_scope == "2010 only" for row in report.bucket_rows if row.id == "repo-2010-demo")
    assert any(row.edition_scope == "schema-only / support-only" for row in report.bucket_rows if row.id == "third-party-ieee1516-omt")


def test_write_fom_corpus_classification_writes_html(tmp_path: Path) -> None:
    from hla.verification.repo_internal.fom_corpus_classification import write_fom_corpus_classification

    json_path, md_path, report = write_fom_corpus_classification(output_root=tmp_path / "classification")
    html_path = tmp_path / "classification" / "fom_corpus_classification.html"
    assert json_path.exists()
    assert md_path.exists()
    assert html_path.exists()
    html_text = html_path.read_text(encoding="utf-8")
    assert "Edition Scope" in html_text
    assert report.total_records >= 0
