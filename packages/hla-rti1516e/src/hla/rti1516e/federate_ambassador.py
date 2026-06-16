from __future__ import annotations

import re
from typing import Protocol, Sequence, Set

from .datatypes import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformationSet,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
)
from .enums import (
    OrderType,
    RestoreFailureReason,
    SaveFailureReason,
    SynchronizationPointFailureReason,
)
from .handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    FederateHandle,
    FederateHandleSet,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandleValueMap,
    TransportationTypeHandle,
)
from .logical_time import LogicalTime


def lower_camel_to_snake(name: str) -> str:
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()

class FederateAmbassador(Protocol):
    """Runtime protocol surface. Strict overloads live in the .pyi stub and SOURCE_TRACE.md."""

    def connectionLost(self, faultDescription: str) -> None:
        ...

    def reportFederationExecutions(self, theFederationExecutionInformationSet: FederationExecutionInformationSet) -> None:
        ...

    def synchronizationPointRegistrationSucceeded(self, synchronizationPointLabel: str) -> None:
        ...

    def synchronizationPointRegistrationFailed(
        self,
        synchronizationPointLabel: str,
        reason: SynchronizationPointFailureReason,
    ) -> None:
        ...

    def announceSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: bytes) -> None:
        ...

    def federationSynchronized(self, synchronizationPointLabel: str, failedToSyncSet: FederateHandleSet) -> None:
        ...

    def initiateFederateSave(self, label: str, time: LogicalTime | None = None) -> None:
        ...

    def federationSaved(self) -> None:
        ...

    def federationNotSaved(self, reason: SaveFailureReason) -> None:
        ...

    def federationSaveStatusResponse(self, response: Sequence[FederateHandleSaveStatusPair]) -> None:
        ...

    def requestFederationRestoreSucceeded(self, label: str) -> None:
        ...

    def requestFederationRestoreFailed(self, label: str) -> None:
        ...

    def federationRestoreBegun(self) -> None:
        ...

    def initiateFederateRestore(self, label: str, federateName: str, federateHandle: FederateHandle) -> None:
        ...

    def federationRestored(self) -> None:
        ...

    def federationNotRestored(self, reason: RestoreFailureReason) -> None:
        ...

    def federationRestoreStatusResponse(self, response: Sequence[FederateRestoreStatus]) -> None:
        ...

    def startRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:
        ...

    def stopRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:
        ...

    def turnInteractionsOn(self, theHandle: InteractionClassHandle) -> None:
        ...

    def turnInteractionsOff(self, theHandle: InteractionClassHandle) -> None:
        ...

    def objectInstanceNameReservationSucceeded(self, objectName: str) -> None:
        ...

    def objectInstanceNameReservationFailed(self, objectName: str) -> None:
        ...

    def multipleObjectInstanceNameReservationSucceeded(self, objectNames: Set[str]) -> None:
        ...

    def multipleObjectInstanceNameReservationFailed(self, objectNames: Set[str]) -> None:
        ...

    def discoverObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theObjectClass: ObjectClassHandle,
        objectName: str,
        producingFederate: FederateHandle | None = None,
    ) -> None:
        ...

    def reflectAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleValueMap,
        userSuppliedTag: bytes,
        sentOrdering: OrderType,
        theTransport: TransportationTypeHandle,
        theTime: LogicalTime | None = None,
        receivedOrdering: OrderType | None = None,
        retractionHandle: MessageRetractionHandle | None = None,
        reflectInfo: SupplementalReflectInfo | None = None,
    ) -> None:
        ...

    def receiveInteraction(
        self,
        interactionClass: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        sentOrdering: OrderType,
        theTransport: TransportationTypeHandle,
        theTime: LogicalTime | None = None,
        receivedOrdering: OrderType | None = None,
        retractionHandle: MessageRetractionHandle | None = None,
        receiveInfo: SupplementalReceiveInfo | None = None,
    ) -> None:
        ...

    def removeObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        userSuppliedTag: bytes,
        sentOrdering: OrderType,
        theTime: LogicalTime | None = None,
        receivedOrdering: OrderType | None = None,
        retractionHandle: MessageRetractionHandle | None = None,
        removeInfo: SupplementalRemoveInfo | None = None,
    ) -> None:
        ...

    def attributesInScope(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        ...

    def attributesOutOfScope(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        ...

    def provideAttributeValueUpdate(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def turnUpdatesOnForObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:
        ...

    def turnUpdatesOffForObjectInstance(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        ...

    def confirmAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theTransportation: TransportationTypeHandle,
    ) -> None:
        ...

    def reportAttributeTransportationType(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
        theTransportation: TransportationTypeHandle,
    ) -> None:
        ...

    def confirmInteractionTransportationTypeChange(
        self,
        theInteraction: InteractionClassHandle,
        theTransportation: TransportationTypeHandle,
    ) -> None:
        ...

    def reportInteractionTransportationType(
        self,
        theFederate: FederateHandle,
        theInteraction: InteractionClassHandle,
        theTransportation: TransportationTypeHandle,
    ) -> None:
        ...

    def requestAttributeOwnershipAssumption(
        self,
        theObject: ObjectInstanceHandle,
        offeredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def requestDivestitureConfirmation(self, theObject: ObjectInstanceHandle, offeredAttributes: AttributeHandleSet) -> None:
        ...

    def attributeOwnershipAcquisitionNotification(
        self,
        theObject: ObjectInstanceHandle,
        securedAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def attributeOwnershipUnavailable(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        ...

    def requestAttributeOwnershipRelease(
        self,
        theObject: ObjectInstanceHandle,
        candidateAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def confirmAttributeOwnershipAcquisitionCancellation(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:
        ...

    def informAttributeOwnership(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
        theOwner: FederateHandle,
    ) -> None:
        ...

    def attributeIsNotOwned(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        ...

    def attributeIsOwnedByRTI(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        ...

    def timeRegulationEnabled(self, time: LogicalTime) -> None:
        ...

    def timeConstrainedEnabled(self, time: LogicalTime) -> None:
        ...

    def timeAdvanceGrant(self, theTime: LogicalTime) -> None:
        ...

    def requestRetraction(self, theHandle: MessageRetractionHandle) -> None:
        ...

class UnimplementedFederateAmbassador(FederateAmbassador):
    def connectionLost(self, faultDescription: str) -> None:
        raise NotImplementedError()

    def reportFederationExecutions(self, theFederationExecutionInformationSet: FederationExecutionInformationSet) -> None:
        raise NotImplementedError()

    def synchronizationPointRegistrationSucceeded(self, synchronizationPointLabel: str) -> None:
        raise NotImplementedError()

    def synchronizationPointRegistrationFailed(self, synchronizationPointLabel: str, reason: SynchronizationPointFailureReason) -> None:
        raise NotImplementedError()

    def announceSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def federationSynchronized(self, synchronizationPointLabel: str, failedToSyncSet: FederateHandleSet) -> None:
        raise NotImplementedError()

    def initiateFederateSave(self, label: str, time: LogicalTime | None=None) -> None:
        raise NotImplementedError()

    def federationSaved(self) -> None:
        raise NotImplementedError()

    def federationNotSaved(self, reason: SaveFailureReason) -> None:
        raise NotImplementedError()

    def federationSaveStatusResponse(self, response: Sequence[FederateHandleSaveStatusPair]) -> None:
        raise NotImplementedError()

    def requestFederationRestoreSucceeded(self, label: str) -> None:
        raise NotImplementedError()

    def requestFederationRestoreFailed(self, label: str) -> None:
        raise NotImplementedError()

    def federationRestoreBegun(self) -> None:
        raise NotImplementedError()

    def initiateFederateRestore(self, label: str, federateName: str, federateHandle: FederateHandle) -> None:
        raise NotImplementedError()

    def federationRestored(self) -> None:
        raise NotImplementedError()

    def federationNotRestored(self, reason: RestoreFailureReason) -> None:
        raise NotImplementedError()

    def federationRestoreStatusResponse(self, response: Sequence[FederateRestoreStatus]) -> None:
        raise NotImplementedError()

    def startRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:
        raise NotImplementedError()

    def stopRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:
        raise NotImplementedError()

    def turnInteractionsOn(self, theHandle: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def turnInteractionsOff(self, theHandle: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def objectInstanceNameReservationSucceeded(self, objectName: str) -> None:
        raise NotImplementedError()

    def objectInstanceNameReservationFailed(self, objectName: str) -> None:
        raise NotImplementedError()

    def multipleObjectInstanceNameReservationSucceeded(self, objectNames: Set[str]) -> None:
        raise NotImplementedError()

    def multipleObjectInstanceNameReservationFailed(self, objectNames: Set[str]) -> None:
        raise NotImplementedError()

    def discoverObjectInstance(self, theObject: ObjectInstanceHandle, theObjectClass: ObjectClassHandle, objectName: str, producingFederate: FederateHandle | None=None) -> None:
        raise NotImplementedError()

    def reflectAttributeValues(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleValueMap, userSuppliedTag: bytes, sentOrdering: OrderType, theTransport: TransportationTypeHandle, theTime: LogicalTime | None=None, receivedOrdering: OrderType | None=None, retractionHandle: MessageRetractionHandle | None=None, reflectInfo: SupplementalReflectInfo | None=None) -> None:
        raise NotImplementedError()

    def receiveInteraction(self, interactionClass: InteractionClassHandle, theParameters: ParameterHandleValueMap, userSuppliedTag: bytes, sentOrdering: OrderType, theTransport: TransportationTypeHandle, theTime: LogicalTime | None=None, receivedOrdering: OrderType | None=None, retractionHandle: MessageRetractionHandle | None=None, receiveInfo: SupplementalReceiveInfo | None=None) -> None:
        raise NotImplementedError()

    def removeObjectInstance(self, theObject: ObjectInstanceHandle, userSuppliedTag: bytes, sentOrdering: OrderType, theTime: LogicalTime | None=None, receivedOrdering: OrderType | None=None, retractionHandle: MessageRetractionHandle | None=None, removeInfo: SupplementalRemoveInfo | None=None) -> None:
        raise NotImplementedError()

    def attributesInScope(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def attributesOutOfScope(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def provideAttributeValueUpdate(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def turnUpdatesOnForObjectInstance(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, updateRateDesignator: str | None=None) -> None:
        raise NotImplementedError()

    def turnUpdatesOffForObjectInstance(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def confirmAttributeTransportationTypeChange(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, theTransportation: TransportationTypeHandle) -> None:
        raise NotImplementedError()

    def reportAttributeTransportationType(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle, theTransportation: TransportationTypeHandle) -> None:
        raise NotImplementedError()

    def confirmInteractionTransportationTypeChange(self, theInteraction: InteractionClassHandle, theTransportation: TransportationTypeHandle) -> None:
        raise NotImplementedError()

    def reportInteractionTransportationType(self, theFederate: FederateHandle, theInteraction: InteractionClassHandle, theTransportation: TransportationTypeHandle) -> None:
        raise NotImplementedError()

    def requestAttributeOwnershipAssumption(self, theObject: ObjectInstanceHandle, offeredAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def requestDivestitureConfirmation(self, theObject: ObjectInstanceHandle, offeredAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisitionNotification(self, theObject: ObjectInstanceHandle, securedAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def attributeOwnershipUnavailable(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def requestAttributeOwnershipRelease(self, theObject: ObjectInstanceHandle, candidateAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def confirmAttributeOwnershipAcquisitionCancellation(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def informAttributeOwnership(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle, theOwner: FederateHandle) -> None:
        raise NotImplementedError()

    def attributeIsNotOwned(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        raise NotImplementedError()

    def attributeIsOwnedByRTI(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        raise NotImplementedError()

    def timeRegulationEnabled(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def timeConstrainedEnabled(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def timeAdvanceGrant(self, theTime: LogicalTime) -> None:
        raise NotImplementedError()

    def requestRetraction(self, theHandle: MessageRetractionHandle) -> None:
        raise NotImplementedError()

class NullFederateAmbassador(FederateAmbassador):
    """No-op federate callback sink matching the standard NullFederateAmbassador shape."""

    def __getattribute__(self, name: str):
        if name.startswith("__"):
            return super().__getattribute__(name)

        protocol_attr = getattr(FederateAmbassador, name, None)
        owner_attr = getattr(type(self), name, None)
        if owner_attr is not None and owner_attr is not protocol_attr:
            return super().__getattribute__(name)

        snake_name = lower_camel_to_snake(name)
        if snake_name != name:
            snake_protocol_attr = getattr(FederateAmbassador, snake_name, None)
            snake_attr = getattr(type(self), snake_name, None)
            if snake_attr is not None and snake_attr is not snake_protocol_attr:
                return object.__getattribute__(self, snake_name)

        if protocol_attr is not None:
            return self.__getattr__(name)

        return super().__getattribute__(name)

    def __getattr__(self, name: str):
        def _callback(*args, **kwargs) -> None:
            return None

        return _callback
