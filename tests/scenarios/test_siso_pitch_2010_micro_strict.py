from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

import pytest

from hla.verification.repo_internal.verification import siso_pitch_micro_parity as micro_parity
from hla.verification.repo_internal.verification.siso_pitch_micro_parity import run_siso_pitch_micro_parity
from hla.verification.repo_internal.verification.siso_pitch_2010_micro_strict import (
    write_siso_pitch_2010_micro_strict_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


def test_siso_pitch_micro_parity_strict_real_vendor_lane_requires_preflight(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HLA2010_PITCH_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(ROOT / ".missing-preflight-dir"))

    with pytest.raises(RuntimeError, match="Pitch preflight not confirmed"):
        run_siso_pitch_micro_parity(require_real_vendor_preflight=True, real_vendor_only=True)


def test_siso_pitch_2010_micro_strict_artifacts_are_generated_with_confirmed_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HLA2010_PITCH_PREFLIGHT_OK", "1")
    monkeypatch.setattr(micro_parity, "build_two_federate_runtime_launchers", lambda: {})
    monkeypatch.setattr(
        micro_parity,
        "run_siso_runtime_showcase_scenario",
        lambda scenario, backend=None: {
            "scenario": scenario,
            "family": "stub",
            "runtime_edition": "2010",
            "topology": "micro-2",
            "status": "lifecycle-green",
            "execution_complete": True,
            "discoveries": 1,
            "reflections": 1,
            "interactions": 1,
            "lifecycle": ["stubbed"],
        },
    )
    paths = write_siso_pitch_2010_micro_strict_artifacts(tmp_path)

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] == 6
    assert summary["real_vendor_only"] is True
    assert summary["strict_real_vendor_preflight"] is True

    with paths.results_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert all(row["backend"] in {"pitch-jpype", "pitch-py4j"} for row in rows)


def test_siso_pitch_2010_micro_strict_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "HLA2010_PITCH_PREFLIGHT_OK": "1",
        "HLA2010_PITCH_HOME": str(tmp_path / "missing-pitch-home"),
    }
    output_dir = tmp_path / "strict"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-siso-pitch-2010-micro-strict"),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads((output_dir / "siso_pitch_micro_parity_summary.json").read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] == 6
