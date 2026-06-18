from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIFFERENTIAL_SET = ROOT / "requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv"
REUSE_DISPOSITION = ROOT / "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv"
STRICT_DOC_INVENTORY = ROOT / "requirements/2025/STRICT_DOC_INVENTORY.json"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


@pytest.mark.requirements("HLA2025-BLG-001", "HLA2025-REQ-001")
def test_2025_renumbered_service_utilization_rows_preserve_behavior_and_update_references() -> None:
    rows = _csv_rows(DIFFERENTIAL_SET)
    renumbered = [
        row
        for row in rows
        if row["reuse_action"] == "Carry forward with reference update"
        and row["surface_type"] == "OMT serviceUtilization"
    ]

    assert len(renumbered) >= 90
    assert all(row["2010_section_or_location"] for row in renumbered)
    assert all(row["2025_section_or_location"] for row in renumbered)
    assert all(row["2010_section_or_location"] != row["2025_section_or_location"] for row in renumbered)
    assert all(row["2010_detail"] == row["2025_detail"] for row in renumbered)
    assert all("update clause number" in row["requirement_action"] for row in renumbered)

    sample = {row["item"]: row for row in renumbered}
    assert sample["announceSynchronizationPoint"]["2010_detail"] == "isCallback=true"
    assert sample["announceSynchronizationPoint"]["2025_detail"] == "isCallback=true"
    assert sample["abortFederationRestore"]["2010_detail"] == "isCallback=false"
    assert sample["abortFederationRestore"]["2025_detail"] == "isCallback=false"


@pytest.mark.requirements("HLA2025-BLG-002", "HLA2025-NEW-006", "HLA2025-REQ-001")
def test_2025_common_object_model_reuse_keeps_shared_model_and_adds_nullable_2025_metadata() -> None:
    rows = _csv_rows(REUSE_DISPOSITION)
    by_area = {row["Code area"]: row for row in rows}
    common_model = by_area["Common FOM/SOM object-model representation"]

    assert common_model["Disposition"] == "Reuse directly in common core"
    assert "Object class" in common_model["2010 code candidate"]
    assert "valueRequired" in common_model["2025 impact"]
    assert "nullable/optional fields" in common_model["Implementation recommendation"]
    assert "2025-only metadata" in common_model["Requirement/test action"]


@pytest.mark.requirements("HLA2025-MOD-009", "HLA2025-MOD-001", "HLA2025-MOD-002")
def test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms() -> None:
    inventory = json.loads(STRICT_DOC_INVENTORY.read_text(encoding="utf-8"))
    rti_groups = inventory["rti_overload_groups"]

    connect = " ".join(rti_groups["connect"])
    create = " ".join(rti_groups["createFederationExecution"])
    create_with_mim = " ".join(rti_groups["createFederationExecutionWithMIM"])
    joined = " ".join(rti_groups["joinFederationExecution"])
    native_surface = "\n".join(connect for overloads in rti_groups.values() for connect in overloads)

    assert "Unauthorized" in connect
    assert "InvalidCredentials" in connect
    assert "RtiConfiguration" in connect
    assert "Credentials" in connect
    assert "InvalidLocalSettingsDesignator" not in connect

    assert {"InvalidFOM", "InconsistentFOM", "ErrorReadingFOM", "CouldNotOpenFOM"} <= set(create.replace(",", " ").split())
    assert {"InvalidMIM", "ErrorReadingMIM", "CouldNotOpenMIM", "DesignatorIsHLAstandardMIM"} <= set(
        create_with_mim.replace(",", " ").split()
    )
    assert "CouldNotCreateLogicalTimeFactory" in joined
    assert "InconsistentFDD" not in native_surface
    assert "ErrorReadingFDD" not in native_surface
    assert "CouldNotOpenFDD" not in native_surface
