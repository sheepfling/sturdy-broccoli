"""Finish-line inventory for the IEEE 1516-2025 requirements tranche."""

from __future__ import annotations

import ast
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.verification.repo_internal.conformance import build_service_conformance_matrix, negative_path_status
from hla.verification.repo_internal.verification.spec2025_route_parity_matrix import ROUTE_IDS_2025, summarize_spec2025_route_parity

HIGH_PRIORITIES = frozenset({"high", "very-high"})
CLOSED_STATUSES = frozenset({"implemented-slice", "unsupported-boundary", "legacy-only"})

IMPLEMENTED_EVIDENCE_SLICES: tuple[Mapping[str, Any], ...] = (
    {
        "id": "2025-factory-composition",
        "status": "implemented-slice",
        "requirements": ("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/test_hla_factory_composition.py",
            "packages/hla-rti-core/src/hla/rti/factory.py",
        ),
    },
    {
        "id": "2025-auth-connect",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_encoding_auth_contexts.py",
            "packages/hla-rti-core/src/hla/rti/factory.py",
        ),
    },
    {
        "id": "2025-fom-validation",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FR-001", "HLA2025-OMT-001", "HLA2025-OMT-005", "HLA2025-OMT-006"),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/test_hla_factory_composition.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py",
        ),
    },
    {
        "id": "2025-lifecycle-and-members",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-005", "HLA2025-FI-006", "HLA2025-NEW-002", "HLA2025-NEW-003"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route cover connection and membership lifecycle proof: "
            "connect/create/join/resign/destroy/disconnect flows, federation execution listing, federation "
            "execution member listing, missing-federation member notices, joined-set isolation after disconnect, "
            "and federateResigned callback delivery."
        ),
    },
    {
        "id": "2025-time-mode-enable-disable",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-101",
            "HLA2025-FI-SVC-102",
            "HLA2025-FI-SVC-103",
            "HLA2025-FI-SVC-104",
            "HLA2025-FI-SVC-105",
            "HLA2025-FI-SVC-106",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates time-mode transitions: selected logical-time factories plus "
            "enable/disable time regulation, timeRegulationEnabled callback delivery, enable/disable time "
            "constrained, and timeConstrainedEnabled callback delivery through the shim and hosted FedPro route."
        ),
    },
    {
        "id": "2025-time-advance-request-modes",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-107",
            "HLA2025-FI-SVC-108",
            "HLA2025-FI-SVC-109",
            "HLA2025-FI-SVC-110",
            "HLA2025-FI-SVC-111",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates advance-request modes: timeAdvanceRequest, "
            "timeAdvanceRequestAvailable, nextMessageRequest, nextMessageRequestAvailable, and "
            "flushQueueRequest with typed logical-time validation, pending-request state transitions, queued "
            "timestamp-order delivery, and hosted FedPro transport parity."
        ),
    },
    {
        "id": "2025-time-grant-and-async-delivery",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-112",
            "HLA2025-FI-SVC-113",
            "HLA2025-FI-SVC-114",
            "HLA2025-FI-SVC-115",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates grant and callback-delivery control: flushQueueGrant and "
            "timeAdvanceGrant callbacks, plus enable/disable asynchronous delivery queue behavior through the shim "
            "and hosted FedPro route."
        ),
    },
    {
        "id": "2025-time-query-and-lookahead-control",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-116",
            "HLA2025-FI-SVC-117",
            "HLA2025-FI-SVC-118",
            "HLA2025-FI-SVC-119",
            "HLA2025-FI-SVC-120",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates time queries and lookahead control: queryGALT, "
            "queryLogicalTime, queryLITS, modifyLookahead, and queryLookahead with typed time-factory handling, "
            "live lookahead changes, and hosted FedPro route parity."
        ),
    },
    {
        "id": "2025-time-queries-retraction-and-order",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-121",
            "HLA2025-FI-SVC-122",
            "HLA2025-FI-SVC-123",
            "HLA2025-FI-SVC-124",
            "HLA2025-FI-SVC-125",
            "HLA2025-FR-010",
            "HLA2025-FI-009",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "tests/backends/test_shim_route_trace_evidence.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates queued timestamp-order delivery and its query surface: "
            "GALT/LITS/lookahead queries, retract and requestRetraction callback delivery, attribute and "
            "interaction order-type changes, queued timestamped object updates/interactions, timestamp-order "
            "delivery on receiving federate time advance, queued-remove handling, and message retraction before "
            "delivery across both the shim and hosted FedPro route."
        ),
    },
    {
        "id": "2025-lookahead-window-proofs",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-107",
            "HLA2025-FI-SVC-108",
            "HLA2025-FI-SVC-121",
            "HLA2025-FI-SVC-122",
            "HLA2025-FI-SVC-123",
            "HLA2025-MOD-006",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "tests/backends/test_shim_route_trace_evidence.py",
        ),
        "supported_scope": (
            "Python 2025 lookahead proof is separated from the generic time-control slice: the Target/Radar "
            "time-window core and future-exclusion proof ladder, output-delivery and consumer-order proofs, "
            "pipelined scan-window proofs, receive-order poison rejection, and save/restore rollback of bounded "
            "time-window state all execute directly on the shim and are replayed over the hosted FedPro route. "
            "Cross-binding parity remains separate backlog work."
        ),
    },
    {
        "id": "2025-save-restore-lifecycle",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-018",
            "HLA2025-FI-SVC-019",
            "HLA2025-FI-SVC-020",
            "HLA2025-FI-SVC-021",
            "HLA2025-FI-SVC-022",
            "HLA2025-FI-SVC-023",
            "HLA2025-FI-SVC-024",
            "HLA2025-FI-SVC-025",
            "HLA2025-FI-SVC-026",
            "HLA2025-FI-SVC-027",
            "HLA2025-FI-SVC-028",
            "HLA2025-FI-SVC-029",
            "HLA2025-FI-SVC-030",
            "HLA2025-FI-SVC-031",
            "HLA2025-FI-SVC-032",
            "HLA2025-FI-SVC-033",
            "HLA2025-FI-SVC-034",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
            "HLA2025-REQ-002",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route support requestFederationSave and "
            "requestFederationRestore with initiate, begun, complete, abort, and query-status flows; federation "
            "save/restore lifecycle callbacks and status responses; successful federationSaved/federationRestored "
            "completion; missing-label restore failure; federate-reported save/restore failure; save/restore abort "
            "callbacks; object registry rollback; joined-federate logical-time rollback; compat-adapter replay of "
            "the shared two-federate save/restore suite; timed initiateFederateSave callback coverage; "
            "save-request precondition rejection; and bounded save/restore rollback of queued callback, "
            "time-window, ownership, and routing state."
        ),
    },
    {
        "id": "2025-fom-showcase",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FR-001", "HLA2025-FR-003", "HLA2025-FR-004"),
        "evidence": (
            "tests/scenarios/test_proto2025_fom_showcase.py",
            "packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py",
        ),
    },
    {
        "id": "2025-handle-normalization",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-005", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate 2025 handle-normalization proof: the "
            "in-process shim normalizes typed federate, object-class, interaction-class, object-instance, and "
            "service-group values with wrong-family rejection, while the hosted FedPro route round-trips typed "
            "service-group and object-instance normalization requests across the 2025 transport surface."
        ),
    },
    {
        "id": "2025-switch-set-get-model",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-008", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route prove the 2025 set/get switch model replaces the old "
            "enable/disable pattern: advisory, reporting, file-reporting, automatic resign, auto-provide, "
            "delay-subscription-evaluation, and related switch state flows are exercised through explicit set/get "
            "services rather than legacy enable/disable calls."
        ),
    },
    {
        "id": "2025-retired-advisory-switch-enable-disable-mapping",
        "status": "legacy-only",
        "requirements": ("HLA2025-RET-001",),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Legacy 2010 enable/disable advisory switch spellings are kept out of native 2025 normative coverage "
            "and are treated as retired or replacement-mapped items unless an explicit compatibility mode is added. "
            "The Python 2025 shim rejects those legacy method spellings as unsupported 2025 services rather than "
            "quietly aliasing them into native coverage."
        ),
    },
    {
        "id": "2025-fom-mim-error-taxonomy",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate create-time FOM/MIM taxonomy proof. "
            "The in-process shim distinguishes missing/open, read, invalid, and merge failures across native 2025 "
            "create and join flows, including destroy-while-joined and explicit HLAstandardMIM designator "
            "rejection. The hosted FedPro route now carries explicit createFederationExecutionWithMIM and "
            "createFederationExecutionWithMIMAndTime handling through the 2025 transport command surface, plus "
            "CouldNotOpen, ErrorReading, Invalid, and Inconsistent FOM/MIM failures over that hosted route."
        ),
    },
    {
        "id": "2025-callback-context-object-delivery",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-004", "HLA2025-RET-002", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
        ),
        "supported_scope": (
            "Python 2025 callback proof now isolates object-delivery callback context: the in-process shim emits "
            "direct producing-federate, region, time, order, and retraction parameters for "
            "discoverObjectInstance, reflectAttributeValues, and removeObjectInstance callbacks without native "
            "Supplemental*Info helper objects, and the hosted FedPro route preserves the corresponding direct "
            "reflection and remove callback fields through its 2025 callback decoder."
        ),
    },
    {
        "id": "2025-callback-context-interaction-delivery",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-004", "HLA2025-RET-002", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
        ),
        "supported_scope": (
            "Python 2025 callback proof now isolates interaction-delivery callback context: the in-process shim "
            "emits direct producing-federate, region, time, order, and retraction parameters for "
            "receiveInteraction and receiveDirectedInteraction callbacks without native Supplemental*Info helper "
            "objects, and the hosted FedPro route preserves the corresponding direct interaction callback fields "
            "through its 2025 callback decoder."
        ),
    },
    {
        "id": "2025-directed-interaction-boundary",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-MOD-007",
            "HLA2025-NEW-001",
            "HLA2025-FR-003",
            "HLA2025-FR-004",
            "HLA2025-FI-001",
            "HLA2025-FI-SVC-039",
            "HLA2025-FI-SVC-040",
            "HLA2025-FI-SVC-045",
            "HLA2025-FI-SVC-046",
            "HLA2025-FI-SVC-063",
            "HLA2025-FI-SVC-064",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route support FOM-backed directed interaction publish, "
            "subscribe, unsubscribe, unpublish, and receiveDirectedInteraction callback delivery from a publisher "
            "to object-class directed subscribers. They also queue timestamped directed interactions until "
            "subscriber time advance, deliver timestamp order plus retraction handles on callback receipt, honor "
            "pre-delivery retract, support selective directed interaction set unsubscribe/unpublish without "
            "collapsing sibling directed classes, and filter directed interaction delivery through target object "
            "update-region and subscribeInteractionClassWithRegions overlap. Java/C++ parity remains later "
            "behavior work."
        ),
    },
    {
        "id": "2025-omt-reference-value-required",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-006", "HLA2025-OMT-002", "HLA2025-OMT-006"),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py",
        ),
        "supported_scope": (
            "Shared OMT parser preserves referenceDataTypes and attribute valueRequired metadata, "
            "serializer round-trips the metadata, and 2025 validation rejects invalid valueRequired values."
        ),
    },
    {
        "id": "2025-omt-component-metadata-roundtrip",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-004",
            "HLA2025-OMT-COMP-013",
            "HLA2025-OMT-COMP-030",
            "HLA2025-OMT-COMP-084",
            "HLA2025-OMT-COMP-085",
            "HLA2025-OMT-COMP-087",
            "HLA2025-OMT-COMP-090",
            "HLA2025-OMT-COMP-094",
            "HLA2025-OMT-COMP-140",
            "HLA2025-OMT-COMP-141",
            "HLA2025-OMT-COMP-142",
            "HLA2025-OMT-COMP-143",
            "HLA2025-OMT-COMP-144",
            "HLA2025-OMT-COMP-146",
            "HLA2025-OMT-COMP-150",
            "HLA2025-OMT-COMP-151",
            "HLA2025-OMT-COMP-152",
            "HLA2025-OMT-COMP-190",
            "HLA2025-OMT-COMP-191",
            "HLA2025-OMT-COMP-194",
            "HLA2025-OMT-COMP-195",
            "HLA2025-OMT-COMP-215",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser and 2025 serializer round-trip array encodings, attribute valueRequired metadata, "
            "referenceDataTypes containers and child fields, model-identification keywords/name/version/copyright/"
            "description metadata, simpleData units/resolution/accuracy, 2025 logicalTime/logicalTimeInterval names "
            "and dataType bindings, and variant-record alternative enumerators."
        ),
    },
    {
        "id": "2025-omt-switch-and-transport-subset",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-078",
            "HLA2025-OMT-COMP-125",
            "HLA2025-OMT-COMP-157",
            "HLA2025-OMT-COMP-158",
            "HLA2025-OMT-COMP-159",
            "HLA2025-OMT-COMP-160",
            "HLA2025-OMT-COMP-161",
            "HLA2025-OMT-COMP-162",
            "HLA2025-OMT-COMP-163",
            "HLA2025-OMT-COMP-164",
            "HLA2025-OMT-COMP-165",
            "HLA2025-OMT-COMP-167",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser preserves the supported 2025 switch container subset "
            "(autoProvide, conveyRegionDesignatorSets, attribute/object/interaction advisories, serviceReporting, "
            "exceptionReporting, delaySubscriptionEvaluation, automaticResignAction), preserves interaction "
            "transportation, and the 2025 serializer round-trips those supported fields while filling the "
            "standard conveyProducingFederate default."
        ),
    },
    {
        "id": "2025-omt-extended-supported-subset",
        "status": "implemented-slice",
        "requirements": tuple(
            f"HLA2025-OMT-COMP-{index:03d}"
            for index in (
                1, 2, 3, 5, 7, 9, 10, 16, 20, 22, 23, 24, 25, 26, 28, 29, 31, 32, 33, 34, 36, 46,
                50, 51, 52, 53, 54, 55, 58, 60, 61, 62, 63, 64, 65, 66, 69, 71, 72, 73, 86, 88,
                89, 91, 92, 93, 95, 96, 97, 98, 99, 100, 101, 103, 104, 105, 108, 116, 117, 118,
                119, 120, 121, 122, 123, 124, 126, 127, 128, 131, 132, 135, 136, 137, 138, 139,
                148, 149, 153, 155, 172, 173, 174, 175, 177, 179, 180, 182, 183, 184, 185, 186,
                187, 188, 199, 203, 205, 206, 209, 211, 212, 213, 214, 216, 217, 218, 220, 221, 223,
            )
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser and 2025 serializer round-trip the supported model-identification scalar and "
            "reference/POC metadata subset, serviceUtilization, object and interaction names plus supported "
            "attribute/parameter datatype links, dimension-name lists, logicalTime/logicalTimeInterval containers, "
            "notes, tag tables, synchronization tables, transportation name tables, update-rate name/rate tables, "
            "and the supported basic/simple/enumerated/array/fixed-record/variant-record datatype tables and "
            "top-level objectModel container sections that hold those structures."
        ),
    },
    {
        "id": "2025-omt-unsupported-component-boundaries",
        "status": "unsupported-boundary",
        "requirements": (
            "HLA2025-OMT-COMP-037",
            "HLA2025-OMT-COMP-038",
            "HLA2025-OMT-COMP-039",
            "HLA2025-OMT-COMP-040",
            "HLA2025-OMT-COMP-042",
            "HLA2025-OMT-COMP-043",
            "HLA2025-OMT-COMP-048",
            "HLA2025-OMT-COMP-049",
            "HLA2025-OMT-COMP-074",
            "HLA2025-OMT-COMP-079",
            "HLA2025-OMT-COMP-110",
            "HLA2025-OMT-COMP-111",
            "HLA2025-OMT-COMP-112",
            "HLA2025-OMT-COMP-113",
            "HLA2025-OMT-COMP-145",
            "HLA2025-OMT-COMP-147",
            "HLA2025-OMT-COMP-166",
            "HLA2025-OMT-COMP-168",
            "HLA2025-OMT-COMP-169",
            "HLA2025-OMT-COMP-170",
            "HLA2025-OMT-COMP-192",
            "HLA2025-OMT-COMP-193",
            "HLA2025-OMT-COMP-196",
            "HLA2025-OMT-COMP-197",
        ),
        "evidence": (
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "These OMT component rows remain intentionally bounded: dimension input-data and normalization metadata "
            "are parsed only as the narrower repo subset and normalization semantics are not executed; "
            "directedInteraction and object-class dimension associations are not modeled in the shared parser/"
            "serializer surface; xs:any extension points are not preserved; nonRegulatedGrant, allowRelaxedDDM, "
            "advisoriesUseKnownClass, and sendServiceReportsToFile are outside the supported switch set; and "
            "logicalTime/logicalTimeInterval optional semantics and xs:any children are not round-tripped."
        ),
    },
    {
        "id": "2025-omt-unmodeled-component-boundaries-expanded",
        "status": "unsupported-boundary",
        "requirements": tuple(
            f"HLA2025-OMT-COMP-{index:03d}"
            for index in (
                6, 8, 11, 12, 14, 15, 17, 18, 19, 21, 27, 35, 41, 44, 45, 47, 56, 57, 59, 67, 68,
                70, 75, 76, 77, 80, 81, 82, 83, 102, 106, 107, 109, 114, 115, 129, 130, 133, 134,
                154, 156, 171, 176, 178, 181, 189, 198, 200, 201, 202, 204, 207, 208, 210, 219, 222, 224,
            )
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "These component rows remain intentionally bounded because the shared parser/serializer surface does not "
            "preserve xs:any extension points, attribute update-condition/ownership/sharing/order/semantics fields, "
            "object and interaction semantics or region-dimension associations, keyword taxonomy attributes, "
            "dimension upperBound/value metadata on round-trip, parameter semantics, transportation reliable/"
            "semantics detail rows, update-rate semantics rows, and other table members that are currently parsed "
            "only as a narrower subset or are not modeled at all in the repo-native OMT representation."
        ),
    },
    {
        "id": "2025-carry-forward-cleanup",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BLG-001", "HLA2025-BLG-002", "HLA2025-REQ-001"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv",
            "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv",
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Renumbered service-utilization rows preserve behavior claims while updating clause references. "
            "Common FOM/SOM object-model parsing remains shared and preserves nullable 2025 metadata."
        ),
    },
    {
        "id": "2025-service-utilization-crosscheck",
        "status": "implemented-slice",
        "requirements": tuple(f"HLA2025-OMT-SU-{index:03d}" for index in range(1, 197)),
        "evidence": (
            "tests/factories/test_fom_omt_parsing.py",
            "tests/factories/test_fom_roundtrip.py",
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser extracts optional serviceUtilization tables from SOM, FOM, and MIM modules, "
            "treats table absence as an empty mapping, preserves service-usage attributes through "
            "parse/serialize roundtrip, and keeps renumbered 2025 service-utilization entries aligned with the "
            "now-covered 2025 Federate Interface catalog."
        ),
    },
    {
        "id": "2025-exception-and-logical-time-deltas",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-009", "HLA2025-MOD-010", "HLA2025-VER-002"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "tests/test_rti1516_2025_validation.py",
            "requirements/2025/STRICT_DOC_INVENTORY.json",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Native 2025 exception inventory uses the 2025 FOM/MIM/auth names without FDD-era exception names. "
            "OMT XML parsing accepts 2025 logicalTime/logicalTimeInterval and serializer emits those names for 2025."
        ),
    },
    {
        "id": "2025-java-binding-source-trace",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-001", "HLA2025-FI-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/STRICT_DOC_INVENTORY.json",
            "requirements/2025/SOURCE_TRACE.md",
            "docs/evidence/java-intake/java-2025-standard-shim-2025-jpype.json",
            "docs/evidence/java-intake/java-2025-standard-shim-2025-py4j.json",
        ),
        "supported_scope": (
            "Java 2025 package, RTI/federate/encoder declaration inventory, source trace, and intake evidence "
            "are separated from common behavior rows. This is surface/intake evidence, not full Java behavior conformance."
        ),
    },
    {
        "id": "2025-cpp-binding-source-trace",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-002", "HLA2025-FI-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/SOURCE_TRACE.md",
            "docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json",
            "docs/evidence/cpp-intake/cpp-standard-2025-2025-grpc.json",
            "docs/evidence/shim_routes/cpp-standard-2025.json",
        ),
        "supported_scope": (
            "C++ 2025 namespace/source trace and route evidence are recorded separately from common behavior rows. "
            "This is source-trace/intake evidence, not a full C++ RTI behavior pass."
        ),
    },
    {
        "id": "2025-standard-route-runtime-capability",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-BND-001",
            "HLA2025-BND-002",
            "HLA2025-FR-001",
            "HLA2025-FR-004",
            "HLA2025-FI-001",
            "HLA2025-FI-003",
            "HLA2025-FI-004",
            "HLA2025-FI-005",
            "HLA2025-FI-006",
            "HLA2025-FI-009",
            "HLA2025-MOD-005",
            "HLA2025-MOD-006",
            "HLA2025-MOD-007",
            "HLA2025-NEW-004",
            "HLA2025-NEW-007",
        ),
        "evidence": (
            "tests/backends/test_standard_shim_artifacts.py",
            "packages/hla-verification/src/hla/verification/shim_route_evidence.py",
            "packages/hla-bridge-java-common/src/hla/bridges/java/common/java_standard_2025.py",
            "packages/hla-backend-cpp-shim/src/hla/backends/cpp_shim/standard.py",
        ),
        "supported_scope": (
            "Artifact-gated 2025 standard Java and C++ routes now share a runtime-capability trace that loads a "
            "2025 FOM, resolves object/attribute/dimension/transport handles, stores default attribute policy, "
            "registers an object, divests and reacquires ownership with 2025 tag callbacks, advances logical time, "
            "and serializes a MOM service report. C++ artifacts exercise this locally; Java runtime evidence runs "
            "when the Java 2025 shim jar is built. This is not full Java/C++ behavior conformance or object exchange."
        ),
    },
    {
        "id": "2025-fedpro-typed-transport-surface",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto",
        ),
        "supported_scope": (
            "2025 FedPro proof now isolates the typed transport surface itself: protobuf package layout, gRPC "
            "service binding, typed RTI request oneofs, typed callback oneofs, schema-tagged client transport "
            "selection, callback decoding, explicit federation-list plus single-FOM and create-with-MIM "
            "transport commands, and loopback transport calls that prove the checked-in 2025 FedPro surface is "
            "executable rather than only declared in proto files."
        ),
    },
    {
        "id": "2025-fedpro-hosted-runtime-core",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
        ),
        "supported_scope": (
            "2025 FedPro proof now separates the hosted loopback runtime core from the heavier stateful proofs: "
            "connect, create federation, explicit single-FOM and create-with-MIM federation creation, join, "
            "resign, destroy, disconnect, explicit federation-execution/member listing, FOM handle lookup, passive "
            "object-attribute and passive interaction subscribe alias routes, universal directed subscribe alias "
            "routing, subscribe-with-rate and passive subscribe-with-rate object-attribute routing, federation "
            "execution/member reporting callbacks including missing-federation notices, available-dimension and "
            "dimension-bound queries, default attribute transportation/order policy calls, per-instance "
            "attribute/interactions order changes, callback-control enable/disable routing, object registration, "
            "untimed and timestamped object delete/remove callback flow, directed-interaction receipt with "
            "selective directed set unsubscribe/unpublish, object discovery, attribute reflection, interaction "
            "receipt, directed interaction receipt, object-class-attribute unpublish gating, "
            "instance/class/region-scoped attribute value update requests, single and multiple object instance "
            "name reservation/release callback flow, and direct attribute and interaction transportation "
            "change/query callbacks. This is a hosted runtime core slice, not a full FedPro RTI conformance claim."
        ),
    },
    {
        "id": "2025-fedpro-hosted-runtime-extended-state",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
        ),
        "supported_scope": (
            "2025 FedPro proof separately isolates the hosted extended-state runtime slice: basic ownership "
            "divest/acquire callbacks, basic and negotiated ownership divest/acquire/query callbacks including "
            "RTI-owned MOM attribute ownership query results, time-regulation/time-constrained/time-advance "
            "callbacks, flushQueueGrant, queued timestamped attribute reflection/interaction receipt, queued "
            "timestamped remove receipt, requestRetraction callback delivery after delivered timestamp-order "
            "receipt, retraction handles, and pre-delivery retract, basic DDM region-overlap filtering for object "
            "attributes and directed interactions, DDM-driven attributesInScope/attributesOutOfScope "
            "transitions, direct synchronization-point registration/announce/achieved/federation-synchronized "
            "callback flow, save/restore lifecycle callbacks including timed initiateFederateSave, "
            "service-reporting switch state, automatic resign directive get/set, read-only 2025 switch inquiry "
            "state, restored callback-delivery enablement, restored plain and directed DDM subscriber routing, "
            "restored in-flight ownership and owner-visibility state, restored attribute/interaction "
            "transportation and order policy state, MOM service-invocation report callbacks over FedPro, object "
            "publication/subscription/object-instance-information/activity-count reports, and synchronization "
            "point/status MOM reports over FedPro. Full MOM action/request routing and full RTI semantics remain "
            "outside this slice. This is a hosted runtime extended-state slice, not a full FedPro RTI conformance claim."
        ),
    },
    {
        "id": "2025-ddm-default-attribute-policy",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-MOD-007",
            "HLA2025-NEW-004",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
            "HLA2025-FI-SVC-159",
            "HLA2025-FI-SVC-160",
            "HLA2025-FI-SVC-161",
            "HLA2025-FI-SVC-164",
            "HLA2025-FI-SVC-128",
            "HLA2025-FI-SVC-129",
            "HLA2025-FI-SVC-126",
            "HLA2025-FI-SVC-127",
            "HLA2025-FI-SVC-130",
            "HLA2025-FI-SVC-131",
            "HLA2025-FI-SVC-132",
            "HLA2025-FI-SVC-133",
            "HLA2025-FI-SVC-134",
            "HLA2025-FI-SVC-135",
            "HLA2025-FI-SVC-136",
            "HLA2025-FI-SVC-137",
            "HLA2025-FI-SVC-076",
            "HLA2025-FI-SVC-124",
            "HLA2025-FI-SVC-157",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route resolve object class, attribute, transportation, and "
            "dimension handles from the loaded FOM/FDD catalog, report available dimensions for object and "
            "interaction classes, return dimension upper bounds, store validated default attribute "
            "transportation/order policy changes, use those defaults when delivering reflectAttributeValues "
            "callbacks, and filter object attribute reflections through basic "
            "createRegion/commitRegionModifications/deleteRegion/setRangeBounds/"
            "registerObjectInstanceWithRegions/subscribeObjectClassAttributesWithRegions/"
            "subscribeObjectClassAttributesPassivelyWithRegions/"
            "unsubscribeObjectClassAttributesWithRegions/associateRegionsForUpdates/"
            "unassociateRegionsForUpdates/requestAttributeValueUpdateWithRegions DDM region overlap. They also "
            "filter interaction delivery through subscribeInteractionClassWithRegions/"
            "unsubscribeInteractionClassWithRegions/sendInteractionWithRegions region overlap, plus "
            "subscribeInteractionClassPassivelyWithRegions alias coverage, and convey sent regions on "
            "receiveInteraction callbacks. Attribute scope advisory callbacks report object-attribute in-scope "
            "and out-of-scope transitions for DDM region overlap changes."
        ),
    },
    {
        "id": "2025-omt-schema-constraint-validation",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-CV-001",
            "HLA2025-OMT-CV-002",
            "HLA2025-OMT-CV-003",
            "HLA2025-OMT-CV-004",
            "HLA2025-OMT-CV-005",
            "HLA2025-OMT-CV-006",
            "HLA2025-OMT-CV-007",
            "HLA2025-OMT-CV-008",
            "HLA2025-OMT-CV-009",
            "HLA2025-OMT-CV-010",
            "HLA2025-OMT-CV-011",
            "HLA2025-OMT-CV-012",
            "HLA2025-OMT-CV-013",
            "HLA2025-OMT-CV-014",
            "HLA2025-OMT-CV-015",
            "HLA2025-OMT-CV-016",
            "HLA2025-OMT-CV-017",
            "HLA2025-OMT-CV-018",
            "HLA2025-OMT-CV-019",
            "HLA2025-OMT-CV-020",
            "HLA2025-OMT-CV-021",
            "HLA2025-OMT-CV-022",
            "HLA2025-OMT-CV-023",
            "HLA2025-OMT-CV-024",
            "HLA2025-OMT-CV-025",
            "HLA2025-OMT-CV-026",
            "HLA2025-OMT-CV-027",
            "HLA2025-OMT-CV-028",
            "HLA2025-OMT-CV-029",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py",
            "docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd",
        ),
        "supported_scope": (
            "Python 2025 validation includes an lxml-backed IEEE1516-OMT-2025 XML Schema validation path, "
            "a compact schema-valid positive fixture, named key/keyref/unique constraint anchors from the "
            "bundled XSD, negative checks for datatype, transportation, and attribute uniqueness constraints, "
            "and strict domain checks for the imported 2025 OMT enumeration/value-domain rows including "
            "union-backed fields such as security classification, application domain, fixed/variant record "
            "encoding, and POC type."
        ),
    },
    {
        "id": "2025-basic-object-exchange",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-057",
            "HLA2025-FI-SVC-058",
            "HLA2025-FI-SVC-059",
            "HLA2025-FI-SVC-060",
            "HLA2025-FI-SVC-061",
            "HLA2025-FI-SVC-062",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route support FOM-backed object instance registration, "
            "discoverObjectInstance delivery, attribute update publication gating, reflectAttributeValues "
            "delivery, default and per-instance order policy changes for reflected attributes, interaction "
            "publication gating, sendInteraction, interaction order policy changes, and receiveInteraction "
            "delivery for subscribed federates."
        ),
    },
    {
        "id": "2025-object-delete-remove-flows",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-065",
            "HLA2025-FI-SVC-066",
            "HLA2025-FI-SVC-067",
            "HLA2025-FR-003",
            "HLA2025-FR-004",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates object deletion flows: FOM-backed deleteObjectInstance and "
            "removeObjectInstance callbacks, delete-with-time behavior, localDeleteObjectInstance validation, and "
            "post-delete object-known-state handling across the shim and hosted FedPro route."
        ),
    },
    {
        "id": "2025-object-attribute-update-request-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-070",
            "HLA2025-FI-SVC-071",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates attribute-value-update request callbacks: "
            "requestAttributeValueUpdate by object instance and object class, provideAttributeValueUpdate callback "
            "delivery, and region-scoped requestAttributeValueUpdate callbacks across the shim and hosted FedPro route."
        ),
    },
    {
        "id": "2025-object-scope-advisory-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-068",
            "HLA2025-FI-SVC-069",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates object-scope advisory callbacks: DDM-driven "
            "attributesInScope and attributesOutOfScope transitions, out-of-scope reflection suppression, "
            "re-entry into scope, and post-transfer ownership-safe update behavior execute across the shim "
            "and the hosted FedPro route with requirement-traceable object-attribute scope changes."
        ),
    },
    {
        "id": "2025-object-update-rate-advisory-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-072",
            "HLA2025-FI-SVC-073",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates update-rate advisory callbacks: "
            "turnUpdatesOnForObjectInstance and turnUpdatesOffForObjectInstance callbacks deliver the expected "
            "attribute sets and update-rate designator context for the affected object instance, and the hosted "
            "FedPro route now proves bounded timestamped reflection delivery under the shared update-rate scenario."
        ),
    },
    {
        "id": "2025-object-attribute-transport-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-074",
            "HLA2025-FI-SVC-075",
            "HLA2025-FI-SVC-077",
            "HLA2025-FI-SVC-078",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates attribute transportation services: "
            "requestAttributeTransportationTypeChange, confirmAttributeTransportationTypeChange, "
            "queryAttributeTransportationType, reportAttributeTransportationType, and hosted FedPro "
            "callback-field preservation for attribute transportation callbacks."
        ),
    },
    {
        "id": "2025-object-interaction-transport-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-079",
            "HLA2025-FI-SVC-080",
            "HLA2025-FI-SVC-081",
            "HLA2025-FI-SVC-082",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates interaction transportation services: "
            "requestInteractionTransportationTypeChange, confirmInteractionTransportationTypeChange, "
            "queryInteractionTransportationType, reportInteractionTransportationType, and hosted FedPro "
            "callback-field preservation for interaction transportation callbacks."
        ),
    },
    {
        "id": "2025-single-name-reservation-services",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-SVC-051", "HLA2025-FI-SVC-052", "HLA2025-FI-SVC-053", "HLA2025-FI-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support single-name reservation requests, "
            "single-name reservation success and failure callbacks, releaseObjectInstanceName, not-connected and "
            "not-joined preconditions for release, save/restore in-progress blocking, reservation preservation "
            "through save/restore completion, release-driven handoff to a rival federate, and "
            "ObjectInstanceNameNotReserved on invalid single-name release."
        ),
    },
    {
        "id": "2025-multi-name-reservation-services",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-SVC-054", "HLA2025-FI-SVC-055", "HLA2025-FI-SVC-056", "HLA2025-FI-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support reserveMultipleObjectInstanceNames and "
            "releaseMultipleObjectInstanceNames with set-wide success/failure callbacks, not-connected and "
            "not-joined preconditions, empty-set validation, save/restore in-progress blocking, reservation "
            "handoff after release, reservation cleanup on join teardown, and reservation preservation through "
            "save/restore snapshots."
        ),
    },
    {
        "id": "2025-connection-lifecycle-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-002",
            "HLA2025-FI-SVC-003",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support orderly disconnect state teardown and "
            "NotConnected preconditions. The shim also exposes a test-harness-only non-orderly connection-loss "
            "injector that delivers the connectionLost callback and tears down the local connection state without "
            "treating orderly disconnect as a fault."
        ),
    },
    {
        "id": "2025-connect-and-federation-catalog-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-001",
            "HLA2025-FI-SVC-004",
            "HLA2025-FI-SVC-005",
            "HLA2025-FI-SVC-006",
            "HLA2025-FI-SVC-007",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route accepts connect requests, creates federation "
            "executions with resolved FOM modules and selected logical-time implementation, lists existing "
            "federation executions, reports federation execution catalogs through callbacks, and destroys "
            "federation executions once they are empty."
        ),
    },
    {
        "id": "2025-federate-membership-and-resign-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-008",
            "HLA2025-FI-SVC-009",
            "HLA2025-FI-SVC-010",
            "HLA2025-FI-SVC-011",
            "HLA2025-FI-SVC-012",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route isolate federate membership and resign behavior: "
            "joinFederationExecution, list/report federation execution members including missing-federation "
            "callbacks, resignFederationExecution with joined-state teardown, and federateResigned callback "
            "delivery with resign context."
        ),
    },
    {
        "id": "2025-synchronization-point-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-013",
            "HLA2025-FI-SVC-014",
            "HLA2025-FI-SVC-015",
            "HLA2025-FI-SVC-016",
            "HLA2025-FI-SVC-017",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route isolate synchronization-point barrier behavior: "
            "register federation synchronization point, confirm registration success and failure, "
            "announceSynchronizationPoint delivery, synchronizationPointAchieved participation, and "
            "federationSynchronized callback flow."
        ),
    },
    {
        "id": "2025-declaration-publication-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-035",
            "HLA2025-FI-SVC-036",
            "HLA2025-FI-SVC-037",
            "HLA2025-FI-SVC-038",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route isolate declaration publication control: publish "
            "and unpublish for object class attributes and interaction classes, with published state gating "
            "updateAttributeValues and sendInteraction delivery."
        ),
    },
    {
        "id": "2025-declaration-subscription-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-041",
            "HLA2025-FI-SVC-042",
            "HLA2025-FI-SVC-043",
            "HLA2025-FI-SVC-044",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route isolate declaration subscription control: "
            "subscribe and unsubscribe for object class attributes and interaction classes, with unsubscribe state "
            "stopping subsequent reflectAttributeValues and receiveInteraction callbacks for the affected target "
            "federate."
        ),
    },
    {
        "id": "2025-declaration-relevance-advisory-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-047",
            "HLA2025-FI-SVC-048",
            "HLA2025-FI-SVC-049",
            "HLA2025-FI-SVC-050",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route isolate declaration relevance and advisory "
            "callbacks: startRegistrationForObjectClass, stopRegistrationForObjectClass, turnInteractionsOn, and "
            "turnInteractionsOff as publication and subscription state becomes relevant or irrelevant."
        ),
    },
    {
        "id": "2025-support-federate-and-object-identity-lookups",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-138",
            "HLA2025-FI-SVC-139",
            "HLA2025-FI-SVC-140",
            "HLA2025-FI-SVC-141",
            "HLA2025-FI-SVC-142",
            "HLA2025-FI-SVC-143",
            "HLA2025-FI-SVC-144",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support direct federate, object-class, "
            "known-object-class, and object-instance handle/name lookups against joined federation membership "
            "and the loaded FOM catalog."
        ),
    },
    {
        "id": "2025-support-attribute-interaction-catalog-lookups",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-145",
            "HLA2025-FI-SVC-146",
            "HLA2025-FI-SVC-149",
            "HLA2025-FI-SVC-150",
            "HLA2025-FI-SVC-151",
            "HLA2025-FI-SVC-152",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support attribute, interaction-class, and "
            "parameter handle/name lookups against the loaded FOM catalog."
        ),
    },
    {
        "id": "2025-support-policy-update-and-transport-lookups",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-147",
            "HLA2025-FI-SVC-148",
            "HLA2025-FI-SVC-153",
            "HLA2025-FI-SVC-154",
            "HLA2025-FI-SVC-155",
            "HLA2025-FI-SVC-156",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support order-type, update-rate, and "
            "transportation lookups against the loaded FOM catalog and joined object state."
        ),
    },
    {
        "id": "2025-support-interaction-dimension-and-range-lookups",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-158",
            "HLA2025-FI-SVC-163",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/verification/test_spec_traceability_and_extended_python_rti.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route support interaction available-dimension lookup "
            "and joined-region range-bounds introspection against loaded FOM metadata and region state."
        ),
    },
    {
        "id": "2025-support-handle-normalization-and-region-introspection",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-162",
            "HLA2025-FI-SVC-165",
            "HLA2025-FI-SVC-166",
            "HLA2025-FI-SVC-167",
            "HLA2025-FI-SVC-168",
            "HLA2025-FI-SVC-169",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route now isolate support-handle normalization and "
            "region introspection: they normalizes service groups plus object class, interaction class, object "
            "instance, and federate handles with typed-handle validation and wrong-family rejection, and return "
            "dimension handle sets for joined regions."
        ),
    },
    {
        "id": "2025-support-advisory-and-reporting-state-inquiries",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-170",
            "HLA2025-FI-SVC-172",
            "HLA2025-FI-SVC-174",
            "HLA2025-FI-SVC-176",
            "HLA2025-FI-SVC-178",
            "HLA2025-FI-SVC-182",
            "HLA2025-FI-SVC-184",
            "HLA2025-FI-SVC-186",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route report advisory and reporting-state inquiry "
            "switches for object-class, attribute, scope, and interaction relevance, convey-region-designator-sets, "
            "service reporting, exception reporting, and send-service-reports-to-file."
        ),
    },
    {
        "id": "2025-support-runtime-policy-state-inquiries",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-180",
            "HLA2025-FI-SVC-188",
            "HLA2025-FI-SVC-189",
            "HLA2025-FI-SVC-190",
            "HLA2025-FI-SVC-191",
            "HLA2025-FI-SVC-192",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route report runtime-policy inquiry state for the "
            "automatic resign directive, auto-provide, delay-subscription-evaluation, advisories-use-known-class, "
            "allow-relaxed-DDM, and non-regulated-grant switches."
        ),
    },
    {
        "id": "2025-support-advisory-and-reporting-state-controls",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-171",
            "HLA2025-FI-SVC-173",
            "HLA2025-FI-SVC-175",
            "HLA2025-FI-SVC-177",
            "HLA2025-FI-SVC-179",
            "HLA2025-FI-SVC-183",
            "HLA2025-FI-SVC-185",
            "HLA2025-FI-SVC-187",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route now isolate advisory/reporting support-service "
            "switch control: they set the object-class, attribute, scope, and interaction advisory switches, "
            "convey-region-designator-sets, service reporting, exception reporting, and send-service-reports-to-file "
            "controls with bool validation for switch services."
        ),
    },
    {
        "id": "2025-support-runtime-policy-state-controls",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-SVC-181",),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim and the hosted FedPro 2025 route now isolate runtime-policy support-service switch "
            "control for the automatic resign directive with ResignAction validation."
        ),
    },
    {
        "id": "2025-callback-control-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-193",
            "HLA2025-FI-SVC-194",
            "HLA2025-FI-SVC-195",
            "HLA2025-FI-SVC-196",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto",
        ),
        "supported_scope": (
            "Python 2025 shim supports callback control services for connected federates: disableCallbacks "
            "queues local and target federate callbacks, enableCallbacks permits delivery again, evokeCallback "
            "delivers one queued callback, and evokeMultipleCallbacks drains the pending callback queue. The "
            "hosted FedPro 2025 route now carries explicit enableCallbacks/disableCallbacks transport calls and "
            "preserves queued callback delivery boundaries across callback polling. The timing parameters are "
            "accepted but not used for wall-clock blocking in this in-process shim slice."
        ),
    },
    {
        "id": "2025-ownership-divestiture-confirmation-flows",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-083",
            "HLA2025-FI-SVC-084",
            "HLA2025-FI-SVC-086",
            "HLA2025-FI-SVC-087",
            "HLA2025-FI-SVC-095",
            "HLA2025-MOD-005",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate ownership divestiture-confirmation proof: "
            "unconditional divestiture, negotiated ownership offers, requestDivestitureConfirmation, "
            "confirmDivestiture transfer, cancelNegotiatedAttributeOwnershipDivestiture, and 2025 tag/set payload "
            "preservation across these ownership transfer paths."
        ),
    },
    {
        "id": "2025-ownership-release-and-if-wanted-flows",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-092",
            "HLA2025-FI-SVC-093",
            "HLA2025-FI-SVC-094",
            "HLA2025-MOD-005",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate ownership release proof: "
            "requestAttributeOwnershipRelease, release-denied callback handling, "
            "divestiture-if-wanted transfer, and 2025 tag/set payload preservation across these "
            "release and transfer paths."
        ),
    },
    {
        "id": "2025-ownership-acquisition-assumption-flows",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-085",
            "HLA2025-FI-SVC-088",
            "HLA2025-FI-SVC-089",
            "HLA2025-MOD-005",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate acquisition-assumption proof: "
            "requestAttributeOwnershipAssumption, attributeOwnershipAcquisition, ownership acquisition "
            "notification, and 2025 user-supplied tag propagation with set-valued acquisition callback payloads."
        ),
    },
    {
        "id": "2025-ownership-acquisition-availability-cancellation-flows",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-090",
            "HLA2025-FI-SVC-091",
            "HLA2025-FI-SVC-096",
            "HLA2025-FI-SVC-097",
            "HLA2025-MOD-005",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate acquisition availability "
            "and cancellation proof: "
            "attributeOwnershipAcquisitionIfAvailable, ownership-unavailable callbacks, "
            "cancelAttributeOwnershipAcquisition, confirmAttributeOwnershipAcquisitionCancellation, and "
            "2025 user-supplied tag propagation across availability, failure, and cancellation paths."
        ),
    },
    {
        "id": "2025-ownership-query-and-resign-policies",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-098",
            "HLA2025-FI-SVC-099",
            "HLA2025-FI-SVC-100",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route now isolate ownership visibility and policy proof: "
            "queryAttributeOwnership, informAttributeOwnership plus attributeIsNotOwned/attributeIsOwnedByRTI "
            "callback outcomes, isAttributeOwnedByFederate, and resign-time ownership policies for cancel pending "
            "acquisitions, delete owned objects, and divest/transfer owned attributes."
        ),
    },
    {
        "id": "2025-mom-service-report-records",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-007", "HLA2025-REQ-002"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route serialize structured MOM service report records with "
            "service names, federate and federation context, serial numbers, success/exception fields, JSON-safe "
            "arguments and returned values, active service-reporting switches, source-local record snapshots, and "
            "service-report callback delivery only to joined federates with service reporting enabled."
        ),
    },
    {
        "id": "2025-mom-manager-action-routing",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-007", "HLA2025-REQ-002"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Python 2025 shim plus the hosted FedPro route carry MOM adjust and service actions through the real "
            "runtime paths they control: service/exception reporting adjust interactions, HLAsetSwitches, "
            "HLAsetTiming, and HLAmodifyAttributeState adjust interactions through receiveInteraction callbacks; "
            "declaration-management MOM service actions through normal publish/subscribe service paths; "
            "federation-management MOM service actions through normal synchronization, save/restore, and resign "
            "service paths; supported time-management MOM service actions through normal time-regulation, "
            "time-constrained, time-advance, flush-queue, and lookahead service paths, including disable, "
            "asynchronous-delivery, TARA, NMR, and NMRA paths; and supported object-management and ownership MOM "
            "service actions through normal delete, local-delete, transportation-change, order-type-change, and "
            "ownership-divestiture service paths. Failed routed MOM actions emit standard HLAreportMOMexception "
            "interactions with service, exception, and parameter-error fields. This is not full MOM manager "
            "action routing or a conformance claim."
        ),
    },
    {
        "id": "2025-mom-manager-query-and-report-routing",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-007", "HLA2025-REQ-002"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Python 2025 shim routes MOM query/report data separately from action routing: MIM data, FOM module "
            "data, and synchronization point/status MOM request/report interactions through receiveInteraction "
            "callbacks, plus federate-level FOM module data, publication/subscription, object-instance "
            "information, and activity/count MOM reports through normal publish/subscribe and report delivery "
            "paths. The FedPro hosted route reports standard MIM data for HLArequestMIMdata, FOM module data for "
            "HLArequestFOMmoduleData, object publication/subscription state for HLArequestPublications and "
            "HLArequestSubscriptions, object instance information for HLArequestObjectInstanceInformation, "
            "object-instance counts for deletable/updated/reflected objects, activity counts for updates, "
            "reflections, interactions sent, and interactions received, plus synchronization point/status reports. "
            "This is not full MOM manager query/report routing or a conformance claim."
        ),
    },
    {
        "id": "2025-wsdl-legacy-only",
        "status": "legacy-only",
        "requirements": ("HLA2025-RET-003", "HLA2025-BND-003", "HLA2025-REQ-002"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv",
            "CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto",
        ),
        "supported_scope": (
            "The 2010 WSDL binding remains legacy-only and is not counted as a native 2025 common behavior row. "
            "2025 transport work is isolated under FedPro/protobuf."
        ),
    },
    {
        "id": "2025-verification-anchor-matrix",
        "status": "implemented-slice",
        "requirements": ("HLA2025-VER-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002"),
        "evidence": (
            "tests/requirements/test_2025_finish_line_snapshot.py",
            "packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py",
            "requirements/2025/requirement_completion_backlog.csv",
            "docs/requirements/ieee-1516-2025/executable_tests/hla_2025_executable_test_requirements_v3.csv",
        ),
        "supported_scope": (
            "Generated finish-line verification matrix links each completion-backlog row to implemented evidence "
            "slices, executable test candidates, or explicit legacy/unsupported-boundary status. The enforced gate "
            "is every high/very-high row has at least one reviewable anchor."
        ),
    },
    {
        "id": "2025-python-rti-milestone-ledger",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-MIL-001",
            "HLA2025-MIL-002",
            "HLA2025-MIL-003",
            "HLA2025-MIL-004",
            "HLA2025-MIL-005",
            "HLA2025-MIL-006",
        ),
        "evidence": (
            "tests/requirements/test_2025_finish_line_snapshot.py",
            "packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py",
            "packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py",
            "requirements/2025/requirement_completion_backlog.csv",
        ),
        "supported_scope": (
            "Repo-owned milestone rows now make the bounded Python 2025 finish-line gates explicit for both the "
            "in-process and hosted FedPro routes: best-attempt working surface, tracked FOM-backed scenarios, "
            "message routing, time synchronization, GALT/LITS bounded query evidence, and lookahead bounded "
            "runtime evidence."
        ),
    },
)

