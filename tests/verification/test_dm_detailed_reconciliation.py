from __future__ import annotations

from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements import (
    load_2010_reconciliation_rows,
    survey_requirement_artifacts,
)

try:
    from reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources
except ModuleNotFoundError:
    from tests.reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources

ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_REL = "requirements/2010/hla1516_1_dm_detailed_reconciliation.csv"


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            RECONCILIATION_REL,
            "docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md",
        )
    }


def _typed_rows() -> list[object]:
    return list(_typed_rows_by_id().values())


def _typed_truth_source_rows() -> list[dict[str, str]]:
    return [
        {
            "packet_requirement_id": row.source_requirement_id,
            "current_test_id": ";".join(row.evidence_refs),
        }
        for row in _typed_rows()
    ]


def _assert_reference_is_live(reference: str) -> None:
    if "=" in reference and "::" not in reference:
        _label, reference = reference.split("=", 1)

    if "::" in reference:
        file_part, test_name = reference.split("::", 1)
        path = ROOT / file_part
        assert path.exists(), f"missing evidence file for {reference}"
        text = path.read_text(encoding="utf-8")
        base_name = test_name.split("[", 1)[0]
        assert (test_name in text or base_name in text), f"missing test anchor for {reference}"
        return

    path = ROOT / reference
    if path.exists():
        return

    matches: list[str] = []
    for candidate in (ROOT / "tests").rglob("*.py"):
        if f"def {reference}(" in candidate.read_text(encoding="utf-8"):
            matches.append(str(candidate.relative_to(ROOT)))
    assert matches, f"unresolved bare evidence ref {reference}"
    assert len(matches) == 1, f"ambiguous bare evidence ref {reference}: {matches}"


def test_declaration_detailed_reconciliation_has_expected_shape():
    rows = _typed_rows()

    assert len(rows) == 212
    assert Counter(row.mapping_kind for row in rows) == Counter(
        {
            "SIG": 28,
            "EFF": 26,
            "SVC": 20,
            "ARG": 14,
            "RTI_API": 14,
            "EXC_API": 14,
            "MOM_TRACE": 14,
            "EXC": 12,
            "MOM": 12,
            "PRE": 12,
            "TEST": 12,
            "CB": 8,
            "CB_SIG": 8,
            "FED_CB": 4,
            "CB_ORD": 4,
            "CB_ORDER": 4,
            "CB_PAYLOAD": 4,
            "OVW": 2,
        }
    )
    assert {row.source_packet_file for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_declaration_detailed_reconciliation_spot_checks_key_rows():
    rows = _typed_rows_by_id()

    assert rows["HLA1516.1-DM-OVERVIEW-004"].mapping_kind == "OVW"
    assert rows["HLA1516.1-DM-OVERVIEW-005"].mapping_kind == "OVW"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001"].mapping_kind == "RTI_API"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-EXC"].mapping_kind == "EXC_API"
    assert rows["HLA1516.1-DM-5_2-RTIAPI-001-MOM"].mapping_kind == "MOM_TRACE"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001"].mapping_kind == "FED_CB"
    assert rows["HLA1516.1-DM-5_10-FEDCB-001-ORD"].mapping_kind == "CB_ORD"
    assert rows["HLA1516.1-DM-5_12-FEDCB-001-SIG"].mapping_kind == "CB_SIG"
    assert rows["HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-TEST-001"].mapping_kind == "TEST"


def test_declaration_detailed_reconciliation_is_explicitly_classified_as_mapping_bridge() -> None:
    survey = survey_requirement_artifacts(ROOT)
    entries_by_path = {entry.path: entry for entry in survey.entries}
    entry = entries_by_path[RECONCILIATION_REL]

    assert entry.family == "mapping-bridge"
    assert entry.classification_basis == (
        "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims"
    )


def test_dm_rows_anchor_to_live_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for requirement_id, typed_row in typed_rows.items():
        references = list(typed_row.evidence_refs)
        assert references, f"{requirement_id} should carry evidence references"
        for reference in references:
            _assert_reference_is_live(reference)


def test_dm_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_typed_truth_source_rows())
