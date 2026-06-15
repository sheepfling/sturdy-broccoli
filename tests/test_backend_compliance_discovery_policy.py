from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from conftest import REPO_ROOT, load_compliance_json, load_compliance_text
from hla2010_repo_internal.verification.backend_compliance_discovery import (
    build_discovery_payload,
    render_backend_compliance_catalog_text,
)
from tests.compliance_row_models import BackendCatalogRow, VendorBacklogRow
from tests.doc_test_helpers import assert_absent_all, assert_contains_all, load_json_fixture, read

ROOT = REPO_ROOT
SUMMARY_LINE_RE = re.compile(r"([A-Za-z0-9-]+)=([0-9]+)")


@dataclass(frozen=True)
class BackendDiscoveryPolicy:
    portico_backend_ids: tuple[str, ...]
    family: str
    matrices_present: tuple[str, ...]
    classification_status: str
    section_ref: str
    filtered_backend: str
    row_kind: str
    scope: str
    recommended_next_action: str
    catalog_text_fragments: tuple[str, ...]
    backlog_text_fragments: tuple[str, ...]
    committed_markdown_required_fragments: tuple[str, ...]
    committed_markdown_forbidden_fragments: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> BackendDiscoveryPolicy:
        return cls(
            portico_backend_ids=tuple(str(item) for item in payload["portico_backend_ids"]),
            family=str(payload["family"]),
            matrices_present=tuple(str(item) for item in payload["matrices_present"]),
            classification_status=str(payload["classification_status"]),
            section_ref=str(payload["section_ref"]),
            filtered_backend=str(payload["filtered_backend"]),
            row_kind=str(payload["row_kind"]),
            scope=str(payload["scope"]),
            recommended_next_action=str(payload["recommended_next_action"]),
            catalog_text_fragments=tuple(str(item) for item in payload["catalog_text_fragments"]),
            backlog_text_fragments=tuple(str(item) for item in payload["backlog_text_fragments"]),
            committed_markdown_required_fragments=tuple(
                str(item) for item in payload["committed_markdown_required_fragments"]
            ),
            committed_markdown_forbidden_fragments=tuple(
                str(item) for item in payload["committed_markdown_forbidden_fragments"]
            ),
        )


DISCOVERY_POLICY = BackendDiscoveryPolicy.from_mapping(
    load_json_fixture("backend_compliance_discovery_policy.json")
)


@dataclass(frozen=True)
class MarkdownTableRow:
    cells: dict[str, str]

    def as_dict(self) -> dict[str, str]:
        return dict(self.cells)


def _markdown_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("| Priority |"))
    header = [cell.strip() for cell in lines[start].strip("|").split("|")]
    rows: list[MarkdownTableRow] = []
    index = start + 2
    while index < len(lines) and lines[index].startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
        rows.append(MarkdownTableRow(dict(zip(header, cells, strict=True))))
        index += 1
    return [row.as_dict() for row in rows]


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


def _catalog_rows(payload: dict[str, object]) -> list[BackendCatalogRow]:
    return [BackendCatalogRow.from_mapping(row) for row in payload["catalog"]["backends"]]


def _backlog_rows(payload: dict[str, object]) -> list[VendorBacklogRow]:
    return [VendorBacklogRow.from_mapping(row) for row in payload["rows"]]


def _stringify_backlog_row(row: VendorBacklogRow) -> dict[str, str]:
    return {
        "Priority": row.priority,
        "Backend": row.backend_id,
        "Family": row.backend_family,
        "Section / Requirement": row.section_or_requirement,
        "Status": row.current_status,
        "Next action": row.recommended_next_action,
        "Source": row.source_artifact,
        "Evidence": ", ".join(row.evidence_tests) if row.evidence_tests else "-",
    }


def _portico_backend_ids() -> tuple[str, ...]:
    return DISCOVERY_POLICY.portico_backend_ids


def _portico_rows_by_backend(rows: list[VendorBacklogRow]) -> dict[str, VendorBacklogRow]:
    return {
        row.backend_id: row
        for row in rows
        if row.backend_id in _portico_backend_ids()
    }


def _assert_portico_catalog_row(row: BackendCatalogRow, backend_id: str) -> None:
    assert row.backend_family == DISCOVERY_POLICY.family
    assert row.matrices_present == DISCOVERY_POLICY.matrices_present
    assert row.status_counts[DISCOVERY_POLICY.classification_status] > 0
    assert DISCOVERY_POLICY.section_ref in row.section_refs


