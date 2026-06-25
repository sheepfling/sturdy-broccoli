from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.verification.pitch_202x_micro_certification import (
    write_pitch_202x_micro_certification,
)


ROOT = Path(__file__).resolve().parents[2]


def _micro_summary_fixture() -> dict[str, object]:
    return {
        "suite_name": "siso-pitch-micro-parity",
        "selected_scenario_count": 12,
        "passed": 12,
        "skipped": 0,
        "failed": 0,
        "results": [
            {
                "scenario": "link16-rpr2-integrated-2010-micro-2",
                "family": "link16",
                "runtime_edition": "2010",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "link16-rpr2-integrated",
                "backend": "pitch-jpype",
                "counts_as_vendor_runtime": True,
                "vendor_notes": "real",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 1,
            },
            {
                "scenario": "link16-rpr2-integrated-2010-micro-2",
                "family": "link16",
                "runtime_edition": "2010",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "link16-rpr2-integrated",
                "backend": "pitch-py4j",
                "counts_as_vendor_runtime": True,
                "vendor_notes": "real",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 1,
            },
            {
                "scenario": "link16-rpr2-integrated-2025-micro-2",
                "family": "link16",
                "runtime_edition": "2025",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "link16-rpr2-integrated",
                "backend": "pitch-202x-jpype",
                "counts_as_vendor_runtime": False,
                "vendor_notes": "bounded",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 1,
            },
            {
                "scenario": "link16-rpr2-integrated-2025-micro-2",
                "family": "link16",
                "runtime_edition": "2025",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "link16-rpr2-integrated",
                "backend": "pitch-202x-py4j",
                "counts_as_vendor_runtime": False,
                "vendor_notes": "bounded",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 1,
            },
            {
                "scenario": "rpr-runtime-2010-micro-2",
                "family": "rpr",
                "runtime_edition": "2010",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "rpr3-merged-informative-1516-2010",
                "backend": "pitch-jpype",
                "counts_as_vendor_runtime": True,
                "vendor_notes": "real",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 2,
            },
            {
                "scenario": "rpr-runtime-2010-micro-2",
                "family": "rpr",
                "runtime_edition": "2010",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "rpr3-merged-informative-1516-2010",
                "backend": "pitch-py4j",
                "counts_as_vendor_runtime": True,
                "vendor_notes": "real",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 2,
            },
            {
                "scenario": "rpr-runtime-2025-micro-2",
                "family": "rpr",
                "runtime_edition": "2025",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "rpr3-annex-a-normative",
                "backend": "pitch-202x-jpype",
                "counts_as_vendor_runtime": False,
                "vendor_notes": "bounded",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 2,
            },
            {
                "scenario": "rpr-runtime-2025-micro-2",
                "family": "rpr",
                "runtime_edition": "2025",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "rpr3-annex-a-normative",
                "backend": "pitch-202x-py4j",
                "counts_as_vendor_runtime": False,
                "vendor_notes": "bounded",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 1,
                "reflections": 1,
                "interactions": 2,
            },
            {
                "scenario": "space-fom-core-2010-micro-2",
                "family": "space",
                "runtime_edition": "2010",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "space-fom-core",
                "backend": "pitch-jpype",
                "counts_as_vendor_runtime": True,
                "vendor_notes": "real",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 2,
                "reflections": 3,
                "interactions": 0,
            },
            {
                "scenario": "space-fom-core-2010-micro-2",
                "family": "space",
                "runtime_edition": "2010",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "space-fom-core",
                "backend": "pitch-py4j",
                "counts_as_vendor_runtime": True,
                "vendor_notes": "real",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 2,
                "reflections": 3,
                "interactions": 0,
            },
            {
                "scenario": "space-fom-core-2025-micro-2",
                "family": "space",
                "runtime_edition": "2025",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "space-fom-core",
                "backend": "pitch-202x-jpype",
                "counts_as_vendor_runtime": False,
                "vendor_notes": "bounded",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 2,
                "reflections": 3,
                "interactions": 0,
            },
            {
                "scenario": "space-fom-core-2025-micro-2",
                "family": "space",
                "runtime_edition": "2025",
                "topology": "micro-2",
                "federate_count": 2,
                "source_packet": "space-fom-core",
                "backend": "pitch-202x-py4j",
                "counts_as_vendor_runtime": False,
                "vendor_notes": "bounded",
                "status": "passed",
                "reason": None,
                "execution_complete": True,
                "discoveries": 2,
                "reflections": 3,
                "interactions": 0,
            },
        ],
    }


