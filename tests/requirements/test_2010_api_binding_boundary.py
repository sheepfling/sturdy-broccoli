from __future__ import annotations

from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements import load_2010_reconciliation_rows, survey_requirement_artifacts


ROOT = Path(__file__).resolve().parents[2]
API_LEDGER_REL = "requirements/2010/hla1516_1_api_detailed_reconciliation.csv"
BOUNDARY_DOC = (
    ROOT / "docs/requirements/ieee-1516-2010/api_binding_bounded_family.md"
)
FRONT_DOOR_DOC = ROOT / "docs/requirements/ieee-1516-2010/README.md"
SOURCE_README = ROOT / "requirements/2010/README.md"


def _typed_rows() -> list[object]:
    return list(
        load_2010_reconciliation_rows(
            ROOT,
            API_LEDGER_REL,
            "docs/requirements/ieee-1516-2010/api_binding_bounded_family.md",
        )
    )


def test_api_partial_tail_current_shape_is_stable() -> None:
    rows = _typed_rows()
    partial_rows = [row for row in rows if row.current_status == "partial"]
    kind_counts = Counter(row.mapping_kind for row in partial_rows)

    assert len(rows) == 614
    assert Counter(row.current_status for row in rows) == {
        "partial": 331,
        "mapped": 283,
    }
    assert kind_counts == {"WSDL_OP": 308, "CPP_CLASS": 17, "CLAUSE12_13_DETAIL": 6}


def test_api_ledger_is_explicitly_classified_as_mapping_bridge() -> None:
    survey = survey_requirement_artifacts(ROOT)
    entries_by_path = {entry.path: entry for entry in survey.entries}
    entry = entries_by_path[API_LEDGER_REL]

    assert entry.family == "mapping-bridge"
    assert entry.classification_basis == (
        "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims"
    )


def test_api_boundary_doc_records_current_family_shape() -> None:
    text = BOUNDARY_DOC.read_text(encoding="utf-8")

    for snippet in (
        "2010 API-Binding Bounded Family",
        "`614` packet rows",
        "`283 mapped`",
        "`331 partial`",
        "`308 WSDL_OP`",
        "`17 CPP_CLASS`",
        "`6 CLAUSE12_13_DETAIL`",
        "## Residual Read Rule",
        "## Residual Exit Rule",
        "`Canonical residual disposition:`",
        "`requirements/2010/canonical_requirements.json`",
        "`requirements/2010/backend_resolution.json`",
        "`requirements/2010/hla1516_1_api_detailed_reconciliation.csv`",
        "`requirements/2010/hla1516_1_conf_detailed_reconciliation.csv`",
        "`requirements/2010/traceability_matrix.csv`",
        "generated projection bridge",
        "`tests/verification/test_spec_traceability_all_methods.py`",
        "`tests/verification/test_requirements_ledger_v013.py`",
        "`tests/factories/test_fom_time_factories.py`",
        "`RTIambassadorFactory.h`",
        "`NullFederateAmbassador.h`",
        "`LogicalTimeFactory.h`",
        "`Handle.h`",
        "`VariableLengthData.h`",
        "`EncodingExceptions.h`",
        "`HLA1516.1-API_WSDL-013`",
        "`HLA1516.1-API_CPP_NORMATIVE-017`",
        "`HLA1516.1-API_WS_NORMATIVE-018`",
    ):
        assert snippet in text


def test_api_owner_surface_is_split_from_clause13_conformance_in_front_doors() -> None:
    front_door = FRONT_DOOR_DOC.read_text(encoding="utf-8")
    source_readme = SOURCE_README.read_text(encoding="utf-8")

    for text in (front_door, source_readme):
        assert "hla1516_1_api_detailed_reconciliation.csv" in text
        assert "api_binding_bounded_family.md" in text
        assert "hla1516_1_conf_detailed_reconciliation.csv" in text

    assert "API-binding rows | `../../../requirements/2010/hla1516_1_api_detailed_reconciliation.csv`" in front_door
    assert "Clause 13 conformance rows | `../../../requirements/2010/hla1516_1_conf_detailed_reconciliation.csv`" in front_door
