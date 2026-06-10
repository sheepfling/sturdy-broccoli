from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from hla2010_repo_internal.verification.vendor_runner_template_drift import (
    build_vendor_runner_template_drift,
    write_vendor_runner_template_drift,
)


ROOT = Path(__file__).resolve().parents[2]


def test_vendor_runner_template_matches_validator_and_workflows() -> None:
    summary = build_vendor_runner_template_drift()

    assert summary["exit_code"] == 0
    assert all(row["ok"] for row in summary["profiles"])


def test_write_vendor_runner_template_drift_emits_artifacts(tmp_path: Path) -> None:
    paths = write_vendor_runner_template_drift(tmp_path)

    payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "vendor-runner-template-drift"
    assert payload["exit_code"] == 0
    report = paths.report_markdown.read_text(encoding="utf-8")
    assert "Vendor Runner Template Drift" in report
    assert "certi" in report


def test_drift_script_prints_json(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            "scripts/check_vendor_runner_template_drift.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["exit_code"] == 0


def test_vendor_runtime_smoke_workflow_fans_out_explicit_probe_profiles() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "vendor-runtime-smoke.yml"
    payload = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    job = payload["jobs"]["vendor-runtime-smoke"]
    assert job["strategy"]["matrix"]["include"] == [
        {"name": "all", "command": "./scripts/ci/vendor_green.sh all", "ci_profile": "all"},
        {"name": "certi-save-restore-probe", "command": "./tools/certi-easy save-restore-probe", "ci_profile": "certi"},
        {"name": "certi-ddm-probe", "command": "./tools/certi-easy ddm-probe", "ci_profile": "certi"},
        {"name": "pitch-save-restore-probe", "command": "./tools/pitch save-restore-probe", "ci_profile": "pitch"},
        {"name": "pitch-ddm-probe", "command": "./tools/pitch ddm-probe", "ci_profile": "pitch"},
        {"name": "pitch-negotiated-probe", "command": "./tools/pitch negotiated-probe", "ci_profile": "pitch"},
    ]
    steps = job["steps"]
    validate_step = next(step for step in steps if step.get("name") == "Validate vendor smoke runtime state")
    assert validate_step["run"] == "python3 scripts/ci/check_vendor_runtime_ci_state.py --profile ${{ matrix.ci_profile }}"
    run_step = next(step for step in steps if step.get("name") == "Run explicit vendor-green smoke tests")
    assert run_step["run"] == "${{ matrix.command }}"
    publish_step = next(step for step in steps if step.get("name") == "Publish vendor smoke runtime-state summary")
    assert publish_step["run"] == "cat analysis/vendor_runtime_ci_state/${{ matrix.ci_profile }}/vendor_runtime_ci_state_report.md >> \"$GITHUB_STEP_SUMMARY\""
    upload_step = next(step for step in steps if step.get("name") == "Upload vendor runtime smoke artifacts")
    assert upload_step["with"]["name"] == "vendor-runtime-smoke-${{ matrix.name }}-artifacts"
    upload_path = upload_step["with"]["path"]
    assert "analysis/vendor_runtime_status/" in upload_path
    assert "analysis/vendor_parity_artifacts/" in upload_path


def test_ci_workflow_has_repeated_probe_stability_job() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "ci.yml"
    payload = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    job = payload["jobs"]["vendor-probe-stability-required"]
    assert job["strategy"]["matrix"]["include"] == [
        {"name": "certi-save-restore-probe", "command": "./tools/certi-easy save-restore-review 5"},
        {"name": "certi-ddm-probe", "command": "./tools/certi-easy ddm-review 5"},
        {"name": "pitch-save-restore-probe", "command": "./tools/pitch save-restore-review 5"},
        {"name": "pitch-ddm-probe", "command": "./tools/pitch ddm-review 5"},
        {"name": "pitch-negotiated-probe", "command": "./tools/pitch negotiated-review 5"},
    ]
    steps = job["steps"]
    run_step = next(step for step in steps if step.get("name") == "Run vendor probe review profile")
    assert run_step["run"] == "${{ matrix.command }}"
    upload_step = next(step for step in steps if step.get("name") == "Upload vendor probe stability artifact")
    assert upload_step["with"]["name"] == "vendor-probe-stability-${{ matrix.name }}"
    upload_path = upload_step["with"]["path"]
    assert "analysis/vendor_probe_stability/" in upload_path
    assert "analysis/vendor_probe_promotion_review/" in upload_path
    assert "analysis/vendor_runtime_status/" in upload_path