def test_write_pitch_202x_micro_certification_emits_comparison_packet(tmp_path: Path) -> None:
    paths = write_pitch_202x_micro_certification(
        tmp_path,
        project_root=ROOT,
        micro_summary=_micro_summary_fixture(),
        command_runs=[
            {"id": "preflight", "label": "preflight", "command": "./tools/pitch preflight", "exit_code": 0, "duration_seconds": 1.2},
            {"id": "micro-parity", "label": "micro parity", "command": "./tools/pitch 202x-micro-certify", "exit_code": 0, "duration_seconds": 12.0},
        ],
    )

    payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "pitch-202x-micro-certification"
    assert payload["certification_state"] == "bounded-vendor-comparison"
    assert len(payload["comparison_rows"]) == 6
    assert any(row["bridge"] == "jpype" and row["family"] == "rpr" for row in payload["comparison_rows"])

    with paths.comparison_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert any(row["status_2010"] == "passed" and row["status_2025"] == "passed" for row in rows)

    report = paths.report_markdown.read_text(encoding="utf-8")
    assert "Pitch 202X Micro Certification" in report
    assert "behavior-discovery evidence" in report
    assert "./tools/pitch 202x-micro-certify" in report


def _write_micro_cert_stub(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
records = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
records.append({"argv": sys.argv[1:]})
record_path.write_text(json.dumps(records, indent=2) + "\\n", encoding="utf-8")

if "--output-dir" in sys.argv:
    output_dir = Path(sys.argv[sys.argv.index("--output-dir") + 1])
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(Path(os.environ["HLA2010_TEST_MICRO_SUMMARY_FILE"]).read_text(encoding="utf-8"))
    (output_dir / "siso_pitch_micro_parity_summary.json").write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
    (output_dir / "siso_pitch_micro_parity_results.csv").write_text("scenario\\nplaceholder\\n", encoding="utf-8")
    (output_dir / "siso_pitch_micro_parity_manifest.json").write_text("{\\"schema_version\\": \\"stub\\"}\\n", encoding="utf-8")
    (output_dir / "siso_pitch_micro_parity_report.md").write_text("# Stub\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_run_pitch_202x_micro_certification_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    stub = tmp_path / "success_stub.py"
    _write_micro_cert_stub(stub)
    fixture_path = tmp_path / "micro_summary.json"
    fixture_path.write_text(json.dumps(_micro_summary_fixture(), indent=2) + "\n", encoding="utf-8")
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HLA2010_TEST_RECORD_FILE": str(tmp_path / "record.json"),
        "HLA2010_TEST_MICRO_SUMMARY_FILE": str(fixture_path),
        "HLA2010_PITCH_202X_MICRO_CERTIFY_PREFLIGHT_CMD": f"{sys.executable} {stub}",
        "HLA2010_PITCH_202X_MICRO_CERTIFY_MICRO_PARITY_CMD": f"{sys.executable} {stub}",
    }

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_pitch_202x_micro_certification.py",
            "--output-dir",
            str(tmp_path / "certification"),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "certification" / "pitch_202x_micro_certification_summary.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "pitch-202x-micro-certification"
    assert payload["executed_runs"][1]["id"] == "micro-parity"
    records = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert len(records) == 2


def test_pitch_top_level_wrapper_runs_202x_micro_certification(tmp_path: Path) -> None:
    stub = tmp_path / "success_stub.py"
    _write_micro_cert_stub(stub)
    fixture_path = tmp_path / "micro_summary.json"
    fixture_path.write_text(json.dumps(_micro_summary_fixture(), indent=2) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_TEST_MICRO_SUMMARY_FILE"] = str(fixture_path)
    env["HLA2010_PITCH_202X_MICRO_CERTIFY_PREFLIGHT_CMD"] = f"{sys.executable} {stub}"
    env["HLA2010_PITCH_202X_MICRO_CERTIFY_MICRO_PARITY_CMD"] = f"{sys.executable} {stub}"

    result = subprocess.run(
        ["bash", "./tools/pitch", "202x-micro-certify"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "pitch_202x_micro_certification_summary.json" in result.stdout