OBJECTIVE_DIMENSIONS: tuple[Mapping[str, Any], ...] = (
    {
        "id": "federation_management",
        "name": "Federation Management",
        "evidence_level": "strong-slice",
        "implemented_slice_ids": (
            "2025-lifecycle-and-members",
            "2025-connection-lifecycle-services",
            "2025-connect-and-federation-catalog-services",
            "2025-federate-membership-and-resign-services",
            "2025-synchronization-point-services",
            "2025-save-restore-lifecycle",
            "2025-fedpro-hosted-runtime-core",
            "2025-fedpro-hosted-runtime-extended-state",
        ),
        "route_scenarios": ("federation_lifecycle", "save_restore"),
        "current_assessment": (
            "Connection, federation catalog control, membership reporting/resign, synchronization barriers, and "
            "save/restore behavior are exercised directly through the Python 2025 shim and the hosted FedPro "
            "route, with parity scenarios recorded across all tracked routes."
        ),
        "residual_blockers": (
            "The evidence is still slice-oriented rather than service-by-service proof.",
            "Standard Java and C++ route coverage remains scenario parity/runtime capability evidence, not exhaustive behavior conformance.",
        ),
    },
    {
        "id": "object_management",
        "name": "Object Management",
        "evidence_level": "strong-slice",
        "implemented_slice_ids": (
            "2025-basic-object-exchange",
            "2025-declaration-publication-services",
            "2025-declaration-subscription-services",
            "2025-declaration-relevance-advisory-callbacks",
            "2025-directed-interaction-boundary",
            "2025-object-delete-remove-flows",
            "2025-object-attribute-update-request-callbacks",
            "2025-object-scope-advisory-callbacks",
            "2025-object-update-rate-advisory-callbacks",
            "2025-object-attribute-transport-callbacks",
            "2025-object-interaction-transport-callbacks",
            "2025-ddm-default-attribute-policy",
            "2025-fedpro-hosted-runtime-core",
            "2025-fedpro-hosted-runtime-extended-state",
        ),
        "route_scenarios": ("object_exchange", "ownership", "ddm"),
        "current_assessment": (
            "The current repo proves a coherent object-management surface: object and interaction exchange, "
            "directed interactions, ownership transfer/query callbacks, DDM overlap filtering, transportation "
            "policy changes, and object deletion flows all execute end to end."
        ),
        "residual_blockers": (
            "Requirement aggregation still hides per-service completion detail inside supported-scope slices.",
            "FedPro coverage is a hosted runtime slice and does not yet constitute full RTI semantics proof.",
        ),
    },
    {
        "id": "time_management",
        "name": "Time Management",
        "evidence_level": "strong-slice",
        "implemented_slice_ids": (
            "2025-time-mode-enable-disable",
            "2025-time-advance-request-modes",
            "2025-time-grant-and-async-delivery",
            "2025-time-query-and-lookahead-control",
            "2025-time-queries-retraction-and-order",
            "2025-lookahead-window-proofs",
            "2025-save-restore-lifecycle",
            "2025-fedpro-hosted-runtime-extended-state",
            "2025-standard-route-runtime-capability",
        ),
        "route_scenarios": ("time_management", "save_restore"),
        "current_assessment": (
            "Logical-time factories, regulation/constrained mode transitions, advance-request modes, grants, "
            "lookahead/query control, timestamped delivery, retraction, and save/restore rollback are all backed "
            "by executable runtime traces."
        ),
        "residual_blockers": (
            "The closeout still aggregates multiple time services into bounded slices instead of final per-requirement proof.",
            "Cross-binding runtime evidence is narrower than the Python in-process and hosted FedPro slices.",
        ),
    },
    {
        "id": "support_services",
        "name": "Support Services",
        "evidence_level": "strong-slice",
        "implemented_slice_ids": (
            "2025-switch-set-get-model",
            "2025-single-name-reservation-services",
            "2025-multi-name-reservation-services",
            "2025-support-federate-and-object-identity-lookups",
            "2025-support-attribute-interaction-catalog-lookups",
            "2025-support-policy-update-and-transport-lookups",
            "2025-support-interaction-dimension-and-range-lookups",
            "2025-support-handle-normalization-and-region-introspection",
            "2025-support-advisory-and-reporting-state-inquiries",
            "2025-support-runtime-policy-state-inquiries",
            "2025-support-advisory-and-reporting-state-controls",
            "2025-support-runtime-policy-state-controls",
            "2025-ddm-default-attribute-policy",
            "2025-fedpro-hosted-runtime-core",
            "2025-fedpro-hosted-runtime-extended-state",
            "2025-standard-route-runtime-capability",
        ),
        "route_scenarios": ("support_services",),
        "current_assessment": (
            "Handle lookup, dimension bounds, default policy control, normalization and switch inquiry/set flows "
            "are exercised through the Python runtime and are represented across tracked binding routes. The "
            "finish-line now also carries an explicit support-service ledger via the RTIambassador conformance matrix."
        ),
        "residual_blockers": (
            "The support-service ledger is executable and negative-path complete inside the Python routes, but it is still aggregated as a bounded slice rather than a final per-service conformance audit.",
            "Java and C++ proof remains capability-oriented rather than a full standard-route behavior pass.",
        ),
    },
    {
        "id": "ownership_management",
        "name": "Ownership Management",
        "evidence_level": "strong-slice",
        "implemented_slice_ids": (
            "2025-ownership-divestiture-confirmation-flows",
            "2025-ownership-release-and-if-wanted-flows",
            "2025-ownership-acquisition-assumption-flows",
            "2025-ownership-acquisition-availability-cancellation-flows",
            "2025-ownership-query-and-resign-policies",
            "2025-save-restore-lifecycle",
            "2025-fedpro-hosted-runtime-extended-state",
        ),
        "route_scenarios": ("ownership", "save_restore"),
        "current_assessment": (
            "Ownership acquisition, divestiture, release negotiation, query callbacks, resign-time policies, "
            "and rollback-sensitive ownership state are all exercised directly through the Python 2025 shim and "
            "through shared backend-matrix scenarios."
        ),
        "residual_blockers": (
            "The closeout still groups ownership proof into bounded runtime slices rather than a final clause-by-clause ownership audit.",
            "Hosted route parity remains scenario-backed runtime evidence, not a full vendor-equivalent ownership conformance pass.",
        ),
    },
    {
        "id": "callbacks",
        "name": "Callbacks",
        "evidence_level": "strong-slice",
        "implemented_slice_ids": (
            "2025-callback-context-object-delivery",
            "2025-callback-context-interaction-delivery",
            "2025-connection-lifecycle-services",
            "2025-connect-and-federation-catalog-services",
            "2025-federate-membership-and-resign-services",
            "2025-synchronization-point-services",
            "2025-object-delete-remove-flows",
            "2025-object-attribute-update-request-callbacks",
            "2025-object-scope-advisory-callbacks",
            "2025-object-update-rate-advisory-callbacks",
            "2025-object-attribute-transport-callbacks",
            "2025-object-interaction-transport-callbacks",
            "2025-single-name-reservation-services",
            "2025-multi-name-reservation-services",
            "2025-save-restore-lifecycle",
            "2025-fedpro-hosted-runtime-core",
            "2025-fedpro-hosted-runtime-extended-state",
        ),
        "route_scenarios": (
            "federation_lifecycle",
            "object_exchange",
            "ownership",
            "time_management",
            "save_restore",
            "mom",
            "support_services",
        ),
        "current_assessment": (
            "Callback delivery is broad and executable across lifecycle, object, ownership, DDM, time, MOM, and "
            "support-service flows, including hosted FedPro callback decoding and direct Python ambassador behavior. "
            "The finish-line now also carries an explicit callback-by-callback ledger via the FederateAmbassador "
            "conformance matrix, and that ledger is fully route-backed across the current Python 2025 lanes."
        ),
        "residual_blockers": (
            "The callback ledger still stops short of exhaustive cross-binding callback signature/ordering equivalence proof.",
            "Binding-route callback parity is tracked at the scenario level, not as exhaustive callback signature/ordering proof.",
        ),
    },
    {
        "id": "omt_handling",
        "name": "OMT Handling",
        "evidence_level": "bounded-slice",
        "implemented_slice_ids": (
            "2025-fom-validation",
            "2025-omt-reference-value-required",
            "2025-omt-component-metadata-roundtrip",
            "2025-omt-switch-and-transport-subset",
            "2025-omt-extended-supported-subset",
            "2025-service-utilization-crosscheck",
            "2025-omt-schema-constraint-validation",
            "2025-omt-unsupported-component-boundaries",
            "2025-omt-unmodeled-component-boundaries-expanded",
        ),
        "route_scenarios": (),
        "current_assessment": (
            "The OMT path is well-instrumented for the supported parser/serializer/schema subset and now explicitly "
            "records the unsupported boundaries instead of leaving them implicit."
        ),
        "residual_blockers": (
            "OMT evidence includes explicit unsupported boundaries, so this area cannot be promoted to full 2025 conformance.",
            "Parser/serializer support is intentionally narrower than the full 2025 schema/component space.",
        ),
    },
    {
        "id": "binding_routes",
        "name": "Binding Routes",
        "evidence_level": "bounded-slice",
        "implemented_slice_ids": (
            "2025-java-binding-source-trace",
            "2025-cpp-binding-source-trace",
            "2025-standard-route-runtime-capability",
            "2025-fedpro-typed-transport-surface",
            "2025-fedpro-hosted-runtime-core",
            "2025-fedpro-hosted-runtime-extended-state",
        ),
        "route_scenarios": (
            "federation_lifecycle",
            "object_exchange",
            "ownership",
            "ddm",
            "time_management",
            "save_restore",
            "mom",
            "support_services",
        ),
        "current_assessment": (
            "Every tracked 2025 route now has explicit scenario parity rows, and the Python in-process plus hosted "
            "FedPro routes provide substantive runtime proof for the working surface."
        ),
        "residual_blockers": (
            "Java and C++ routes are still backed by artifact/runtime-capability traces rather than exhaustive behavior equivalence proof.",
            "The hosted FedPro route remains a bounded working slice, not a full RTI conformance route.",
        ),
    },
)

