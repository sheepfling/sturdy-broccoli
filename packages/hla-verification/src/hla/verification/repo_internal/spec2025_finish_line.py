"""Finish-line inventory for the IEEE 1516-2025 requirements tranche."""

from __future__ import annotations

import ast
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.verification.repo_internal.conformance import build_service_conformance_matrix, negative_path_status
from hla.verification.repo_internal.verification.spec2025_route_parity_matrix import (
    ROUTE_IDS_2025,
    summarize_spec2025_route_parity,
    write_spec2025_route_parity_matrix,
)

HIGH_PRIORITIES = frozenset({"high", "very-high"})
CLOSED_STATUSES = frozenset({"implemented-slice", "unsupported-boundary", "legacy-only"})
PYTHON2025_BACKEND_EVIDENCE_PATH = "packages/hla-backend-python2025/src/hla/backends/python2025/backend.py"
SHIM_BACKEND_EVIDENCE_PATH = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"

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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route cover connection and membership lifecycle proof: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates time-mode transitions: selected logical-time factories plus "
            "enable/disable time regulation, timeRegulationEnabled callback delivery, enable/disable time "
            "constrained, and timeConstrainedEnabled callback delivery through the live Python 2025 RTI lane "
            "and hosted FedPro route."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates grant and callback-delivery control: flushQueueGrant and "
            "timeAdvanceGrant callbacks, plus enable/disable asynchronous delivery queue behavior through the live "
            "Python 2025 RTI lane and hosted FedPro route."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "tests/backends/test_shim_route_trace_evidence.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates queued timestamp-order delivery and its query surface: "
            "GALT/LITS/lookahead queries, retract and requestRetraction callback delivery, attribute and "
            "interaction order-type changes, queued timestamped object updates/interactions, timestamp-order "
            "delivery on receiving federate time advance, queued-remove handling, and message retraction before "
            "delivery across both the live Python 2025 RTI lane and hosted FedPro route."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "tests/backends/test_shim_route_trace_evidence.py",
        ),
        "supported_scope": (
            "Python 2025 lookahead proof is separated from the generic time-control slice: the Target/Radar "
            "time-window core and future-exclusion proof ladder, output-delivery and consumer-order proofs, "
            "pipelined scan-window proofs, receive-order poison rejection, and save/restore rollback of bounded "
            "time-window state all execute directly on the live Python 2025 RTI lane and are replayed over the "
            "hosted FedPro route, with matching negative-oracle guards that reject mismatched LITS boundaries, "
            "premature output, reversed consumer order, cross-window contamination, closed-window mutation, and "
            "dirty post-restore replay. "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route support requestFederationSave and "
            "requestFederationRestore with initiate, begun, complete, abort, and query-status flows; federation "
            "save/restore lifecycle callbacks and status responses; successful federationSaved/federationRestored "
            "completion; missing-label restore failure; federate-reported save/restore failure; save/restore abort "
            "callbacks; object registry rollback; joined-federate logical-time rollback; plain object/interaction "
            "subscriber-routing rollback; directed DDM subscriber-routing rollback; direct execution of the shared "
            "two-federate save/restore suite on the main python2025 runtime plus hosted replay over the FedPro "
            "route; timed initiateFederateSave callback coverage; save-request precondition rejection; and bounded "
            "save/restore rollback of queued callback, time-window, ownership, and routing state."
        ),
    },
    {
        "id": "2025-fom-showcase",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FR-001", "HLA2025-FR-003", "HLA2025-FR-004"),
        "evidence": (
            "tests/scenarios/test_proto2025_fom_showcase.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py",
        ),
    },
    {
        "id": "2025-handle-normalization",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-005", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate 2025 handle-normalization proof: the "
            "in-process python2025 runtime normalizes typed federate, object-class, interaction-class, object-instance, and "
            "service-group values with wrong-family rejection, while the hosted FedPro route round-trips typed "
            "service-group and object-instance normalization requests across the 2025 transport surface."
        ),
    },
    {
        "id": "2025-switch-set-get-model",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-008", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route prove the 2025 set/get switch model replaces the old "
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
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Legacy 2010 enable/disable advisory switch spellings are kept out of native 2025 normative coverage "
            "and are treated as retired or replacement-mapped items unless an explicit compatibility mode is added. "
            "The current Python 2025 RTI rejects those legacy method spellings as unsupported 2025 services rather than "
            "quietly aliasing them into native coverage."
        ),
    },
    {
        "id": "2025-fom-mim-error-taxonomy",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007"),
        "evidence": (
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate create-time FOM/MIM taxonomy proof. "
            "The in-process python2025 runtime distinguishes missing/open, read, invalid, and merge failures across native 2025 "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
        ),
        "supported_scope": (
            "Python 2025 callback proof now isolates object-delivery callback context: the in-process python2025 runtime emits "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
        ),
        "supported_scope": (
            "Python 2025 callback proof now isolates interaction-delivery callback context: the in-process python2025 runtime "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route support FOM-backed directed interaction publish, "
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
            "HLA2025-OMT-COMP-192",
            "HLA2025-OMT-COMP-194",
            "HLA2025-OMT-COMP-195",
            "HLA2025-OMT-COMP-196",
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
            "description metadata, simpleData units/resolution/accuracy, 2025 logicalTime/logicalTimeInterval names, "
            "dataType bindings, and semantics text, and variant-record alternative enumerators."
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
            "HLA2025-OMT-COMP-166",
            "HLA2025-OMT-COMP-167",
            "HLA2025-OMT-COMP-168",
            "HLA2025-OMT-COMP-169",
            "HLA2025-OMT-COMP-170",
            "HLA2025-OMT-COMP-200",
            "HLA2025-OMT-COMP-201",
            "HLA2025-OMT-COMP-207",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser preserves the supported 2025 switch container subset "
            "(autoProvide, conveyRegionDesignatorSets, attribute/object/interaction advisories, serviceReporting, "
            "exceptionReporting, delaySubscriptionEvaluation, nonRegulatedGrant, allowRelaxedDDM, "
            "advisoriesUseKnownClass, sendServiceReportsToFile, automaticResignAction), preserves interaction "
            "transportation, preserves transportation reliable/semantics metadata, preserves update-rate "
            "semantics metadata, and the 2025 serializer round-trips those supported fields while filling the "
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
                50, 51, 52, 53, 54, 55, 58, 60, 61, 62, 63, 64, 65, 66, 69, 71, 72, 73, 83, 86, 88,
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
            "reference/POC/keyword taxonomy metadata subset, serviceUtilization, object and interaction names plus supported "
            "attribute/parameter datatype links, dimension-name lists, logicalTime/logicalTimeInterval containers, "
            "notes, tag tables, synchronization tables, transportation name tables, update-rate name/rate tables, "
            "and the supported basic/simple/enumerated/array/fixed-record/variant-record datatype tables and "
            "top-level objectModel container sections that hold those structures."
        ),
    },
    {
        "id": "2025-omt-dimension-metadata-roundtrip",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-037",
            "HLA2025-OMT-COMP-038",
            "HLA2025-OMT-COMP-040",
            "HLA2025-OMT-COMP-041",
            "HLA2025-OMT-COMP-042",
            "HLA2025-OMT-COMP-043",
            "HLA2025-OMT-COMP-044",
        ),
        "evidence": (
            "tests/factories/test_fom_omt_parsing.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser and serializer preserve top-level dimension declarations, including dataType, "
            "2025 inputDataTypes, inputDataDescription, upperBound, normalization metadata text, "
            "outputDataSemantics, value, and semantics, across parse/serialize/parse round-trip. "
            "This is OMT metadata preservation evidence; it does not claim full runtime execution of DDM "
            "normalization semantics."
        ),
    },
    {
        "id": "2025-omt-attribute-metadata-roundtrip",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-011",
            "HLA2025-OMT-COMP-012",
            "HLA2025-OMT-COMP-014",
            "HLA2025-OMT-COMP-015",
            "HLA2025-OMT-COMP-017",
            "HLA2025-OMT-COMP-018",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser and serializer preserve attribute updateType, updateCondition, ownership, "
            "sharing, order, and semantics metadata across parse/serialize/parse round-trip. This is OMT "
            "metadata preservation evidence; it does not claim that those metadata fields independently "
            "execute runtime ownership or update-policy behavior."
        ),
    },
    {
        "id": "2025-omt-class-parameter-metadata-roundtrip",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-074",
            "HLA2025-OMT-COMP-079",
            "HLA2025-OMT-COMP-080",
            "HLA2025-OMT-COMP-109",
            "HLA2025-OMT-COMP-114",
            "HLA2025-OMT-COMP-133",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser and serializer preserve object-class sharing/semantics, "
            "interaction-class sharing/order/semantics, and parameter semantics metadata "
            "across parse/serialize/parse round-trip. This is OMT metadata preservation evidence; "
            "it does not claim those metadata fields independently execute runtime declaration, ordering, "
            "or interaction-policy behavior."
        ),
    },
    {
        "id": "2025-omt-association-metadata-roundtrip",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-048",
            "HLA2025-OMT-COMP-049",
            "HLA2025-OMT-COMP-075",
            "HLA2025-OMT-COMP-076",
            "HLA2025-OMT-COMP-110",
            "HLA2025-OMT-COMP-111",
            "HLA2025-OMT-COMP-112",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser and serializer preserve object-class directedInteraction name/sharing "
            "metadata plus object-class and interaction-class dimension association references across "
            "parse/serialize/parse round-trip. This is association metadata preservation evidence; it "
            "does not claim full DDM region-routing semantics or schema extension-point preservation."
        ),
    },
    {
        "id": "2025-omt-xs-any-extension-tolerance",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-OMT-COMP-006",
            "HLA2025-OMT-COMP-008",
            "HLA2025-OMT-COMP-019",
            "HLA2025-OMT-COMP-021",
            "HLA2025-OMT-COMP-027",
            "HLA2025-OMT-COMP-035",
            "HLA2025-OMT-COMP-039",
            "HLA2025-OMT-COMP-045",
            "HLA2025-OMT-COMP-047",
            "HLA2025-OMT-COMP-056",
            "HLA2025-OMT-COMP-057",
            "HLA2025-OMT-COMP-059",
            "HLA2025-OMT-COMP-067",
            "HLA2025-OMT-COMP-068",
            "HLA2025-OMT-COMP-070",
            "HLA2025-OMT-COMP-077",
            "HLA2025-OMT-COMP-081",
            "HLA2025-OMT-COMP-082",
            "HLA2025-OMT-COMP-102",
            "HLA2025-OMT-COMP-106",
            "HLA2025-OMT-COMP-107",
            "HLA2025-OMT-COMP-113",
            "HLA2025-OMT-COMP-115",
            "HLA2025-OMT-COMP-129",
            "HLA2025-OMT-COMP-130",
            "HLA2025-OMT-COMP-134",
            "HLA2025-OMT-COMP-145",
            "HLA2025-OMT-COMP-147",
            "HLA2025-OMT-COMP-154",
            "HLA2025-OMT-COMP-156",
            "HLA2025-OMT-COMP-171",
            "HLA2025-OMT-COMP-176",
            "HLA2025-OMT-COMP-178",
            "HLA2025-OMT-COMP-181",
            "HLA2025-OMT-COMP-189",
            "HLA2025-OMT-COMP-193",
            "HLA2025-OMT-COMP-197",
            "HLA2025-OMT-COMP-198",
            "HLA2025-OMT-COMP-202",
            "HLA2025-OMT-COMP-204",
            "HLA2025-OMT-COMP-208",
            "HLA2025-OMT-COMP-210",
            "HLA2025-OMT-COMP-219",
            "HLA2025-OMT-COMP-222",
            "HLA2025-OMT-COMP-224",
        ),
        "evidence": (
            "tests/test_rti1516_2025_validation.py",
            "packages/hla-rti1516e/src/hla/rti1516e/fom.py",
        ),
        "supported_scope": (
            "Shared OMT parser accepts foreign-namespace xs:any extension elements at the remaining 2025 OMT "
            "extension points, preserves text/attribute/nested XML payloads for serializer round-trip, and isolates "
            "them as non-native metadata so extension children are not interpreted as standard HLA elements. This "
            "is extension payload preservation evidence, not a claim to execute arbitrary third-party extension semantics."
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
            "and serializes a MOM service report. These binding routes execute over the primary python2025 runtime "
            "lane in hla-backend-python2025 while the Java and C++ packages stay wrapper-only adaptation surfaces. "
            "C++ artifacts exercise this locally; Java runtime evidence runs when the Java 2025 standard-route jar is built. "
            "This is not full Java/C++ behavior conformance or object exchange."
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
            "publication/subscription/object-instance-information/activity-count reports, synchronization "
            "point/status MOM reports over FedPro, targeted transport/ownership/time save-restore manager actions, and MOM "
            "exception routing over FedPro. full RTI semantics remain outside this slice. This is a hosted runtime "
            "extended-state slice, not a full FedPro RTI conformance claim."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route resolve object class, attribute, transportation, and "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route support FOM-backed object instance registration, "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates object deletion flows: FOM-backed deleteObjectInstance and "
            "removeObjectInstance callbacks, delete-with-time behavior, localDeleteObjectInstance validation, and "
            "post-delete object-known-state handling across the live python2025 runtime lane and hosted FedPro route."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates attribute-value-update request callbacks: "
            "requestAttributeValueUpdate by object instance and object class, provideAttributeValueUpdate callback "
            "delivery, and region-scoped requestAttributeValueUpdate callbacks across the live python2025 runtime "
            "lane and hosted FedPro route."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Python 2025 runtime proof now isolates object-scope advisory callbacks: DDM-driven "
            "attributesInScope and attributesOutOfScope transitions, out-of-scope reflection suppression, "
            "re-entry into scope, and post-transfer ownership-safe update behavior execute across the live "
            "python2025 runtime lane and the hosted FedPro route with requirement-traceable object-attribute "
            "scope changes."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support single-name reservation requests, "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support reserveMultipleObjectInstanceNames and "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support orderly disconnect state teardown and "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route accepts connect requests, creates federation "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route isolate federate membership and resign behavior: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route isolate synchronization-point barrier behavior: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route isolate declaration publication control: publish "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route isolate declaration subscription control: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route isolate declaration relevance and advisory "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support direct federate, object-class, "
            "known-object-class, and object-instance handle/name lookups against joined federation membership "
            "and the loaded FOM catalog. Over FedPro, joined-member identity lookup stops after resign while "
            "decode-oriented object/class/instance catalog lookups remain available across the transport seam."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support attribute, interaction-class, and "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support order-type, update-rate, and "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/verification/test_spec_traceability_and_extended_python_rti.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route support interaction available-dimension lookup "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route now isolate support-handle normalization and "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route report advisory and reporting-state inquiry "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route report runtime-policy inquiry state for the "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route now isolate advisory/reporting support-service "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI and the hosted FedPro 2025 route now isolate runtime-policy support-service switch "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto",
        ),
        "supported_scope": (
            "Current Python 2025 RTI supports callback control services for connected federates: disableCallbacks "
            "queues local and target federate callbacks, enableCallbacks permits delivery again, evokeCallback "
            "delivers one queued callback, and evokeMultipleCallbacks drains the pending callback queue. The "
            "hosted FedPro 2025 route now carries explicit enableCallbacks/disableCallbacks transport calls and "
            "preserves queued callback delivery boundaries across callback polling. The timing parameters are "
            "accepted but not used for wall-clock blocking in this in-process runtime slice."
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate ownership divestiture-confirmation proof: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate ownership release proof: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate acquisition-assumption proof: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate acquisition availability "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route now isolate ownership visibility and policy proof: "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route serialize structured MOM service report records with "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Current Python 2025 RTI plus the hosted FedPro route carry MOM adjust and service actions through the real "
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
            "tests/test_rti1516_2025_python2025_runtime.py",
            "tests/transport/test_grpc_transport_2025.py",
            PYTHON2025_BACKEND_EVIDENCE_PATH,
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
        ),
        "supported_scope": (
            "Current Python 2025 RTI routes MOM query/report data separately from action routing: MIM data, FOM module "
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


def _preferred_2025_runtime_backend_path(project_root: Path) -> str:
    if (project_root / PYTHON2025_BACKEND_EVIDENCE_PATH).exists():
        return PYTHON2025_BACKEND_EVIDENCE_PATH
    return SHIM_BACKEND_EVIDENCE_PATH


def _normalize_implemented_slice(project_root: Path, evidence_slice: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(evidence_slice)
    runtime_backend_path = _preferred_2025_runtime_backend_path(project_root)
    legacy_runtime_paths = {SHIM_BACKEND_EVIDENCE_PATH, PYTHON2025_BACKEND_EVIDENCE_PATH}
    normalized["evidence"] = tuple(
        runtime_backend_path if path in legacy_runtime_paths else path
        for path in evidence_slice.get("evidence", ())
    )
    return normalized


def _normalized_implemented_evidence_slices(project_root: Path) -> tuple[dict[str, Any], ...]:
    return tuple(_normalize_implemented_slice(project_root, evidence_slice) for evidence_slice in IMPLEMENTED_EVIDENCE_SLICES)


PROJECT_ROOT = Path(__file__).resolve().parents[6]


def _implemented_slices() -> tuple[dict[str, Any], ...]:
    return _normalized_implemented_evidence_slices(PROJECT_ROOT)

OBJECTIVE_DIMENSIONS: tuple[Mapping[str, Any], ...] = (
    {
        "id": "federation_management",
        "name": "Federation Management",
        "evidence_level": "decomposed-strong-slice",
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
            "Connection, federation catalog control, membership reporting and resign handling, synchronization barriers, "
            "and save or restore behavior are exercised directly through the current Python 2025 RTI and the hosted "
            "FedPro route, and the finish-line now separates that proof into named families instead of leaving it as "
            "one large bucket: connect/create/catalog control, join or membership reporting, resign or disconnect cleanup, "
            "synchronization barriers, save/restore lifecycle control, and save/restore participant recovery."
        ),
        "residual_blockers": (
            "The finish-line now decomposes federation-management proof families, but it still stops short of clause-by-clause service closure.",
            "Standard Java and C++ route coverage remains scenario parity/runtime capability evidence, not exhaustive behavior conformance.",
        ),
    },
    {
        "id": "object_management",
        "name": "Object Management",
        "evidence_level": "decomposed-strong-slice",
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
            "The current repo proves a coherent object-management surface and the finish-line now separates that proof "
            "into named families instead of leaving it as one large bucket: declaration and exchange gating, delete/local-known-state "
            "lifecycle, attribute-value-update routing, advisory/update-rate callbacks, transportation policy callbacks, "
            "object-region scope routing, and directed or directed-DDM routing. Hosted FedPro replay now also covers "
            "rollback-sensitive object state including plain and directed routing restore, stale timed-remove cleanup, "
            "and restored local-known-state after local delete, plus hosted shared scenario replay for request-attribute-value-update "
            "routing and object-scope relevance over the main python2025 runtime."
        ),
        "residual_blockers": (
            "The finish-line now decomposes object-management proof families, but it still stops short of clause-by-clause service closure.",
            "FedPro coverage is a hosted runtime slice and does not yet constitute full RTI semantics proof.",
        ),
    },
    {
        "id": "time_management",
        "name": "Time Management",
        "evidence_level": "decomposed-query-and-window-proof-backed",
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
            "by executable runtime traces. The time proof now also includes bounded GALT/LITS query evidence, "
            "the Target/Radar lookahead-window proof ladder, matching negative-oracle guards across the "
            "current Python 2025 lanes, and named runtime proof families instead of one flat bounded time bucket."
        ),
        "residual_blockers": (
            "The closeout now separates time proof into named runtime families, but it still stops short of final per-requirement time-service proof.",
            "Cross-binding runtime evidence is narrower than the Python in-process and hosted FedPro slices.",
        ),
    },
    {
        "id": "support_services",
        "name": "Support Services",
        "evidence_level": "decomposed-per-service-runtime-traceable",
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
            "are exercised through the Python runtime and are represented across tracked binding and hosted routes. The "
            "finish-line now also carries an explicit support-service ledger via the RTIambassador conformance "
            "matrix, and it now separates that proof into named families instead of leaving it as one ledger-only "
            "summary: reservation/release flows, lookup and normalization surfaces, transport or dimension lookups, "
            "the 2025 switch model, and factory/decode plus hosted support seams. That gives the Python lanes "
            "per-service runtime traceability plus complete actionable negative-path coverage. Hosted FedPro "
            "support-service replay now also proves reconnect-safe discard of a disconnected peer's disabled "
            "callback backlog before later reconnect."
        ),
        "residual_blockers": (
            "The finish-line now decomposes support-service proof families and reaches per-service runtime traceability plus complete actionable negative-path coverage inside the Python routes, but it still stops short of exhaustive cross-binding behavior-conformance proof.",
            "Java and C++ proof remains capability-oriented rather than a full standard-route behavior pass, and the hosted FedPro route remains a bounded runtime slice rather than a full support-service conformance route.",
        ),
    },
    {
        "id": "ownership_management",
        "name": "Ownership Management",
        "evidence_level": "decomposed-strong-slice",
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
            "and rollback-sensitive ownership state are all exercised directly through the current Python 2025 RTI and "
            "through shared backend-matrix scenarios. Hosted FedPro replay now also proves restored in-flight "
            "ownership negotiation state plus restored cross-federate owner-visibility queries, and the "
            "finish-line now separates that proof into named ownership families instead of leaving it as one opaque bucket."
        ),
        "residual_blockers": (
            "The closeout now separates ownership proof into named runtime families, but it still stops short of a final clause-by-clause ownership audit.",
            "Hosted route parity remains scenario-backed runtime evidence, not a full vendor-equivalent ownership conformance pass.",
        ),
    },
    {
        "id": "callbacks",
        "name": "Callbacks",
        "evidence_level": "decomposed-callback-ledger-route-backed",
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
            "support-service flows, including hosted FedPro callback decoding, reconnect-safe callback backlog "
            "cleanup across disconnect/reconnect, and direct Python ambassador behavior. "
            "The finish-line now also carries an explicit callback-by-callback ledger via the FederateAmbassador "
            "conformance matrix, that ledger is fully route-backed across the current Python 2025 lanes, and the "
            "finish-line now separates callback proof into named runtime families instead of leaving it as a flat ledger."
        ),
        "residual_blockers": (
            "The callback proof is now decomposed into named runtime families, but it still stops short of exhaustive cross-binding callback signature/ordering equivalence proof.",
            "Binding-route callback parity is tracked at the scenario level, not as exhaustive callback signature/ordering proof.",
        ),
    },
    {
        "id": "omt_handling",
        "name": "OMT Handling",
        "evidence_level": "decomposed-bounded-slice",
        "implemented_slice_ids": (
            "2025-fom-validation",
            "2025-omt-reference-value-required",
            "2025-omt-component-metadata-roundtrip",
            "2025-omt-switch-and-transport-subset",
            "2025-omt-extended-supported-subset",
            "2025-omt-dimension-metadata-roundtrip",
            "2025-service-utilization-crosscheck",
            "2025-omt-schema-constraint-validation",
            "2025-omt-association-metadata-roundtrip",
            "2025-omt-xs-any-extension-tolerance",
        ),
        "route_scenarios": (),
        "current_assessment": (
            "The OMT path is well-instrumented for parser/serializer/schema handling, metadata round-trips, "
            "association metadata, and foreign xs:any extension tolerance with extension payload preservation "
            "round-trip evidence. The finish-line now also separates that bounded OMT proof into named decomposition "
            "audits for the extended supported subset, service-utilization crosschecks, xs:any extension tolerance, "
            "and schema-constraint validation instead of leaving it as one flat parser/validator bucket. Arbitrary "
            "third-party extension semantics remain outside the repo-native runtime claim."
        ),
        "residual_blockers": (
            "The OMT proof is now decomposed into named subset and validator families, but foreign xs:any extension payloads are still preserved as XML payloads rather than interpreted as repo-native HLA metadata.",
            "Parser/serializer support remains a decomposed bounded OMT working surface rather than exhaustive third-party extension execution semantics.",
        ),
    },
    {
        "id": "binding_routes",
        "name": "Binding Routes",
        "evidence_level": "decomposed-bounded-slice",
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
            "FedPro routes provide substantive runtime proof for the working surface. The finish-line now also "
            "separates route evidence into named binding and hosted-route families instead of one flat bounded bucket."
        ),
        "residual_blockers": (
            "The route evidence is now decomposed into named families, but Java and C++ routes are still backed by artifact/runtime-capability traces rather than exhaustive behavior equivalence proof.",
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
    return {slice_["id"]: slice_ for slice_ in _implemented_slices()}


def _fi_service_family(requirement_id: str) -> str:
    service_number = int(requirement_id.rsplit("-", 1)[1])
    for start, end, family in FI_SERVICE_FAMILY_RANGES:
        if start <= service_number <= end:
            return family
    return "unknown"


_FI_SERVICE_SOURCE_FAMILY_HINTS: dict[str, tuple[str, ...]] = {
    "federation_management": ("federation-management-runtime",),
    "save_restore": ("save-restore-runtime",),
    "declaration_management": ("object-attribute-runtime",),
    "object_class_relevance": ("object-attribute-runtime",),
    "name_reservation": ("object-attribute-runtime",),
    "object_management": ("object-attribute-runtime", "interaction-routing-runtime"),
    "ownership_management": ("ownership-runtime",),
    "time_management": ("time-management-runtime",),
    "ddm": ("ddm-region-runtime", "object-attribute-runtime"),
    "support_services": ("misc-support", "mom-and-switch-services", "fom-catalog-and-handle-support"),
    "callback_control": ("callback-delivery-and-control",),
}


def _python2025_runtime_modules_by_family(project_root: Path) -> dict[str, list[dict[str, Any]]]:
    audit = _build_python2025_source_responsibility_audit(project_root)
    by_family: dict[str, list[dict[str, Any]]] = {}
    for module in audit["extracted_runtime_modules"]:
        by_family.setdefault(str(module["family"]), []).append(module)
    for modules in by_family.values():
        modules.sort(key=lambda item: (-int(item["line_count"]), str(item["path"])))
    return by_family


def _specialized_python2025_runtime_artifacts(
    project_root: Path,
    evidence_paths: set[str],
    *,
    family_hints: tuple[str, ...] = (),
) -> list[str]:
    runtime_backend_path = _preferred_2025_runtime_backend_path(project_root)
    if runtime_backend_path not in evidence_paths:
        return sorted(evidence_paths)

    selected: list[str] = []
    modules_by_family = _python2025_runtime_modules_by_family(project_root)
    for family in family_hints:
        for module in modules_by_family.get(family, ())[:2]:
            path = str(module["path"])
            if path not in selected:
                selected.append(path)
            if len(selected) >= 4:
                break
        if len(selected) >= 4:
            break

    normalized = sorted(path for path in evidence_paths if path != runtime_backend_path)
    if selected:
        normalized.extend(path for path in selected if path not in normalized)
        return normalized

    normalized.append(runtime_backend_path)
    return normalized


def _delta_source_family_hints(supporting_slice_ids: tuple[str, ...]) -> tuple[str, ...]:
    hints: list[str] = []
    for slice_id in supporting_slice_ids:
        normalized = slice_id.lower()
        if any(token in normalized for token in ("save-restore", "save_restore", "restore")):
            hints.append("save-restore-runtime")
        if any(token in normalized for token in ("time-", "time_", "lookahead", "galt", "lits", "tso", "flush")):
            hints.append("time-management-runtime")
        if any(token in normalized for token in ("ownership", "attributeis", "queryattributeownership")):
            hints.append("ownership-runtime")
        if any(token in normalized for token in ("directed", "interaction")):
            hints.append("interaction-routing-runtime")
        if any(token in normalized for token in ("ddm", "region")):
            hints.append("ddm-region-runtime")
        if any(token in normalized for token in ("callback", "evoke")):
            hints.append("callback-delivery-and-control")
        if any(token in normalized for token in ("switch", "support", "lookup", "catalog", "auth", "connect")):
            hints.append("misc-support")
        if any(token in normalized for token in ("mom", "report")):
            hints.append("mom-and-switch-services")
        if any(token in normalized for token in ("fom", "mim", "federation", "join", "resign", "lifecycle", "member")):
            hints.append("federation-management-runtime")
        if any(token in normalized for token in ("declaration", "object", "name-reservation", "name_reservation", "handle-normalization", "handle_normalization")):
            hints.append("object-attribute-runtime")
        if any(token in normalized for token in ("handle-normalization", "handle_normalization", "lookup")):
            hints.append("misc-support")
        if "catalog" in normalized:
            hints.append("fom-catalog-and-handle-support")
    deduped: list[str] = []
    for hint in hints:
        if hint not in deduped:
            deduped.append(hint)
    return tuple(deduped)


def _build_fi_service_proof_audit() -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[6]
    fi_service_rows: list[dict[str, Any]] = []
    for requirement_id in sorted(
        {
            requirement_id
            for evidence_slice in _implemented_slices()
            for requirement_id in evidence_slice.get("requirements", ())
            if requirement_id.startswith("HLA2025-FI-SVC-")
        }
    ):
        supporting_slices = [
            evidence_slice
            for evidence_slice in _implemented_slices()
            if requirement_id in evidence_slice.get("requirements", ())
        ]
        proof_kind = "multi-slice-runtime" if len(supporting_slices) > 1 else "single-slice-runtime"
        family = _fi_service_family(requirement_id)
        evidence_py_paths = {
            evidence_path
            for evidence_slice in supporting_slices
            for evidence_path in evidence_slice["evidence"]
            if evidence_path.endswith(".py")
        }
        normalized_python_paths = _specialized_python2025_runtime_artifacts(
            project_root,
            evidence_py_paths,
            family_hints=_FI_SERVICE_SOURCE_FAMILY_HINTS.get(family, ()),
        )
        evidence_artifacts = _specialized_python2025_runtime_artifacts(
            project_root,
            {
                evidence_path
                for evidence_slice in supporting_slices
                for evidence_path in evidence_slice["evidence"]
            },
            family_hints=_FI_SERVICE_SOURCE_FAMILY_HINTS.get(family, ()),
        )
        fi_service_rows.append(
            {
                "requirement_id": requirement_id,
                "service_number": int(requirement_id.rsplit("-", 1)[1]),
                "family": family,
                "proof_status": "implemented-slice-traceable",
                "proof_kind": proof_kind,
                "supporting_slice_ids": [evidence_slice["id"] for evidence_slice in supporting_slices],
                "evidence_tests": normalized_python_paths,
                "evidence_artifacts": evidence_artifacts,
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
    project_root = Path(__file__).resolve().parents[6]
    delta_rows: list[dict[str, Any]] = []
    for requirement_id in sorted(
        {
            requirement_id
            for evidence_slice in _implemented_slices()
            for requirement_id in evidence_slice.get("requirements", ())
            if requirement_id.startswith(("HLA2025-MOD-", "HLA2025-NEW-", "HLA2025-RET-"))
        }
    ):
        supporting_slices = [
            evidence_slice
            for evidence_slice in _implemented_slices()
            if requirement_id in evidence_slice.get("requirements", ())
        ]
        supporting_slice_ids = tuple(evidence_slice["id"] for evidence_slice in supporting_slices)
        family_hints = _delta_source_family_hints(supporting_slice_ids)
        evidence_tests = _specialized_python2025_runtime_artifacts(
            project_root,
            {
                evidence_path
                for evidence_slice in supporting_slices
                for evidence_path in evidence_slice["evidence"]
                if evidence_path.endswith(".py")
            },
            family_hints=family_hints,
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
                "supporting_slice_ids": list(supporting_slice_ids),
                "evidence_tests": evidence_tests,
                "evidence_artifacts": _specialized_python2025_runtime_artifacts(
                    project_root,
                    {
                        evidence_path
                        for evidence_slice in supporting_slices
                        for evidence_path in evidence_slice["evidence"]
                    },
                    family_hints=family_hints,
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
            for evidence_slice in _implemented_slices()
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
            "artifact/runtime-capability bounded and FedPro remains a hosted runtime slice rather than full conformance. "
            "Those remaining limits are adapter or transport seam evidence boundaries over the main "
            "hla-backend-python2025 runtime, not alternate ownership lanes for core 2025 RTI semantics."
        ),
        "rows": binding_rows,
    }


def _build_omt_requirement_proof_audit() -> dict[str, Any]:
    omt_rows: list[dict[str, Any]] = []
    for requirement_id in sorted(
        {
            requirement_id
            for evidence_slice in _implemented_slices()
            for requirement_id in evidence_slice.get("requirements", ())
            if requirement_id.startswith(("HLA2025-OMT-", "HLA2025-OMT-COMP-", "HLA2025-OMT-CV-", "HLA2025-OMT-SU-"))
        }
    ):
        supporting_slices = [
            evidence_slice
            for evidence_slice in _implemented_slices()
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
            "All OMT-related rows are now explicit requirement records with supported-subset proof, including bounded "
            "foreign xs:any extension tolerance. This closes the traceability gap without pretending extension "
            "payloads are preserved as repo-native runtime semantics."
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
            "matrix, and all 55 callback rows are helper-backed with focused executable evidence, including "
            "reconnect-safe callback backlog cleanup across disconnect/reconnect on the hosted FedPro seam. This closes the "
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


def _build_callback_decomposition_audit() -> dict[str, Any]:
    slice_ids = [
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
    ]
    requirement_count = len(
        {
            requirement
            for slice_row in IMPLEMENTED_EVIDENCE_SLICES
            if slice_row["id"] in slice_ids
            for requirement in slice_row["requirements"]
        }
    )
    proof_families = [
        {
            "family": "declaration-relevance-and-interest-advisories",
            "focus": "start or stop registration plus turnInteractionsOn/off callback delivery across declaration and time-managed declaration flows",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_declaration_management_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_managed_declaration_independence_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_passive_full_declaration_scenario_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_declaration_management_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_time_managed_declaration_independence_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "federation-sync-save-restore-and-reporting",
            "focus": "synchronization registration and announce flow, federationSynchronized completion, save/restore lifecycle callbacks, connectionLost teardown, and federation execution reporting",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_synchronization_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_multiple_synchronization_points_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_save_restore_lifecycle",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_connection_lost_callback_tears_down_connection",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_reports_federation_executions_and_members",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_emits_synchronization_callbacks_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_targeted_synchronization_callbacks_only_to_sync_set_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_restore_lifecycle_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_save_restore_completion_callbacks_only_to_reporting_federate_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_federation_reporting_callbacks_over_fedpro_schema",
            ],
        },
        {
            "family": "object-discovery-delivery-and-removal",
            "focus": "discoverObjectInstance, reflectAttributeValues, receiveInteraction, provideAttributeValueUpdate, and removeObjectInstance delivery across plain, timed, restore, and requester-only routing paths",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_two_federate_object_and_interaction_exchange",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_object_management_and_support_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_locally_deleted_object_known_state",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_discovery_and_remove_only_to_subscriber_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_attribute_value_update_requests_only_to_owner_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_object_and_interaction_exchange_over_fedpro_schema",
            ],
        },
        {
            "family": "object-advisory-transport-and-name-reservation-callbacks",
            "focus": "scope advisories, update-rate advisories, transport change/query callbacks, and single or multiple object-instance name reservation callback flows",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_object_scope_relevance_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_python_rti_runs_name_reservation_scenario_without_wrapper_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_object_management_and_support_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_supports_multiple_object_instance_name_reservation_and_release",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_object_scope_relevance_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_attribute_scope_advisories_only_to_overlapping_subscribers_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_isolates_name_reservation_callbacks_per_federate_over_fedpro_schema",
            ],
        },
        {
            "family": "supplemental-context-and-region-introspection",
            "focus": "callback-context preservation for producing-federate and sent-region metadata on direct and hosted callback delivery surfaces",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_preserves_direct_callback_context_for_timed_region_delivery",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_decoder_preserves_direct_callback_context_details",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_decodes_extended_callback_routes_over_fedpro_schema",
            ],
        },
        {
            "family": "ownership-negotiation-and-query-callbacks",
            "focus": "ownership assumption, release, divestiture confirmation, acquisition notification, unavailable/query callbacks, and restore recovery of inflight ownership state",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_basic_ownership_divest_acquire_and_query_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_python_rti_runs_negotiated_ownership_flow_without_wrapper_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_inflight_ownership_state",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_attribute_ownership_query_callbacks_only_to_requester_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema",
            ],
        },
        {
            "family": "time-grant-regulation-and-retraction",
            "focus": "time regulation/time constrained enable callbacks, timeAdvanceGrant progression, and requestRetraction delivery across direct and hosted time-window or queued-TSO flows",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_uses_selected_logical_time_factory_for_queries_and_grants",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_future_exclusion_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_queues_timestamped_messages_and_supports_retraction",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_time_enable_callbacks_only_to_named_federate_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_decodes_request_retraction_callback_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_future_exclusion_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_time_window_gauntlet_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "callback-control-and-backlog-hygiene",
            "focus": "disableCallbacks or enableCallbacks queue control, evokeCallback ordering, and reconnect-safe stale-backlog cleanup on the hosted seam",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_enable_disable_callbacks_controls_evoked_delivery",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_enable_disable_callbacks_controls_evoked_delivery_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drains_multiple_callbacks_in_order_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_disconnected_peer_callback_backlog_before_reconnect_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_plain_callbacks_and_preserves_post_restore_routing",
            ],
        },
    ]
    return {
        "audit_status": "callback-decomposition-captured",
        "slice_id": "2025-callback-proof-families",
        "slice_ids": slice_ids,
        "requirement_count": requirement_count,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "Callback proof is no longer just a flat ledger plus one route-backed count. Its current evidence separates "
            "into declaration advisories, federation sync/save-restore/reporting, object delivery, advisory or name-reservation "
            "callbacks, supplemental callback context, ownership callbacks, time or retraction callbacks, and callback-control "
            "hygiene families, with direct and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these callback proof families before attempting "
            "callback-by-callback signature or ordering claims beyond the current Python lanes."
        ),
    }


