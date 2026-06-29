from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.requirements_backlog import write_imported_hla_backlog


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_imported_hla_backlog_is_generated_with_expected_families(tmp_path: Path):
    markdown_path = tmp_path / "imported_requirements_backlog_v1_0.md"
    json_path = tmp_path / "imported_requirements_backlog_v1_0.json"

    written = write_imported_hla_backlog(markdown_path, json_path)

    assert written["markdown"] == markdown_path
    assert written["json"] == json_path

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Imported HLA Requirements Backlog v1.0" in markdown
    assert "## Federation Management" in markdown
    assert "## MOM/MIM" in markdown
    assert "## Transports" in markdown
    assert "mapping-bridge work projection" in markdown
    assert "does not define requirement truth" in markdown

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    families = [family["family"] for family in payload["families"]]
    assert families == [
        "Federation Management",
        "Declaration Management",
        "Object Management",
        "Ownership Management",
        "Time Management",
        "Data Distribution Management",
        "Support Services",
        "MOM/MIM",
        "OMT",
        "XML",
        "Transports",
    ]
    assert payload["canonical_requirement_artifact"] == "requirements/2010/canonical_requirements.json"
    assert payload["canonical_requirement_row_count"] == 880
    assert payload["canonical_requirement_status_counts"] == {"pass": 880}
    assert payload["backlog_surface_class"] == "generated-mapping-bridge-backlog"
    assert payload["source_artifact_classes"]["requirements/2010/hla1516_1_clause_8_tm_detailed_reconciliation.csv"] == "mapping-bridge"
    assert payload["source_artifact_classes"]["requirements/2010/hla1516_2_omt.csv"] == "import-history"
    assert payload["total_open_rows"] == 0
    assert all(family["open_row_count"] == 0 for family in payload["families"])
    federation_management = next(family for family in payload["families"] if family["family"] == "Federation Management")
    assert federation_management["queue_items"] == []
    assert federation_management["open_row_count"] == 0


def test_imported_hla_backlog_script_bootstraps_source_checkout(tmp_path: Path):
    markdown_path = tmp_path / "imported_requirements_backlog_v1_0.md"
    json_path = tmp_path / "imported_requirements_backlog_v1_0.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_imported_packet_backlog.py",
            "--markdown",
            str(markdown_path),
            "--json",
            str(json_path),
        ],
        cwd=REPO_ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert markdown_path.exists()
    assert json_path.exists()


