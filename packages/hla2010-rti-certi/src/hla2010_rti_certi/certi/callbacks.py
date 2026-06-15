"""Callback decoding for CERTI helper transport events."""
from __future__ import annotations

from typing import Any

from hla2010.enums import (
    RestoreFailureReason,
    RestoreStatus,
    SaveFailureReason,
    SaveStatus,
    SynchronizationPointFailureReason,
)
from hla2010.exceptions import RTIinternalError
from hla2010.ambassadors import invoke_federate_callback
from hla2010.handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    FederateHandle,
    FederateHandleSet,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    ParameterHandleValueMap,
    TransportationTypeHandle,
)
from .codecs import (
    decode_bytes,
    decode_handle_set,
    decode_handle_value_map,
    decode_order,
)
from .runtime import decode_logical_time
from hla2010.types import FederateHandleSaveStatusPair, FederateRestoreStatus


def dispatch_helper_callback(ambassador: Any, parts: list[str], *, logical_time_hint: str | None = None) -> None:
    if ambassador is None or not parts:
        return

    kind = parts[0]
    if kind == "DISCOVER":
        invoke_federate_callback(
            ambassador,
            "discoverObjectInstance",
            ObjectInstanceHandle(int(parts[1])),
            ObjectClassHandle(int(parts[2])),
            parts[3],
        )
        return
    if kind == "REFLECT":
        invoke_federate_callback(
            ambassador,
            "reflectAttributeValues",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
        )
        return
    if kind == "REFLECT_TSO":
        time_type = logical_time_hint or parts[6]
        invoke_federate_callback(
            ambassador,
            "reflectAttributeValues",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
            decode_logical_time(time_type, parts[7]),
            decode_order(parts[8]),
        )
        return
    if kind == "INTERACTION":
        invoke_federate_callback(
            ambassador,
            "receiveInteraction",
            InteractionClassHandle(int(parts[1])),
            decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
        )
        return
    if kind == "INTERACTION_TSO":
        time_type = logical_time_hint or parts[6]
        invoke_federate_callback(
            ambassador,
            "receiveInteraction",
            InteractionClassHandle(int(parts[1])),
            decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
            decode_logical_time(time_type, parts[7]),
            decode_order(parts[8]),
        )
        return
    if kind == "TIME_REGULATION_ENABLED":
        time_type = logical_time_hint or parts[1]
        invoke_federate_callback(
            ambassador,
            "timeRegulationEnabled",
            decode_logical_time(time_type, parts[2]),
        )
        return
    if kind == "TIME_CONSTRAINED_ENABLED":
        time_type = logical_time_hint or parts[1]
        invoke_federate_callback(
            ambassador,
            "timeConstrainedEnabled",
            decode_logical_time(time_type, parts[2]),
        )
        return
    if kind == "TIME_ADVANCE_GRANT":
        time_type = logical_time_hint or parts[1]
        invoke_federate_callback(
            ambassador,
            "timeAdvanceGrant",
            decode_logical_time(time_type, parts[2]),
        )
        return
    if kind == "PROVIDE_ATTRIBUTE_VALUE_UPDATE":
        invoke_federate_callback(
            ambassador,
            "provideAttributeValueUpdate",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_RETRACTION":
        invoke_federate_callback(ambassador, "requestRetraction", MessageRetractionHandle(int(parts[1])))
        return
    if kind == "START_REGISTRATION_FOR_OBJECT_CLASS":
        invoke_federate_callback(
            ambassador,
            "startRegistrationForObjectClass",
            ObjectClassHandle(int(parts[1])),
        )
        return
    if kind == "STOP_REGISTRATION_FOR_OBJECT_CLASS":
        invoke_federate_callback(
            ambassador,
            "stopRegistrationForObjectClass",
            ObjectClassHandle(int(parts[1])),
        )
        return
    if kind == "TURN_INTERACTIONS_ON":
        invoke_federate_callback(
            ambassador,
            "turnInteractionsOn",
            InteractionClassHandle(int(parts[1])),
        )
        return
    if kind == "TURN_INTERACTIONS_OFF":
        invoke_federate_callback(
            ambassador,
            "turnInteractionsOff",
            InteractionClassHandle(int(parts[1])),
        )
        return
    if kind == "REMOVE_OBJECT_INSTANCE":
        if len(parts) >= 5:
            invoke_federate_callback(
                ambassador,
                "removeObjectInstance",
                ObjectInstanceHandle(int(parts[1])),
                decode_bytes(parts[2]),
                decode_order(parts[3]),
                TransportationTypeHandle(int(parts[4])),
            )
            return
        invoke_federate_callback(
            ambassador,
            "removeObjectInstance",
            ObjectInstanceHandle(int(parts[1])),
            decode_bytes(parts[2]),
        )
        return
    if kind == "SYNC_POINT_REGISTRATION_SUCCEEDED":
        invoke_federate_callback(ambassador, "synchronizationPointRegistrationSucceeded", parts[1])
        return
    if kind == "SYNC_POINT_REGISTRATION_FAILED":
        invoke_federate_callback(
            ambassador,
            "synchronizationPointRegistrationFailed",
            parts[1],
            SynchronizationPointFailureReason[parts[2]],
        )
        return
    if kind == "ANNOUNCE_SYNC_POINT":
        invoke_federate_callback(
            ambassador,
            "announceSynchronizationPoint",
            parts[1],
            decode_bytes(parts[2]),
        )
        return
    if kind == "FEDERATION_SYNCHRONIZED":
        invoke_federate_callback(
            ambassador,
            "federationSynchronized",
            parts[1],
            decode_handle_set(parts[2], FederateHandle, FederateHandleSet),
        )
        return
    if kind == "INITIATE_FEDERATE_SAVE":
        invoke_federate_callback(ambassador, "initiateFederateSave", parts[1])
        return
    if kind == "INITIATE_FEDERATE_SAVE_AT":
        time_type = logical_time_hint or parts[2]
        invoke_federate_callback(
            ambassador,
            "initiateFederateSave",
            parts[1],
            decode_logical_time(time_type, parts[3]),
        )
        return
    if kind == "FEDERATION_SAVED":
        invoke_federate_callback(ambassador, "federationSaved")
        return
    if kind == "FEDERATION_NOT_SAVED":
        invoke_federate_callback(ambassador, "federationNotSaved", SaveFailureReason[parts[1]])
        return
    if kind == "FEDERATION_SAVE_STATUS_RESPONSE":
        payload = []
        if len(parts) >= 2 and parts[1]:
            for item in parts[1].split(";"):
                handle_raw, status_raw = item.split(":", 1)
                payload.append(FederateHandleSaveStatusPair(FederateHandle(int(handle_raw)), SaveStatus[status_raw]))
        invoke_federate_callback(ambassador, "federationSaveStatusResponse", payload)
        return
    if kind == "REQUEST_FEDERATION_RESTORE_SUCCEEDED":
        invoke_federate_callback(ambassador, "requestFederationRestoreSucceeded", parts[1])
        return
    if kind == "REQUEST_FEDERATION_RESTORE_FAILED":
        invoke_federate_callback(ambassador, "requestFederationRestoreFailed", parts[1])
        return
    if kind == "FEDERATION_RESTORE_BEGUN":
        invoke_federate_callback(ambassador, "federationRestoreBegun")
        return
    if kind == "INITIATE_FEDERATE_RESTORE":
        invoke_federate_callback(
            ambassador,
            "initiateFederateRestore",
            parts[1],
            parts[2],
            FederateHandle(int(parts[3])),
        )
        return
    if kind == "FEDERATION_RESTORED":
        invoke_federate_callback(ambassador, "federationRestored")
        return
    if kind == "FEDERATION_NOT_RESTORED":
        invoke_federate_callback(ambassador, "federationNotRestored", RestoreFailureReason[parts[1]])
        return
    if kind == "FEDERATION_RESTORE_STATUS_RESPONSE":
        payload = []
        if len(parts) >= 2 and parts[1]:
            for item in parts[1].split(";"):
                pre_raw, post_raw, status_raw = item.split(":", 2)
                payload.append(
                    FederateRestoreStatus(
                        FederateHandle(int(pre_raw)),
                        FederateHandle(int(post_raw)),
                        RestoreStatus[status_raw],
                    )
                )
        invoke_federate_callback(ambassador, "federationRestoreStatusResponse", payload)
        return
    if kind == "OWNERSHIP_ACQUIRED":
        invoke_federate_callback(
            ambassador,
            "attributeOwnershipAcquisitionNotification",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION":
        invoke_federate_callback(
            ambassador,
            "requestAttributeOwnershipAssumption",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "INFORM_ATTRIBUTE_OWNERSHIP":
        invoke_federate_callback(
            ambassador,
            "informAttributeOwnership",
            ObjectInstanceHandle(int(parts[1])),
            AttributeHandle(int(parts[2])),
            FederateHandle(int(parts[3])),
        )
        return
    if kind == "ATTRIBUTE_IS_NOT_OWNED":
        invoke_federate_callback(
            ambassador,
            "attributeIsNotOwned",
            ObjectInstanceHandle(int(parts[1])),
            AttributeHandle(int(parts[2])),
        )
        return
    if kind == "ATTRIBUTE_OWNERSHIP_UNAVAILABLE":
        invoke_federate_callback(
            ambassador,
            "attributeOwnershipUnavailable",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE":
        invoke_federate_callback(
            ambassador,
            "requestAttributeOwnershipRelease",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_DIVESTITURE_CONFIRMATION":
        invoke_federate_callback(
            ambassador,
            "requestDivestitureConfirmation",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION":
        invoke_federate_callback(
            ambassador,
            "confirmAttributeOwnershipAcquisitionCancellation",
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    raise RTIinternalError(f"Unknown CERTI helper callback payload: {parts!r}")