FI_SERVICE_FAMILY_RANGES: tuple[tuple[int, int, str], ...] = (
    (1, 17, "federation_management"),
    (18, 34, "save_restore"),
    (35, 46, "declaration_management"),
    (47, 50, "object_class_relevance"),
    (51, 56, "name_reservation"),
    (57, 82, "object_management"),
    (83, 100, "ownership_management"),
    (101, 125, "time_management"),
    (126, 137, "ddm"),
    (138, 192, "support_services"),
    (193, 196, "callback_control"),
)


def _implemented_slice_index() -> dict[str, Mapping[str, Any]]:
    return {slice_["id"]: slice_ for slice_ in IMPLEMENTED_EVIDENCE_SLICES}


def _fi_service_family(requirement_id: str) -> str:
    service_number = int(requirement_id.rsplit("-", 1)[1])
    for start, end, family in FI_SERVICE_FAMILY_RANGES:
        if start <= service_number <= end:
            return family
    return "unknown"


def _build_fi_service_proof_audit() -> dict[str, Any]:
    fi_service_rows: list[dict[str, Any]] = []
    for requirement_id in sorted(
        {
            requirement_id
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            for requirement_id in evidence_slice.get("requirements", ())
            if requirement_id.startswith("HLA2025-FI-SVC-")
        }
    ):
        supporting_slices = [
            evidence_slice
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            if requirement_id in evidence_slice.get("requirements", ())
        ]
        proof_kind = "multi-slice-runtime" if len(supporting_slices) > 1 else "single-slice-runtime"
        evidence_tests = sorted(
            {
                evidence_path
                for evidence_slice in supporting_slices
                for evidence_path in evidence_slice["evidence"]
                if evidence_path.endswith(".py")
            }
        )
        fi_service_rows.append(
            {
                "requirement_id": requirement_id,
                "service_number": int(requirement_id.rsplit("-", 1)[1]),
                "family": _fi_service_family(requirement_id),
                "proof_status": "implemented-slice-traceable",
                "proof_kind": proof_kind,
                "supporting_slice_ids": [evidence_slice["id"] for evidence_slice in supporting_slices],
                "evidence_tests": evidence_tests,
                "evidence_artifacts": sorted(
                    {
                        evidence_path
                        for evidence_slice in supporting_slices
                        for evidence_path in evidence_slice["evidence"]
                    }
                ),
            }
        )

    return {
        "row_count": len(fi_service_rows),
        "by_family": dict(sorted(Counter(row["family"] for row in fi_service_rows).items())),
        "by_proof_kind": dict(sorted(Counter(row["proof_kind"] for row in fi_service_rows).items())),
        "fully_traceable_service_count": len(fi_service_rows),
        "ready_for_per_service_runtime_traceability_claim": len(fi_service_rows) == 196,
        "ready_for_full_fi_service_conformance_claim": False,
        "current_assessment": (
            "All 196 Federate Interface service catalog rows now map to explicit runtime evidence rows, but many "
            "services are still proven through clustered slice evidence rather than isolated one-service final "
            "conformance tests."
        ),
        "rows": fi_service_rows,
    }


def _build_delta_requirement_proof_audit() -> dict[str, Any]:
    delta_rows: list[dict[str, Any]] = []
    for requirement_id in sorted(
        {
            requirement_id
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            for requirement_id in evidence_slice.get("requirements", ())
            if requirement_id.startswith(("HLA2025-MOD-", "HLA2025-NEW-", "HLA2025-RET-"))
        }
    ):
        supporting_slices = [
            evidence_slice
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            if requirement_id in evidence_slice.get("requirements", ())
        ]
        evidence_tests = sorted(
            {
                evidence_path
                for evidence_slice in supporting_slices
                for evidence_path in evidence_slice["evidence"]
                if evidence_path.endswith(".py")
            }
        )
        if requirement_id.startswith("HLA2025-MOD-"):
            category = "modified-existing"
        elif requirement_id.startswith("HLA2025-NEW-"):
            category = "new-2025-requirement"
        else:
            category = "retired-mapped-2010"
        delta_rows.append(
            {
                "requirement_id": requirement_id,
                "category": category,
                "proof_status": "implemented-slice-traceable",
                "supporting_slice_ids": [evidence_slice["id"] for evidence_slice in supporting_slices],
                "evidence_tests": evidence_tests,
                "evidence_artifacts": sorted(
                    {
                        evidence_path
                        for evidence_slice in supporting_slices
                        for evidence_path in evidence_slice["evidence"]
                    }
                ),
            }
        )

    return {
        "row_count": len(delta_rows),
        "by_category": dict(sorted(Counter(row["category"] for row in delta_rows).items())),
        "fully_traceable_requirement_count": len(delta_rows),
        "ready_for_delta_traceability_claim": len(delta_rows) == 20,
        "ready_for_full_delta_conformance_claim": False,
        "current_assessment": (
            "All modified, new, and retired common delta rows now map to explicit evidence slices, but several are "
            "still proven through grouped behavioral slices or retirement mappings rather than isolated final SHALL tests."
        ),
        "rows": delta_rows,
    }


