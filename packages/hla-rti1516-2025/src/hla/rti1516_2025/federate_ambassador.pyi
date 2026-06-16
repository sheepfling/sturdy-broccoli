from typing import Protocol, Sequence, Set, overload, runtime_checkable

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
    """Typed Python protocol for IEEE 1516.1-2025 FederateAmbassador.

    Source trace: Java and C++ API files in the 1516-2025_API_XML_2025_08_14 bundle.
    Python overloads preserve the Java overload set where Python can represent it unambiguously.
    """

    def connectionLost(self, faultDescription: str) -> None:
        """Source: Java FederateAmbassador.java §4.4; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def reportFederationExecutions(self, report: FederationExecutionInformationSet) -> None:
        """Source: Java FederateAmbassador.java §4.8; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def reportFederationExecutionMembers(self, federationName: str, report: FederationExecutionMemberInformationSet) -> None:
        """Source: Java FederateAmbassador.java §4.10; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def reportFederationExecutionDoesNotExist(self, federationName: str) -> None:
        """Source: Java FederateAmbassador.java §4.10; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federateResigned(self, reasonForResignDescription: str) -> None:
        """Source: Java FederateAmbassador.java §4.13; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def synchronizationPointRegistrationSucceeded(self, synchronizationPointLabel: str) -> None:
        """Source: Java FederateAmbassador.java §4.15; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def synchronizationPointRegistrationFailed(self, synchronizationPointLabel: str, reason: SynchronizationPointFailureReason) -> None:
        """Source: Java FederateAmbassador.java §4.15; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def announceSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §4.16; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationSynchronized(self, synchronizationPointLabel: str, failedToSyncSet: FederateHandleSet) -> None:
        """Source: Java FederateAmbassador.java §4.18; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    # Source: Java FederateAmbassador.java §4.20; C++ FederateAmbassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateInternalError.
    @overload
    def initiateFederateSave(self, label: str) -> None: ...
    @overload
    def initiateFederateSave(self, label: str, time: LogicalTime) -> None: ...

    def federationSaved(self) -> None:
        """Source: Java FederateAmbassador.java §4.23; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationNotSaved(self, reason: SaveFailureReason) -> None:
        """Source: Java FederateAmbassador.java §4.23; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationSaveStatusResponse(self, response: Sequence[FederateHandleSaveStatusPair]) -> None:
        """Source: Java FederateAmbassador.java §4.26; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def requestFederationRestoreSucceeded(self, label: str) -> None:
        """Source: Java FederateAmbassador.java §4.28; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def requestFederationRestoreFailed(self, label: str) -> None:
        """Source: Java FederateAmbassador.java §4.28; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationRestoreBegun(self) -> None:
        """Source: Java FederateAmbassador.java §4.29; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def initiateFederateRestore(self, label: str, federateName: str, postRestoreFederateHandle: FederateHandle) -> None:
        """Source: Java FederateAmbassador.java §4.30; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationRestored(self) -> None:
        """Source: Java FederateAmbassador.java §4.32; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationNotRestored(self, reason: RestoreFailureReason) -> None:
        """Source: Java FederateAmbassador.java §4.29; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def federationRestoreStatusResponse(self, response: Sequence[FederateRestoreStatus]) -> None:
        """Source: Java FederateAmbassador.java §4.35; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def startRegistrationForObjectClass(self, objectClass: ObjectClassHandle) -> None:
        """Source: Java FederateAmbassador.java §5.14; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def stopRegistrationForObjectClass(self, objectClass: ObjectClassHandle) -> None:
        """Source: Java FederateAmbassador.java §5.15; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def turnInteractionsOn(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java FederateAmbassador.java §5.16; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def turnInteractionsOff(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java FederateAmbassador.java §5.17; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def objectInstanceNameReservationSucceeded(self, objectInstanceName: str) -> None:
        """Source: Java FederateAmbassador.java §6.3; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def objectInstanceNameReservationFailed(self, objectInstanceName: str) -> None:
        """Source: Java FederateAmbassador.java §6.3; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def multipleObjectInstanceNameReservationSucceeded(self, objectInstanceNames: Set[str]) -> None:
        """Source: Java FederateAmbassador.java §6.6; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def multipleObjectInstanceNameReservationFailed(self, objectInstanceNames: Set[str]) -> None:
        """Source: Java FederateAmbassador.java §6.6; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def discoverObjectInstance(self, objectInstance: ObjectInstanceHandle, objectClass: ObjectClassHandle, objectInstanceName: str, producingFederate: FederateHandle) -> None:
        """Source: Java FederateAmbassador.java §6.9; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    # Source: Java FederateAmbassador.java §6.11; C++ FederateAmbassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateInternalError.
    @overload
    def reflectAttributeValues(self, objectInstance: ObjectInstanceHandle, attributeValues: AttributeHandleValueMap, userSuppliedTag: bytes, transportationType: TransportationTypeHandle, producingFederate: FederateHandle, optionalSentRegions: RegionHandleSet) -> None: ...
    @overload
    def reflectAttributeValues(self, objectInstance: ObjectInstanceHandle, attributeValues: AttributeHandleValueMap, userSuppliedTag: bytes, transportationType: TransportationTypeHandle, producingFederate: FederateHandle, optionalSentRegions: RegionHandleSet, time: LogicalTime, sentOrderType: OrderType, receivedOrderType: OrderType, optionalRetraction: MessageRetractionHandle) -> None: ...

    # Source: Java FederateAmbassador.java §6.13; C++ FederateAmbassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateInternalError.
    @overload
    def receiveInteraction(self, interactionClass: InteractionClassHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes, transportationType: TransportationTypeHandle, producingFederate: FederateHandle, optionalSentRegions: RegionHandleSet) -> None: ...
    @overload
    def receiveInteraction(self, interactionClass: InteractionClassHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes, transportationType: TransportationTypeHandle, producingFederate: FederateHandle, optionalSentRegions: RegionHandleSet, time: LogicalTime, sentOrderType: OrderType, receivedOrderType: OrderType, optionalRetraction: MessageRetractionHandle) -> None: ...

    # Source: Java FederateAmbassador.java §6.15; C++ FederateAmbassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateInternalError.
    @overload
    def receiveDirectedInteraction(self, interactionClass: InteractionClassHandle, objectInstance: ObjectInstanceHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes, transportationType: TransportationTypeHandle, producingFederate: FederateHandle) -> None: ...
    @overload
    def receiveDirectedInteraction(self, interactionClass: InteractionClassHandle, objectInstance: ObjectInstanceHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes, transportationType: TransportationTypeHandle, producingFederate: FederateHandle, time: LogicalTime, sentOrderType: OrderType, receivedOrderType: OrderType, optionalRetraction: MessageRetractionHandle) -> None: ...

    # Source: Java FederateAmbassador.java §6.17; C++ FederateAmbassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateInternalError.
    @overload
    def removeObjectInstance(self, objectInstance: ObjectInstanceHandle, userSuppliedTag: bytes, producingFederate: FederateHandle) -> None: ...
    @overload
    def removeObjectInstance(self, objectInstance: ObjectInstanceHandle, userSuppliedTag: bytes, producingFederate: FederateHandle, time: LogicalTime, sentOrderType: OrderType, receivedOrderType: OrderType, optionalRetraction: MessageRetractionHandle) -> None: ...

    def attributesInScope(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java FederateAmbassador.java §6.19; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def attributesOutOfScope(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java FederateAmbassador.java §6.20; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def provideAttributeValueUpdate(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §6.22; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    # Source: Java FederateAmbassador.java §6.23; C++ FederateAmbassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateInternalError.
    @overload
    def turnUpdatesOnForObjectInstance(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None: ...
    @overload
    def turnUpdatesOnForObjectInstance(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, updateRateDesignator: str) -> None: ...

    def turnUpdatesOffForObjectInstance(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java FederateAmbassador.java §6.24; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def confirmAttributeTransportationTypeChange(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, transportationType: TransportationTypeHandle) -> None:
        """Source: Java FederateAmbassador.java §6.26; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def reportAttributeTransportationType(self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle, transportationType: TransportationTypeHandle) -> None:
        """Source: Java FederateAmbassador.java §6.29; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def confirmInteractionTransportationTypeChange(self, interactionClass: InteractionClassHandle, transportationType: TransportationTypeHandle) -> None:
        """Source: Java FederateAmbassador.java §6.31; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def reportInteractionTransportationType(self, federate: FederateHandle, interactionClass: InteractionClassHandle, transportationType: TransportationTypeHandle) -> None:
        """Source: Java FederateAmbassador.java §6.33; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def requestAttributeOwnershipAssumption(self, objectInstance: ObjectInstanceHandle, offeredAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §7.4; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def requestDivestitureConfirmation(self, objectInstance: ObjectInstanceHandle, releasedAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §7.5; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def attributeOwnershipAcquisitionNotification(self, objectInstance: ObjectInstanceHandle, securedAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §7.7; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def attributeOwnershipUnavailable(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §7.10; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def requestAttributeOwnershipRelease(self, objectInstance: ObjectInstanceHandle, candidateAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java FederateAmbassador.java §7.11; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def confirmAttributeOwnershipAcquisitionCancellation(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java FederateAmbassador.java §7.16; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def informAttributeOwnership(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, owner: FederateHandle) -> None:
        """Source: Java FederateAmbassador.java §7.18; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def attributeIsNotOwned(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java FederateAmbassador.java §7.18; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def attributeIsOwnedByRTI(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java FederateAmbassador.java §7.18; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def timeRegulationEnabled(self, time: LogicalTime) -> None:
        """Source: Java FederateAmbassador.java §8.3; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def timeConstrainedEnabled(self, time: LogicalTime) -> None:
        """Source: Java FederateAmbassador.java §8.6; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def flushQueueGrant(self, time: LogicalTime, optimisticTime: LogicalTime) -> None:
        """Source: Java FederateAmbassador.java §8.13; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def timeAdvanceGrant(self, time: LogicalTime) -> None:
        """Source: Java FederateAmbassador.java §8.14; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...

    def requestRetraction(self, retraction: MessageRetractionHandle) -> None:
        """Source: Java FederateAmbassador.java §8.23; C++ FederateAmbassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateInternalError."""
        ...


class NullFederateAmbassador(FederateAmbassador):
    """Concrete scaffold mirroring FederateAmbassador; runtime implementation raises/notifies as in the .py module."""
    ...
