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
    assert payload["helper_deps"] == ["pytest", "py", "matplotlib", "fonttools", "kiwisolver", "grpcio", "protobuf"]
    assert payload["workspace_packages"] == [
        "packages/hla2010-spec",
        "packages/hla2010-rti-backend-common",
        "packages/hla2010-rti-runtime-common",
        "packages/hla2010-rti-transport-common",
        "packages/hla2010-rti-java-common",
        "packages/hla2010-rti-python",
        "packages/hla2010-rti-certi",
        "packages/hla2010-rti-pitch-common",
        "packages/hla2010-rti-transport-grpc",
        "packages/hla2010-rti-transport-rest",
        "packages/hla2010-verification-harness",
        "packages/hla2010-fom-target-radar",
        "packages/hla2010-fom-minimal-demo",
    ]


def test_bootstrap_python_plan_for_jpype_adds_only_jpype_bridge_packages() -> None:
    payload = _bootstrap_plan(extras="jpype")

    assert payload["profile"] == "jpype"
    assert payload["helper_deps"] == ["pytest", "py", "matplotlib", "fonttools", "kiwisolver", "grpcio", "protobuf", "jpype1"]
    assert "packages/hla2010-rti-java-jpype" in payload["workspace_packages"]
    assert "packages/hla2010-rti-pitch-jpype" in payload["workspace_packages"]
    assert "packages/hla2010-rti-java-py4j" not in payload["workspace_packages"]
    assert "packages/hla2010-rti-pitch-py4j" not in payload["workspace_packages"]
    assert "packages/hla2010-rti-portico" not in payload["workspace_packages"]


def test_bootstrap_python_plan_for_py4j_adds_only_py4j_bridge_packages() -> None:
    payload = _bootstrap_plan(extras="py4j")

    assert payload["profile"] == "py4j"
    assert payload["helper_deps"] == ["pytest", "py", "matplotlib", "fonttools", "kiwisolver", "grpcio", "protobuf", "py4j"]
    assert "packages/hla2010-rti-java-py4j" in payload["workspace_packages"]
    assert "packages/hla2010-rti-pitch-py4j" in payload["workspace_packages"]
    assert "packages/hla2010-rti-java-jpype" not in payload["workspace_packages"]
    assert "packages/hla2010-rti-pitch-jpype" not in payload["workspace_packages"]
    assert "packages/hla2010-rti-portico" not in payload["workspace_packages"]


def test_bootstrap_python_plan_for_java_adds_both_bridge_families_and_portico() -> None:
    payload = _bootstrap_plan(extras="java")

    assert payload["profile"] == "full-java"
    assert payload["helper_deps"] == ["pytest", "py", "matplotlib", "fonttools", "kiwisolver", "grpcio", "protobuf", "jpype1", "py4j"]
    for package in (
        "packages/hla2010-rti-java-jpype",
        "packages/hla2010-rti-pitch-jpype",
        "packages/hla2010-rti-java-py4j",
        "packages/hla2010-rti-pitch-py4j",
        "packages/hla2010-rti-portico",
    ):
        assert package in payload["workspace_packages"]


def test_bootstrap_python_plan_for_qa_matches_repo_green_workspace() -> None:
    payload = _bootstrap_plan(extras="qa")

    assert payload["profile"] == "full-java"
    assert payload["helper_deps"] == ["pytest", "py", "matplotlib", "fonttools", "kiwisolver", "grpcio", "protobuf", "ruff", "pyright", "typing_extensions", "jpype1", "py4j"]
    assert len(payload["workspace_packages"]) == 18
    for package in (
        "packages/hla2010-rti-java-jpype",
        "packages/hla2010-rti-java-py4j",
        "packages/hla2010-rti-pitch-jpype",
        "packages/hla2010-rti-pitch-py4j",
        "packages/hla2010-rti-portico",
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
