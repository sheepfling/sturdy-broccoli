"""Callback decoding for CERTI helper transport events."""
from __future__ import annotations

from typing import Any

from ...exceptions import RTIinternalError
from ...handles import (
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


def dispatch_helper_callback(ambassador: Any, parts: list[str], *, logical_time_hint: str | None = None) -> None:
    if ambassador is None or not parts:
        return

    kind = parts[0]
    if kind == "DISCOVER":
        getattr(ambassador, "discoverObjectInstance")(ObjectInstanceHandle(int(parts[1])), ObjectClassHandle(int(parts[2])), parts[3])
        return
    if kind == "REFLECT":
        getattr(ambassador, "reflectAttributeValues")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_value_map(parts[2], AttributeHandle, AttributeHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
        )
        return
    if kind == "REFLECT_TSO":
        time_type = logical_time_hint or parts[6]
        getattr(ambassador, "reflectAttributeValues")(
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
        getattr(ambassador, "receiveInteraction")(
            InteractionClassHandle(int(parts[1])),
            decode_handle_value_map(parts[2], ParameterHandle, ParameterHandleValueMap),
            decode_bytes(parts[3]),
            decode_order(parts[4]),
            TransportationTypeHandle(int(parts[5])),
        )
        return
    if kind == "INTERACTION_TSO":
        time_type = logical_time_hint or parts[6]
        getattr(ambassador, "receiveInteraction")(
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
        getattr(ambassador, "timeRegulationEnabled")(decode_logical_time(time_type, parts[2]))
        return
    if kind == "TIME_CONSTRAINED_ENABLED":
        time_type = logical_time_hint or parts[1]
        getattr(ambassador, "timeConstrainedEnabled")(decode_logical_time(time_type, parts[2]))
        return
    if kind == "TIME_ADVANCE_GRANT":
        time_type = logical_time_hint or parts[1]
        getattr(ambassador, "timeAdvanceGrant")(decode_logical_time(time_type, parts[2]))
        return
    if kind == "REQUEST_RETRACTION":
        getattr(ambassador, "requestRetraction")(MessageRetractionHandle(int(parts[1])))
        return
    if kind == "ANNOUNCE_SYNC_POINT":
        getattr(ambassador, "announceSynchronizationPoint")(parts[1], decode_bytes(parts[2]))
        return
    if kind == "FEDERATION_SYNCHRONIZED":
        getattr(ambassador, "federationSynchronized")(parts[1], decode_handle_set(parts[2], FederateHandle, FederateHandleSet))
        return
    if kind == "OWNERSHIP_ACQUIRED":
        getattr(ambassador, "attributeOwnershipAcquisitionNotification")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION":
        getattr(ambassador, "requestAttributeOwnershipAssumption")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "INFORM_ATTRIBUTE_OWNERSHIP":
        getattr(ambassador, "informAttributeOwnership")(
            ObjectInstanceHandle(int(parts[1])),
            AttributeHandle(int(parts[2])),
            FederateHandle(int(parts[3])),
        )
        return
    if kind == "ATTRIBUTE_IS_NOT_OWNED":
        getattr(ambassador, "attributeIsNotOwned")(ObjectInstanceHandle(int(parts[1])), AttributeHandle(int(parts[2])))
        return
    if kind == "ATTRIBUTE_OWNERSHIP_UNAVAILABLE":
        getattr(ambassador, "attributeOwnershipUnavailable")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE":
        getattr(ambassador, "requestAttributeOwnershipRelease")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
            decode_bytes(parts[3]),
        )
        return
    if kind == "REQUEST_DIVESTITURE_CONFIRMATION":
        getattr(ambassador, "requestDivestitureConfirmation")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    if kind == "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION":
        getattr(ambassador, "confirmAttributeOwnershipAcquisitionCancellation")(
            ObjectInstanceHandle(int(parts[1])),
            decode_handle_set(parts[2], AttributeHandle, AttributeHandleSet),
        )
        return
    raise RTIinternalError(f"Unknown CERTI helper callback payload: {parts!r}")