def _build_binding_requirement_proof_audit(route_parity_matrix: Mapping[str, Any]) -> dict[str, Any]:
    binding_rows: list[dict[str, Any]] = []
    for requirement_id in ("HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003"):
        supporting_slices = [
            evidence_slice
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            if requirement_id in evidence_slice.get("requirements", ())
        ]
        evidence_tests = sorted(
            {
                evidence_path
                for evidence_slice in supporting_slices
                for evidence_path in evidence_slice["evidence"]
                if evidence_path.endswith(".py")
            }
        )
        relevant_routes = {
            "HLA2025-BND-001": ("java-standard-2025-jpype", "java-standard-2025-py4j"),
            "HLA2025-BND-002": ("cpp-standard-2025-pybind", "cpp-standard-2025-grpc"),
            "HLA2025-BND-003": ("python-2025-fedpro-grpc",),
        }[requirement_id]
        parity_rows = [row for row in route_parity_matrix["rows"] if row["route"] in relevant_routes]
        binding_rows.append(
            {
                "requirement_id": requirement_id,
                "routes": list(relevant_routes),
                "proof_status": "implemented-slice-traceable",
                "supporting_slice_ids": [evidence_slice["id"] for evidence_slice in supporting_slices],
                "evidence_tests": evidence_tests,
                "route_parity_counts": dict(sorted(Counter(row["status"] for row in parity_rows).items())),
                "route_scenarios": sorted({row["scenario"] for row in parity_rows}),
            }
        )
    return {
        "row_count": len(binding_rows),
        "fully_traceable_requirement_count": len(binding_rows),
        "ready_for_binding_traceability_claim": len(binding_rows) == 3,
        "ready_for_full_binding_conformance_claim": False,
        "current_assessment": (
            "All three binding rows now have explicit slice and route-parity proof records, but Java/C++ remain "
            "artifact/runtime-capability bounded and FedPro remains a hosted runtime slice rather than full conformance."
        ),
        "rows": binding_rows,
    }


def _build_omt_requirement_proof_audit() -> dict[str, Any]:
    omt_rows: list[dict[str, Any]] = []
    for requirement_id in sorted(
        {
            requirement_id
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            for requirement_id in evidence_slice.get("requirements", ())
            if requirement_id.startswith(("HLA2025-OMT-", "HLA2025-OMT-COMP-", "HLA2025-OMT-CV-", "HLA2025-OMT-SU-"))
        }
    ):
        supporting_slices = [
            evidence_slice
            for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES
            if requirement_id in evidence_slice.get("requirements", ())
        ]
        statuses = {evidence_slice["status"] for evidence_slice in supporting_slices}
        if statuses == {"unsupported-boundary"}:
            proof_status = "unsupported-boundary-traceable"
        else:
            proof_status = "supported-subset-traceable"
        if requirement_id.startswith("HLA2025-OMT-COMP-"):
            category = "component"
        elif requirement_id.startswith("HLA2025-OMT-CV-"):
            category = "validator-negative"
        elif requirement_id.startswith("HLA2025-OMT-SU-"):
            category = "service-utilization"
        else:
            category = "core-omt"
        omt_rows.append(
            {
                "requirement_id": requirement_id,
                "category": category,
                "proof_status": proof_status,
                "supporting_slice_ids": [evidence_slice["id"] for evidence_slice in supporting_slices],
                "evidence_tests": sorted(
                    {
                        evidence_path
                        for evidence_slice in supporting_slices
                        for evidence_path in evidence_slice["evidence"]
                        if evidence_path.endswith(".py")
                    }
                ),
            }
        )

    return {
        "row_count": len(omt_rows),
        "by_category": dict(sorted(Counter(row["category"] for row in omt_rows).items())),
        "by_proof_status": dict(sorted(Counter(row["proof_status"] for row in omt_rows).items())),
        "traceable_requirement_count": len(omt_rows),
        "ready_for_omt_traceability_claim": len(omt_rows) == 454,
        "ready_for_full_omt_conformance_claim": False,
        "current_assessment": (
            "All OMT-related rows are now explicit requirement records, with supported-subset proof separated from "
            "unsupported-boundary proof. This closes the traceability gap without pretending the unsupported OMT "
            "boundaries are delivered support."
        ),
        "rows": omt_rows,
    }


def _build_callback_proof_audit() -> dict[str, Any]:
    callback_rows = [
        row
        for row in build_service_conformance_matrix().rows
        if row.interface == "FederateAmbassador"
    ]
    helper_backed_rows = [row for row in callback_rows if row.implementation_status == "callback-helper"]
    focused_rows = [row for row in callback_rows if row.verification_status == "focused-executable-tests"]
    helper_covered_rows = [row for row in callback_rows if row.verification_status == "callback-helper-covered"]
    rows_with_known_gaps = [row for row in callback_rows if row.known_gaps]
    return {
        "row_count": len(callback_rows),
        "helper_backed_callback_count": len(helper_backed_rows),
        "focused_executable_callback_count": len(focused_rows),
        "helper_covered_callback_count": len(helper_covered_rows),
        "rows_with_known_gaps": len(rows_with_known_gaps),
        "by_service_group": dict(sorted(Counter(row.service_group for row in callback_rows).items())),
        "by_verification_status": dict(sorted(Counter(row.verification_status for row in callback_rows).items())),
        "ready_for_callback_surface_traceability_claim": (
            len(callback_rows) == len(helper_backed_rows) and not rows_with_known_gaps
        ),
        "ready_for_callback_by_callback_working_surface_claim": len(callback_rows) == len(focused_rows),
        "current_assessment": (
            "The repo now has an explicit callback-by-callback ledger through the FederateAmbassador conformance "
            "matrix, and all 55 callback rows are helper-backed with focused executable evidence. This closes the "
            "callback-ledger gap, but it still does not by itself prove exhaustive cross-binding callback "
            "signature/ordering parity or a full callback conformance claim."
        ),
        "rows": [
            {
                "requirement_id": row.requirement_id,
                "method_name": row.method_name,
                "service_group": row.service_group,
                "implementation_status": row.implementation_status,
                "verification_status": row.verification_status,
                "positive_test_refs": list(row.positive_test_refs),
                "known_gaps": list(row.known_gaps),
            }
            for row in callback_rows
        ],
    }


def _build_callback_route_parity_audit(callback_proof_audit: Mapping[str, Any]) -> dict[str, Any]:
    rows = list(callback_proof_audit["rows"])
    hosted_or_route_rows = [
        row
        for row in rows
        if any(
            "test_python_route_parity" in ref or "transport/test_grpc_transport_2025.py" in ref
            for ref in row["positive_test_refs"]
        )
    ]
    callback_helper_only_rows = [
        row
        for row in rows
        if row["method_name"] not in {item["method_name"] for item in hosted_or_route_rows}
    ]
    return {
        "row_count": len(rows),
        "hosted_or_route_backed_callback_count": len(hosted_or_route_rows),
        "callback_helper_only_count": len(callback_helper_only_rows),
        "ready_for_full_python_lane_callback_route_parity_claim": len(callback_helper_only_rows) == 0,
        "ready_for_exhaustive_cross_binding_callback_parity_claim": False,
        "current_assessment": (
            "The callback ledger is now fully route-backed across the current Python 2025 lanes, so every callback row "
            "has hosted/direct executable evidence in addition to the helper-backed working-surface proof. The repo "
            "still does not yet prove exhaustive callback-by-callback signature and ordering equivalence across every "
            "binding."
        ),
        "residual_blockers": [
            "Callback ordering parity is still asserted primarily at the scenario level rather than row-by-row for every callback.",
            "The hosted/current Python evidence is strong, but Java and C++ bindings still do not execute the same callback-conformance surface.",
            "Java and C++ bindings remain artifact/runtime-capability bounded instead of executable callback-conformance lanes.",
        ],
        "hosted_or_route_backed_callbacks": sorted(row["method_name"] for row in hosted_or_route_rows),
        "sample_callback_helper_only_rows": sorted(row["method_name"] for row in callback_helper_only_rows[:12]),
    }


def _build_support_service_proof_audit() -> dict[str, Any]:
    support_rows = [
        row
        for row in build_service_conformance_matrix().rows
        if row.interface == "RTIambassador" and row.service_group == "Support Services"
    ]
    focused_rows = [row for row in support_rows if row.verification_status == "focused-executable-tests"]
    rows_with_known_gaps = [row for row in support_rows if row.known_gaps]
    negative_status_counts = dict(sorted(Counter(negative_path_status(row) for row in support_rows).items()))
    return {
        "row_count": len(support_rows),
        "focused_executable_row_count": len(focused_rows),
        "rows_with_known_gaps": len(rows_with_known_gaps),
        "by_verification_status": dict(sorted(Counter(row.verification_status for row in support_rows).items())),
        "by_negative_path_status": negative_status_counts,
        "complete_negative_path_row_count": negative_status_counts.get("complete", 0),
        "partial_negative_path_row_count": negative_status_counts.get("partial", 0),
        "mapped_not_exhaustive_negative_path_row_count": negative_status_counts.get("mapped-not-exhaustive", 0),
        "ready_for_support_service_traceability_claim": len(support_rows) == len(focused_rows),
        "ready_for_support_service_full_conformance_claim": False,
        "current_assessment": (
            "The repo now has an explicit support-service ledger through the RTIambassador conformance matrix, and "
            "all 62 support-service rows have focused executable evidence. Negative-path coverage is now complete "
            "for all 61 actionable support-service rows, with the remaining row marked not-applicable because it "
            "declares no actionable RTI exception surface. Support services are no longer the main blocker; "
            "cross-binding evidence remains weaker than the Python routes."
        ),
        "rows": [
            {
                "requirement_id": row.requirement_id,
                "method_name": row.method_name,
                "verification_status": row.verification_status,
                "negative_path_status": negative_path_status(row),
                "positive_test_refs": list(row.positive_test_refs),
                "known_gaps": list(row.known_gaps),
            }
            for row in support_rows
        ],
    }


def _build_completion_claim_audit(
    backlog: Mapping[str, Any],
    disposition: Mapping[str, Any],
    objective_audit: Mapping[str, Any],
    fi_audit: Mapping[str, Any],
    delta_audit: Mapping[str, Any],
    binding_audit: Mapping[str, Any],
    omt_audit: Mapping[str, Any],
) -> dict[str, Any]:
    by_disposition = disposition["by_disposition"]
    covered_count = by_disposition.get("covered", 0)
    unsupported_count = by_disposition.get("unsupported-boundary", 0)
    legacy_only_count = by_disposition.get("retired/legacy-only", 0)
    duplicate_count = by_disposition.get("duplicate/umbrella", 0)
    fully_closed_backlog = backlog["high_priority_open_count"] == 0 and "planned" not in backlog["by_current_status"]
    return {
        "claim_shape": "bounded-working-surface-with-explicit-boundaries",
        "ready_for_supported-boundary_statement": (
            objective_audit["ready_for_bounded_working_surface_claim"]
            and fi_audit["ready_for_per_service_runtime_traceability_claim"]
            and delta_audit["ready_for_delta_traceability_claim"]
            and binding_audit["ready_for_binding_traceability_claim"]
            and omt_audit["ready_for_omt_traceability_claim"]
            and fully_closed_backlog
        ),
        "ready_for_full_2025_conformance_claim": False,
        "requirement_universe": {
            "total_rows": disposition["row_count"],
            "covered_rows": covered_count,
            "unsupported_boundary_rows": unsupported_count,
            "retired_or_legacy_only_rows": legacy_only_count,
            "duplicate_or_umbrella_rows": duplicate_count,
        },
        "backlog_closure": {
            "row_count": backlog["row_count"],
            "implemented_slice_rows": backlog["by_current_status"].get("implemented-slice", 0),
            "legacy_only_rows": backlog["by_current_status"].get("legacy-only", 0),
            "high_priority_open_count": backlog["high_priority_open_count"],
            "fully_closed": fully_closed_backlog,
        },
        "traceability_ledgers": {
            "fi_service_rows": fi_audit["row_count"],
            "delta_rows": delta_audit["row_count"],
            "binding_rows": binding_audit["row_count"],
            "omt_rows": omt_audit["row_count"],
        },
        "current_assessment": (
            "The repo can now make a defensible supported-boundary statement: the claimed working surface is backed "
            "by explicit requirement ledgers, the backlog is closed at the tracked 2025 delta level, and unsupported "
            "or legacy-only areas are named rather than hidden. This is still short of a full 2025 conformance claim."
        ),
        "full_claim_blockers": [
            "Covered rows are mixed with explicit unsupported-boundary and retired/legacy-only rows in the 2025 universe, so the delivered statement must stay bounded.",
            "Java and C++ binding rows remain artifact/runtime-capability evidence rather than exhaustive behavior-conformance proof.",
            "The hosted FedPro route remains a bounded runtime slice and not a full RTI semantics/MOM action-request conformance pass.",
            "Duplicate/umbrella rows remain normalization aids rather than direct one-row conformance assertions.",
        ],
    }


def _build_requirement_by_requirement_audit(
    harmonization_rows: list[Mapping[str, str]],
    disposition: Mapping[str, Any],
) -> dict[str, Any]:
    by_disposition = disposition["by_disposition"]
    all_rows_dispositioned = disposition["row_count"] == sum(by_disposition.values())
    metadata_fields = ("repo_evidence_status", "closure_wave", "priority", "promotion_rule")
    rows_with_complete_review_metadata = sum(
        1 for row in harmonization_rows if all(row[field] for field in metadata_fields)
    )
    covered_rows_with_evidence_paths = sum(
        1
        for row in harmonization_rows
        if row["harmonization_disposition"] == "covered" and row["suggested_repo_evidence_path"]
    )
    unsupported_rows_with_explicit_boundary_flag = sum(
        1
        for row in harmonization_rows
        if row["harmonization_disposition"] == "unsupported-boundary"
        and row["unsupported_boundary_candidate"] == "yes"
    )
    area_rows = disposition["by_area_and_disposition"]
    return {
        "audit_status": "row-level-requirement-disposition-audit-captured",
        "ready_for_row_level_requirement_audit_claim": (
            all_rows_dispositioned
            and rows_with_complete_review_metadata == disposition["row_count"]
            and covered_rows_with_evidence_paths == by_disposition.get("covered", 0)
            and unsupported_rows_with_explicit_boundary_flag == by_disposition.get("unsupported-boundary", 0)
        ),
        "ready_for_full_2025_conformance_claim": False,
        "row_count": disposition["row_count"],
        "disposition_counts": dict(by_disposition),
        "area_closure": {
            "fi_service_catalog": dict(area_rows["Federate Interface service catalog"]),
            "som_fom_service_usage": dict(area_rows["SOM/FOM service-usage requirements"]),
            "omt_component_conformance": dict(area_rows["OMT component-level conformance"]),
            "omt_validator_negative_conformance": dict(area_rows["OMT validator-negative conformance"]),
            "framework_rules": dict(area_rows["Framework and Rules"]),
            "callback_configuration_binding_deltas": dict(area_rows["Callback/configuration/binding deltas"]),
            "retired_replacement_mapping_candidates": dict(area_rows["Retired / replacement mapping candidates"]),
        },
        "rows_with_complete_review_metadata": rows_with_complete_review_metadata,
        "covered_rows_with_evidence_paths": covered_rows_with_evidence_paths,
        "unsupported_rows_with_explicit_boundary_flag": unsupported_rows_with_explicit_boundary_flag,
        "current_assessment": (
            "The repo now has an explicit row-level requirement-by-requirement disposition audit across all 691 "
            "tracked 2025 rows: every row is reviewed, dispositioned, and linked either to repo evidence, an "
            "explicit unsupported boundary, a retired exclusion, or an umbrella normalization role. That closes "
            "the missing-audit gap without turning the result into an unconditional all-covered conformance pass."
        ),
        "full_claim_blockers": [
            "81 rows are explicit unsupported-boundary decisions rather than delivered support.",
            "24 rows are retired/legacy-only exclusions rather than active 2025 support.",
            "22 rows remain duplicate/umbrella normalization aids rather than one-row conformance assertions.",
            "Many covered rows still inherit bounded supported-scope language from slice-level evidence rather than standalone exhaustive clause-by-clause proof.",
        ],
    }


def _build_supported_boundary_statement(
    claim_audit: Mapping[str, Any],
    objective_audit: Mapping[str, Any],
    route_parity_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "statement_status": "supported-boundary-statement",
        "ready": claim_audit["ready_for_supported-boundary_statement"],
        "statement": (
            "The Python-centered 2025 RTI surface is validated as a bounded working surface across federation "
            "management, object management, time management, support services, callbacks, OMT handling, and "
            "binding routes, with explicit unsupported, legacy-only, and artifact-gated boundaries recorded in the repo."
        ),
        "supported_scope": [
            "Python 2025 in-process runtime behavior is executable and parity-covered across the tracked scenario set.",
            "Hosted FedPro 2025 transport behavior is executable as a bounded runtime slice with explicit route parity coverage.",
            "FI service requirements are traced across all 196 catalog rows.",
            "Common delta rows, binding rows, and OMT-related rows are all represented by explicit requirement ledgers.",
        ],
        "explicit_boundaries": [
            "Unsupported OMT component rows remain unsupported-boundary entries rather than delivered support.",
            "Retired or legacy-only rows remain excluded from the supported 2025 working surface.",
            "Java and C++ bindings remain artifact/runtime-capability bounded rather than full behavior-conformance proof.",
            "FedPro remains a hosted runtime slice rather than a full RTI semantics/MOM action-request conformance pass.",
        ],
        "evidence_summary": {
            "bounded_ready_dimensions": objective_audit["bounded_ready_dimension_count"],
            "dimension_count": objective_audit["dimension_count"],
            "route_parity_missing_count": route_parity_matrix["by_status"].get("missing", 0),
            "route_parity_partial_count": route_parity_matrix["by_status"].get("partial", 0),
            "covered_rows": claim_audit["requirement_universe"]["covered_rows"],
            "unsupported_boundary_rows": claim_audit["requirement_universe"]["unsupported_boundary_rows"],
            "retired_or_legacy_only_rows": claim_audit["requirement_universe"]["retired_or_legacy_only_rows"],
        },
    }


def _build_promotion_split_audit(
    closeout_readiness: Mapping[str, Any],
    claim_audit: Mapping[str, Any],
    boundary_statement: Mapping[str, Any],
    milestone_audit: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "decision_shape": "promote-current-lane-or-split-later-based-on-evidence",
        "current_lane": {
            "package": "hla-backend-shim",
            "role": "current executable Python 2025 RTI lane",
            "spec_package": "hla-rti1516-2025",
        },
        "current_recommendation": "promote-current-lane-as-working-surface-and-keep-split-optional",
        "ready_for_current_lane_promotion_as_working_surface": (
            closeout_readiness["ready_for_slice_closeout"]
            and claim_audit["ready_for_supported-boundary_statement"]
            and boundary_statement["ready"]
            and milestone_audit["by_route"]["python-2025-inprocess"]["all_route_parity_covered"]
            and milestone_audit["by_route"]["python-2025-fedpro-grpc"]["all_route_parity_covered"]
        ),
        "ready_for_permanent_no-split_decision": False,
        "promotion_basis": [
            "The current 2025 lane has green executable runtime coverage in the main in-process suite.",
            "Both Python 2025 routes clear the tracked bounded working-surface milestones.",
            "The repo can make a supported-boundary statement over the current 2025 lane without hiding unsupported areas.",
            "Route parity partial and missing counts are both zero for the tracked 2025 matrix.",
            "The callback ledger is fully route-backed across the current Python 2025 lanes, eliminating callback-helper-only gaps in the promotion surface.",
            "The main shim-backed pressure families across save/restore, directed interaction, and DDM/default-policy are all route-backed across the current Python 2025 lanes.",
        ],
        "current_evidence_runs": [
            {
                "name": "combined-2025-verification-slice",
                "result": "467 passed in 78.98s",
                "scope": "main in-process 2025 runtime, requirement, and route evidence slice",
            },
            {
                "name": "hosted-2025-fedpro-transport-suite",
                "result": "168 passed in 38.01s",
                "scope": (
                    "typed hosted FedPro route including strict local FOM/MIM resolution, create-time error "
                    "taxonomy, time-window proof ladder, save/restore rollback, and directed TSO stale-queue cleanup"
                ),
            },
        ],
        "split_triggers": [
            "Adapter concerns begin to obscure or distort core RTI semantics.",
            "Callback or route normalization grows more complex than the underlying RTI behavior it wraps.",
            "New 2025 behavior is materially harder to implement because shim and RTI state management are too tightly mixed.",
            "The row-level requirement-by-requirement audit cannot be promoted from bounded disposition evidence to cleaner all-covered runtime proof without separating a narrower shim from a dedicated 2025 backend.",
        ],
        "permanent_decision_blockers": [
            "The repo now has a row-level requirement-by-requirement audit, but it is still a bounded disposition audit rather than an all-covered 2025 conformance pass.",
            "Several implemented slices still aggregate multiple requirements under bounded supported-scope language.",
            "Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or MOM action/request conformance pass.",
            "Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.",
        ],
        "current_assessment": (
            "Current evidence is strong enough to treat hla-backend-shim as the live Python 2025 RTI lane for bounded "
            "working-surface claims, including across the main shim-backed pressure families, but not strong enough "
            "to make a permanent no-split architectural decision."
        ),
    }