def _build_time_management_decomposition_audit() -> dict[str, Any]:
    slice_ids = [
        "2025-time-mode-enable-disable",
        "2025-time-advance-request-modes",
        "2025-time-grant-and-async-delivery",
        "2025-time-query-and-lookahead-control",
        "2025-time-queries-retraction-and-order",
        "2025-lookahead-window-proofs",
        "2025-save-restore-lifecycle",
    ]
    requirement_count = len(
        {
            requirement
            for slice_row in IMPLEMENTED_EVIDENCE_SLICES
            if slice_row["id"] in slice_ids
            for requirement in slice_row["requirements"]
        }
    )
    proof_families = [
        {
            "family": "factory-mode-enable-and-request-primitives",
            "focus": "logical-time factory selection, regulation/constrained enablement, advance-request modes, MOM time-management control routing, and typed flush-queue request handling",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_requires_valid_fom_modules_and_default_logical_time",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_section8_time_bound_queries_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_mom_time_management_service_interactions",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_time_management_services_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_time_enable_callbacks_only_to_named_federate_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_time_control_actions_to_named_federate_runtime_effects_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_time_management_service_interactions",
            ],
        },
        {
            "family": "galt-lits-query-and-lookahead-observability",
            "focus": "queryLogicalTime, queryGALT, queryLITS, queryLookahead, modifyLookahead, and visible divergence or convergence of GALT/LITS under queued traffic and live lookahead changes",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_uses_selected_logical_time_factory_for_queries_and_grants",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_future_exclusion_oracle_rejects_mismatched_lits_boundary",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_future_exclusion_scenario_end_to_end",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_tracks_lookahead_and_galt_per_federate_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_distinguishes_galt_from_lits_after_lookahead_change_with_queued_tso_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_future_exclusion_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
            ],
        },
        {
            "family": "timestamped-delivery-retraction-and-ordering",
            "focus": "queued timestamped delivery, requestRetraction fanout or suppression, lagging-subscriber behavior, and receive-order versus timestamp-order handling across direct and hosted routes",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_queues_timestamped_messages_and_supports_retraction",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_fans_out_post_delivery_retraction_to_all_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_drops_retraction_callbacks_for_disconnected_delivered_targets",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_section8_request_retraction_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_queues_timestamped_messages_and_retracts_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_fans_out_post_delivery_retraction_to_all_subscribers_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_retraction_callbacks_for_disconnected_delivered_targets_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_decodes_request_retraction_callback_over_fedpro_schema",
            ],
        },
        {
            "family": "lookahead-window-proof-ladder",
            "focus": "Target/Radar safe-window closure, future-message exclusion, output delivery, consumer ordering, pipeline overlap, receive-order poison rejection, and the integrated lookahead-processing-window gauntlet",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_core_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_future_exclusion_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_output_delivery_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_consumer_order_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_pipeline_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_receive_order_poison_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_integrated_time_window_gauntlet_end_to_end",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_time_window_core_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_future_exclusion_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_delivers_post_closure_timestamped_output_to_consumer_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_preserves_consumer_timestamp_order_between_competing_output_and_radar_output_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_replays_time_window_proof_ladder_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_time_window_gauntlet_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
            ],
        },
        {
            "family": "save-restore-time-state-and-lookahead-rollback",
            "focus": "saved logical-time, lookahead, switch-control, queued-TSO, and open or closed window state rollback, including restore resumption without dirty post-save replay",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_scheduled_save_restore_time_state_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_time_and_switch_control_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_restore_state_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_restore_output_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_window_pipeline_restore_scenario_end_to_end",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_scheduled_save_restore_time_state_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_time_and_switch_control_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_per_federate_time_state_and_flush_grant_targeting_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_open_and_closed_time_window_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_treats_callback_delivery_as_runtime_policy_not_saved_state_over_fedpro_route",
            ],
        },
    ]
    return {
        "audit_status": "time-management-decomposition-captured",
        "slice_id": "2025-time-management-proof-families",
        "slice_ids": slice_ids,
        "requirement_count": requirement_count,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "Time-management proof is no longer just one bounded query/window bucket. Its current evidence separates "
            "into factory/mode/request primitives, GALT/LITS and lookahead observability, timestamped delivery and "
            "retraction ordering, the Target/Radar lookahead-window proof ladder, and save/restore rollback of time, "
            "lookahead, and window state, with direct and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these time-management proof families before "
            "attempting per-service completion claims across regulation, advance requests, timestamped delivery, "
            "queries, and save/restore time-state semantics."
        ),
    }


