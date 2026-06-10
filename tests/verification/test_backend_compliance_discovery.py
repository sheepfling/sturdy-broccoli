from __future__ import annotations

from pathlib import Path

from hla2010_repo_internal.verification.backend_compliance_discovery import (
    build_backend_compliance_catalog,
    build_discovery_payload,
    build_vendor_discovery_backlog,
    render_backend_compliance_catalog_text,
    write_vendor_discovery_backlog_artifacts,
)


def test_backend_compliance_catalog_exposes_primary_backend_views():
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)

    assert catalog["summary"]["backend_count"] >= 6
    assert "analysis/compliance/core_backend_matrix.json" in catalog["source_artifacts"]
    assert catalog["operator_entrypoints"]["discover_command"] == "python3 scripts/discover_backend_compliance.py"

    backends = {row["backend_id"]: row for row in catalog["backends"]}
    assert "python-inmemory" in backends
    assert "certi-native" in backends
    assert "pitch-jpype" in backends

    assert "core" in backends["python-inmemory"]["matrices_present"]
    assert "section8" in backends["python-inmemory"]["matrices_present"]
    assert backends["certi-native"]["status_counts"].get("vendor-divergent", 0) >= 1
    assert any("queryGALT" in " ".join(row["section_refs"]) or row["slice_id"] == "negotiated-ownership" for row in backends["certi-native"]["notable_rows"])

    vendor_summary = catalog["requirements_vendor_summary"]
    assert vendor_summary["python_runtime_status_counts"].get("yes", 0) > 0
    assert vendor_summary["certi_runtime_status_counts"].get("partial", 0) > 0
    assert "analysis/compliance/vendor_discovery_backlog.json" in catalog["source_artifacts"]


def test_backend_compliance_catalog_text_render_supports_filtering():
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)

    rendered = render_backend_compliance_catalog_text(catalog, backend_filter="certi-native")
    assert "Backend Compliance Discovery" in rendered
    assert "certi-native" in rendered
    assert "python-inmemory" not in rendered
    assert "Refresh: python3 scripts/generate_compliance_artifacts.py" in rendered


def test_vendor_discovery_backlog_covers_divergent_gated_matrixed_and_defended_rows():
    project_root = Path(__file__).resolve().parents[2]
    backlog = build_vendor_discovery_backlog(project_root)

    assert backlog["summary"]["row_count"] > 0
    assert backlog["summary"]["status_counts"].get("vendor-divergent", 0) > 0
    assert backlog["summary"]["status_counts"].get("env-gated-positive", 0) > 0
    assert backlog["summary"]["status_counts"].get("not-yet-matrixed", 0) > 0
    assert backlog["summary"]["status_counts"].get("defended-partial", 0) > 0

    by_backend_and_target = {
        (row["backend_id"], row["requirement_id"] or row["section_ref"], row["current_status"]): row
        for row in backlog["rows"]
    }
    assert ("certi-native", "IEEE 1516.1-2010 §7.3, IEEE 1516.1-2010 §7.15", "vendor-divergent") in by_backend_and_target
    assert ("certi-native", "IEEE 1516.1-2010 §4.25, IEEE 1516.1-2010 §4.26", "env-gated-positive") in by_backend_and_target
    assert ("pitch-jpype", "IEEE 1516.1-2010 §8.16", "not-yet-matrixed") in by_backend_and_target

    hosted_positive = [
        row for row in backlog["rows"] if row["backend_id"] == "rest-hosted-python" and row["current_status"] == "positive-path-passing"
    ]
    assert hosted_positive
    assert hosted_positive[0]["recommended_next_action"] == "widen from positive-path slice into deeper vendor matrix coverage"

    defended = [row for row in backlog["rows"] if row["current_status"] == "defended-partial"]
    assert any(row["requirement_id"] == "HLA1516.1-OM-6.1.12-001" for row in defended)
    assert backlog["rows"][0]["priority"] == "P1"


def test_discovery_payload_and_text_support_backlog_filters():
    project_root = Path(__file__).resolve().parents[2]
    payload = build_discovery_payload(project_root, backend_filter="certi-native", priority_filter="P1")

    assert payload["catalog"]["summary"]["backend_count"] == 1
    assert all(row["backend_id"] == "certi-native" for row in payload["backlog"]["rows"])
    assert all(row["priority"] == "P1" for row in payload["backlog"]["rows"])

    rendered = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter="certi-native",
        backlog=payload["backlog"],
        priority_filter="P1",
    )
    assert "Vendor discovery backlog:" in rendered
    assert "P1 certi-native" in rendered
    assert "priority=P1" in rendered


def test_vendor_discovery_backlog_writers_emit_generated_artifacts(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    json_path, md_path = write_vendor_discovery_backlog_artifacts(
        project_root,
        json_path=tmp_path / "vendor_discovery_backlog.json",
        markdown_path=tmp_path / "vendor_discovery_backlog.md",
    )

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    md_text = md_path.read_text(encoding="utf-8")
    assert "Vendor Discovery Backlog" in md_text
    assert "certi-native" in md_text
    assert "pitch-jpype" in md_text
