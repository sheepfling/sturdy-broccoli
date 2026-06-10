from __future__ import annotations

import json
import subprocess
from pathlib import Path

from hla2010_repo_internal.verification.vendor_runtime_status import build_vendor_runtime_status, write_vendor_runtime_status


ROOT = Path(__file__).resolve().parents[2]


def _write_payload(path: Path, *, tool: str, environment: str, result: str, exit_code: int) -> None:
    payload = {
        "tool": tool,
        "environment": environment,
        "result": result,
        "exit_code": exit_code,
        "next_step": "./tools/certi-easy preflight" if tool == "certi-preflight" else "./tools/pitch preflight",
        "checks": [
            {
                "name": "docker" if tool == "pitch-preflight" else "loopback_bind",
                "ok": exit_code == 0,
                "status": "ok" if exit_code == 0 else "blocked",
                "detail": result,
            }
        ],
    }
    if tool == "certi-preflight":
        payload["required_markers"] = {
            "active_prefix": "/tmp/certi/bin/rtig",
            "active_build_root": "/tmp/certi-build/libRTI/ieee1516-2010",
        }
    else:
        payload["required_markers"] = {
            "runtime_home": "/tmp/pitch/lib/prtifull.jar",
        }
        payload["ports"] = {
            "crc": {
                "host": "127.0.0.1",
                "port": 8989,
                "status": "ok" if exit_code == 0 else "blocked",
                "detail": "port available" if exit_code == 0 else result,
            },
            "fedpro": {
                "host": "127.0.0.1",
                "port": 15164,
                "status": "ok" if exit_code == 0 else "blocked",
                "detail": "port available" if exit_code == 0 else result,
            },
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def test_repo_green_treats_blocked_environment_as_nonfatal(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "preflight"
    _write_payload(
        artifact_dir / "certi-preflight.json",
        tool="certi-preflight",
        environment="loopback-blocked",
        result="real CERTI will skip",
        exit_code=1,
    )
    _write_payload(
        artifact_dir / "pitch-preflight.json",
        tool="pitch-preflight",
        environment="docker-blocked",
        result="Pitch runtime is not ready",
        exit_code=1,
    )

    summary = build_vendor_runtime_status(artifact_dir=artifact_dir, lane="repo-green")

    assert summary["overall_classification"] == "repo-green"
    assert summary["exit_code"] == 0
    assert sorted(summary["blocked_vendors"]) == ["certi", "pitch"]
    assert summary["recommended_next_steps"]["certi"] == ["./tools/certi-easy preflight"]
    assert summary["recommended_next_steps"]["pitch"] == ["./tools/pitch preflight"]


def test_vendor_green_fails_when_environment_is_blocked(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "preflight"
    _write_payload(
        artifact_dir / "certi-preflight.json",
        tool="certi-preflight",
        environment="loopback-ok",
        result="real CERTI runnable",
        exit_code=0,
    )
    _write_payload(
        artifact_dir / "pitch-preflight.json",
        tool="pitch-preflight",
        environment="docker-blocked",
        result="Pitch runtime is not ready",
        exit_code=1,
    )

    summary = build_vendor_runtime_status(artifact_dir=artifact_dir, lane="vendor-green")

    assert summary["overall_classification"] == "environment-blocked"
    assert summary["exit_code"] == 1
    assert summary["ready_vendors"] == ["certi"]
    assert summary["blocked_vendors"] == ["pitch"]
    pitch_row = summary["vendors"][1]
    assert pitch_row["blocked_reason"] == "docker"
    assert pitch_row["blocked_checks"][0]["name"] == "docker"
    assert pitch_row["required_markers"]["runtime_home"].endswith("/lib/prtifull.jar")
    assert pitch_row["required_ports"]["crc"]["port"] == 8989
    assert pitch_row["next_steps"] == ["./tools/pitch preflight"]


def test_write_vendor_runtime_status_emits_summary_and_report(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "preflight"
    _write_payload(
        artifact_dir / "certi-preflight.json",
        tool="certi-preflight",
        environment="loopback-ok",
        result="real CERTI runnable",
        exit_code=0,
    )

    paths = write_vendor_runtime_status(
        tmp_path / "status",
        artifact_dir=artifact_dir,
        lane="vendor-green",
        vendors=("certi",),
    )

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["overall_classification"] == "vendor-green"
    assert summary["ready_vendors"] == ["certi"]
    report_text = paths.report_markdown.read_text(encoding="utf-8")
    assert "Vendor Runtime Status" in report_text
    assert "vendor-green" in report_text
    assert "certi" in report_text
    assert "Blocked Reason" in report_text
    assert "Required markers for `certi`" in report_text


def test_script_returns_nonzero_for_vendor_green_blocked_environment(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "preflight"
    _write_payload(
        artifact_dir / "pitch-preflight.json",
        tool="pitch-preflight",
        environment="docker-blocked",
        result="Pitch runtime is not ready",
        exit_code=1,
    )

    result = subprocess.run(
        [
            "python3",
            "scripts/classify_vendor_runtime.py",
            "--artifact-dir",
            str(artifact_dir),
            "--output-dir",
            str(tmp_path / "status"),
            "--lane",
            "vendor-green",
            "--vendor",
            "pitch",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["overall_classification"] == "environment-blocked"
    assert payload["blocked_vendors"] == ["pitch"]


def test_unexpected_preflight_failure_is_reported_with_blocked_check_details(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "preflight"
    _write_payload(
        artifact_dir / "certi-preflight.json",
        tool="certi-preflight",
        environment="partial",
        result="real CERTI will skip",
        exit_code=1,
    )
    payload = json.loads((artifact_dir / "certi-preflight.json").read_text(encoding="utf-8"))
    payload["checks"] = [
        {
            "name": "active_prefix",
            "ok": False,
            "message": "active_prefix: blocked: active CERTI install prefix missing",
        }
    ]
    payload["next_steps"] = ["./tools/certi-easy install", "./tools/certi-easy preflight"]
    (artifact_dir / "certi-preflight.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = build_vendor_runtime_status(artifact_dir=artifact_dir, lane="vendor-green", vendors=("certi",))

    assert summary["overall_classification"] == "unexpected-preflight-failure"
    assert summary["unexpected_failure_vendors"] == ["certi"]
    vendor = summary["vendors"][0]
    assert vendor["blocked_reason"] == "active_prefix"
    assert vendor["blocked_checks"][0]["message"] == "active_prefix: blocked: active CERTI install prefix missing"
    assert vendor["required_markers"]["active_build_root"].endswith("/libRTI/ieee1516-2010")
    assert vendor["next_steps"] == ["./tools/certi-easy install", "./tools/certi-easy preflight"]
