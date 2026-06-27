from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_test_focus_help_describes_inventory_run_and_resume() -> None:
    result = subprocess.run(
        ["bash", "tools/test-focus", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/test-focus inventory" in result.stdout
    assert "./tools/test-focus run foundation" in result.stdout
    assert "./tools/test-focus run python-examples" in result.stdout
    assert "./tools/test-focus run jpype" in result.stdout
    assert "./tools/test-focus run target-radar" in result.stdout
    assert "./tools/test-focus run fom-target-radar" in result.stdout
    assert "./tools/test-focus run rti-factory" in result.stdout
    assert "./tools/test-focus run execution-membership" in result.stdout
    assert "./tools/test-focus run python-2025-time" in result.stdout
    assert "./tools/test-focus run python-2025-ddm" in result.stdout
    assert "./tools/test-focus run save-restore-2025" in result.stdout
    assert "./tools/test-focus run routes-2025" in result.stdout
    assert "./tools/test-focus resume python-2025-runtime" in result.stdout


def test_tools_test_focus_inventory_json_lists_expected_targets() -> None:
    result = subprocess.run(
        ["bash", "tools/test-focus", "inventory", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    target_ids = [row["id"] for row in payload["targets"]]
    assert target_ids == [
        "foundation",
        "python-examples",
        "java-bridges",
        "jpype",
        "py4j",
        "fom",
        "target-radar",
        "siso-surfaces",
        "python-2025-runtime",
        "execution-membership",
        "python-2025-time",
        "python-2025-save-restore",
        "python-2025-ownership",
        "python-2025-ddm",
        "python-2025-mom-callbacks",
        "transport",
        "routes-2025",
        "backends",
        "rti-core",
        "requirements-2025",
        "verification",
        "time",
        "vendors",
    ]
    targets = {row["id"]: row for row in payload["targets"]}
    assert "fom-target-radar" in targets["target-radar"]["aliases"]
    assert "rti-factory" in targets["rti-core"]["aliases"]
    assert "bridge-jpype" in targets["jpype"]["aliases"]
    assert "save-restore-2025" in targets["python-2025-save-restore"]["aliases"]
    assert "membership-guards" in targets["execution-membership"]["aliases"]
    assert "ddm-2025" in targets["python-2025-ddm"]["aliases"]
    assert "gRPC/FedPro lane and the REST-hosted Python route" in targets["execution-membership"]["description"]
    assert "hosted gRPC/FedPro save/restore" in targets["python-2025-save-restore"]["description"]
    assert "hosted gRPC/FedPro route" in targets["python-2025-ownership"]["description"]
    assert "hosted gRPC/FedPro route" in targets["python-2025-ddm"]["description"]
    assert "hosted gRPC/FedPro route" in targets["python-2025-mom-callbacks"]["description"]


def test_tools_test_focus_run_accepts_alias_target_name() -> None:
    result = subprocess.run(
        ["bash", "tools/test-focus", "run", "fom-target-radar", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"] == "target-radar"


def test_tools_test_focus_run_dry_run_writes_summary_artifacts() -> None:
    result = subprocess.run(
        ["bash", "tools/test-focus", "run", "python-examples", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"] == "python-examples"
    assert payload["status"] == "passed"
    assert payload["dry_run"] is True
    assert payload["steps"][0]["argv"] == [
        "./tools/test",
        "tests/test_python_route_examples.py",
        "tests/test_tools_python_wrapper.py",
    ]
    assert (ROOT / payload["artifacts"]["json"]).is_file()
    assert (ROOT / payload["artifacts"]["markdown"]).is_file()


def test_tools_test_focus_resume_uses_last_failed_mode() -> None:
    result = subprocess.run(
        ["bash", "tools/test-focus", "resume", "foundation", "--dry-run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"] == "foundation"
    assert payload["last_failed"] is True
    assert "--lf" in payload["steps"][0]["argv"]


def test_tools_test_focus_run_accepts_extra_pytest_args_after_separator() -> None:
    result = subprocess.run(
        ["bash", "tools/test-focus", "run", "java-bridges", "--dry-run", "--json", "--", "--maxfail=1"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"] == "java-bridges"
    assert payload["steps"][0]["argv"][-1] == "--maxfail=1"