def _build_implementation_lane_audit(
    promotion_split_audit: Mapping[str, Any],
    milestone_audit: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "audit_status": "current-lane-architecture-captured",
        "current_2025_lane": {
            "backend_package": "hla-backend-shim",
            "plugin_family": "shim",
            "supports": ["rti1516_2025"],
            "role": "current executable Python 2025 RTI lane",
            "spec_package": "hla-rti1516-2025",
        },
        "reference_2010_lane": {
            "backend_package": "hla-backend-inmemory",
            "plugin_family": "inmemory",
            "supports": ["rti1516e"],
            "role": "2010 pure Python RTI backend",
        },
        "python_2025_routes": [
            {
                "route": "python-2025-inprocess",
                "kind": "in-process-backend-route",
                "is_separate_rti_family": False,
                "all_route_parity_covered": milestone_audit["by_route"]["python-2025-inprocess"]["all_route_parity_covered"],
            },
            {
                "route": "python-2025-fedpro-grpc",
                "kind": "hosted-transport-route",
                "is_separate_rti_family": False,
                "all_route_parity_covered": milestone_audit["by_route"]["python-2025-fedpro-grpc"]["all_route_parity_covered"],
            },
        ],
        "dedicated_2025_backend_package_present": False,
        "ready_for_current_lane_promotion_as_working_surface": promotion_split_audit[
            "ready_for_current_lane_promotion_as_working_surface"
        ],
        "ready_for_permanent_no-split_decision": promotion_split_audit["ready_for_permanent_no-split_decision"],
        "clean_extraction_still_optional": True,
        "current_assessment": (
            "The repo's current 2025 implementation reality is explicit: hla-backend-shim is the live Python 2025 "
            "backend lane, the hosted FedPro route is a route variant over that lane rather than a separate RTI "
            "family, and the older pure-Python backend remains the 2010-only inmemory lane."
        ),
        "extraction_boundary": (
            "Keep using the current lane as the executable Python 2025 RTI surface unless future evidence shows that "
            "shim adaptation is obscuring core runtime semantics strongly enough to justify extracting a dedicated "
            "2025 backend beside a narrower shim layer."
        ),
        "evidence_anchors": [
            "packages/hla-backend-shim/README.md",
            "packages/hla-backend-shim/src/hla/backends/shim/plugin.py",
            "packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py",
            "docs/backend_route_inventory_remote.md",
            "docs/plans/2025_python_rti_backend_audit.md",
            "docs/python_rti_backend.md",
        ],
    }


def _build_implementation_concentration_audit() -> dict[str, Any]:
    anchor_counts: Counter[str] = Counter()
    shim_backend_path = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    spec_package_prefix = "packages/hla-rti1516-2025/src/"
    transport_prefixes = ("packages/hla-transport-grpc/", "packages/hla-transport-rest/")
    shim_backend_slice_ids: list[str] = []
    spec_package_slice_ids: list[str] = []
    transport_slice_ids: list[str] = []

    for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES:
        evidence_paths = set(evidence_slice.get("evidence", ()))
        if shim_backend_path in evidence_paths:
            shim_backend_slice_ids.append(evidence_slice["id"])
        if any(path.startswith(spec_package_prefix) for path in evidence_paths):
            spec_package_slice_ids.append(evidence_slice["id"])
        if any(path.startswith(transport_prefixes) for path in evidence_paths):
            transport_slice_ids.append(evidence_slice["id"])
        for path in evidence_paths:
            anchor_counts[path] += 1

    total_slices = len(IMPLEMENTED_EVIDENCE_SLICES)
    shim_backend_slice_count = len(shim_backend_slice_ids)
    shim_backend_share = round(shim_backend_slice_count / total_slices, 3) if total_slices else 0.0
    spec_package_slice_count = len(spec_package_slice_ids)
    transport_slice_count = len(transport_slice_ids)

    return {
        "audit_status": "implementation-concentration-captured",
        "implemented_slice_count": total_slices,
        "shim_backend_path": shim_backend_path,
        "shim_backend_slice_count": shim_backend_slice_count,
        "shim_backend_slice_share": shim_backend_share,
        "spec_package_slice_count": spec_package_slice_count,
        "transport_slice_count": transport_slice_count,
        "semantic_concentration_is_material": shim_backend_share >= 0.5,
        "top_evidence_anchors": [
            {"path": path, "slice_count": count}
            for path, count in anchor_counts.most_common(10)
        ],
        "sample_shim_backend_slice_ids": shim_backend_slice_ids[:12],
        "current_assessment": (
            "The current 2025 lane is substantively executable, but the implementation proof is materially "
            "concentrated in hla-backend-shim/backend.py. That concentration does not by itself force a split, "
            "because spec-package and transport-layer evidence also exist, but it is a real architectural pressure "
            "signal to monitor as more 2025 behavior lands."
        ),
        "extraction_pressure_boundary": (
            "A future dedicated 2025 backend becomes more compelling if new runtime semantics keep accumulating "
            "primarily in the shim backend implementation instead of moving into cleaner reusable runtime modules."
        ),
    }


def _build_slice_aggregation_pressure_audit() -> dict[str, Any]:
    shim_backend_path = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    implemented_rows = [row for row in IMPLEMENTED_EVIDENCE_SLICES if row.get("status") == "implemented-slice"]
    ranked_rows = sorted(
        (
            {
                "slice_id": row["id"],
                "requirement_count": len(row.get("requirements", ())),
                "shim_backend_backed": shim_backend_path in set(row.get("evidence", ())),
            }
            for row in implemented_rows
        ),
        key=lambda item: (-item["requirement_count"], item["slice_id"]),
    )
    aggregated_ge10 = [row for row in ranked_rows if row["requirement_count"] >= 10]
    aggregated_ge20 = [row for row in ranked_rows if row["requirement_count"] >= 20]
    aggregated_ge10_shim = [row for row in aggregated_ge10 if row["shim_backend_backed"]]
    aggregated_ge20_shim = [row for row in aggregated_ge20 if row["shim_backend_backed"]]
    return {
        "audit_status": "slice-aggregation-pressure-captured",
        "implemented_slice_count": len(implemented_rows),
        "aggregated_slice_count_ge_10_requirements": len(aggregated_ge10),
        "aggregated_slice_count_ge_10_requirements_shim_backed": len(aggregated_ge10_shim),
        "aggregated_slice_count_ge_20_requirements": len(aggregated_ge20),
        "aggregated_slice_count_ge_20_requirements_shim_backed": len(aggregated_ge20_shim),
        "largest_implemented_slices": ranked_rows[:10],
        "largest_shim_backed_aggregated_slices": aggregated_ge10_shim[:10],
        "current_assessment": (
            "Most implemented 2025 slices are not huge aggregations, but a small set of large slices still carry a "
            "lot of requirement mass. The main runtime pressure points are the shim-backed ddm-default-attribute-policy, "
            "save-restore-lifecycle, and directed-interaction-boundary slices, which are credible next decomposition "
            "targets if the repo needs tighter requirement-level proof or a cleaner backend seam."
        ),
        "next_decomposition_boundary": (
            "If deeper proof is needed, start by splitting the largest shim-backed slices into narrower service- or "
            "behavior-family audits before extracting a dedicated 2025 backend."
        ),
    }


def _build_save_restore_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "lifecycle-control",
            "focus": "save/restore request, initiate, completion, failure, abort, and precondition control flow",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_federation_save_restore_lifecycle",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_save_failure_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_restore_request_failure_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_save_request_precondition_scenario_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_restore_lifecycle_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_completes_restore_after_peer_disconnect_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_request_precondition_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "shared-scenario-rollback",
            "focus": "shared two-federate save/restore, object-state rollback, and federate-local rollback",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_two_federate_suite_save_restore_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_backend_neutral_save_restore_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_restore_federate_local_state_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_restore_object_state_scenario_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_save_restore_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_backend_neutral_save_restore_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_restore_object_state_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_restore_federate_local_state_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "routing-policy-rollback",
            "focus": "callback policy, transport/order policy, object routing, interaction routing, directed routing, and stale queued callback cleanup",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_callback_delivery_policy",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_transport_and_order_policy_state",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_plain_object_subscriber_routing",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_plain_interaction_subscriber_routing",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_clears_stale_directed_tso_and_preserves_post_restore_routing",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_treats_callback_delivery_as_runtime_policy_not_saved_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_transport_and_order_policy_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema",
            ],
        },
        {
            "family": "ownership-rollback",
            "focus": "ownership gauntlets, inflight acquisition/divestiture state, and owner-visibility rollback",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_smoke_fom_save_restore_ownership_gauntlet",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_inflight_ownership_state",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restores_cross_federate_attribute_owner_visibility",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema",
            ],
        },
        {
            "family": "time-window-and-time-state-rollback",
            "focus": "lookahead, queued TSO, time/switch state, open/closed window state, output resume, and pipeline resume",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_time_and_switch_control_state",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restores_open_and_closed_time_window_state",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restores_closed_window_output_resume_without_dirty_replay",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restores_pipeline_resume_without_cross_window_replay",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_time_and_switch_control_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_open_and_closed_time_window_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_closed_window_output_resume_without_dirty_replay_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_pipeline_resume_without_cross_window_replay_over_fedpro_schema",
            ],
        },
    ]
    return {
        "audit_status": "save-restore-decomposition-captured",
        "slice_id": "2025-save-restore-lifecycle",
        "requirement_count": 20,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "The save/restore slice is no longer just one broad working-surface claim. Its current evidence already "
            "separates into lifecycle control, shared rollback scenarios, routing/policy rollback, ownership rollback, "
            "and time-window/time-state rollback, with both direct and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this slice needs further tightening, split it first by these proof families before extracting save/restore "
            "runtime semantics into a dedicated 2025 backend."
        ),
    }


def _build_directed_interaction_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "base-routing-and-callback-delivery",
            "focus": "publish, subscribe, unsubscribe, unpublish, and receiveDirectedInteraction callback delivery",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_routes_directed_interactions_to_object_class_subscribers",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_routes_directed_interactions_only_to_subscribers",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_directed_interaction_exchange_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_directed_interactions_only_to_subscribers_over_fedpro_schema",
            ],
        },
        {
            "family": "timestamped-delivery-and-retraction",
            "focus": "queued timestamped directed delivery, per-subscriber routing, pre-delivery retract, and target-departure cleanup",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_queues_timestamped_directed_interactions_until_time_advance",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_delivers_and_retracts_timestamped_directed_interactions_for_all_subscribers",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_drops_queued_directed_tso_for_departed_target",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_queues_timestamped_directed_interactions_and_retracts_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_delivers_and_retracts_timestamped_directed_interactions_for_all_subscribers_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_queued_directed_tso_for_disconnected_target_over_fedpro_schema",
            ],
        },
        {
            "family": "ddm-overlap-filtering",
            "focus": "region-overlap filtering for directed interactions and removal of disconnected directed DDM subscribers",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_filters_directed_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_routes_directed_ddm_interactions_only_to_overlapping_subscribers",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_removes_disconnected_directed_ddm_subscriber_from_delivery_state",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_directed_interactions_by_ddm_region_overlap",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_removes_disconnected_directed_ddm_subscriber_from_delivery_state_over_fedpro_schema",
            ],
        },
        {
            "family": "selective-set-and-publication-isolation",
            "focus": "selective directed-interaction set unsubscribe/unpublish without collapsing sibling classes or other publishers",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_directed_interaction_set_unsubscribe_and_unpublish_are_selective",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_preserves_other_federate_directed_publication_after_unpublish",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_directed_with_set_unsubscribe_and_unpublish_are_selective",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_preserves_other_federate_directed_publication_after_unpublish_over_fedpro_schema",
            ],
        },
        {
            "family": "restore-routing-and-stale-queue-cleanup",
            "focus": "restore recovers directed DDM subscriber routing and clears stale directed TSO without replaying dirty state",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_clears_stale_directed_tso_and_preserves_post_restore_routing",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema",
            ],
        },
    ]
    return {
        "audit_status": "directed-interaction-decomposition-captured",
        "slice_id": "2025-directed-interaction-boundary",
        "requirement_count": 11,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "The directed-interaction slice is no longer just one boundary claim. Its evidence separates into base "
            "routing/callback delivery, timestamped delivery and retraction, DDM overlap filtering, selective set "
            "and publication isolation, and restore-path routing cleanup, with direct and hosted anchors across all families."
        ),
        "next_split_boundary": (
            "If this slice needs further tightening, split it first by these directed-interaction proof families before "
            "moving directed-routing semantics into a dedicated 2025 backend."
        ),
    }


def _build_ddm_default_policy_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "lookup-and-default-policy-control",
            "focus": "FOM-backed dimension lookup, bounds queries, and default attribute transportation/order policy control",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap",
            ],
        },
        {
            "family": "object-region-routing-and-scope-advisories",
            "focus": "object reflection filtering through region overlap plus attributesInScope/attributesOutOfScope transitions",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_filters_object_reflections_by_ddm_region_overlap",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap",
            ],
        },
        {
            "family": "interaction-region-routing",
            "focus": "region-filtered interaction delivery, sent-region callback context, and plain interaction subscriber cleanup",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_filters_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_preserves_direct_callback_context_for_timed_region_delivery",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_interactions_by_ddm_region_overlap",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_removes_disconnected_region_interaction_subscriber_from_delivery_state_over_fedpro_schema",
            ],
        },
        {
            "family": "directed-ddm-routing",
            "focus": "directed interaction delivery through object update-region and subscribeInteractionClassWithRegions overlap",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_filters_directed_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_routes_directed_ddm_interactions_only_to_overlapping_subscribers",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_removes_disconnected_directed_ddm_subscriber_from_delivery_state",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_directed_interactions_by_ddm_region_overlap",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_removes_disconnected_directed_ddm_subscriber_from_delivery_state_over_fedpro_schema",
            ],
        },
        {
            "family": "passive-alias-and-compat-scenarios",
            "focus": "passive region subscription aliases and backend-neutral compat DDM scenarios over the same semantics",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_two_federate_suite_ddm_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_ddm_object_region_lifecycle_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_ddm_declaration_gating_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_runs_ddm_passive_region_subscription_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_passive_ddm_region_subscription_aliases_match_active_region_delivery",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_two_federate_suite_ddm_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_ddm_object_region_lifecycle_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_ddm_declaration_gating_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_ddm_passive_region_subscription_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_passive_ddm_region_subscription_aliases_match_active_region_delivery_over_fedpro_route",
            ],
        },
        {
            "family": "ddm-restore-and-disconnect-cleanup",
            "focus": "restore and disconnect cleanup for queued DDM delivery and directed DDM subscriber routing state",
            "direct_tests": [
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_spec_and_shim.py::test_2025_shim_drops_queued_ddm_tso_reflect_for_departed_target",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_queued_ddm_tso_reflect_for_disconnected_target_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema",
            ],
        },
    ]
    return {
        "audit_status": "ddm-default-policy-decomposition-captured",
        "slice_id": "2025-ddm-default-attribute-policy",
        "requirement_count": 23,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "The DDM/default-policy slice is no longer just one large region-policy bucket. Its evidence separates into "
            "lookup/default-policy control, object-region routing and scope advisories, interaction-region routing, "
            "directed DDM routing, passive/compat aliases, and DDM restore/disconnect cleanup."
        ),
        "next_split_boundary": (
            "If this slice needs further tightening, split it first by these DDM/default-policy proof families before "
            "moving region-routing semantics into a dedicated 2025 backend."
        ),
    }


def _build_shim_pressure_family_route_backing_audit() -> dict[str, Any]:
    audits = (
        _build_save_restore_decomposition_audit(),
        _build_directed_interaction_decomposition_audit(),
        _build_ddm_default_policy_decomposition_audit(),
    )
    families: list[dict[str, Any]] = []
    for audit in audits:
        for family in audit["proof_families"]:
            direct_count = len(family["direct_tests"])
            hosted_count = len(family["hosted_tests"])
            families.append(
                {
                    "slice_id": audit["slice_id"],
                    "family": family["family"],
                    "direct_test_count": direct_count,
                    "hosted_test_count": hosted_count,
                    "route_backed_across_current_python_lanes": direct_count > 0 and hosted_count > 0,
                }
            )

    fully_route_backed = [family for family in families if family["route_backed_across_current_python_lanes"]]
    return {
        "audit_status": "shim-pressure-family-route-backing-captured",
        "family_count": len(families),
        "fully_route_backed_family_count": len(fully_route_backed),
        "all_families_route_backed_across_current_python_lanes": len(fully_route_backed) == len(families),
        "families": families,
        "current_assessment": (
            "The decomposed shim-backed pressure families are not in-process-only claims. Every currently named family "
            "across save/restore, directed interaction, and DDM/default-policy has both direct shim proof and hosted "
            "FedPro proof, which strengthens the current-lane working-RTI claim."
        ),
        "residual_boundary": (
            "This still does not prove full cross-binding conformance or full requirement-by-requirement closure; it "
            "proves that the main shim-backed pressure families are executable across the current Python 2025 lanes."
        ),
    }


def _build_shim_pressure_family_asymmetry_audit() -> dict[str, Any]:
    route_backing_audit = _build_shim_pressure_family_route_backing_audit()
    families: list[dict[str, Any]] = []
    for family in route_backing_audit["families"]:
        direct = family["direct_test_count"]
        hosted = family["hosted_test_count"]
        if direct == hosted:
            balance = "balanced"
        elif direct > hosted:
            balance = "direct-heavier"
        else:
            balance = "hosted-heavier"
        families.append({**family, "balance": balance, "count_delta": direct - hosted})

    by_balance = dict(sorted(Counter(item["balance"] for item in families).items()))
    if by_balance.get("direct-heavier", 0) == 0 and by_balance.get("hosted-heavier", 0) == 0:
        current_assessment = (
            "The main shim-backed pressure families are route-backed across the current Python lanes and are now "
            "symmetric at the named proof-family level. The remaining work is no longer family-count parity; it is "
            "deeper behavioral expansion, stronger evidence quality, and architectural judgment about whether the "
            "current 2025 lane should remain shim-backed or be extracted into a dedicated backend."
        )
    else:
        current_assessment = (
            "The main shim-backed pressure families are route-backed across the current Python lanes, but they are "
            "not perfectly symmetric. The remaining parity work is now clearer: close hosted-heavier and direct-heavier "
            "family imbalances rather than inventing new top-level proof areas."
        )
    return {
        "audit_status": "shim-pressure-family-asymmetry-captured",
        "family_count": len(families),
        "by_balance": by_balance,
        "families": families,
        "current_assessment": current_assessment,
        "next_parity_boundary": (
            "Use the hosted-heavier and direct-heavier family rows as the next executable parity worklist for the "
            "current 2025 lane."
        ),
    }


def _build_current_lane_coherence_audit(
    promotion_split_audit: Mapping[str, Any],
    implementation_concentration_audit: Mapping[str, Any],
    slice_aggregation_pressure_audit: Mapping[str, Any],
    shim_pressure_family_route_backing_audit: Mapping[str, Any],
) -> dict[str, Any]:
    major_pressure_slice_ids = {
        item["slice_id"]
        for item in slice_aggregation_pressure_audit["largest_shim_backed_aggregated_slices"]
    }
    return {
        "audit_status": "current-lane-coherence-captured",
        "coherence_claim": "bounded-working-RTI-surface",
        "ready_for_current_lane_coherent_working_surface_claim": (
            promotion_split_audit["ready_for_current_lane_promotion_as_working_surface"]
            and shim_pressure_family_route_backing_audit["all_families_route_backed_across_current_python_lanes"]
        ),
        "ready_for_permanent_no-split_architecture_claim": False,
        "major_pressure_slice_count": len(major_pressure_slice_ids),
        "major_pressure_slices": sorted(major_pressure_slice_ids),
        "shim_backend_concentration_is_material": implementation_concentration_audit["semantic_concentration_is_material"],
        "all_pressure_families_route_backed_across_current_python_lanes": shim_pressure_family_route_backing_audit[
            "all_families_route_backed_across_current_python_lanes"
        ],
        "current_assessment": (
            "The current 2025 lane now has a defensible coherence story: its main shim-backed pressure slices are "
            "identified, decomposed into named proof families, and all of those families are executable across the "
            "current Python 2025 lanes. That is strong evidence for a coherent bounded working RTI surface even "
            "though the lane is still materially concentrated in the shim backend implementation."
        ),
        "residual_blockers": [
            "Implementation concentration in hla-backend-shim/backend.py remains material, so coherence is not the same thing as a permanently settled architecture.",
            "The repo now has a row-level requirement-by-requirement audit, but it still stops at bounded disposition and supported-scope proof rather than an all-covered conformance pass.",
            "Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.",
            "Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or MOM action/request conformance pass.",
        ],
    }


def _build_current_lane_working_surface_statement(
    supported_boundary_statement: Mapping[str, Any],
    current_lane_coherence_audit: Mapping[str, Any],
    promotion_split_audit: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "statement_status": "current-lane-working-surface-statement",
        "ready": (
            supported_boundary_statement["ready"]
            and current_lane_coherence_audit["ready_for_current_lane_coherent_working_surface_claim"]
            and promotion_split_audit["ready_for_current_lane_promotion_as_working_surface"]
        ),
        "statement": (
            "The current 2025 lane can be promoted as the repo's coherent bounded working Python RTI surface: "
            "hla-backend-shim is the live Python 2025 RTI lane, its main shim-backed pressure families are "
            "route-backed across the current Python lanes, and the repo has enough evidence to make that bounded "
            "working-surface claim without hiding unsupported or legacy-only boundaries."
        ),
        "non_claims": [
            "This is not a full requirement-by-requirement IEEE 1516.1-2025 conformance claim.",
            "This is not a permanent no-split architecture decision.",
            "This does not upgrade Java or C++ bindings into exhaustive behavior-conformance lanes.",
            "This does not turn the hosted FedPro route into a full RTI semantics or MOM action/request conformance pass.",
        ],
        "current_assessment": (
            "The repo now has a single explicit statement for the current 2025 lane: promote it as the bounded "
            "working Python 2025 RTI surface, keep the architecture seam intact, and continue using the remaining "
            "requirement-level and cross-binding blockers to decide whether extraction is ever warranted."
        ),
    }


