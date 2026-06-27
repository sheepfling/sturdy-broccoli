from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OWN_PATH = ROOT / "requirements" / "2010" / "hla1516_1_own_detailed_reconciliation.csv"


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


def test_ownership_family_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows(OWN_PATH)
    by_feature: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_feature[row["feature"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 11

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert "PRE and EXC companion rows are intentionally narrowed" in row["notes"]

        feature_rows = by_feature[row["feature"]]
        for companion_kind in ("SIG", "MOM", "EFF"):
            assert feature_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert test_ids
        assert all(_node_exists(test_id) for test_id in test_ids)
