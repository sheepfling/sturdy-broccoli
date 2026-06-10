"""Service-by-service conformance matrix generation.

This module does not claim certification.  It creates an auditable engineering
matrix from the source-derived Java/C++ API metadata, the Python backend service
handlers, callback helpers, and the verification artifacts we currently have.

Section anchors: IEEE 1516.1-2010 §4-§12, especially the per-service clauses
listed in :mod:`hla2010.spec_refs`.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ambassadors import RecordingFederateAmbassador
from .backends.base import CALLBACK_METHOD_NAMES, RTI_METHOD_NAMES, lower_camel_to_snake
from .backends.python import PythonRTIBackend
from .raw_api import API_METADATA
from .spec_refs import method_reference
from .mom_negative_testing import build_mom_negative_test_cases
from .mom_negative_testing import default_mom_model, mom_negative_case_report

_FOCUSED_EVIDENCE_BY_GROUP: dict[str, tuple[str, ...]] = {
    "Federation Management": (
        "tests/backends/test_python_backend.py",
        "tests/scenarios/test_startup_sync_fom_java_translation_v09.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "Declaration Management": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/backends/test_python_backend.py",
    ),
    "Object Management": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "Ownership Management": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "Time Management": (
        "tests/time/test_mom_mim_time_v10.py",
        "tests/time/test_mom_mim_and_time_semantics_v010.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "Data Distribution Management": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "Support Services": (
        "tests/factories/test_fom_time_factories.py",
        "tests/verification/test_spec_traceability_all_methods.py",
    ),
    "Programming Language Mappings": (
        "tests/factories/test_fom_time_factories.py",
        "tests/verification/test_spec_traceability_all_methods.py",
    ),
}

_FOCUSED_EVIDENCE_BY_METHOD: dict[str, tuple[str, ...]] = {
    "connect": ("tests/scenarios/test_startup_sync_fom_java_translation_v09.py",),
    "createFederationExecution": ("tests/factories/test_fom_time_factories.py", "tests/scenarios/test_startup_sync_fom_java_translation_v09.py"),
    "createFederationExecutionWithMIM": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "disconnect": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "destroyFederationExecution": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/backends/test_java_shim_backends.py",
    ),
    "listFederationExecutions": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "joinFederationExecution": ("tests/scenarios/test_startup_sync_fom_java_translation_v09.py",),
    "resignFederationExecution": (
        "tests/backends/test_python_backend.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "publishObjectClassAttributes": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "unpublishObjectClass": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "unpublishObjectClassAttributes": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "publishInteractionClass": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "unpublishInteractionClass": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "subscribeObjectClassAttributes": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "subscribeObjectClassAttributesPassively": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "unsubscribeObjectClass": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "unsubscribeObjectClassAttributes": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "subscribeInteractionClass": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "subscribeInteractionClassPassively": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "unsubscribeInteractionClass": ("tests/backends/test_python_backend.py", "tests/scenarios/test_target_radar_scenario.py"),
    "reserveObjectInstanceName": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "releaseObjectInstanceName": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "reserveMultipleObjectInstanceName": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "releaseMultipleObjectInstanceName": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "registerObjectInstance": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "deleteObjectInstance": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "localDeleteObjectInstance": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "requestAttributeTransportationTypeChange": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "queryAttributeTransportationType": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "requestInteractionTransportationTypeChange": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "queryInteractionTransportationType": (
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_compliance_slice_v011.py",
        "tests/time/test_mom_mim_time_v10.py",
    ),
    "registerFederationSynchronizationPoint": (
        "tests/scenarios/test_startup_sync_fom_java_translation_v09.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "synchronizationPointAchieved": (
        "tests/scenarios/test_startup_sync_fom_java_translation_v09.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "federationSynchronized": ("tests/scenarios/test_startup_sync_fom_java_translation_v09.py",),
    "requestFederationSave": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "federateSaveBegun": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "federateSaveComplete": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "federateSaveNotComplete": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "abortFederationSave": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "queryFederationSaveStatus": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "requestFederationRestore": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "federateRestoreComplete": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "federateRestoreNotComplete": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "abortFederationRestore": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "queryFederationRestoreStatus": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "enableTimeRegulation": ("tests/time/test_mom_mim_time_v10.py", "tests/verification/test_compliance_slice_v011.py"),
    "enableTimeConstrained": (
        "tests/time/test_mom_mim_and_time_semantics_v010.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "disableTimeRegulation": ("tests/time/test_mom_mim_and_time_semantics_v010.py",),
    "disableTimeConstrained": ("tests/time/test_mom_mim_and_time_semantics_v010.py",),
    "timeAdvanceRequest": ("tests/time/test_mom_mim_time_v10.py", "tests/verification/test_compliance_slice_v011.py"),
    "timeAdvanceRequestAvailable": ("tests/time/test_mom_mim_time_v10.py",),
    "nextMessageRequest": ("tests/time/test_mom_mim_time_v10.py",),
    "nextMessageRequestAvailable": (
        "tests/time/test_mom_mim_time_v10.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "flushQueueRequest": ("tests/time/test_mom_mim_time_v10.py",),
    "queryGALT": ("tests/time/test_mom_mim_time_v10.py", "tests/verification/test_compliance_slice_v011.py"),
    "queryLogicalTime": (
        "tests/time/test_mom_mim_and_time_semantics_v010.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "queryLITS": ("tests/time/test_mom_mim_time_v10.py", "tests/verification/test_compliance_slice_v011.py"),
    "modifyLookahead": (
        "tests/time/test_mom_mim_and_time_semantics_v010.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "queryLookahead": ("tests/time/test_mom_mim_and_time_semantics_v010.py",),
    "retract": (
        "tests/time/test_mom_mim_time_v10.py",
        "tests/time/test_mom_mim_and_time_semantics_v010.py",
    ),
    "enableAsynchronousDelivery": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "disableAsynchronousDelivery": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "changeAttributeOrderType": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "changeInteractionOrderType": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "sendInteraction": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/scenarios/test_target_radar_scenario.py",
        "tests/verification/test_mom_negative_matrix_v013.py",
    ),
    "updateAttributeValues": ("tests/scenarios/test_target_radar_scenario.py", "tests/verification/test_compliance_slice_v011.py"),
    "requestAttributeValueUpdate": ("tests/scenarios/test_target_radar_scenario.py", "tests/time/test_mom_mim_time_v10.py"),
    "unconditionalAttributeOwnershipDivestiture": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "negotiatedAttributeOwnershipDivestiture": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "confirmDivestiture": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "attributeOwnershipAcquisition": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "attributeOwnershipAcquisitionIfAvailable": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "attributeOwnershipReleaseDenied": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "attributeOwnershipDivestitureIfWanted": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "cancelAttributeOwnershipAcquisition": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "cancelNegotiatedAttributeOwnershipDivestiture": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "queryAttributeOwnership": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "isAttributeOwnedByFederate": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "createRegion": (
        "tests/verification/test_compliance_slice_v011.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "commitRegionModifications": ("tests/verification/test_compliance_slice_v011.py",),
    "deleteRegion": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "registerObjectInstanceWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "associateRegionsForUpdates": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "unassociateRegionsForUpdates": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "subscribeObjectClassAttributesWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "subscribeObjectClassAttributesPassivelyWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "unsubscribeObjectClassAttributesWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "subscribeInteractionClassWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "subscribeInteractionClassPassivelyWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "unsubscribeInteractionClassWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "sendInteractionWithRegions": ("tests/verification/test_compliance_slice_v011.py",),
    "requestAttributeValueUpdateWithRegions": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
    ),
    "getFederateName": (
        "tests/vendors/test_java_profile_backend_matrix.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getFederateHandle": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getObjectClassHandle": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getObjectClassName": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getAttributeHandle": (
        "tests/factories/test_fom_time_factories.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getAttributeName": (
        "tests/factories/test_fom_time_factories.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getInteractionClassHandle": (
        "tests/factories/test_fom_time_factories.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getInteractionClassName": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getParameterHandle": (
        "tests/factories/test_fom_time_factories.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getParameterName": (
        "tests/factories/test_fom_time_factories.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getObjectInstanceHandle": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getObjectInstanceName": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getKnownObjectClassHandle": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getDimensionHandle": (
        "tests/factories/test_fom_time_factories.py",
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getDimensionName": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getTransportationTypeHandle": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getTransportationTypeName": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "getHLAversion": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getDimensionHandleSet": (
        "tests/factories/test_fom_time_factories.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getOrderName": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getOrderType": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getTransportationType": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "getTransportationName": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getAvailableDimensionsForClassAttribute": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getAvailableDimensionsForInteractionClass": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "getUpdateRateValue": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "getUpdateRateValueForAttribute": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "normalizeFederateHandle": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "normalizeServiceGroup": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "getAttributeSetRegionSetPairListFactory": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getAutomaticResignDirective": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "setAutomaticResignDirective": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "enableObjectClassRelevanceAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "disableObjectClassRelevanceAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "enableAttributeRelevanceAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "disableAttributeRelevanceAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "enableAttributeScopeAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "disableAttributeScopeAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "enableInteractionRelevanceAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "disableInteractionRelevanceAdvisorySwitch": ("tests/verification/test_spec_traceability_and_extended_python_rti.py",),
    "enableCallbacks": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "disableCallbacks": (
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "evokeCallback": (
        "tests/transport/test_rest_transport.py",
        "tests/transport/test_grpc_transport_python_server.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "evokeMultipleCallbacks": (
        "tests/transport/test_rest_transport.py",
        "tests/transport/test_grpc_transport_python_server.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getRangeBounds": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "setRangeBounds": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getDimensionUpperBound": (
        "tests/verification/test_spec_traceability_and_extended_python_rti.py",
        "tests/backends/test_python_backend_support_services.py",
        "tests/backends/test_python_backend_federation_extended.py",
        "tests/backends/test_python_backend_object_ownership_extended.py",
        "tests/backends/test_python_backend_time_ddm_extended.py",
    ),
    "getTimeFactory": ("tests/factories/test_fom_time_factories.py",),
    "getAttributeHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getAttributeHandleSetFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getAttributeHandleValueMapFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getDimensionHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getDimensionHandleSetFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getFederateHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getFederateHandleSetFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getInteractionClassHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getObjectClassHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getObjectInstanceHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getParameterHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getParameterHandleValueMapFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getRegionHandleSetFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "getTransportationTypeHandleFactory": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeAttributeHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeDimensionHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeFederateHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeInteractionClassHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeMessageRetractionHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeObjectClassHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeObjectInstanceHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeParameterHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
    "decodeRegionHandle": ("tests/verification/test_spec_traceability_all_methods.py",),
}

_SECTION_TO_VERIFICATION_ASSET: dict[str, str] = {
    "4": "ASSET-FEDERATION-MGMT-STARTUP-SYNC",
    "5": "ASSET-DECLARATION-MGMT-SMOKE",
    "6": "ASSET-OBJECT-MGMT-TARGET-RADAR",
    "7": "ASSET-OWNERSHIP-MGMT-REFERENCE-SUBSET",
    "8": "ASSET-TIME-MGMT-ORDERING",
    "9": "ASSET-DDM-REGION-TIME-FILTERING",
    "10": "ASSET-SUPPORT-SERVICES-HANDLE-FACTORIES",
    "11": "ASSET-MOM-MIM-MATRIX",
    "12": "ASSET-LANGUAGE-BINDING-HANDLE-ENCODING",
}

_NEGATIVE_PATH_GAP = "Declared exception matrix is identified from source metadata; exhaustive negative execution remains incomplete."
_NON_ACTIONABLE_NEGATIVE_EXCEPTIONS = frozenset({"RTIinternalError", "FederateInternalError"})

_NEGATIVE_EXECUTED_BY_METHOD: dict[str, int] = {
    "abortFederationSave": 1,
    "abortFederationRestore": 1,
    "connect": 1,
    "createFederationExecution": 9,
    "createFederationExecutionWithMIM": 9,
    "destroyFederationExecution": 1,
    "disconnect": 1,
    "attributeOwnershipAcquisition": 9,
    "attributeOwnershipAcquisitionIfAvailable": 10,
    "attributeOwnershipDivestitureIfWanted": 7,
    "attributeOwnershipReleaseDenied": 7,
    "associateRegionsForUpdates": 6,
    "cancelAttributeOwnershipAcquisition": 8,
    "cancelNegotiatedAttributeOwnershipDivestiture": 8,
    "changeAttributeOrderType": 7,
    "commitRegionModifications": 4,
    "createRegion": 4,
    "confirmDivestiture": 9,
    "deleteObjectInstance": 6,
    "disableAsynchronousDelivery": 5,
    "disableCallbacks": 2,
    "disableTimeConstrained": 5,
    "disableTimeRegulation": 5,
    "disableInteractionRelevanceAdvisorySwitch": 5,
    "enableAsynchronousDelivery": 5,
    "enableCallbacks": 2,
    "enableInteractionRelevanceAdvisorySwitch": 5,
    "enableTimeConstrained": 7,
    "enableTimeRegulation": 8,
    "evokeCallback": 1,
    "evokeMultipleCallbacks": 1,
    "getAttributeHandle": 4,
    "getAttributeHandleFactory": 2,
    "getAttributeHandleSetFactory": 2,
    "getAttributeHandleValueMapFactory": 2,
    "federateRestoreComplete": 3,
    "federateRestoreNotComplete": 3,
    "federateSaveBegun": 3,
    "federateSaveComplete": 3,
    "federateSaveNotComplete": 3,
    "flushQueueRequest": 9,
    "getAutomaticResignDirective": 2,
    "getAttributeName": 4,
    "getAvailableDimensionsForInteractionClass": 3,
    "getAvailableDimensionsForClassAttribute": 4,
    "getDimensionHandle": 3,
    "getDimensionHandleFactory": 2,
    "getDimensionHandleSetFactory": 2,
    "getDimensionHandleSet": 5,
    "getDimensionName": 3,
    "getDimensionUpperBound": 3,
    "getFederateHandle": 3,
    "getFederateHandleFactory": 2,
    "getFederateHandleSetFactory": 2,
    "getFederateName": 4,
    "getInteractionClassHandle": 3,
    "getInteractionClassHandleFactory": 2,
    "getInteractionClassName": 3,
    "getKnownObjectClassHandle": 3,
    "getObjectClassHandle": 3,
    "getObjectClassHandleFactory": 2,
    "getObjectClassName": 3,
    "getObjectInstanceHandle": 3,
    "getObjectInstanceHandleFactory": 2,
    "getObjectInstanceName": 3,
    "getOrderName": 3,
    "getOrderType": 3,
    "getParameterName": 4,
    "getParameterHandle": 4,
    "getParameterHandleFactory": 2,
    "getParameterHandleValueMapFactory": 2,
    "getRangeBounds": 6,
    "getRegionHandleSetFactory": 2,
    "getTimeFactory": 2,
    "getTransportationName": 3,
    "getTransportationType": 3,
    "getTransportationTypeHandle": 3,
    "getTransportationTypeHandleFactory": 2,
    "getTransportationTypeName": 3,
    "getUpdateRateValue": 3,
    "getUpdateRateValueForAttribute": 4,
    "joinFederationExecution": 11,
    "listFederationExecutions": 1,
    "localDeleteObjectInstance": 6,
    "modifyLookahead": 7,
    "normalizeFederateHandle": 3,
    "normalizeServiceGroup": 3,
    "nextMessageRequest": 9,
    "nextMessageRequestAvailable": 9,
    "negotiatedAttributeOwnershipDivestiture": 8,
    "enableAttributeRelevanceAdvisorySwitch": 5,
    "enableAttributeScopeAdvisorySwitch": 5,
    "enableObjectClassRelevanceAdvisorySwitch": 5,
    "publishObjectClassAttributes": 4,
    "publishInteractionClass": 4,
    "queryGALT": 4,
    "queryFederationRestoreStatus": 2,
    "queryFederationSaveStatus": 2,
    "queryAttributeOwnership": 6,
    "queryAttributeTransportationType": 4,
    "queryInteractionTransportationType": 4,
    "queryLogicalTime": 4,
    "queryLookahead": 5,
    "queryLITS": 4,
    "registerFederationSynchronizationPoint": 4,
    "registerObjectInstanceWithRegions": 7,
    "registerObjectInstance": 6,
    "releaseMultipleObjectInstanceName": 4,
    "releaseObjectInstanceName": 4,
    "reserveObjectInstanceName": 4,
    "reserveMultipleObjectInstanceName": 4,
    "requestAttributeTransportationTypeChange": 3,
    "requestAttributeValueUpdate": 4,
    "requestAttributeValueUpdateWithRegions": 8,
    "requestFederationRestore": 4,
    "requestFederationSave": 4,
    "requestInteractionTransportationTypeChange": 6,
    "retract": 7,
    "resignFederationExecution": 6,
    "sendInteraction": 4,
    "sendInteractionWithRegions": 9,
    "setRangeBounds": 7,
    "setAutomaticResignDirective": 3,
    "getAttributeSetRegionSetPairListFactory": 2,
    "subscribeInteractionClassPassivelyWithRegions": 6,
    "subscribeInteractionClassWithRegions": 6,
    "subscribeObjectClassAttributes": 4,
    "subscribeObjectClassAttributesPassively": 4,
    "subscribeObjectClassAttributesPassivelyWithRegions": 8,
    "subscribeObjectClassAttributesWithRegions": 8,
    "synchronizationPointAchieved": 5,
    "timeAdvanceRequest": 9,
    "timeAdvanceRequestAvailable": 9,
    "unassociateRegionsForUpdates": 6,
    "unconditionalAttributeOwnershipDivestiture": 7,
    "unpublishInteractionClass": 4,
    "unpublishObjectClass": 4,
    "unpublishObjectClassAttributes": 4,
    "disableAttributeRelevanceAdvisorySwitch": 5,
    "disableAttributeScopeAdvisorySwitch": 5,
    "disableObjectClassRelevanceAdvisorySwitch": 5,
    "unsubscribeInteractionClass": 4,
    "unsubscribeInteractionClassWithRegions": 5,
    "unsubscribeObjectClass": 4,
    "deleteRegion": 5,
    "unsubscribeObjectClassAttributes": 4,
    "unsubscribeObjectClassAttributesWithRegions": 5,
    "updateAttributeValues": 8,
    "subscribeInteractionClass": 4,
    "subscribeInteractionClassPassively": 4,
    "isAttributeOwnedByFederate": 6,
    "changeInteractionOrderType": 6,
}


@dataclass(frozen=True)
class ServiceConformanceRow:
    requirement_id: str
    interface: str
    method_name: str
    python_name: str
    document: str
    section: str
    section_ref: str
    title: str
    service_group: str
    source_languages: tuple[str, ...]
    source_overload_count: int
    declared_exceptions: tuple[str, ...]
    python_entry_point: str
    implementation_status: str
    verification_status: str
    implementation_refs: tuple[str, ...] = field(default_factory=tuple)
    positive_test_refs: tuple[str, ...] = field(default_factory=tuple)
    negative_test_refs: tuple[str, ...] = field(default_factory=tuple)
    artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    negative_expectation_count: int = 0
    negative_executed_count: int = 0
    verification_asset_id: str = ""
    known_gaps: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ServiceConformanceMatrix:
    version: str
    rows: tuple[ServiceConformanceRow, ...]
    mom_negative_summary: Mapping[str, Any]

    def summary(self) -> dict[str, Any]:
        by_interface: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_verification: dict[str, int] = {}
        by_group: dict[str, int] = {}
        gap_rows = 0
        for row in self.rows:
            by_interface[row.interface] = by_interface.get(row.interface, 0) + 1
            by_status[row.implementation_status] = by_status.get(row.implementation_status, 0) + 1
            by_verification[row.verification_status] = by_verification.get(row.verification_status, 0) + 1
            by_group[row.service_group] = by_group.get(row.service_group, 0) + 1
            if row.known_gaps:
                gap_rows += 1
        return {
            "version": self.version,
            "row_count": len(self.rows),
            "by_interface": dict(sorted(by_interface.items())),
            "by_implementation_status": dict(sorted(by_status.items())),
            "by_verification_status": dict(sorted(by_verification.items())),
            "by_service_group": dict(sorted(by_group.items())),
            "rows_with_known_gaps": gap_rows,
            "mom_negative_summary": dict(self.mom_negative_summary),
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(
            {
                "summary": self.summary(),
                "rows": [row.as_dict() for row in self.rows],
            },
            indent=indent,
            sort_keys=True,
        )


@dataclass(frozen=True)
class RequirementLedgerRow:
    requirement_id: str
    interface: str
    method_name: str
    python_name: str
    document: str
    section: str
    section_ref: str
    title: str
    service_group: str
    outcome: str
    implementation_status: str
    verification_status: str
    implementation_refs: tuple[str, ...] = field(default_factory=tuple)
    positive_test_refs: tuple[str, ...] = field(default_factory=tuple)
    negative_test_refs: tuple[str, ...] = field(default_factory=tuple)
    artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    known_gaps: tuple[str, ...] = field(default_factory=tuple)
    verification_asset_id: str = ""
    rationale: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequirementLedger:
    version: str
    rows: tuple[RequirementLedgerRow, ...]

    def summary(self) -> dict[str, Any]:
        by_outcome: dict[str, int] = {}
        by_interface: dict[str, int] = {}
        by_section: dict[str, dict[str, int]] = {}
        for row in self.rows:
            by_outcome[row.outcome] = by_outcome.get(row.outcome, 0) + 1
            by_interface[row.interface] = by_interface.get(row.interface, 0) + 1
            section_bucket = by_section.setdefault(row.section_ref, {})
            section_bucket[row.outcome] = section_bucket.get(row.outcome, 0) + 1
        return {
            "version": self.version,
            "row_count": len(self.rows),
            "outcome_counts": dict(sorted(by_outcome.items())),
            "interface_counts": dict(sorted(by_interface.items())),
            "section_outcomes": {key: dict(sorted(value.items())) for key, value in sorted(by_section.items())},
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(
            {
                "summary": self.summary(),
                "rows": [row.as_dict() for row in self.rows],
            },
            indent=indent,
            sort_keys=True,
        )


def _metadata_for(interface: str, method: str) -> tuple[Mapping[str, Any], ...]:
    return tuple(API_METADATA.get(interface, {}).get(method, ()))


def _source_languages(overloads: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(sorted({str(item.get("language")) for item in overloads if item.get("language")}))


def _declared_exceptions(overloads: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    exceptions: set[str] = set()
    for item in overloads:
        exceptions.update(str(exc) for exc in item.get("throws", ()) if exc)
    return tuple(sorted(exceptions))


def _section_asset_id(section: str) -> str:
    root = str(section).split(".", 1)[0]
    return _SECTION_TO_VERIFICATION_ASSET.get(root, "ASSET-UNMAPPED")


_SERVICE_GROUP_REQUIREMENT_PREFIX = {
    "Data Distribution Management": "DDM",
    "Declaration Management": "DM",
    "Federate Ambassador Callback": "FA",
    "Federation Management": "FM",
    "Management Object Model": "MOM",
    "Object Management": "OM",
    "Ownership Management": "OWN",
    "Programming Language Mappings": "PLM",
    "Support Services": "SS",
    "Time Management": "TM",
    "Unmapped": "UNMAPPED",
}

_VERIFICATION_ASSET_ARTIFACT_REFS: dict[str, tuple[str, ...]] = {
    "ASSET-SECTION4": ("analysis/compliance/section4_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION5": ("analysis/compliance/section5_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION6": ("analysis/compliance/section6_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION7": ("analysis/compliance/section7_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION8": ("analysis/compliance/section8_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION9": ("analysis/compliance/section9_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION10": ("analysis/compliance/section10_backend_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION11": ("analysis/compliance/section11_mom_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-SECTION12": ("analysis/compliance/section12_language_matrix.json", "analysis/compliance/service_conformance.json"),
    "ASSET-UNMAPPED": ("analysis/compliance/service_conformance.json",),
}


def _normalize_requirement_section(section: str) -> str:
    token = str(section).strip() or "unmapped"
    return token.replace("§", "").replace(".", "_").replace(" ", "_").replace("-", "_").replace("/", "_")


def _requirement_prefix(interface: str, service_group: str) -> str:
    interface_token = "RTI" if interface == "RTIambassador" else "FED"
    group_token = _SERVICE_GROUP_REQUIREMENT_PREFIX.get(service_group, "GEN")
    return f"{interface_token}-{group_token}"


def requirement_id_for_row(row: ServiceConformanceRow) -> str:
    return (
        f"REQ-{_requirement_prefix(row.interface, row.service_group)}-"
        f"{_normalize_requirement_section(row.section)}-{row.method_name}"
    )


def _evidence_for(method: str, service_group: str) -> tuple[str, ...]:
    evidence = list(_FOCUSED_EVIDENCE_BY_GROUP.get(service_group, ()))
    evidence.extend(_FOCUSED_EVIDENCE_BY_METHOD.get(method, ()))
    return tuple(dict.fromkeys(evidence))


def _implementation_refs(row: ServiceConformanceRow) -> tuple[str, ...]:
    refs = [row.python_entry_point]
    if row.interface == "RTIambassador":
        refs.append("hla2010/backends/python/backend.py")
    elif row.interface == "FederateAmbassador":
        refs.append("hla2010/ambassadors.py")
    return tuple(dict.fromkeys(refs))


def _positive_test_refs(evidence: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(item for item in evidence if item.startswith("tests/"))


def _negative_test_refs(
    method: str,
    service_group: str,
    evidence: tuple[str, ...],
    negative_executed_count: int,
) -> tuple[str, ...]:
    if negative_executed_count <= 0:
        return ()
    explicit = [item for item in evidence if item.startswith("tests/") and "negative" in item.lower()]
    if explicit:
        return tuple(dict.fromkeys(explicit))
    fallback_by_group = {
        "Management Object Model": ("tests/verification/test_mom_negative_matrix_executable_v013.py",),
        "Time Management": ("tests/verification/test_compliance_slice_v011.py",),
        "Ownership Management": ("tests/backends/test_python_backend_object_ownership_extended.py",),
    }
    fallback = fallback_by_group.get(service_group, ())
    if fallback:
        return fallback
    return tuple(item for item in evidence if item.startswith("tests/"))


def _artifact_refs(verification_asset_id: str, positive_test_refs: tuple[str, ...], negative_test_refs: tuple[str, ...]) -> tuple[str, ...]:
    refs = list(_VERIFICATION_ASSET_ARTIFACT_REFS.get(verification_asset_id, ("analysis/compliance/service_conformance.json",)))
    refs.extend(
        item
        for item in positive_test_refs + negative_test_refs
        if item.startswith("analysis/") or item.startswith("verification/")
    )
    return tuple(dict.fromkeys(refs))


def _verification_status(method: str, service_group: str, evidence: tuple[str, ...]) -> str:
    if method in _FOCUSED_EVIDENCE_BY_METHOD:
        return "focused-executable-tests"
    if evidence:
        return "group-level-slice-tests"
    if service_group == "Federate Ambassador Callback":
        return "callback-helper-covered"
    return "matrix-only-planned"


def _functional_known_gaps(row: ServiceConformanceRow) -> tuple[str, ...]:
    return tuple(gap for gap in row.known_gaps if gap != _NEGATIVE_PATH_GAP)


def actionable_negative_expectation_count(row: ServiceConformanceRow) -> int:
    return sum(1 for exc in row.declared_exceptions if exc not in _NON_ACTIONABLE_NEGATIVE_EXCEPTIONS)


def _negative_path_rationale(row: ServiceConformanceRow) -> str:
    expectation_count = actionable_negative_expectation_count(row)
    if expectation_count == 0:
        return "No declared RTI exception matrix is present for this row."
    if row.negative_executed_count >= expectation_count:
        if any(exc in _NON_ACTIONABLE_NEGATIVE_EXCEPTIONS for exc in row.declared_exceptions):
            return (
                "All actionable negative-path expectations are represented by executable evidence; "
                "generic internal-failure declarations remain excluded from completeness scoring."
            )
        return "Declared negative-path expectations are fully represented by executable evidence."
    if row.negative_executed_count > 0:
        return "Some declared negative-path expectations are covered by executable tests, but coverage is not yet exhaustive."
    if _NEGATIVE_PATH_GAP in row.known_gaps:
        return "Declared exceptions are mapped from source metadata, but exhaustive negative-path execution is still incomplete."
    return "Some negative-path evidence exists, but completeness has not been explicitly recorded."


def negative_path_status(row: ServiceConformanceRow) -> str:
    expectation_count = actionable_negative_expectation_count(row)
    if expectation_count == 0:
        return "not-applicable"
    if row.negative_executed_count >= expectation_count:
        return "complete"
    if row.negative_executed_count > 0:
        return "partial"
    if _NEGATIVE_PATH_GAP in row.known_gaps:
        return "mapped-not-exhaustive"
    return "not-evidenced"


def _requirement_outcome(row: ServiceConformanceRow) -> tuple[str, str]:
    if row.implementation_status in {"adapter-or-gap", "callback-helper-gap"}:
        return "fail", "No backend-neutral implementation surface is present for this requirement."
    if row.verification_status == "matrix-only-planned":
        return "not-evidenced", "The requirement is mapped, but no executable evidence is linked yet."
    if _functional_known_gaps(row):
        return "partial", "Executable evidence exists, but known functional gaps remain for this requirement."
    if row.verification_status in {"focused-executable-tests", "callback-helper-covered"}:
        if _NEGATIVE_PATH_GAP in row.known_gaps:
            return "pass", "Executable positive-path evidence exists at the requirement level; negative-path completeness is tracked separately."
        return "pass", "Executable evidence exists at the requirement level with no recorded functional gap for this row."
    return "partial", "Only group-level or slice-level evidence exists for this requirement."


def build_service_conformance_matrix(*, version: str = "0.13.0") -> ServiceConformanceMatrix:
    """Build the current service-by-service conformance matrix."""

    mom_model = default_mom_model()
    mom_cases = build_mom_negative_test_cases(mom_model)
    mom_executable_count = sum(1 for case in mom_cases if case.execution_level == "rti-strict")
    rows: list[ServiceConformanceRow] = []

    for method in RTI_METHOD_NAMES:
        overloads = _metadata_for("RTIambassador", method)
        ref = method_reference(method)
        section = ref.section if ref else ""
        group = ref.service_group if ref and ref.service_group else "Unmapped"
        evidence = _evidence_for(method, group)
        handler = f"_svc_{method}"
        has_handler = hasattr(PythonRTIBackend, handler)
        gaps: list[str] = []
        if not has_handler:
            gaps.append("No pure-Python service handler is visible; calls may be adapter-only or unsupported.")
        if overloads and _declared_exceptions(overloads):
            gaps.append("Declared exception matrix is identified from source metadata; exhaustive negative execution remains incomplete.")
        negative_executed_count = _NEGATIVE_EXECUTED_BY_METHOD.get(method, mom_executable_count if method == "sendInteraction" else 0)
        asset_id = _section_asset_id(section)
        seed_row = ServiceConformanceRow(
            requirement_id="",
            interface="RTIambassador",
            method_name=method,
            python_name=lower_camel_to_snake(method),
            document=ref.document if ref else "IEEE 1516.1-2010",
            section=section,
            section_ref=f"IEEE 1516.1-2010 §{section}" if section else "unmapped",
            title=ref.title if ref else method,
            service_group=group,
            source_languages=_source_languages(overloads),
            source_overload_count=len(overloads),
            declared_exceptions=_declared_exceptions(overloads),
            python_entry_point=f"PythonRTIBackend.{handler}" if has_handler else "DelegatingRTIAmbassador/backend adapter",
            implementation_status="pure-python-reference-handler" if has_handler else "adapter-or-gap",
            verification_status=_verification_status(method, group, evidence),
            evidence=evidence,
            negative_expectation_count=len(_declared_exceptions(overloads)),
            negative_executed_count=negative_executed_count,
            verification_asset_id=asset_id,
            known_gaps=tuple(gaps),
        )
        requirement_id = requirement_id_for_row(seed_row)
        implementation_refs = _implementation_refs(seed_row)
        positive_test_refs = _positive_test_refs(evidence)
        negative_test_refs = _negative_test_refs(method, group, evidence, negative_executed_count)
        artifact_refs = _artifact_refs(asset_id, positive_test_refs, negative_test_refs)
        rows.append(
            ServiceConformanceRow(
                requirement_id=requirement_id,
                interface=seed_row.interface,
                method_name=seed_row.method_name,
                python_name=seed_row.python_name,
                document=seed_row.document,
                section=seed_row.section,
                section_ref=seed_row.section_ref,
                title=seed_row.title,
                service_group=seed_row.service_group,
                source_languages=seed_row.source_languages,
                source_overload_count=seed_row.source_overload_count,
                declared_exceptions=seed_row.declared_exceptions,
                python_entry_point=seed_row.python_entry_point,
                implementation_status=seed_row.implementation_status,
                verification_status=seed_row.verification_status,
                implementation_refs=implementation_refs,
                positive_test_refs=positive_test_refs,
                negative_test_refs=negative_test_refs,
                artifact_refs=artifact_refs,
                evidence=evidence,
                negative_expectation_count=seed_row.negative_expectation_count,
                negative_executed_count=seed_row.negative_executed_count,
                verification_asset_id=seed_row.verification_asset_id,
                known_gaps=seed_row.known_gaps,
            )
        )

    for method in CALLBACK_METHOD_NAMES:
        overloads = _metadata_for("FederateAmbassador", method)
        ref = method_reference(method)
        section = ref.section if ref else ""
        group = ref.service_group if ref and ref.service_group else "Federate Ambassador Callback"
        has_helper = hasattr(RecordingFederateAmbassador, method) and hasattr(RecordingFederateAmbassador, lower_camel_to_snake(method))
        evidence = ("hla2010/ambassadors.py::RecordingFederateAmbassador", "tests/verification/test_spec_traceability_and_extended_python_rti.py")
        asset_id = _section_asset_id(section)
        seed_row = ServiceConformanceRow(
            requirement_id="",
            interface="FederateAmbassador",
            method_name=method,
            python_name=lower_camel_to_snake(method),
            document=ref.document if ref else "IEEE 1516.1-2010",
            section=section,
            section_ref=f"IEEE 1516.1-2010 §{section}" if section else "unmapped",
            title=ref.title if ref else method,
            service_group=group,
            source_languages=_source_languages(overloads),
            source_overload_count=len(overloads),
            declared_exceptions=_declared_exceptions(overloads),
            python_entry_point="RecordingFederateAmbassador callback + snake_case alias" if has_helper else "callback helper missing",
            implementation_status="callback-helper" if has_helper else "callback-helper-gap",
            verification_status="callback-helper-covered" if has_helper else "matrix-only-planned",
            evidence=evidence if has_helper else (),
            negative_expectation_count=0,
            negative_executed_count=0,
            verification_asset_id=asset_id,
            known_gaps=() if has_helper else ("No callback helper method found.",),
        )
        requirement_id = requirement_id_for_row(seed_row)
        implementation_refs = _implementation_refs(seed_row)
        positive_test_refs = _positive_test_refs(seed_row.evidence)
        negative_test_refs = ()
        artifact_refs = _artifact_refs(asset_id, positive_test_refs, negative_test_refs)
        rows.append(
            ServiceConformanceRow(
                requirement_id=requirement_id,
                interface=seed_row.interface,
                method_name=seed_row.method_name,
                python_name=seed_row.python_name,
                document=seed_row.document,
                section=seed_row.section,
                section_ref=seed_row.section_ref,
                title=seed_row.title,
                service_group=seed_row.service_group,
                source_languages=seed_row.source_languages,
                source_overload_count=seed_row.source_overload_count,
                declared_exceptions=seed_row.declared_exceptions,
                python_entry_point=seed_row.python_entry_point,
                implementation_status=seed_row.implementation_status,
                verification_status=seed_row.verification_status,
                implementation_refs=implementation_refs,
                positive_test_refs=positive_test_refs,
                negative_test_refs=negative_test_refs,
                artifact_refs=artifact_refs,
                evidence=seed_row.evidence,
                negative_expectation_count=seed_row.negative_expectation_count,
                negative_executed_count=seed_row.negative_executed_count,
                verification_asset_id=seed_row.verification_asset_id,
                known_gaps=seed_row.known_gaps,
            )
        )

    return ServiceConformanceMatrix(
        version=version,
        rows=tuple(sorted(rows, key=lambda row: (row.interface, row.service_group, row.section, row.method_name))),
        mom_negative_summary=mom_negative_case_report(mom_model),
    )


def build_requirements_ledger(*, version: str = "0.13.0") -> RequirementLedger:
    matrix = build_service_conformance_matrix(version=version)
    rows: list[RequirementLedgerRow] = []
    for row in matrix.rows:
        outcome, rationale = _requirement_outcome(row)
        rows.append(
            RequirementLedgerRow(
                requirement_id=requirement_id_for_row(row),
                interface=row.interface,
                method_name=row.method_name,
                python_name=row.python_name,
                document=row.document,
                section=row.section,
                section_ref=row.section_ref,
                title=row.title,
                service_group=row.service_group,
                outcome=outcome,
                implementation_status=row.implementation_status,
                verification_status=row.verification_status,
                implementation_refs=row.implementation_refs,
                positive_test_refs=row.positive_test_refs,
                negative_test_refs=row.negative_test_refs,
                artifact_refs=row.artifact_refs,
                evidence=row.evidence,
                known_gaps=row.known_gaps,
                verification_asset_id=row.verification_asset_id,
                rationale=rationale,
            )
        )
    return RequirementLedger(version=version, rows=tuple(rows))


def write_service_conformance_json(path: str | Path, *, version: str = "0.13.0") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_service_conformance_matrix(version=version).to_json(indent=2) + "\n", encoding="utf-8")
    return target


def write_service_conformance_csv(path: str | Path, *, version: str = "0.13.0") -> Path:
    matrix = build_service_conformance_matrix(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ServiceConformanceRow.__dataclass_fields__.keys())
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in matrix.rows:
            record = row.as_dict()
            for key, value in list(record.items()):
                if isinstance(value, tuple):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


def write_requirements_ledger_json(path: str | Path, *, version: str = "0.13.0") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_requirements_ledger(version=version).to_json(indent=2) + "\n", encoding="utf-8")
    return target


def write_requirements_ledger_csv(path: str | Path, *, version: str = "0.13.0") -> Path:
    ledger = build_requirements_ledger(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(RequirementLedgerRow.__dataclass_fields__.keys())
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in ledger.rows:
            record = row.as_dict()
            for key, value in list(record.items()):
                if isinstance(value, tuple):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


__all__ = [
    "RequirementLedger",
    "RequirementLedgerRow",
    "ServiceConformanceMatrix",
    "ServiceConformanceRow",
    "build_requirements_ledger",
    "build_service_conformance_matrix",
    "negative_path_status",
    "actionable_negative_expectation_count",
    "write_requirements_ledger_csv",
    "write_requirements_ledger_json",
    "write_service_conformance_csv",
    "write_service_conformance_json",
]
