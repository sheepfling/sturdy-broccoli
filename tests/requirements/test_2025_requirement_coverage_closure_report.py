from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_disposition_ledger.csv"
REPORT = ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_coverage_closure_report.md"


def _rows() -> list[dict[str, str]]:
    with LEDGER.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_2025_requirement_coverage_closure_report_matches_current_disposition_ledger() -> None:
    rows = _rows()
    counts = Counter(row["harmonization_disposition"] for row in rows)
    priorities = Counter(row["priority"] for row in rows)
    covered_with_evidence = sum(
        1
        for row in rows
        if row["harmonization_disposition"] == "covered" and row.get("suggested_repo_evidence_path", "").strip()
    )

    text = REPORT.read_text(encoding="utf-8")

    assert len(rows) == 691
    assert counts == {
        "covered": 645,
        "duplicate/umbrella": 22,
        "retired/legacy-only": 24,
    }
    assert priorities == {"P0": 89, "P1": 430, "P2": 172}
    assert covered_with_evidence == 645

    assert "- Total rows dispositioned: 691" in text
    assert "- Disposition counts: covered=645, duplicate/umbrella=22, partial=0, planned=0, retired/legacy-only=24, unsupported-boundary=0" in text
    assert "- Priority counts: P0=89, P1=430, P2=172" in text
    assert "- Covered rows with evidence paths: 645" in text
    assert "- Rows remaining as explicit unsupported-boundary dispositions: 0" in text
    assert "historical intermediate evidence rather than the current closeout state" in text
    assert "docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md" in text
    assert "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md" in text
    assert "the direct `python1516_2025` lane is the primary runtime owner behind the" in text
    assert "Java/C++ standard-shim surfaces remain wrapper or capability layers over" in text
    assert "hosted FedPro evidence remains a bounded hosted-route surface over" in text
    assert "Pitch proto HLA 4 / `202X` overlap remains explicit vendor-resolution" in text
    assert "Delta hints are not standalone proof" in text
    assert "tied to concrete child FI/binding evidence and its canonical owner doc" in text
    assert "Framework rules are not standalone proof" in text
    assert "tied to concrete child FI/OMT/runtime evidence and its canonical owner doc" in text
