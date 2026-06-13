from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIRST_RUN_DOC = ROOT / "docs" / "first_run.md"
EXPECTED_OUTPUT = ROOT / "docs" / "examples" / "target_radar_python_expected_output.txt"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_first_run_doc_uses_canonical_bootstrap_path() -> None:
    text = _read(FIRST_RUN_DOC)
    assert "./tools/bootstrap doctor" in text
    assert "./tools/bootstrap python" in text
    assert "source .venv/bin/activate" in text
    assert "./tools/rti-factories show in-memory --probe" in text
    assert "./tools/examples backend-recording" in text
    assert "./tools/examples target-radar --backend in-memory --steps 5" in text
    assert "python -m pip install --no-build-isolation" not in text
    assert "do not use `pip install -e .`" in text
    assert "manual `pip install -e ...` recovery commands" in text
    assert "workspace_imports: ok" in text


def test_first_run_doc_references_expected_output_artifact() -> None:
    text = _read(FIRST_RUN_DOC)
    assert "examples/target_radar_python_expected_output.txt" in text
    expected = _read(EXPECTED_OUTPUT)
    assert expected.startswith("backend=python/in-memory,python/in-memory")
    assert "tracks=5" in expected
    assert "TRK-005" in expected


def test_first_run_commands_exist() -> None:
    expected_paths = (
        ROOT / "tools" / "bootstrap",
        ROOT / "tools" / "examples",
        ROOT / "tools" / "rti-factories",
        ROOT / "examples" / "backend_recording.py",
        ROOT / "examples" / "rti_factory_selection.py",
        ROOT / "examples" / "target_radar_simulation.py",
        EXPECTED_OUTPUT,
    )
    for path in expected_paths:
        assert path.exists(), path.relative_to(ROOT)


def test_bootstrap_plan_includes_required_split_packages() -> None:
    result = subprocess.run(
        ["./tools/bootstrap", "python", "plan"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "packages/hla2010-spec" in result.stdout
    assert "packages/hla2010-rti-backend-common" in result.stdout
    assert "packages/hla2010-rti-python" in result.stdout
    assert "packages/hla2010-verification-harness" in result.stdout
    assert "packages/hla2010-fom-target-radar" in result.stdout


def test_first_run_examples_import_after_bootstrap() -> None:
    subprocess.run(
        ["bash", "./tools/bootstrap", "python"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    result = subprocess.run(
        [
            str(ROOT / ".venv" / "bin" / "python"),
            "-c",
            (
                "import hla2010;"
                "import hla2010.spec;"
                "import hla2010_rti_backend_common;"
                "import hla2010_rti_python;"
                "import hla2010_fom_target_radar"
            ),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_expected_output_shape_matches_live_example() -> None:
    python_bin = ROOT / ".venv" / "bin" / "python"
    if not python_bin.exists():
        raise AssertionError(".venv/bin/python is missing; run ./tools/bootstrap python")
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
