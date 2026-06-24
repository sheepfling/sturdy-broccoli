from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hla.verification.repo_internal.verification.pitch_202x_certification import write_pitch_202x_certification


ROOT = Path(__file__).resolve().parents[2]


def test_write_pitch_202x_certification_emits_trial_safe_packet(tmp_path: Path) -> None:
    paths = write_pitch_202x_certification(
        tmp_path,
        project_root=ROOT,
        command_runs=[
            {"id": "preflight", "label": "preflight", "command": "./tools/pitch preflight", "exit_code": 0, "duration_seconds": 1.2},
            {"id": "surface-audit", "label": "surface audit", "command": "python3 scripts/report_pitch_202x_surface.py", "exit_code": 0, "duration_seconds": 0.8},
            {"id": "smoke", "label": "smoke", "command": "./tools/pitch smoke", "exit_code": 0, "duration_seconds": 4.0},
            {"id": "time-window-future-exclusion", "label": "time window future exclusion", "command": "./tools/pitch time-window-probe", "exit_code": 0, "duration_seconds": 5.0},
            {"id": "time-window-restore-state", "label": "time window restore state", "command": "./tools/pitch time-window-restore-state-probe", "exit_code": 0, "duration_seconds": 5.5},
        ],
    )

    payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "pitch-202x-certification"
    assert payload["certification_state"] == "vendor-credence-candidate"
    assert payload["surface_audit"]["vendor_label"] == "Pitch pRTI Free"
    assert payload["time_window_vendor_parity_audit"]["current_trial_candidate"]["scenario_id"] == "time-window-future-exclusion"
    scenario_ids = {row["scenario_id"] for row in payload["trial_safe_scenario_allowlist"]}
    assert "exchange-smoke" in scenario_ids
    assert "time-window-future-exclusion" in scenario_ids
    assert "time-window-restore-state" in scenario_ids
    assert "time-window-restore-output" not in scenario_ids
    assert any(row["area"] == "negotiated-ownership" for row in payload["known_boundaries"])

    report_text = paths.report_markdown.read_text(encoding="utf-8")
    assert "Pitch 202X Certification Packet" in report_text
    assert "./tools/pitch time-window-probe" in report_text
    assert "./tools/pitch time-window-restore-state-probe" in report_text


def _write_success_stub(path: Path) -> None:
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
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_run_pitch_202x_certification_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    stub = tmp_path / "success_stub.py"
    _write_success_stub(stub)
    env = {"PATH": os.environ.get("PATH", ""), "HLA2010_TEST_RECORD_FILE": str(tmp_path / "record.json")}
    for name in (
        "HLA2010_PITCH_202X_CERTIFY_PREFLIGHT_CMD",
        "HLA2010_PITCH_202X_CERTIFY_SURFACE_CMD",
        "HLA2010_PITCH_202X_CERTIFY_SMOKE_CMD",
        "HLA2010_PITCH_202X_CERTIFY_TIME_WINDOW_CMD",
        "HLA2010_PITCH_202X_CERTIFY_RESTORE_STATE_CMD",
    ):
        env[name] = f"{sys.executable} {stub}"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_pitch_202x_certification.py",
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
    summary_path = tmp_path / "certification" / "pitch_202x_certification_summary.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "pitch-202x-certification"
    assert payload["executed_runs"][0]["id"] == "preflight"
    records = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert len(records) == 5


def test_pitch_top_level_wrapper_runs_202x_certification(tmp_path: Path) -> None:
    stub = tmp_path / "success_stub.py"
    _write_success_stub(stub)
    env = os.environ.copy()
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_PITCH_202X_CERTIFY_PREFLIGHT_CMD"] = f"{sys.executable} {stub}"
    env["HLA2010_PITCH_202X_CERTIFY_SURFACE_CMD"] = f"{sys.executable} {stub}"
    env["HLA2010_PITCH_202X_CERTIFY_SMOKE_CMD"] = f"{sys.executable} {stub}"
    env["HLA2010_PITCH_202X_CERTIFY_TIME_WINDOW_CMD"] = f"{sys.executable} {stub}"
    env["HLA2010_PITCH_202X_CERTIFY_RESTORE_STATE_CMD"] = f"{sys.executable} {stub}"

    result = subprocess.run(
        ["bash", "./tools/pitch", "202x-certify"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "pitch_202x_certification_summary.json" in result.stdout
