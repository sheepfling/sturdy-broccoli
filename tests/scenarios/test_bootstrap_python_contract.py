from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _bootstrap_plan(*, extras: str) -> dict[str, object]:
    env = os.environ.copy()
    env["HLA2010_BOOTSTRAP_EXTRAS"] = extras
    result = subprocess.run(
        ["bash", "./scripts/bootstrap_python.sh", "plan-json"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout or result.stderr
    return json.loads(result.stdout)


def test_bootstrap_python_help_mentions_planning_modes() -> None:
    result = subprocess.run(
        ["bash", "./scripts/bootstrap_python.sh", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./scripts/bootstrap_python.sh plan" in result.stdout
    assert "./scripts/bootstrap_python.sh plan-json" in result.stdout


def test_bootstrap_python_plan_for_test_is_lean_core_workspace() -> None:
    payload = _bootstrap_plan(extras="test")

    assert payload["extras"] == "test"
    assert payload["profile"] == "core"
    assert payload["helper_deps"] == ["pytest"]
    assert payload["workspace_packages"] == [
        "packages/hla-rti1516e",
        "packages/hla-backend-common",
        "packages/hla-rti-core",
        "packages/hla-transport-common",
        "packages/hla-bridge-java-common",
        "packages/hla-backend-inmemory",
        "packages/hla-backend-certi",
        "packages/hla-vendor-pitch",
        "packages/hla-transport-grpc",
        "packages/hla-transport-rest",
        "packages/hla-verification",
        "packages/hla-fom-target-radar",
    ]


def test_bootstrap_python_plan_for_jpype_adds_only_jpype_bridge_packages() -> None:
    payload = _bootstrap_plan(extras="jpype")

    assert payload["profile"] == "jpype"
    assert payload["helper_deps"] == ["pytest", "jpype1"]
    assert "packages/hla-bridge-java-jpype" in payload["workspace_packages"]
    assert "packages/hla-vendor-pitch-jpype" in payload["workspace_packages"]
    assert "packages/hla-bridge-java-py4j" not in payload["workspace_packages"]
    assert "packages/hla-vendor-pitch-py4j" not in payload["workspace_packages"]
    assert "packages/hla-vendor-portico" not in payload["workspace_packages"]


def test_bootstrap_python_plan_for_py4j_adds_only_py4j_bridge_packages() -> None:
    payload = _bootstrap_plan(extras="py4j")

    assert payload["profile"] == "py4j"
    assert payload["helper_deps"] == ["pytest", "py4j"]
    assert "packages/hla-bridge-java-py4j" in payload["workspace_packages"]
    assert "packages/hla-vendor-pitch-py4j" in payload["workspace_packages"]
    assert "packages/hla-bridge-java-jpype" not in payload["workspace_packages"]
    assert "packages/hla-vendor-pitch-jpype" not in payload["workspace_packages"]
    assert "packages/hla-vendor-portico" not in payload["workspace_packages"]


def test_bootstrap_python_plan_for_java_adds_both_bridge_families_and_portico() -> None:
    payload = _bootstrap_plan(extras="java")

    assert payload["profile"] == "full-java"
    assert payload["helper_deps"] == ["pytest", "jpype1", "py4j"]
    for package in (
        "packages/hla-bridge-java-jpype",
        "packages/hla-vendor-pitch-jpype",
        "packages/hla-bridge-java-py4j",
        "packages/hla-vendor-pitch-py4j",
        "packages/hla-vendor-portico",
    ):
        assert package in payload["workspace_packages"]


def test_bootstrap_python_plan_for_qa_matches_repo_green_workspace() -> None:
    payload = _bootstrap_plan(extras="qa")

    assert payload["profile"] == "full-java"
    assert payload["helper_deps"] == ["pytest", "ruff", "pyright", "jpype1", "py4j"]
    assert len(payload["workspace_packages"]) == 17
    for package in (
        "packages/hla-bridge-java-jpype",
        "packages/hla-bridge-java-py4j",
        "packages/hla-vendor-pitch-jpype",
        "packages/hla-vendor-pitch-py4j",
        "packages/hla-vendor-portico",
    ):
        assert package in payload["workspace_packages"]


def test_bootstrap_python_plan_rejects_unknown_extra_token() -> None:
    env = os.environ.copy()
    env["HLA2010_BOOTSTRAP_EXTRAS"] = "bogus"
    result = subprocess.run(
        ["bash", "./scripts/bootstrap_python.sh", "plan-json"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "unsupported HLA2010_BOOTSTRAP_EXTRAS token: bogus" in result.stderr