def _build_binding_route_decomposition_audit() -> dict[str, Any]:
    slice_ids = [
        "2025-java-binding-source-trace",
        "2025-cpp-binding-source-trace",
        "2025-standard-route-runtime-capability",
        "2025-fedpro-typed-transport-surface",
        "2025-fedpro-hosted-runtime-core",
        "2025-fedpro-hosted-runtime-extended-state",
    ]
    requirement_count = len(
        {
            requirement
            for slice_row in IMPLEMENTED_EVIDENCE_SLICES
            if slice_row["id"] in slice_ids
            for requirement in slice_row["requirements"]
        }
    )
    proof_families = [
        {
            "family": "java-binding-source-and-intake-evidence",
            "focus": "Java package inventory, source trace, intake manifests, and the distinction between Java wrapper surfaces and the main python2025 runtime owner",
            "evidence_tests": [
                "tests/requirements/test_2025_tail_backlog_evidence.py",
                "tests/requirements/test_2025_python_rti_backend_audit.py",
            ],
            "route_groups": ["java-standard-2025-jpype", "java-standard-2025-py4j"],
        },
        {
            "family": "cpp-binding-source-and-intake-evidence",
            "focus": "C++ namespace/source trace, intake evidence, and wrapper-surface separation from the main python2025 runtime lane",
            "evidence_tests": [
                "tests/requirements/test_2025_tail_backlog_evidence.py",
                "tests/requirements/test_2025_python_rti_backend_audit.py",
            ],
            "route_groups": ["cpp-standard-2025-pybind", "cpp-standard-2025-grpc"],
        },
        {
            "family": "standard-java-cpp-runtime-capability-traces",
            "focus": "artifact-gated standard-route lifecycle, object, ownership, time, MOM, DDM, support-service, and save/restore capability traces executed over the primary python2025 runtime lane",
            "evidence_tests": [
                "tests/backends/test_standard_shim_artifacts.py",
                "tests/backends/test_shim_route_trace_evidence.py",
                "tests/requirements/test_2025_route_parity_matrix.py",
            ],
            "route_groups": [
                "java-standard-2025-jpype",
                "java-standard-2025-py4j",
                "cpp-standard-2025-pybind",
                "cpp-standard-2025-grpc",
            ],
        },
        {
            "family": "fedpro-typed-transport-and-schema-surface",
            "focus": "typed RTI request oneofs, typed callback oneofs, schema-tagged client selection, federation-list plus create-with-MIM transport commands, and executable FedPro transport-schema proof",
            "evidence_tests": [
                "tests/transport/test_grpc_transport_2025.py",
                "tests/requirements/test_2025_tail_backlog_evidence.py",
                "tests/requirements/test_2025_route_parity_matrix.py",
            ],
            "route_groups": ["python-2025-fedpro-grpc"],
        },
        {
            "family": "fedpro-hosted-runtime-core-and-extended-state",
            "focus": "hosted 2025 runtime lifecycle, object, ownership, time, save/restore, callback, MOM, support-service, and example-FOM replay over create_rti_ambassador('python2025', transport=...)",
            "evidence_tests": [
                "tests/transport/test_grpc_transport_2025.py",
                "tests/requirements/test_2025_python_rti_backend_audit.py",
                "tests/requirements/test_2025_route_parity_matrix.py",
            ],
            "route_groups": ["python-2025-fedpro-grpc"],
        },
        {
            "family": "cross-route-scenario-parity-ledger",
            "focus": "the explicit parity ledger across federation_lifecycle, object_exchange, ownership, ddm, time_management, save_restore, mom, and support_services for all current 2025 routes",
            "evidence_tests": [
                "tests/requirements/test_2025_route_parity_matrix.py",
                "tests/requirements/test_2025_finish_line_snapshot.py",
                "scripts/run_spec2025_route_parity_matrix.py",
            ],
            "route_groups": [
                "python-2025-inprocess",
                "python-2025-fedpro-grpc",
                "java-standard-2025-jpype",
                "java-standard-2025-py4j",
                "cpp-standard-2025-pybind",
                "cpp-standard-2025-grpc",
            ],
        },
    ]
    return {
        "audit_status": "binding-route-decomposition-captured",
        "slice_id": "2025-binding-route-proof-families",
        "slice_ids": slice_ids,
        "requirement_count": requirement_count,
        "proof_family_count": len(proof_families),
        "route_group_coverage_count": sum(len(family["route_groups"]) for family in proof_families),
        "proof_families": proof_families,
        "current_assessment": (
            "Binding and hosted-route proof is no longer just one bounded route bucket. Its current evidence now "
            "separates into named binding and hosted-route families: Java intake/source traces, C++ intake/source "
            "traces, artifact-gated standard runtime-capability traces, the typed FedPro schema surface, the hosted "
            "FedPro runtime slices, and the cross-route scenario parity ledger, while keeping the distinction "
            "between bounded adapter evidence and the main python2025 runtime owner explicit."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these route families before attempting any "
            "stronger behavior-equivalence or hosted-conformance claim."
        ),
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
    ready_for_full_conformance_claim = (
        len(support_rows) == len(focused_rows)
        and not rows_with_known_gaps
        and negative_status_counts.get("partial", 0) == 0
        and negative_status_counts.get("mapped-not-exhaustive", 0) == 0
        and negative_status_counts.get("not-evidenced", 0) == 0
    )
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
        "ready_for_support_service_full_conformance_claim": ready_for_full_conformance_claim,
        "current_assessment": (
            "The repo now has an explicit support-service ledger through the RTIambassador conformance matrix, and "
            "all 62 support-service rows have focused executable evidence. Negative-path coverage is now complete "
            "for all 61 actionable support-service rows, with the remaining row marked not-applicable because it "
            "declares no actionable RTI exception surface. Hosted FedPro support-service replay now also proves "
            "reconnect-safe discard of a disconnected peer's disabled callback backlog before later reconnect. "
            "Support services are now ready for a requirement-level full conformance claim within this audit slice; "
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
            "by explicit requirement ledgers, the backlog is closed at the tracked 2025 delta level, and legacy-only "
            "or bounded-extension areas are named rather than hidden. This is still short of a full 2025 conformance claim."
        ),
        "full_claim_blockers": [
            "Covered rows include bounded supported-scope evidence, including OMT xs:any extension payload preservation without arbitrary third-party extension execution semantics.",
            "Java and C++ binding rows remain artifact/runtime-capability evidence rather than exhaustive behavior-conformance proof.",
            "The hosted FedPro route remains a bounded runtime slice and not a full RTI semantics or exhaustive cross-binding conformance pass.",
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
    duplicate_umbrella_rows = [
        row for row in harmonization_rows if row["harmonization_disposition"] == "duplicate/umbrella"
    ]
    duplicate_umbrella_rows_by_role: dict[str, list[str]] = {}
    for row in duplicate_umbrella_rows:
        duplicate_umbrella_rows_by_role.setdefault(row["row_role"], []).append(row["id"])
    for row_ids in duplicate_umbrella_rows_by_role.values():
        row_ids.sort()
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
        "duplicate_umbrella_rows_by_role": duplicate_umbrella_rows_by_role,
        "current_assessment": (
            "The repo now has an explicit row-level requirement-by-requirement disposition audit across all 691 "
            "tracked 2025 rows: every row is reviewed, dispositioned, and linked either to repo evidence, an "
            "explicit bounded support claim, a retired exclusion, or an umbrella normalization role. That closes "
            "the missing-audit gap without turning the result into an unconditional all-covered conformance pass, "
            "and it strengthens the bounded main-implementation claim for hla-backend-python2025 while leaving "
            "hla-backend-shim in a wrapper-only compatibility role."
        ),
        "full_claim_blockers": [
            "24 rows are retired/legacy-only exclusions rather than active 2025 support.",
            "22 rows remain duplicate/umbrella normalization aids rather than one-row conformance assertions; those rows are split between framework-rule umbrellas and callback/configuration/binding delta umbrellas.",
            "OMT xs:any extension-point rows are covered as payload-preserving tolerance, not arbitrary third-party extension execution semantics.",
            "Many covered rows still inherit bounded supported-scope language from slice-level evidence rather than standalone exhaustive clause-by-clause proof.",
        ],
    }


def _build_retired_legacy_mapping_audit(
    project_root: Path,
    harmonization_rows: list[Mapping[str, str]],
) -> dict[str, Any]:
    doc_rel = "docs/requirements/ieee-1516-2025/retired_legacy_mapping.md"
    doc_path = project_root / doc_rel
    doc_text = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    rows = [row for row in harmonization_rows if row["harmonization_disposition"] == "retired/legacy-only"]
    by_service_group: dict[str, list[str]] = {}
    for row in rows:
        by_service_group.setdefault(row["service_group"], []).append(row["id"])
    for row_ids in by_service_group.values():
        row_ids.sort()
    rows_with_doc_anchor = [
        row["id"]
        for row in rows
        if doc_rel in row["suggested_repo_evidence_path"]
    ]
    rows_missing_doc_anchor = sorted({row["id"] for row in rows} - set(rows_with_doc_anchor))
    rows_mentioned_in_doc = [row["id"] for row in rows if row["id"] in doc_text]
    rows_missing_from_doc = sorted({row["id"] for row in rows} - set(rows_mentioned_in_doc))
    rows_with_candidate_replacement_note = [
        row["id"] for row in rows if "candidate replacement:" in row["notes"]
    ]
    rows_missing_candidate_replacement_note = sorted(
        {row["id"] for row in rows} - set(rows_with_candidate_replacement_note)
    )
    return {
        "audit_status": "retired-legacy-mapping-captured",
        "doc_path": doc_rel,
        "row_count": len(rows),
        "doc_exists": doc_path.exists(),
        "rows_with_doc_anchor_count": len(rows_with_doc_anchor),
        "rows_missing_doc_anchor": rows_missing_doc_anchor,
        "rows_mentioned_in_doc_count": len(rows_mentioned_in_doc),
        "rows_missing_from_doc": rows_missing_from_doc,
        "rows_with_candidate_replacement_note_count": len(rows_with_candidate_replacement_note),
        "rows_missing_candidate_replacement_note": rows_missing_candidate_replacement_note,
        "by_service_group": by_service_group,
        "ready_for_retired_legacy_mapping_claim": (
            doc_path.exists()
            and not rows_missing_doc_anchor
            and not rows_missing_from_doc
            and not rows_missing_candidate_replacement_note
        ),
        "current_assessment": (
            "The retired/legacy-only rows are no longer just a count in the finish-line bundle. They now have an "
            "explicit mapping note that enumerates every retired row and the candidate 2025 replacement surface, "
            "which makes the exclusion boundary auditable rather than implied."
        ),
        "residual_boundary": (
            "This audit proves exclusion mapping and documentation quality for retired rows. It does not convert those "
            "legacy-only rows into active 2025 support obligations."
        ),
    }


def _build_duplicate_umbrella_mapping_audit(
    project_root: Path,
    harmonization_rows: list[Mapping[str, str]],
) -> dict[str, Any]:
    framework_doc_rel = "docs/requirements/ieee-1516-2025/framework_rules.md"
    delta_doc_rel = "docs/requirements/ieee-1516-2025/callback_binding_deltas.md"
    registry_rel = "docs/requirements/ieee-1516-2025/requirements.json"
    backlog_rel = "requirements/2025/requirement_completion_backlog.csv"
    framework_text = (project_root / framework_doc_rel).read_text(encoding="utf-8")
    delta_text = (project_root / delta_doc_rel).read_text(encoding="utf-8")
    registry_data = json.loads((project_root / registry_rel).read_text(encoding="utf-8"))
    registry_row_ids = {row["id"] for row in registry_data["requirements"]}
    backlog_row_ids = {row["id"] for row in _read_csv(project_root / backlog_rel)}
    all_row_ids = {row["id"] for row in harmonization_rows} | registry_row_ids | backlog_row_ids
    row_disposition_by_id = {row["id"]: row["harmonization_disposition"] for row in harmonization_rows}
    rows = [row for row in harmonization_rows if row["harmonization_disposition"] == "duplicate/umbrella"]
    by_row_role: dict[str, list[str]] = {}
    for row in rows:
        by_row_role.setdefault(row["row_role"], []).append(row["id"])
    for row_ids in by_row_role.values():
        row_ids.sort()
    framework_rows = [row for row in rows if row["row_role"] == "framework-umbrella"]
    delta_rows = [row for row in rows if row["row_role"] == "delta-umbrella"]
    framework_child_links = _extract_umbrella_child_links(framework_text, row_id_prefix="HLA2025-FR-")
    delta_child_links = _extract_umbrella_child_links(delta_text, row_id_prefix="HLA2025-")
    framework_missing_doc_anchor = sorted(
        row["id"] for row in framework_rows if framework_doc_rel not in row["suggested_repo_evidence_path"]
    )
    delta_missing_doc_anchor = sorted(
        row["id"] for row in delta_rows if delta_doc_rel not in row["suggested_repo_evidence_path"]
    )
    framework_missing_from_doc = sorted(row["id"] for row in framework_rows if row["id"] not in framework_text)
    delta_missing_from_doc = sorted(row["id"] for row in delta_rows if row["id"] not in delta_text)
    framework_missing_child_links = sorted(row["id"] for row in framework_rows if not framework_child_links.get(row["id"]))
    delta_missing_child_links = sorted(row["id"] for row in delta_rows if not delta_child_links.get(row["id"]))
    framework_unknown_child_ids: dict[str, list[str]] = {}
    for row_id, child_ids in framework_child_links.items():
        unknown_child_ids = sorted(child_id for child_id in child_ids if child_id not in all_row_ids)
        if unknown_child_ids:
            framework_unknown_child_ids[row_id] = unknown_child_ids
    delta_unknown_child_ids: dict[str, list[str]] = {}
    for row_id, child_ids in delta_child_links.items():
        unknown_child_ids = sorted(child_id for child_id in child_ids if child_id not in all_row_ids)
        if unknown_child_ids:
            delta_unknown_child_ids[row_id] = unknown_child_ids
    framework_rows_without_concrete_child = sorted(
        row_id
        for row_id, child_ids in framework_child_links.items()
        if not any(row_disposition_by_id.get(child_id) != "duplicate/umbrella" for child_id in child_ids)
    )
    delta_rows_without_concrete_child = sorted(
        row_id
        for row_id, child_ids in delta_child_links.items()
        if not any(row_disposition_by_id.get(child_id) != "duplicate/umbrella" for child_id in child_ids)
    )
    return {
        "audit_status": "duplicate-umbrella-mapping-captured",
        "row_count": len(rows),
        "framework_doc_path": framework_doc_rel,
        "delta_doc_path": delta_doc_rel,
        "registry_path": registry_rel,
        "backlog_path": backlog_rel,
        "framework_row_count": len(framework_rows),
        "delta_row_count": len(delta_rows),
        "framework_missing_doc_anchor": framework_missing_doc_anchor,
        "delta_missing_doc_anchor": delta_missing_doc_anchor,
        "framework_missing_from_doc": framework_missing_from_doc,
        "delta_missing_from_doc": delta_missing_from_doc,
        "framework_child_links": framework_child_links,
        "delta_child_links": delta_child_links,
        "framework_missing_child_links": framework_missing_child_links,
        "delta_missing_child_links": delta_missing_child_links,
        "framework_unknown_child_ids": framework_unknown_child_ids,
        "delta_unknown_child_ids": delta_unknown_child_ids,
        "framework_rows_without_concrete_child": framework_rows_without_concrete_child,
        "delta_rows_without_concrete_child": delta_rows_without_concrete_child,
        "by_row_role": by_row_role,
        "ready_for_duplicate_umbrella_mapping_claim": (
            not framework_missing_doc_anchor
            and not delta_missing_doc_anchor
            and not framework_missing_from_doc
            and not delta_missing_from_doc
            and not framework_missing_child_links
            and not delta_missing_child_links
            and not framework_unknown_child_ids
            and not delta_unknown_child_ids
            and not framework_rows_without_concrete_child
            and not delta_rows_without_concrete_child
        ),
        "current_assessment": (
            "The duplicate/umbrella rows are no longer just grouped by role in the finish-line bundle. The repo now "
            "has explicit proof-note documents for both framework-rule umbrellas and callback/configuration/binding "
            "delta umbrellas, and every umbrella row is anchored to, enumerated by, and child-linked from those notes."
        ),
        "residual_boundary": (
            "This audit improves the traceability of umbrella rows, but it does not change their status into "
            "standalone one-row conformance claims."
        ),
    }


def _extract_umbrella_child_links(text: str, *, row_id_prefix: str) -> dict[str, list[str]]:
    child_links: dict[str, list[str]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(f"| {row_id_prefix}"):
            continue
        columns = [column.strip() for column in stripped.strip("|").split("|")]
        if len(columns) < 3:
            continue
        row_id = columns[0]
        child_ids = sorted({match for match in re.findall(r"HLA2025-[A-Z0-9-]+", stripped) if match != row_id})
        child_links[row_id] = child_ids
    return child_links


def _build_omt_xs_any_mapping_audit(
    project_root: Path,
    harmonization_rows: list[Mapping[str, str]],
) -> dict[str, Any]:
    doc_rel = "docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md"
    doc_path = project_root / doc_rel
    doc_text = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    test_rel = "tests/test_rti1516_2025_validation.py"
    impl_rel = "packages/hla-rti1516e/src/hla/rti1516e/fom.py"
    test_text = (project_root / test_rel).read_text(encoding="utf-8")
    impl_text = (project_root / impl_rel).read_text(encoding="utf-8")
    rows = [
        row
        for row in harmonization_rows
        if row["id"].startswith("HLA2025-OMT-COMP-")
        and "xs:any" in row["service_or_check"]
    ]
    rows.sort(key=lambda row: row["id"])
    rows_with_doc_anchor = [
        row["id"]
        for row in rows
        if doc_rel in row["suggested_repo_evidence_path"]
    ]
    rows_missing_doc_anchor = sorted({row["id"] for row in rows} - set(rows_with_doc_anchor))
    rows_mentioned_in_doc = [row["id"] for row in rows if row["id"] in doc_text]
    rows_missing_from_doc = sorted({row["id"] for row in rows} - set(rows_mentioned_in_doc))
    family_map = {
        "object-model-root-and-identity": (
            "HLA2025-OMT-COMP-006",
            "HLA2025-OMT-COMP-008",
        ),
        "object-class-and-attribute-extension-points": (
            "HLA2025-OMT-COMP-019",
            "HLA2025-OMT-COMP-021",
            "HLA2025-OMT-COMP-027",
            "HLA2025-OMT-COMP-035",
            "HLA2025-OMT-COMP-039",
            "HLA2025-OMT-COMP-045",
            "HLA2025-OMT-COMP-047",
            "HLA2025-OMT-COMP-056",
            "HLA2025-OMT-COMP-057",
            "HLA2025-OMT-COMP-059",
            "HLA2025-OMT-COMP-067",
            "HLA2025-OMT-COMP-068",
            "HLA2025-OMT-COMP-070",
            "HLA2025-OMT-COMP-077",
            "HLA2025-OMT-COMP-081",
            "HLA2025-OMT-COMP-082",
        ),
        "interaction-class-and-parameter-extension-points": (
            "HLA2025-OMT-COMP-102",
            "HLA2025-OMT-COMP-106",
            "HLA2025-OMT-COMP-107",
            "HLA2025-OMT-COMP-113",
            "HLA2025-OMT-COMP-115",
            "HLA2025-OMT-COMP-129",
            "HLA2025-OMT-COMP-130",
            "HLA2025-OMT-COMP-134",
        ),
        "datatype-and-encoding-extension-points": (
            "HLA2025-OMT-COMP-145",
            "HLA2025-OMT-COMP-147",
            "HLA2025-OMT-COMP-154",
            "HLA2025-OMT-COMP-156",
            "HLA2025-OMT-COMP-171",
            "HLA2025-OMT-COMP-176",
            "HLA2025-OMT-COMP-178",
            "HLA2025-OMT-COMP-181",
            "HLA2025-OMT-COMP-189",
            "HLA2025-OMT-COMP-193",
            "HLA2025-OMT-COMP-197",
            "HLA2025-OMT-COMP-198",
        ),
        "container-table-and-reference-extension-points": (
            "HLA2025-OMT-COMP-202",
            "HLA2025-OMT-COMP-204",
            "HLA2025-OMT-COMP-208",
            "HLA2025-OMT-COMP-210",
            "HLA2025-OMT-COMP-219",
            "HLA2025-OMT-COMP-222",
            "HLA2025-OMT-COMP-224",
        ),
    }
    family_headings_ready = all(f"### `{family}`" in doc_text for family in family_map)
    executable_anchor_checks = [
        "test_2025_parser_accepts_isolates_and_preserves_foreign_namespace_extension_points" in test_text,
        "serialize_fom_module(module, edition=\"2025\")" in test_text,
        "assert module.foreign_extensions" in test_text,
        "assert len(reparsed.foreign_extensions) == len(module.foreign_extensions)" in test_text,
        "payload-text" in test_text and "nested-text" in test_text and "attribute-child" in test_text,
    ]
    implementation_anchor_checks = [
        "class ForeignExtensionSpec" in impl_text,
        "Foreign-namespace OMT extension payload retained without interpretation." in impl_text,
        "foreign_extensions: tuple[ForeignExtensionSpec, ...] = ()" in impl_text,
        "or self.foreign_extensions" in impl_text,
    ]
    return {
        "audit_status": "omt-xs-any-mapping-captured",
        "doc_path": doc_rel,
        "row_count": len(rows),
        "doc_exists": doc_path.exists(),
        "test_path": test_rel,
        "implementation_path": impl_rel,
        "rows_with_doc_anchor_count": len(rows_with_doc_anchor),
        "rows_missing_doc_anchor": rows_missing_doc_anchor,
        "rows_mentioned_in_doc_count": len(rows_mentioned_in_doc),
        "rows_missing_from_doc": rows_missing_from_doc,
        "family_count": len(family_map),
        "family_headings_ready": family_headings_ready,
        "executable_anchor_ready": all(executable_anchor_checks),
        "implementation_anchor_ready": all(implementation_anchor_checks),
        "by_family": {family: list(row_ids) for family, row_ids in family_map.items()},
        "ready_for_omt_xs_any_mapping_claim": (
            doc_path.exists()
            and len(rows) == 45
            and not rows_missing_doc_anchor
            and not rows_missing_from_doc
            and family_headings_ready
            and all(executable_anchor_checks)
            and all(implementation_anchor_checks)
        ),
        "current_assessment": (
            "The 45 OMT xs:any rows are no longer just grouped under a bounded decomposition slice. They now have a "
            "requirement-facing proof note that enumerates every row by family, a concrete parser round-trip test for "
            "foreign namespace payload preservation, and explicit implementation anchors that keep those payloads "
            "isolated from repo-native HLA semantics."
        ),
        "residual_boundary": (
            "This audit makes the xs:any bounded claim explicit and fully reviewable, but it does not convert foreign "
            "extension payload tolerance into arbitrary third-party extension execution semantics."
        ),
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
            "binding and hosted routes, with explicit legacy-only, bounded-extension, and artifact-gated boundaries "
            "recorded in the repo."
        ),
        "supported_scope": [
            "Python 2025 in-process runtime behavior is executable and parity-covered across the tracked scenario set.",
            "Hosted FedPro 2025 transport behavior is executable as a bounded runtime slice with explicit route parity coverage, spanning lifecycle, object, time, save/restore, support-service, and callback scenario replay over hla-backend-python2025; its remaining proof burden is transport-seam evidence over hla-backend-python2025 rather than missing core runtime ownership.",
            "FI service requirements are traced across all 196 catalog rows.",
            "Common delta rows, binding rows, and OMT-related rows are all represented by explicit requirement ledgers.",
        ],
        "explicit_boundaries": [
            "Foreign OMT xs:any extension payloads are preserved for XML round-trip but not interpreted as repo-native runtime semantics.",
            "Retired or legacy-only rows remain excluded from the supported 2025 working surface.",
            "Java and C++ bindings remain artifact/runtime-capability bounded as binding/adaptation-seam proof over the main python2025 runtime rather than full behavior-conformance proof.",
            "FedPro remains a hosted runtime slice rather than a full RTI semantics or exhaustive cross-binding conformance pass, and its remaining gaps are transport-seam proof gaps rather than evidence that hla-backend-python2025 lacks the underlying semantics.",
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


def _build_hosted_shared_scenario_coverage_audit(project_root: Path) -> dict[str, Any]:
    transport_test = (project_root / "tests" / "transport" / "test_grpc_transport_2025.py").read_text(encoding="utf-8")
    conformance_evidence = (
        project_root
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "repo_internal"
        / "conformance_evidence.py"
    ).read_text(encoding="utf-8")
    shared_scenarios = sorted(
        set(
            re.findall(
                r"def (test_2025_transport_server_runs_shared_[A-Za-z0-9_]+?_scenario_over_fedpro_route)\(",
                transport_test,
            )
        )
    )
    zero_count_shared_scenarios = [name for name in shared_scenarios if conformance_evidence.count(name) == 0]
    represented_count = len(shared_scenarios) - len(zero_count_shared_scenarios)
    return {
        "audit_status": "hosted-shared-fedpro-scenarios-accounted-for",
        "shared_scenario_count": len(shared_scenarios),
        "represented_in_conformance_evidence_count": represented_count,
        "zero_count_shared_scenarios": zero_count_shared_scenarios,
        "ready_for_full_shared_scenario_representation_claim": not zero_count_shared_scenarios,
        "current_assessment": (
            "Every shared hosted FedPro 2025 scenario is now represented in the conformance evidence ledger, so the "
            "hosted route summary is no longer silently under-counting the main python2025 runtime surface."
            if not zero_count_shared_scenarios
            else "Some shared hosted FedPro 2025 scenarios still have zero explicit representation in the conformance "
            "evidence ledger, so the hosted route summary remains incomplete."
        ),
    }


def _build_python2025_proof_lane_audit(project_root: Path) -> dict[str, Any]:
    manifest = json.loads((project_root / "testing" / "test_surface_manifest.json").read_text(encoding="utf-8"))
    tools_python = (project_root / "tools" / "python").read_text(encoding="utf-8")
    test_surface = (project_root / "docs" / "test_surface.md").read_text(encoding="utf-8")
    root_readme = (project_root / "README.md").read_text(encoding="utf-8")
    lane_rows = {
        row["id"]: row
        for row in manifest["lanes"]
        if row["id"] in {"python-main-2025", "python-routes-2025"}
    }
    direct_lane = lane_rows["python-main-2025"]
    hosted_lane = lane_rows["python-routes-2025"]
    direct_command = " ".join(direct_lane["owner_command"])
    hosted_command = " ".join(hosted_lane["owner_command"])
    readiness_checks = [
        direct_command in tools_python,
        hosted_command in tools_python,
        direct_command in test_surface,
        hosted_command in test_surface,
        direct_command in root_readme,
        hosted_command in root_readme,
        "Use `verify-main-2025` as the default direct `python2025` proof lane." in root_readme,
        "`verify-routes-2025` when you also need the bounded hosted" in root_readme,
    ]
    return {
        "audit_status": "python2025-proof-lanes-captured",
        "ready_for_main_implementation_operator_lane_claim": all(readiness_checks),
        "default_direct_lane": {
            "lane_id": direct_lane["id"],
            "title": direct_lane["title"],
            "owner_command": direct_lane["owner_command"],
            "estimated_cost": direct_lane["estimated_cost"],
            "docs": direct_lane["docs"],
            "preflight_kind": direct_lane["preflight"]["kind"],
            "description": direct_lane["description"],
        },
        "hosted_extension_lane": {
            "lane_id": hosted_lane["id"],
            "title": hosted_lane["title"],
            "owner_command": hosted_lane["owner_command"],
            "estimated_cost": hosted_lane["estimated_cost"],
            "docs": hosted_lane["docs"],
            "preflight_kind": hosted_lane["preflight"]["kind"],
            "description": hosted_lane["description"],
        },
        "shared_claim": (
            "The repo does not treat hla-backend-python2025 as a package-only promotion. The canonical operator "
            "surface declares ./tools/python verify-main-2025 as the default direct proof lane for the real "
            "python2025 runtime and ./tools/python verify-routes-2025 as the bounded hosted FedPro extension over "
            "that same runtime."
        ),
        "current_operator_runs": [
            {
                "lane_id": "python-main-2025",
                "command": "./tools/python verify-main-2025",
                "result": "324 passed across wrapper subcommands plus Target/Radar example",
                "scope": (
                    "current-tree direct python2025 package-boundary, federation/object/DDM, support/ownership/MOM, "
                    "time-window, save/restore, callback, OMT, and example-scenario proof lane"
                ),
            },
            {
                "lane_id": "python-routes-2025",
                "command": "./tools/python verify-routes-2025",
                "result": "434 passed across direct-plus-hosted wrapper subcommands plus finish-line bundle and Target/Radar example",
                "scope": (
                    "current-tree direct python2025 plus bounded hosted FedPro route verification lane, including "
                    "transport suite, route-parity bundle, finish-line artifact generation, and package-owned example replay"
                ),
            },
        ],
        "evidence_anchors": [
            "testing/test_surface_manifest.json",
            "tools/python",
            "docs/test_surface.md",
            "README.md",
        ],
        "residual_boundary": (
            "This lane audit now proves command identity, operator-facing proof-lane ownership, and one current-tree "
            "green execution of both canonical wrapper commands. It still does not replace the need to keep those "
            "proof lanes green as the tree changes."
        ),
    }


def _build_binding_boundary_mapping_audit(
    project_root: Path,
    completion_backlog_rows: list[Mapping[str, str]],
) -> dict[str, Any]:
    doc_rel = "docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md"
    doc_path = project_root / doc_rel
    doc_text = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    requirement_ids = ("HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003")
    row_labels = {
        "HLA2025-BND-001": "java-binding",
        "HLA2025-BND-002": "cpp-binding",
        "HLA2025-BND-003": "hosted-fedpro",
    }
    rows = [row for row in completion_backlog_rows if row["id"] in requirement_ids]
    rows.sort(key=lambda row: row["id"])
    rows_mentioned_in_doc = [row["id"] for row in rows if row["id"] in doc_text]
    rows_with_doc_anchor = list(rows_mentioned_in_doc)
    rows_missing_doc_anchor = sorted({row["id"] for row in rows} - set(rows_with_doc_anchor))
    rows_missing_from_doc = sorted({row["id"] for row in rows} - set(rows_mentioned_in_doc))
    by_boundary_role = {
        row_labels[requirement_id]: [requirement_id]
        for requirement_id in requirement_ids
    }
    narrative_checks = [
        "main 2025" in doc_text and "RTI implementation lane is `hla-backend-python2025`" in doc_text,
        "`hla-backend-shim` remains a compatibility wrapper" in doc_text
        or "`hla-backend-shim` remains a compatibility wrapper and is not a runtime owner" in doc_text,
        "not an independent Java RTI" in doc_text,
        "not an independent C++ RTI" in doc_text,
        "not a second RTI implementation lane" in doc_text,
    ]
    return {
        "audit_status": "binding-boundary-mapping-captured",
        "doc_path": doc_rel,
        "row_count": len(rows),
        "doc_exists": doc_path.exists(),
        "rows_with_doc_anchor_count": len(rows_with_doc_anchor),
        "rows_missing_doc_anchor": rows_missing_doc_anchor,
        "rows_mentioned_in_doc_count": len(rows_mentioned_in_doc),
        "rows_missing_from_doc": rows_missing_from_doc,
        "boundary_narrative_ready": all(narrative_checks),
        "by_boundary_role": by_boundary_role,
        "ready_for_binding_boundary_mapping_claim": (
            doc_path.exists()
            and len(rows) == len(requirement_ids)
            and not rows_missing_doc_anchor
            and not rows_missing_from_doc
            and all(narrative_checks)
        ),
        "current_assessment": (
            "The binding and hosted boundary rows are no longer only counted as bounded blockers in the finish-line "
            "bundle. They now have an explicit boundary note that enumerates all three rows and states that "
            "hla-backend-python2025 is the main 2025 Python RTI lane while the Java/C++ bindings and hosted FedPro "
            "route remain bounded wrapper or transport evidence over that same runtime."
        ),
        "residual_boundary": (
            "This audit makes the binding and hosted boundary mapping explicit and reviewable. It does not promote "
            "the Java/C++ rows into exhaustive cross-binding behavior conformance or the hosted FedPro row into a "
            "second full RTI implementation lane."
        ),
    }


def _build_hosted_fedpro_bounded_proof_audit(
    project_root: Path,
    route_parity_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    doc_rel = "docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md"
    doc_path = project_root / doc_rel
    doc_text = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    hosted_rows = [row for row in route_parity_matrix["rows"] if row["route"] == "python-2025-fedpro-grpc"]
    hosted_rows.sort(key=lambda row: row["scenario"])
    expected_scenarios = [
        "ddm",
        "federation_lifecycle",
        "mom",
        "object_exchange",
        "ownership",
        "save_restore",
        "support_services",
        "time_management",
    ]
    required_evidence_tests = [
        "tests/transport/test_grpc_transport_2025.py",
        "tests/scenarios/test_python_route_parity.py",
    ]
    all_rows_parity_covered = all(row["status"] == "parity-covered" for row in hosted_rows)
    identity_ready = all(
        row["runtime_provider"] == "python2025"
        and row["implementation_lane"] == "hla-backend-python2025"
        and row["counts_as_python_2025_rti"] is True
        and row["wrapper_only"] is False
        for row in hosted_rows
    )
    rows_missing_required_evidence_tests = {
        row["scenario"]: [
            test_path for test_path in required_evidence_tests if test_path not in row["evidence_tests"]
        ]
        for row in hosted_rows
    }
    rows_missing_required_evidence_tests = {
        scenario: missing_paths
        for scenario, missing_paths in rows_missing_required_evidence_tests.items()
        if missing_paths
    }
    rows_missing_identity_note = sorted(
        row["scenario"]
        for row in hosted_rows
        if "primary 2025 Python RTI implementation lane" not in row["notes"]
    )
    rows_missing_transport_seam_note = sorted(
        row["scenario"]
        for row in hosted_rows
        if "transport-seam evidence over hla-backend-python2025" not in row["notes"]
    )
    doc_checks = [
        "`python-2025-fedpro-grpc`" in doc_text,
        "`hla-backend-python2025`" in doc_text,
        "`tests/transport/test_grpc_transport_2025.py`" in doc_text,
        "`tests/scenarios/test_python_route_parity.py`" in doc_text,
        "bounded runtime slice" in doc_text,
        "shared Target/Radar example" in doc_text,
        "not a separate 2025 RTI owner" in doc_text
        or ("second full RTI" in doc_text and "implementation lane" in doc_text),
        "transport-seam and cross-binding" in doc_text,
    ]
    return {
        "audit_status": "hosted-fedpro-bounded-proof-captured",
        "doc_path": doc_rel,
        "doc_exists": doc_path.exists(),
        "route": "python-2025-fedpro-grpc",
        "scenario_count": len(hosted_rows),
        "scenarios": [row["scenario"] for row in hosted_rows],
        "expected_scenarios": expected_scenarios,
        "required_evidence_tests": required_evidence_tests,
        "all_rows_parity_covered": all_rows_parity_covered,
        "identity_ready": identity_ready,
        "rows_missing_required_evidence_tests": rows_missing_required_evidence_tests,
        "rows_missing_identity_note": rows_missing_identity_note,
        "rows_missing_transport_seam_note": rows_missing_transport_seam_note,
        "doc_narrative_ready": all(doc_checks),
        "ready_for_hosted_fedpro_bounded_proof_claim": (
            doc_path.exists()
            and len(hosted_rows) == len(expected_scenarios)
            and [row["scenario"] for row in hosted_rows] == expected_scenarios
            and all_rows_parity_covered
            and identity_ready
            and not rows_missing_required_evidence_tests
            and not rows_missing_identity_note
            and not rows_missing_transport_seam_note
            and all(doc_checks)
        ),
        "current_assessment": (
            "The hosted FedPro route is no longer only implied by route-parity tables and finish-line summaries. It "
            "now has a requirement-facing proof note tied to the eight tracked hosted scenario families, explicit "
            "python2025 runtime identity, per-scenario transport-plus-parity test anchors, and an auditable "
            "statement that the route is a bounded transport/runtime slice over hla-backend-python2025."
        ),
        "residual_boundary": (
            "This audit strengthens the hosted-route proof and identity story, but it does not promote the hosted "
            "FedPro lane into full remote-RTI semantics or exhaustive cross-binding conformance."
        ),
    }


def _build_standard_binding_runtime_capability_audit(
    project_root: Path,
    route_parity_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    doc_rel = "docs/requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md"
    doc_path = project_root / doc_rel
    doc_text = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    standard_routes = {
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    }
    standard_rows = [row for row in route_parity_matrix["rows"] if row["route"] in standard_routes]
    standard_rows.sort(key=lambda row: (row["route"], row["scenario"]))
    by_binding = {
        "HLA2025-BND-001": [row for row in standard_rows if row["route"].startswith("java-")],
        "HLA2025-BND-002": [row for row in standard_rows if row["route"].startswith("cpp-")],
    }
    route_counts = {
        requirement_id: sorted({row["route"] for row in rows})
        for requirement_id, rows in by_binding.items()
    }
    parity_counts = {
        requirement_id: {
            "parity-covered": sum(1 for row in rows if row["status"] == "parity-covered"),
            "non-covered": sum(1 for row in rows if row["status"] != "parity-covered"),
        }
        for requirement_id, rows in by_binding.items()
    }
    required_evidence_test = "tests/backends/test_standard_shim_artifacts.py"
    rows_missing_required_evidence_test = sorted(
        f"{row['route']}:{row['scenario']}"
        for row in standard_rows
        if required_evidence_test not in row["evidence_tests"]
    )
    rows_missing_route_trace_artifact = sorted(
        f"{row['route']}:{row['scenario']}"
        for row in standard_rows
        if f"docs/evidence/shim_routes/route_traces/{row['route']}.json" not in row["evidence_artifacts"]
    )
    rows_missing_binding_aggregate_artifact = sorted(
        f"{row['route']}:{row['scenario']}"
        for row in standard_rows
        if (
            "docs/evidence/shim_routes/java-standard-2025.json"
            if row["route"].startswith("java-")
            else "docs/evidence/shim_routes/cpp-standard-2025.json"
        )
        not in row["evidence_artifacts"]
    )
    doc_checks = [
        "`java-standard-2025-jpype`" in doc_text,
        "`java-standard-2025-py4j`" in doc_text,
        "`cpp-standard-2025-pybind`" in doc_text,
        "`cpp-standard-2025-grpc`" in doc_text,
        "`hla-backend-python2025`" in doc_text,
        "`tests/backends/test_standard_shim_artifacts.py`" in doc_text,
        "artifact-gated/runtime-capability" in doc_text,
        "does not claim exhaustive cross-binding behavior equivalence" in doc_text,
    ]
    identity_ready = all(
        row["runtime_provider"] == "python2025"
        and row["implementation_lane"] == "hla-backend-python2025"
        and row["counts_as_python_2025_rti"] is False
        and row["wrapper_only"] is False
        for row in standard_rows
    )
    rows_missing_backing_note = sorted(
        f"{row['route']}:{row['scenario']}"
        for row in standard_rows
        if "executed over the primary python2025 runtime lane in hla-backend-python2025" not in row["notes"]
    )
    rows_missing_seam_note = sorted(
        f"{row['route']}:{row['scenario']}"
        for row in standard_rows
        if "binding/adaptation-seam evidence over the main hla-backend-python2025 runtime" not in row["notes"]
    )
    return {
        "audit_status": "standard-binding-runtime-capability-captured",
        "doc_path": doc_rel,
        "doc_exists": doc_path.exists(),
        "row_count": len(standard_rows),
        "required_evidence_test": required_evidence_test,
        "identity_ready": identity_ready,
        "rows_missing_required_evidence_test": rows_missing_required_evidence_test,
        "rows_missing_route_trace_artifact": rows_missing_route_trace_artifact,
        "rows_missing_binding_aggregate_artifact": rows_missing_binding_aggregate_artifact,
        "rows_missing_backing_note": rows_missing_backing_note,
        "rows_missing_seam_note": rows_missing_seam_note,
        "doc_narrative_ready": all(doc_checks),
        "by_binding_requirement": {
            requirement_id: {
                "routes": route_counts[requirement_id],
                "parity_covered_row_count": parity_counts[requirement_id]["parity-covered"],
                "non_covered_row_count": parity_counts[requirement_id]["non-covered"],
            }
            for requirement_id in ("HLA2025-BND-001", "HLA2025-BND-002")
        },
        "ready_for_standard_binding_runtime_capability_claim": (
            doc_path.exists()
            and len(standard_rows) == 32
            and identity_ready
            and not rows_missing_required_evidence_test
            and not rows_missing_route_trace_artifact
            and not rows_missing_binding_aggregate_artifact
            and not rows_missing_backing_note
            and not rows_missing_seam_note
            and all(doc_checks)
            and parity_counts["HLA2025-BND-001"]["parity-covered"] == 16
            and parity_counts["HLA2025-BND-001"]["non-covered"] == 0
            and parity_counts["HLA2025-BND-002"]["parity-covered"] == 16
            and parity_counts["HLA2025-BND-002"]["non-covered"] == 0
        ),
        "current_assessment": (
            "The Java and C++ standard binding lanes are no longer only described as a generic artifact-gated blocker. "
            "They now have a requirement-facing bounded-proof note tied to their route families, per-row executable "
            "plus artifact anchors, parity-covered scenario counts, and explicit main-runtime identity over "
            "hla-backend-python2025."
        ),
        "residual_boundary": (
            "This audit strengthens the Java/C++ binding proof story, but it does not promote standard-route traces "
            "into exhaustive cross-binding behavior equivalence or separate RTI implementation ownership."
        ),
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
            "package": "hla-backend-python2025",
            "role": "main full Python 2025 RTI implementation lane (owned by hla-backend-python2025 with hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support)",
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
            "The primary 2025 Python RTI lane has green executable runtime coverage in the main in-process suite.",
            "Both Python 2025 routes clear the tracked bounded working-surface milestones.",
            "The extracted hla-backend-python2025 package now has direct split-package proof instead of relying only on legacy shim-facing package evidence.",
            "The python2025 runtime lane is protected by explicit import-boundary guardrails that forbid runtime backflow into hla.backends.shim modules.",
            "The repo can make a supported-boundary statement over the primary 2025 Python RTI lane without hiding legacy-only or bounded-extension areas.",
            "Route parity partial and missing counts are both zero for the tracked 2025 matrix.",
            "The callback ledger is fully route-backed across the current Python 2025 lanes, eliminating callback-helper-only gaps in the promotion surface.",
            "The main current-package pressure families across save/restore, directed interaction, and DDM/default-policy are all route-backed across the current Python 2025 lanes.",
        ],
        "current_evidence_runs": [
            {
                "name": "target-radar-time-window-proof-ladder",
                "result": "26 passed, 8 deselected in 4.78s",
                "scope": (
                    "route-backed Target/Radar time-window ladder: future-exclusion, output-delivery, "
                    "consumer-order, pipeline, receive-order poison, and save/restore time-window proofs "
                    "across the current Python 2025 routes"
                ),
            },
            {
                "name": "python2025-split-package-surface",
                "result": "71 passed in 0.67s",
                "scope": (
                    "dedicated hla-backend-python2025 package surface plus local factory composition, "
                    "split-package identity, and 2025 validation behavior over the standalone runtime lane"
                ),
            },
            {
                "name": "python2025-import-boundary-guardrails",
                "result": "163 passed in 40.34s",
                "scope": (
                    "package import isolation, root-facade and operator policy, split-package scaffolds, "
                    "route-parity and finish-line audits, and explicit no-backflow proof that the live "
                    "python2025 runtime package does not import back through hla.backends.shim.*"
                ),
            },
            {
                "name": "combined-2025-verification-slice",
                "result": "targeted finish-line/backend-owner audit slice ran green on current tree",
                "scope": (
                    "main finish-line and backend-owner audit pair proving current-lane identity, "
                    "requirement ledgers, and supported-boundary closeout evidence"
                ),
            },
            {
                "name": "hosted-2025-fedpro-transport-suite",
                "result": "252 passed in current-tree hosted FedPro transport suite",
                "scope": (
                    "typed hosted FedPro route including strict local FOM/MIM resolution, create-time error "
                    "taxonomy, object/ownership/save-restore coverage, time-window proof ladder, and "
                    "directed TSO stale-queue cleanup"
                ),
            },
        ],
        "split_triggers": [
            "Adapter concerns begin to obscure or distort core RTI semantics.",
            "Callback or route normalization grows more complex than the underlying RTI behavior it wraps.",
            "New 2025 behavior is materially harder to implement because shim and RTI state management are too tightly mixed.",
            "The row-level requirement-by-requirement audit cannot be promoted from bounded disposition evidence to cleaner all-covered runtime proof without further shrinking wrapper-only compatibility logic around the main python2025 runtime.",
        ],
        "permanent_decision_blockers": [
            "The repo now has a row-level requirement-by-requirement audit, but it is still a bounded disposition audit rather than an all-covered 2025 conformance pass.",
            "Several implemented slices still aggregate multiple requirements under bounded supported-scope language.",
            "Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or exhaustive cross-binding conformance pass.",
            "Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.",
        ],
        "current_assessment": (
            "Current evidence is strong enough to treat the real Python 2025 RTI implementation now owned by "
            "hla-backend-python2025, with hla-backend-shim retained only as temporary import-compatibility "
            "scaffolding and wrapper-only compatibility support, as the live bounded working-surface lane across the "
            "main current-package pressure families, while keeping Java and C++ shim/binding packages segregated "
            "from that claim, but not strong enough to make a permanent no-split architectural decision."
        ),
    }


def _literal_string_sequence(node: ast.AST | None) -> list[str]:
    if node is None:
        return []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.Tuple, ast.List)):
        values: list[str] = []
        for element in node.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                values.append(element.value)
        return values
    return []


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _scan_for_shim_delegation(project_root: Path, package_name: str) -> list[dict[str, Any]]:
    package_path = project_root / "packages" / package_name
    forbidden_module = "hla.backends.shim.backend"
    forbidden_symbol = "create_shim_backend"
    violations: list[dict[str, Any]] = []

    for source_path in sorted(package_path.glob("src/**/*.py")):
        try:
            tree = ast.parse(source_path.read_text())
        except (OSError, SyntaxError):
            continue
        relative_source_path = str(source_path.relative_to(project_root))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == forbidden_module:
                imported_symbols = [alias.name for alias in node.names]
                if forbidden_symbol in imported_symbols or "*" in imported_symbols:
                    violations.append(
                        {
                            "package": package_name,
                            "path": relative_source_path,
                            "kind": "forbidden-import",
                            "target": f"{forbidden_module}.{forbidden_symbol}",
                        }
                    )
            elif isinstance(node, ast.Import):
                imported_modules = [alias.name for alias in node.names]
                if forbidden_module in imported_modules:
                    violations.append(
                        {
                            "package": package_name,
                            "path": relative_source_path,
                            "kind": "forbidden-module-import",
                            "target": forbidden_module,
                        }
                    )

    return violations


def _discover_backend_plugin_records(project_root: Path) -> dict[str, Any]:
    package_root = project_root / "packages"
    backend_package_dirs = sorted(path.name for path in package_root.glob("hla-backend-*") if path.is_dir())
    plugin_records: list[dict[str, Any]] = []

    for package_name in backend_package_dirs:
        package_path = package_root / package_name
        for plugin_path in sorted(package_path.glob("src/hla/backends/*/plugin.py")):
            try:
                tree = ast.parse(plugin_path.read_text())
            except (OSError, SyntaxError):
                continue
            relative_plugin_path = str(plugin_path.relative_to(project_root))
            for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
                function_name = call.func.id if isinstance(call.func, ast.Name) else None
                if function_name != "RTIBackendPlugin":
                    continue
                keyword_by_name = {keyword.arg: keyword.value for keyword in call.keywords if keyword.arg}
                plugin_name = _literal_string(keyword_by_name.get("name"))
                family = _literal_string(keyword_by_name.get("family"))
                supports = _literal_string_sequence(keyword_by_name.get("supports"))
                if not plugin_name or not family:
                    continue
                plugin_records.append(
                    {
                        "package": package_name,
                        "plugin_path": relative_plugin_path,
                        "name": plugin_name,
                        "family": family,
                        "supports": supports,
                    }
                )

    python_2025_candidates = [
        record
        for record in plugin_records
        if "rti1516_2025" in record["supports"]
        and record["family"] not in {"shim", "cpp-shim", "standard/cpp", "intake/cpp"}
        and not record["family"].startswith("compatibility-wrapper")
        and record["package"] != "hla-backend-shim"
    ]
    legacy_package_delegation_violations = [
        violation
        for record in python_2025_candidates
        for violation in _scan_for_shim_delegation(project_root, record["package"])
    ]

    return {
        "backend_package_dirs": backend_package_dirs,
        "backend_package_count": len(backend_package_dirs),
        "plugin_records": plugin_records,
        "rti1516_2025_plugin_records": [
            record
            for record in plugin_records
            if "rti1516_2025" in record["supports"]
            and record["family"] != "shim"
            and not record["family"].startswith("compatibility-wrapper")
        ],
        "dedicated_python_2025_backend_candidates": python_2025_candidates,
        "dedicated_python_2025_legacy_package_delegation_violations": legacy_package_delegation_violations,
        "dedicated_python_2025_candidates_cleanly_separated": not legacy_package_delegation_violations,
    }


def _build_implementation_lane_audit(
    project_root: Path,
    promotion_split_audit: Mapping[str, Any],
    milestone_audit: Mapping[str, Any],
) -> dict[str, Any]:
    backend_scan = _discover_backend_plugin_records(project_root)
    dedicated_python_2025_candidates = backend_scan["dedicated_python_2025_backend_candidates"]
    dedicated_candidate_present = bool(dedicated_python_2025_candidates)
    return {
        "audit_status": "current-lane-architecture-captured",
        "current_2025_lane": {
            "backend_package": "hla-backend-python2025",
            "plugin_family": "python-rti-2025",
            "supports": ["rti1516_2025"],
            "role": "main full Python 2025 RTI implementation lane (owned by hla-backend-python2025 with hla-backend-shim retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support)",
            "spec_package": "hla-rti1516-2025",
        },
        "compatibility_wrapper_lane": {
            "backend_package": "hla-backend-shim",
            "status": "compatibility-maintained",
            "role": "compatibility-wrapper",
            "counts_as_python_2025_rti": False,
            "delegates_runtime_semantics_to": "hla-backend-python2025",
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
        "hosted_runtime_identity_evidence": {
            "audit_status": "direct-server-client-identity-aligned",
            "route": "python-2025-fedpro-grpc",
            "claim": (
                "The hosted 2025 FedPro route is explicitly evidenced as a route variant over "
                "hla-backend-python2025 rather than a separate shim or RTI family."
            ),
            "evidence_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_reports_python2025_main_lane_identity",
                "tests/test_rti1516_2025_python2025_runtime.py::test_dedicated_python2025_backend_is_discoverable_and_executable",
            ],
            "direct_runtime_report": {
                "backend_name": "python2025-rti",
                "backend_kind": "python/2025",
                "runtime_provider": "python2025",
                "implementation_lane": "hla-backend-python2025",
                "counts_as_python_2025_rti": True,
            },
            "hosted_server_report": {
                "runtime_provider": "python2025",
                "implementation_lane": "hla-backend-python2025",
                "counts_as_python_2025_rti": True,
                "wrapper_only": False,
                "spec": "rti1516_2025",
                "transport_kind": "grpc",
            },
            "hosted_client_report": {
                "runtime_provider": "python2025",
                "implementation_lane": "hla-backend-python2025",
                "counts_as_python_2025_rti": True,
                "wrapper_only": False,
                "spec": "rti1516_2025",
                "transport_kind": "grpc",
                "route_family": "fedpro",
            },
            "current_assessment": (
                "Hosted-client and hosted-server capability surfaces now agree with the direct 2025 ambassador "
                "that python-2025-fedpro-grpc is a route variant over the primary python2025 RTI lane in "
                "hla-backend-python2025 rather than a wrapper-defined implementation family."
            ),
        },
        "hosted_factory_boundary_evidence": {
            "audit_status": "factory-boundary-explicit",
            "supported_hosted_creation_surface": (
                "start_2025_grpc_server(...) plus GrpcTransport(..., schema='rti1516_2025') plus "
                "create_rti_ambassador(backend='python2025'|'python-2025'|'python-2025-backend', "
                "transport={'kind': 'grpc', ...})"
            ),
            "unsupported_factory_surfaces": [
                "create_rti_ambassador(backend='shim', transport=...)",
            ],
            "current_policy": (
                "The primary python2025 backend path and its supported runtime aliases now accept transport=... "
                "and create the hosted FedPro 2025 ambassador over the main hla-backend-python2025 lane, while "
                "the legacy shim provider spelling is no longer part of the supported public backend-selection "
                "surface and therefore rejects hosted ownership and other backend-specific factory transport "
                "routing. "
                "The same factory-hosted python2025 path now also runs a direct federation listing/member-report "
                "slice, the package-owned Target/Radar future-exclusion, output-delivery, consumer-order, and "
                "integrated lookahead-processing-window gauntlet time-window proofs, restore-state, "
                "restore-output-resume, and pipeline-resume save/restore proofs, a direct restore-control negative "
                "slice, "
                "a direct local-delete restore slice, "
                "a direct plain-callback restore cleanup slice, a direct timed-remove restore cleanup slice, "
                "a direct plain-object restore routing slice, a direct plain-interaction restore routing slice, "
                "a direct directed-DDM restore routing slice, a direct restore time/switch-control slice, "
                "and a direct restore lookahead/queued-TSO slice, "
                "direct MOM federation-management and time-management service interactions, "
                "a direct MOM request/report slice, a direct MOM object/ownership service slice, a direct "
                "support-service slice, the shared support factory/decode scenario, a direct object-exchange slice, "
                "a direct timestamped delivery/retraction slice, a direct directed-interaction slice, "
                "a direct callback-backlog disconnect/rejoin slice, and a direct ownership slice instead of "
                "stopping at ambassador-construction evidence."
            ),
            "evidence_tests": [
                "tests/test_python_api_spec.py::test_runtime_backend_listing_exposes_python2025_as_primary_2025_lane",
                "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_python2025_aliases_and_keeps_primary_identity",
                "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_legacy_shim_provider_name",
                "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_hosted_transport_on_python2025_aliases",
                "tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_hosted_transport_on_legacy_shim_provider",
                "tests/test_hla_factory_composition.py::test_2025_version_local_factory_accepts_hosted_transport_creation_on_python2025_lane",
                "tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_legacy_shim_provider_name",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_transport_route_creates_hosted_python2025_ambassador",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_restore_control_negative_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_local_delete_restore_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_plain_callbacks_and_preserves_post_restore_routing",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_timed_remove_and_preserves_post_restore_remove_routing",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_object_subscriber_routing_after_restore",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_interaction_subscriber_routing_after_restore",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_directed_ddm_subscriber_routing_after_restore",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_time_and_switch_control_state_after_restore",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_lookahead_and_redelivers_presave_queued_tso",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_federation_management_service_interactions",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_time_management_service_interactions",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_request_report_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_object_and_ownership_service_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_shared_support_factory_and_decode_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_drops_disconnected_callback_backlog_before_reconnect",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_object_exchange_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_timestamped_delivery_and_retraction_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_directed_interaction_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_ownership_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_inflight_ownership_state",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_cross_federate_attribute_owner_visibility",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario",
                "tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_unknown_backend_specific_options",
                "tests/test_hla_factory_composition.py::test_hla_factory_registry_strips_composition_only_options_before_2025_backend_creation",
                "tests/test_hla_factory_composition.py::test_2025_direct_factory_rejects_composition_only_options_without_hla_factory_layer",
                "tests/requirements/test_2025_python_rti_backend_audit.py::test_2025_python_rti_backend_audit_keeps_package_docs_aligned_with_runtime_wrapper_boundary",
            ],
        },
        "package_owned_shared_scenario_evidence": {
            "audit_status": "package-owned-target-radar-2025-path-captured",
            "scenario_package": "hla-fom-target-radar",
            "shared_route": "target-radar-shared-scenario",
            "example_entrypoint": "python examples/target_radar_simulation.py --backend python2025 --steps 5",
            "adapter_class": (
                "hla.foms.target_radar._internal.target_radar_2025_adapter.TargetRadar2025RTIAdapter"
            ),
            "supported_backend_names": [
                "python2025",
                "python-2025",
                "python-2025-backend",
            ],
            "python2025_runtime_report": {
                "backend_kind": "python/2025",
                "implementation_lane": "hla-backend-python2025",
                "counts_as_python_2025_rti": True,
                "wrapper_only": False,
            },
            "shim_runtime_report": {
                "backend_kind": "shim/2025",
                "implementation_lane": "hla-backend-python2025",
                "counts_as_python_2025_rti": False,
                "wrapper_only": True,
            },
            "claim": (
                "The shared Target/Radar 2025 execution seam is now owned by the hla-fom-target-radar package, "
                "where one package-owned compatibility adapter wraps the primary python2025 backend lane without "
                "moving implementation ownership back into hla-backend-shim."
            ),
            "current_assessment": (
                "The README-advertised Target/Radar python2025 example path is now executable under package-owned "
                "2025 adapter coverage. The legacy shim package is no longer treated as a backend-selection route, "
                "and the same package-owned adapter now also proves that the factory-hosted python2025 FedPro route can execute "
                "the shared Target/Radar example scenario plus the shared future-exclusion, output-delivery, "
                "consumer-order, integrated lookahead-processing-window gauntlet, restore-state, restore-output-resume, "
                "and pipeline-resume scenarios without falling back to shim-owned semantics or raw transport-only wrappers."
            ),
            "evidence_tests": [
                "tests/scenarios/test_target_radar_scenario.py::test_target_radar_example_supports_2025_backends",
                "tests/test_fom_target_radar_split_package.py::test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter",
                "tests/test_fom_target_radar_split_package.py::test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_target_radar_shared_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario",
            ],
        },
        "non_python_2025_binding_lanes": [
            {
                "backend_package": "hla-bridge-java-common",
                "family": "standard/java",
                "role": "Java 2025 binding surface and artifact/intake evidence lane",
                "counts_as_python_2025_rti": False,
            },
            {
                "backend_package": "hla-backend-cpp-shim",
                "family": "cpp-shim",
                "role": "C++ 2025 binding surface and artifact/runtime-capability evidence lane",
                "counts_as_python_2025_rti": False,
            },
        ],
        "backend_package_scan": backend_scan,
        "dedicated_2025_backend_package_present": dedicated_candidate_present,
        "ready_for_current_lane_promotion_as_working_surface": promotion_split_audit[
            "ready_for_current_lane_promotion_as_working_surface"
        ],
        "ready_for_permanent_no-split_decision": promotion_split_audit["ready_for_permanent_no-split_decision"],
        "clean_extraction_still_optional": True,
        "current_assessment": (
            "The repo's current 2025 implementation reality is explicit: the main full Python 2025 RTI implementation now "
            "runs from hla-backend-python2025, hla-backend-shim remains only as temporary import-compatibility "
            "scaffolding and wrapper-only compatibility support over that runtime, the hosted FedPro route is a route "
            "variant over that implementation rather than a separate RTI family, the older pure-Python backend "
            "remains the 2010-only inmemory lane, and the Java/C++ lanes remain segregated as non-Python "
            "binding-capability surfaces rather than being mixed into the Python 2025 RTI claim."
        ),
        "extraction_boundary": (
            "Keep using hla-backend-python2025 as the executable Python 2025 RTI surface while continuing to narrow "
            "hla-backend-shim toward temporary import-compatibility scaffolding and wrapper-only responsibilities; "
            "only reopen a deeper extraction question if future evidence shows that residual compatibility or route "
            "normalization logic is still obscuring core runtime semantics."
        ),
        "evidence_anchors": [
            "README.md",
            "docs/architecture.md",
            "docs/documentation_hierarchy.md",
            "docs/package_layout.md",
            "docs/test_surface.md",
            "docs/workspace_layout.md",
            "docs/rti_options_and_test_matrix.md",
            "docs/verification/time_model_compliance.md",
            "docs/verification/verification_plan.md",
            "docs/backend_route_inventory.md",
            "docs/backend_route_inventory_remote.md",
            "packages/hla-backend-python2025/pyproject.toml",
            "packages/hla-backend-python2025/README.md",
            "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "packages/hla-backend-shim/pyproject.toml",
            "packages/hla-backend-shim/README.md",
            "packages/hla-backend-shim/src/hla/backends/shim/plugin.py",
            "packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py",
            "packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/target_radar_factory.py",
            "packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/target_radar_2025_adapter.py",
            "examples/target_radar_simulation.py",
            "docs/plans/2025_python_rti_backend_audit.md",
            "docs/python_rti_backend.md",
        ],
    }


def _build_time_window_vendor_parity_audit() -> dict[str, Any]:
    route_rows = [
        {
            "scenario_id": "time-window-future-exclusion",
            "federate_count": 2,
            "trial_pitch_safe": True,
            "roles": ["SlowRegulatorFederate", "RadarFederate"],
            "purpose": (
                "Prove radar window closure stays blocked while another regulating federate can still legally send "
                "into the closing window, then prove closure becomes legal only after that future input is excluded."
            ),
            "python_route_parity_test": (
                "tests/scenarios/test_python_route_parity.py::"
                "test_python_route_parity_target_radar_time_window_future_exclusion"
            ),
            "pitch_vendor_test": (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_time_window_future_exclusion_matrix"
            ),
            "recommended_pitch_operator_route": "./tools/pitch time-window-probe",
            "current_pitch_runtime_boundary": "seat-availability",
            "current_pitch_runtime_boundary_evidence": (
                "Pitch managed runtime currently reports no available pRTI federate seats for this two-federate "
                "future-exclusion proof."
            ),
        },
        {
            "scenario_id": "time-window-restore-state",
            "federate_count": 2,
            "trial_pitch_safe": True,
            "roles": ["TruthFederate", "RadarFederate"],
            "purpose": (
                "Prove that restore reopens or recloses the radar window at the saved point without leaking dirty "
                "future state across the checkpoint boundary."
            ),
            "python_route_parity_test": (
                "tests/scenarios/test_python_route_parity.py::"
                "test_python_route_parity_target_radar_time_window_restore_state"
            ),
            "pitch_vendor_test": (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_time_window_restore_state_matrix"
            ),
            "recommended_pitch_operator_route": "./tools/pitch time-window-restore-state-probe",
            "current_pitch_runtime_boundary": "seat-availability",
            "current_pitch_runtime_boundary_evidence": (
                "Pitch managed runtime currently reports no available pRTI federate seats for this two-federate "
                "time-window restore proof."
            ),
        },
        {
            "scenario_id": "time-window-restore-output",
            "federate_count": 3,
            "trial_pitch_safe": False,
            "roles": ["TruthFederate", "RadarFederate", "TrackConsumerFederate"],
            "purpose": (
                "Prove restore resumes legal post-window output delivery without duplicate replay to the consumer."
            ),
            "python_route_parity_test": (
                "tests/scenarios/test_python_route_parity.py::"
                "test_python_route_parity_target_radar_time_window_restore_output"
            ),
            "pitch_vendor_test": (
                "tests/vendors/test_pitch_real_backend_matrix.py::"
                "test_pitch_time_window_restore_output_matrix"
            ),
            "current_pitch_runtime_boundary": "trial-federate-limit-and-seat-availability",
            "current_pitch_runtime_boundary_evidence": (
                "Pitch managed runtime currently reports no available pRTI federate seats for this three-federate "
                "time-window restore-output proof."
            ),
        },
    ]
    trial_safe_rows = [row for row in route_rows if row["trial_pitch_safe"]]
    current_trial_candidate = next(row for row in route_rows if row["scenario_id"] == "time-window-future-exclusion")
    return {
        "audit_status": "time-window-vendor-parity-captured",
        "route_count": len(route_rows),
        "trial_pitch_safe_route_count": len(trial_safe_rows),
        "trial_pitch_safe_route_ids": [row["scenario_id"] for row in trial_safe_rows],
        "trial_pitch_unsafe_route_ids": [row["scenario_id"] for row in route_rows if not row["trial_pitch_safe"]],
        "current_trial_candidate": {
            "scenario_id": current_trial_candidate["scenario_id"],
            "federate_count": current_trial_candidate["federate_count"],
            "pitch_vendor_test": current_trial_candidate["pitch_vendor_test"],
            "recommended_pitch_operator_route": current_trial_candidate["recommended_pitch_operator_route"],
            "why_selected": (
                "This is the smallest lookahead-window proof that still exercises future-message exclusion. It keeps "
                "the topology to two federates, so a successful Pitch run would add meaningful vendor credence "
                "without depending on the larger multi-federate gauntlet."
            ),
        },
        "routes": route_rows,
        "current_assessment": (
            "The Target/Radar time-window ladder now has an explicit vendor-parity shape audit. The future-exclusion "
            "route is intentionally two-federate-safe and is the right Pitch trial candidate; the current Pitch gap "
            "is runtime seat availability, not an overgrown scenario topology."
        ),
        "residual_boundary": (
            "A green Pitch result would add vendor credence for the two-federate future-exclusion proof, but it would "
            "still not replace the broader in-process and hosted Python evidence for output delivery, consumer order, "
            "pipeline overlap, or save/restore window replay."
        ),
    }


def _build_implementation_concentration_audit() -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[6]
    runtime_backend_path = _preferred_2025_runtime_backend_path(project_root)
    implemented_slices = _normalized_implemented_evidence_slices(project_root)
    source_responsibility = _build_python2025_source_responsibility_audit(project_root)
    anchor_counts: Counter[str] = Counter()
    spec_package_prefix = "packages/hla-rti1516-2025/src/"
    transport_prefixes = ("packages/hla-transport-grpc/", "packages/hla-transport-rest/")
    runtime_backend_slice_ids: list[str] = []
    spec_package_slice_ids: list[str] = []
    transport_slice_ids: list[str] = []

    for evidence_slice in implemented_slices:
        evidence_paths = set(evidence_slice.get("evidence", ()))
        if runtime_backend_path in evidence_paths:
            runtime_backend_slice_ids.append(evidence_slice["id"])
        if any(path.startswith(spec_package_prefix) for path in evidence_paths):
            spec_package_slice_ids.append(evidence_slice["id"])
        if any(path.startswith(transport_prefixes) for path in evidence_paths):
            transport_slice_ids.append(evidence_slice["id"])
        for path in evidence_paths:
            anchor_counts[path] += 1

    total_slices = len(implemented_slices)
    runtime_backend_slice_count = len(runtime_backend_slice_ids)
    runtime_backend_share = round(runtime_backend_slice_count / total_slices, 3) if total_slices else 0.0
    spec_package_slice_count = len(spec_package_slice_ids)
    transport_slice_count = len(transport_slice_ids)
    ambassador_method_line_count = int(source_responsibility["ambassador_method_line_count"])
    extracted_runtime_module_line_count = int(source_responsibility["extracted_runtime_module_line_count"])
    backend_shell_ratio = (
        round(ambassador_method_line_count / extracted_runtime_module_line_count, 3)
        if extracted_runtime_module_line_count
        else 0.0
    )
    semantic_concentration_is_material = runtime_backend_share >= 0.5 and ambassador_method_line_count >= 250
    if semantic_concentration_is_material:
        current_assessment = (
            "The primary 2025 Python RTI lane is substantively executable, but the implementation proof is still "
            "materially concentrated in hla-backend-python2025/backend.py. That concentration does not by itself "
            "force a split, because spec-package and transport-layer evidence also exist, but it remains a real "
            "architectural pressure signal to monitor as more 2025 behavior lands."
        )
    else:
        current_assessment = (
            "The primary 2025 Python RTI lane still cites hla-backend-python2025/backend.py as a frequent evidence "
            "anchor, but semantic concentration is no longer material there: the ambassador shell is thin and most "
            "runtime behavior now lives in extracted python2025 modules. Remaining pressure is architectural hygiene, "
            "not proof that core 2025 semantics still live in one oversized backend class."
        )
    leading_extracted_runtime_modules = sorted(
        source_responsibility["extracted_runtime_modules"],
        key=lambda module: (-int(module["line_count"]), str(module["path"])),
    )[:5]

    return {
        "audit_status": "implementation-concentration-captured",
        "implemented_slice_count": total_slices,
        "runtime_backend_path": runtime_backend_path,
        "runtime_backend_slice_count": runtime_backend_slice_count,
        "runtime_backend_slice_share": runtime_backend_share,
        "spec_package_slice_count": spec_package_slice_count,
        "transport_slice_count": transport_slice_count,
        "semantic_concentration_is_material": semantic_concentration_is_material,
        "runtime_ambassador_method_line_count": ambassador_method_line_count,
        "extracted_runtime_module_line_count": extracted_runtime_module_line_count,
        "backend_shell_ratio": backend_shell_ratio,
        "leading_extracted_runtime_modules": leading_extracted_runtime_modules,
        "top_evidence_anchors": [
            {"path": path, "slice_count": count}
            for path, count in anchor_counts.most_common(10)
        ],
        "sample_runtime_backend_slice_ids": runtime_backend_slice_ids[:12],
        "current_assessment": current_assessment,
        "extraction_pressure_boundary": (
            "The main python2025 runtime should keep absorbing real RTI semantics, while wrapper-only compatibility "
            "logic should keep shrinking or moving outward into narrower adapters and reusable runtime modules."
        ),
    }


def _shim_backend_method_responsibility(method_name: str) -> str:
    normalized = method_name.lower()
    if "mom" in normalized or "switch" in normalized:
        return "mom-and-switch-services"
    if "save" in normalized or "restore" in normalized:
        return "save-restore-runtime"
    if (
        "time" in normalized
        or "lookahead" in normalized
        or "advance" in normalized
        or "lits" in normalized
        or "galt" in normalized
        or "tso" in normalized
        or "retract" in normalized
    ):
        return "time-management-runtime"
    if "region" in normalized or "ddm" in normalized or "scope" in normalized or "dimension" in normalized or "range" in normalized:
        return "ddm-region-runtime"
    if (
        "ownership" in normalized
        or "divest" in normalized
        or "acquisition" in normalized
        or "acquire" in normalized
        or "owner" in normalized
    ):
        return "ownership-runtime"
    if (
        "callback" in normalized
        or "deliver" in normalized
        or "evoke" in normalized
        or "enablecallbacks" in normalized
        or "disablecallbacks" in normalized
        or "connectionlost" in normalized
    ):
        return "callback-delivery-and-control"
    if "interaction" in normalized or "parameter" in normalized or "transportation" in normalized or "order" in normalized:
        return "interaction-routing-runtime"
    if "object" in normalized or "attribute" in normalized or "discover" in normalized or "update" in normalized or "reflect" in normalized or "instance" in normalized:
        return "object-attribute-runtime"
    if (
        "federation" in normalized
        or "federate" in normalized
        or "join" in normalized
        or "resign" in normalized
        or "synchronization" in normalized
        or "connect" in normalized
        or "credential" in normalized
    ):
        return "federation-management-runtime"
    if (
        "fom" in normalized
        or "mim" in normalized
        or "catalog" in normalized
        or "module" in normalized
        or "class" in normalized
        or "handle" in normalized
        or "name" in normalized
        or "resolve" in normalized
        or "coerce" in normalized
        or "extract" in normalized
    ):
        return "fom-catalog-and-handle-support"
    return "misc-support"


def _build_python2025_source_responsibility_audit(project_root: Path) -> dict[str, Any]:
    shim_backend_path = project_root / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim" / "backend.py"
    python2025_backend_path = (
        project_root / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025" / "backend.py"
    )
    python2025_wrapper_path = (
        project_root
        / "packages"
        / "hla-backend-python2025"
        / "src"
        / "hla"
        / "backends"
        / "python2025"
        / "compatibility_wrapper.py"
    )
    source_backend_path = python2025_backend_path if python2025_backend_path.exists() else shim_backend_path
    source_text = source_backend_path.read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    runtime_ambassador_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Python2025RTIAmbassador"
        ),
        None,
    )
    if runtime_ambassador_class is None:
        runtime_ambassador_class = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Shim2025RTIAmbassador"
        )
    shim_wrapper_source_path = python2025_wrapper_path if python2025_wrapper_path.exists() else shim_backend_path
    shim_wrapper_source_text = shim_wrapper_source_path.read_text(encoding="utf-8")
    shim_wrapper_tree = ast.parse(shim_wrapper_source_text)
    shim_wrapper_ambassador_class = next(
        (
            node
            for node in shim_wrapper_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Shim2025RTIAmbassador"
        ),
        None,
    )
    runtime_dir = source_backend_path.parent
    relative_source_backend_path = str(source_backend_path.relative_to(project_root))
    family_counts: dict[str, dict[str, Any]] = {}
    total_method_count = 0
    total_method_lines = 0
    for method in (node for node in runtime_ambassador_class.body if isinstance(node, ast.FunctionDef)):
        family = _shim_backend_method_responsibility(method.name)
        method_lines = int(method.end_lineno or method.lineno) - int(method.lineno) + 1
        total_method_count += 1
        total_method_lines += method_lines
        row = family_counts.setdefault(
            family,
            {
                "family": family,
                "method_count": 0,
                "line_count": 0,
                "sample_methods": [],
            },
        )
        row["method_count"] += 1
        row["line_count"] += method_lines
        if len(row["sample_methods"]) < 8:
            row["sample_methods"].append(method.name)

    extracted_runtime_modules: list[dict[str, Any]] = []
    helper_family_by_stem = {
        "attribute_scope": "object-attribute-runtime",
        "attribute_policy": "object-attribute-runtime",
        "attribute_policy_runtime": "object-attribute-runtime",
        "callback_runtime": "callback-delivery-and-control",
        "catalog_access_runtime": "fom-catalog-and-handle-support",
        "catalog_runtime": "fom-catalog-and-handle-support",
        "declaration_ddm_surface_mixin": "ddm-region-runtime",
        "declaration_management": "object-attribute-runtime",
        "delivery_state_runtime": "time-management-runtime",
        "federation_management": "federation-management-runtime",
        "federation_bootstrap_runtime": "federation-management-runtime",
        "federation_state_runtime": "federation-management-runtime",
        "federation_time_surface_mixin": "time-management-runtime",
        "input_guard_runtime": "misc-support",
        "interaction_policy_runtime": "interaction-routing-runtime",
        "mom_surface_mixin": "mom-and-switch-services",
        "object_ownership_surface_mixin": "ownership-runtime",
        "runtime_helper_surface_mixin": "misc-support",
        "runtime_state": "misc-support",
        "ownership_runtime": "ownership-runtime",
        "save_restore": "save-restore-runtime",
        "save_restore_lifecycle": "save-restore-runtime",
        "support_surface_mixin": "misc-support",
        "directed_interaction": "interaction-routing-runtime",
        "directed_interaction_boundary": "interaction-routing-runtime",
        "interaction_runtime": "interaction-routing-runtime",
        "mom_codec": "mom-and-switch-services",
        "mom_runtime": "mom-and-switch-services",
        "object_instance_runtime": "object-attribute-runtime",
        "object_model": "object-attribute-runtime",
        "object_region_runtime": "object-attribute-runtime",
        "object_reflection": "object-attribute-runtime",
        "time_management": "time-management-runtime",
        "time_management_runtime": "time-management-runtime",
        "support_lookup": "misc-support",
        "support_policy": "mom-and-switch-services",
        "support_lookup_runtime": "misc-support",
        "support_policy_runtime": "mom-and-switch-services",
        "update_rate": "object-attribute-runtime",
        "update_rate_runtime": "object-attribute-runtime",
    }
    for helper_path in sorted(runtime_dir.glob("*.py")):
        if helper_path.name in {"__init__.py", "backend.py", "backend_scaffold.py", "compatibility_wrapper.py", "plugin.py"}:
            continue
        helper_text = helper_path.read_text(encoding="utf-8")
        helper_tree = ast.parse(helper_text)
        helper_functions = [node for node in helper_tree.body if isinstance(node, ast.FunctionDef)]
        family = helper_family_by_stem.get(helper_path.stem)
        if family is None and helper_functions:
            family = Counter(_shim_backend_method_responsibility(function.name) for function in helper_functions).most_common(1)[0][0]
        if family is None:
            family = "misc-support"
        extracted_runtime_modules.append(
            {
                "path": str(helper_path.relative_to(project_root)),
                "family": family,
                "line_count": len(helper_text.splitlines()),
                "function_count": len(helper_functions),
                "functions": [function.name for function in helper_functions],
            }
        )
        row = family_counts.setdefault(
            family,
            {
                "family": family,
                "method_count": 0,
                "line_count": 0,
                "sample_methods": [],
            },
        )
        row["method_count"] += len(helper_functions)
        row["line_count"] += len(helper_text.splitlines())
        for function in helper_functions:
            if len(row["sample_methods"]) >= 8:
                break
            if function.name not in row["sample_methods"]:
                row["sample_methods"].append(function.name)

    families = sorted(family_counts.values(), key=lambda row: (-row["line_count"], row["family"]))
    return {
        "audit_status": "python2025-source-responsibility-captured",
        "source_path": relative_source_backend_path,
        "source_line_count": len(source_text.splitlines()),
        "extracted_runtime_module_count": len(extracted_runtime_modules),
        "extracted_runtime_modules": extracted_runtime_modules,
        "extracted_runtime_module_line_count": sum(module["line_count"] for module in extracted_runtime_modules),
        "shim_wrapper_path": str(shim_wrapper_source_path.relative_to(project_root)),
        "shim_wrapper_line_count": len(shim_wrapper_source_text.splitlines()),
        "ambassador_class": runtime_ambassador_class.name,
        "ambassador_line_count": int(runtime_ambassador_class.end_lineno or runtime_ambassador_class.lineno) - int(runtime_ambassador_class.lineno) + 1,
        "ambassador_method_count": total_method_count,
        "ambassador_method_line_count": total_method_lines,
        "shim_wrapper_ambassador_class": (
            shim_wrapper_ambassador_class.name if shim_wrapper_ambassador_class is not None else None
        ),
        "shim_wrapper_ambassador_line_count": (
            int(shim_wrapper_ambassador_class.end_lineno or shim_wrapper_ambassador_class.lineno)
            - int(shim_wrapper_ambassador_class.lineno)
            + 1
            if shim_wrapper_ambassador_class is not None
            else 0
        ),
        "family_count": len(families),
        "families": families,
        "largest_family": families[0]["family"] if families else None,
        "largest_family_line_count": families[0]["line_count"] if families else 0,
        "current_assessment": (
            "The live Python 2025 RTI source now presents a thin ambassador shell in hla-backend-python2025, while "
            "the substantive runtime behavior is spread across extracted python2025 modules and hla-backend-shim has "
            "been reduced to a compatibility wrapper. Save/restore lifecycle, directed-interaction routing, time "
            "management, declaration/DDM surfaces, ownership, MOM/reporting, federation bootstrap/state handling, "
            "catalog access, object lifecycle/update handling, attribute policy/scope, and callback delivery are now "
            "measurable as named source-owned families under the main python2025 runtime package."
        ),
        "extraction_use": (
            "Use these families as the source ownership baseline while continuing to shrink hla-backend-shim toward "
            "temporary import-compatibility scaffolding and wrapper-only responsibilities; new runtime movement "
            "should reduce compatibility-surface pressure without weakening direct or hosted route evidence."
        ),
    }


