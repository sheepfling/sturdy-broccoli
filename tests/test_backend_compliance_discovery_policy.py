from __future__ import annotations

import json
from pathlib import Path

from compliance_helpers import IEEE_1516_1_2010, has_section_ref
from hla.verification.repo_internal.verification.backend_compliance_discovery import (
    build_discovery_payload,
    render_backend_compliance_catalog_text,
)

ROOT = Path(__file__).resolve().parents[1]


def test_discovery_catalog_surfaces_portico_disposition_only_backends() -> None:
    payload = build_discovery_payload(".")
    backends = {row["backend_id"]: row for row in payload["catalog"]["backends"]}

    for backend_id in ("portico", "portico-jpype", "portico-py4j"):
        assert backend_id in backends, backend_id
        row = backends[backend_id]
        assert row["backend_family"] == "vendor-portico-java-bridge"
        assert row["matrices_present"] == ["requirement-disposition"]
        assert row["status_counts"]["classification-required"] > 0
        assert has_section_ref(row["section_refs"], IEEE_1516_1_2010, "4")


def test_discovery_catalog_backend_filter_keeps_portico_disposition_only_profile() -> None:
    payload = build_discovery_payload(".", backend_filter="portico-jpype")

    assert payload["catalog"]["summary"]["backend_count"] == 1
    backend = payload["catalog"]["backends"][0]
    assert backend["backend_id"] == "portico-jpype"
    assert backend["backend_family"] == "vendor-portico-java-bridge"
    assert backend["matrices_present"] == ["requirement-disposition"]


def test_discovery_text_renders_portico_disposition_only_profile() -> None:
    payload = build_discovery_payload(".", backend_filter="portico-jpype")
    text = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter="portico-jpype",
        backlog=payload["backlog"],
    )

    assert "portico-jpype (vendor-portico-java-bridge)" in text
    assert "matrices: requirement-disposition" in text
    assert "classification-required=" in text


def test_vendor_backlog_surfaces_portico_disposition_only_backends() -> None:
    payload = build_discovery_payload(".")
    backlog_rows = payload["backlog"]["rows"]
    rows_by_backend = {row["backend_id"]: row for row in backlog_rows if row["backend_id"].startswith("portico")}

    assert set(rows_by_backend) == {"portico", "portico-jpype", "portico-py4j"}
    for backend_id, row in rows_by_backend.items():
        assert row["current_status"] == "classification-required", backend_id
        assert row["backend_family"] == "vendor-portico-java-bridge", backend_id
        assert row["recommended_next_action"] == "classify backend applicability/disposition", backend_id
        assert row["source_artifact"].endswith(f"{backend_id}_requirement_disposition.json") or (
            backend_id == "portico" and row["source_artifact"].endswith("portico_requirement_disposition.json")
        )
        assert row["row_kind"] == "synthetic-requirement-disposition-backlog-row", backend_id
        assert row["scope"] == "generated-backend-disposition", backend_id


def test_discovery_text_backlog_renders_portico_disposition_only_profile() -> None:
    payload = build_discovery_payload(".", backend_filter="portico-jpype")
    text = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter="portico-jpype",
        backlog=payload["backlog"],
    )

    assert "Vendor discovery backlog:" in text
    assert "P4 portico-jpype" in text
    assert "classification-required" in text
    assert "classify backend applicability/disposition" in text


def test_generated_vendor_backlog_surfaces_portico_disposition_only_rows() -> None:
    payload = build_discovery_payload(".")
    backlog = payload["backlog"]
    rows_by_backend = {
        row["backend_id"]: row
        for row in backlog["rows"]
        if str(row.get("backend_id", "")).startswith("portico")
    }

    assert set(rows_by_backend) == {"portico", "portico-jpype", "portico-py4j"}
    for backend_id, row in rows_by_backend.items():
        assert row["current_status"] == "classification-required", backend_id
        assert row["recommended_next_action"] == "classify backend applicability/disposition", backend_id
        assert row["row_kind"] == "synthetic-requirement-disposition-backlog-row", backend_id


def test_generated_vendor_backlog_surfaces_backlog_summary_and_priorities() -> None:
    payload = build_discovery_payload(".")
    backlog = payload["backlog"]
    assert backlog["summary"]["row_count"] == len(backlog["rows"])
    assert any(row["current_status"] == "classification-required" for row in backlog["rows"])
    assert any(row["priority"] == "P1" for row in backlog["rows"])
