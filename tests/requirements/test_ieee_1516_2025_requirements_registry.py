from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = ROOT / "docs/requirements/ieee-1516-2025"
REGISTRY = REGISTRY_DIR / "requirements.json"


@pytest.mark.requirements("HLA-X-2025-REQ-001", "HLA-X-2025-REQ-002")
def test_ieee_1516_2025_requirements_registry_has_initial_tranche() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    requirements = {row["id"]: row for row in data["requirements"]}

    assert data["extraction_stance"]["classification"]["shall"] == "normative requirement"
    assert len(requirements) == 28
    assert {f"HLA-X-2025-FR-{index:03d}" for index in range(1, 11)} <= set(requirements)
    assert {f"HLA-X-2025-FI-{index:03d}" for index in range(1, 10)} <= set(requirements)
    assert {f"HLA-X-2025-OMT-{index:03d}" for index in range(1, 8)} <= set(requirements)

    assert requirements["HLA-X-2025-REQ-002"]["text_summary"].startswith("Do not label")
    assert "two-federate-core-exchange" in requirements["HLA-X-2025-FR-003"]["tests"]
    assert "full interface service surface accounting" in requirements["HLA-X-2025-FI-002"]["tests"]
    assert "validate_hla_name" in requirements["HLA-X-2025-OMT-001"]["tests"]


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_ieee_1516_2025_requirements_markdown_views_exist() -> None:
    expected = {
        "README.md",
        "framework_rules.md",
        "federate_interface.md",
        "omt.md",
        "traceability_matrix.md",
    }
    assert expected <= {path.name for path in REGISTRY_DIR.iterdir()}