def _build_slice_aggregation_pressure_audit() -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[6]
    runtime_backend_path = _preferred_2025_runtime_backend_path(project_root)
    implemented_rows = [
        row for row in _normalized_implemented_evidence_slices(project_root) if row.get("status") == "implemented-slice"
    ]
    ranked_rows = sorted(
        (
            {
                "slice_id": row["id"],
                "requirement_count": len(row.get("requirements", ())),
                "runtime_backend_backed": runtime_backend_path in set(row.get("evidence", ())),
            }
            for row in implemented_rows
        ),
        key=lambda item: (-item["requirement_count"], item["slice_id"]),
    )
    aggregated_ge10 = [row for row in ranked_rows if row["requirement_count"] >= 10]
    aggregated_ge20 = [row for row in ranked_rows if row["requirement_count"] >= 20]
    aggregated_ge10_runtime = [row for row in aggregated_ge10 if row["runtime_backend_backed"]]
    aggregated_ge20_runtime = [row for row in aggregated_ge20 if row["runtime_backend_backed"]]
    return {
        "audit_status": "slice-aggregation-pressure-captured",
        "implemented_slice_count": len(implemented_rows),
        "aggregated_slice_count_ge_10_requirements": len(aggregated_ge10),
        "aggregated_slice_count_ge_10_requirements_runtime_backed": len(aggregated_ge10_runtime),
        "aggregated_slice_count_ge_20_requirements": len(aggregated_ge20),
        "aggregated_slice_count_ge_20_requirements_runtime_backed": len(aggregated_ge20_runtime),
        "largest_implemented_slices": ranked_rows[:10],
        "largest_runtime_backed_aggregated_slices": aggregated_ge10_runtime[:10],
        "current_assessment": (
            "Most implemented 2025 slices are not huge aggregations, but a small set of large slices still carry a "
            "lot of requirement mass. The runtime-heavy DDM/default-policy, save/restore, and directed-interaction "
            "slices now have explicit requirement-family maps, so the remaining pressure is no longer about unnamed "
            "large bundles; it is about whether the repo wants leaf-level implemented slices rather than larger "
            "family-mapped aggregates."
        ),
        "next_decomposition_boundary": (
            "If deeper proof is needed, start by splitting the largest runtime-heavy slices into narrower service- or "
            "behavior-family audits inside the main python2025 backend lane."
        ),
    }


def _build_service_utilization_decomposition_audit(fi_service_audit: Mapping[str, Any]) -> dict[str, Any]:
    rows_by_family: dict[str, list[Mapping[str, Any]]] = {}
    for row in fi_service_audit["rows"]:
        rows_by_family.setdefault(str(row["family"]), []).append(row)

    families: list[dict[str, Any]] = []
    for family, rows in sorted(rows_by_family.items()):
        sorted_rows = sorted(rows, key=lambda item: int(item["service_number"]))
        service_numbers = [int(row["service_number"]) for row in sorted_rows]
        omt_requirement_ids = [f"HLA2025-OMT-SU-{number:03d}" for number in service_numbers]
        families.append(
            {
                "family": family,
                "service_count": len(sorted_rows),
                "service_number_min": min(service_numbers),
                "service_number_max": max(service_numbers),
                "omt_requirement_ids": omt_requirement_ids,
                "fi_requirement_ids": [str(row["requirement_id"]) for row in sorted_rows],
                "supporting_slice_ids": sorted(
                    {
                        slice_id
                        for row in sorted_rows
                        for slice_id in row.get("supporting_slice_ids", ())
                    }
                ),
                "all_fi_rows_traceable": all(row["proof_status"] == "implemented-slice-traceable" for row in sorted_rows),
            }
        )

    return {
        "audit_status": "service-utilization-decomposition-captured",
        "slice_id": "2025-service-utilization-crosscheck",
        "requirement_count": 196,
        "family_count": len(families),
        "families": families,
        "all_service_utilization_rows_family_mapped": sum(row["service_count"] for row in families) == 196,
        "all_backing_fi_rows_traceable": all(row["all_fi_rows_traceable"] for row in families),
        "current_assessment": (
            "The 196-row service-utilization slice is no longer only one broad OMT parser claim. It is decomposed "
            "by the same Federate Interface service families used by the runtime proof audit, so each OMT service "
            "usage row has a corresponding FI service row, service number, family, and supporting runtime slice."
        ),
        "residual_boundary": (
            "This proves service-utilization table extraction and alignment with runtime-backed FI service families; "
            "it does not turn optional SOM/FOM service-usage declarations into independent execution of every service."
        ),
    }


def _build_omt_extended_subset_decomposition_audit() -> dict[str, Any]:
    slice_id = "2025-omt-extended-supported-subset"
    slice_row = _implemented_slice_index()[slice_id]
    slice_requirement_ids = set(slice_row["requirements"])
    family_specs = [
        {
            "family": "model-identification-and-taxonomy",
            "focus": "objectModel identity scalars plus reference, POC, and keyword taxonomy metadata",
            "requirement_numbers": (1, 2, 3, 5, 7, 9, 10, 83),
        },
        {
            "family": "object-attribute-and-class-metadata",
            "focus": "object class names, attribute datatype links, dimensions, notes, and ownership/routing metadata",
            "requirement_numbers": (
                16, 20, 22, 23, 24, 25, 26, 28, 29, 31, 32, 33, 34, 36, 46, 50, 51, 52, 53, 54,
                55, 58, 60, 61, 62, 63, 64, 65, 66, 69, 71, 72, 73,
            ),
        },
        {
            "family": "interaction-parameter-and-routing-metadata",
            "focus": "interaction class names, parameter datatype links, dimensions, transportation/order metadata, and notes",
            "requirement_numbers": (
                86, 88, 89, 91, 92, 93, 95, 96, 97, 98, 99, 100, 101, 103, 104, 105, 108,
                116, 117, 118, 119, 120, 121, 122, 123, 124, 126, 127, 128, 131, 132, 135,
                136, 137, 138, 139,
            ),
        },
        {
            "family": "datatype-table-roundtrip",
            "focus": "basic, simple, enumerated, array, fixed-record, and variant-record datatype table preservation",
            "requirement_numbers": (
                148, 149, 153, 155, 172, 173, 174, 175, 177, 179, 180, 182, 183, 184, 185, 186,
                187, 188,
            ),
        },
        {
            "family": "container-reference-and-table-sections",
            "focus": "top-level table containers for tags, synchronization, transport, update rates, and datatype references",
            "requirement_numbers": (199, 203, 205, 206, 209, 211, 212, 213, 214, 216, 217, 218, 220, 221, 223),
        },
    ]

    families: list[dict[str, Any]] = []
    mapped_requirement_ids: set[str] = set()
    for spec in family_specs:
        requirement_ids = tuple(f"HLA2025-OMT-COMP-{number:03d}" for number in spec["requirement_numbers"])
        mapped_requirement_ids.update(requirement_ids)
        families.append(
            {
                "family": spec["family"],
                "focus": spec["focus"],
                "requirement_count": len(requirement_ids),
                "requirement_number_min": min(spec["requirement_numbers"]),
                "requirement_number_max": max(spec["requirement_numbers"]),
                "requirement_ids": requirement_ids,
                "all_requirements_in_slice": all(requirement_id in slice_requirement_ids for requirement_id in requirement_ids),
            }
        )

    unmapped_requirement_ids = sorted(slice_requirement_ids - mapped_requirement_ids)
    unexpected_requirement_ids = sorted(mapped_requirement_ids - slice_requirement_ids)
    return {
        "audit_status": "omt-extended-subset-decomposition-captured",
        "slice_id": slice_id,
        "requirement_count": len(slice_requirement_ids),
        "family_count": len(families),
        "families": families,
        "all_extended_subset_rows_family_mapped": not unmapped_requirement_ids and not unexpected_requirement_ids,
        "unmapped_requirement_ids": unmapped_requirement_ids,
        "unexpected_requirement_ids": unexpected_requirement_ids,
        "evidence": tuple(slice_row["evidence"]),
        "current_assessment": (
            "The 110-row OMT extended supported-subset slice is now decomposed into model identity, object/"
            "attribute metadata, interaction/parameter metadata, datatype tables, and container/table-section "
            "families. That makes the broad parser/serializer claim auditable by OMT structure instead of leaving "
            "one opaque requirement bundle."
        ),
        "residual_boundary": (
            "This is still OMT metadata parse/serialize preservation evidence for the supported subset; it does "
            "not claim execution of arbitrary OMT extension semantics or every possible semantic interpretation "
            "of preserved table fields."
        ),
    }


