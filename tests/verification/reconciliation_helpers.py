from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rows_by_id(rows: list[dict[str, str]], key: str = "packet_requirement_id") -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def status_counts(rows: list[dict[str, str]]) -> Counter[str]:
    return Counter(row["current_status"] for row in rows)


def kind_status_counts(rows: list[dict[str, str]]) -> Counter[tuple[str, str]]:
    return Counter((row["reconciliation_kind"], row["current_status"]) for row in rows)


def grouped_rows(
    rows: list[dict[str, str]],
    *,
    group_key: str,
) -> dict[str, dict[str, dict[str, str]]]:
    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[row[group_key]][row["reconciliation_kind"]] = row
    return grouped


def split_test_ids(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def node_exists(node_id: str) -> bool:
    file_part, _, test_name = node_id.partition("::")
    if not file_part or not test_name:
        return False
    path = Path(file_part)
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return f"def {test_name}(" in text


def assert_mapped_test_rows_with_companions(
    rows: list[dict[str, str]],
    *,
    group_key: str,
    expected_count: int,
    note_fragment: str,
    companion_kinds: tuple[str, ...] = ("SIG", "MOM", "ARG", "EFF"),
    min_test_ids: int = 2,
) -> None:
    grouped = grouped_rows(rows, group_key=group_key)
    test_rows = [row for row in rows if row["reconciliation_kind"] == "TEST"]
    assert len(test_rows) == expected_count

    for row in test_rows:
        assert row["current_status"] == "mapped"
        assert note_fragment in row["notes"]

        companion_rows = grouped[row[group_key]]
        for companion_kind in companion_kinds:
            assert companion_rows[companion_kind]["current_status"] == "mapped"

        test_ids = split_test_ids(row["current_test_id"])
        assert len(test_ids) >= min_test_ids
        assert all(node_exists(test_id) for test_id in test_ids)
