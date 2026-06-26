from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
    / "hla1516_1_clause_10_sup_detailed_reconciliation.csv"
)


def _load_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
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


def test_clause10_support_test_rows_have_direct_evidence_and_mapped_companion_slices():
    rows = _load_rows()
    by_service: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_service[row["service_name"]][row["reconciliation_kind"]] = row

    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == 43

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert "transport-mediated delivery is not applicable" in row["notes"]

        service_rows = by_service[row["service_name"]]
        for companion_kind in ("SIG", "MOM", "ARG", "EFF"):
            assert service_rows[companion_kind]["current_status"] == "mapped"

        test_ids = [item.strip() for item in row["current_test_id"].split(";") if item.strip()]
        assert len(test_ids) >= 2
        assert all(_node_exists(test_id) for test_id in test_ids)
