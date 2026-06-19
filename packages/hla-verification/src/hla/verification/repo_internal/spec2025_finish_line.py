"""Finish-line inventory for the IEEE 1516-2025 requirements tranche."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.verification.repo_internal.verification.spec2025_route_parity_matrix import summarize_spec2025_route_parity

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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-logical-time",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-101",
            "HLA2025-FI-SVC-102",
            "HLA2025-FI-SVC-103",
            "HLA2025-FI-SVC-104",
            "HLA2025-FI-SVC-105",
            "HLA2025-FI-SVC-106",
            "HLA2025-FI-SVC-107",
            "HLA2025-FI-SVC-108",
            "HLA2025-FI-SVC-109",
            "HLA2025-FI-SVC-110",
            "HLA2025-FI-SVC-111",
            "HLA2025-FI-SVC-112",
            "HLA2025-FI-SVC-113",
            "HLA2025-FI-SVC-114",
            "HLA2025-FI-SVC-115",
            "HLA2025-FI-SVC-116",
            "HLA2025-FI-SVC-117",
            "HLA2025-FI-SVC-118",
            "HLA2025-FI-SVC-119",
            "HLA2025-FI-SVC-120",
            "HLA2025-FI-SVC-121",
            "HLA2025-FI-SVC-122",
            "HLA2025-FI-SVC-123",
            "HLA2025-FI-SVC-125",
            "HLA2025-FR-010",
            "HLA2025-FI-009",
            "HLA2025-MOD-006",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "tests/backends/test_shim_route_trace_evidence.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py",
        ),
        "supported_scope": (
            "Python 2025 shim covers default logical-time factory selection, enable/disable time regulation, "
            "enable/disable time constrained, enable/disable asynchronous delivery, lookahead query/modify, "
            "timeAdvanceRequest, timeAdvanceRequestAvailable, nextMessageRequest, nextMessageRequestAvailable, "
            "flushQueueRequest, timeAdvanceGrant, flushQueueGrant, GALT/LITS/logical-time/lookahead queries, "
            "retract, requestRetraction callback delivery, attribute and interaction order-type changes, queued "
            "timestamped object updates/interactions, timestamp-order delivery on receiving federate time advance, "
            "and message retraction before delivery. Cross-binding parity remains separate backlog work."
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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports requestFederationSave and requestFederationRestore with initiate, begun, "
            "complete, abort, and query-status flows; federation save/restore lifecycle callbacks and status "
            "responses; successful federationSaved/federationRestored completion; missing-label restore failure; "
            "federate-reported save/restore failure; save/restore abort callbacks; object registry rollback; "
            "and joined-federate logical-time rollback."
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
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-switch-inquiry-control",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-008", "HLA2025-RET-001", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-fom-mim-error-taxonomy",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
    },
    {
        "id": "2025-callback-context-parameters",
        "status": "implemented-slice",
        "requirements": ("HLA2025-MOD-004", "HLA2025-RET-002", "HLA2025-FI-001"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
        ),
        "supported_scope": (
            "Python 2025 federate ambassador surface exposes direct callback context parameters "
            "for discovery, reflection, interaction, directed interaction, and remove callbacks "
            "without native Supplemental*Info helper objects."
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
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py",
            "packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports FOM-backed directed interaction publish, subscribe, unsubscribe, "
            "unpublish, and receiveDirectedInteraction callback delivery from a publisher to object-class "
            "directed subscribers. It also queues timestamped directed interactions until subscriber time advance, "
            "delivers timestamp order plus retraction handles on callback receipt, honors pre-delivery retract, "
            "supports selective directed interaction set unsubscribe/unpublish without collapsing sibling directed classes, and filters directed interaction delivery through target object update-region and "
            "subscribeInteractionClassWithRegions overlap. Java/C++/FedPro route parity remain later behavior work."
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
        "id": "2025-fedpro-transport-contract",
        "status": "implemented-slice",
        "requirements": ("HLA2025-BND-003", "HLA2025-FI-004"),
        "evidence": (
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "tests/transport/test_grpc_transport_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py",
            "packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto",
            "packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto",
        ),
        "supported_scope": (
            "2025 FedPro protobuf package, gRPC service binding, typed request/callback oneofs, and a hosted "
            "loopback runtime session are present for connect, create federation, join, FOM handle lookup, "
            "passive object-attribute and passive interaction subscribe alias routes, universal directed "
            "subscribe alias routing, "
            "available-dimension and dimension-bound queries, default attribute transportation/order policy calls, "
            "object registration, basic ownership divest/acquire callbacks, time-regulation/time-constrained/time-advance "
            "callbacks, queued timestamped attribute reflection/interaction receipt, plus directed-interaction "
            "receipt with selective directed set unsubscribe/unpublish, retraction handles, and pre-delivery retract, object discovery, attribute reflection, "
            "interaction receipt, directed interaction receipt, basic DDM region-overlap filtering for object attributes "
            "and directed interactions, "
            "service-reporting switch state, MOM service-invocation report callbacks over FedPro, "
            "synchronization point/status MOM reports over FedPro, resign, destroy, and disconnect. Full MOM "
            "action/request routing and full RTI semantics remain outside this slice."
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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim resolves object class, attribute, transportation, and dimension handles from the "
            "loaded FOM/FDD catalog, reports available dimensions for object and interaction classes, returns "
            "dimension upper bounds, stores validated default attribute transportation/order policy changes, "
            "uses those defaults when delivering reflectAttributeValues callbacks, and filters object attribute "
            "reflections through basic createRegion/commitRegionModifications/deleteRegion/setRangeBounds/"
            "registerObjectInstanceWithRegions/subscribeObjectClassAttributesWithRegions/"
            "unsubscribeObjectClassAttributesWithRegions/associateRegionsForUpdates/"
            "unassociateRegionsForUpdates/requestAttributeValueUpdateWithRegions DDM region overlap. It also "
            "filters interaction delivery through subscribeInteractionClassWithRegions/"
            "unsubscribeInteractionClassWithRegions/sendInteractionWithRegions region overlap and conveys sent "
            "regions on receiveInteraction callbacks. Attribute scope advisory callbacks report object-attribute "
            "in-scope and out-of-scope transitions for DDM region overlap changes."
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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports FOM-backed object instance registration, discoverObjectInstance delivery, "
            "attribute update publication gating, reflectAttributeValues delivery, interaction publication gating, "
            "sendInteraction, and receiveInteraction delivery for subscribed federates."
        ),
    },
    {
        "id": "2025-object-management-support-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-065",
            "HLA2025-FI-SVC-066",
            "HLA2025-FI-SVC-067",
            "HLA2025-FI-SVC-068",
            "HLA2025-FI-SVC-069",
            "HLA2025-FI-SVC-070",
            "HLA2025-FI-SVC-071",
            "HLA2025-FI-SVC-072",
            "HLA2025-FI-SVC-073",
            "HLA2025-FI-SVC-074",
            "HLA2025-FI-SVC-075",
            "HLA2025-FI-SVC-077",
            "HLA2025-FI-SVC-078",
            "HLA2025-FI-SVC-079",
            "HLA2025-FI-SVC-080",
            "HLA2025-FI-SVC-081",
            "HLA2025-FI-SVC-082",
            "HLA2025-FR-003",
            "HLA2025-FR-004",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_object_management_backend_matrix.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports FOM-backed deleteObjectInstance/removeObjectInstance callbacks, "
            "localDeleteObjectInstance validation, requestAttributeValueUpdate callbacks by object instance "
            "and object class, turnUpdatesOnForObjectInstance and turnUpdatesOffForObjectInstance advisory "
            "callbacks with update-rate designator delivery, attribute transportation type change/query callbacks, "
            "interaction transportation type change/query callbacks, and DDM-driven attributesInScope and "
            "attributesOutOfScope transitions."
        ),
    },
    {
        "id": "2025-single-name-reservation-services",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-SVC-051", "HLA2025-FI-SVC-052", "HLA2025-FI-SVC-053", "HLA2025-FI-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports single-name reservation requests, single-name reservation success and failure "
            "callbacks, releaseObjectInstanceName, not-connected and not-joined preconditions for release, save/restore in-progress blocking, reservation "
            "preservation through save/restore completion, release-driven handoff to a rival federate, and "
            "ObjectInstanceNameNotReserved on invalid single-name release."
        ),
    },
    {
        "id": "2025-multi-name-reservation-services",
        "status": "implemented-slice",
        "requirements": ("HLA2025-FI-SVC-054", "HLA2025-FI-SVC-055", "HLA2025-FI-SVC-056", "HLA2025-FI-001", "HLA2025-FI-005"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports reserveMultipleObjectInstanceNames and releaseMultipleObjectInstanceNames "
            "with set-wide success/failure callbacks, not-connected and not-joined preconditions, empty-set "
            "validation, save/restore in-progress blocking, reservation handoff after release, reservation cleanup "
            "on join teardown, and reservation preservation through save/restore snapshots."
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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports orderly disconnect state teardown and NotConnected preconditions. "
            "It also exposes a test-harness-only non-orderly connection-loss injector that delivers the "
            "connectionLost callback and tears down the local connection state without treating orderly "
            "disconnect as a fault."
        ),
    },
    {
        "id": "2025-federation-lifecycle-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-001",
            "HLA2025-FI-SVC-005",
            "HLA2025-FI-SVC-006",
            "HLA2025-FI-SVC-007",
            "HLA2025-FI-SVC-013",
            "HLA2025-FI-SVC-014",
            "HLA2025-FI-SVC-015",
            "HLA2025-FI-SVC-016",
            "HLA2025-FI-SVC-017",
            "HLA2025-FI-SVC-004",
            "HLA2025-FI-SVC-008",
            "HLA2025-FI-SVC-009",
            "HLA2025-FI-SVC-010",
            "HLA2025-FI-SVC-011",
            "HLA2025-FI-SVC-012",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim accepts 2025 connect requests, creates federation executions with resolved FOM "
            "modules and selected logical-time implementation, lists federation executions, joins named federates, "
            "reports federation execution members and missing-federation callbacks, registers synchronization "
            "points with announce/achieved/federationSynchronized callback flow, resigns joined federates, emits "
            "the federateResigned callback with resign context on local resign, and destroys federation executions "
            "once they are empty."
        ),
    },
    {
        "id": "2025-basic-declaration-services",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-047",
            "HLA2025-FI-SVC-048",
            "HLA2025-FI-SVC-049",
            "HLA2025-FI-SVC-050",
            "HLA2025-FI-SVC-035",
            "HLA2025-FI-SVC-036",
            "HLA2025-FI-SVC-037",
            "HLA2025-FI-SVC-038",
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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports publish and unpublish for object class attributes and interaction classes "
            "plus subscribe and unsubscribe for object class attributes and interaction classes. It also delivers "
            "startRegistrationForObjectClass, stopRegistrationForObjectClass, turnInteractionsOn, and "
            "turnInteractionsOff callbacks as publication and subscription state becomes relevant or irrelevant. "
            "Published state gates updateAttributeValues and sendInteraction delivery, and unsubscribe state stops "
            "subsequent reflectAttributeValues and receiveInteraction callbacks for the affected target federate."
        ),
    },
    {
        "id": "2025-support-query-lookups",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-138",
            "HLA2025-FI-SVC-139",
            "HLA2025-FI-SVC-140",
            "HLA2025-FI-SVC-141",
            "HLA2025-FI-SVC-142",
            "HLA2025-FI-SVC-143",
            "HLA2025-FI-SVC-144",
            "HLA2025-FI-SVC-145",
            "HLA2025-FI-SVC-146",
            "HLA2025-FI-SVC-147",
            "HLA2025-FI-SVC-148",
            "HLA2025-FI-SVC-149",
            "HLA2025-FI-SVC-150",
            "HLA2025-FI-SVC-151",
            "HLA2025-FI-SVC-152",
            "HLA2025-FI-SVC-153",
            "HLA2025-FI-SVC-154",
            "HLA2025-FI-SVC-155",
            "HLA2025-FI-SVC-156",
            "HLA2025-FI-SVC-158",
            "HLA2025-FI-SVC-163",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_support_services_backend_matrix.py",
            "tests/backends/test_python_backend_support_services.py",
            "tests/verification/test_spec_traceability_and_extended_python_rti.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports direct federate, object-class, known-object-class, object-instance, "
            "attribute, interaction-class, parameter, order, update-rate, transportation, available-dimension, "
            "and range-bounds handle/name lookups against the loaded FOM catalog."
        ),
    },
    {
        "id": "2025-support-handle-normalization-and-switches",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-162",
            "HLA2025-FI-SVC-165",
            "HLA2025-FI-SVC-166",
            "HLA2025-FI-SVC-167",
            "HLA2025-FI-SVC-168",
            "HLA2025-FI-SVC-169",
            "HLA2025-FI-SVC-170",
            "HLA2025-FI-SVC-171",
            "HLA2025-FI-SVC-172",
            "HLA2025-FI-SVC-173",
            "HLA2025-FI-SVC-174",
            "HLA2025-FI-SVC-175",
            "HLA2025-FI-SVC-176",
            "HLA2025-FI-SVC-177",
            "HLA2025-FI-SVC-178",
            "HLA2025-FI-SVC-179",
            "HLA2025-FI-SVC-180",
            "HLA2025-FI-SVC-181",
            "HLA2025-FI-SVC-182",
            "HLA2025-FI-SVC-183",
            "HLA2025-FI-SVC-184",
            "HLA2025-FI-SVC-185",
            "HLA2025-FI-SVC-186",
            "HLA2025-FI-SVC-187",
            "HLA2025-FI-SVC-188",
            "HLA2025-FI-SVC-189",
            "HLA2025-FI-SVC-190",
            "HLA2025-FI-SVC-191",
            "HLA2025-FI-SVC-192",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/backends/test_python_backend_time_ddm_extended.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim normalizes object class, interaction class, object instance, and federate handles "
            "with typed-handle validation and wrong-family rejection, and returns dimension handle sets for joined "
            "regions. It also implements explicit get/set support "
            "for object-class relevance, attribute relevance, attribute scope, interaction relevance, convey "
            "region designator sets, automatic resign directive, service reporting, exception reporting, "
            "send-service-reports-to-file, auto-provide, delay-subscription-evaluation, advisories-use-known-class, "
            "allow-relaxed-DDM, and non-regulated-grant controls, including bool validation for switch services "
            "and ResignAction validation for automatic resign directive."
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
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports callback control services for connected federates: disableCallbacks "
            "queues local and target federate callbacks, enableCallbacks permits delivery again, evokeCallback "
            "delivers one queued callback, and evokeMultipleCallbacks drains the pending callback queue. The "
            "timing parameters are accepted but not used for wall-clock blocking in this in-process shim slice."
        ),
    },
    {
        "id": "2025-ownership-basic-tag-callbacks",
        "status": "implemented-slice",
        "requirements": (
            "HLA2025-FI-SVC-083",
            "HLA2025-FI-SVC-084",
            "HLA2025-FI-SVC-085",
            "HLA2025-FI-SVC-086",
            "HLA2025-FI-SVC-087",
            "HLA2025-FI-SVC-088",
            "HLA2025-FI-SVC-089",
            "HLA2025-FI-SVC-090",
            "HLA2025-FI-SVC-091",
            "HLA2025-FI-SVC-092",
            "HLA2025-FI-SVC-093",
            "HLA2025-FI-SVC-094",
            "HLA2025-FI-SVC-095",
            "HLA2025-FI-SVC-096",
            "HLA2025-FI-SVC-097",
            "HLA2025-FI-SVC-098",
            "HLA2025-FI-SVC-099",
            "HLA2025-FI-SVC-100",
            "HLA2025-MOD-005",
            "HLA2025-FI-001",
            "HLA2025-FI-005",
        ),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/scenarios/test_ownership_management_backend_matrix.py",
            "tests/backends/test_python_backend_object_ownership_extended.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim supports FOM-backed object instance registration, initial attribute ownership by "
            "the registering federate, unconditional divestiture with ownership validation, acquire-if-available "
            "with 2025 user-supplied tags, negotiated ownership offers, confirmDivestiture transfer, release-denied "
            "pending-acquisition clearing, pending acquisition cancellation, divestiture-if-wanted transfer, "
            "ownership unavailable/acquisition callbacks, ownership query callbacks, "
            "isAttributeOwnedByFederate, requestAttributeOwnershipAssumption, "
            "requestDivestitureConfirmation, requestAttributeOwnershipRelease, "
            "confirmAttributeOwnershipAcquisitionCancellation, and resign-time ownership policies for cancel pending "
            "acquisitions, delete owned objects, and divest/transfer owned attributes."
        ),
    },
    {
        "id": "2025-mom-service-report-serialization",
        "status": "implemented-slice",
        "requirements": ("HLA2025-NEW-007", "HLA2025-REQ-002"),
        "evidence": (
            "tests/test_rti1516_2025_spec_and_shim.py",
            "tests/requirements/test_2025_tail_backlog_evidence.py",
            "packages/hla-backend-shim/src/hla/backends/shim/backend.py",
        ),
        "supported_scope": (
            "Python 2025 shim serializes structured MOM service report records with service names, federate and "
            "federation context, serial numbers, success/exception fields, JSON-safe arguments and returned values, "
            "active service-reporting switches, source-local record snapshots, and service-report callback delivery "
            "to joined federates with service reporting enabled. The Python 2025 shim also routes MIM data, "
            "FOM module data, synchronization point MOM request/report interactions, and service/exception "
            "reporting MOM adjust interactions plus exposed HLAsetSwitches, HLAsetTiming, and "
            "HLAmodifyAttributeState adjust interactions through receiveInteraction callbacks, and routes "
            "federate-level FOM module data, publication/subscription, and object-instance information MOM reports plus "
            "declaration-management MOM service actions through the "
            "normal publish/subscribe service paths plus federation-management MOM service actions through "
            "normal synchronization, save/restore, and resign service paths plus supported time-management MOM "
            "service actions through normal time-regulation, time-constrained, time-advance, flush-queue, and "
            "lookahead service paths, including disable, asynchronous-delivery, TARA, NMR, and NMRA paths, "
            "plus supported object-management and ownership MOM service actions through "
            "normal delete, transportation-change, order-type-change, and ownership-divestiture service paths plus activity/count MOM "
            "reports for updates, reflections, interactions, and deletable/updated/reflected objects. Failed routed MOM "
            "actions emit standard HLAreportMOMexception interactions with service, exception, and parameter-error "
            "fields. The FedPro hosted route also reports standard MIM data for "
            "HLArequestMIMdata, FOM module data for HLArequestFOMmoduleData, and object "
            "publication/subscription state for HLArequestPublications and "
            "HLArequestSubscriptions, object instance information for HLArequestObjectInstanceInformation, "
            "object-instance counts for deletable/updated/reflected objects, plus activity counts for updates, "
            "reflections, interactions sent, and interactions received, plus synchronization point/status reports, "
            "and standard HLAreportMOMexception interactions for failed routed MOM actions. "
            "This is not full MOM manager interaction routing or a conformance claim."
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
)

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

    return {
        "scope": "IEEE 1516-2025 requirements finish-line inventory, not a conformance claim",
        "registry": {
            "initial_tranche_requirements": len(registry_requirements),
            "imported_packets": [packet["id"] for packet in registry.get("imported_packets", ())],
        },
        "completion_backlog": {
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
        },
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
        "requirement_coverage_disposition": {
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
        },
        "implemented_evidence_slices": [dict(slice_) for slice_ in IMPLEMENTED_EVIDENCE_SLICES],
        "verification_matrix": verification_matrix,
        "route_parity_matrix": summarize_spec2025_route_parity(),
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
        "## Implemented Evidence Slices",
        "",
        "| Slice | Status | Requirements | Evidence |",
        "|---|---|---|---|",
    ]
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