def test_imported_hla_backlog_does_not_queue_clause6_precondition_rows_already_closed_by_the_canonical_owner_surface(
    tmp_path: Path,
):
    markdown_path = tmp_path / "imported_requirements_backlog_v1_0.md"
    json_path = tmp_path / "imported_requirements_backlog_v1_0.json"

    write_imported_hla_backlog(markdown_path, json_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    queued_ids = {
        requirement_id
        for family in payload["families"]
        for item in family["queue_items"]
        for requirement_id in item["requirement_ids"]
    }

    for requirement_id in (
        "HLA1516.1-OM-6_2-PRE-004",
        "HLA1516.1-OM-6_2-ARG-003",
        "HLA1516.1-OM-6_2-EFF-005",
        "HLA1516.1-OM-6_2-EXC-006",
        "HLA1516.1-OM-6_3-ARG-003",
        "HLA1516.1-OM-6_3-PRE-004",
        "HLA1516.1-OM-6_3-EXC-006",
        "HLA1516.1-OM-6_4-ARG-003",
        "HLA1516.1-OM-6_4-PRE-004",
        "HLA1516.1-OM-6_4-EFF-005",
        "HLA1516.1-OM-6_4-EXC-006",
        "HLA1516.1-OM-6_5-ARG-003",
        "HLA1516.1-OM-6_5-PRE-004",
        "HLA1516.1-OM-6_5-EFF-005",
        "HLA1516.1-OM-6_5-EXC-006",
        "HLA1516.1-OM-6_6-ARG-003",
        "HLA1516.1-OM-6_6-PRE-004",
        "HLA1516.1-OM-6_6-EXC-006",
        "HLA1516.1-OM-6_7-ARG-003",
        "HLA1516.1-OM-6_7-PRE-004",
        "HLA1516.1-OM-6_7-EFF-005",
        "HLA1516.1-OM-6_7-EXC-006",
        "HLA1516.1-OM-6_8-PRE-004",
        "HLA1516.1-OM-6_8-EFF-005",
        "HLA1516.1-OM-6_8-EXC-006",
        "HLA1516.1-OM-6_9-ARG-003",
        "HLA1516.1-OM-6_9-PRE-004",
        "HLA1516.1-OM-6_9-EXC-006",
        "HLA1516.1-OM-6_10-EFF-005",
        "HLA1516.1-OM-6_10-PRE-004",
        "HLA1516.1-OM-6_10-EXC-006",
        "HLA1516.1-OM-6_12-PRE-004",
        "HLA1516.1-OM-6_13-ARG-003",
        "HLA1516.1-OM-6_13-PRE-004",
        "HLA1516.1-OM-6_13-EXC-006",
        "HLA1516.1-OM-6_14-EFF-005",
        "HLA1516.1-OM-6_14-PRE-004",
        "HLA1516.1-OM-6_14-EXC-006",
        "HLA1516.1-OM-6_15-ARG-003",
        "HLA1516.1-OM-6_15-PRE-004",
        "HLA1516.1-OM-6_15-EXC-006",
        "HLA1516.1-OM-6_16-EFF-005",
        "HLA1516.1-OM-6_16-PRE-004",
        "HLA1516.1-OM-6_16-EXC-006",
        "HLA1516.1-OM-6_17-ARG-003",
        "HLA1516.1-OM-6_17-PRE-004",
        "HLA1516.1-OM-6_17-EXC-006",
        "HLA1516.1-OM-6_18-ARG-003",
        "HLA1516.1-OM-6_18-PRE-004",
        "HLA1516.1-OM-6_18-EXC-006",
        "HLA1516.1-OM-6_19-EXC-006",
        "HLA1516.1-OM-6_19-PRE-004",
        "HLA1516.1-OM-6_23-SVC-001",
        "HLA1516.1-OM-6_23-EFF-005",
        "HLA1516.1-OM-6_23-EXC-006",
        "HLA1516.1-OM-6_24-SVC-001",
        "HLA1516.1-OM-6_24-ARG-003",
        "HLA1516.1-OM-6_24-PRE-004",
        "HLA1516.1-OM-6_24-EFF-005",
        "HLA1516.1-OM-6_24-EXC-006",
        "HLA1516.1-OM-6_25-SVC-001",
        "HLA1516.1-OM-6_25-EFF-005",
        "HLA1516.1-OM-6_25-EXC-006",
        "HLA1516.1-OM-6_26-SVC-001",
        "HLA1516.1-OM-6_26-ARG-003",
        "HLA1516.1-OM-6_26-PRE-004",
        "HLA1516.1-OM-6_26-EFF-005",
        "HLA1516.1-OM-6_26-EXC-006",
        "HLA1516.1-OM-6_27-SVC-001",
        "HLA1516.1-OM-6_27-EFF-005",
        "HLA1516.1-OM-6_27-EXC-006",
        "HLA1516.1-OM-6_28-SVC-001",
        "HLA1516.1-OM-6_28-ARG-003",
        "HLA1516.1-OM-6_28-PRE-004",
        "HLA1516.1-OM-6_28-EFF-005",
        "HLA1516.1-OM-6_28-EXC-006",
        "HLA1516.1-OM-6_29-SVC-001",
        "HLA1516.1-OM-6_29-EFF-005",
        "HLA1516.1-OM-6_29-EXC-006",
        "HLA1516.1-OM-6_30-SVC-001",
        "HLA1516.1-OM-6_30-ARG-003",
        "HLA1516.1-OM-6_30-PRE-004",
        "HLA1516.1-OM-6_30-EFF-005",
        "HLA1516.1-OM-6_30-EXC-006",
    ):
        assert requirement_id not in queued_ids
