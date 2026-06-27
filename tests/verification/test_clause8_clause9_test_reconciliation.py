from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLAUSE8_PATH = ROOT / "requirements" / "2010" / "hla1516_1_clause_8_tm_detailed_reconciliation.csv"
CLAUSE9_PATH = ROOT / "requirements" / "2010" / "hla1516_1_clause_9_ddm_detailed_reconciliation.csv"
TM_PATH = ROOT / "requirements" / "2010" / "hla1516_1_tm_detailed_reconciliation.csv"
DDM_PATH = ROOT / "requirements" / "2010" / "hla1516_1_ddm_detailed_reconciliation.csv"


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _node_exists(node_id: str) -> bool:
    file_part, _, test_name = node_id.partition("::")
    if not file_part or not test_name:
        return False
    path = Path(file_part)
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return f"def {test_name}(" in text


def test_clause8_time_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows(CLAUSE8_PATH)
    by_service: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_service[row["service_name"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 19

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert (
            "broader PRE and EXC envelope rows remain partial" in row["notes"]
            or "PRE and EXC companion rows are mapped only where their notes are intentionally narrowed" in row["notes"]
        )

        service_rows = by_service[row["service_name"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert service_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)


def test_clause9_ddm_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows(CLAUSE9_PATH)
    by_service: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_service[row["service_name"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 14

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert (
            "broader PRE and EXC envelope rows remain partial" in row["notes"]
            or "PRE and EXC companion rows are mapped only where their notes are intentionally narrowed" in row["notes"]
        )

        service_rows = by_service[row["service_name"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert service_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)


def test_tm_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows(TM_PATH)
    by_feature: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_feature[row["feature"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 19

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert (
            "broader PRE and EXC envelope rows remain partial" in row["notes"]
            or "PRE and EXC companion rows are mapped only where their notes are intentionally narrowed" in row["notes"]
        )

        feature_rows = by_feature[row["feature"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert feature_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)


def test_ddm_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows(DDM_PATH)
    by_feature: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_feature[row["feature"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 14

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert (
            "broader PRE and EXC envelope rows remain partial" in row["notes"]
            or "PRE and EXC companion rows are mapped only where their notes are intentionally narrowed" in row["notes"]
        )

        feature_rows = by_feature[row["feature"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert feature_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)


def test_clause9_ddm_subscription_pre_rows_are_synchronized_with_direct_owner_closeout() -> None:
    rows = _load_rows(CLAUSE9_PATH)
    by_requirement = {row["packet_requirement_id"]: row for row in rows}

    expected = {
        "HLA1516.1-DDM-9_2-CREATEREGION-PRE-001": "invalid-dimension or empty-dimension-set",
        "HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-PRE-001": "foreign-region ownership",
        "HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-PRE-001": "publication-state",
        "HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-PRE-001": "object-knownness",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELYWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "invalid-update-rate",
        "HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001": "attribute-definition validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
        "HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001": "interaction-class validation",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-PRE-001": "interaction-class validation",
        "HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001": "publication-state",
        "HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001": "attribute-definition validation",
    }

    for requirement_id, phrase in expected.items():
        row = by_requirement[requirement_id]
        assert row["current_status"] == "mapped"
        assert "applicable precondition surface" in row["notes"]
        assert phrase in row["notes"]


def test_clause9_ddm_subscription_exception_rows_are_synchronized_with_direct_owner_closeout() -> None:
    rows = _load_rows(CLAUSE9_PATH)
    by_requirement = {row["packet_requirement_id"]: row for row in rows}

    expected = {
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-EXC-001": "service-reporting-via-MOM",
        "HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001": "service-reporting-via-MOM",
    }

    for requirement_id, phrase in expected.items():
        row = by_requirement[requirement_id]
        assert row["current_status"] == "mapped"
        assert phrase in row["notes"]
