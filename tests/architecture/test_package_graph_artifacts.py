from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "docs" / "package_dependency_tree.md"
ANALYSIS_PATH = ROOT / "analysis" / "package_graph.json"


def test_package_deps_check_passes() -> None:
    result = subprocess.run(
        ["bash", "./tools/package-deps", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "package dependency tree artifacts are current" in result.stdout


def test_package_graph_analysis_matches_yaml_source() -> None:
    payload = json.loads(ANALYSIS_PATH.read_text(encoding="utf-8"))
    assert payload["source"] == "packages/package_graph.yaml"
    assert payload["package_count"] == len(payload["packages"])
    assert "hla2010-fom-minimal-demo" in payload["packages"]
    assert payload["packages"]["hla2010-fom-minimal-demo"]["role"] == "fom-example"


def test_package_dependency_tree_doc_declares_generated_source() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "`packages/package_graph.yaml`" in text
    assert "./tools/package-deps generate" in text
    assert "./tools/package-deps check" in text