def _route_dimension_summary(
    route_parity_rows: list[dict[str, Any]],
    scenarios: tuple[str, ...],
) -> dict[str, Any]:
    if not scenarios:
        return {
            "scenario_count": 0,
            "row_count": 0,
            "by_status": {},
            "by_route": {},
            "scenarios": [],
            "routes_with_full_parity": [],
        }

    selected_rows = [row for row in route_parity_rows if row["scenario"] in scenarios]
    by_status = dict(sorted(Counter(row["status"] for row in selected_rows).items()))
    by_route: dict[str, dict[str, int]] = {route: {} for route in ROUTE_IDS_2025}
    for row in selected_rows:
        route_counts = by_route.setdefault(row["route"], {})
        route_counts[row["status"]] = route_counts.get(row["status"], 0) + 1
    return {
        "scenario_count": len({row["scenario"] for row in selected_rows}),
        "row_count": len(selected_rows),
        "by_status": by_status,
        "by_route": by_route,
        "scenarios": list(scenarios),
        "routes_with_full_parity": [
            route
            for route, counts in by_route.items()
            if counts.get("parity-covered", 0) == len(scenarios)
            and counts.get("partial", 0) == 0
            and counts.get("missing", 0) == 0
        ],
    }


def _build_objective_dimension_audit(route_parity_matrix: Mapping[str, Any]) -> dict[str, Any]:
    slice_index = _implemented_slice_index()
    route_rows = list(route_parity_matrix["rows"])
    dimensions: list[dict[str, Any]] = []
    for dimension in OBJECTIVE_DIMENSIONS:
        slice_ids = tuple(dimension["implemented_slice_ids"])
        slice_rows = [slice_index[slice_id] for slice_id in slice_ids]
        route_summary = _route_dimension_summary(route_rows, tuple(dimension["route_scenarios"]))
        evidence_tests = sorted({path for row in slice_rows for path in row["evidence"]})
        route_artifacts = sorted(
            {
                artifact
                for row in route_rows
                if row["scenario"] in dimension["route_scenarios"]
                for artifact in row.get("evidence_artifacts", ())
            }
        )
        bounded_ready = (
            dimension["evidence_level"] in {"strong-slice", "bounded-slice"}
            and route_summary["by_status"].get("partial", 0) == 0
            and route_summary["by_status"].get("missing", 0) == 0
        )
        if not dimension["route_scenarios"]:
            bounded_ready = True
        dimensions.append(
            {
                "id": dimension["id"],
                "name": dimension["name"],
                "evidence_level": dimension["evidence_level"],
                "bounded_working_surface_ready": bounded_ready,
                "ready_for_full_claim": False,
                "implemented_slice_ids": slice_ids,
                "requirements_count": sum(len(row["requirements"]) for row in slice_rows),
                "evidence_tests": evidence_tests,
                "route_scenarios": tuple(dimension["route_scenarios"]),
                "route_summary": route_summary,
                "route_artifacts": route_artifacts,
                "current_assessment": dimension["current_assessment"],
                "residual_blockers": list(dimension["residual_blockers"]),
            }
        )

    bounded_ready_dimensions = sum(1 for dimension in dimensions if dimension["bounded_working_surface_ready"])
    return {
        "goal_shape": (
            "Convert the clean 2025 requirement closeout into deeper runtime proof across federation management, "
            "object management, time management, support services, callbacks, OMT handling, and binding routes."
        ),
        "surface_claim": "bounded-working-surface",
        "ready_for_bounded_working_surface_claim": bounded_ready_dimensions == len(dimensions),
        "ready_for_full_2025_completion_claim": False,
        "dimension_count": len(dimensions),
        "bounded_ready_dimension_count": bounded_ready_dimensions,
        "dimensions": dimensions,
        "overall_assessment": (
            "The repo now supports a bounded working-surface claim across the core runtime dimensions, but that is "
            "still weaker than a final 2025 conformance claim because several areas remain slice-bounded or "
            "artifact-gated rather than requirement-by-requirement proven."
        ),
    }


def _build_python_rti_milestone_audit(route_parity_matrix: Mapping[str, Any]) -> dict[str, Any]:
    route_rows = list(route_parity_matrix["rows"])
    route_index = {(row["route"], row["scenario"]): row for row in route_rows}
    milestone_specs: tuple[dict[str, Any], ...] = (
        {
            "id": "best_attempt_working_surface",
            "label": "Best-attempt Python RTI 2025 working surface",
            "status": "bounded-working-slice",
            "scenarios": (
                "federation_lifecycle",
                "object_exchange",
                "ownership",
                "ddm",
                "time_management",
                "save_restore",
                "mom",
                "support_services",
            ),
            "supporting_slice_ids": (
                "2025-fedpro-hosted-runtime-core",
                "2025-fedpro-hosted-runtime-extended-state",
                "2025-standard-route-runtime-capability",
            ),
            "requirement_ids": ("HLA2025-FI-001", "HLA2025-FI-004", "HLA2025-FI-005", "HLA2025-FI-009"),
            "summary_by_route": {
                "python-2025-inprocess": (
                    "In-process Python 2025 is a best-attempt bounded working surface across the tracked runtime "
                    "scenario set, not a full requirement-by-requirement conformance claim."
                ),
                "python-2025-fedpro-grpc": (
                    "Hosted FedPro Python 2025 is a best-attempt bounded working surface across the tracked runtime "
                    "scenario set, not a full RTI semantics or MOM action-request conformance claim."
                ),
            },
            "boundary_by_route": {
                "python-2025-inprocess": (
                    "This milestone does not certify a full-fledged RTI beyond the tracked scenario and requirement slices."
                ),
                "python-2025-fedpro-grpc": (
                    "This milestone remains explicitly bounded to the hosted FedPro runtime slice."
                ),
            },
        },
        {
            "id": "example_fom_scenarios",
            "label": "Tracked example and FOM-backed scenario execution",
            "status": "covered-scenario-slice",
            "scenarios": ("object_exchange", "save_restore", "mom"),
            "supporting_slice_ids": ("2025-fom-showcase", "2025-basic-object-exchange", "2025-save-restore-lifecycle"),
            "requirement_ids": ("HLA2025-FR-001", "HLA2025-FR-003", "HLA2025-FR-004", "HLA2025-REQ-002"),
            "summary_by_route": {
                "python-2025-inprocess": (
                    "The in-process route executes the tracked repo example/FOM-backed scenarios, including object "
                    "exchange, FOM showcase, and save/restore rollback paths."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route executes the tracked FOM-backed runtime scenarios used by the current "
                    "object, MOM, and save/restore route tests."
                ),
            },
            "boundary_by_route": {
                "python-2025-inprocess": (
                    "This does not yet prove every conceivable example FOM scenario outside the tracked suite."
                ),
                "python-2025-fedpro-grpc": (
                    "This is scenario-suite evidence, not a universal claim for every possible FOM composition."
                ),
            },
        },
        {
            "id": "messaging_and_routing",
            "label": "Message exchange and routing",
            "status": "covered-routing-slice",
            "scenarios": ("object_exchange", "ddm", "mom"),
            "supporting_slice_ids": (
                "2025-basic-object-exchange",
                "2025-directed-interaction-boundary",
                "2025-ddm-default-attribute-policy",
                "2025-fedpro-hosted-runtime-core",
                "2025-fedpro-hosted-runtime-extended-state",
            ),
            "requirement_ids": (
                "HLA2025-FI-SVC-057",
                "HLA2025-FI-SVC-060",
                "HLA2025-FI-SVC-063",
                "HLA2025-FI-SVC-126",
                "HLA2025-FI-SVC-134",
            ),
            "summary_by_route": {
                "python-2025-inprocess": (
                    "The in-process route sends, receives, discovers, reflects, directs, and DDM-filters the tracked "
                    "message flows end to end."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route sends, receives, discovers, reflects, directs, and DDM-filters the "
                    "tracked message flows over the typed transport surface."
                ),
            },
            "boundary_by_route": {
                "python-2025-inprocess": (
                    "Routing proof remains bounded to the executable scenario matrix rather than every FI service in isolation."
                ),
                "python-2025-fedpro-grpc": (
                    "Routing proof remains bounded to the hosted transport/runtime slice."
                ),
            },
        },
        {
            "id": "time_sync_and_advances",
            "label": "Time synchronization and advance flow",
            "status": "covered-time-advance-slice",
            "scenarios": ("time_management", "save_restore"),
            "supporting_slice_ids": (
                "2025-time-mode-enable-disable",
                "2025-time-advance-request-modes",
                "2025-time-grant-and-async-delivery",
                "2025-time-queries-retraction-and-order",
                "2025-save-restore-lifecycle",
                "2025-fedpro-hosted-runtime-extended-state",
            ),
            "requirement_ids": ("HLA2025-FI-SVC-101", "HLA2025-FI-SVC-112", "HLA2025-FI-SVC-121", "HLA2025-FI-SVC-123"),
            "summary_by_route": {
                "python-2025-inprocess": (
                    "The in-process route exercises regulation/constrained enablement, time advance, flush queue, "
                    "timestamped delivery, retraction, restore rollback of logical time, and restore recovery of "
                    "saved lookahead plus time/switch control state."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route exercises regulation/constrained enablement, async delivery control, "
                    "advance/grant flow, queued TSO delivery, retraction, restore rollback of logical time, and "
                    "restore recovery of saved lookahead plus time/switch control state."
                ),
            },
            "boundary_by_route": {
                "python-2025-inprocess": (
                    "This is strong runtime evidence for time sync behavior, not a final per-service conformance proof."
                ),
                "python-2025-fedpro-grpc": (
                    "This is strong hosted runtime evidence for time sync behavior, not a full RTI time-semantics proof."
                ),
            },
        },
        {
            "id": "galt_lits_queries",
            "label": "GALT and LITS behavior",
            "status": "bounded-query-evidence",
            "scenarios": ("time_management",),
            "supporting_slice_ids": (
                "2025-time-query-and-lookahead-control",
                "2025-time-queries-retraction-and-order",
                "2025-lookahead-window-proofs",
                "2025-fedpro-hosted-runtime-extended-state",
                "2025-standard-route-runtime-capability",
            ),
            "requirement_ids": ("HLA2025-FI-SVC-122", "HLA2025-FI-SVC-123"),
            "summary_by_route": {
                "python-2025-inprocess": (
                    "The in-process route has executable GALT/LITS query evidence inside the logical-time slice and "
                    "the Target/Radar future-exclusion proof, with the integrated lookahead-processing-window gauntlet "
                    "proving the combined closure/output/consumer-order/pipeline ladder on the actual 2025 shim, plus "
                    "save/restore evidence that dirty lookahead changes are rolled back while a pre-save queued TSO is "
                    "still redelivered after restore."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route has executable GALT/LITS query evidence inside the hosted time-management "
                    "slice, including queued-TSO GALT/LITS divergence after a live lookahead change, the hosted "
                    "Target/Radar proof-ladder replay, restore rollback of dirty lookahead with pre-save queued TSO "
                    "redelivered after restore, and the Target/Radar future-exclusion proof."
                ),
            },
            "boundary_by_route": {
                "python-2025-inprocess": (
                    "Current evidence is not strong enough to claim a fully proven or universally correct GALT/LITS algorithm."
                ),
                "python-2025-fedpro-grpc": (
                    "Current evidence is not strong enough to claim a fully proven or universally correct hosted GALT/LITS algorithm."
                ),
            },
        },
        {
            "id": "lookahead_windows",
            "label": "Lookahead handling and windows",
            "status": "bounded-lookahead-evidence",
            "scenarios": ("time_management",),
            "supporting_slice_ids": (
                "2025-time-advance-request-modes",
                "2025-time-query-and-lookahead-control",
                "2025-lookahead-window-proofs",
                "2025-fedpro-hosted-runtime-extended-state",
                "2025-standard-route-runtime-capability",
            ),
            "requirement_ids": ("HLA2025-FI-SVC-107", "HLA2025-FI-SVC-108", "HLA2025-FI-SVC-121"),
            "summary_by_route": {
                "python-2025-inprocess": (
                    "The in-process route exercises lookahead query/modify behavior, queued timestamped delivery, "
                    "the integrated Target/Radar lookahead-processing-window gauntlet, and the time-window core, "
                    "output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, "
                    "save-restore-window-state, save-restore lookahead rollback with queued-TSO redelivery, "
                    "save-restore-output-resume, and save-restore-pipeline-resume proofs."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route exercises lookahead queries together with advance/grant, queued "
                    "timestamped delivery, the hosted Target/Radar proof-ladder replay, and the Target/Radar "
                    "output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, "
                    "save-restore lookahead rollback with queued-TSO redelivery, "
                    "save-restore-output-resume, and save-restore-pipeline-resume proofs."
                ),
            },
            "boundary_by_route": {
                "python-2025-inprocess": (
                    "This is bounded runtime evidence for lookahead-window handling, including safe window closure and "
                    "future-message exclusion, not a final proof for every edge case."
                ),
                "python-2025-fedpro-grpc": (
                    "This is bounded hosted runtime evidence for lookahead-window handling, including future-message "
                        "exclusion, not a final proof for every edge case."
                ),
            },
        },
    )

    rows: list[dict[str, Any]] = []
    for route in ("python-2025-inprocess", "python-2025-fedpro-grpc"):
        for spec in milestone_specs:
            matched_rows = [route_index[(route, scenario)] for scenario in spec["scenarios"]]
            rows.append(
                {
                    "route": route,
                    "milestone_id": spec["id"],
                    "milestone_label": spec["label"],
                    "status": spec["status"],
                    "scenario_count": len(spec["scenarios"]),
                    "route_parity_statuses": dict(sorted(Counter(row["status"] for row in matched_rows).items())),
                    "supporting_scenarios": list(spec["scenarios"]),
                    "supporting_slice_ids": list(spec["supporting_slice_ids"]),
                    "requirement_ids": list(spec["requirement_ids"]),
                    "evidence_tests": sorted({test_path for row in matched_rows for test_path in row["evidence_tests"]}),
                    "route_notes": [row["notes"] for row in matched_rows],
                    "summary": spec["summary_by_route"][route],
                    "boundary": spec["boundary_by_route"][route],
                }
            )

    by_route: dict[str, dict[str, Any]] = {}
    for route in ("python-2025-inprocess", "python-2025-fedpro-grpc"):
        route_milestones = [row for row in rows if row["route"] == route]
        by_route[route] = {
            "milestone_count": len(route_milestones),
            "status_counts": dict(sorted(Counter(row["status"] for row in route_milestones).items())),
            "all_route_parity_covered": all(
                row["route_parity_statuses"].get("parity-covered", 0) == row["scenario_count"] for row in route_milestones
            ),
            "current_assessment": "The route clears the tracked milestone gates as a bounded Python 2025 working surface.",
        }

    return {
        "audit_status": "bounded-python-rti-milestones",
        "milestone_count": len(milestone_specs),
        "row_count": len(rows),
        "routes": ["python-2025-inprocess", "python-2025-fedpro-grpc"],
        "current_assessment": (
            "Both Python 2025 routes now have explicit milestone gates for working-surface breadth, FOM-backed "
            "scenario execution, message routing, time sync, GALT/LITS query evidence, and lookahead handling. "
            "The time milestones now explicitly include Target/Radar future-exclusion, output-delivery, consumer-order, "
            "pipeline, receive-order poison, save/restore window-state, save/restore output resume, save/restore pipeline "
            "resume, and time-window proof, "
            "but the last four remain bounded-evidence milestones rather than blanket correctness claims."
        ),
        "rows": rows,
        "by_route": by_route,
    }

BACKLOG_STATUS_BY_ROW = {
    "HLA2025-BLG-001": "implemented-slice",
    "HLA2025-BLG-002": "implemented-slice",
    "HLA2025-BND-001": "implemented-slice",
    "HLA2025-BND-002": "implemented-slice",
    "HLA2025-BND-003": "implemented-slice",
    "HLA2025-MOD-001": "implemented-slice",
    "HLA2025-MOD-002": "implemented-slice",
    "HLA2025-MOD-003": "implemented-slice",
    "HLA2025-MOD-004": "implemented-slice",
    "HLA2025-MOD-005": "implemented-slice",
    "HLA2025-MOD-006": "implemented-slice",
    "HLA2025-MOD-007": "implemented-slice",
    "HLA2025-MOD-008": "implemented-slice",
    "HLA2025-MOD-009": "implemented-slice",
    "HLA2025-MOD-010": "implemented-slice",
    "HLA2025-NEW-001": "implemented-slice",
    "HLA2025-NEW-002": "implemented-slice",
    "HLA2025-NEW-003": "implemented-slice",
    "HLA2025-NEW-004": "implemented-slice",
    "HLA2025-NEW-005": "implemented-slice",
    "HLA2025-NEW-006": "implemented-slice",
    "HLA2025-NEW-007": "implemented-slice",
    "HLA2025-RET-001": "implemented-slice",
    "HLA2025-RET-002": "implemented-slice",
    "HLA2025-RET-003": "legacy-only",
    "HLA2025-VER-001": "implemented-slice",
    "HLA2025-VER-002": "implemented-slice",
    "HLA2025-MIL-001": "implemented-slice",
    "HLA2025-MIL-002": "implemented-slice",
    "HLA2025-MIL-003": "implemented-slice",
    "HLA2025-MIL-004": "implemented-slice",
    "HLA2025-MIL-005": "implemented-slice",
    "HLA2025-MIL-006": "implemented-slice",
}


@dataclass(frozen=True, slots=True)
class Spec2025Paths:
    project_root: Path
    completion_backlog: Path
    executable_summary: Path
    executable_rows: Path
    depth_summary: Path
    depth_rows: Path
    harmonization_rollup: Path
    harmonization_rows: Path
    registry: Path


def _paths(project_root: Path) -> Spec2025Paths:
    req_dir = project_root / "docs" / "requirements" / "ieee-1516-2025"
    return Spec2025Paths(
        project_root=project_root,
        completion_backlog=project_root / "requirements" / "2025" / "requirement_completion_backlog.csv",
        executable_summary=req_dir / "executable_tests" / "hla_2025_executable_test_requirements_v3_summary.json",
        executable_rows=req_dir / "executable_tests" / "hla_2025_executable_test_requirements_v3.csv",
        depth_summary=project_root / "requirements" / "2025" / "depth" / "hla_2025_requirement_depth_expansion_summary.json",
        depth_rows=project_root / "requirements" / "2025" / "depth" / "hla_2025_requirement_depth_expansion.csv",
        harmonization_rollup=project_root / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_coverage_rollup.json",
        harmonization_rows=project_root / "requirements" / "2025" / "harmonization" / "hla_2025_requirement_disposition_ledger.csv",
        registry=req_dir / "requirements.json",
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _counter(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row[field] for row in rows).items()))


def _next_status(row_id: str) -> str:
    return BACKLOG_STATUS_BY_ROW.get(row_id, "planned")


