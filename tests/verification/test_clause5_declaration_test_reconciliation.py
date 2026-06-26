from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DM_PATH = ROOT / "requirements" / "2010" / "hla1516_1_dm_detailed_reconciliation.csv"
CLAUSE_5_PATH = ROOT / "requirements" / "2010" / "hla1516_1_clause_5_dm_detailed_reconciliation.csv"


def _load_rows() -> list[dict[str, str]]:
    with DM_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_clause5_rows() -> list[dict[str, str]]:
    with CLAUSE_5_PATH.open(newline="", encoding="utf-8") as handle:
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


def test_declaration_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows()
    by_feature: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_feature[row["feature"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 12

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert "broader PRE and EXC envelope rows remain partial" in row["notes"]

        feature_rows = by_feature[row["feature"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert feature_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)


def test_clause5_declaration_test_rows_match_family_level_direct_evidence():
    rows = _load_clause5_rows()
    by_feature: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_feature[row["feature"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 12
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"mapped": 92, "partial": 24}
    )

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert "broader PRE and EXC envelope rows remain partial" in row["notes"]

        feature_rows = by_feature[row["feature"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert feature_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)
