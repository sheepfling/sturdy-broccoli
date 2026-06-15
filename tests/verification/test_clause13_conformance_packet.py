from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import hla2010
from hla2010_repo_internal.verification.clause13_conformance import (
    build_clause13_conformance_packet,
    write_clause13_conformance_packet_json,
    write_clause13_conformance_packet_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = REPO_ROOT / "docs" / "verification" / "clause13_conformance_packet.json"
MD_PATH = REPO_ROOT / "docs" / "verification" / "clause13_conformance_packet.md"


def test_clause13_conformance_packet_matches_generated_json():
    expected = build_clause13_conformance_packet(REPO_ROOT, version=hla2010.__version__)
    actual = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    assert actual == expected


def test_clause13_conformance_packet_backs_federate_and_rti_claims():
    packet = build_clause13_conformance_packet(REPO_ROOT, version=hla2010.__version__)

    assert packet["federate_conformance"]["claim_backed"] is True
    assert packet["rti_conformance"]["claim_backed"] is True
    assert packet["aggregate_counts"]["requirements_ledger_pass_rows"] == 217
    assert packet["aggregate_counts"]["explicit_requirement_marker_count"] > 0
    assert packet["aggregate_counts"]["callback_tested_row_count"] > 0
    assert packet["aggregate_counts"]["rti_rows_with_negative_refs"] > 0

    federate_categories = {
        category["name"]: category
        for category in packet["federate_conformance"]["categories"]
    }
    assert {"FM", "DM", "OM", "OWN", "TM", "DDM", "SUP"} <= set(
        federate_categories["standard_service_usage"]["requirement_marker_families"]
    )
    assert federate_categories["object_models"]["capability_counts"]["CAP-MOM"]["mapped"] > 0
    assert federate_categories["object_models"]["capability_counts"]["CAP-OMT"]["mapped"] > 0
    assert federate_categories["object_models"]["capability_counts"]["CAP-XML"]["mapped"] > 0


def test_clause13_conformance_packet_writers_emit_review_assets(tmp_path: Path):
    json_path = write_clause13_conformance_packet_json(
        tmp_path / "clause13.json", REPO_ROOT, version=hla2010.__version__
    )
    md_path = write_clause13_conformance_packet_markdown(
        tmp_path / "clause13.md", REPO_ROOT, version=hla2010.__version__
    )

    assert json.loads(json_path.read_text(encoding="utf-8"))["scope"].startswith(
        "IEEE 1516.1-2010 Clause 13"
    )
    md_text = md_path.read_text(encoding="utf-8")
    assert "## Federate conformance" in md_text
    assert "## RTI conformance" in md_text
    assert "claim_backed: True" in md_text


def test_clause13_conformance_markdown_is_committed():
    text = MD_PATH.read_text(encoding="utf-8")

    assert text.startswith(f"# Clause 13 Conformance Packet v{hla2010.__version__}")
    assert "## Federate conformance" in text
    assert "## RTI conformance" in text


def test_clause13_generator_script_bootstraps_source_checkout():
    result = subprocess.run(
        [sys.executable, "scripts/generate_clause13_conformance_packet.py"],
        cwd=REPO_ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