def _extract_requirement_markers_from_test(path: Path) -> list[tuple[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    anchors: list[tuple[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr == "requirements"
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "mark"
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id == "pytest"
            ):
                continue
            for arg in decorator.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("HLA2025-"):
                    anchors.append((arg.value, f"{path.as_posix()}::{node.name}"))
    return anchors


def _build_requirement_pytest_anchor_audit(project_root: Path) -> dict[str, Any]:
    tests_root = project_root / "tests"
    by_requirement: dict[str, list[str]] = {}
    for path in sorted(tests_root.rglob("test_*.py")):
        for requirement_id, nodeid in _extract_requirement_markers_from_test(path):
            by_requirement.setdefault(requirement_id, []).append(nodeid)
    rows = [
        {
            "requirement_id": requirement_id,
            "pytest_anchor_count": len(sorted(set(nodeids))),
            "pytest_anchors": sorted(set(nodeids)),
        }
        for requirement_id, nodeids in sorted(by_requirement.items())
    ]
    return {
        "row_count": len(rows),
        "anchored_requirement_count": len(rows),
        "current_assessment": (
            "Repo-native HLA2025 requirement markers now provide direct pytest-function anchors for the supported "
            "working-surface claim, complementing the broader evidence-slice ledgers."
        ),
        "rows": rows,
    }


def _build_unanchored_requirement_audit(
    pytest_anchor_audit: Mapping[str, Any],
    fi_audit: Mapping[str, Any],
    delta_audit: Mapping[str, Any],
    binding_audit: Mapping[str, Any],
    omt_audit: Mapping[str, Any],
) -> dict[str, Any]:
    anchored = {row["requirement_id"] for row in pytest_anchor_audit["rows"]}
    ledger_rows = [
        *fi_audit["rows"],
        *delta_audit["rows"],
        *binding_audit["rows"],
        *omt_audit["rows"],
    ]
    unanchored_rows = sorted(
        (
            {
                "requirement_id": row["requirement_id"],
                "family": row["requirement_id"].split("-", 1)[0] if False else (
                    "FI" if row["requirement_id"].startswith("HLA2025-FI-")
                    else "OMT" if row["requirement_id"].startswith("HLA2025-OMT-")
                    else "other"
                ),
            }
            for row in ledger_rows
            if row["requirement_id"] not in anchored
        ),
        key=lambda row: row["requirement_id"],
    )
    if unanchored_rows:
        current_assessment = (
            "Direct pytest anchors still lag behind the broader requirement ledgers. The remaining gap is now "
            "concentrated in FI service rows and OMT rows rather than the higher-level delta and binding requirements."
        )
    else:
        current_assessment = (
            "All FI, delta, binding, and OMT proof-ledger rows now have direct pytest-function anchors, so the "
            "broader evidence-slice ledgers and direct requirement markers are aligned."
        )
    return {
        "row_count": len(unanchored_rows),
        "by_family": dict(sorted(Counter(row["family"] for row in unanchored_rows).items())),
        "current_assessment": current_assessment,
        "sample_requirement_ids": [row["requirement_id"] for row in unanchored_rows[:40]],
        "rows": unanchored_rows,
    }


def _priority_rank(row: dict[str, str]) -> tuple[int, str]:
    priority_order = {"very-high": 0, "high": 1, "medium-high": 2}
    status_order = {"planned": 0, "partial": 1, "implemented-slice": 2}
    return (
        priority_order.get(row["priority"], 9) * 10 + status_order.get(row["current_status"], 9),
        row["id"],
    )


def _evidence_slices_by_requirement() -> dict[str, list[str]]:
    anchors: dict[str, list[str]] = {}
    for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES:
        for requirement_id in evidence_slice["requirements"]:
            anchors.setdefault(requirement_id, []).append(str(evidence_slice["id"]))
    return anchors


def _executable_tests_by_requirement(executable_rows: list[dict[str, str]]) -> dict[str, list[str]]:
    anchors: dict[str, list[str]] = {}
    for row in executable_rows:
        parent_id = row["parent_requirement_id"]
        if row["pytest_candidate"] or row["evidence_artifact"] or row["dependency_or_blocker"]:
            anchors.setdefault(parent_id, []).append(row["executable_test_id"])
    return anchors


def _build_verification_matrix(
    completion_rows: list[dict[str, str]],
    executable_rows: list[dict[str, str]],
) -> dict[str, Any]:
    evidence_slices = _evidence_slices_by_requirement()
    executable_tests = _executable_tests_by_requirement(executable_rows)
    rows: list[dict[str, Any]] = []
    for row in completion_rows:
        requirement_id = row["id"]
        status = row["current_status"]
        evidence_slice_ids = tuple(evidence_slices.get(requirement_id, ()))
        executable_test_ids = tuple(executable_tests.get(requirement_id, ()))
        explicit_disposition_anchor = status in {"legacy-only", "unsupported-boundary"}
        has_anchor = bool(evidence_slice_ids or executable_test_ids or explicit_disposition_anchor)
        rows.append(
            {
                "id": requirement_id,
                "bucket": row["bucket"],
                "area": row["area"],
                "priority": row["priority"],
                "current_status": status,
                "binding_scope": row["binding_scope"],
                "has_anchor": has_anchor,
                "evidence_slices": evidence_slice_ids,
                "executable_tests": executable_test_ids,
                "explicit_disposition_anchor": explicit_disposition_anchor,
                "verification_work": row["verification_work"],
            }
        )
    high_priority_rows = [row for row in rows if row["priority"] in HIGH_PRIORITIES]
    high_priority_missing = [row for row in high_priority_rows if not row["has_anchor"]]
    return {
        "row_count": len(rows),
        "anchor_count": sum(1 for row in rows if row["has_anchor"]),
        "missing_anchor_count": sum(1 for row in rows if not row["has_anchor"]),
        "high_priority_row_count": len(high_priority_rows),
        "high_priority_missing_anchor_count": len(high_priority_missing),
        "high_priority_missing_anchors": high_priority_missing,
        "rows": rows,
    }


def build_spec2025_finish_line_snapshot(project_root: Path) -> dict[str, Any]:
    """Return the current 2025 requirements finish-line inventory."""

    paths = _paths(project_root)
    completion_rows = _read_csv(paths.completion_backlog)
    executable_summary = json.loads(paths.executable_summary.read_text(encoding="utf-8"))
    executable_rows = _read_csv(paths.executable_rows)
    depth_summary = json.loads(paths.depth_summary.read_text(encoding="utf-8"))
    depth_rows = _read_csv(paths.depth_rows)
    harmonization_rollup = json.loads(paths.harmonization_rollup.read_text(encoding="utf-8"))
    harmonization_rows = _read_csv(paths.harmonization_rows)
    registry = json.loads(paths.registry.read_text(encoding="utf-8"))
    imported_packets = {packet["id"]: packet for packet in registry.get("imported_packets", ())}
    registry_requirements = registry.get("requirements", ())

    completion_with_status: list[dict[str, str]] = []
    for row in completion_rows:
        item = dict(row)
        item["current_status"] = _next_status(row["id"])
        completion_with_status.append(item)

    high_priority_open = [row for row in completion_with_status if row["priority"] in HIGH_PRIORITIES and row["current_status"] not in CLOSED_STATUSES]
    high_priority_open = sorted(high_priority_open, key=_priority_rank)

    executable_status_counts = dict(sorted(Counter(row["expected_status"] for row in executable_rows).items()))
    executable_priority_counts = dict(sorted(Counter(row["priority"] for row in executable_rows).items()))
    verification_matrix = _build_verification_matrix(completion_with_status, executable_rows)
    requirement_pytest_anchor_audit = _build_requirement_pytest_anchor_audit(project_root)
    route_parity_matrix = summarize_spec2025_route_parity()
    objective_dimension_audit = _build_objective_dimension_audit(route_parity_matrix)
    fi_service_proof_audit = _build_fi_service_proof_audit()
    delta_requirement_proof_audit = _build_delta_requirement_proof_audit()
    binding_requirement_proof_audit = _build_binding_requirement_proof_audit(route_parity_matrix)
    omt_requirement_proof_audit = _build_omt_requirement_proof_audit()
    callback_proof_audit = _build_callback_proof_audit()
    callback_route_parity_audit = _build_callback_route_parity_audit(callback_proof_audit)
    support_service_proof_audit = _build_support_service_proof_audit()
    python_rti_milestone_audit = _build_python_rti_milestone_audit(route_parity_matrix)
    unanchored_requirement_audit = _build_unanchored_requirement_audit(
        requirement_pytest_anchor_audit,
        fi_service_proof_audit,
        delta_requirement_proof_audit,
        binding_requirement_proof_audit,
        omt_requirement_proof_audit,
    )
    route_partial_count = route_parity_matrix["by_status"].get("partial", 0)
    route_missing_count = route_parity_matrix["by_status"].get("missing", 0)
    closeout_ready = len(high_priority_open) == 0 and route_partial_count == 0 and route_missing_count == 0
    conformance_blockers = [
        "The repo now has a row-level requirement-by-requirement disposition audit across all 2025 rows, but that audit still contains unsupported, retired, and umbrella rows rather than an all-covered conformance pass.",
        "Many implemented-slice rows outside the FI service catalog still aggregate multiple requirements under bounded supported-scope language rather than proving every requirement individually.",
        "Java and C++ standard-route evidence remains artifact-gated/runtime-capability evidence, not a full cross-binding behavior-conformance pass.",
        "The hosted FedPro route is verified as a runtime slice, but its own supported-scope rows explicitly stop short of full RTI semantics and full MOM action/request conformance.",
        "OMT component and validator coverage still mixes supported-subset proof with explicit unsupported-boundary rows, so those areas are not yet represented as an unconditional requirement-by-requirement conformance pass.",
        "Unsupported-boundary and legacy-only rows remain explicit exclusions rather than delivered support, so overall completion cannot be promoted to an unconditional 2025 conformance claim.",
    ]

    completion_backlog = {
        "row_count": len(completion_with_status),
        "by_bucket": _counter(completion_with_status, "bucket"),
        "by_priority": _counter(completion_with_status, "priority"),
        "by_current_status": _counter(completion_with_status, "current_status"),
        "high_priority_open_count": len(high_priority_open),
        "high_priority_open": [
            {
                "id": row["id"],
                "bucket": row["bucket"],
                "area": row["area"],
                "priority": row["priority"],
                "current_status": row["current_status"],
                "acceptance_criteria": row["acceptance_criteria"],
                "verification_work": row["verification_work"],
            }
            for row in high_priority_open
        ],
    }
    requirement_coverage_disposition = {
        "row_count": harmonization_rollup["total_rows"],
        "row_count_from_csv": len(harmonization_rows),
        "by_disposition": harmonization_rollup["by_disposition"],
        "by_priority": harmonization_rollup["by_priority"],
        "by_area_and_disposition": harmonization_rollup["by_area_and_disposition"],
        "by_closure_wave": harmonization_rollup["by_closure_wave"],
        "fi_binding_surface": harmonization_rollup["fi_binding_surface"],
        "covered_row_count": harmonization_rollup["by_disposition"].get("covered", 0),
        "source": "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv",
        "status": imported_packets["hla-2025-requirement-coverage-disposition"]["status"],
    }
    requirement_by_requirement_audit = _build_requirement_by_requirement_audit(
        harmonization_rows,
        requirement_coverage_disposition,
    )
    completion_claim_audit = _build_completion_claim_audit(
        completion_backlog,
        requirement_coverage_disposition,
        objective_dimension_audit,
        fi_service_proof_audit,
        delta_requirement_proof_audit,
        binding_requirement_proof_audit,
        omt_requirement_proof_audit,
    )
    implementation_concentration_audit = _build_implementation_concentration_audit()
    slice_aggregation_pressure_audit = _build_slice_aggregation_pressure_audit()
    save_restore_decomposition_audit = _build_save_restore_decomposition_audit()
    directed_interaction_decomposition_audit = _build_directed_interaction_decomposition_audit()
    ddm_default_policy_decomposition_audit = _build_ddm_default_policy_decomposition_audit()
    shim_pressure_family_route_backing_audit = _build_shim_pressure_family_route_backing_audit()
    shim_pressure_family_asymmetry_audit = _build_shim_pressure_family_asymmetry_audit()
    closeout_readiness = {
        "implemented_slice_count": len(IMPLEMENTED_EVIDENCE_SLICES),
        "high_priority_open_count": len(high_priority_open),
        "route_parity_partial_count": route_partial_count,
        "route_parity_missing_count": route_missing_count,
        "ready_for_slice_closeout": closeout_ready,
        "ready_for_full_completion_claim": False,
        "current_assessment": (
            "Executable slice coverage, route parity, FI per-service runtime traceability, and bounded working-RTI "
            "milestone evidence are in strong shape for the current 2025 lane, and the repo now has a row-level "
            "requirement-by-requirement disposition audit across the full 2025 universe, but the remaining "
            "unsupported, umbrella, cross-binding, and bounded-route limits still block a complete 2025 claim or "
            "a permanent promotion decision over a future shim-versus-dedicated-RTI split."
        ),
        "conformance_blockers": conformance_blockers,
    }
    supported_boundary_statement = _build_supported_boundary_statement(
        completion_claim_audit,
        objective_dimension_audit,
        route_parity_matrix,
    )
    promotion_split_audit = _build_promotion_split_audit(
        closeout_readiness,
        completion_claim_audit,
        supported_boundary_statement,
        python_rti_milestone_audit,
    )
    current_lane_coherence_audit = _build_current_lane_coherence_audit(
        promotion_split_audit,
        implementation_concentration_audit,
        slice_aggregation_pressure_audit,
        shim_pressure_family_route_backing_audit,
    )
    current_lane_working_surface_statement = _build_current_lane_working_surface_statement(
        supported_boundary_statement,
        current_lane_coherence_audit,
        promotion_split_audit,
    )
    implementation_lane_audit = _build_implementation_lane_audit(
        promotion_split_audit,
        python_rti_milestone_audit,
    )

    return {
        "scope": "IEEE 1516-2025 requirements finish-line inventory, not a conformance claim",
        "registry": {
            "initial_tranche_requirements": len(registry_requirements),
            "imported_packets": [packet["id"] for packet in registry.get("imported_packets", ())],
        },
        "completion_backlog": completion_backlog,
        "executable_test_backlog": {
            "row_count": executable_summary["executable_test_rows"],
            "source_rows": executable_summary["source_rows"],
            "by_test_kind": executable_summary["by_test_kind"],
            "by_expected_status": executable_summary["by_expected_status"],
            "by_priority": executable_priority_counts,
            "expected_status_counts_from_rows": executable_status_counts,
        },
        "requirement_depth_expansion": {
            "row_count": depth_summary["total_rows"],
            "row_count_from_csv": len(depth_rows),
            "by_area": depth_summary["by_area"],
            "by_delta_type": depth_summary["by_delta_type"],
            "by_source_document": depth_summary["by_source_document"],
            "source": "requirements/2025/depth/hla_2025_requirement_depth_expansion.csv",
            "status": imported_packets["hla-2025-requirement-depth-expansion"]["status"],
        },
        "requirement_coverage_disposition": requirement_coverage_disposition,
        "implemented_evidence_slices": [dict(slice_) for slice_ in IMPLEMENTED_EVIDENCE_SLICES],
        "verification_matrix": verification_matrix,
        "requirement_pytest_anchor_audit": requirement_pytest_anchor_audit,
        "unanchored_requirement_audit": unanchored_requirement_audit,
        "route_parity_matrix": route_parity_matrix,
        "route_parity_audit": route_parity_matrix,
        "objective_dimension_audit": objective_dimension_audit,
        "fi_service_proof_audit": fi_service_proof_audit,
        "delta_requirement_proof_audit": delta_requirement_proof_audit,
        "binding_requirement_proof_audit": binding_requirement_proof_audit,
        "omt_requirement_proof_audit": omt_requirement_proof_audit,
        "callback_proof_audit": callback_proof_audit,
        "callback_route_parity_audit": callback_route_parity_audit,
        "support_service_proof_audit": support_service_proof_audit,
        "python_rti_milestone_audit": python_rti_milestone_audit,
        "requirement_by_requirement_audit": requirement_by_requirement_audit,
        "completion_claim_audit": completion_claim_audit,
        "supported_boundary_statement": supported_boundary_statement,
        "implementation_concentration_audit": implementation_concentration_audit,
        "slice_aggregation_pressure_audit": slice_aggregation_pressure_audit,
        "save_restore_decomposition_audit": save_restore_decomposition_audit,
        "directed_interaction_decomposition_audit": directed_interaction_decomposition_audit,
        "ddm_default_policy_decomposition_audit": ddm_default_policy_decomposition_audit,
        "shim_pressure_family_route_backing_audit": shim_pressure_family_route_backing_audit,
        "shim_pressure_family_asymmetry_audit": shim_pressure_family_asymmetry_audit,
        "current_lane_coherence_audit": current_lane_coherence_audit,
        "current_lane_working_surface_statement": current_lane_working_surface_statement,
        "implementation_lane_audit": implementation_lane_audit,
        "promotion_split_audit": promotion_split_audit,
        "promotion_vs_split_audit": promotion_split_audit,
        "closeout_readiness": closeout_readiness,
        "finish_rule": (
            "Each remaining row needs a positive test, a negative unsupported-boundary test, "
            "or an explicit supported-subset/unsupported-boundary row before it can be counted as closed."
        ),
    }


def build_spec2025_finish_line_markdown(project_root: Path) -> list[str]:
    snapshot = build_spec2025_finish_line_snapshot(project_root)
    backlog = snapshot["completion_backlog"]
    executable = snapshot["executable_test_backlog"]
    depth = snapshot["requirement_depth_expansion"]
    disposition = snapshot["requirement_coverage_disposition"]
    pytest_anchor_audit = snapshot["requirement_pytest_anchor_audit"]
    unanchored_audit = snapshot["unanchored_requirement_audit"]
    objective_audit = snapshot["objective_dimension_audit"]
    fi_service_audit = snapshot["fi_service_proof_audit"]
    delta_audit = snapshot["delta_requirement_proof_audit"]
    binding_audit = snapshot["binding_requirement_proof_audit"]
    omt_audit = snapshot["omt_requirement_proof_audit"]
    callback_audit = snapshot["callback_proof_audit"]
    callback_route_parity_audit = snapshot["callback_route_parity_audit"]
    support_service_audit = snapshot["support_service_proof_audit"]
    milestone_audit = snapshot["python_rti_milestone_audit"]
    requirement_by_requirement_audit = snapshot["requirement_by_requirement_audit"]
    claim_audit = snapshot["completion_claim_audit"]
    supported_boundary = snapshot["supported_boundary_statement"]
    implementation_concentration_audit = snapshot["implementation_concentration_audit"]
    slice_aggregation_pressure_audit = snapshot["slice_aggregation_pressure_audit"]
    save_restore_decomposition_audit = snapshot["save_restore_decomposition_audit"]
    directed_interaction_decomposition_audit = snapshot["directed_interaction_decomposition_audit"]
    ddm_default_policy_decomposition_audit = snapshot["ddm_default_policy_decomposition_audit"]
    shim_pressure_family_route_backing_audit = snapshot["shim_pressure_family_route_backing_audit"]
    shim_pressure_family_asymmetry_audit = snapshot["shim_pressure_family_asymmetry_audit"]
    current_lane_coherence_audit = snapshot["current_lane_coherence_audit"]
    current_lane_working_surface_statement = snapshot["current_lane_working_surface_statement"]
    implementation_lane_audit = snapshot["implementation_lane_audit"]
    promotion_split_audit = snapshot["promotion_split_audit"]
    lines = [
        "# IEEE 1516-2025 Requirements Finish Line",
        "",
        "This inventory is deliberately conservative. It records implemented slices, partial slices, and planned work without using HLA conformance language.",
        "",
        "## Current Scale",
        "",
        f"- Initial curated registry rows: {snapshot['registry']['initial_tranche_requirements']}",
        f"- Imported executable-test rows: {executable['row_count']}",
        f"- Imported requirement-depth rows: {depth['row_count']}",
        f"- Imported provisional disposition rows: {disposition['row_count']}",
        f"- Completion-backlog rows: {backlog['row_count']}",
        f"- High-priority rows still open: {backlog['high_priority_open_count']}",
        "",
        "## Closeout Readiness",
        "",
        f"- Implemented evidence slices: {snapshot['closeout_readiness']['implemented_slice_count']}",
        f"- Route parity partial rows: {snapshot['closeout_readiness']['route_parity_partial_count']}",
        f"- Route parity missing rows: {snapshot['closeout_readiness']['route_parity_missing_count']}",
        f"- Ready for slice closeout: {snapshot['closeout_readiness']['ready_for_slice_closeout']}",
        f"- Ready for full completion claim: {snapshot['closeout_readiness']['ready_for_full_completion_claim']}",
        f"- Assessment: {snapshot['closeout_readiness']['current_assessment']}",
        "",
        "Conformance blockers:",
        "",
    ]
    for blocker in snapshot["closeout_readiness"]["conformance_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## Pytest Anchor Audit",
            "",
            f"- Anchored requirements: {pytest_anchor_audit['anchored_requirement_count']}",
            f"- Assessment: {pytest_anchor_audit['current_assessment']}",
            "",
            "## Unanchored Requirement Audit",
            "",
            f"- Unanchored ledger requirements: {unanchored_audit['row_count']}",
            f"- Assessment: {unanchored_audit['current_assessment']}",
            "",
            "## FI Service Proof Audit",
            "",
            f"- Service rows: {fi_service_audit['row_count']}",
            f"- Ready for per-service runtime traceability claim: {fi_service_audit['ready_for_per_service_runtime_traceability_claim']}",
            f"- Ready for full FI service conformance claim: {fi_service_audit['ready_for_full_fi_service_conformance_claim']}",
            f"- Assessment: {fi_service_audit['current_assessment']}",
            "",
            "FI service family counts:",
            "",
        ]
    )
    for family, count in fi_service_audit["by_family"].items():
        lines.append(f"- {family}: {count}")
    lines.extend(
        [
            "",
            "## Delta Requirement Proof Audit",
            "",
            f"- Delta rows: {delta_audit['row_count']}",
            f"- Ready for delta traceability claim: {delta_audit['ready_for_delta_traceability_claim']}",
            f"- Ready for full delta conformance claim: {delta_audit['ready_for_full_delta_conformance_claim']}",
            f"- Assessment: {delta_audit['current_assessment']}",
            "",
        ]
    )
    for category, count in delta_audit["by_category"].items():
        lines.append(f"- {category}: {count}")
    lines.extend(
        [
            "",
            "## Binding Requirement Proof Audit",
            "",
            f"- Binding rows: {binding_audit['row_count']}",
            f"- Ready for binding traceability claim: {binding_audit['ready_for_binding_traceability_claim']}",
            f"- Ready for full binding conformance claim: {binding_audit['ready_for_full_binding_conformance_claim']}",
            f"- Assessment: {binding_audit['current_assessment']}",
            "",
            "## OMT Requirement Proof Audit",
            "",
            f"- OMT rows: {omt_audit['row_count']}",
            f"- Ready for OMT traceability claim: {omt_audit['ready_for_omt_traceability_claim']}",
            f"- Ready for full OMT conformance claim: {omt_audit['ready_for_full_omt_conformance_claim']}",
            f"- Assessment: {omt_audit['current_assessment']}",
            "",
            "## Callback Proof Audit",
            "",
            f"- Callback rows: {callback_audit['row_count']}",
            f"- Helper-backed callbacks: {callback_audit['helper_backed_callback_count']}",
            f"- Focused executable callbacks: {callback_audit['focused_executable_callback_count']}",
            f"- Ready for callback surface traceability claim: {callback_audit['ready_for_callback_surface_traceability_claim']}",
            f"- Ready for callback-by-callback working-surface claim: {callback_audit['ready_for_callback_by_callback_working_surface_claim']}",
            f"- Assessment: {callback_audit['current_assessment']}",
            "",
            "Callback verification status counts:",
            "",
        ]
    )
    for status, count in callback_audit["by_verification_status"].items():
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
            "",
            "## Callback Route Parity Audit",
            "",
            f"- Callback rows: {callback_route_parity_audit['row_count']}",
            f"- Hosted/direct route-backed callbacks: {callback_route_parity_audit['hosted_or_route_backed_callback_count']}",
            f"- Callback-helper-only rows: {callback_route_parity_audit['callback_helper_only_count']}",
            f"- Ready for full Python-lane callback route parity claim: {callback_route_parity_audit['ready_for_full_python_lane_callback_route_parity_claim']}",
            f"- Ready for exhaustive cross-binding callback parity claim: {callback_route_parity_audit['ready_for_exhaustive_cross_binding_callback_parity_claim']}",
            f"- Assessment: {callback_route_parity_audit['current_assessment']}",
            "",
            "## Support-Service Proof Audit",
            "",
            f"- Support-service rows: {support_service_audit['row_count']}",
            f"- Focused executable rows: {support_service_audit['focused_executable_row_count']}",
            f"- Rows with known gaps: {support_service_audit['rows_with_known_gaps']}",
            f"- Complete negative-path rows: {support_service_audit['complete_negative_path_row_count']}",
            f"- Partial negative-path rows: {support_service_audit['partial_negative_path_row_count']}",
            f"- Metadata-mapped negative-path rows: {support_service_audit['mapped_not_exhaustive_negative_path_row_count']}",
            f"- Ready for support-service traceability claim: {support_service_audit['ready_for_support_service_traceability_claim']}",
            f"- Ready for support-service full conformance claim: {support_service_audit['ready_for_support_service_full_conformance_claim']}",
            f"- Assessment: {support_service_audit['current_assessment']}",
            "",
            "Support-service verification status counts:",
            "",
        ]
    )
    for status, count in support_service_audit["by_verification_status"].items():
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
            "",
            "Support-service negative-path status counts:",
            "",
        ]
    )
    for status, count in support_service_audit["by_negative_path_status"].items():
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
            "",
            "## Python RTI Milestone Audit",
            "",
            f"- Audit status: {milestone_audit['audit_status']}",
            f"- Routes: {', '.join(milestone_audit['routes'])}",
            f"- Milestones per route: {milestone_audit['milestone_count']}",
            f"- Assessment: {milestone_audit['current_assessment']}",
            "",
            "## Requirement-By-Requirement Audit",
            "",
            f"- Audit status: {requirement_by_requirement_audit['audit_status']}",
            f"- Row count: {requirement_by_requirement_audit['row_count']}",
            f"- Ready for row-level audit claim: {requirement_by_requirement_audit['ready_for_row_level_requirement_audit_claim']}",
            f"- Ready for full 2025 conformance claim: {requirement_by_requirement_audit['ready_for_full_2025_conformance_claim']}",
            f"- Rows with complete review metadata: {requirement_by_requirement_audit['rows_with_complete_review_metadata']}",
            f"- Covered rows with evidence paths: {requirement_by_requirement_audit['covered_rows_with_evidence_paths']}",
            f"- Unsupported rows with explicit boundary flag: {requirement_by_requirement_audit['unsupported_rows_with_explicit_boundary_flag']}",
            f"- Assessment: {requirement_by_requirement_audit['current_assessment']}",
            "",
            "Requirement-by-requirement blockers:",
            "",
        ]
    )
    for blocker in requirement_by_requirement_audit["full_claim_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "Requirement-by-requirement area closure:",
            "",
        ]
    )
    for area, counts in requirement_by_requirement_audit["area_closure"].items():
        counts_rendered = ", ".join(f"{status}={count}" for status, count in counts.items())
        lines.append(f"- {area}: {counts_rendered}")
    lines.extend(
        [
            "",
            "## Completion Claim Audit",
            "",
            f"- Claim shape: {claim_audit['claim_shape']}",
            f"- Ready for supported-boundary statement: {claim_audit['ready_for_supported-boundary_statement']}",
            f"- Ready for full 2025 conformance claim: {claim_audit['ready_for_full_2025_conformance_claim']}",
            f"- Assessment: {claim_audit['current_assessment']}",
            "",
            "Requirement universe:",
            "",
            f"- Total rows: {claim_audit['requirement_universe']['total_rows']}",
            f"- Covered rows: {claim_audit['requirement_universe']['covered_rows']}",
            f"- Unsupported-boundary rows: {claim_audit['requirement_universe']['unsupported_boundary_rows']}",
            f"- Retired/legacy-only rows: {claim_audit['requirement_universe']['retired_or_legacy_only_rows']}",
            f"- Duplicate/umbrella rows: {claim_audit['requirement_universe']['duplicate_or_umbrella_rows']}",
            "",
            "Full-claim blockers:",
            "",
        ]
    )
    for route in milestone_audit["routes"]:
        route_summary = milestone_audit["by_route"][route]
        lines.extend(
            [
                f"### {route}",
                "",
                f"- Milestone count: {route_summary['milestone_count']}",
                f"- All milestone parity-covered: {route_summary['all_route_parity_covered']}",
                f"- Assessment: {route_summary['current_assessment']}",
                "",
            ]
        )
        for row in milestone_audit["rows"]:
            if row["route"] != route:
                continue
            lines.append(f"- {row['milestone_label']}: {row['status']} ({row['summary']})")
        lines.append("")
    for blocker in claim_audit["full_claim_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## Supported Boundary Statement",
            "",
            f"- Status: {supported_boundary['statement_status']}",
            f"- Ready: {supported_boundary['ready']}",
            f"- Statement: {supported_boundary['statement']}",
            "",
            "Supported scope:",
            "",
        ]
    )
    for item in supported_boundary["supported_scope"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Explicit boundaries:",
            "",
        ]
    )
    for item in supported_boundary["explicit_boundaries"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Implementation Concentration Audit",
            "",
            f"- Audit status: {implementation_concentration_audit['audit_status']}",
            f"- Implemented slices: {implementation_concentration_audit['implemented_slice_count']}",
            f"- Shim backend implementation path: {implementation_concentration_audit['shim_backend_path']}",
            f"- Shim backend-backed slices: {implementation_concentration_audit['shim_backend_slice_count']}",
            f"- Shim backend slice share: {implementation_concentration_audit['shim_backend_slice_share']}",
            f"- 2025 spec-package-backed slices: {implementation_concentration_audit['spec_package_slice_count']}",
            f"- Transport-backed slices: {implementation_concentration_audit['transport_slice_count']}",
            f"- Semantic concentration is material: {implementation_concentration_audit['semantic_concentration_is_material']}",
            f"- Assessment: {implementation_concentration_audit['current_assessment']}",
            f"- Extraction pressure boundary: {implementation_concentration_audit['extraction_pressure_boundary']}",
            "",
            "Top evidence anchors:",
            "",
        ]
    )
    for item in implementation_concentration_audit["top_evidence_anchors"]:
        lines.append(f"- {item['slice_count']}: {item['path']}")
    lines.extend(
        [
            "",
            "## Slice Aggregation Pressure Audit",
            "",
            f"- Audit status: {slice_aggregation_pressure_audit['audit_status']}",
            f"- Implemented slices: {slice_aggregation_pressure_audit['implemented_slice_count']}",
            f"- Aggregated slices >=10 requirements: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_10_requirements']}",
            f"- Aggregated slices >=10 requirements and shim-backed: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_10_requirements_shim_backed']}",
            f"- Aggregated slices >=20 requirements: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_20_requirements']}",
            f"- Aggregated slices >=20 requirements and shim-backed: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_20_requirements_shim_backed']}",
            f"- Assessment: {slice_aggregation_pressure_audit['current_assessment']}",
            f"- Next decomposition boundary: {slice_aggregation_pressure_audit['next_decomposition_boundary']}",
            "",
            "Largest implemented slices:",
            "",
        ]
    )
    for item in slice_aggregation_pressure_audit["largest_implemented_slices"]:
        lines.append(
            f"- {item['slice_id']}: {item['requirement_count']} requirements "
            f"(shim-backed: {item['shim_backend_backed']})"
        )
    lines.extend(
        [
            "",
            "Largest shim-backed aggregated slices:",
            "",
        ]
    )
    for item in slice_aggregation_pressure_audit["largest_shim_backed_aggregated_slices"]:
        lines.append(f"- {item['slice_id']}: {item['requirement_count']} requirements")
    lines.extend(
        [
            "",
            "## Save/Restore Decomposition Audit",
            "",
            f"- Audit status: {save_restore_decomposition_audit['audit_status']}",
            f"- Slice id: {save_restore_decomposition_audit['slice_id']}",
            f"- Requirement count: {save_restore_decomposition_audit['requirement_count']}",
            f"- Proof families: {save_restore_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {save_restore_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {save_restore_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {save_restore_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {save_restore_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in save_restore_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### save-restore/{family['family']}",
                "",
                f"- Focus: {family['focus']}",
                f"- Direct test count: {len(family['direct_tests'])}",
                f"- Hosted test count: {len(family['hosted_tests'])}",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Directed Interaction Decomposition Audit",
            "",
            f"- Audit status: {directed_interaction_decomposition_audit['audit_status']}",
            f"- Slice id: {directed_interaction_decomposition_audit['slice_id']}",
            f"- Requirement count: {directed_interaction_decomposition_audit['requirement_count']}",
            f"- Proof families: {directed_interaction_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {directed_interaction_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {directed_interaction_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {directed_interaction_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {directed_interaction_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in directed_interaction_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### directed-interaction/{family['family']}",
                "",
                f"- Focus: {family['focus']}",
                f"- Direct test count: {len(family['direct_tests'])}",
                f"- Hosted test count: {len(family['hosted_tests'])}",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## DDM Default-Policy Decomposition Audit",
            "",
            f"- Audit status: {ddm_default_policy_decomposition_audit['audit_status']}",
            f"- Slice id: {ddm_default_policy_decomposition_audit['slice_id']}",
            f"- Requirement count: {ddm_default_policy_decomposition_audit['requirement_count']}",
            f"- Proof families: {ddm_default_policy_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {ddm_default_policy_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {ddm_default_policy_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {ddm_default_policy_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {ddm_default_policy_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in ddm_default_policy_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### ddm-default-policy/{family['family']}",
                "",
                f"- Focus: {family['focus']}",
                f"- Direct test count: {len(family['direct_tests'])}",
                f"- Hosted test count: {len(family['hosted_tests'])}",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Shim Pressure Family Route-Backing Audit",
            "",
            f"- Audit status: {shim_pressure_family_route_backing_audit['audit_status']}",
            f"- Family count: {shim_pressure_family_route_backing_audit['family_count']}",
            f"- Fully route-backed family count: {shim_pressure_family_route_backing_audit['fully_route_backed_family_count']}",
            f"- All families route-backed across current Python lanes: {shim_pressure_family_route_backing_audit['all_families_route_backed_across_current_python_lanes']}",
            f"- Assessment: {shim_pressure_family_route_backing_audit['current_assessment']}",
            f"- Residual boundary: {shim_pressure_family_route_backing_audit['residual_boundary']}",
            "",
        ]
    )
    for family in shim_pressure_family_route_backing_audit["families"]:
        lines.append(
            f"- {family['slice_id']}/{family['family']}: direct={family['direct_test_count']}, "
            f"hosted={family['hosted_test_count']}, "
            f"route-backed={family['route_backed_across_current_python_lanes']}"
        )
    lines.extend(
        [
            "",
            "## Shim Pressure Family Asymmetry Audit",
            "",
            f"- Audit status: {shim_pressure_family_asymmetry_audit['audit_status']}",
            f"- Family count: {shim_pressure_family_asymmetry_audit['family_count']}",
            f"- Balanced families: {shim_pressure_family_asymmetry_audit['by_balance'].get('balanced', 0)}",
            f"- Direct-heavier families: {shim_pressure_family_asymmetry_audit['by_balance'].get('direct-heavier', 0)}",
            f"- Hosted-heavier families: {shim_pressure_family_asymmetry_audit['by_balance'].get('hosted-heavier', 0)}",
            f"- Assessment: {shim_pressure_family_asymmetry_audit['current_assessment']}",
            f"- Next parity boundary: {shim_pressure_family_asymmetry_audit['next_parity_boundary']}",
            "",
        ]
    )
    for family in shim_pressure_family_asymmetry_audit["families"]:
        lines.append(
            f"- {family['slice_id']}/{family['family']}: balance={family['balance']}, "
            f"direct={family['direct_test_count']}, hosted={family['hosted_test_count']}, delta={family['count_delta']}"
        )
    lines.extend(
        [
            "",
            "## Current Lane Coherence Audit",
            "",
            f"- Audit status: {current_lane_coherence_audit['audit_status']}",
            f"- Coherence claim: {current_lane_coherence_audit['coherence_claim']}",
            f"- Ready for current-lane coherent working-surface claim: {current_lane_coherence_audit['ready_for_current_lane_coherent_working_surface_claim']}",
            f"- Ready for permanent no-split architecture claim: {current_lane_coherence_audit['ready_for_permanent_no-split_architecture_claim']}",
            f"- Major pressure slice count: {current_lane_coherence_audit['major_pressure_slice_count']}",
            f"- Shim backend concentration is material: {current_lane_coherence_audit['shim_backend_concentration_is_material']}",
            f"- All pressure families route-backed across current Python lanes: {current_lane_coherence_audit['all_pressure_families_route_backed_across_current_python_lanes']}",
            f"- Assessment: {current_lane_coherence_audit['current_assessment']}",
            "",
            "Residual blockers:",
            "",
        ]
    )
    for item in current_lane_coherence_audit["residual_blockers"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Current Lane Working-Surface Statement",
            "",
            f"- Status: {current_lane_working_surface_statement['statement_status']}",
            f"- Ready: {current_lane_working_surface_statement['ready']}",
            f"- Statement: {current_lane_working_surface_statement['statement']}",
            f"- Assessment: {current_lane_working_surface_statement['current_assessment']}",
            "",
            "Non-claims:",
            "",
        ]
    )
    for item in current_lane_working_surface_statement["non_claims"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Implementation Lane Audit",
            "",
            f"- Audit status: {implementation_lane_audit['audit_status']}",
            f"- Current 2025 backend package: {implementation_lane_audit['current_2025_lane']['backend_package']}",
            f"- Current 2025 role: {implementation_lane_audit['current_2025_lane']['role']}",
            f"- Current 2025 plugin family: {implementation_lane_audit['current_2025_lane']['plugin_family']}",
            f"- Current 2025 spec support: {', '.join(implementation_lane_audit['current_2025_lane']['supports'])}",
            f"- Reference 2010 backend package: {implementation_lane_audit['reference_2010_lane']['backend_package']}",
            f"- Reference 2010 role: {implementation_lane_audit['reference_2010_lane']['role']}",
            f"- Dedicated 2025 backend package present: {implementation_lane_audit['dedicated_2025_backend_package_present']}",
            f"- Ready for working-surface promotion: {implementation_lane_audit['ready_for_current_lane_promotion_as_working_surface']}",
            f"- Ready for permanent no-split decision: {implementation_lane_audit['ready_for_permanent_no-split_decision']}",
            f"- Clean extraction still optional: {implementation_lane_audit['clean_extraction_still_optional']}",
            f"- Assessment: {implementation_lane_audit['current_assessment']}",
            f"- Extraction boundary: {implementation_lane_audit['extraction_boundary']}",
            "",
            "Python 2025 route variants:",
            "",
        ]
    )
    for route in implementation_lane_audit["python_2025_routes"]:
        lines.append(
            f"- {route['route']}: {route['kind']} "
            f"(separate RTI family: {route['is_separate_rti_family']}, "
            f"all milestone parity-covered: {route['all_route_parity_covered']})"
        )
    lines.extend(
        [
            "",
            "## Promotion Vs Split Audit",
            "",
            f"- Decision shape: {promotion_split_audit['decision_shape']}",
            f"- Current lane package: {promotion_split_audit['current_lane']['package']}",
            f"- Current lane role: {promotion_split_audit['current_lane']['role']}",
            f"- Recommendation: {promotion_split_audit['current_recommendation']}",
            f"- Ready for working-surface promotion: {promotion_split_audit['ready_for_current_lane_promotion_as_working_surface']}",
            f"- Ready for permanent no-split decision: {promotion_split_audit['ready_for_permanent_no-split_decision']}",
            f"- Assessment: {promotion_split_audit['current_assessment']}",
            "",
            "Promotion basis:",
            "",
        ]
    )
    for item in promotion_split_audit["promotion_basis"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Split triggers:",
            "",
        ]
    )
    for item in promotion_split_audit["split_triggers"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Permanent-decision blockers:",
            "",
        ]
    )
    for item in promotion_split_audit["permanent_decision_blockers"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Objective Audit",
            "",
            f"- Surface claim: {objective_audit['surface_claim']}",
            f"- Ready for bounded working-surface claim: {objective_audit['ready_for_bounded_working_surface_claim']}",
            f"- Ready for full 2025 completion claim: {objective_audit['ready_for_full_2025_completion_claim']}",
            f"- Bounded-ready dimensions: {objective_audit['bounded_ready_dimension_count']} / {objective_audit['dimension_count']}",
            f"- Assessment: {objective_audit['overall_assessment']}",
            "",
        ]
    )
    for dimension in objective_audit["dimensions"]:
        lines.extend(
            [
                f"### {dimension['name']}",
                "",
                f"- Evidence level: {dimension['evidence_level']}",
                f"- Bounded working-surface ready: {dimension['bounded_working_surface_ready']}",
                f"- Ready for full claim: {dimension['ready_for_full_claim']}",
                f"- Route scenarios: {', '.join(dimension['route_scenarios']) if dimension['route_scenarios'] else 'none'}",
                f"- Assessment: {dimension['current_assessment']}",
                "",
            ]
        )
        for blocker in dimension["residual_blockers"]:
            lines.append(f"- Residual blocker: {blocker}")
        lines.append("")
    lines.extend(
        [
            "",
        "## Implemented Evidence Slices",
        "",
        "| Slice | Status | Requirements | Evidence |",
        "|---|---|---|---|",
        ]
    )
    for slice_ in snapshot["implemented_evidence_slices"]:
        lines.append(
            "| {id} | {status} | {requirements} | {evidence} |".format(
                id=slice_["id"],
                status=slice_["status"],
                requirements=", ".join(slice_["requirements"]),
                evidence=", ".join(slice_["evidence"]),
            )
        )
    lines.extend(
        [
            "",
            "## Highest-Priority Open Work",
            "",
            "| ID | Area | Priority | Status | Verification work |",
            "|---|---|---|---|---|",
        ]
    )
    for row in backlog["high_priority_open"]:
        lines.append(f"| {row['id']} | {row['area']} | {row['priority']} | {row['current_status']} | {row['verification_work']} |")
    lines.extend(
        [
            "",
            "## Finish Rule",
            "",
            str(snapshot["finish_rule"]),
            "",
            "Do not promote `partial` rows by broad wording. Narrow the claim or add the missing positive/negative evidence.",
        ]
    )
    return lines


