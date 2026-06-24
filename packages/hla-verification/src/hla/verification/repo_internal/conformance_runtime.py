from __future__ import annotations

import importlib

_PYTHON_BACKEND_HANDLER_NAMES: set[str] | None = None

_FOCUSED_EVIDENCE_BY_GROUP: dict[str, tuple[str, ...]] = {
    "Federation Management": (
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py",
        "tests/scenarios/test_federation_management_backend_matrix.py",
    ),
    "Declaration Management": (
        "tests/scenarios/test_object_management_backend_matrix.py",
    ),
    "Object Management": (
        "tests/scenarios/test_object_management_backend_matrix.py",
    ),
    "Ownership Management": (
        "tests/scenarios/test_ownership_management_backend_matrix.py",
    ),
    "Time Management": (
        "tests/time/test_mom_mim_time_v10.py",
        "tests/time/test_mom_mim_and_time_semantics_v010.py",
        "tests/verification/test_compliance_slice_v011.py",
    ),
    "Data Distribution Management": (
        "tests/scenarios/test_ddm_backend_matrix.py",
    ),
    "Support Services": (
        "tests/scenarios/test_support_services_backend_matrix.py",
    ),
    "Programming Language Mappings": (
        "tests/scenarios/test_support_services_backend_matrix.py",
    ),
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

_NEGATIVE_TEST_REF_FALLBACKS: dict[str, tuple[str, ...]] = {
    "Management Object Model": ("tests/verification/test_mom_negative_matrix_executable_v013.py",),
    "Time Management": ("tests/verification/test_compliance_slice_v011.py",),
    "Ownership Management": ("tests/scenarios/test_ownership_management_backend_matrix.py",),
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
    "disableAttributeRelevanceAdvisorySwitch": 5,
    "disableAttributeScopeAdvisorySwitch": 5,
    "disableCallbacks": 2,
    "disableTimeConstrained": 5,
    "disableTimeRegulation": 5,
    "disableInteractionRelevanceAdvisorySwitch": 5,
    "disableObjectClassRelevanceAdvisorySwitch": 5,
    "enableAsynchronousDelivery": 5,
    "enableAttributeRelevanceAdvisorySwitch": 5,
    "enableAttributeScopeAdvisorySwitch": 5,
    "enableCallbacks": 2,
    "enableInteractionRelevanceAdvisorySwitch": 5,
    "enableObjectClassRelevanceAdvisorySwitch": 5,
    "enableTimeConstrained": 7,
    "enableTimeRegulation": 8,
    "evokeCallback": 1,
    "evokeMultipleCallbacks": 1,
    "getAttributeHandle": 4,
    "getAttributeName": 5,
    "getAvailableDimensionsForClassAttribute": 5,
    "getAvailableDimensionsForInteractionClass": 3,
    "getDimensionHandle": 3,
    "getDimensionHandleSet": 5,
    "getDimensionName": 3,
    "getDimensionUpperBound": 3,
    "getFederateHandle": 3,
    "getFederateName": 4,
    "getHLAversion": 1,
    "getInteractionClassHandle": 3,
    "getInteractionClassName": 3,
    "getKnownObjectClassHandle": 3,
    "getObjectClassHandle": 3,
    "getObjectClassName": 3,
    "getObjectInstanceHandle": 3,
    "getObjectInstanceName": 3,
    "getUpdateRateValue": 3,
    "getUpdateRateValueForAttribute": 4,
    "getAutomaticResignDirective": 2,
    "getOrderName": 3,
    "getOrderType": 3,
    "getParameterHandle": 4,
    "getParameterName": 5,
    "getRangeBounds": 6,
    "getTransportationName": 3,
    "getTransportationType": 3,
    "getTransportationTypeHandle": 3,
    "getTransportationTypeName": 3,
    "joinFederationExecution": 8,
    "listFederationExecutions": 1,
    "localDeleteObjectInstance": 2,
    "modifyLookahead": 4,
    "nextMessageRequestAvailable": 1,
    "normalizeFederateHandle": 3,
    "normalizeServiceGroup": 3,
    "publishInteractionClass": 2,
    "publishObjectClassAttributes": 2,
    "queryAttributeOwnership": 2,
    "queryFederationRestoreStatus": 2,
    "queryFederationSaveStatus": 2,
    "queryInteractionTransportationType": 2,
    "queryLITS": 1,
    "queryLogicalTime": 1,
    "registerFederationSynchronizationPoint": 5,
    "registerObjectInstance": 3,
    "registerObjectInstanceWithRegions": 4,
    "releaseMultipleObjectInstanceName": 2,
    "releaseObjectInstanceName": 2,
    "requestAttributeTransportationTypeChange": 3,
    "requestAttributeValueUpdate": 2,
    "requestAttributeValueUpdateWithRegions": 3,
    "requestFederationRestore": 2,
    "requestFederationSave": 2,
    "requestInteractionTransportationTypeChange": 3,
    "reserveMultipleObjectInstanceName": 3,
    "reserveObjectInstanceName": 3,
    "resignFederationExecution": 6,
    "sendInteraction": 2,
    "sendInteractionWithRegions": 1,
    "setAutomaticResignDirective": 3,
    "setRangeBounds": 8,
    "subscribeInteractionClassWithRegions": 4,
    "subscribeObjectClassAttributesWithRegions": 4,
    "synchronizationPointAchieved": 4,
    "timeAdvanceRequest": 1,
    "unsubscribeInteractionClassWithRegions": 2,
    "unsubscribeObjectClassAttributesWithRegions": 2,
    "updateAttributeValues": 2,
    "getAttributeHandleFactory": 2,
    "getAttributeHandleSetFactory": 2,
    "getAttributeHandleValueMapFactory": 2,
    "getAttributeSetRegionSetPairListFactory": 2,
    "getDimensionHandleFactory": 2,
    "getDimensionHandleSetFactory": 2,
    "getFederateHandleFactory": 2,
    "getFederateHandleSetFactory": 2,
    "getInteractionClassHandleFactory": 2,
    "getObjectClassHandleFactory": 2,
    "getObjectInstanceHandleFactory": 2,
    "getParameterHandleFactory": 2,
    "getParameterHandleValueMapFactory": 2,
    "getRegionHandleSetFactory": 2,
    "getTimeFactory": 2,
    "getTransportationTypeHandleFactory": 2,
}


def python_backend_handler_names() -> set[str]:
    global _PYTHON_BACKEND_HANDLER_NAMES
    if _PYTHON_BACKEND_HANDLER_NAMES is not None:
        return _PYTHON_BACKEND_HANDLER_NAMES
    try:
        module = importlib.import_module("hla.backends.python1516e.backend")
    except ModuleNotFoundError:
        _PYTHON_BACKEND_HANDLER_NAMES = set()
        return _PYTHON_BACKEND_HANDLER_NAMES
    backend_cls = getattr(module, "PythonRTIBackend", None)
    if backend_cls is None:
        _PYTHON_BACKEND_HANDLER_NAMES = set()
        return _PYTHON_BACKEND_HANDLER_NAMES
    _PYTHON_BACKEND_HANDLER_NAMES = {
        name for name in dir(backend_cls) if name.startswith("_svc_")
    }
    return _PYTHON_BACKEND_HANDLER_NAMES


def verification_asset_artifact_refs() -> dict[str, tuple[str, ...]]:
    return _VERIFICATION_ASSET_ARTIFACT_REFS


def focused_evidence_by_group() -> dict[str, tuple[str, ...]]:
    return _FOCUSED_EVIDENCE_BY_GROUP


def section_to_verification_asset() -> dict[str, str]:
    return _SECTION_TO_VERIFICATION_ASSET


def service_group_requirement_prefix() -> dict[str, str]:
    return _SERVICE_GROUP_REQUIREMENT_PREFIX


def negative_path_gap() -> str:
    return _NEGATIVE_PATH_GAP


def non_actionable_negative_exceptions() -> frozenset[str]:
    return _NON_ACTIONABLE_NEGATIVE_EXCEPTIONS


def negative_executed_by_method() -> dict[str, int]:
    return _NEGATIVE_EXECUTED_BY_METHOD


def negative_test_ref_fallbacks() -> dict[str, tuple[str, ...]]:
    return _NEGATIVE_TEST_REF_FALLBACKS


__all__ = [
    "focused_evidence_by_group",
    "negative_executed_by_method",
    "negative_path_gap",
    "negative_test_ref_fallbacks",
    "non_actionable_negative_exceptions",
    "python_backend_handler_names",
    "section_to_verification_asset",
    "service_group_requirement_prefix",
    "verification_asset_artifact_refs",
]
