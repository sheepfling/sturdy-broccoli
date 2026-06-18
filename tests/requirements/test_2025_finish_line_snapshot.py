from __future__ import annotations

import json
from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import (
    build_spec2025_finish_line_markdown,
    build_spec2025_finish_line_snapshot,
    write_spec2025_finish_line,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_finish_line_snapshot_keeps_scope_counts_and_open_work_honest() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    assert snapshot["scope"] == "IEEE 1516-2025 requirements finish-line inventory, not a conformance claim"
    assert snapshot["registry"]["initial_tranche_requirements"] == 28
    assert "hla-2025-executable-test-requirements-v3" in snapshot["registry"]["imported_packets"]

    executable = snapshot["executable_test_backlog"]
    assert executable["row_count"] == 1117
    assert executable["source_rows"] == 398
    assert executable["by_test_kind"]["surface_contract"] == 196
    assert executable["by_test_kind"]["validator_positive_fixture"] == 158
    assert executable["by_test_kind"]["validator_negative_fixture"] == 158

    backlog = snapshot["completion_backlog"]
    assert backlog["by_bucket"]["new-2025-requirements"] == 7
    assert backlog["by_current_status"]["implemented-slice"] >= 3
    assert backlog["by_current_status"]["partial"] >= 3
    assert backlog["by_current_status"]["planned"] >= 10
    assert backlog["high_priority_open_count"] > 10

    open_ids = {row["id"] for row in backlog["high_priority_open"]}
    assert {"HLA2025-NEW-001", "HLA2025-MOD-004", "HLA2025-BND-001", "HLA2025-BND-002"} <= open_ids
    assert "HLA2025-NEW-002" not in open_ids
    assert "HLA2025-NEW-005" not in open_ids


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-TRACE-001")
def test_2025_finish_line_snapshot_names_only_implemented_slices_with_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    slices = {row["id"]: row for row in snapshot["implemented_evidence_slices"]}

    assert slices["2025-auth-connect"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-001" in slices["2025-auth-connect"]["requirements"]
    assert any(path.endswith("test_rti1516_2025_encoding_auth_contexts.py") for path in slices["2025-auth-connect"]["evidence"])

    assert slices["2025-logical-time"]["status"] == "partial"
    assert "flushQueueGrant" in slices["2025-logical-time"]["remaining"]

    markdown = "\n".join(build_spec2025_finish_line_markdown(ROOT))
    assert "HLA conformance" in markdown
    assert "Highest-Priority Open Work" in markdown
    assert "HLA2025-NEW-001" in markdown
    assert "Do not promote `partial` rows" in markdown


@pytest.mark.requirements("HLA2025-TRACE-001")
def test_2025_finish_line_writer_emits_reviewable_json_and_markdown(tmp_path: Path) -> None:
    paths = write_spec2025_finish_line(tmp_path, ROOT)

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["executable_test_backlog"]["row_count"] == 1117

    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert markdown.startswith("# IEEE 1516-2025 Requirements Finish Line")
    assert "Implemented Evidence Slices" in markdown
