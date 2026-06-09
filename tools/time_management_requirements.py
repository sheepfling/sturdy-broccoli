from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeRequirement:
    requirement_id: str
    clause: str
    service: str
    expected_behavior: str
    required: bool = True


TIME_REQUIREMENTS: tuple[TimeRequirement, ...] = (
    TimeRequirement(
        "HLA1516.1-TM-8.1.4-LOWERBOUND-TEST-001",
        "8.1.4",
        "valid TSO lower bound",
        "Non-regulating federates make no GALT contribution; regulating federates use current/pending time plus lookahead.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.1.6-TSOQUEUE-TEST-001",
        "8.1.6",
        "timestamp-order queue",
        "TSO messages are recipient-filtered, retractable before delivery, ordered by timestamp/sequence, and popped through explicit boundaries.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.8-TIMEADVANCEREQUEST-TEST-001",
        "8.8",
        "timeAdvanceRequest",
        "TAR is strict with respect to GALT and does not deliver messages when the requested grant is unsafe.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.9-TIMEADVANCEREQUESTAVAILABLE-TEST-001",
        "8.9",
        "timeAdvanceRequestAvailable",
        "TARA permits equality at GALT and delivers eligible TSO messages through the requested time when safe.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.10-NEXTMESSAGEREQUEST-TEST-001",
        "8.10",
        "nextMessageRequest",
        "NMR grants at the earliest eligible TSO timestamp and groups equal earliest timestamps.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.11-NEXTMESSAGEREQUESTAVAILABLE-TEST-001",
        "8.11",
        "nextMessageRequestAvailable",
        "NMRA preserves NMR earliest-message behavior while allowing inclusive GALT boundaries.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.12-FLUSHQUEUEREQUEST-TEST-001",
        "8.12",
        "flushQueueRequest",
        "FQR grants at the earliest of request, deliverable TSO, and GALT, and delivers only messages through the computed grant boundary.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.16-QUERYGALT-TEST-001",
        "8.16",
        "queryGALT",
        "GALT is computed from other active regulating federates and is invalid when no contributor exists.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.17-QUERYLOGICALTIME-TEST-001",
        "8.17",
        "queryLogicalTime",
        "The RTI API reports local logical time before and after grants.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.18-QUERYLITS-TEST-001",
        "8.18",
        "queryLITS",
        "LITS is the minimum of valid GALT and recipient-local active queued TSO messages.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.19-MODIFYLOOKAHEAD-TEST-001",
        "8.19",
        "query/modify lookahead",
        "Lookahead is queryable after regulation, non-negative, and participates in lower-bound calculations.",
    ),
    TimeRequirement(
        "HLA1516.1-TM-8.22-REQUESTRETRACTION-TEST-001",
        "8.22",
        "requestRetraction/retract",
        "Retraction before delivery removes queued timestamp-order messages from the receiver callback path.",
    ),
)

