from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONF_LEDGER = ROOT / "requirements/2010/hla1516_1_conf_detailed_reconciliation.csv"
CLOSEOUT_DOC = (
    ROOT / "docs/requirements/ieee-1516-2010/clause13_conformance_closeout.md"
)
FRONT_DOOR_DOC = ROOT / "docs/requirements/ieee-1516-2010/README.md"
SOURCE_README = ROOT / "requirements/2010/README.md"
HIERARCHY_DOC = ROOT / "docs/verification/requirements_hierarchy.md"
REQUIREMENTS_INDEX = ROOT / "requirements/README.md"


def test_clause13_conformance_owner_ledger_is_fully_mapped() -> None:
    rows = list(csv.DictReader(CONF_LEDGER.open(newline="", encoding="utf-8")))

    assert len(rows) == 2
    assert Counter(row["current_status"] for row in rows) == {"mapped": 2}


def test_clause13_conformance_closeout_doc_records_current_shape() -> None:
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for snippet in (
        "2010 Clause 13 Conformance Closeout",
        "`2` packet rows",
        "`2 mapped`",
        "`0 partial`",
        "`HLA1516.1-CONF_FEDERATE-014`",
        "`HLA1516.1-CONF_RTI-015`",
        "`requirements/2010/hla1516_1_conf_detailed_reconciliation.csv`",
        "`docs/verification/clause13_conformance_packet.md`",
        "`docs/verification/clause13_conformance_packet.json`",
        "do not claim external standards certification",
        "do claim that the imported Clause 13 conformance assertions are directly backed",
    ):
        assert snippet in text


def test_clause13_conformance_owner_surface_is_split_from_api_binding_in_front_doors() -> None:
    front_door = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    source_readme = SOURCE_README.read_text(encoding="utf-8")
    hierarchy = HIERARCHY_DOC.read_text(encoding="utf-8")
    requirements_index = REQUIREMENTS_INDEX.read_text(encoding="utf-8")

    assert "Clause 13 conformance closeout reading | `clause13_conformance_closeout.md`" in front_door
    assert "API binding | `hla1516_1_api_detailed_reconciliation.csv`" in source_readme
    assert "Clause 13 conformance | `hla1516_1_conf_detailed_reconciliation.csv`" in source_readme
    assert "| API binding | `requirements/2010/hla1516_1_api_detailed_reconciliation.csv` |" in hierarchy
    assert "| Clause 13 conformance | `requirements/2010/hla1516_1_conf_detailed_reconciliation.csv` |" in hierarchy
    assert "It does not claim external certification." in requirements_index
    assert "directly back the imported federate and RTI conformance-package rows" in requirements_index
