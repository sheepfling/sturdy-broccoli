from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements import load_2010_reconciliation_rows

try:
    from reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources
except ModuleNotFoundError:
    from tests.reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources

ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_PATH = (
    ROOT / "requirements" / "2010" / "hla1516_1_tm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_1_tm_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/time_management_bounded_family.md",
        )
    }


def _split_refs(refs: str) -> list[str]:
    return [item.strip() for item in refs.split(";") if item.strip()]


def _assert_reference_is_live(reference: str) -> None:
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


def test_tm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 301
    assert Counter(row["current_status"] for row in rows) == Counter({"mapped": 301})
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_tm_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-TM-OVERVIEW-009"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-OVERVIEW-010"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001"]["reconciliation_kind"] == "FED_CB"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001-ORD"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_3-FEDCB-001-ORD"]["reconciliation_kind"] == "CB_ORD"
    assert rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-TEST-001"]["reconciliation_kind"] == "TEST"
    assert (
        rows["HLA1516.1-TM-8_22-REQUESTRETRACTION-CB_PAYLOAD-001"]["current_status"]
        == "mapped"
    )
    assert (
        rows["HLA1516.1-TM-8_22-REQUESTRETRACTION-CB_PAYLOAD-001"][
            "reconciliation_kind"
        ]
        == "CB_PAYLOAD"
    )
    assert rows["HLA1516.1-TM-8_16-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_16-RTIAPI-001-RET"]["reconciliation_kind"] == "RET"
    assert rows["HLA1516.1-TM-8_16-QUERYGALT-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_16-QUERYGALT-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_16-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_17-QUERYLOGICALTIME-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_17-QUERYLOGICALTIME-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_17-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_18-QUERYLITS-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_18-QUERYLITS-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_18-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_20-QUERYLOOKAHEAD-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_20-QUERYLOOKAHEAD-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_20-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_2-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_4-DISABLETIMEREGULATION-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_4-DISABLETIMEREGULATION-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_4-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_5-ENABLETIMECONSTRAINED-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_5-ENABLETIMECONSTRAINED-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_5-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_7-DISABLETIMECONSTRAINED-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_7-DISABLETIMECONSTRAINED-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_7-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_8-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_9-TIMEADVANCEREQUESTAVAILABLE-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_9-TIMEADVANCEREQUESTAVAILABLE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_9-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_10-NEXTMESSAGEREQUEST-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_10-NEXTMESSAGEREQUEST-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_10-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_11-NEXTMESSAGEREQUESTAVAILABLE-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_11-NEXTMESSAGEREQUESTAVAILABLE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_11-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_12-FLUSHQUEUEREQUEST-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_12-FLUSHQUEUEREQUEST-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_12-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_14-ENABLEASYNCHRONOUSDELIVERY-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_14-ENABLEASYNCHRONOUSDELIVERY-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_14-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_15-DISABLEASYNCHRONOUSDELIVERY-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_15-DISABLEASYNCHRONOUSDELIVERY-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_15-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_19-MODIFYLOOKAHEAD-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_19-MODIFYLOOKAHEAD-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_19-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_21-RETRACT-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_21-RETRACT-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_23-CHANGEATTRIBUTEORDERTYPE-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_23-CHANGEATTRIBUTEORDERTYPE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_23-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_24-CHANGEINTERACTIONORDERTYPE-PRE-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_24-CHANGEINTERACTIONORDERTYPE-EXC-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-TM-8_24-RTIAPI-001-EXC"]["current_status"] == "mapped"
    assert "priority backend-resolution companion" in rows["HLA1516.1-TM-OVERVIEW-009"]["notes"]
    assert "applicable precondition surface" in rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-PRE-001"]["notes"]
    assert "invalid-lookahead" in rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-PRE-001"]["notes"]
    assert "immediate-grant witness" in rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-EXC-001"]["notes"]
    assert "within-callback rejection" in rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-PRE-001"]["notes"]
    assert "directly exercised `retract` guard surface" in rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["notes"]
    assert "MessageCanNoLongerBeRetracted" in rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["notes"]
    assert "zero-argument `queryGALT` service" in rows["HLA1516.1-TM-8_16-QUERYGALT-PRE-001"]["notes"]
    assert "exercised save or restore, membership, and connection guard surface for `queryGALT`" in rows["HLA1516.1-TM-8_16-QUERYGALT-EXC-001"]["notes"]
    assert "directly exercised `queryGALT` guard surface" in rows["HLA1516.1-TM-8_16-RTIAPI-001-EXC"]["notes"]
    assert "zero-argument `queryLogicalTime` service" in rows["HLA1516.1-TM-8_17-QUERYLOGICALTIME-PRE-001"]["notes"]
    assert "exercised save or restore, membership, and connection guard surface for `queryLogicalTime`" in rows["HLA1516.1-TM-8_17-QUERYLOGICALTIME-EXC-001"]["notes"]
    assert "directly exercised `queryLogicalTime` guard surface" in rows["HLA1516.1-TM-8_17-RTIAPI-001-EXC"]["notes"]
    assert "zero-argument `queryLITS` service" in rows["HLA1516.1-TM-8_18-QUERYLITS-PRE-001"]["notes"]
    assert "exercised save or restore, membership, and connection guard surface for `queryLITS`" in rows["HLA1516.1-TM-8_18-QUERYLITS-EXC-001"]["notes"]
    assert "directly exercised `queryLITS` guard surface" in rows["HLA1516.1-TM-8_18-RTIAPI-001-EXC"]["notes"]
    assert "zero-argument `queryLookahead` service" in rows["HLA1516.1-TM-8_20-QUERYLOOKAHEAD-PRE-001"]["notes"]
    assert "exercised time-regulation-enabled, save or restore, membership, and connection guard surface for `queryLookahead`" in rows["HLA1516.1-TM-8_20-QUERYLOOKAHEAD-EXC-001"]["notes"]
    assert "directly exercised `queryLookahead` guard surface" in rows["HLA1516.1-TM-8_20-RTIAPI-001-EXC"]["notes"]
    assert "full applicable precondition surface the Python RTI exposes" in rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-PRE-001"]["notes"]
    assert "invalid-lookahead, duplicate-regulation, time-advancing, save or restore, membership, and connection guard surface" in rows["HLA1516.1-TM-8_2-ENABLETIMEREGULATION-EXC-001"]["notes"]
    assert "directly exercised `enableTimeRegulation` guard surface" in rows["HLA1516.1-TM-8_2-RTIAPI-001-EXC"]["notes"]
    assert "disableTimeRegulation` public path" in rows["HLA1516.1-TM-8_4-DISABLETIMEREGULATION-PRE-001"]["notes"]
    assert "regulation-disabled, save or restore, membership, and connection guard surface" in rows["HLA1516.1-TM-8_4-DISABLETIMEREGULATION-EXC-001"]["notes"]
    assert "directly exercised `disableTimeRegulation` guard surface" in rows["HLA1516.1-TM-8_4-RTIAPI-001-EXC"]["notes"]
    assert "full applicable precondition surface the Python RTI exposes" in rows["HLA1516.1-TM-8_5-ENABLETIMECONSTRAINED-PRE-001"]["notes"]
    assert "duplicate-enable, time-advancing, save or restore, membership, and connection guard surface" in rows["HLA1516.1-TM-8_5-ENABLETIMECONSTRAINED-EXC-001"]["notes"]
    assert "directly exercised `enableTimeConstrained` guard surface" in rows["HLA1516.1-TM-8_5-RTIAPI-001-EXC"]["notes"]
    assert "disableTimeConstrained` public path" in rows["HLA1516.1-TM-8_7-DISABLETIMECONSTRAINED-PRE-001"]["notes"]
    assert "constrained-disabled, save or restore, membership, and connection guard surface" in rows["HLA1516.1-TM-8_7-DISABLETIMECONSTRAINED-EXC-001"]["notes"]
    assert "directly exercised `disableTimeConstrained` guard surface" in rows["HLA1516.1-TM-8_7-RTIAPI-001-EXC"]["notes"]
    assert "timeAdvanceRequest` public path" in rows["HLA1516.1-TM-8_8-TIMEADVANCEREQUEST-PRE-001"]["notes"]
    assert "immediate-grant witness" in rows["HLA1516.1-TM-8_8-RTIAPI-001-EXC"]["notes"]
    assert "timeAdvanceRequestAvailable` public path" in rows["HLA1516.1-TM-8_9-TIMEADVANCEREQUESTAVAILABLE-PRE-001"]["notes"]
    assert "nextMessageRequest` public path" in rows["HLA1516.1-TM-8_10-NEXTMESSAGEREQUEST-PRE-001"]["notes"]
    assert "nextMessageRequestAvailable` public path" in rows["HLA1516.1-TM-8_11-NEXTMESSAGEREQUESTAVAILABLE-PRE-001"]["notes"]
    assert "flushQueueRequest` public path" in rows["HLA1516.1-TM-8_12-FLUSHQUEUEREQUEST-PRE-001"]["notes"]
    assert "enableAsynchronousDelivery` public path" in rows["HLA1516.1-TM-8_14-ENABLEASYNCHRONOUSDELIVERY-PRE-001"]["notes"]
    assert "immediate-callback witness" in rows["HLA1516.1-TM-8_14-ENABLEASYNCHRONOUSDELIVERY-EXC-001"]["notes"]
    assert "directly exercised `enableAsynchronousDelivery` guard surface" in rows["HLA1516.1-TM-8_14-RTIAPI-001-EXC"]["notes"]
    assert "disableAsynchronousDelivery` public path" in rows["HLA1516.1-TM-8_15-DISABLEASYNCHRONOUSDELIVERY-PRE-001"]["notes"]
    assert "already-disabled async-delivery state" in rows["HLA1516.1-TM-8_15-DISABLEASYNCHRONOUSDELIVERY-EXC-001"]["notes"]
    assert "directly exercised `disableAsynchronousDelivery` guard surface" in rows["HLA1516.1-TM-8_15-RTIAPI-001-EXC"]["notes"]
    assert "modifyLookahead` public path" in rows["HLA1516.1-TM-8_19-MODIFYLOOKAHEAD-PRE-001"]["notes"]
    assert "invalid-lookahead, pending-advance, regulation-disabled" in rows["HLA1516.1-TM-8_19-MODIFYLOOKAHEAD-EXC-001"]["notes"]
    assert "directly exercised `modifyLookahead` guard surface" in rows["HLA1516.1-TM-8_19-RTIAPI-001-EXC"]["notes"]
    assert "retract` public path" in rows["HLA1516.1-TM-8_21-RETRACT-PRE-001"]["notes"]
    assert "message-retraction-handle validation, can-no-longer-be-retracted" in rows["HLA1516.1-TM-8_21-RETRACT-EXC-001"]["notes"]
    assert "directly exercised `retract` guard surface" in rows["HLA1516.1-TM-8_21-RTIAPI-001-EXC"]["notes"]
    assert "changeAttributeOrderType` public path" in rows["HLA1516.1-TM-8_23-CHANGEATTRIBUTEORDERTYPE-PRE-001"]["notes"]
    assert "attribute-ownership, attribute-definition, object-known" in rows["HLA1516.1-TM-8_23-CHANGEATTRIBUTEORDERTYPE-EXC-001"]["notes"]
    assert "directly exercised `changeAttributeOrderType` guard surface" in rows["HLA1516.1-TM-8_23-RTIAPI-001-EXC"]["notes"]
    assert "changeInteractionOrderType` public path" in rows["HLA1516.1-TM-8_24-CHANGEINTERACTIONORDERTYPE-PRE-001"]["notes"]
    assert "interaction-publication, interaction-definition" in rows["HLA1516.1-TM-8_24-CHANGEINTERACTIONORDERTYPE-EXC-001"]["notes"]
    assert "directly exercised `changeInteractionOrderType` guard surface" in rows["HLA1516.1-TM-8_24-RTIAPI-001-EXC"]["notes"]


def test_tm_partial_rows_use_explicit_bounded_envelope_notes() -> None:
    rows = _read_rows()
    partial_rows = [row for row in rows if row["current_status"] == "partial"]
    assert partial_rows == []


def test_tm_rows_anchor_to_live_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert references, f"{row['packet_requirement_id']} should carry evidence references"
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)
        for reference in references:
            _assert_reference_is_live(reference)


def test_tm_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())
