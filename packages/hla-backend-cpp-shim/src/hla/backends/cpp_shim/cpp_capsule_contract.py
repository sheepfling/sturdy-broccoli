"""Stable C++ runtime capsule contract names and smoke semantics."""
from __future__ import annotations

CAPSULE_C_ABI_FUNCTIONS = (
    "shim_capsule_discover_json",
    "shim_capsule_create_json",
    "shim_capsule_invoke_json",
    "shim_capsule_evoke_callbacks_json",
    "shim_capsule_free_string",
    "shim_capsule_close",
)

CAPSULE_V1_METHODS = (
    "connect",
    "disconnect",
    "createFederationExecution",
    "destroyFederationExecution",
    "joinFederationExecution",
    "resignFederationExecution",
    "getObjectClassHandle",
    "getObjectClassName",
    "getAttributeHandle",
    "getAttributeName",
    "getInteractionClassHandle",
    "getInteractionClassName",
    "getParameterHandle",
    "getParameterName",
    "publishObjectClassAttributes",
    "subscribeObjectClassAttributes",
    "publishInteractionClass",
    "subscribeInteractionClass",
    "registerObjectInstance",
    "updateAttributeValues",
    "sendInteraction",
    "registerFederationSynchronizationPoint",
    "synchronizationPointAchieved",
    "enableTimeRegulation",
    "enableTimeConstrained",
    "timeAdvanceRequest",
    "evokeCallback",
    "evokeMultipleCallbacks",
)

UNSUPPORTED_SERVICE_LEDGER = (
    "requestFederationSave",
    "requestFederationRestore",
    "createRegion",
)

SMOKE_TRACE_EVENTS = (
    "capsuleDiscover",
    "createRtiAmbassador",
    "connect",
    "disconnect",
    "unsupportedService",
    "callbackPoll",
    "close",
)


__all__ = [
    "CAPSULE_C_ABI_FUNCTIONS",
    "CAPSULE_V1_METHODS",
    "SMOKE_TRACE_EVENTS",
    "UNSUPPORTED_SERVICE_LEDGER",
]