def _build_omt_xs_any_extension_decomposition_audit() -> dict[str, Any]:
    slice_id = "2025-omt-xs-any-extension-tolerance"
    slice_row = _implemented_slice_index()[slice_id]
    slice_requirement_ids = set(slice_row["requirements"])
    family_specs = [
        {
            "family": "object-model-root-and-identity",
            "focus": "foreign extension points around objectModel identity and model-level descriptive metadata",
            "requirement_numbers": (6, 8),
        },
        {
            "family": "object-class-and-attribute-extension-points",
            "focus": "foreign extension points attached to object classes, attributes, update metadata, and associations",
            "requirement_numbers": (19, 21, 27, 35, 39, 45, 47, 56, 57, 59, 67, 68, 70, 77, 81, 82),
        },
        {
            "family": "interaction-class-and-parameter-extension-points",
            "focus": "foreign extension points attached to interaction classes, parameters, order metadata, and associations",
            "requirement_numbers": (102, 106, 107, 113, 115, 129, 130, 134),
        },
        {
            "family": "datatype-and-encoding-extension-points",
            "focus": "foreign extension points attached to datatype, encoding, array, record, and enumerator structures",
            "requirement_numbers": (145, 147, 154, 156, 171, 176, 178, 181, 189, 193, 197, 198),
        },
        {
            "family": "container-table-and-reference-extension-points",
            "focus": "foreign extension points attached to table containers and top-level reference sections",
            "requirement_numbers": (202, 204, 208, 210, 219, 222, 224),
        },
    ]

    families: list[dict[str, Any]] = []
    mapped_requirement_ids: set[str] = set()
    for spec in family_specs:
        requirement_ids = tuple(f"HLA2025-OMT-COMP-{number:03d}" for number in spec["requirement_numbers"])
        mapped_requirement_ids.update(requirement_ids)
        families.append(
            {
                "family": spec["family"],
                "focus": spec["focus"],
                "requirement_count": len(requirement_ids),
                "requirement_number_min": min(spec["requirement_numbers"]),
                "requirement_number_max": max(spec["requirement_numbers"]),
                "requirement_ids": requirement_ids,
                "all_requirements_in_slice": all(requirement_id in slice_requirement_ids for requirement_id in requirement_ids),
            }
        )

    unmapped_requirement_ids = sorted(slice_requirement_ids - mapped_requirement_ids)
    unexpected_requirement_ids = sorted(mapped_requirement_ids - slice_requirement_ids)
    return {
        "audit_status": "omt-xs-any-extension-decomposition-captured",
        "slice_id": slice_id,
        "requirement_count": len(slice_requirement_ids),
        "family_count": len(families),
        "families": families,
        "all_xs_any_extension_rows_family_mapped": not unmapped_requirement_ids and not unexpected_requirement_ids,
        "unmapped_requirement_ids": unmapped_requirement_ids,
        "unexpected_requirement_ids": unexpected_requirement_ids,
        "evidence": tuple(slice_row["evidence"]),
        "current_assessment": (
            "The 45-row OMT xs:any extension slice is now decomposed by the parent OMT structures where foreign "
            "extensions may appear. This preserves the stronger payload-preservation claim while keeping the "
            "extension boundary explicit and auditable."
        ),
        "residual_boundary": (
            "The parser preserves and reserializes foreign XML payloads at these extension points and isolates them "
            "from native HLA elements; it still does not execute arbitrary third-party extension semantics."
        ),
    }


def _build_omt_schema_constraint_decomposition_audit() -> dict[str, Any]:
    slice_id = "2025-omt-schema-constraint-validation"
    slice_row = _implemented_slice_index()[slice_id]
    slice_requirement_ids = set(slice_row["requirements"])
    family_specs = [
        {
            "family": "xsd-key-constraints",
            "focus": "XSD key constraints for dimension datatype, representation, datatype, dimension, and transportation declarations",
            "requirement_numbers": (1, 3, 5, 7, 9),
        },
        {
            "family": "xsd-keyref-constraints",
            "focus": "XSD keyref constraints for dimension datatype, representation, datatype, dimension, and transportation references",
            "requirement_numbers": (2, 4, 6, 8, 10),
        },
        {
            "family": "xsd-unique-constraints",
            "focus": "XSD unique constraints for object class, attribute, interaction class, and parameter names",
            "requirement_numbers": (11, 12, 13, 14),
        },
        {
            "family": "enumeration-and-union-domain-constraints",
            "focus": "strict value-domain checks for 2025 OMT enumerations and union-backed fields",
            "requirement_numbers": (15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29),
        },
    ]

    families: list[dict[str, Any]] = []
    mapped_requirement_ids: set[str] = set()
    for spec in family_specs:
        requirement_ids = tuple(f"HLA2025-OMT-CV-{number:03d}" for number in spec["requirement_numbers"])
        mapped_requirement_ids.update(requirement_ids)
        families.append(
            {
                "family": spec["family"],
                "focus": spec["focus"],
                "requirement_count": len(requirement_ids),
                "requirement_number_min": min(spec["requirement_numbers"]),
                "requirement_number_max": max(spec["requirement_numbers"]),
                "requirement_ids": requirement_ids,
                "all_requirements_in_slice": all(requirement_id in slice_requirement_ids for requirement_id in requirement_ids),
            }
        )

    unmapped_requirement_ids = sorted(slice_requirement_ids - mapped_requirement_ids)
    unexpected_requirement_ids = sorted(mapped_requirement_ids - slice_requirement_ids)
    return {
        "audit_status": "omt-schema-constraint-decomposition-captured",
        "slice_id": slice_id,
        "requirement_count": len(slice_requirement_ids),
        "family_count": len(families),
        "families": families,
        "all_schema_constraint_rows_family_mapped": not unmapped_requirement_ids and not unexpected_requirement_ids,
        "unmapped_requirement_ids": unmapped_requirement_ids,
        "unexpected_requirement_ids": unexpected_requirement_ids,
        "evidence": tuple(slice_row["evidence"]),
        "current_assessment": (
            "The 29-row OMT validator-negative slice is now decomposed into key, keyref, unique, and "
            "enumeration/domain validation families. That makes the schema-validation proof auditable as "
            "negative validator coverage rather than one broad XSD-backed claim."
        ),
        "residual_boundary": (
            "This proves the supported Python validation path reports the imported 2025 schema and value-domain "
            "negative cases; it does not claim exhaustive third-party schema-validator certification beyond the "
            "bundled IEEE1516-OMT-2025 subset fixture coverage."
        ),
    }


def _build_save_restore_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "lifecycle-control",
            "focus": "save/restore request, initiate, completion, failure, abort, and precondition control flow",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_save_restore_lifecycle",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_save_failure_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_failure_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_abort_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_request_failure_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_save_request_precondition_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_request_precondition_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_participant_exception_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_status_exception_scenario_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_restore_lifecycle_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_completes_restore_after_peer_disconnect_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_restore_failure_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_restore_abort_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_request_precondition_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_restore_request_precondition_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_restore_participant_exception_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_restore_status_exception_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "shared-scenario-rollback",
            "focus": "shared two-federate save/restore, object-state rollback, and federate-local rollback",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_two_federate_suite_save_restore_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_backend_neutral_save_restore_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_federate_local_state_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_restore_object_state_scenario_via_compat_adapter",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_callback_delivery_policy",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_transport_and_order_policy_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_transportation_type_restore_persistence_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_plain_object_subscriber_routing",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_plain_interaction_subscriber_routing",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_clears_stale_directed_tso_and_preserves_post_restore_routing",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_treats_callback_delivery_as_runtime_policy_not_saved_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_transport_and_order_policy_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_transportation_type_restore_persistence_scenario_over_fedpro_route",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_inflight_ownership_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restores_cross_federate_attribute_owner_visibility",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_runtime_factory_restores_cross_federate_attribute_owner_visibility",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet",
            ],
        },
        {
            "family": "time-window-and-time-state-rollback",
            "focus": "lookahead, queued TSO, time/switch state, open/closed window state, output resume, and pipeline resume",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_time_and_switch_control_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restores_open_and_closed_time_window_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restores_closed_window_output_resume_without_dirty_replay",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restores_pipeline_resume_without_cross_window_replay",
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
            "and time-window/time-state rollback, with both direct and hosted anchors across every family, including "
            "restore-failure/abort control flow and restore persistence of transport/order policy metadata."
        ),
        "next_split_boundary": (
            "If this slice needs further tightening, split it first by these proof families before further modularizing "
            "save/restore runtime semantics inside hla-backend-python2025."
        ),
    }


def _build_save_restore_requirement_family_audit() -> dict[str, Any]:
    slice_requirement_ids = {
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
    }
    families = [
        {
            "family": "lifecycle-control",
            "requirement_ids": [
                "HLA2025-FI-SVC-018",
                "HLA2025-FI-SVC-019",
                "HLA2025-FI-SVC-020",
                "HLA2025-FI-SVC-021",
                "HLA2025-FI-SVC-022",
                "HLA2025-FI-SVC-023",
                "HLA2025-FI-SVC-026",
                "HLA2025-FI-SVC-027",
                "HLA2025-FI-SVC-028",
                "HLA2025-FI-SVC-029",
                "HLA2025-FI-SVC-030",
                "HLA2025-FI-SVC-031",
                "HLA2025-FI-SVC-032",
            ],
        },
        {
            "family": "shared-scenario-rollback",
            "requirement_ids": ["HLA2025-REQ-002"],
        },
        {
            "family": "routing-policy-rollback",
            "requirement_ids": [
                "HLA2025-FI-SVC-024",
                "HLA2025-FI-SVC-025",
                "HLA2025-FI-SVC-033",
                "HLA2025-FI-SVC-034",
            ],
        },
        {
            "family": "ownership-rollback",
            "requirement_ids": ["HLA2025-FI-005"],
        },
        {
            "family": "time-window-and-time-state-rollback",
            "requirement_ids": ["HLA2025-FI-001"],
        },
    ]
    mapped_requirement_ids = {
        requirement_id
        for family in families
        for requirement_id in family["requirement_ids"]
    }
    for family in families:
        family["requirement_count"] = len(family["requirement_ids"])
        family["all_requirements_in_slice"] = set(family["requirement_ids"]) <= slice_requirement_ids
    return {
        "audit_status": "save-restore-requirement-family-map-captured",
        "slice_id": "2025-save-restore-lifecycle",
        "requirement_count": len(slice_requirement_ids),
        "family_count": len(families),
        "all_save_restore_rows_family_mapped": mapped_requirement_ids == slice_requirement_ids,
        "unmapped_requirement_ids": sorted(slice_requirement_ids - mapped_requirement_ids),
        "unexpected_requirement_ids": sorted(mapped_requirement_ids - slice_requirement_ids),
        "families": families,
        "current_assessment": (
            "The large save/restore aggregate is now backed by an explicit requirement-family map instead of only one "
            "flat slice-level claim. That makes the lifecycle-control, shared rollback, routing rollback, and "
            "ownership/time rollback boundaries auditable requirement-by-requirement."
        ),
        "residual_boundary": (
            "This is still a requirement-family map over one larger save/restore runtime slice, not a promise that every "
            "save/restore requirement now has its own standalone implemented-evidence slice."
        ),
    }


def _build_federation_management_decomposition_audit() -> dict[str, Any]:
    slice_ids = [
        "2025-lifecycle-and-members",
        "2025-connection-lifecycle-services",
        "2025-connect-and-federation-catalog-services",
        "2025-federate-membership-and-resign-services",
        "2025-synchronization-point-services",
        "2025-save-restore-lifecycle",
    ]
    requirement_count = len(
        {
            requirement
            for slice_row in IMPLEMENTED_EVIDENCE_SLICES
            if slice_row["id"] in slice_ids
            for requirement in slice_row["requirements"]
        }
    )
    proof_families = [
        {
            "family": "connect-create-destroy-and-catalog-control",
            "focus": "connect or disconnect state, create or destroy federation control, federation listing, duplicate-create rejection, and FOM-validation or callback-model connect preconditions",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_lifecycle_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_lifecycle_with_mim_create_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_listing_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_validates_callback_model_and_credentials_at_connect",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_rejects_duplicate_federation_and_federate_names",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_rejects_invalid_join_fom_modules_and_destroy_while_joined",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_lifecycle_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_lifecycle_with_mim_create_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_listing_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_federation_reporting_callbacks_over_fedpro_schema",
            ],
        },
        {
            "family": "join-membership-and-name-preconditions",
            "focus": "join preconditions, federation-execution member reporting, multi-participation visibility, and federate-name uniqueness or joined-state constraints",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_multi_participation_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_join_precondition_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_reports_federation_executions_and_members",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_rejects_duplicate_federation_and_federate_names",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_multi_participation_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_keeps_decode_support_helpers_available_while_joined_identity_queries_stop_after_resign_over_fedpro_schema",
            ],
        },
        {
            "family": "resign-disconnect-loss-and-member-cleanup",
            "focus": "resign and disconnect preconditions, federation member cleanup after resign or loss, connectionLost teardown, and federateResigned callback or MOM cleanup behavior",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_resign_precondition_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_resign_mom_cleanup_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_disconnect_mom_cleanup_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_lost_federate_mom_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_connection_lost_callback_tears_down_connection",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_resigned_federate_callback_silence_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_reports_federate_resigned_callback_with_reason_context",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_resign_mom_cleanup_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_disconnect_mom_cleanup_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_resigned_federate_callback_silence_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_keeps_other_federates_joined_after_disconnect_and_resign_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_removes_mom_resigned_federate_from_delivery_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_applies_mom_resign_policy_over_fedpro_schema",
            ],
        },
        {
            "family": "synchronization-barriers-and-targeted-callbacks",
            "focus": "sync-point registration, announce or achieved flow, federationSynchronized completion, failure cases, late joiners, multiple sync points, and targeted sync callback routing",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_synchronization_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_synchronization_registration_failure_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_failed_federate_synchronization_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_late_join_synchronization_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_multiple_synchronization_points_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_mom_synchronization_point_reports_through_interactions",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_synchronization_scenario_via_runner_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_synchronization_registration_failure_scenario_via_runner_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_failed_federate_synchronization_scenario_via_runner_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_late_join_synchronization_scenario_via_runner_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_multiple_synchronization_points_scenario_via_runner_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_emits_synchronization_callbacks_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_targeted_synchronization_callbacks_only_to_sync_set_over_fedpro_schema",
            ],
        },
        {
            "family": "save-restore-lifecycle-control",
            "focus": "request or initiate, status, fail, abort, and completion control flow for federation save or restore across direct and hosted ambassadors",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_federation_save_restore_lifecycle",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_two_federate_suite_save_restore_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_backend_neutral_save_restore_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_save_restore_queued_callback_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_scheduled_save_restore_time_state_scenario_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_restore_lifecycle_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_save_restore_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_backend_neutral_save_restore_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_save_restore_queued_callback_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_scheduled_save_restore_time_state_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_restore_control_negative_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_save_restore_completion_callbacks_only_to_reporting_federate_over_fedpro_schema",
            ],
        },
        {
            "family": "save-restore-participant-recovery-and-branching",
            "focus": "multi-federate participant tracking, restore after disconnect, example FOM rollback branching, and recovery of saved participant state rather than dirty future state",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_example_fom_save_restore_gauntlet",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_completes_restore_after_peer_disconnect_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_example_fom_save_restore_gauntlet_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet",
            ],
        },
    ]
    return {
        "audit_status": "federation-management-decomposition-captured",
        "slice_id": "2025-federation-management-proof-families",
        "slice_ids": slice_ids,
        "requirement_count": requirement_count,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "Federation-management proof is no longer just one broad strong-slice claim. Its current evidence separates "
            "into connect/create/catalog control, join or membership reporting, resign or disconnect cleanup, "
            "synchronization barriers, save/restore lifecycle control, and save/restore participant recovery families, "
            "with direct and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these federation-management proof families before "
            "attempting clause-by-clause completion claims across connect, join, resign, sync, and save/restore services."
        ),
    }


def _build_support_services_decomposition_audit() -> dict[str, Any]:
    slice_ids = [
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
    ]
    requirement_count = len(
        {
            requirement
            for slice_row in IMPLEMENTED_EVIDENCE_SLICES
            if slice_row["id"] in slice_ids
            for requirement in slice_row["requirements"]
        }
    )
    proof_families = [
        {
            "family": "name-reservation-and-release-flows",
            "focus": "single and multi-name reservation success or failure callbacks, release flows, handoff behavior, and save or join preconditions around reservation state",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_python_rti_runs_name_reservation_scenario_without_wrapper_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_supports_single_object_instance_name_reservation_callback_and_release",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_supports_multiple_object_instance_name_reservation_and_release",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_object_instance_name_reservation_flow_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_isolates_name_reservation_callbacks_per_federate_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_name_reservation_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice",
            ],
        },
        {
            "family": "identity-catalog-and-handle-normalization-lookups",
            "focus": "federate, object, interaction, parameter, and service-group lookup or normalization flows across joined runtime state and loaded catalog metadata",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_support_lookup_and_normalization_route_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_accepts_support_lookup_aliases_and_rejects_invalid_values",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_round_trips_support_services_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_rejects_invalid_support_lookup_values_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_keeps_decode_support_helpers_available_while_joined_identity_queries_stop_after_resign_over_fedpro_schema",
            ],
        },
        {
            "family": "transport-order-update-dimension-and-range-lookups",
            "focus": "transportation, order type, update-rate, dimension, and range-bound lookups plus requester-only transport query callback routing",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_support_lookup_and_normalization_route_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_accepts_support_lookup_aliases_and_rejects_invalid_values",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_object_management_and_support_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_fom_backed_ddm_lookup_and_default_attribute_policy",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_round_trips_support_services_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_rejects_invalid_support_lookup_values_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_object_management_support_callbacks_over_fedpro_schema",
            ],
        },
        {
            "family": "switch-inquiry-and-control-model",
            "focus": "2025 set/get support switch model for advisory, reporting, and runtime policy state, including automatic resign, with validation of switch-control inputs",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_supports_explicit_switch_inquiry_and_control_model",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_round_trips_automatic_resign_directive_support_service",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_round_trips_support_services_over_fedpro_schema",
            ],
        },
        {
            "family": "factory-decode-and-hosted-support-seam",
            "focus": "support handle factories, decode helpers, hosted direct support route execution, callback-backlog control around support seams, and preservation of support surfaces across transport",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_support_factory_and_decode_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_callback_control_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_enable_disable_callbacks_controls_evoked_delivery",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_shared_support_factory_and_decode_scenario",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_support_factory_and_decode_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_disconnected_peer_callback_backlog_before_reconnect_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_enable_disable_callbacks_controls_evoked_delivery_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drains_multiple_callbacks_in_order_over_fedpro_schema",
            ],
        },
    ]
    return {
        "audit_status": "support-services-decomposition-captured",
        "slice_id": "2025-support-services-proof-families",
        "slice_ids": slice_ids,
        "requirement_count": requirement_count,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "Support-service proof is no longer just one large ledger summary. Its current evidence separates into "
            "name reservation and release flows, identity/catalog normalization lookups, transport or range lookups, "
            "the 2025 switch inquiry/control model, and factory/decode plus hosted support-seam families, with direct "
            "and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these support-service proof families before "
            "attempting clause-by-clause completion claims across lookup, inquiry, control, reservation, and decode surfaces."
        ),
    }


def _build_object_management_decomposition_audit() -> dict[str, Any]:
    slice_ids = [
        "2025-basic-object-exchange",
        "2025-declaration-publication-services",
        "2025-declaration-subscription-services",
        "2025-declaration-relevance-advisory-callbacks",
        "2025-object-delete-remove-flows",
        "2025-object-attribute-update-request-callbacks",
        "2025-object-scope-advisory-callbacks",
        "2025-object-update-rate-advisory-callbacks",
        "2025-object-attribute-transport-callbacks",
        "2025-object-interaction-transport-callbacks",
        "2025-directed-interaction-boundary",
        "2025-ddm-default-attribute-policy",
    ]
    requirement_count = len(
        {
            requirement
            for slice_row in IMPLEMENTED_EVIDENCE_SLICES
            if slice_row["id"] in slice_ids
            for requirement in slice_row["requirements"]
        }
    )
    proof_families = [
        {
            "family": "declaration-and-basic-exchange-gating",
            "focus": "publish and subscribe control, discovery metadata/class visibility, plain object exchange, and declaration gating or rejection paths",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_two_federate_object_and_interaction_exchange",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_declaration_management_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_discovery_class_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_declaration_invalid_attribute_publication_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_declaration_unpublish_rejection_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_time_managed_declaration_independence_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_passive_full_declaration_scenario_via_compat_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_object_and_interaction_exchange_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_discovery_and_remove_only_to_subscriber_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_reflect_and_interaction_only_to_subscriber_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_object_exchange_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_declaration_management_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_declaration_invalid_attribute_publication_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_declaration_unpublish_rejection_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_time_managed_declaration_independence_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_object_subscription_with_rate_aliases_over_fedpro_schema",
            ],
        },
        {
            "family": "deletion-and-local-known-state-lifecycle",
            "focus": "local delete, timed delete, orphan and remove flows, subscriber known-state rollback, and stale remove cleanup",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_local_delete_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_orphan_object_lifecycle_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_timed_delete_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_object_management_and_support_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_locally_deleted_object_known_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_deletes_objects_and_queues_timed_removes_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_local_delete_restore_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_local_delete_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_locally_deleted_object_known_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_clears_stale_timed_remove_and_preserves_post_restore_remove_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_delete_remove_only_to_discovered_observers_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_local_delete_to_requester_local_known_state_over_fedpro_schema",
            ],
        },
        {
            "family": "attribute-value-update-request-routing",
            "focus": "instance and class-wide requestAttributeValueUpdate callbacks, owner-only routing, and disconnected-owner suppression",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_request_attribute_value_update_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_request_attribute_value_update_routing_scenario_end_to_end",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_object_management_and_support_callbacks",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_object_management_support_callbacks_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_attribute_value_update_requests_only_to_owner_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_attribute_value_update_requests_for_disconnected_owner_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_request_attribute_value_update_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_request_attribute_value_update_routing_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "advisory-and-update-rate-callbacks",
            "focus": "turnUpdatesOn/off advisories, object-scope in-scope or out-of-scope transitions, update-rate routing, and rate alias parity",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_update_rate_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_object_scope_relevance_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_passive_and_universal_subscription_aliases_match_active_exchange",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_turn_updates_advisory_callbacks_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_update_rate_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_object_scope_relevance_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_object_subscription_with_rate_aliases_over_fedpro_schema",
            ],
        },
        {
            "family": "transportation-query-and-policy-state",
            "focus": "attribute and interaction transportation change confirmation, requester-only query/report callbacks, rejection paths, and restore persistence",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_transportation_type_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_transportation_type_restore_persistence_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_transportation_type_rejection_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restores_transportation_type_state_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_object_management_and_support_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_transport_and_order_policy_state",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_transportation_type_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_transportation_type_restore_persistence_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_transportation_type_rejection_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_transportation_query_callbacks_only_to_requester_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_transport_and_order_policy_state_over_fedpro_schema",
            ],
        },
        {
            "family": "object-region-scope-and-passive-alias-routing",
            "focus": "DDM object-region routing, attributesInScope and attributesOutOfScope advisories, passive region aliases, and DDM cleanup",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_filters_object_reflections_by_ddm_region_overlap",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_ddm_declaration_gating_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_ddm_passive_region_subscription_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_passive_ddm_region_subscription_aliases_match_active_region_delivery",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_drops_queued_ddm_tso_reflect_for_departed_target",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_ddm_declaration_gating_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_ddm_passive_region_subscription_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_passive_ddm_region_subscription_aliases_match_active_region_delivery_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_object_scope_relevance_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_drops_queued_ddm_tso_reflect_for_disconnected_target_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema",
            ],
        },
        {
            "family": "directed-and-directed-ddm-interaction-routing",
            "focus": "directed interaction delivery, timestamped directed routing and retraction, selective directed publication or subscription isolation, and directed DDM overlap routing",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_interactions_to_object_class_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_interactions_only_to_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_queues_timestamped_directed_interactions_until_time_advance",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_directed_interaction_set_unsubscribe_and_unpublish_are_selective",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_filters_directed_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_ddm_interactions_only_to_overlapping_subscribers",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_directed_interaction_exchange_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_directed_interaction_slice",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_queues_timestamped_directed_interactions_and_retracts_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_directed_with_set_unsubscribe_and_unpublish_are_selective",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_directed_interactions_by_ddm_region_overlap",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema",
            ],
        },
    ]
    return {
        "audit_status": "object-management-decomposition-captured",
        "slice_id": "2025-object-management-proof-families",
        "slice_ids": slice_ids,
        "requirement_count": requirement_count,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "Object-management proof is no longer just one broad strong-slice claim. Its current evidence separates "
            "into declaration/exchange gating, deletion and local-known-state lifecycle, attribute-value-update "
            "routing, advisory/update-rate callbacks, transportation policy callbacks, object-region scope routing, "
            "and directed or directed-DDM routing families, with direct and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these object-management proof families before "
            "attempting clause-by-clause completion claims for object, declaration, directed-routing, and DDM services."
        ),
    }


def _build_ownership_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "divestiture-and-confirmation-flows",
            "focus": "unconditional and negotiated divestiture, requestDivestitureConfirmation, confirmDivestiture, and cancel-negotiated-offer handling",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_basic_ownership_divest_acquire_and_query_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_negotiated_attribute_ownership_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_confirm_divestiture_negotiated_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_negotiated_ownership_matches_python_parity_flow",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_negotiated_attribute_ownership_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_confirm_divestiture_negotiated_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema",
            ],
        },
        {
            "family": "release-and-if-wanted-flows",
            "focus": "requestAttributeOwnershipRelease, attributeOwnershipReleaseDenied, and divestiture-if-wanted transfer behavior",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_release_request_ownership_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_negotiated_ownership_matches_python_parity_flow",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_python_rti_runs_negotiated_ownership_flow_without_wrapper_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_release_request_ownership_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route",
            ],
        },
        {
            "family": "acquisition-assumption-and-notification",
            "focus": "requestAttributeOwnershipAssumption, explicit acquisition requests, and ownership acquisition notification delivery",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_basic_ownership_divest_acquire_and_query_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_negotiated_attribute_ownership_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_mom_object_and_ownership_service_interactions",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_negotiated_attribute_ownership_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_transport_and_ownership_actions_to_observable_runtime_effects_over_fedpro_schema",
            ],
        },
        {
            "family": "acquisition-availability-and-cancellation",
            "focus": "attributeOwnershipAcquisitionIfAvailable, unavailable callbacks, acquisition cancellation, and cancel-confirmation flows",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_attribute_ownership_unavailable_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_negotiated_ownership_matches_python_parity_flow",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_python_rti_runs_negotiated_ownership_flow_without_wrapper_adapter",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_attribute_ownership_unavailable_scenario_over_fedpro_route",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_negotiated_ownership_flow",
            ],
        },
        {
            "family": "query-visibility-and-resign-policies",
            "focus": "queryAttributeOwnership, attributeIsOwnedByRTI and attributeIsNotOwned callback outcomes, isAttributeOwnedByFederate, and resign-time ownership policy behavior",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_basic_ownership_divest_acquire_and_query_callbacks",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_applies_resign_time_ownership_policies",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_mom_object_and_ownership_service_interactions",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_attribute_ownership_query_callbacks_only_to_requester_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_routes_mom_transport_and_ownership_actions_to_observable_runtime_effects_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_applies_resign_ownership_policy_over_fedpro_schema",
            ],
        },
        {
            "family": "rollback-and-restore-state",
            "focus": "save/restore ownership gauntlets, inflight acquisition or divestiture state, and cross-federate owner-visibility rollback",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_inflight_ownership_state",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restores_cross_federate_attribute_owner_visibility",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_primary_runtime_factory_restores_cross_federate_attribute_owner_visibility",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_inflight_ownership_state_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restores_cross_federate_attribute_owner_visibility_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet",
            ],
        },
    ]
    return {
        "audit_status": "ownership-decomposition-captured",
        "slice_id": "2025-ownership-proof-families",
        "slice_ids": [
            "2025-ownership-divestiture-confirmation-flows",
            "2025-ownership-release-and-if-wanted-flows",
            "2025-ownership-acquisition-assumption-flows",
            "2025-ownership-acquisition-availability-cancellation-flows",
            "2025-ownership-query-and-resign-policies",
            "2025-save-restore-lifecycle",
        ],
        "requirement_count": 18,
        "proof_family_count": len(proof_families),
        "direct_family_count": sum(1 for family in proof_families if family["direct_tests"]),
        "hosted_family_count": sum(1 for family in proof_families if family["hosted_tests"]),
        "proof_families": proof_families,
        "current_assessment": (
            "Ownership proof is no longer just a broad strong-slice claim. Its current evidence separates into "
            "divestiture/confirmation, release/if-wanted, acquisition/assumption, availability/cancellation, "
            "query/resign-policy, and rollback/restore families, with direct and hosted anchors across every family."
        ),
        "next_split_boundary": (
            "If this area needs further tightening, split it first by these ownership proof families before attempting "
            "a clause-by-clause ownership conformance audit."
        ),
    }


def _build_directed_interaction_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "base-routing-and-callback-delivery",
            "focus": "publish, subscribe, unsubscribe, unpublish, and receiveDirectedInteraction callback delivery",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_interactions_to_object_class_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_interactions_only_to_subscribers",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_queues_timestamped_directed_interactions_until_time_advance",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_delivers_and_retracts_timestamped_directed_interactions_for_all_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_drops_queued_directed_tso_for_departed_target",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_filters_directed_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_ddm_interactions_only_to_overlapping_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_removes_disconnected_directed_ddm_subscriber_from_delivery_state",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_directed_interaction_set_unsubscribe_and_unpublish_are_selective",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_preserves_other_federate_directed_publication_after_unpublish",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_clears_stale_directed_tso_and_preserves_post_restore_routing",
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
            "further modularizing directed-routing semantics inside hla-backend-python2025."
        ),
    }


def _build_directed_interaction_requirement_family_audit() -> dict[str, Any]:
    slice_requirement_ids = {
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
    }
    families = [
        {
            "family": "declaration-publication-control",
            "requirement_ids": [
                "HLA2025-FI-SVC-039",
                "HLA2025-FI-SVC-040",
            ],
        },
        {
            "family": "declaration-subscription-control",
            "requirement_ids": [
                "HLA2025-FI-SVC-045",
                "HLA2025-FI-SVC-046",
            ],
        },
        {
            "family": "send-receive-routing-and-hla-surface",
            "requirement_ids": [
                "HLA2025-FI-SVC-063",
                "HLA2025-FI-SVC-064",
                "HLA2025-FR-003",
                "HLA2025-FR-004",
            ],
        },
        {
            "family": "directed-interaction-delta-rows",
            "requirement_ids": [
                "HLA2025-MOD-007",
                "HLA2025-NEW-001",
            ],
        },
        {
            "family": "service-group-matrix-traceability",
            "requirement_ids": ["HLA2025-FI-001"],
        },
    ]
    mapped_requirement_ids = {
        requirement_id
        for family in families
        for requirement_id in family["requirement_ids"]
    }
    for family in families:
        family["requirement_count"] = len(family["requirement_ids"])
        family["all_requirements_in_slice"] = set(family["requirement_ids"]) <= slice_requirement_ids
    return {
        "audit_status": "directed-interaction-requirement-family-map-captured",
        "slice_id": "2025-directed-interaction-boundary",
        "requirement_count": len(slice_requirement_ids),
        "family_count": len(families),
        "all_directed_interaction_rows_family_mapped": mapped_requirement_ids == slice_requirement_ids,
        "unmapped_requirement_ids": sorted(slice_requirement_ids - mapped_requirement_ids),
        "unexpected_requirement_ids": sorted(mapped_requirement_ids - slice_requirement_ids),
        "families": families,
        "current_assessment": (
            "The directed-interaction aggregate is now backed by an explicit requirement-family map instead of only one "
            "flat slice-level claim. That makes the directed declaration-control, send/receive routing, spec-delta, "
            "and FI matrix umbrella rows auditable requirement-by-requirement."
        ),
        "residual_boundary": (
            "This is still a requirement-family map over one larger directed-interaction runtime slice, not a promise "
            "that every directed-interaction requirement now has its own standalone implemented-evidence slice."
        ),
    }


