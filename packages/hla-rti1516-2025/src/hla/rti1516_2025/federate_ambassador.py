"""FederateAmbassador model for IEEE 1516.1-2025.

Sources: Java FederateAmbassador.java and C++ FederateAmbassador.h.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence, Set, runtime_checkable

from .datatypes import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformationSet,
    FederationExecutionMemberInformationSet,
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
    RegionHandleSet,
    TransportationTypeHandle,
)
from .logical_time import LogicalTime


@runtime_checkable
class FederateAmbassador(Protocol):
    """Runtime protocol surface for IEEE 1516.1-2025 federate callback services."""
    def connectionLost(self, faultDescription: str) -> None: ...

    def reportFederationExecutions(
        self, report: FederationExecutionInformationSet
    ) -> None: ...

    def reportFederationExecutionMembers(
        self, federationName: str, report: FederationExecutionMemberInformationSet
    ) -> None: ...

    def reportFederationExecutionDoesNotExist(self, federationName: str) -> None: ...
    def federateResigned(self, reasonForResignDescription: str) -> None: ...

    def synchronizationPointRegistrationSucceeded(
        self, synchronizationPointLabel: str
    ) -> None: ...

    def synchronizationPointRegistrationFailed(
        self, synchronizationPointLabel: str, reason: SynchronizationPointFailureReason
    ) -> None: ...

    def announceSynchronizationPoint(
        self, synchronizationPointLabel: str, userSuppliedTag: bytes
    ) -> None: ...

    def federationSynchronized(
        self, synchronizationPointLabel: str, failedToSyncSet: FederateHandleSet
    ) -> None: ...

    def initiateFederateSave(
        self, label: str, time: LogicalTime | None = None
    ) -> None: ...

    def federationSaved(self) -> None: ...
    def federationNotSaved(self, reason: SaveFailureReason) -> None: ...

    def federationSaveStatusResponse(
        self, response: Sequence[FederateHandleSaveStatusPair]
    ) -> None: ...

    def requestFederationRestoreSucceeded(self, label: str) -> None: ...
    def requestFederationRestoreFailed(self, label: str) -> None: ...
    def federationRestoreBegun(self) -> None: ...

    def initiateFederateRestore(
        self, label: str, federateName: str, postRestoreFederateHandle: FederateHandle
    ) -> None: ...

    def federationRestored(self) -> None: ...
    def federationNotRestored(self, reason: RestoreFailureReason) -> None: ...

    def federationRestoreStatusResponse(
        self, response: Sequence[FederateRestoreStatus]
    ) -> None: ...

    def startRegistrationForObjectClass(
        self, objectClass: ObjectClassHandle
    ) -> None: ...

    def stopRegistrationForObjectClass(
        self, objectClass: ObjectClassHandle
    ) -> None: ...
    def turnInteractionsOn(self, interactionClass: InteractionClassHandle) -> None: ...
    def turnInteractionsOff(self, interactionClass: InteractionClassHandle) -> None: ...

    def objectInstanceNameReservationSucceeded(
        self, objectInstanceName: str
    ) -> None: ...
    def objectInstanceNameReservationFailed(self, objectInstanceName: str) -> None: ...

    def multipleObjectInstanceNameReservationSucceeded(
        self, objectInstanceNames: Set[str]
    ) -> None: ...

    def multipleObjectInstanceNameReservationFailed(
        self, objectInstanceNames: Set[str]
    ) -> None: ...

    def discoverObjectInstance(
        self,
        objectInstance: ObjectInstanceHandle,
        objectClass: ObjectClassHandle,
        objectInstanceName: str,
        producingFederate: FederateHandle,
    ) -> None: ...

    def reflectAttributeValues(
        self,
        objectInstance: ObjectInstanceHandle,
        attributeValues: AttributeHandleValueMap,
        userSuppliedTag: bytes,
        transportationType: TransportationTypeHandle,
        producingFederate: FederateHandle,
        optionalSentRegions: RegionHandleSet,
        time: LogicalTime | None = None,
        sentOrderType: OrderType | None = None,
        receivedOrderType: OrderType | None = None,
        optionalRetraction: MessageRetractionHandle | None = None,
    ) -> None: ...

    def receiveInteraction(
        self,
        interactionClass: InteractionClassHandle,
        parameterValues: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        transportationType: TransportationTypeHandle,
        producingFederate: FederateHandle,
        optionalSentRegions: RegionHandleSet,
        time: LogicalTime | None = None,
        sentOrderType: OrderType | None = None,
        receivedOrderType: OrderType | None = None,
        optionalRetraction: MessageRetractionHandle | None = None,
    ) -> None: ...

    def receiveDirectedInteraction(
        self,
        interactionClass: InteractionClassHandle,
        objectInstance: ObjectInstanceHandle,
        parameterValues: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        transportationType: TransportationTypeHandle,
        producingFederate: FederateHandle,
        time: LogicalTime | None = None,
        sentOrderType: OrderType | None = None,
        receivedOrderType: OrderType | None = None,
        optionalRetraction: MessageRetractionHandle | None = None,
    ) -> None: ...

    def removeObjectInstance(
        self,
        objectInstance: ObjectInstanceHandle,
        userSuppliedTag: bytes,
        producingFederate: FederateHandle,
        time: LogicalTime | None = None,
        sentOrderType: OrderType | None = None,
        receivedOrderType: OrderType | None = None,
        optionalRetraction: MessageRetractionHandle | None = None,
    ) -> None: ...

    def attributesInScope(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def attributesOutOfScope(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def provideAttributeValueUpdate(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def turnUpdatesOnForObjectInstance(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None: ...

    def turnUpdatesOffForObjectInstance(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def confirmAttributeTransportationTypeChange(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def reportAttributeTransportationType(
        self,
        objectInstance: ObjectInstanceHandle,
        attribute: AttributeHandle,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def confirmInteractionTransportationTypeChange(
        self,
        interactionClass: InteractionClassHandle,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def reportInteractionTransportationType(
        self,
        federate: FederateHandle,
        interactionClass: InteractionClassHandle,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def requestAttributeOwnershipAssumption(
        self,
        objectInstance: ObjectInstanceHandle,
        offeredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def requestDivestitureConfirmation(
        self,
        objectInstance: ObjectInstanceHandle,
        releasedAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def attributeOwnershipAcquisitionNotification(
        self,
        objectInstance: ObjectInstanceHandle,
        securedAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def attributeOwnershipUnavailable(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def requestAttributeOwnershipRelease(
        self,
        objectInstance: ObjectInstanceHandle,
        candidateAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def confirmAttributeOwnershipAcquisitionCancellation(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def informAttributeOwnership(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        owner: FederateHandle,
    ) -> None: ...

    def attributeIsNotOwned(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def attributeIsOwnedByRTI(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def timeRegulationEnabled(self, time: LogicalTime) -> None: ...
    def timeConstrainedEnabled(self, time: LogicalTime) -> None: ...

    def flushQueueGrant(
        self, time: LogicalTime, optimisticTime: LogicalTime
    ) -> None: ...
    def timeAdvanceGrant(self, time: LogicalTime) -> None: ...
    def requestRetraction(self, retraction: MessageRetractionHandle) -> None: ...


class NullFederateAmbassador(FederateAmbassador):
    def connectionLost(self, faultDescription: str) -> None:
        return None

    def __getattr__(self, name: str):
        def _callback(*args: Any, **kwargs: Any) -> None:
            return None

        return _callback


__all__ = ["FederateAmbassador", "NullFederateAmbassador"]
