from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pitch_docker_first_run_doc_keeps_canonical_operator_flow() -> None:
    text = (ROOT / "docs" / "pitch_docker_first_run.md").read_text(encoding="utf-8")

    assert "./tools/bootstrap pitch" in text
    assert "./tools/pitch doctor" in text
    assert "./tools/pitch preflight" in text
    assert "./tools/pitch install" in text
    assert "./tools/pitch start" in text
    assert "./tools/pitch smoke" in text
    assert "./tools/pitch verify" in text
    assert "./tools/pitch smoke-best-effort" in text
    assert "./tools/pitch verify-best-effort" in text
    assert "./tools/test-surface run unit-vendor-onboarding" in text
    assert "third_party/pitch/PITCH-prti1516e-manual" in text
    assert "HLA2010_PITCH_HOME" in text
    assert "docker info" in text
    assert "Docker Desktop is open" in text
    assert "artifacts/preflight_artifacts/pitch-preflight.json" in text
    assert "JPype and Py4J are bridge-debugging routes" in text
    assert "environment: ready" in text
