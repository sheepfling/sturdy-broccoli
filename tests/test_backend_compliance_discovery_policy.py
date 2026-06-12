from __future__ import annotations

import json
import re
from pathlib import Path

from hla2010_repo_internal.verification.backend_compliance_discovery import (
    build_discovery_payload,
    render_backend_compliance_catalog_text,
)

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_LINE_RE = re.compile(r"([A-Za-z0-9-]+)=([0-9]+)")


def _markdown_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("| Priority |"))
    header = [cell.strip() for cell in lines[start].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    index = start + 2
    while index < len(lines) and lines[index].startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
        rows.append(dict(zip(header, cells, strict=True)))
        index += 1
    return rows


def _markdown_summary_counts(text: str, label: str) -> dict[str, int]:
    line = next(
        candidate
        for candidate in text.splitlines()
        if candidate.startswith(f"- {label}: ")
    )
    return {
        key: int(value)
        for key, value in SUMMARY_LINE_RE.findall(line.removeprefix(f"- {label}: "))
    }


def _stringify_backlog_row(row: dict[str, object]) -> dict[str, str]:
    evidence_tests = row.get("evidence_tests", [])
    return {
        "Priority": str(row.get("priority", "")),
        "Backend": str(row.get("backend_id", "")),
        "Family": str(row.get("backend_family", "")),
        "Section / Requirement": str(row.get("requirement_id") or row.get("section_ref", "")),
        "Status": str(row.get("current_status", "")),
        "Next action": str(row.get("recommended_next_action", "")),
        "Source": str(row.get("source_artifact", "")),
        "Evidence": ", ".join(str(item) for item in evidence_tests) if evidence_tests else "-",
    }


def test_discovery_catalog_surfaces_portico_disposition_only_backends() -> None:
    payload = build_discovery_payload(".")
    backends = {row["backend_id"]: row for row in payload["catalog"]["backends"]}

    for backend_id in ("portico", "portico-jpype", "portico-py4j"):
        assert backend_id in backends, backend_id
        row = backends[backend_id]
        assert row["backend_family"] == "vendor-portico-java-bridge"
        assert row["matrices_present"] == ["requirement-disposition"]
        assert row["status_counts"]["classification-required"] > 0
        assert "IEEE 1516.1-2010 §4" in row["section_refs"]


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


def test_committed_vendor_backlog_artifacts_surface_portico_disposition_only_rows() -> None:
    payload = json.loads((ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.json").read_text(encoding="utf-8"))
    rows_by_backend = {
        row["backend_id"]: row
        for row in payload["rows"]
        if str(row.get("backend_id", "")).startswith("portico")
    }

    assert set(rows_by_backend) == {"portico", "portico-jpype", "portico-py4j"}
    for backend_id, row in rows_by_backend.items():
        assert row["current_status"] == "classification-required", backend_id
        assert row["recommended_next_action"] == "classify backend applicability/disposition", backend_id
        assert row["row_kind"] == "synthetic-requirement-disposition-backlog-row", backend_id

    text = (ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.md").read_text(encoding="utf-8")
    assert "classify backend applicability/disposition" in text
    assert "classify Pitch applicability/disposition" not in text
    assert "| P4 | portico | vendor-portico-java-bridge |" in text
    assert "| P4 | portico-jpype | vendor-portico-java-bridge |" in text
    assert "| P4 | portico-py4j | vendor-portico-java-bridge |" in text


def test_committed_vendor_backlog_markdown_matches_json_packet() -> None:
    json_path = ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.json"
    markdown_path = ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.md"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    text = markdown_path.read_text(encoding="utf-8")

    assert f"- Rows: {payload['summary']['row_count']}" in text
    assert _markdown_summary_counts(text, "Status counts") == payload["summary"]["status_counts"]
    assert _markdown_summary_counts(text, "Priority counts") == payload["summary"]["priority_counts"]
    assert _markdown_table(markdown_path) == [
        _stringify_backlog_row(row)
        for row in payload["rows"]
    ]
