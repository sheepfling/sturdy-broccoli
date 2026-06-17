from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_vendor_green_stub(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

profile = sys.argv[1]
record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
state_path = Path(os.environ["HLA2010_TEST_STATE_FILE"])
exit_codes = [int(item) for item in os.environ["HLA2010_TEST_EXIT_CODES"].split(",")]
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"index": 0}
index = state["index"]
exit_code = exit_codes[index]
state["index"] = index + 1
state_path.write_text(json.dumps(state), encoding="utf-8")
records = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
records.append({"profile": profile, "exit_code": exit_code})
record_path.write_text(json.dumps(records, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(exit_code)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _write_ci_state_stub(path: Path, *, exit_code: int) -> None:
    path.write_text(
        f"""#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

record_path = Path(os.environ["HLA2010_TEST_CI_STATE_RECORD_FILE"])
records = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
records.append({{"argv": sys.argv[1:]}})
record_path.write_text(json.dumps(records, indent=2) + "\\n", encoding="utf-8")
raise SystemExit({exit_code})
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_vendor_probe_stability_reports_repeated_probe_success(tmp_path: Path) -> None:
    stub = tmp_path / "vendor_green_stub.py"
    _write_vendor_green_stub(stub)
    env = os.environ.copy()
    env["HLA2010_VENDOR_PROBE_STABILITY_VENDOR_GREEN"] = str(stub)
    env["HLA2010_VENDOR_PROBE_STABILITY_DIR"] = str(tmp_path / "stability")
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_TEST_STATE_FILE"] = str(tmp_path / "state.json")
    env["HLA2010_TEST_EXIT_CODES"] = "0,0,0"
    env["HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE"] = "0"

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_stability.sh", "pitch-negotiated-probe", "3"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    summary_path = tmp_path / "stability" / "pitch-negotiated-probe" / "vendor_probe_stability_summary.json"
    report_path = tmp_path / "stability" / "pitch-negotiated-probe" / "vendor_probe_stability_report.md"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-negotiated-probe"
    assert payload["evidence_tier"] == "probe"
    assert payload["command"] == "./tools/pitch negotiated-probe"
    assert payload["executor_command"] == f"{stub} pitch-negotiated-probe"
    assert payload["repeat_count"] == 3
    assert payload["success_count"] == 3
    assert payload["failure_count"] == 0
    assert payload["stable"] is True
    assert payload["promotion_readiness"] == "needs-more-runs"
    assert len(payload["attempts"]) == 3
    report_text = report_path.read_text(encoding="utf-8")
    assert "Vendor Probe Stability" in report_text
    assert "`stable`: `True`" not in report_text
    assert "- stable: `True`" in report_text
    assert "- command: `./tools/pitch negotiated-probe`" in report_text
    assert f"- executor command: `{stub} pitch-negotiated-probe`" in report_text
    assert "- promotion readiness: `needs-more-runs`" in report_text
    records = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert records == [
        {"profile": "pitch-negotiated-probe", "exit_code": 0},
        {"profile": "pitch-negotiated-probe", "exit_code": 0},
        {"profile": "pitch-negotiated-probe", "exit_code": 0},
    ]


def test_vendor_probe_stability_reports_failure_when_any_attempt_fails(tmp_path: Path) -> None:
    stub = tmp_path / "vendor_green_stub.py"
    _write_vendor_green_stub(stub)
    env = os.environ.copy()
    env["HLA2010_VENDOR_PROBE_STABILITY_VENDOR_GREEN"] = str(stub)
    env["HLA2010_VENDOR_PROBE_STABILITY_DIR"] = str(tmp_path / "stability")
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_TEST_STATE_FILE"] = str(tmp_path / "state.json")
    env["HLA2010_TEST_EXIT_CODES"] = "0,7,0"
    env["HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE"] = "0"

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_stability.sh", "certi-ddm-probe", "3"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    summary_path = tmp_path / "stability" / "certi-ddm-probe" / "vendor_probe_stability_summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-ddm-probe"
    assert payload["evidence_tier"] == "probe"
    assert payload["command"] == "./tools/certi-easy ddm-probe"
    assert payload["executor_command"] == f"{stub} certi-ddm-probe"
    assert payload["success_count"] == 2
    assert payload["failure_count"] == 1
    assert payload["stable"] is False
    assert payload["promotion_readiness"] == "unstable"
    assert payload["attempts"][1]["exit_code"] == 7


def test_vendor_probe_stability_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    attempts_file = tmp_path / "attempts.csv"
    attempts_file.write_text(
        "iteration,exit_code,duration_seconds\n"
        "1,0,2\n"
        "2,0,3\n"
        "3,0,4\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/ci/write_vendor_probe_stability.py",
            "--profile",
            "pitch-negotiated-probe",
            "--repeat-count",
            "3",
            "--attempts-file",
            str(attempts_file),
            "--output-dir",
            str(tmp_path / "stability"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "stability" / "vendor_probe_stability_summary.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-negotiated-probe"
    assert payload["command"] == "./tools/pitch negotiated-probe"
    assert payload["success_count"] == 3


def test_vendor_probe_stability_ci_validation_blocks_attempt_loop_on_invalid_runtime_state(tmp_path: Path) -> None:
    stub = tmp_path / "vendor_green_stub.py"
    ci_state = tmp_path / "ci_state_stub.py"
    _write_vendor_green_stub(stub)
    _write_ci_state_stub(ci_state, exit_code=1)
    env = os.environ.copy()
    env["GITHUB_ACTIONS"] = "true"
    env["HLA2010_VENDOR_PROBE_STABILITY_VENDOR_GREEN"] = str(stub)
    env["HLA2010_VENDOR_PROBE_STABILITY_DIR"] = str(tmp_path / "stability")
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_TEST_STATE_FILE"] = str(tmp_path / "state.json")
    env["HLA2010_TEST_EXIT_CODES"] = "0,0,0"
    env["HLA2010_TEST_CI_STATE_RECORD_FILE"] = str(tmp_path / "ci-state-record.json")
    env["HLA2010_VENDOR_RUNTIME_CI_STATE_DIR"] = str(tmp_path / "runtime-ci-state")
    env["HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE"] = "1"
    env["HLA2010_VENDOR_PROBE_CI_STATE_CMD"] = str(ci_state)

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_stability.sh", "pitch-negotiated-probe", "3"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert not (tmp_path / "record.json").exists()
    records = json.loads((tmp_path / "ci-state-record.json").read_text(encoding="utf-8"))
    assert records == [{"argv": ["--profile", "pitch", "--output-dir", str(tmp_path / "runtime-ci-state")]}]


def test_vendor_probe_stability_ci_validation_runs_once_before_repeated_attempts(tmp_path: Path) -> None:
    stub = tmp_path / "vendor_green_stub.py"
    ci_state = tmp_path / "ci_state_stub.py"
    _write_vendor_green_stub(stub)
    _write_ci_state_stub(ci_state, exit_code=0)
    env = os.environ.copy()
    env["GITHUB_ACTIONS"] = "true"
    env["HLA2010_VENDOR_PROBE_STABILITY_VENDOR_GREEN"] = str(stub)
    env["HLA2010_VENDOR_PROBE_STABILITY_DIR"] = str(tmp_path / "stability")
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")
    env["HLA2010_TEST_STATE_FILE"] = str(tmp_path / "state.json")
    env["HLA2010_TEST_EXIT_CODES"] = "0,0,0"
    env["HLA2010_TEST_CI_STATE_RECORD_FILE"] = str(tmp_path / "ci-state-record.json")
    env["HLA2010_VENDOR_RUNTIME_CI_STATE_DIR"] = str(tmp_path / "runtime-ci-state")
    env["HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE"] = "1"
    env["HLA2010_VENDOR_PROBE_CI_STATE_CMD"] = str(ci_state)

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_stability.sh", "certi-ddm-probe", "3"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    records = json.loads((tmp_path / "ci-state-record.json").read_text(encoding="utf-8"))
    assert records == [{"argv": ["--profile", "certi", "--output-dir", str(tmp_path / "runtime-ci-state")]}]
    probe_records = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert len(probe_records) == 3
