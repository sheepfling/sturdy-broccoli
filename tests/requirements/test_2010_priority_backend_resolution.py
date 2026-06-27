from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements/2010/hla1516_1_priority_backend_resolution.csv"


def test_priority_backend_resolution_ledger_tracks_bounded_mixed_backend_rows() -> None:
    rows = list(csv.DictReader(LEDGER.open(newline="", encoding="utf-8")))
    assert all(None not in row for row in rows)
    by_id = {row["requirement_id"]: row for row in rows}

    assert set(by_id) == {
        "HLA1516.1-FM-4.1.5-001",
        "HLA1516.1-FM-4.1.5-002",
        "HLA1516.1-TM-8.1.2-003",
    }
    assert by_id["HLA1516.1-FM-4.1.5-001"]["canonical_status"] == "pass"
    assert by_id["HLA1516.1-FM-4.1.5-001"]["python_runtime_disposition"] == "verified"
    assert by_id["HLA1516.1-FM-4.1.5-001"]["pitch_runtime_disposition"] == "blocked"
    assert "HLAreportFederateLost" in by_id["HLA1516.1-FM-4.1.5-001"]["boundary_note"]
    assert "CERTI is not yet closed" in by_id["HLA1516.1-FM-4.1.5-001"]["boundary_note"]
    assert by_id["HLA1516.1-FM-4.1.5-002"]["certi_runtime_disposition"] == "not-yet-tested"
    assert "automatic lost-federate resign handling" in by_id["HLA1516.1-FM-4.1.5-002"]["boundary_note"]
    assert by_id["HLA1516.1-TM-8.1.2-003"]["canonical_status"] == "pass"
    assert by_id["HLA1516.1-TM-8.1.2-003"]["certi_runtime_disposition"] == "verified"
    assert by_id["HLA1516.1-TM-8.1.2-003"]["pitch_runtime_disposition"] == "vendor-divergent"
    assert "receive-order override paths remain receive-order on delivery" in by_id["HLA1516.1-TM-8.1.2-003"]["boundary_note"]
