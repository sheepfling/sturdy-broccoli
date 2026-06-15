from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from conftest import (
    REPO_ROOT,
    bootstrap_test_env,
    load_json_fixture,
    materialize_fresh_checkout,
    read_repo_text,
    workspace_python_bin,
    workspace_python_env,
)


ROOT = REPO_ROOT
FIRST_RUN_DOC = ROOT / "docs" / "first_run.md"
EXPECTED_OUTPUT = ROOT / "docs" / "examples" / "target_radar_python_expected_output.txt"


@dataclass(frozen=True)
class FirstRunPolicy:
    doc_contains: tuple[str, ...]
    doc_absent: tuple[str, ...]
    existing_paths: tuple[str, ...]
    bootstrap_plan_contains: tuple[str, ...]
    expected_output_contains: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> FirstRunPolicy:
        return cls(
            doc_contains=tuple(str(item) for item in payload["doc_contains"]),
            doc_absent=tuple(str(item) for item in payload["doc_absent"]),
            existing_paths=tuple(str(item) for item in payload["existing_paths"]),
            bootstrap_plan_contains=tuple(str(item) for item in payload["bootstrap_plan_contains"]),
            expected_output_contains=tuple(str(item) for item in payload["expected_output_contains"]),
        )


POLICY = FirstRunPolicy.from_mapping(load_json_fixture("first_run_policy.json"))


def _read(path: Path) -> str:
    return read_repo_text(path)


def test_first_run_doc_uses_canonical_bootstrap_path() -> None:
    text = _read(FIRST_RUN_DOC)
    for snippet in POLICY.doc_contains:
        assert snippet in text
    for snippet in POLICY.doc_absent:
        assert snippet not in text


def test_first_run_doc_references_expected_output_artifact() -> None:
    text = _read(FIRST_RUN_DOC)
    assert "examples/target_radar_python_expected_output.txt" in text
    expected = _read(EXPECTED_OUTPUT)
    for snippet in POLICY.expected_output_contains:
        assert snippet in expected


def test_first_run_commands_exist() -> None:
    for rel_path in POLICY.existing_paths:
        path = ROOT / rel_path
        assert path.exists(), path.relative_to(ROOT)


def test_bootstrap_plan_includes_required_split_packages() -> None:
    result = subprocess.run(
        ["./tools/bootstrap", "python", "plan"],
        cwd=ROOT,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    for snippet in POLICY.bootstrap_plan_contains:
        assert snippet in result.stdout


def test_first_run_examples_import_after_bootstrap(tmp_path: Path) -> None:
    fresh_root = materialize_fresh_checkout(tmp_path / "fresh-checkout")
    subprocess.run(
        ["bash", "./tools/bootstrap", "python"],
        cwd=fresh_root,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    result = subprocess.run(
        [
            str(fresh_root / ".venv" / "bin" / "python"),
            "-c",
            (
                "import hla2010;"
                "import hla2010.spec;"
                "import hla2010_rti_backend_common;"
                "import hla2010_rti_python;"
                "import hla2010_fom_target_radar"
            ),
        ],
        cwd=fresh_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_expected_output_shape_matches_live_example() -> None:
    python_bin = workspace_python_bin()
    result = subprocess.run(
        [
            str(python_bin),
            "examples/target_radar_simulation.py",
            "--backend",
            "python",
            "--steps",
            "5",
        ],
        cwd=ROOT,
        env=workspace_python_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines
    assert lines[0].startswith("backend=python/in-memory,python/in-memory")
    assert "tracks=5" in lines[0]
    track_lines = [line for line in lines[1:] if line.lstrip().startswith("TRK-")]
    assert len(track_lines) == 5

    expected_lines = [line for line in _read(EXPECTED_OUTPUT).splitlines() if line.strip()]
    assert expected_lines[0].startswith("backend=python/in-memory,python/in-memory")
    assert len([line for line in expected_lines[1:] if line.lstrip().startswith("TRK-")]) == 5