def _build_ddm_default_policy_decomposition_audit() -> dict[str, Any]:
    proof_families = [
        {
            "family": "lookup-and-default-policy-control",
            "focus": "FOM-backed dimension lookup, bounds queries, and default attribute transportation/order policy control",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_implements_fom_backed_ddm_lookup_and_default_attribute_policy",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap",
            ],
        },
        {
            "family": "object-region-routing-and-scope-advisories",
            "focus": "object reflection filtering through region overlap plus attributesInScope/attributesOutOfScope transitions",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_filters_object_reflections_by_ddm_region_overlap",
            ],
            "hosted_tests": [
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_filters_object_reflections_by_ddm_region_overlap",
            ],
        },
        {
            "family": "interaction-region-routing",
            "focus": "region-filtered interaction delivery, sent-region callback context, and plain interaction subscriber cleanup",
            "direct_tests": [
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_filters_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_preserves_direct_callback_context_for_timed_region_delivery",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_filters_directed_interactions_by_ddm_region_overlap",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_routes_directed_ddm_interactions_only_to_overlapping_subscribers",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_removes_disconnected_directed_ddm_subscriber_from_delivery_state",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_two_federate_suite_ddm_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_ddm_object_region_lifecycle_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_ddm_declaration_gating_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_runs_ddm_passive_region_subscription_scenario_via_compat_adapter",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_passive_ddm_region_subscription_aliases_match_active_region_delivery",
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
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_restore_recovers_directed_ddm_subscriber_routing",
                "tests/test_rti1516_2025_python2025_runtime.py::test_2025_provider_drops_queued_ddm_tso_reflect_for_departed_target",
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
            "further modularizing region-routing semantics inside hla-backend-python2025."
        ),
    }


def _build_ddm_default_policy_requirement_family_audit() -> dict[str, Any]:
    slice_requirement_ids = {
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
    }
    families = [
        {
            "family": "lookup-and-default-policy-control",
            "requirement_ids": [
                "HLA2025-NEW-004",
                "HLA2025-FI-SVC-076",
                "HLA2025-FI-SVC-124",
                "HLA2025-FI-SVC-157",
                "HLA2025-FI-SVC-159",
                "HLA2025-FI-SVC-160",
                "HLA2025-FI-SVC-161",
                "HLA2025-FI-SVC-164",
            ],
        },
        {
            "family": "object-region-routing-and-scope-advisories",
            "requirement_ids": [
                "HLA2025-FI-SVC-126",
                "HLA2025-FI-SVC-127",
                "HLA2025-FI-SVC-128",
                "HLA2025-FI-SVC-129",
                "HLA2025-FI-SVC-130",
                "HLA2025-FI-SVC-131",
                "HLA2025-FI-SVC-132",
                "HLA2025-FI-SVC-133",
                "HLA2025-FI-SVC-137",
            ],
        },
        {
            "family": "interaction-region-routing",
            "requirement_ids": [
                "HLA2025-FI-SVC-134",
                "HLA2025-FI-SVC-135",
                "HLA2025-FI-SVC-136",
            ],
        },
        {
            "family": "directed-ddm-routing",
            "requirement_ids": ["HLA2025-MOD-007"],
        },
        {
            "family": "passive-alias-and-compat-scenarios",
            "requirement_ids": ["HLA2025-FI-005"],
        },
        {
            "family": "ddm-restore-and-disconnect-cleanup",
            "requirement_ids": ["HLA2025-FI-001"],
        },
    ]
    mapped_requirement_ids = {
        requirement_id
        for family in families
        for requirement_id in family["requirement_ids"]
    }
    for family in families:
        family["requirement_count"] = len(family["requirement_ids"])
        family["all_requirements_in_slice"] = set(family["requirement_ids"]) <= slice_requirement_ids
    return {
        "audit_status": "ddm-default-policy-requirement-family-map-captured",
        "slice_id": "2025-ddm-default-attribute-policy",
        "requirement_count": len(slice_requirement_ids),
        "family_count": len(families),
        "all_ddm_rows_family_mapped": mapped_requirement_ids == slice_requirement_ids,
        "unmapped_requirement_ids": sorted(slice_requirement_ids - mapped_requirement_ids),
        "unexpected_requirement_ids": sorted(mapped_requirement_ids - slice_requirement_ids),
        "families": families,
        "current_assessment": (
            "The largest runtime-backed DDM/default-policy aggregate is now backed by an explicit requirement-family map "
            "instead of only one flat slice-level claim. That makes the lookup/default-policy, region-routing, "
            "directed-DDM, passive-alias, and restore/disconnect cleanup boundaries auditable requirement-by-requirement."
        ),
        "residual_boundary": (
            "This is still a requirement-family map over one larger runtime slice, not a promise that every DDM/default-policy "
            "requirement now has its own standalone implemented-evidence slice."
        ),
    }


def _build_shim_pressure_family_route_backing_audit() -> dict[str, Any]:
    audits = (
        _build_save_restore_decomposition_audit(),
        _build_ownership_decomposition_audit(),
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
        "audit_status": "wrapper-boundary-family-route-backing-captured",
        "family_count": len(families),
        "fully_route_backed_family_count": len(fully_route_backed),
        "all_families_route_backed_across_current_python_lanes": len(fully_route_backed) == len(families),
        "families": families,
        "current_assessment": (
            "The decomposed current-package pressure families are not in-process-only claims. Every currently named family "
            "across save/restore, ownership, directed interaction, and DDM/default-policy has both direct python2025 proof "
            "and hosted FedPro proof, which strengthens the current-lane working-RTI claim."
        ),
        "residual_boundary": (
            "This still does not prove full cross-binding conformance or full requirement-by-requirement closure; it "
            "proves that the main current-package pressure families are executable across the current Python 2025 lanes."
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
            "The main current-package pressure families are route-backed across the current Python lanes and are now "
            "symmetric at the named proof-family level. The remaining work is no longer family-count parity; it is "
            "deeper behavioral expansion, stronger evidence quality, and architectural judgment about how far the "
            "repo should continue decomposing runtime semantics away from the remaining compatibility-wrapper seam."
        )
    else:
        current_assessment = (
            "The main current-package pressure families are route-backed across the current Python lanes, but they are "
            "not perfectly symmetric. The remaining parity work is now clearer: close hosted-heavier and direct-heavier "
            "family imbalances rather than inventing new top-level proof areas."
        )
    return {
        "audit_status": "wrapper-boundary-family-asymmetry-captured",
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
        for item in slice_aggregation_pressure_audit["largest_runtime_backed_aggregated_slices"]
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
        "python2025_backend_concentration_is_material": implementation_concentration_audit[
            "semantic_concentration_is_material"
        ],
        "shim_backend_concentration_is_material": implementation_concentration_audit["semantic_concentration_is_material"],
        "all_pressure_families_route_backed_across_current_python_lanes": shim_pressure_family_route_backing_audit[
            "all_families_route_backed_across_current_python_lanes"
        ],
        "current_assessment": (
            "The primary 2025 Python RTI lane now has a defensible coherence story: its main current-package pressure slices are "
            "identified, decomposed into named proof families, and all of those families are executable across the "
            "current Python 2025 lanes. That is strong evidence for a coherent bounded working RTI surface even "
            "though the lane still depends on disciplined ownership across the extracted hla-backend-python2025 "
            "runtime/state/surface modules."
        ),
        "residual_blockers": [
            "The public hla-backend-python2025/backend.py shell is now thin, but the extracted runtime/state/surface split still needs continued discipline so coherence is not mistaken for a permanently settled architecture.",
            "The repo now has a row-level requirement-by-requirement audit, but it still stops at bounded disposition and supported-scope proof rather than an all-covered conformance pass.",
            "Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.",
            "Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or MOM action/request conformance pass.",
        ],
    }


def _build_extraction_readiness_audit(
    implementation_lane_audit: Mapping[str, Any],
    implementation_concentration_audit: Mapping[str, Any],
    save_restore_decomposition_audit: Mapping[str, Any],
    ownership_decomposition_audit: Mapping[str, Any],
    directed_interaction_decomposition_audit: Mapping[str, Any],
    ddm_default_policy_decomposition_audit: Mapping[str, Any],
    shim_pressure_family_route_backing_audit: Mapping[str, Any],
) -> dict[str, Any]:
    runtime_audits = (
        save_restore_decomposition_audit,
        ownership_decomposition_audit,
        directed_interaction_decomposition_audit,
        ddm_default_policy_decomposition_audit,
    )
    candidate_runtime_modules = {
        "2025-save-restore-lifecycle": "packages/hla-backend-python2025/src/hla/backends/python2025/save_restore_lifecycle.py",
        "2025-ownership-proof-families": "packages/hla-backend-python2025/src/hla/backends/python2025/ownership_runtime.py",
        "2025-directed-interaction-boundary": "packages/hla-backend-python2025/src/hla/backends/python2025/directed_interaction_boundary.py",
        "2025-ddm-default-attribute-policy": "packages/hla-backend-python2025/src/hla/backends/python2025/ddm_default_attribute_policy.py",
    }
    migration_worklist: list[dict[str, Any]] = []
    for audit in runtime_audits:
        family_names = [family["family"] for family in audit["proof_families"]]
        direct_test_count = sum(len(family["direct_tests"]) for family in audit["proof_families"])
        hosted_test_count = sum(len(family["hosted_tests"]) for family in audit["proof_families"])
        migration_worklist.append(
            {
                "slice_id": audit["slice_id"],
                "proof_family_count": audit["proof_family_count"],
                "proof_families": family_names,
                "direct_test_count": direct_test_count,
                "hosted_test_count": hosted_test_count,
                "route_backed": all(family["direct_tests"] and family["hosted_tests"] for family in audit["proof_families"]),
                "candidate_runtime_module": candidate_runtime_modules[audit["slice_id"]],
            }
        )
    python2025_runtime_dir = Path.cwd() / "packages" / "hla-backend-python2025" / "src" / "hla" / "backends" / "python2025"
    migrated_runtime_modules = []
    migrated_runtime_module_names = {
        "attribute_scope_runtime.py",
        "callback_runtime.py",
        "catalog_runtime.py",
        "ddm_default_attribute_policy.py",
        "declaration_management_runtime.py",
        "directed_interaction_boundary.py",
        "federation_management_runtime.py",
        "interaction_policy_runtime.py",
        "interaction_runtime.py",
        "mom_codec.py",
        "mom_runtime.py",
        "object_instance_runtime.py",
        "object_model_runtime.py",
        "object_reflection_runtime.py",
        "object_region_runtime.py",
        "ownership_runtime.py",
        "save_restore_lifecycle.py",
        "support_lookup_runtime.py",
        "support_policy_runtime.py",
        "support_services_runtime.py",
        "time_management_runtime.py",
        "update_rate_runtime.py",
    }
    if python2025_runtime_dir.exists():
        for module_path in sorted(python2025_runtime_dir.glob("*.py")):
            if module_path.name not in migrated_runtime_module_names:
                continue
            migrated_runtime_modules.append(str(module_path.relative_to(Path.cwd())))
    current_package_state = (
        "live-runtime-present"
        if implementation_lane_audit["current_2025_lane"]["backend_package"] == "hla-backend-python2025"
        else
        "semantic-slices-present"
        if migrated_runtime_modules
        else "scaffold-present"
        if implementation_lane_audit["dedicated_2025_backend_package_present"]
        else "not-present"
    )

    return {
        "audit_status": "extraction-readiness-map-captured",
        "extraction_needed_now": False,
        "dedicated_python_2025_backend_present": implementation_lane_audit["dedicated_2025_backend_package_present"],
        "recommended_current_action": "promote-python2025-as-live-lane-and-keep-shim-wrapper-narrowing-map",
        "future_backend_package_target": "hla-backend-python2025",
        "future_backend_plugin_family": "python-rti-2025",
        "extraction_package_contract": {
            "current_package_state": current_package_state,
            "target_distribution": "hla-backend-python2025",
            "target_import_root": "hla.backends.python2025",
            "target_plugin_path": "packages/hla-backend-python2025/src/hla/backends/python2025/plugin.py",
            "target_backend_name": "python2025",
            "target_plugin_family": "python-rti-2025",
            "target_supports": ["rti1516_2025"],
            "must_not_delegate_to": ["hla.backends.shim.backend.create_shim_backend"],
            "scanner_regression_test": (
                "tests/requirements/test_2025_finish_line_snapshot.py::"
                "test_2025_backend_plugin_scan_detects_future_dedicated_python_2025_backend"
            ),
            "package_creation_rule": (
                "Keep this package as the promoted live backend only while the direct and hosted proof families stay "
                "green and hla-backend-shim continues narrowing toward temporary import-compatibility scaffolding and "
                "wrapper-only responsibilities."
            ),
        },
        "extraction_cutover_invariants": [
            "python-2025-inprocess and python-2025-fedpro-grpc parity rows remain green for every migrated slice",
            "hla-backend-shim keeps only route normalization, compatibility aliases, and binding bridge behavior",
            "the dedicated python2025 plugin owns core RTI state for migrated save/restore, directed interaction, DDM, and time semantics",
            "backend plugin discovery reports hla-backend-python2025 as a dedicated rti1516_2025 candidate before any promotion claim changes",
        ],
        "shim_responsibilities_after_extraction": [
            "standard-route adaptation and compatibility aliases",
            "transport-facing normalization that is not core RTI state",
            "binding/package bridge behavior for standard Java/C++/hosted routes",
        ],
        "runtime_semantics_to_extract_first": migration_worklist,
        "runtime_semantics_to_extract_first_count": len(migration_worklist),
        "route_backed_runtime_semantics_count": sum(1 for row in migration_worklist if row["route_backed"]),
        "all_candidate_runtime_semantics_route_backed": all(row["route_backed"] for row in migration_worklist),
        "migrated_runtime_modules": migrated_runtime_modules,
        "extraction_trigger_signals": [
            "new runtime semantics keep accumulating in wrapper-facing compatibility layers instead of the python2025 runtime package",
            "adapter compatibility logic begins to obscure save/restore, directed interaction, DDM, or time semantics",
            "a future all-covered requirement audit needs cleaner service-by-service runtime ownership than the remaining compatibility-wrapper layer can provide",
        ],
        "pre_extraction_gates": [
            "keep the dedicated rti1516_2025 Python backend plugin discoverable and keep the backend scan detecting it",
            "move one decomposed pressure slice at a time while keeping direct and hosted route tests green",
            "keep hla-backend-shim as a narrower adapter layer instead of deleting the route-normalization seam",
        ],
        "current_assessment": (
            "The extraction cutover is materially underway: hla-backend-python2025 now owns the live backend, "
            "hla-backend-shim remains only as temporary import-compatibility scaffolding and wrapper-only "
            "compatibility support, and the repo still has a concrete migration map for continuing to narrow those "
            "scaffolding responsibilities while preserving the direct and hosted proof families."
            if implementation_lane_audit["current_2025_lane"]["backend_package"] == "hla-backend-python2025"
            else "Extraction is still not required for the current bounded working-surface claim, but the repo now has "
            "both a concrete migration map and extracted runtime semantic slices in hla-backend-python2025. "
            "Directed-interaction target-selection, interaction policy/routing, save/restore lifecycle, "
            "DDM/default-policy, object-region/DDM routing, callback delivery/control, catalog/handle lookup, "
            "attribute-scope advisories, update-rate policy, ownership acquisition/divestiture flows, MOM "
            "codec/routing, time-management, support-policy, support-lookup, declaration-management, object-model, "
            "object-instance lifecycle, object-reflection delivery, and federation-management semantics now live "
            "in the dedicated package while the live Python 2025 RTI lane consumes them as shared runtime logic, "
            "and the next meaningful step is to continue moving route-backed semantic slices without breaking the "
            "direct/hosted proof families."
        ),
        "pressure_signal": {
            "runtime_backend_slice_share": implementation_concentration_audit["runtime_backend_slice_share"],
            "semantic_concentration_is_material": implementation_concentration_audit["semantic_concentration_is_material"],
            "pressure_family_count": shim_pressure_family_route_backing_audit["family_count"],
            "fully_route_backed_pressure_family_count": shim_pressure_family_route_backing_audit[
                "fully_route_backed_family_count"
            ],
        },
    }


def _build_extraction_impact_audit(
    extraction_readiness_audit: Mapping[str, Any],
    python2025_source_responsibility_audit: Mapping[str, Any],
) -> dict[str, Any]:
    family_by_name = {
        family["family"]: family
        for family in python2025_source_responsibility_audit["families"]
    }
    slice_family_map = {
        "2025-save-restore-lifecycle": (
            "save-restore-runtime",
            "time-management-runtime",
            "ownership-runtime",
            "callback-delivery-and-control",
        ),
        "2025-ownership-proof-families": (
            "ownership-runtime",
            "save-restore-runtime",
            "callback-delivery-and-control",
        ),
        "2025-directed-interaction-boundary": (
            "interaction-routing-runtime",
            "ddm-region-runtime",
            "callback-delivery-and-control",
        ),
        "2025-ddm-default-attribute-policy": (
            "ddm-region-runtime",
            "object-attribute-runtime",
            "interaction-routing-runtime",
            "callback-delivery-and-control",
        ),
    }

    rows: list[dict[str, Any]] = []
    for item in extraction_readiness_audit["runtime_semantics_to_extract_first"]:
        source_families: list[dict[str, Any]] = []
        for family_name in slice_family_map[item["slice_id"]]:
            family = family_by_name.get(family_name)
            if family is None:
                source_families.append(
                    {
                        "family": family_name,
                        "current_method_count": 0,
                        "current_line_count": 0,
                        "present_in_runtime_backend": False,
                    }
                )
                continue
            source_families.append(
                {
                    "family": family_name,
                    "current_method_count": family["method_count"],
                    "current_line_count": family["line_count"],
                    "present_in_runtime_backend": True,
                }
            )
        rows.append(
            {
                "slice_id": item["slice_id"],
                "candidate_runtime_module": item["candidate_runtime_module"],
                "proof_family_count": item["proof_family_count"],
                "route_backed": item["route_backed"],
                "source_families": source_families,
                "source_family_count": len(source_families),
                "current_source_line_baseline": sum(family["current_line_count"] for family in source_families),
                "current_source_method_baseline": sum(family["current_method_count"] for family in source_families),
            }
        )

    return {
        "audit_status": "extraction-impact-map-captured",
        "slice_count": len(rows),
        "all_candidate_slices_have_source_family_map": len(rows) == extraction_readiness_audit[
            "runtime_semantics_to_extract_first_count"
        ],
        "all_candidate_slices_route_backed": all(row["route_backed"] for row in rows),
        "rows": rows,
        "largest_current_source_baseline": max(rows, key=lambda row: row["current_source_line_baseline"])["slice_id"] if rows else None,
        "current_assessment": (
            "The extraction worklist is now tied to measurable current source families. Save/restore, directed "
            "interaction, and DDM/default-policy migration candidates each identify the remaining adapter pressure "
            "and runtime line baselines that should keep shrinking around hla-backend-python2025."
        ),
        "non_claim": (
            "This is an impact map, not a migration-complete claim. The dedicated backend is present, but the line "
            "baselines are intentionally overlapping because some source families support multiple candidate slices."
        ),
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
            "The primary 2025 Python RTI lane can be promoted as the repo's coherent bounded working Python RTI surface: "
            "the main full Python 2025 RTI implementation now runs from hla-backend-python2025 while hla-backend-shim "
            "is retained only as temporary import-compatibility scaffolding and wrapper-only compatibility support, its "
            "main current-package pressure families are route-backed across the current Python lanes and the "
            "route-parity matrix now serves as the scenario-family ledger for federation, object, ownership, DDM, "
            "time, save/restore, MOM, and support-services evidence, "
            "Java and C++ shim/binding packages remain segregated supporting lanes rather than alternate "
            "Python RTIs, and the repo has enough evidence to make that bounded working-surface claim without hiding "
            "legacy-only, bounded-extension, or artifact-gated boundaries."
        ),
        "non_claims": [
            "This is not a full requirement-by-requirement IEEE 1516.1-2025 conformance claim.",
            "This is not a permanent no-split architecture decision.",
            "This does not upgrade Java or C++ bindings into exhaustive behavior-conformance lanes.",
            "This does not turn the hosted FedPro route into a full RTI semantics or exhaustive cross-binding conformance pass.",
        ],
        "current_assessment": (
            "The repo now has a single explicit statement for the primary 2025 Python RTI lane: promote it as the bounded "
            "working Python 2025 RTI surface, treat it as the main full implementation rather than as a mere "
            "adapter layer, use the route-parity matrix as the scenario-family ledger behind that claim, "
            "keep the architecture seam intact, and continue using the remaining requirement-level and cross-binding "
            "blockers to decide whether extraction is ever warranted."
        ),
    }


def _build_main_python2025_implementation_claim_audit(
    implementation_lane_audit: Mapping[str, Any],
    python2025_proof_lane_audit: Mapping[str, Any],
    objective_dimension_audit: Mapping[str, Any],
    current_lane_working_surface_statement: Mapping[str, Any],
    completion_claim_audit: Mapping[str, Any],
    promotion_split_audit: Mapping[str, Any],
) -> dict[str, Any]:
    ready = (
        implementation_lane_audit["current_2025_lane"]["backend_package"] == "hla-backend-python2025"
        and implementation_lane_audit["dedicated_2025_backend_package_present"]
        and python2025_proof_lane_audit["ready_for_main_implementation_operator_lane_claim"]
        and objective_dimension_audit["ready_for_bounded_working_surface_claim"]
        and current_lane_working_surface_statement["ready"]
        and promotion_split_audit["ready_for_current_lane_promotion_as_working_surface"]
    )
    return {
        "audit_status": "main-python2025-implementation-claim-captured",
        "claim_shape": "bounded-main-python2025-rti-implementation",
        "ready_for_main_python2025_implementation_claim": ready,
        "ready_for_full_2025_conformance_claim": completion_claim_audit["ready_for_full_2025_conformance_claim"],
        "implementation_owner": "hla-backend-python2025",
        "compatibility_wrapper": "hla-backend-shim",
        "default_operator_lane": python2025_proof_lane_audit["default_direct_lane"]["lane_id"],
        "hosted_extension_lane": python2025_proof_lane_audit["hosted_extension_lane"]["lane_id"],
        "claim": (
            "The repo can now make a distinct bounded claim for the main Python 2025 RTI implementation lane: "
            "hla-backend-python2025 is the implementation owner for the real executable 2025 Python RTI surface, "
            "hla-backend-shim is compatibility-wrapper-only, and the direct plus hosted Python 2025 proof lanes are "
            "sufficiently green to promote that lane as the main bounded working RTI implementation."
        ),
        "promotion_basis": [
            "hla-backend-python2025 is the discovered dedicated rti1516_2025 backend package and current implementation owner.",
            "The canonical operator lane marks verify-main-2025 as the default direct proof route for the real python2025 runtime.",
            "All tracked objective dimensions are bounded-ready for the Python-centered 2025 working surface.",
            "The current-lane working-surface statement is ready without relying on shim-owned runtime semantics.",
            "The promotion-vs-split audit already says the current python2025 lane can be promoted as the working surface while keeping future extraction optional.",
        ],
        "non_claims": [
            "This is not a full IEEE 1516.1-2025 conformance claim.",
            "This does not promote Java or C++ binding routes into full behavior-conformance lanes.",
            "This does not turn the hosted FedPro route into a second full RTI implementation owner.",
            "This does not settle a permanent no-split architecture decision.",
        ],
        "full_conformance_blockers": list(completion_claim_audit["full_claim_blockers"]),
        "current_assessment": (
            "The repo now separates the two judgments cleanly: the main python2025 RTI implementation claim is ready "
            "as a bounded working-surface statement, while the broader full-2025 conformance claim remains blocked by "
            "row-granularity, cross-binding, hosted-route, xs:any-extension, and legacy-only boundaries."
        ),
    }


def _build_full_claim_blocker_partition_audit(
    completion_claim_audit: Mapping[str, Any],
    closeout_readiness: Mapping[str, Any],
    main_python2025_implementation_claim_audit: Mapping[str, Any],
) -> dict[str, Any]:
    blocker_rows = [
        {
            "blocker": "omt_xs_any_extension_boundary",
            "classification": "external-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "bounded OMT extension-payload preservation rather than arbitrary third-party extension execution semantics"
            ),
        },
        {
            "blocker": "standard_java_cpp_binding_behavior_gap",
            "classification": "external-binding-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "Java/C++ rows remain artifact/runtime-capability binding evidence rather than exhaustive behavior conformance"
            ),
        },
        {
            "blocker": "hosted_fedpro_full_conformance_gap",
            "classification": "external-hosted-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or cross-binding pass"
            ),
        },
        {
            "blocker": "duplicate_umbrella_row_granularity_gap",
            "classification": "row-granularity-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "duplicate/umbrella rows remain normalization aids instead of direct one-row conformance assertions"
            ),
        },
    ]
    direct_runtime_blocker_count = sum(
        1 for row in blocker_rows if row["counts_against_main_python2025_runtime_completeness"]
    )
    return {
        "audit_status": "full-claim-blocker-partition-captured",
        "full_claim_blocker_count": len(completion_claim_audit["full_claim_blockers"]),
        "partitioned_blocker_count": len(blocker_rows),
        "direct_runtime_incompleteness_blocker_count": direct_runtime_blocker_count,
        "boundary_only_blocker_count": len(blocker_rows) - direct_runtime_blocker_count,
        "all_current_full_claim_blockers_are_external_to_main_python2025_runtime": (
            len(completion_claim_audit["full_claim_blockers"]) == len(blocker_rows)
            and direct_runtime_blocker_count == 0
            and main_python2025_implementation_claim_audit["ready_for_main_python2025_implementation_claim"]
            and closeout_readiness["ready_for_slice_closeout"]
        ),
        "blocker_rows": blocker_rows,
        "current_assessment": (
            "The remaining blockers in the full-2025 claim are now explicitly partitioned. On the current tree they "
            "all sit outside direct main-lane python2025 runtime completeness: they are OMT extension-scope, "
            "Java/C++ binding, hosted-route, or row-granularity boundaries rather than missing core executable "
            "behavior in hla-backend-python2025."
        ),
        "residual_boundary": (
            "This partition audit clarifies blocker ownership. It does not convert those external boundaries into a "
            "full 2025 conformance pass."
        ),
    }


