from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.typed_json_models import AnalyzeSpecsOutput


ROOT = Path(__file__).resolve().parents[2]


def test_analyze_specs_tool_generates_scaffold_from_repo_ieee_inputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "hla2010_python_v0_3"
    zip_path = tmp_path / "hla2010_python_v0_3.zip"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "analyze_specs.py"),
            "--output-dir",
            str(output_dir),
            "--zip-path",
            str(zip_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    json_start = next(index for index, line in enumerate(lines) if line.startswith("{"))
    payload = AnalyzeSpecsOutput.from_mapping(json.loads("\n".join(lines[json_start:])))
    assert Path(payload.out) == output_dir
    assert Path(payload.zip_path) == zip_path
    assert payload.java_rti_unique is not None and payload.java_rti_unique >= 100
    assert (output_dir / "hla2010" / "raw_api.py").exists()
    assert (output_dir / "hla2010" / "_spec_impl.py").exists()
    assert (output_dir / "hla2010" / "runtime_api.py").exists()
    assert (output_dir / "hla2010" / "spec" / "__init__.py").exists()
    assert zip_path.exists()