def _assert_portico_backlog_row(row: VendorBacklogRow, backend_id: str) -> None:
    assert row.current_status == DISCOVERY_POLICY.classification_status, backend_id
    assert row.backend_family == DISCOVERY_POLICY.family, backend_id
    assert row.recommended_next_action == DISCOVERY_POLICY.recommended_next_action, backend_id
    assert row.row_kind == DISCOVERY_POLICY.row_kind, backend_id
    assert row.scope == DISCOVERY_POLICY.scope, backend_id
    assert row.source_artifact.endswith(f"{backend_id}_requirement_disposition.json"), backend_id


def test_discovery_catalog_surfaces_portico_disposition_only_backends() -> None:
    payload = build_discovery_payload(".")
    backends = {row.backend_id: row for row in _catalog_rows(payload)}

    for backend_id in _portico_backend_ids():
        assert backend_id in backends, backend_id
        _assert_portico_catalog_row(backends[backend_id], backend_id)


def test_discovery_catalog_backend_filter_keeps_portico_disposition_only_profile() -> None:
    payload = build_discovery_payload(".", backend_filter=DISCOVERY_POLICY.filtered_backend)

    assert payload["catalog"]["summary"]["backend_count"] == 1
    backend = _catalog_rows(payload)[0]
    assert backend.backend_id == DISCOVERY_POLICY.filtered_backend
    _assert_portico_catalog_row(backend, DISCOVERY_POLICY.filtered_backend)


def test_discovery_text_renders_portico_disposition_only_profile() -> None:
    payload = build_discovery_payload(".", backend_filter=DISCOVERY_POLICY.filtered_backend)
    text = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter=DISCOVERY_POLICY.filtered_backend,
        backlog=payload["backlog"],
    )

    assert_contains_all(text, DISCOVERY_POLICY.catalog_text_fragments)


def test_vendor_backlog_surfaces_portico_disposition_only_backends() -> None:
    payload = build_discovery_payload(".")
    rows_by_backend = _portico_rows_by_backend(
        [VendorBacklogRow.from_mapping(row) for row in payload["backlog"]["rows"]]
    )

    assert set(rows_by_backend) == set(_portico_backend_ids())
    for backend_id, row in rows_by_backend.items():
        _assert_portico_backlog_row(row, backend_id)


def test_discovery_text_backlog_renders_portico_disposition_only_profile() -> None:
    payload = build_discovery_payload(".", backend_filter=DISCOVERY_POLICY.filtered_backend)
    text = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter=DISCOVERY_POLICY.filtered_backend,
        backlog=payload["backlog"],
    )

    assert_contains_all(text, DISCOVERY_POLICY.backlog_text_fragments)


def test_committed_vendor_backlog_artifacts_surface_portico_disposition_only_rows() -> None:
    payload = load_compliance_json("vendor_discovery_backlog.json")
    rows_by_backend = _portico_rows_by_backend(_backlog_rows(payload))

    assert set(rows_by_backend) == set(_portico_backend_ids())
    for backend_id, row in rows_by_backend.items():
        _assert_portico_backlog_row(row, backend_id)

    markdown_path = ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.md"
    text = read(markdown_path)
    assert_contains_all(text, DISCOVERY_POLICY.committed_markdown_required_fragments, path=markdown_path)
    assert_absent_all(text, DISCOVERY_POLICY.committed_markdown_forbidden_fragments, path=markdown_path)


def test_committed_vendor_backlog_markdown_matches_json_packet() -> None:
    json_path = ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.json"
    markdown_path = ROOT / "analysis" / "compliance" / "vendor_discovery_backlog.md"
    payload = load_compliance_json("vendor_discovery_backlog.json")
    text = load_compliance_text("vendor_discovery_backlog.md")
    backlog_rows = _backlog_rows(payload)

    assert f"- Rows: {payload['summary']['row_count']}" in text
    assert _markdown_summary_counts(text, "Status counts") == payload["summary"]["status_counts"]
    assert _markdown_summary_counts(text, "Priority counts") == payload["summary"]["priority_counts"]
    assert _markdown_table(markdown_path) == [
        _stringify_backlog_row(row)
        for row in backlog_rows
    ]