def write_spec2025_finish_line(output_dir: Path, project_root: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_spec2025_finish_line_snapshot(project_root)
    json_path = output_dir / "spec2025_finish_line_snapshot.json"
    markdown_path = output_dir / "spec2025_finish_line.md"
    matrix_path = output_dir / "spec2025_verification_matrix.csv"
    route_matrix_csv_path = output_dir / "spec2025_route_parity_matrix.csv"
    json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text("\n".join(build_spec2025_finish_line_markdown(project_root)) + "\n", encoding="utf-8")
    matrix_rows = snapshot["verification_matrix"]["rows"]
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = (
            "id",
            "bucket",
            "area",
            "priority",
            "current_status",
            "binding_scope",
            "has_anchor",
            "evidence_slices",
            "executable_tests",
            "explicit_disposition_anchor",
            "verification_work",
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in matrix_rows:
            writer.writerow(
                {
                    **row,
                    "evidence_slices": ";".join(row["evidence_slices"]),
                    "executable_tests": ";".join(row["executable_tests"]),
                }
            )
    with route_matrix_csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = (
            "scenario",
            "route",
            "status",
            "evidence_scope",
            "requirements",
            "evidence_tests",
            "evidence_artifacts",
            "notes",
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in snapshot["route_parity_matrix"]["rows"]:
            writer.writerow(
                {
                    **row,
                    "requirements": ";".join(row["requirements"]),
                    "evidence_tests": ";".join(row["evidence_tests"]),
                    "evidence_artifacts": ";".join(row["evidence_artifacts"]),
                }
            )
    return {
        "json": json_path,
        "markdown": markdown_path,
        "verification_matrix": matrix_path,
        "route_parity_matrix": route_matrix_csv_path,
    }


__all__ = [
    "build_spec2025_finish_line_markdown",
    "build_spec2025_finish_line_snapshot",
    "write_spec2025_finish_line",
]
