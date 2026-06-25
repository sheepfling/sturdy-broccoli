from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.siso_runtime_showcase import (
    build_siso_runtime_showcase_manifest,
)
from hla.verification.repo_internal.verification.siso_runtime_showcase_launcher import (
    run_siso_runtime_showcase_launcher,
    write_siso_runtime_showcase_launcher_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


def test_siso_runtime_showcase_launcher_reads_manifest_and_filters_rows(tmp_path: Path) -> None:
    manifest_path = tmp_path / "showcase_manifest.json"
    manifest_path.write_text(json.dumps(build_siso_runtime_showcase_manifest(), indent=2), encoding="utf-8")
    summary = run_siso_runtime_showcase_launcher(
        manifest_path=manifest_path,
        families=["space"],
        editions=["2025"],
        topologies=["constellation-10"],
    )

    assert summary["suite_name"] == "siso-runtime-showcase-launcher"
    assert summary["selected_scenario_count"] == 1
    assert summary["status"] == "lifecycle-green"
    assert summary["results"][0]["scenario"] == "space-fom-core-2025-constellation-10"


def test_siso_runtime_showcase_launcher_artifacts_are_generated(tmp_path: Path) -> None:
    manifest_path = tmp_path / "showcase_manifest.json"
    manifest_path.write_text(json.dumps(build_siso_runtime_showcase_manifest(), indent=2), encoding="utf-8")
    paths = write_siso_runtime_showcase_launcher_artifacts(
        tmp_path / "launcher",
        manifest_path=manifest_path,
        families=["rpr"],
        topologies=["squad-5"],
    )

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] == 2
    assert summary["status"] == "lifecycle-green"

    with paths.results_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert {row["scenario"] for row in rows} == {
        "rpr-runtime-2010-squad-5",
        "rpr-runtime-2025-squad-5",
    }

    manifest = json.loads(paths.selected_manifest_json.read_text(encoding="utf-8"))
    assert manifest["scenario_count"] == 2


def test_siso_runtime_showcase_launcher_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    showcase_manifest = tmp_path / "siso_runtime_showcase_manifest.json"
    showcase_manifest.write_text(json.dumps(build_siso_runtime_showcase_manifest(), indent=2), encoding="utf-8")
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "launcher"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-siso-runtime-launcher"),
            "--manifest",
            str(showcase_manifest),
            "--family",
            "link16",
            "--topology",
            "micro-2",
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
    summary = json.loads((output_dir / "siso_runtime_showcase_launcher_summary.json").read_text(encoding="utf-8"))
    assert summary["selected_scenario_count"] == 2