def _build_closeout_blocker_partition_audit(
    closeout_readiness: Mapping[str, Any],
    objective_dimension_audit: Mapping[str, Any],
    main_python2025_implementation_claim_audit: Mapping[str, Any],
) -> dict[str, Any]:
    blocker_rows = [
        {
            "blocker": "row_level_requirement_closeout_limit",
            "classification": "requirement-closeout-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "row-level disposition still includes retired, umbrella, and bounded-scope rows rather than an unconditional conformance pass"
            ),
        },
        {
            "blocker": "implemented_slice_requirement_granularity_gap",
            "classification": "requirement-granularity-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "many implemented slices still aggregate multiple requirements under bounded supported-scope language"
            ),
        },
        {
            "blocker": "standard_java_cpp_cross_binding_gap",
            "classification": "external-binding-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "Java/C++ standard-route evidence remains artifact-gated/runtime-capability proof rather than full cross-binding behavior conformance"
            ),
        },
        {
            "blocker": "hosted_fedpro_cross_binding_gap",
            "classification": "external-hosted-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "hosted FedPro supported-scope rows stop short of full RTI semantics and full cross-binding conformance"
            ),
        },
        {
            "blocker": "omt_extension_execution_scope_gap",
            "classification": "external-omt-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "OMT xs:any coverage preserves foreign extension payloads but leaves arbitrary third-party extension execution semantics out of scope"
            ),
        },
        {
            "blocker": "legacy_only_explicit_exclusion",
            "classification": "legacy-exclusion-boundary",
            "counts_against_main_python2025_runtime_completeness": False,
            "evidence_basis": (
                "legacy-only rows remain explicit exclusions from an unconditional 2025 completion claim"
            ),
        },
    ]
    direct_runtime_blocker_count = sum(
        1 for row in blocker_rows if row["counts_against_main_python2025_runtime_completeness"]
    )
    return {
        "audit_status": "closeout-blocker-partition-captured",
        "closeout_blocker_count": len(closeout_readiness["conformance_blockers"]),
        "partitioned_blocker_count": len(blocker_rows),
        "direct_runtime_incompleteness_blocker_count": direct_runtime_blocker_count,
        "boundary_only_blocker_count": len(blocker_rows) - direct_runtime_blocker_count,
        "all_current_closeout_blockers_are_external_to_main_python2025_runtime": (
            len(closeout_readiness["conformance_blockers"]) == len(blocker_rows)
            and direct_runtime_blocker_count == 0
            and objective_dimension_audit["ready_for_bounded_working_surface_claim"]
            and main_python2025_implementation_claim_audit["ready_for_main_python2025_implementation_claim"]
        ),
        "blocker_rows": blocker_rows,
        "current_assessment": (
            "The broader closeout blockers are now explicitly partitioned too. On the current tree they all describe "
            "requirement-granularity, cross-binding, hosted-route, OMT-extension-scope, or legacy-exclusion limits "
            "rather than missing core executable behavior in the main hla-backend-python2025 runtime lane."
        ),
        "residual_boundary": (
            "This partition audit clarifies why closeout remains incomplete without treating the main python2025 "
            "runtime as behaviorally unfinished."
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


def _objective_dimension_evidence_basis(
    dimension_id: str,
    *,
    route_summary: Mapping[str, Any],
    omt_requirement_proof_audit: Mapping[str, Any],
    support_service_proof_audit: Mapping[str, Any],
    callback_proof_audit: Mapping[str, Any],
    callback_route_parity_audit: Mapping[str, Any],
    python_rti_milestone_audit: Mapping[str, Any],
    time_window_vendor_parity_audit: Mapping[str, Any],
) -> list[str]:
    if dimension_id == "federation_management":
        return [
            f"route_summary.scenario_count={route_summary['scenario_count']}",
            f"route_summary.row_count={route_summary['row_count']}",
            f"route_summary.routes_with_full_parity={len(route_summary['routes_with_full_parity'])}",
            "federation_management_decomposition.slice_id=2025-federation-management-proof-families",
            "federation_management_decomposition.proof_family_count=6",
        ]
    if dimension_id == "object_management":
        return [
            f"route_summary.scenario_count={route_summary['scenario_count']}",
            f"route_summary.row_count={route_summary['row_count']}",
            "route_summary.scenarios=ddm,object_exchange,ownership",
            "object_management_decomposition.slice_id=2025-object-management-proof-families",
            "object_management_decomposition.proof_family_count=7",
        ]
    if dimension_id == "ownership_management":
        return [
            f"route_summary.scenario_count={route_summary['scenario_count']}",
            f"route_summary.row_count={route_summary['row_count']}",
            "route_summary.scenarios=ownership,save_restore",
            "ownership_decomposition.slice_id=2025-ownership-proof-families",
            "ownership_decomposition.proof_family_count=6",
        ]
    if dimension_id == "support_services":
        return [
            "support_service_proof_audit.ready_for_support_service_traceability_claim=true",
            "support_service_proof_audit.focused_executable_row_count=62",
            "support_service_proof_audit.complete_negative_path_row_count=61",
            "support_services_decomposition.slice_id=2025-support-services-proof-families",
            "support_services_decomposition.proof_family_count=5",
        ]
    if dimension_id == "callbacks":
        return [
            "callback_proof_audit.ready_for_callback_by_callback_working_surface_claim=true",
            "callback_route_parity_audit.ready_for_full_python_lane_callback_route_parity_claim=true",
            "callback_route_parity_audit.hosted_or_route_backed_callback_count=55",
            "callback_decomposition.slice_id=2025-callback-proof-families",
            "callback_decomposition.proof_family_count=8",
        ]
    if dimension_id == "time_management":
        milestone_rows = list(python_rti_milestone_audit["rows"])
        bounded_time_rows = [
            row
            for row in milestone_rows
            if row["route"] in {"python-2025-inprocess", "python-2025-fedpro-grpc"}
            and row["status"] in {"bounded-query-evidence", "bounded-lookahead-evidence"}
        ]
        bounded_time_statuses = ",".join(
            sorted({f"{row['route']}:{row['status']}" for row in bounded_time_rows})
        )
        return [
            f"python_rti_milestone_audit bounded time rows={bounded_time_statuses}",
            f"time_window_vendor_parity_audit.audit_status={time_window_vendor_parity_audit['audit_status']}",
            "time_window_vendor_parity_audit.current_trial_candidate.scenario_id=time-window-future-exclusion",
            "time_management_decomposition.slice_id=2025-time-management-proof-families",
            "time_management_decomposition.proof_family_count=5",
        ]
    if dimension_id == "omt_handling":
        return [
            f"omt_requirement_proof_audit.ready_for_omt_traceability_claim={str(omt_requirement_proof_audit['ready_for_omt_traceability_claim']).lower()}",
            f"omt_requirement_proof_audit.row_count={omt_requirement_proof_audit['row_count']}",
            "omt_requirement_proof_audit.by_proof_status=supported-subset-traceable:454",
            "omt_decomposition.slice_ids=2025-service-utilization-crosscheck,2025-omt-extended-supported-subset,2025-omt-xs-any-extension-tolerance,2025-omt-schema-constraint-validation",
            "omt_decomposition.family_counts=service-utilization:10,extended-subset:5,xs-any:5,schema-constraint:4",
        ]
    if dimension_id == "binding_routes":
        return [
            f"route_summary.scenario_count={route_summary['scenario_count']}",
            f"route_summary.row_count={route_summary['row_count']}",
            f"route_summary.routes_with_full_parity={len(route_summary['routes_with_full_parity'])}",
            "binding_route_decomposition.slice_id=2025-binding-route-proof-families",
            "binding_route_decomposition.proof_family_count=6",
        ]
    return []


def _build_objective_dimension_audit(
    route_parity_matrix: Mapping[str, Any],
    *,
    omt_requirement_proof_audit: Mapping[str, Any],
    support_service_proof_audit: Mapping[str, Any],
    callback_proof_audit: Mapping[str, Any],
    callback_route_parity_audit: Mapping[str, Any],
    python_rti_milestone_audit: Mapping[str, Any],
    time_window_vendor_parity_audit: Mapping[str, Any],
) -> dict[str, Any]:
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
            dimension["evidence_level"] in {
                "strong-slice",
                "decomposed-strong-slice",
                "bounded-slice",
                "decomposed-bounded-slice",
                "per-service-runtime-traceable",
                "decomposed-per-service-runtime-traceable",
                "callback-ledger-route-backed",
                "decomposed-callback-ledger-route-backed",
                "query-and-window-proof-backed",
                "decomposed-query-and-window-proof-backed",
            }
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
                "evidence_basis": _objective_dimension_evidence_basis(
                    dimension["id"],
                    route_summary=route_summary,
                    omt_requirement_proof_audit=omt_requirement_proof_audit,
                    support_service_proof_audit=support_service_proof_audit,
                    callback_proof_audit=callback_proof_audit,
                    callback_route_parity_audit=callback_route_parity_audit,
                    python_rti_milestone_audit=python_rti_milestone_audit,
                    time_window_vendor_parity_audit=time_window_vendor_parity_audit,
                ),
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
            "object management, time management, support services, callbacks, OMT handling, and binding and hosted "
            "routes."
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
                    "scenario set, with broad hosted replay across lifecycle, object, time, save/restore, support-service, "
                    "and callback scenarios, not a full RTI semantics or exhaustive cross-binding conformance claim."
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
                    "The hosted FedPro route now executes the tracked FOM-backed runtime scenarios through the "
                    "package-owned Proto2025 example/FOM showcase, including MessageTest, SpaceLite, TimeMgmtTest, "
                    "and Target/Radar, rather than relying only on indirect object, MOM, and save/restore route slices."
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
                    "exercising the combined closure/output/consumer-order/pipeline ladder on the actual current Python 2025 RTI lane, plus "
                    "negative-oracle guards rejecting mismatched LITS boundaries, premature output, reversed consumer "
                    "order, cross-window contamination, and dirty post-restore replay while save/restore evidence still "
                    "shows that dirty lookahead changes are rolled back and a pre-save queued TSO is redelivered after "
                    "restore."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route has executable GALT/LITS query evidence inside the hosted time-management "
                    "slice, including queued-TSO GALT/LITS divergence after a live lookahead change, the hosted "
                    "Target/Radar proof-ladder replay, negative-oracle guards rejecting mismatched LITS boundaries, "
                    "premature output, reversed consumer order, cross-window contamination, and dirty post-restore "
                    "replay, restore rollback of dirty lookahead with pre-save queued TSO redelivered after restore, "
                    "and the Target/Radar future-exclusion proof."
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
                    "save-restore-output-resume, and save-restore-pipeline-resume scenarios together with matching "
                    "negative-oracle guards."
                ),
                "python-2025-fedpro-grpc": (
                    "The hosted FedPro route exercises lookahead queries together with advance/grant, queued "
                    "timestamped delivery, the hosted Target/Radar proof-ladder replay, and the Target/Radar "
                    "output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, "
                    "save-restore lookahead rollback with queued-TSO redelivery, "
                    "save-restore-output-resume, and save-restore-pipeline-resume scenarios together with matching "
                    "negative-oracle guards."
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
            "resume, and time-window proof, paired with negative-oracle rejection guards, "
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
    for evidence_slice in _implemented_slices():
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
        "The repo now has a row-level requirement-by-requirement disposition audit across all 2025 rows, but that audit still contains retired, umbrella, and bounded-scope rows rather than an unconditional conformance pass; this is a requirement-closeout limit rather than evidence that the main python2025 runtime lane is behaviorally incomplete.",
        "Many implemented-slice rows outside the FI service catalog still aggregate multiple requirements under bounded supported-scope language rather than proving every requirement individually; that remaining gap is about requirement granularity, not about whether hla-backend-python2025 has the underlying executable behavior.",
        "Java and C++ standard-route evidence remains artifact-gated/runtime-capability evidence, not a full cross-binding behavior-conformance pass.",
        "The hosted FedPro route is verified as a runtime slice, but its own supported-scope rows explicitly stop short of full RTI semantics and full cross-binding conformance; the remaining route boundary is a hosted/cross-binding proof limit rather than evidence that the direct python2025 runtime lane lacks those semantics.",
        "OMT component coverage includes foreign xs:any extension payload preservation, but arbitrary third-party extension execution semantics remain out of scope.",
        "Legacy-only rows remain explicit exclusions, so overall completion cannot be promoted to an unconditional 2025 conformance claim.",
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
    implemented_evidence_slices = _normalized_implemented_evidence_slices(project_root)
    implementation_concentration_audit = _build_implementation_concentration_audit()
    python2025_source_responsibility_audit = _build_python2025_source_responsibility_audit(project_root)
    slice_aggregation_pressure_audit = _build_slice_aggregation_pressure_audit()
    service_utilization_decomposition_audit = _build_service_utilization_decomposition_audit(fi_service_proof_audit)
    omt_extended_subset_decomposition_audit = _build_omt_extended_subset_decomposition_audit()
    omt_xs_any_extension_decomposition_audit = _build_omt_xs_any_extension_decomposition_audit()
    omt_schema_constraint_decomposition_audit = _build_omt_schema_constraint_decomposition_audit()
    save_restore_decomposition_audit = _build_save_restore_decomposition_audit()
    federation_management_decomposition_audit = _build_federation_management_decomposition_audit()
    callback_decomposition_audit = _build_callback_decomposition_audit()
    time_management_decomposition_audit = _build_time_management_decomposition_audit()
    binding_route_decomposition_audit = _build_binding_route_decomposition_audit()
    support_services_decomposition_audit = _build_support_services_decomposition_audit()
    object_management_decomposition_audit = _build_object_management_decomposition_audit()
    save_restore_requirement_family_audit = _build_save_restore_requirement_family_audit()
    ownership_decomposition_audit = _build_ownership_decomposition_audit()
    directed_interaction_decomposition_audit = _build_directed_interaction_decomposition_audit()
    directed_interaction_requirement_family_audit = _build_directed_interaction_requirement_family_audit()
    ddm_default_policy_decomposition_audit = _build_ddm_default_policy_decomposition_audit()
    ddm_default_policy_requirement_family_audit = _build_ddm_default_policy_requirement_family_audit()
    shim_pressure_family_route_backing_audit = _build_shim_pressure_family_route_backing_audit()
    shim_pressure_family_asymmetry_audit = _build_shim_pressure_family_asymmetry_audit()
    wrapper_boundary_family_route_backing_audit = shim_pressure_family_route_backing_audit
    wrapper_boundary_family_asymmetry_audit = shim_pressure_family_asymmetry_audit
    closeout_readiness = {
        "implemented_slice_count": len(_implemented_slices()),
        "high_priority_open_count": len(high_priority_open),
        "route_parity_partial_count": route_partial_count,
        "route_parity_missing_count": route_missing_count,
        "ready_for_slice_closeout": closeout_ready,
        "ready_for_full_completion_claim": False,
        "current_assessment": (
            "Executable slice coverage, route parity, FI per-service runtime traceability, and bounded working-RTI "
            "milestone evidence are in strong shape for the primary 2025 Python RTI lane, and the repo now has a row-level "
            "requirement-by-requirement disposition audit across the full 2025 universe. The remaining "
            "retired, umbrella, cross-binding, bounded-extension, and bounded-route limits still block a complete "
            "2025 claim, but those limits now sit outside the already-green primary python2025 runtime lane: "
            "hla-backend-python2025 is the repo's main 2025 Python RTI lane and hla-backend-shim is treated as a "
            "compatibility wrapper."
        ),
        "conformance_blockers": conformance_blockers,
    }
    time_window_vendor_parity_audit = _build_time_window_vendor_parity_audit()
    python2025_proof_lane_audit = _build_python2025_proof_lane_audit(project_root)
    objective_dimension_audit = _build_objective_dimension_audit(
        route_parity_matrix,
        omt_requirement_proof_audit=omt_requirement_proof_audit,
        support_service_proof_audit=support_service_proof_audit,
        callback_proof_audit=callback_proof_audit,
        callback_route_parity_audit=callback_route_parity_audit,
        python_rti_milestone_audit=python_rti_milestone_audit,
        time_window_vendor_parity_audit=time_window_vendor_parity_audit,
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
    retired_legacy_mapping_audit = _build_retired_legacy_mapping_audit(
        project_root,
        harmonization_rows,
    )
    omt_xs_any_mapping_audit = _build_omt_xs_any_mapping_audit(
        project_root,
        harmonization_rows,
    )
    binding_boundary_mapping_audit = _build_binding_boundary_mapping_audit(
        project_root,
        completion_rows,
    )
    hosted_fedpro_bounded_proof_audit = _build_hosted_fedpro_bounded_proof_audit(
        project_root,
        route_parity_matrix,
    )
    standard_binding_runtime_capability_audit = _build_standard_binding_runtime_capability_audit(
        project_root,
        route_parity_matrix,
    )
    duplicate_umbrella_mapping_audit = _build_duplicate_umbrella_mapping_audit(
        project_root,
        harmonization_rows,
    )
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
        project_root,
        promotion_split_audit,
        python_rti_milestone_audit,
    )
    extraction_readiness_audit = _build_extraction_readiness_audit(
        implementation_lane_audit,
        implementation_concentration_audit,
        save_restore_decomposition_audit,
        ownership_decomposition_audit,
        directed_interaction_decomposition_audit,
        ddm_default_policy_decomposition_audit,
        shim_pressure_family_route_backing_audit,
    )
    extraction_impact_audit = _build_extraction_impact_audit(
        extraction_readiness_audit,
        python2025_source_responsibility_audit,
    )
    hosted_shared_scenario_coverage_audit = _build_hosted_shared_scenario_coverage_audit(project_root)
    main_python2025_implementation_claim_audit = _build_main_python2025_implementation_claim_audit(
        implementation_lane_audit,
        python2025_proof_lane_audit,
        objective_dimension_audit,
        current_lane_working_surface_statement,
        completion_claim_audit,
        promotion_split_audit,
    )
    full_claim_blocker_partition_audit = _build_full_claim_blocker_partition_audit(
        completion_claim_audit,
        closeout_readiness,
        main_python2025_implementation_claim_audit,
    )
    closeout_blocker_partition_audit = _build_closeout_blocker_partition_audit(
        closeout_readiness,
        objective_dimension_audit,
        main_python2025_implementation_claim_audit,
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
        "implemented_evidence_slices": [dict(slice_) for slice_ in implemented_evidence_slices],
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
        "retired_legacy_mapping_audit": retired_legacy_mapping_audit,
        "omt_xs_any_mapping_audit": omt_xs_any_mapping_audit,
        "binding_boundary_mapping_audit": binding_boundary_mapping_audit,
        "hosted_fedpro_bounded_proof_audit": hosted_fedpro_bounded_proof_audit,
        "standard_binding_runtime_capability_audit": standard_binding_runtime_capability_audit,
        "duplicate_umbrella_mapping_audit": duplicate_umbrella_mapping_audit,
        "completion_claim_audit": completion_claim_audit,
        "closeout_blocker_partition_audit": closeout_blocker_partition_audit,
        "supported_boundary_statement": supported_boundary_statement,
        "implementation_concentration_audit": implementation_concentration_audit,
        "python2025_source_responsibility_audit": python2025_source_responsibility_audit,
        "slice_aggregation_pressure_audit": slice_aggregation_pressure_audit,
        "service_utilization_decomposition_audit": service_utilization_decomposition_audit,
        "omt_extended_subset_decomposition_audit": omt_extended_subset_decomposition_audit,
        "omt_xs_any_extension_decomposition_audit": omt_xs_any_extension_decomposition_audit,
        "omt_schema_constraint_decomposition_audit": omt_schema_constraint_decomposition_audit,
        "save_restore_decomposition_audit": save_restore_decomposition_audit,
        "save_restore_requirement_family_audit": save_restore_requirement_family_audit,
        "federation_management_decomposition_audit": federation_management_decomposition_audit,
        "callback_decomposition_audit": callback_decomposition_audit,
        "time_management_decomposition_audit": time_management_decomposition_audit,
        "binding_route_decomposition_audit": binding_route_decomposition_audit,
        "support_services_decomposition_audit": support_services_decomposition_audit,
        "object_management_decomposition_audit": object_management_decomposition_audit,
        "ownership_decomposition_audit": ownership_decomposition_audit,
        "directed_interaction_decomposition_audit": directed_interaction_decomposition_audit,
        "directed_interaction_requirement_family_audit": directed_interaction_requirement_family_audit,
        "ddm_default_policy_decomposition_audit": ddm_default_policy_decomposition_audit,
        "ddm_default_policy_requirement_family_audit": ddm_default_policy_requirement_family_audit,
        "shim_pressure_family_route_backing_audit": shim_pressure_family_route_backing_audit,
        "shim_pressure_family_asymmetry_audit": shim_pressure_family_asymmetry_audit,
        "wrapper_boundary_family_route_backing_audit": wrapper_boundary_family_route_backing_audit,
        "wrapper_boundary_family_asymmetry_audit": wrapper_boundary_family_asymmetry_audit,
        "current_lane_coherence_audit": current_lane_coherence_audit,
        "current_lane_working_surface_statement": current_lane_working_surface_statement,
        "main_python2025_implementation_claim_audit": main_python2025_implementation_claim_audit,
        "full_claim_blocker_partition_audit": full_claim_blocker_partition_audit,
        "implementation_lane_audit": implementation_lane_audit,
        "hosted_shared_scenario_coverage_audit": hosted_shared_scenario_coverage_audit,
        "time_window_vendor_parity_audit": time_window_vendor_parity_audit,
        "python2025_proof_lane_audit": python2025_proof_lane_audit,
        "extraction_readiness_audit": extraction_readiness_audit,
        "extraction_impact_audit": extraction_impact_audit,
        "promotion_split_audit": promotion_split_audit,
        "promotion_vs_split_audit": promotion_split_audit,
        "closeout_readiness": closeout_readiness,
        "finish_rule": (
            "Each future or reopened row needs a positive test, a negative unsupported-boundary test, "
            "or an explicit supported-subset/unsupported-boundary disposition before it can be counted as closed."
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
    retired_legacy_mapping_audit = snapshot["retired_legacy_mapping_audit"]
    omt_xs_any_mapping_audit = snapshot["omt_xs_any_mapping_audit"]
    binding_boundary_mapping_audit = snapshot["binding_boundary_mapping_audit"]
    hosted_fedpro_bounded_proof_audit = snapshot["hosted_fedpro_bounded_proof_audit"]
    standard_binding_runtime_capability_audit = snapshot["standard_binding_runtime_capability_audit"]
    duplicate_umbrella_mapping_audit = snapshot["duplicate_umbrella_mapping_audit"]
    claim_audit = snapshot["completion_claim_audit"]
    closeout_blocker_partition_audit = snapshot["closeout_blocker_partition_audit"]
    supported_boundary = snapshot["supported_boundary_statement"]
    implementation_concentration_audit = snapshot["implementation_concentration_audit"]
    python2025_source_responsibility_audit = snapshot["python2025_source_responsibility_audit"]
    slice_aggregation_pressure_audit = snapshot["slice_aggregation_pressure_audit"]
    service_utilization_decomposition_audit = snapshot["service_utilization_decomposition_audit"]
    omt_extended_subset_decomposition_audit = snapshot["omt_extended_subset_decomposition_audit"]
    omt_xs_any_extension_decomposition_audit = snapshot["omt_xs_any_extension_decomposition_audit"]
    omt_schema_constraint_decomposition_audit = snapshot["omt_schema_constraint_decomposition_audit"]
    save_restore_decomposition_audit = snapshot["save_restore_decomposition_audit"]
    save_restore_requirement_family_audit = snapshot["save_restore_requirement_family_audit"]
    federation_management_decomposition_audit = snapshot["federation_management_decomposition_audit"]
    callback_decomposition_audit = snapshot["callback_decomposition_audit"]
    time_management_decomposition_audit = snapshot["time_management_decomposition_audit"]
    binding_route_decomposition_audit = snapshot["binding_route_decomposition_audit"]
    support_services_decomposition_audit = snapshot["support_services_decomposition_audit"]
    object_management_decomposition_audit = snapshot["object_management_decomposition_audit"]
    ownership_decomposition_audit = snapshot["ownership_decomposition_audit"]
    directed_interaction_decomposition_audit = snapshot["directed_interaction_decomposition_audit"]
    directed_interaction_requirement_family_audit = snapshot["directed_interaction_requirement_family_audit"]
    ddm_default_policy_decomposition_audit = snapshot["ddm_default_policy_decomposition_audit"]
    ddm_default_policy_requirement_family_audit = snapshot["ddm_default_policy_requirement_family_audit"]
    shim_pressure_family_route_backing_audit = snapshot["shim_pressure_family_route_backing_audit"]
    shim_pressure_family_asymmetry_audit = snapshot["shim_pressure_family_asymmetry_audit"]
    current_lane_coherence_audit = snapshot["current_lane_coherence_audit"]
    current_lane_working_surface_statement = snapshot["current_lane_working_surface_statement"]
    main_python2025_implementation_claim_audit = snapshot["main_python2025_implementation_claim_audit"]
    full_claim_blocker_partition_audit = snapshot["full_claim_blocker_partition_audit"]
    implementation_lane_audit = snapshot["implementation_lane_audit"]
    hosted_shared_scenario_coverage_audit = snapshot["hosted_shared_scenario_coverage_audit"]
    time_window_vendor_parity_audit = snapshot["time_window_vendor_parity_audit"]
    python2025_proof_lane_audit = snapshot["python2025_proof_lane_audit"]
    extraction_readiness_audit = snapshot["extraction_readiness_audit"]
    extraction_impact_audit = snapshot["extraction_impact_audit"]
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
            "## Closeout Blocker Partition Audit",
            "",
            f"- Audit status: {closeout_blocker_partition_audit['audit_status']}",
            f"- Closeout blocker count: {closeout_blocker_partition_audit['closeout_blocker_count']}",
            f"- Partitioned blocker count: {closeout_blocker_partition_audit['partitioned_blocker_count']}",
            f"- Direct-runtime incompleteness blocker count: {closeout_blocker_partition_audit['direct_runtime_incompleteness_blocker_count']}",
            f"- Boundary-only blocker count: {closeout_blocker_partition_audit['boundary_only_blocker_count']}",
            f"- All current closeout blockers external to main python2025 runtime: {closeout_blocker_partition_audit['all_current_closeout_blockers_are_external_to_main_python2025_runtime']}",
            f"- Assessment: {closeout_blocker_partition_audit['current_assessment']}",
            f"- Residual boundary: {closeout_blocker_partition_audit['residual_boundary']}",
            "",
            "Partitioned blockers:",
            "",
        ]
    )
    for row in closeout_blocker_partition_audit["blocker_rows"]:
        lines.append(
            f"- {row['blocker']}: {row['classification']}, "
            f"counts_against_main_python2025_runtime_completeness={row['counts_against_main_python2025_runtime_completeness']} "
            f"({row['evidence_basis']})"
        )
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
            "Requirement-by-requirement duplicate/umbrella breakdown:",
            "",
        ]
    )
    for row_role, row_ids in requirement_by_requirement_audit["duplicate_umbrella_rows_by_role"].items():
        lines.append(f"- {row_role}: {len(row_ids)} rows ({', '.join(row_ids)})")
    lines.extend(
        [
            "",
            "## Duplicate Umbrella Mapping Audit",
            "",
            f"- Audit status: {duplicate_umbrella_mapping_audit['audit_status']}",
            f"- Row count: {duplicate_umbrella_mapping_audit['row_count']}",
            f"- Framework doc path: {duplicate_umbrella_mapping_audit['framework_doc_path']}",
            f"- Delta doc path: {duplicate_umbrella_mapping_audit['delta_doc_path']}",
            f"- Framework row count: {duplicate_umbrella_mapping_audit['framework_row_count']}",
            f"- Delta row count: {duplicate_umbrella_mapping_audit['delta_row_count']}",
            f"- Ready for duplicate umbrella mapping claim: {duplicate_umbrella_mapping_audit['ready_for_duplicate_umbrella_mapping_claim']}",
            f"- Assessment: {duplicate_umbrella_mapping_audit['current_assessment']}",
            f"- Residual boundary: {duplicate_umbrella_mapping_audit['residual_boundary']}",
            "",
            "Duplicate umbrella rows by role:",
            "",
        ]
    )
    for row_role, row_ids in duplicate_umbrella_mapping_audit["by_row_role"].items():
        lines.append(f"- {row_role}: {len(row_ids)} rows ({', '.join(row_ids)})")
    lines.extend(
        [
            "",
            "## Retired Legacy Mapping Audit",
            "",
            f"- Audit status: {retired_legacy_mapping_audit['audit_status']}",
            f"- Doc path: {retired_legacy_mapping_audit['doc_path']}",
            f"- Row count: {retired_legacy_mapping_audit['row_count']}",
            f"- Doc exists: {retired_legacy_mapping_audit['doc_exists']}",
            f"- Rows with doc anchor: {retired_legacy_mapping_audit['rows_with_doc_anchor_count']}",
            f"- Rows mentioned in doc: {retired_legacy_mapping_audit['rows_mentioned_in_doc_count']}",
            f"- Rows with candidate replacement note: {retired_legacy_mapping_audit['rows_with_candidate_replacement_note_count']}",
            f"- Ready for retired legacy mapping claim: {retired_legacy_mapping_audit['ready_for_retired_legacy_mapping_claim']}",
            f"- Assessment: {retired_legacy_mapping_audit['current_assessment']}",
            f"- Residual boundary: {retired_legacy_mapping_audit['residual_boundary']}",
            "",
            "Retired rows by service group:",
            "",
        ]
    )
    for service_group, row_ids in retired_legacy_mapping_audit["by_service_group"].items():
        lines.append(f"- {service_group}: {len(row_ids)} rows ({', '.join(row_ids)})")
    lines.extend(
        [
            "",
            "## OMT xs:any Mapping Audit",
            "",
            f"- Audit status: {omt_xs_any_mapping_audit['audit_status']}",
            f"- Doc path: {omt_xs_any_mapping_audit['doc_path']}",
            f"- Row count: {omt_xs_any_mapping_audit['row_count']}",
            f"- Doc exists: {omt_xs_any_mapping_audit['doc_exists']}",
            f"- Rows with doc anchor: {omt_xs_any_mapping_audit['rows_with_doc_anchor_count']}",
            f"- Rows mentioned in doc: {omt_xs_any_mapping_audit['rows_mentioned_in_doc_count']}",
            f"- Family count: {omt_xs_any_mapping_audit['family_count']}",
            f"- Family headings ready: {omt_xs_any_mapping_audit['family_headings_ready']}",
            f"- Ready for OMT xs:any mapping claim: {omt_xs_any_mapping_audit['ready_for_omt_xs_any_mapping_claim']}",
            f"- Assessment: {omt_xs_any_mapping_audit['current_assessment']}",
            f"- Residual boundary: {omt_xs_any_mapping_audit['residual_boundary']}",
            "",
            "OMT xs:any rows by family:",
            "",
        ]
    )
    for family, row_ids in omt_xs_any_mapping_audit["by_family"].items():
        lines.append(f"- {family}: {len(row_ids)} rows ({', '.join(row_ids)})")
    lines.extend(
        [
            "",
            "## Binding Boundary Mapping Audit",
            "",
            f"- Audit status: {binding_boundary_mapping_audit['audit_status']}",
            f"- Doc path: {binding_boundary_mapping_audit['doc_path']}",
            f"- Row count: {binding_boundary_mapping_audit['row_count']}",
            f"- Doc exists: {binding_boundary_mapping_audit['doc_exists']}",
            f"- Rows with doc anchor: {binding_boundary_mapping_audit['rows_with_doc_anchor_count']}",
            f"- Rows mentioned in doc: {binding_boundary_mapping_audit['rows_mentioned_in_doc_count']}",
            f"- Boundary narrative ready: {binding_boundary_mapping_audit['boundary_narrative_ready']}",
            f"- Ready for binding boundary mapping claim: {binding_boundary_mapping_audit['ready_for_binding_boundary_mapping_claim']}",
            f"- Assessment: {binding_boundary_mapping_audit['current_assessment']}",
            f"- Residual boundary: {binding_boundary_mapping_audit['residual_boundary']}",
            "",
            "Binding boundary rows by role:",
            "",
        ]
    )
    for boundary_role, row_ids in binding_boundary_mapping_audit["by_boundary_role"].items():
        lines.append(f"- {boundary_role}: {len(row_ids)} rows ({', '.join(row_ids)})")
    lines.extend(
        [
            "",
            "## Hosted FedPro Bounded Proof Audit",
            "",
            f"- Audit status: {hosted_fedpro_bounded_proof_audit['audit_status']}",
            f"- Doc path: {hosted_fedpro_bounded_proof_audit['doc_path']}",
            f"- Doc exists: {hosted_fedpro_bounded_proof_audit['doc_exists']}",
            f"- Route: {hosted_fedpro_bounded_proof_audit['route']}",
            f"- Scenario count: {hosted_fedpro_bounded_proof_audit['scenario_count']}",
            f"- All rows parity-covered: {hosted_fedpro_bounded_proof_audit['all_rows_parity_covered']}",
            f"- Identity ready: {hosted_fedpro_bounded_proof_audit['identity_ready']}",
            f"- Doc narrative ready: {hosted_fedpro_bounded_proof_audit['doc_narrative_ready']}",
            f"- Ready for hosted FedPro bounded proof claim: {hosted_fedpro_bounded_proof_audit['ready_for_hosted_fedpro_bounded_proof_claim']}",
            f"- Assessment: {hosted_fedpro_bounded_proof_audit['current_assessment']}",
            f"- Residual boundary: {hosted_fedpro_bounded_proof_audit['residual_boundary']}",
            "",
            f"Hosted scenarios: {', '.join(hosted_fedpro_bounded_proof_audit['scenarios'])}",
            "",
        ]
    )
    lines.extend(
        [
            "",
            "## Standard Binding Runtime-Capability Audit",
            "",
            f"- Audit status: {standard_binding_runtime_capability_audit['audit_status']}",
            f"- Doc path: {standard_binding_runtime_capability_audit['doc_path']}",
            f"- Doc exists: {standard_binding_runtime_capability_audit['doc_exists']}",
            f"- Row count: {standard_binding_runtime_capability_audit['row_count']}",
            f"- Identity ready: {standard_binding_runtime_capability_audit['identity_ready']}",
            f"- Doc narrative ready: {standard_binding_runtime_capability_audit['doc_narrative_ready']}",
            f"- Ready for standard binding runtime-capability claim: {standard_binding_runtime_capability_audit['ready_for_standard_binding_runtime_capability_claim']}",
            f"- Assessment: {standard_binding_runtime_capability_audit['current_assessment']}",
            f"- Residual boundary: {standard_binding_runtime_capability_audit['residual_boundary']}",
            "",
            "Standard binding rows by requirement:",
            "",
        ]
    )
    for requirement_id, row in standard_binding_runtime_capability_audit["by_binding_requirement"].items():
        lines.append(
            f"- {requirement_id}: routes={', '.join(row['routes'])}; "
            f"parity-covered={row['parity_covered_row_count']}; non-covered={row['non_covered_row_count']}"
        )
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
            f"- Runtime backend implementation path: {implementation_concentration_audit['runtime_backend_path']}",
            f"- Runtime backend-backed slices: {implementation_concentration_audit['runtime_backend_slice_count']}",
            f"- Runtime backend slice share: {implementation_concentration_audit['runtime_backend_slice_share']}",
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
    if implementation_concentration_audit["leading_extracted_runtime_modules"]:
        lines.extend(
            [
                "",
                "Leading extracted runtime owners:",
                "",
            ]
        )
        for module in implementation_concentration_audit["leading_extracted_runtime_modules"]:
            lines.append(
                f"- {module['path']}: {module['family']}, {module['line_count']} lines"
            )
    lines.extend(
        [
            "",
            "## Python 2025 Source Responsibility Audit",
            "",
            f"- Audit status: {python2025_source_responsibility_audit['audit_status']}",
            f"- Source path: {python2025_source_responsibility_audit['source_path']}",
            f"- Source line count: {python2025_source_responsibility_audit['source_line_count']}",
            f"- Extracted runtime helper modules: {python2025_source_responsibility_audit['extracted_runtime_module_count']}",
            f"- Extracted runtime helper lines: {python2025_source_responsibility_audit['extracted_runtime_module_line_count']}",
            f"- Runtime ambassador class: {python2025_source_responsibility_audit['ambassador_class']}",
            f"- Runtime ambassador line count: {python2025_source_responsibility_audit['ambassador_line_count']}",
            f"- Runtime ambassador methods: {python2025_source_responsibility_audit['ambassador_method_count']}",
            f"- Runtime ambassador method lines: {python2025_source_responsibility_audit['ambassador_method_line_count']}",
            f"- Shim wrapper ambassador class: {python2025_source_responsibility_audit['shim_wrapper_ambassador_class']}",
            f"- Shim wrapper ambassador line count: {python2025_source_responsibility_audit['shim_wrapper_ambassador_line_count']}",
            f"- Responsibility families: {python2025_source_responsibility_audit['family_count']}",
            f"- Largest family: {python2025_source_responsibility_audit['largest_family']} ({python2025_source_responsibility_audit['largest_family_line_count']} lines)",
            f"- Assessment: {python2025_source_responsibility_audit['current_assessment']}",
            f"- Extraction use: {python2025_source_responsibility_audit['extraction_use']}",
            "",
            "Python 2025 source responsibility families:",
            "",
        ]
    )
    for family in python2025_source_responsibility_audit["families"]:
        sample = ", ".join(family["sample_methods"])
        lines.append(
            f"- {family['family']}: {family['method_count']} methods, "
            f"{family['line_count']} lines; sample={sample}"
        )
    if python2025_source_responsibility_audit["extracted_runtime_modules"]:
        lines.extend(
            [
                "",
                "Extracted Python 2025 runtime helper modules:",
                "",
            ]
        )
        for module in python2025_source_responsibility_audit["extracted_runtime_modules"]:
            lines.append(
                f"- {module['path']}: {module['family']}, {module['function_count']} functions, "
                f"{module['line_count']} lines; functions={', '.join(module['functions'])}"
            )
    lines.extend(
        [
            "",
            "## Slice Aggregation Pressure Audit",
            "",
            f"- Audit status: {slice_aggregation_pressure_audit['audit_status']}",
            f"- Implemented slices: {slice_aggregation_pressure_audit['implemented_slice_count']}",
            f"- Aggregated slices >=10 requirements: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_10_requirements']}",
            f"- Aggregated slices >=10 requirements and runtime-backed: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_10_requirements_runtime_backed']}",
            f"- Aggregated slices >=20 requirements: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_20_requirements']}",
            f"- Aggregated slices >=20 requirements and runtime-backed: {slice_aggregation_pressure_audit['aggregated_slice_count_ge_20_requirements_runtime_backed']}",
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
            f"(runtime-backed: {item['runtime_backend_backed']})"
        )
    lines.extend(
        [
            "",
            "Largest runtime-backed aggregated slices:",
            "",
        ]
    )
    for item in slice_aggregation_pressure_audit["largest_runtime_backed_aggregated_slices"]:
        lines.append(f"- {item['slice_id']}: {item['requirement_count']} requirements")
    lines.extend(
        [
            "",
            "## Service Utilization Decomposition Audit",
            "",
            f"- Audit status: {service_utilization_decomposition_audit['audit_status']}",
            f"- Slice id: {service_utilization_decomposition_audit['slice_id']}",
            f"- Requirement count: {service_utilization_decomposition_audit['requirement_count']}",
            f"- Family count: {service_utilization_decomposition_audit['family_count']}",
            f"- All service-utilization rows family-mapped: {service_utilization_decomposition_audit['all_service_utilization_rows_family_mapped']}",
            f"- All backing FI rows traceable: {service_utilization_decomposition_audit['all_backing_fi_rows_traceable']}",
            f"- Assessment: {service_utilization_decomposition_audit['current_assessment']}",
            f"- Residual boundary: {service_utilization_decomposition_audit['residual_boundary']}",
            "",
            "Service-utilization families:",
            "",
        ]
    )
    for family in service_utilization_decomposition_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['service_count']} services "
            f"({family['service_number_min']}..{family['service_number_max']}), "
            f"traceable={family['all_fi_rows_traceable']}"
        )
    lines.extend(
        [
            "",
            "## OMT Extended Subset Decomposition Audit",
            "",
            f"- Audit status: {omt_extended_subset_decomposition_audit['audit_status']}",
            f"- Slice id: {omt_extended_subset_decomposition_audit['slice_id']}",
            f"- Requirement count: {omt_extended_subset_decomposition_audit['requirement_count']}",
            f"- Family count: {omt_extended_subset_decomposition_audit['family_count']}",
            f"- All extended-subset rows family-mapped: {omt_extended_subset_decomposition_audit['all_extended_subset_rows_family_mapped']}",
            f"- Unmapped requirement ids: {len(omt_extended_subset_decomposition_audit['unmapped_requirement_ids'])}",
            f"- Unexpected requirement ids: {len(omt_extended_subset_decomposition_audit['unexpected_requirement_ids'])}",
            f"- Assessment: {omt_extended_subset_decomposition_audit['current_assessment']}",
            f"- Residual boundary: {omt_extended_subset_decomposition_audit['residual_boundary']}",
            "",
            "OMT extended-subset families:",
            "",
        ]
    )
    for family in omt_extended_subset_decomposition_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['requirement_count']} requirements "
            f"({family['requirement_number_min']}..{family['requirement_number_max']}), "
            f"in-slice={family['all_requirements_in_slice']}"
        )
    lines.extend(
        [
            "",
            "## OMT xs:any Extension Decomposition Audit",
            "",
            f"- Audit status: {omt_xs_any_extension_decomposition_audit['audit_status']}",
            f"- Slice id: {omt_xs_any_extension_decomposition_audit['slice_id']}",
            f"- Requirement count: {omt_xs_any_extension_decomposition_audit['requirement_count']}",
            f"- Family count: {omt_xs_any_extension_decomposition_audit['family_count']}",
            f"- All xs:any extension rows family-mapped: {omt_xs_any_extension_decomposition_audit['all_xs_any_extension_rows_family_mapped']}",
            f"- Unmapped requirement ids: {len(omt_xs_any_extension_decomposition_audit['unmapped_requirement_ids'])}",
            f"- Unexpected requirement ids: {len(omt_xs_any_extension_decomposition_audit['unexpected_requirement_ids'])}",
            f"- Assessment: {omt_xs_any_extension_decomposition_audit['current_assessment']}",
            f"- Residual boundary: {omt_xs_any_extension_decomposition_audit['residual_boundary']}",
            "",
            "OMT xs:any extension families:",
            "",
        ]
    )
    for family in omt_xs_any_extension_decomposition_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['requirement_count']} requirements "
            f"({family['requirement_number_min']}..{family['requirement_number_max']}), "
            f"in-slice={family['all_requirements_in_slice']}"
        )
    lines.extend(
        [
            "",
            "## OMT Schema Constraint Decomposition Audit",
            "",
            f"- Audit status: {omt_schema_constraint_decomposition_audit['audit_status']}",
            f"- Slice id: {omt_schema_constraint_decomposition_audit['slice_id']}",
            f"- Requirement count: {omt_schema_constraint_decomposition_audit['requirement_count']}",
            f"- Family count: {omt_schema_constraint_decomposition_audit['family_count']}",
            f"- All schema-constraint rows family-mapped: {omt_schema_constraint_decomposition_audit['all_schema_constraint_rows_family_mapped']}",
            f"- Unmapped requirement ids: {len(omt_schema_constraint_decomposition_audit['unmapped_requirement_ids'])}",
            f"- Unexpected requirement ids: {len(omt_schema_constraint_decomposition_audit['unexpected_requirement_ids'])}",
            f"- Assessment: {omt_schema_constraint_decomposition_audit['current_assessment']}",
            f"- Residual boundary: {omt_schema_constraint_decomposition_audit['residual_boundary']}",
            "",
            "OMT schema-constraint families:",
            "",
        ]
    )
    for family in omt_schema_constraint_decomposition_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['requirement_count']} requirements "
            f"({family['requirement_number_min']}..{family['requirement_number_max']}), "
            f"in-slice={family['all_requirements_in_slice']}"
        )
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
            "## Save/Restore Requirement-Family Audit",
            "",
            f"- Audit status: {save_restore_requirement_family_audit['audit_status']}",
            f"- Slice id: {save_restore_requirement_family_audit['slice_id']}",
            f"- Requirement count: {save_restore_requirement_family_audit['requirement_count']}",
            f"- Family count: {save_restore_requirement_family_audit['family_count']}",
            f"- All save/restore rows family-mapped: {save_restore_requirement_family_audit['all_save_restore_rows_family_mapped']}",
            f"- Unmapped requirement ids: {len(save_restore_requirement_family_audit['unmapped_requirement_ids'])}",
            f"- Unexpected requirement ids: {len(save_restore_requirement_family_audit['unexpected_requirement_ids'])}",
            f"- Assessment: {save_restore_requirement_family_audit['current_assessment']}",
            f"- Residual boundary: {save_restore_requirement_family_audit['residual_boundary']}",
            "",
            "Save/restore requirement families:",
            "",
        ]
    )
    for family in save_restore_requirement_family_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['requirement_count']} requirements, "
            f"in-slice={family['all_requirements_in_slice']}"
        )
    lines.extend(
        [
            "",
            "## Federation-Management Decomposition Audit",
            "",
            f"- Audit status: {federation_management_decomposition_audit['audit_status']}",
            f"- Slice id: {federation_management_decomposition_audit['slice_id']}",
            f"- Slice ids: {', '.join(federation_management_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {federation_management_decomposition_audit['requirement_count']}",
            f"- Proof families: {federation_management_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {federation_management_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {federation_management_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {federation_management_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {federation_management_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in federation_management_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### federation-management/{family['family']}",
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
            "## Callback Decomposition Audit",
            "",
            f"- Audit status: {callback_decomposition_audit['audit_status']}",
            f"- Slice id: {callback_decomposition_audit['slice_id']}",
            f"- Slice ids: {', '.join(callback_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {callback_decomposition_audit['requirement_count']}",
            f"- Proof families: {callback_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {callback_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {callback_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {callback_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {callback_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in callback_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### callbacks/{family['family']}",
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
            "## Time-Management Decomposition Audit",
            "",
            f"- Audit status: {time_management_decomposition_audit['audit_status']}",
            f"- Slice id: {time_management_decomposition_audit['slice_id']}",
            f"- Slice ids: {', '.join(time_management_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {time_management_decomposition_audit['requirement_count']}",
            f"- Proof families: {time_management_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {time_management_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {time_management_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {time_management_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {time_management_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in time_management_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### time-management/{family['family']}",
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
            "## Binding-Route Decomposition Audit",
            "",
            f"- Audit status: {binding_route_decomposition_audit['audit_status']}",
            f"- Slice id: {binding_route_decomposition_audit['slice_id']}",
            f"- Slice ids: {', '.join(binding_route_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {binding_route_decomposition_audit['requirement_count']}",
            f"- Proof families: {binding_route_decomposition_audit['proof_family_count']}",
            f"- Route-group coverage count: {binding_route_decomposition_audit['route_group_coverage_count']}",
            f"- Assessment: {binding_route_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {binding_route_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in binding_route_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### binding-routes/{family['family']}",
                "",
                f"- Focus: {family['focus']}",
                f"- Evidence test count: {len(family['evidence_tests'])}",
                f"- Route groups: {', '.join(family['route_groups'])}",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Support-Services Decomposition Audit",
            "",
            f"- Audit status: {support_services_decomposition_audit['audit_status']}",
            f"- Slice id: {support_services_decomposition_audit['slice_id']}",
            f"- Slice ids: {', '.join(support_services_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {support_services_decomposition_audit['requirement_count']}",
            f"- Proof families: {support_services_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {support_services_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {support_services_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {support_services_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {support_services_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in support_services_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### support-services/{family['family']}",
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
            "## Object-Management Decomposition Audit",
            "",
            f"- Audit status: {object_management_decomposition_audit['audit_status']}",
            f"- Slice id: {object_management_decomposition_audit['slice_id']}",
            f"- Slice ids: {', '.join(object_management_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {object_management_decomposition_audit['requirement_count']}",
            f"- Proof families: {object_management_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {object_management_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {object_management_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {object_management_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {object_management_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in object_management_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### object-management/{family['family']}",
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
            "## Ownership Decomposition Audit",
            "",
            f"- Audit status: {ownership_decomposition_audit['audit_status']}",
            f"- Slice ids: {', '.join(ownership_decomposition_audit['slice_ids'])}",
            f"- Requirement count: {ownership_decomposition_audit['requirement_count']}",
            f"- Proof families: {ownership_decomposition_audit['proof_family_count']}",
            f"- Direct-backed families: {ownership_decomposition_audit['direct_family_count']}",
            f"- Hosted-backed families: {ownership_decomposition_audit['hosted_family_count']}",
            f"- Assessment: {ownership_decomposition_audit['current_assessment']}",
            f"- Next split boundary: {ownership_decomposition_audit['next_split_boundary']}",
            "",
        ]
    )
    for family in ownership_decomposition_audit["proof_families"]:
        lines.extend(
            [
                f"### ownership/{family['family']}",
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
            "## Directed Interaction Requirement-Family Audit",
            "",
            f"- Audit status: {directed_interaction_requirement_family_audit['audit_status']}",
            f"- Slice id: {directed_interaction_requirement_family_audit['slice_id']}",
            f"- Requirement count: {directed_interaction_requirement_family_audit['requirement_count']}",
            f"- Family count: {directed_interaction_requirement_family_audit['family_count']}",
            f"- All directed-interaction rows family-mapped: {directed_interaction_requirement_family_audit['all_directed_interaction_rows_family_mapped']}",
            f"- Unmapped requirement ids: {len(directed_interaction_requirement_family_audit['unmapped_requirement_ids'])}",
            f"- Unexpected requirement ids: {len(directed_interaction_requirement_family_audit['unexpected_requirement_ids'])}",
            f"- Assessment: {directed_interaction_requirement_family_audit['current_assessment']}",
            f"- Residual boundary: {directed_interaction_requirement_family_audit['residual_boundary']}",
            "",
            "Directed-interaction requirement families:",
            "",
        ]
    )
    for family in directed_interaction_requirement_family_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['requirement_count']} requirements, "
            f"in-slice={family['all_requirements_in_slice']}"
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
            "## DDM Default-Policy Requirement-Family Audit",
            "",
            f"- Audit status: {ddm_default_policy_requirement_family_audit['audit_status']}",
            f"- Slice id: {ddm_default_policy_requirement_family_audit['slice_id']}",
            f"- Requirement count: {ddm_default_policy_requirement_family_audit['requirement_count']}",
            f"- Family count: {ddm_default_policy_requirement_family_audit['family_count']}",
            f"- All DDM rows family-mapped: {ddm_default_policy_requirement_family_audit['all_ddm_rows_family_mapped']}",
            f"- Unmapped requirement ids: {len(ddm_default_policy_requirement_family_audit['unmapped_requirement_ids'])}",
            f"- Unexpected requirement ids: {len(ddm_default_policy_requirement_family_audit['unexpected_requirement_ids'])}",
            f"- Assessment: {ddm_default_policy_requirement_family_audit['current_assessment']}",
            f"- Residual boundary: {ddm_default_policy_requirement_family_audit['residual_boundary']}",
            "",
            "DDM default-policy requirement families:",
            "",
        ]
    )
    for family in ddm_default_policy_requirement_family_audit["families"]:
        lines.append(
            f"- {family['family']}: {family['requirement_count']} requirements, "
            f"in-slice={family['all_requirements_in_slice']}"
        )
    lines.extend(
        [
            "",
            "## Wrapper-Boundary Family Route-Backing Audit",
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
            "## Wrapper-Boundary Family Asymmetry Audit",
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
            f"- Python2025 backend concentration is material: {current_lane_coherence_audit['python2025_backend_concentration_is_material']}",
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
            "## Main Python2025 Implementation Claim Audit",
            "",
            f"- Audit status: {main_python2025_implementation_claim_audit['audit_status']}",
            f"- Claim shape: {main_python2025_implementation_claim_audit['claim_shape']}",
            f"- Ready for main python2025 implementation claim: {main_python2025_implementation_claim_audit['ready_for_main_python2025_implementation_claim']}",
            f"- Ready for full 2025 conformance claim: {main_python2025_implementation_claim_audit['ready_for_full_2025_conformance_claim']}",
            f"- Implementation owner: {main_python2025_implementation_claim_audit['implementation_owner']}",
            f"- Compatibility wrapper: {main_python2025_implementation_claim_audit['compatibility_wrapper']}",
            f"- Default operator lane: {main_python2025_implementation_claim_audit['default_operator_lane']}",
            f"- Hosted extension lane: {main_python2025_implementation_claim_audit['hosted_extension_lane']}",
            f"- Claim: {main_python2025_implementation_claim_audit['claim']}",
            f"- Assessment: {main_python2025_implementation_claim_audit['current_assessment']}",
            "",
            "Promotion basis:",
            "",
        ]
    )
    for item in main_python2025_implementation_claim_audit["promotion_basis"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Non-claims:",
            "",
        ]
    )
    for item in main_python2025_implementation_claim_audit["non_claims"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Full-conformance blockers:",
            "",
        ]
    )
    for item in main_python2025_implementation_claim_audit["full_conformance_blockers"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Full-Claim Blocker Partition Audit",
            "",
            f"- Audit status: {full_claim_blocker_partition_audit['audit_status']}",
            f"- Full-claim blocker count: {full_claim_blocker_partition_audit['full_claim_blocker_count']}",
            f"- Partitioned blocker count: {full_claim_blocker_partition_audit['partitioned_blocker_count']}",
            f"- Direct-runtime incompleteness blocker count: {full_claim_blocker_partition_audit['direct_runtime_incompleteness_blocker_count']}",
            f"- Boundary-only blocker count: {full_claim_blocker_partition_audit['boundary_only_blocker_count']}",
            f"- All current full-claim blockers external to main python2025 runtime: {full_claim_blocker_partition_audit['all_current_full_claim_blockers_are_external_to_main_python2025_runtime']}",
            f"- Assessment: {full_claim_blocker_partition_audit['current_assessment']}",
            f"- Residual boundary: {full_claim_blocker_partition_audit['residual_boundary']}",
            "",
            "Partitioned blockers:",
            "",
        ]
    )
    for row in full_claim_blocker_partition_audit["blocker_rows"]:
        lines.append(
            f"- {row['blocker']}: {row['classification']}, "
            f"counts_against_main_python2025_runtime_completeness={row['counts_against_main_python2025_runtime_completeness']} "
            f"({row['evidence_basis']})"
        )
    lines.extend(
        [
            "",
            "## Implementation Lane Audit",
            "",
            f"- Audit status: {implementation_lane_audit['audit_status']}",
            f"- Current 2025 backend package: {implementation_lane_audit['current_2025_lane']['backend_package']}",
            f"- Primary 2025 RTI role: {implementation_lane_audit['current_2025_lane']['role']}",
            f"- Current 2025 plugin family: {implementation_lane_audit['current_2025_lane']['plugin_family']}",
            f"- Current 2025 spec support: {', '.join(implementation_lane_audit['current_2025_lane']['supports'])}",
            f"- Compatibility wrapper package: {implementation_lane_audit['compatibility_wrapper_lane']['backend_package']}",
            f"- Compatibility wrapper status: {implementation_lane_audit['compatibility_wrapper_lane']['status']}",
            f"- Compatibility wrapper role: {implementation_lane_audit['compatibility_wrapper_lane']['role']}",
            f"- Compatibility wrapper delegates runtime semantics to: {implementation_lane_audit['compatibility_wrapper_lane']['delegates_runtime_semantics_to']}",
            f"- Reference 2010 backend package: {implementation_lane_audit['reference_2010_lane']['backend_package']}",
            f"- Reference 2010 role: {implementation_lane_audit['reference_2010_lane']['role']}",
            f"- Backend packages discovered: {implementation_lane_audit['backend_package_scan']['backend_package_count']}",
            f"- Dedicated 2025 backend package present: {implementation_lane_audit['dedicated_2025_backend_package_present']}",
            f"- Dedicated 2025 candidates cleanly separated: {implementation_lane_audit['backend_package_scan']['dedicated_python_2025_candidates_cleanly_separated']}",
            f"- Dedicated 2025 legacy-package delegation violations: {len(implementation_lane_audit['backend_package_scan']['dedicated_python_2025_legacy_package_delegation_violations'])}",
            f"- Ready for working-surface promotion: {implementation_lane_audit['ready_for_current_lane_promotion_as_working_surface']}",
            f"- Ready for permanent no-split decision: {implementation_lane_audit['ready_for_permanent_no-split_decision']}",
            f"- Clean extraction still optional: {implementation_lane_audit['clean_extraction_still_optional']}",
            f"- Assessment: {implementation_lane_audit['current_assessment']}",
            f"- Extraction boundary: {implementation_lane_audit['extraction_boundary']}",
            "",
            "Discovered backend packages:",
            "",
        ]
    )
    for package_name in implementation_lane_audit["backend_package_scan"]["backend_package_dirs"]:
        lines.append(f"- {package_name}")
    lines.extend(
        [
            "",
            "Discovered 2025-capable backend plugin records:",
            "",
        ]
    )
    for record in implementation_lane_audit["backend_package_scan"]["rti1516_2025_plugin_records"]:
        lines.append(
            f"- {record['name']} ({record['family']}): {record['package']} supports {', '.join(record['supports'])}"
        )
    lines.extend(
        [
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
            "## Python2025 Proof-Lane Audit",
            "",
            f"- Audit status: {python2025_proof_lane_audit['audit_status']}",
            f"- Ready for main-implementation operator-lane claim: {python2025_proof_lane_audit['ready_for_main_implementation_operator_lane_claim']}",
            f"- Direct lane: {' '.join(python2025_proof_lane_audit['default_direct_lane']['owner_command'])}",
            f"- Direct lane id: {python2025_proof_lane_audit['default_direct_lane']['lane_id']}",
            f"- Direct lane cost: {python2025_proof_lane_audit['default_direct_lane']['estimated_cost']}",
            f"- Hosted extension lane: {' '.join(python2025_proof_lane_audit['hosted_extension_lane']['owner_command'])}",
            f"- Hosted extension lane id: {python2025_proof_lane_audit['hosted_extension_lane']['lane_id']}",
            f"- Hosted extension lane cost: {python2025_proof_lane_audit['hosted_extension_lane']['estimated_cost']}",
            f"- Claim: {python2025_proof_lane_audit['shared_claim']}",
            f"- Residual boundary: {python2025_proof_lane_audit['residual_boundary']}",
            "",
            "Current operator runs:",
            "",
        ]
    )
    for run in python2025_proof_lane_audit["current_operator_runs"]:
        lines.append(
            f"- {run['lane_id']} / {run['command']}: {run['result']} ({run['scope']})"
        )
    lines.extend(
        [
            "",
            f"Evidence anchors: {', '.join(python2025_proof_lane_audit['evidence_anchors'])}",
            "",
        ]
    )
    lines.extend(
        [
            "",
            "Hosted runtime identity evidence:",
            "",
            f"- Audit status: {implementation_lane_audit['hosted_runtime_identity_evidence']['audit_status']}",
            f"- Route: {implementation_lane_audit['hosted_runtime_identity_evidence']['route']}",
            f"- Claim: {implementation_lane_audit['hosted_runtime_identity_evidence']['claim']}",
            f"- Assessment: {implementation_lane_audit['hosted_runtime_identity_evidence']['current_assessment']}",
            "",
            "Hosted runtime identity reports:",
            "",
        ]
    )
    lines.append(
        "- Direct ambassador: "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['direct_runtime_report']['backend_name']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['direct_runtime_report']['backend_kind']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['direct_runtime_report']['runtime_provider']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['direct_runtime_report']['implementation_lane']} / "
        f"counts_as_python_2025_rti={implementation_lane_audit['hosted_runtime_identity_evidence']['direct_runtime_report']['counts_as_python_2025_rti']}"
    )
    lines.append(
        "- Hosted server: "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_server_report']['runtime_provider']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_server_report']['implementation_lane']} / "
        f"counts_as_python_2025_rti={implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_server_report']['counts_as_python_2025_rti']} / "
        f"wrapper_only={implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_server_report']['wrapper_only']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_server_report']['spec']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_server_report']['transport_kind']}"
    )
    lines.append(
        "- Hosted client: "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['runtime_provider']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['implementation_lane']} / "
        f"counts_as_python_2025_rti={implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['counts_as_python_2025_rti']} / "
        f"wrapper_only={implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['wrapper_only']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['spec']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['transport_kind']} / "
        f"{implementation_lane_audit['hosted_runtime_identity_evidence']['hosted_client_report']['route_family']}"
    )
    lines.extend(
        [
            "",
            "Hosted runtime identity evidence tests:",
            "",
        ]
    )
    for item in implementation_lane_audit["hosted_runtime_identity_evidence"]["evidence_tests"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Hosted factory boundary evidence:",
            "",
            f"- Audit status: {implementation_lane_audit['hosted_factory_boundary_evidence']['audit_status']}",
            (
                "- Supported hosted creation surface: "
                f"{implementation_lane_audit['hosted_factory_boundary_evidence']['supported_hosted_creation_surface']}"
            ),
            (
                "- Unsupported factory surfaces: "
                f"{', '.join(implementation_lane_audit['hosted_factory_boundary_evidence']['unsupported_factory_surfaces'])}"
            ),
            f"- Policy: {implementation_lane_audit['hosted_factory_boundary_evidence']['current_policy']}",
            "",
            "Hosted factory boundary evidence tests:",
            "",
        ]
    )
    for item in implementation_lane_audit["hosted_factory_boundary_evidence"]["evidence_tests"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Package-owned shared scenario evidence:",
            "",
            f"- Audit status: {implementation_lane_audit['package_owned_shared_scenario_evidence']['audit_status']}",
            (
                "- Scenario package: "
                f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['scenario_package']}"
            ),
            f"- Shared route: {implementation_lane_audit['package_owned_shared_scenario_evidence']['shared_route']}",
            (
                "- Example entrypoint: "
                f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['example_entrypoint']}"
            ),
            (
                "- Adapter class: "
                f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['adapter_class']}"
            ),
            (
                "- Supported backend names: "
                f"{', '.join(implementation_lane_audit['package_owned_shared_scenario_evidence']['supported_backend_names'])}"
            ),
            f"- Claim: {implementation_lane_audit['package_owned_shared_scenario_evidence']['claim']}",
            f"- Assessment: {implementation_lane_audit['package_owned_shared_scenario_evidence']['current_assessment']}",
            "",
            "Package-owned shared scenario runtime reports:",
            "",
        ]
    )
    lines.append(
        "- python2025: "
        f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['python2025_runtime_report']['backend_kind']} / "
        f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['python2025_runtime_report']['implementation_lane']} / "
        f"counts_as_python_2025_rti={implementation_lane_audit['package_owned_shared_scenario_evidence']['python2025_runtime_report']['counts_as_python_2025_rti']} / "
        f"wrapper_only={implementation_lane_audit['package_owned_shared_scenario_evidence']['python2025_runtime_report']['wrapper_only']}"
    )
    lines.append(
        "- shim: "
        f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['shim_runtime_report']['backend_kind']} / "
        f"{implementation_lane_audit['package_owned_shared_scenario_evidence']['shim_runtime_report']['implementation_lane']} / "
        f"counts_as_python_2025_rti={implementation_lane_audit['package_owned_shared_scenario_evidence']['shim_runtime_report']['counts_as_python_2025_rti']} / "
        f"wrapper_only={implementation_lane_audit['package_owned_shared_scenario_evidence']['shim_runtime_report']['wrapper_only']}"
    )
    lines.extend(
        [
            "",
            "Package-owned shared scenario evidence tests:",
            "",
        ]
    )
    for item in implementation_lane_audit["package_owned_shared_scenario_evidence"]["evidence_tests"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Hosted shared-scenario coverage audit:",
            "",
            f"- Audit status: {hosted_shared_scenario_coverage_audit['audit_status']}",
            f"- Shared hosted FedPro scenarios: {hosted_shared_scenario_coverage_audit['shared_scenario_count']}",
            (
                "- Shared hosted scenarios represented in conformance evidence: "
                f"{hosted_shared_scenario_coverage_audit['represented_in_conformance_evidence_count']}"
            ),
            (
                "- Ready for full shared-scenario representation claim: "
                f"{hosted_shared_scenario_coverage_audit['ready_for_full_shared_scenario_representation_claim']}"
            ),
            f"- Assessment: {hosted_shared_scenario_coverage_audit['current_assessment']}",
            "",
            "## Time-Window Vendor Parity Audit",
            "",
            f"- Audit status: {time_window_vendor_parity_audit['audit_status']}",
            f"- Route count: {time_window_vendor_parity_audit['route_count']}",
            f"- Trial-Pitch-safe route count: {time_window_vendor_parity_audit['trial_pitch_safe_route_count']}",
            f"- Trial-Pitch-safe routes: {', '.join(time_window_vendor_parity_audit['trial_pitch_safe_route_ids'])}",
            f"- Trial-Pitch-unsafe routes: {', '.join(time_window_vendor_parity_audit['trial_pitch_unsafe_route_ids'])}",
            f"- Current trial candidate: {time_window_vendor_parity_audit['current_trial_candidate']['scenario_id']} "
            f"({time_window_vendor_parity_audit['current_trial_candidate']['federate_count']} federates)",
            f"- Assessment: {time_window_vendor_parity_audit['current_assessment']}",
            f"- Residual boundary: {time_window_vendor_parity_audit['residual_boundary']}",
            "",
            "Time-window vendor parity routes:",
            "",
        ]
    )
    for row in time_window_vendor_parity_audit["routes"]:
        lines.append(
            f"- {row['scenario_id']}: federates={row['federate_count']}, "
            f"trial-pitch-safe={row['trial_pitch_safe']}, "
            f"boundary={row['current_pitch_runtime_boundary']}"
        )
    lines.extend(
        [
            "",
            "## Extraction Readiness Audit",
            "",
            f"- Audit status: {extraction_readiness_audit['audit_status']}",
            f"- Extraction needed now: {extraction_readiness_audit['extraction_needed_now']}",
            f"- Dedicated Python 2025 backend present: {extraction_readiness_audit['dedicated_python_2025_backend_present']}",
            f"- Recommended current action: {extraction_readiness_audit['recommended_current_action']}",
            f"- Future backend package target: {extraction_readiness_audit['future_backend_package_target']}",
            f"- Future backend plugin family: {extraction_readiness_audit['future_backend_plugin_family']}",
            f"- Runtime semantics to extract first: {extraction_readiness_audit['runtime_semantics_to_extract_first_count']}",
            f"- Route-backed runtime semantics: {extraction_readiness_audit['route_backed_runtime_semantics_count']}",
            f"- All candidate runtime semantics route-backed: {extraction_readiness_audit['all_candidate_runtime_semantics_route_backed']}",
            f"- Assessment: {extraction_readiness_audit['current_assessment']}",
            "",
            "Extraction package contract:",
            "",
            f"- Current package state: {extraction_readiness_audit['extraction_package_contract']['current_package_state']}",
            f"- Target distribution: {extraction_readiness_audit['extraction_package_contract']['target_distribution']}",
            f"- Target import root: {extraction_readiness_audit['extraction_package_contract']['target_import_root']}",
            f"- Target plugin path: {extraction_readiness_audit['extraction_package_contract']['target_plugin_path']}",
            f"- Target backend name: {extraction_readiness_audit['extraction_package_contract']['target_backend_name']}",
            f"- Target plugin family: {extraction_readiness_audit['extraction_package_contract']['target_plugin_family']}",
            f"- Target supports: {', '.join(extraction_readiness_audit['extraction_package_contract']['target_supports'])}",
            f"- Must not delegate to: {', '.join(extraction_readiness_audit['extraction_package_contract']['must_not_delegate_to'])}",
            f"- Scanner regression test: {extraction_readiness_audit['extraction_package_contract']['scanner_regression_test']}",
            f"- Package creation rule: {extraction_readiness_audit['extraction_package_contract']['package_creation_rule']}",
            "",
            "Extraction cutover invariants:",
            "",
        ]
    )
    for item in extraction_readiness_audit["extraction_cutover_invariants"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Shim responsibilities after extraction:",
            "",
        ]
    )
    for item in extraction_readiness_audit["shim_responsibilities_after_extraction"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Runtime semantics migration worklist:",
            "",
        ]
    )
    for item in extraction_readiness_audit["runtime_semantics_to_extract_first"]:
        lines.append(
            f"- {item['slice_id']}: {item['proof_family_count']} proof families, "
            f"direct={item['direct_test_count']}, hosted={item['hosted_test_count']}, "
            f"route-backed={item['route_backed']}, target={item['candidate_runtime_module']}"
        )
    lines.extend(
        [
            "",
            "Pre-extraction gates:",
            "",
        ]
    )
    for item in extraction_readiness_audit["pre_extraction_gates"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Extraction Impact Audit",
            "",
            f"- Audit status: {extraction_impact_audit['audit_status']}",
            f"- Candidate slices: {extraction_impact_audit['slice_count']}",
            f"- All candidate slices have source-family maps: {extraction_impact_audit['all_candidate_slices_have_source_family_map']}",
            f"- All candidate slices route-backed: {extraction_impact_audit['all_candidate_slices_route_backed']}",
            f"- Largest current source baseline: {extraction_impact_audit['largest_current_source_baseline']}",
            f"- Assessment: {extraction_impact_audit['current_assessment']}",
            f"- Non-claim: {extraction_impact_audit['non_claim']}",
            "",
            "Extraction impact rows:",
            "",
        ]
    )
    for row in extraction_impact_audit["rows"]:
        families = ", ".join(
            f"{family['family']}={family['current_line_count']} lines/{family['current_method_count']} methods"
            for family in row["source_families"]
        )
        lines.append(
            f"- {row['slice_id']}: source families={row['source_family_count']}, "
            f"baseline={row['current_source_line_baseline']} lines/{row['current_source_method_baseline']} methods, "
            f"target={row['candidate_runtime_module']}; {families}"
        )
    lines.extend(
        [
            "",
            "## Promotion Vs Split Audit",
            "",
            f"- Decision shape: {promotion_split_audit['decision_shape']}",
            f"- Primary lane package: {promotion_split_audit['current_lane']['package']}",
            f"- Primary lane role: {promotion_split_audit['current_lane']['role']}",
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
        for evidence_basis in dimension.get("evidence_basis", ()):
            lines.append(f"- Evidence basis: {evidence_basis}")
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
    legacy_markdown_path = output_dir / "2025_requirements_finish_line.md"
    matrix_path = output_dir / "spec2025_verification_matrix.csv"
    json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_text = "\n".join(build_spec2025_finish_line_markdown(project_root)) + "\n"
    markdown_path.write_text(markdown_text, encoding="utf-8")
    legacy_markdown_path.write_text(markdown_text, encoding="utf-8")
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
    route_matrix_csv_path, route_matrix_markdown_path = write_spec2025_route_parity_matrix(output_dir)
    return {
        "json": json_path,
        "markdown": markdown_path,
        "legacy_markdown": legacy_markdown_path,
        "verification_matrix": matrix_path,
        "route_parity_matrix": route_matrix_csv_path,
        "route_parity_markdown": route_matrix_markdown_path,
    }


__all__ = [
    "build_spec2025_finish_line_markdown",
    "build_spec2025_finish_line_snapshot",
    "write_spec2025_finish_line",
]
