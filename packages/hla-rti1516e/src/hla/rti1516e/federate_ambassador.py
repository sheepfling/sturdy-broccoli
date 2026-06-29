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
    """Runtime protocol surface for IEEE 1516.1-2010 FederateAmbassador."""

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
        theTime: LogicalTime | SupplementalReflectInfo | None = None,
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
        theTime: LogicalTime | SupplementalReceiveInfo | None = None,
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
        theTime: LogicalTime | SupplementalRemoveInfo | None = None,
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
