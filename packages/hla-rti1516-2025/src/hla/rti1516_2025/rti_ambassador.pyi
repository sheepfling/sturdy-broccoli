from typing import Protocol, Sequence, Set, overload

from .datatypes import (
    ConfigurationResult,
    Credentials,
    MessageRetractionReturn,
    RangeBounds,
    RtiConfiguration,
)
from .enums import CallbackModel, OrderType, ResignAction, ServiceGroup
from .federate_ambassador import FederateAmbassador
from .handle_factory import (
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    DimensionHandleSetFactory,
    FederateHandleFactory,
    FederateHandleSetFactory,
    InteractionClassHandleSetFactory,
    ObjectClassHandleFactory,
    InteractionClassHandleFactory,
    ObjectInstanceHandleFactory,
    AttributeHandleFactory,
    ParameterHandleFactory,
    DimensionHandleFactory,
    MessageRetractionHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandleFactory,
    RegionHandleSetFactory,
    TransportationTypeHandleFactory,
)
from .handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    AttributeSetRegionSetPairList,
    DimensionHandle,
    DimensionHandleSet,
    FederateHandle,
    FederateHandleSet,
    InteractionClassHandle,
    InteractionClassHandleSet,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    ParameterHandleValueMap,
    RegionHandle,
    RegionHandleSet,
    TransportationTypeHandle,
)
from .logical_time import (
    LogicalTime,
    LogicalTimeFactory,
    LogicalTimeInterval,
    TimeQueryReturn,
)

class RTIambassador(Protocol):
    """Typed Python protocol for IEEE 1516.1-2025 RTIambassador.

    Source trace: Java and C++ API files in the 1516-2025_API_XML_2025_08_14 bundle.
    Python overloads preserve the Java overload set where Python can represent it unambiguously.
    """

    # Source: Java RTIambassador.java §4.2; C++ RTIambassador.h. Java overloads: 4; C++ overloads: 4. Java throws: AlreadyConnected, CallNotAllowedFromWithinCallback, ConnectionFailed, InvalidCredentials, RTIinternalError, Unauthorized, UnsupportedCallbackModel.
    @overload
    def connect(self, federateAmbassador: FederateAmbassador, callbackModel: CallbackModel) -> ConfigurationResult: ...
    @overload
    def connect(self, federateAmbassador: FederateAmbassador, callbackModel: CallbackModel, configuration: RtiConfiguration) -> ConfigurationResult: ...
    @overload
    def connect(self, federateAmbassador: FederateAmbassador, callbackModel: CallbackModel, credentials: Credentials) -> ConfigurationResult: ...
    @overload
    def connect(self, federateAmbassador: FederateAmbassador, callbackModel: CallbackModel, configuration: RtiConfiguration, credentials: Credentials) -> ConfigurationResult: ...

    def disconnect(self) -> None:
        """Source: Java RTIambassador.java §4.3; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: CallNotAllowedFromWithinCallback, FederateIsExecutionMember, RTIinternalError."""
        ...

    # Source: Java RTIambassador.java §4.5; C++ RTIambassador.h. Java overloads: 4; C++ overloads: 2. Java throws: CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM, ErrorReadingFOM, FederationExecutionAlreadyExists, InconsistentFOM, InvalidFOM, NotConnected, RTIinternalError, Unauthorized.
    @overload
    def createFederationExecution(self, federationName: str, fomModule: str) -> None: ...
    @overload
    def createFederationExecution(self, federationName: str, fomModule: str, logicalTimeImplementationName: str) -> None: ...
    @overload
    def createFederationExecution(self, federationName: str, fomModules: Sequence[str]) -> None: ...
    @overload
    def createFederationExecution(self, federationName: str, fomModules: Sequence[str], logicalTimeImplementationName: str) -> None: ...

    # Source: Java RTIambassador.java §4.5; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 1. Java throws: CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM, CouldNotOpenMIM, DesignatorIsHLAstandardMIM, ErrorReadingFOM, ErrorReadingMIM, FederationExecutionAlreadyExists, InconsistentFOM, InvalidFOM, InvalidMIM, NotConnected, RTIinternalError; ….
    @overload
    def createFederationExecutionWithMIM(self, federationName: str, fomModules: Sequence[str], mimModule: str) -> None: ...
    @overload
    def createFederationExecutionWithMIM(self, federationName: str, fomModules: Sequence[str], mimModule: str, logicalTimeImplementationName: str) -> None: ...

    def destroyFederationExecution(self, federationName: str) -> None:
        """Source: Java RTIambassador.java §4.6; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederatesCurrentlyJoined, FederationExecutionDoesNotExist, NotConnected, RTIinternalError, Unauthorized."""
        ...

    def listFederationExecutions(self) -> None:
        """Source: Java RTIambassador.java §4.7; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: NotConnected, RTIinternalError."""
        ...

    def listFederationExecutionMembers(self, federationName: str) -> None:
        """Source: Java RTIambassador.java §4.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: NotConnected, RTIinternalError."""
        ...

    # Source: Java RTIambassador.java §4.11; C++ RTIambassador.h. Java overloads: 4; C++ overloads: 2. Java throws: CallNotAllowedFromWithinCallback, CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM, ErrorReadingFOM, FederateAlreadyExecutionMember, FederateNameAlreadyInUse, FederationExecutionDoesNotExist, InconsistentFOM, InvalidFOM, NotConnected, RTIinternalError, RestoreInProgress; ….
    @overload
    def joinFederationExecution(self, *, federateType: str, federationName: str) -> FederateHandle: ...
    @overload
    def joinFederationExecution(self, *, federateType: str, federationName: str, additionalFomModules: Sequence[str]) -> FederateHandle: ...
    @overload
    def joinFederationExecution(self, *, federateName: str, federateType: str, federationName: str) -> FederateHandle: ...
    @overload
    def joinFederationExecution(self, *, federateName: str, federateType: str, federationName: str, additionalFomModules: Sequence[str]) -> FederateHandle: ...

    def resignFederationExecution(self, resignAction: ResignAction) -> None:
        """Source: Java RTIambassador.java §4.12; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: CallNotAllowedFromWithinCallback, FederateNotExecutionMember, FederateOwnsAttributes, InvalidResignAction, NotConnected, OwnershipAcquisitionPending, RTIinternalError."""
        ...

    # Source: Java RTIambassador.java §4.14; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, InvalidFederateHandle, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def registerFederationSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: bytes) -> None: ...
    @overload
    def registerFederationSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: bytes, synchronizationSet: FederateHandleSet) -> None: ...

    # Source: Java RTIambassador.java §4.17; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, SynchronizationPointLabelNotAnnounced.
    @overload
    def synchronizationPointAchieved(self, synchronizationPointLabel: str) -> None: ...
    @overload
    def synchronizationPointAchieved(self, synchronizationPointLabel: str, successfully: bool) -> None: ...

    # Source: Java RTIambassador.java §4.19; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, FederateUnableToUseTime, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def requestFederationSave(self, label: str) -> None: ...
    @overload
    def requestFederationSave(self, label: str, time: LogicalTime) -> None: ...

    def federateSaveBegun(self) -> None:
        """Source: Java RTIambassador.java §4.21; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveNotInitiated."""
        ...

    def federateSaveComplete(self) -> None:
        """Source: Java RTIambassador.java §4.22; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateHasNotBegunSave, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress."""
        ...

    def federateSaveNotComplete(self) -> None:
        """Source: Java RTIambassador.java §4.22; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateHasNotBegunSave, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress."""
        ...

    def abortFederationSave(self) -> None:
        """Source: Java RTIambassador.java §4.24; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, SaveNotInProgress."""
        ...

    def queryFederationSaveStatus(self) -> None:
        """Source: Java RTIambassador.java §4.25; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress."""
        ...

    def requestFederationRestore(self, label: str) -> None:
        """Source: Java RTIambassador.java §4.27; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def federateRestoreComplete(self) -> None:
        """Source: Java RTIambassador.java §4.31; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreNotRequested, SaveInProgress."""
        ...

    def federateRestoreNotComplete(self) -> None:
        """Source: Java RTIambassador.java §4.31; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreNotRequested, SaveInProgress."""
        ...

    def abortFederationRestore(self) -> None:
        """Source: Java RTIambassador.java §4.33; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreNotInProgress."""
        ...

    def queryFederationRestoreStatus(self) -> None:
        """Source: Java RTIambassador.java §4.34; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, SaveInProgress."""
        ...

    def publishObjectClassAttributes(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java RTIambassador.java §5.2; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def unpublishObjectClass(self, objectClass: ObjectClassHandle) -> None:
        """Source: Java RTIambassador.java §5.3; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, OwnershipAcquisitionPending, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def unpublishObjectClassAttributes(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java RTIambassador.java §5.3; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, OwnershipAcquisitionPending, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def publishInteractionClass(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java RTIambassador.java §5.4; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def unpublishInteractionClass(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java RTIambassador.java §5.5; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def publishObjectClassDirectedInteractions(self, objectClass: ObjectClassHandle, interactionClasses: InteractionClassHandleSet) -> None:
        """Source: Java RTIambassador.java §5.6; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §5.7; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def unpublishObjectClassDirectedInteractions(self, objectClass: ObjectClassHandle) -> None: ...
    @overload
    def unpublishObjectClassDirectedInteractions(self, objectClass: ObjectClassHandle, interactionClasses: InteractionClassHandleSet) -> None: ...

    # Source: Java RTIambassador.java §5.8; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidUpdateRateDesignator, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def subscribeObjectClassAttributes(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet) -> None: ...
    @overload
    def subscribeObjectClassAttributes(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet, updateRateDesignator: str) -> None: ...

    # Source: Java RTIambassador.java §5.8; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 0. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidUpdateRateDesignator, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def subscribeObjectClassAttributesPassively(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet) -> None: ...
    @overload
    def subscribeObjectClassAttributesPassively(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet, updateRateDesignator: str) -> None: ...

    def unsubscribeObjectClass(self, objectClass: ObjectClassHandle) -> None:
        """Source: Java RTIambassador.java §5.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def unsubscribeObjectClassAttributes(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java RTIambassador.java §5.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def subscribeInteractionClass(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java RTIambassador.java §5.10; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def subscribeInteractionClassPassively(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java RTIambassador.java §5.10; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def unsubscribeInteractionClass(self, interactionClass: InteractionClassHandle) -> None:
        """Source: Java RTIambassador.java §5.11; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def subscribeObjectClassDirectedInteractions(self, objectClass: ObjectClassHandle, interactionClasses: InteractionClassHandleSet) -> None:
        """Source: Java RTIambassador.java §5.12; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def subscribeObjectClassDirectedInteractionsUniversally(self, objectClass: ObjectClassHandle, interactionClasses: InteractionClassHandleSet) -> None:
        """Source: Java RTIambassador.java §5.12; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §5.13; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def unsubscribeObjectClassDirectedInteractions(self, objectClass: ObjectClassHandle) -> None: ...
    @overload
    def unsubscribeObjectClassDirectedInteractions(self, objectClass: ObjectClassHandle, interactionClasses: InteractionClassHandleSet) -> None: ...

    def reserveObjectInstanceName(self, objectInstanceName: str) -> None:
        """Source: Java RTIambassador.java §6.2; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, IllegalName, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def releaseObjectInstanceName(self, objectInstanceName: str) -> None:
        """Source: Java RTIambassador.java §6.4; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectInstanceNameNotReserved, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def reserveMultipleObjectInstanceNames(self, objectInstanceNames: Set[str]) -> None:
        """Source: Java RTIambassador.java §6.5; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, IllegalName, NameSetWasEmpty, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def releaseMultipleObjectInstanceNames(self, objectInstanceNames: Set[str]) -> None:
        """Source: Java RTIambassador.java §6.7; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectInstanceNameNotReserved, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §6.8; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, ObjectClassNotPublished, ObjectInstanceNameInUse, ObjectInstanceNameNotReserved, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def registerObjectInstance(self, objectClass: ObjectClassHandle) -> ObjectInstanceHandle: ...
    @overload
    def registerObjectInstance(self, objectClass: ObjectClassHandle, objectInstanceName: str) -> ObjectInstanceHandle: ...

    # Source: Java RTIambassador.java §6.10; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, InvalidLogicalTime, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def updateAttributeValues(self, objectInstance: ObjectInstanceHandle, attributeValues: AttributeHandleValueMap, userSuppliedTag: bytes) -> None: ...
    @overload
    def updateAttributeValues(self, objectInstance: ObjectInstanceHandle, attributeValues: AttributeHandleValueMap, userSuppliedTag: bytes, time: LogicalTime) -> MessageRetractionReturn: ...

    # Source: Java RTIambassador.java §6.12; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, InteractionParameterNotDefined, InvalidLogicalTime, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def sendInteraction(self, interactionClass: InteractionClassHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes) -> None: ...
    @overload
    def sendInteraction(self, interactionClass: InteractionClassHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes, time: LogicalTime) -> MessageRetractionReturn: ...

    # Source: Java RTIambassador.java §6.14; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, InteractionParameterNotDefined, InvalidLogicalTime, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def sendDirectedInteraction(self, interactionClass: InteractionClassHandle, objectInstance: ObjectInstanceHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes) -> None: ...
    @overload
    def sendDirectedInteraction(self, interactionClass: InteractionClassHandle, objectInstance: ObjectInstanceHandle, parameterValues: ParameterHandleValueMap, userSuppliedTag: bytes, time: LogicalTime) -> MessageRetractionReturn: ...

    # Source: Java RTIambassador.java §6.16; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: DeletePrivilegeNotHeld, FederateNotExecutionMember, InvalidLogicalTime, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def deleteObjectInstance(self, objectInstance: ObjectInstanceHandle, userSuppliedTag: bytes) -> None: ...
    @overload
    def deleteObjectInstance(self, objectInstance: ObjectInstanceHandle, userSuppliedTag: bytes, time: LogicalTime) -> MessageRetractionReturn: ...

    def localDeleteObjectInstance(self, objectInstance: ObjectInstanceHandle) -> None:
        """Source: Java RTIambassador.java §6.18; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, FederateOwnsAttributes, NotConnected, ObjectInstanceNotKnown, OwnershipAcquisitionPending, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §6.21; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress.
    @overload
    def requestAttributeValueUpdate(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None: ...
    @overload
    def requestAttributeValueUpdate(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None: ...

    def requestAttributeTransportationTypeChange(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, transportationType: TransportationTypeHandle) -> None:
        """Source: Java RTIambassador.java §6.25; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeAlreadyBeingChanged, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, InvalidTransportationTypeHandle, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def changeDefaultAttributeTransportationType(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet, transportationType: TransportationTypeHandle) -> None:
        """Source: Java RTIambassador.java §6.27; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidTransportationTypeHandle, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def queryAttributeTransportationType(self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle) -> None:
        """Source: Java RTIambassador.java §6.28; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def requestInteractionTransportationTypeChange(self, interactionClass: InteractionClassHandle, transportationType: TransportationTypeHandle) -> None:
        """Source: Java RTIambassador.java §6.30; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassAlreadyBeingChanged, InteractionClassNotDefined, InteractionClassNotPublished, InvalidTransportationTypeHandle, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def queryInteractionTransportationType(self, federate: FederateHandle, interactionClass: InteractionClassHandle) -> None:
        """Source: Java RTIambassador.java §6.32; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def unconditionalAttributeOwnershipDivestiture(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §7.2; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def negotiatedAttributeOwnershipDivestiture(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §7.3; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeAlreadyBeingDivested, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def confirmDivestiture(self, objectInstance: ObjectInstanceHandle, confirmedAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §7.6; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeDivestitureWasNotRequested, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NoAcquisitionPending, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def attributeOwnershipAcquisition(self, objectInstance: ObjectInstanceHandle, desiredAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §7.8; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, AttributeNotPublished, FederateNotExecutionMember, FederateOwnsAttributes, NotConnected, ObjectClassNotPublished, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def attributeOwnershipAcquisitionIfAvailable(self, objectInstance: ObjectInstanceHandle, desiredAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §7.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeAlreadyBeingAcquired, AttributeNotDefined, AttributeNotPublished, FederateNotExecutionMember, FederateOwnsAttributes, NotConnected, ObjectClassNotPublished, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def attributeOwnershipReleaseDenied(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §7.12; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def attributeOwnershipDivestitureIfWanted(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, userSuppliedTag: bytes) -> AttributeHandleSet:
        """Source: Java RTIambassador.java §7.13; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def cancelNegotiatedAttributeOwnershipDivestiture(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java RTIambassador.java §7.14; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeDivestitureWasNotRequested, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def cancelAttributeOwnershipAcquisition(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java RTIambassador.java §7.15; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeAcquisitionWasNotRequested, AttributeAlreadyOwned, AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def queryAttributeOwnership(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet) -> None:
        """Source: Java RTIambassador.java §7.17; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def isAttributeOwnedByFederate(self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle) -> bool:
        """Source: Java RTIambassador.java §7.19; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def enableTimeRegulation(self, lookahead: LogicalTimeInterval) -> None:
        """Source: Java RTIambassador.java §8.2; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLookahead, NotConnected, RTIinternalError, RequestForTimeRegulationPending, RestoreInProgress, SaveInProgress, TimeRegulationAlreadyEnabled."""
        ...

    def disableTimeRegulation(self) -> None:
        """Source: Java RTIambassador.java §8.4; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeRegulationIsNotEnabled."""
        ...

    def enableTimeConstrained(self) -> None:
        """Source: Java RTIambassador.java §8.5; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RestoreInProgress, SaveInProgress, TimeConstrainedAlreadyEnabled."""
        ...

    def disableTimeConstrained(self) -> None:
        """Source: Java RTIambassador.java §8.7; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeConstrainedIsNotEnabled."""
        ...

    def timeAdvanceRequest(self, time: LogicalTime) -> None:
        """Source: Java RTIambassador.java §8.8; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RequestForTimeRegulationPending, RestoreInProgress, SaveInProgress."""
        ...

    def timeAdvanceRequestAvailable(self, time: LogicalTime) -> None:
        """Source: Java RTIambassador.java §8.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RequestForTimeRegulationPending, RestoreInProgress, SaveInProgress."""
        ...

    def nextMessageRequest(self, time: LogicalTime) -> None:
        """Source: Java RTIambassador.java §8.10; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RequestForTimeRegulationPending, RestoreInProgress, SaveInProgress."""
        ...

    def nextMessageRequestAvailable(self, time: LogicalTime) -> None:
        """Source: Java RTIambassador.java §8.11; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RequestForTimeRegulationPending, RestoreInProgress, SaveInProgress."""
        ...

    def flushQueueRequest(self, time: LogicalTime) -> None:
        """Source: Java RTIambassador.java §8.12; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RequestForTimeRegulationPending, RestoreInProgress, SaveInProgress."""
        ...

    def enableAsynchronousDelivery(self) -> None:
        """Source: Java RTIambassador.java §8.15; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AsynchronousDeliveryAlreadyEnabled, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def disableAsynchronousDelivery(self) -> None:
        """Source: Java RTIambassador.java §8.16; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AsynchronousDeliveryAlreadyDisabled, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def queryGALT(self) -> TimeQueryReturn:
        """Source: Java RTIambassador.java §8.17; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def queryLogicalTime(self) -> LogicalTime:
        """Source: Java RTIambassador.java §8.18; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def queryLITS(self) -> TimeQueryReturn:
        """Source: Java RTIambassador.java §8.19; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def modifyLookahead(self, lookahead: LogicalTimeInterval) -> None:
        """Source: Java RTIambassador.java §8.20; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InTimeAdvancingState, InvalidLookahead, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeRegulationIsNotEnabled."""
        ...

    def queryLookahead(self) -> LogicalTimeInterval:
        """Source: Java RTIambassador.java §8.21; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeRegulationIsNotEnabled."""
        ...

    def retract(self, retraction: MessageRetractionHandle) -> None:
        """Source: Java RTIambassador.java §8.22; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidMessageRetractionHandle, MessageCanNoLongerBeRetracted, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeRegulationIsNotEnabled."""
        ...

    def changeAttributeOrderType(self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet, orderType: OrderType) -> None:
        """Source: Java RTIambassador.java §8.24; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def changeDefaultAttributeOrderType(self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet, orderType: OrderType) -> None:
        """Source: Java RTIambassador.java §8.25; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def changeInteractionOrderType(self, interactionClass: InteractionClassHandle, orderType: OrderType) -> None:
        """Source: Java RTIambassador.java §8.26; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle:
        """Source: Java RTIambassador.java §9.2; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidDimensionHandle, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def commitRegionModifications(self, regions: RegionHandleSet) -> None:
        """Source: Java RTIambassador.java §9.3; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def deleteRegion(self, region: RegionHandle) -> None:
        """Source: Java RTIambassador.java §9.4; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RegionInUseForUpdateOrSubscription, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §9.5; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: AttributeNotDefined, AttributeNotPublished, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, NotConnected, ObjectClassNotDefined, ObjectClassNotPublished, ObjectInstanceNameInUse, ObjectInstanceNameNotReserved, RTIinternalError, RegionNotCreatedByThisFederate; ….
    @overload
    def registerObjectInstanceWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> ObjectInstanceHandle: ...
    @overload
    def registerObjectInstanceWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, objectInstanceName: str) -> ObjectInstanceHandle: ...

    def associateRegionsForUpdates(self, objectInstance: ObjectInstanceHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None:
        """Source: Java RTIambassador.java §9.6; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def unassociateRegionsForUpdates(self, objectInstance: ObjectInstanceHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None:
        """Source: Java RTIambassador.java §9.7; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §9.8; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, InvalidUpdateRateDesignator, NotConnected, ObjectClassNotDefined, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress.
    @overload
    def subscribeObjectClassAttributesWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None: ...
    @overload
    def subscribeObjectClassAttributesWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, updateRateDesignator: str) -> None: ...

    # Source: Java RTIambassador.java §9.8; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 0. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, InvalidUpdateRateDesignator, NotConnected, ObjectClassNotDefined, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress.
    @overload
    def subscribeObjectClassAttributesPassivelyWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None: ...
    @overload
    def subscribeObjectClassAttributesPassivelyWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, updateRateDesignator: str) -> None: ...

    def unsubscribeObjectClassAttributesWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None:
        """Source: Java RTIambassador.java §9.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, NotConnected, ObjectClassNotDefined, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def subscribeInteractionClassWithRegions(self, interactionClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        """Source: Java RTIambassador.java §9.10; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, InvalidRegion, InvalidRegionContext, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def subscribeInteractionClassPassivelyWithRegions(self, interactionClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        """Source: Java RTIambassador.java §9.10; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, InvalidRegion, InvalidRegionContext, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def unsubscribeInteractionClassWithRegions(self, interactionClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        """Source: Java RTIambassador.java §9.11; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, InvalidRegion, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    # Source: Java RTIambassador.java §9.12; C++ RTIambassador.h. Java overloads: 2; C++ overloads: 2. Java throws: FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, InteractionParameterNotDefined, InvalidLogicalTime, InvalidRegion, InvalidRegionContext, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress.
    @overload
    def sendInteractionWithRegions(self, interactionClass: InteractionClassHandle, parameterValues: ParameterHandleValueMap, regions: RegionHandleSet, userSuppliedTag: bytes) -> None: ...
    @overload
    def sendInteractionWithRegions(self, interactionClass: InteractionClassHandle, parameterValues: ParameterHandleValueMap, regions: RegionHandleSet, userSuppliedTag: bytes, time: LogicalTime) -> MessageRetractionReturn: ...

    def requestAttributeValueUpdateWithRegions(self, objectClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, userSuppliedTag: bytes) -> None:
        """Source: Java RTIambassador.java §9.13; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, NotConnected, ObjectClassNotDefined, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def getFederateHandle(self, federateName: str) -> FederateHandle:
        """Source: Java RTIambassador.java §10.2; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError."""
        ...

    def getFederateName(self, federate: FederateHandle) -> str:
        """Source: Java RTIambassador.java §10.3; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateHandleNotKnown, FederateNotExecutionMember, InvalidFederateHandle, NotConnected, RTIinternalError."""
        ...

    def getObjectClassHandle(self, objectClassName: str) -> ObjectClassHandle:
        """Source: Java RTIambassador.java §10.4; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError."""
        ...

    def getObjectClassName(self, objectClass: ObjectClassHandle) -> str:
        """Source: Java RTIambassador.java §10.5; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidObjectClassHandle, NotConnected, RTIinternalError."""
        ...

    def getKnownObjectClassHandle(self, objectInstance: ObjectInstanceHandle) -> ObjectClassHandle:
        """Source: Java RTIambassador.java §10.6; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError."""
        ...

    def getObjectInstanceHandle(self, objectInstanceName: str) -> ObjectInstanceHandle:
        """Source: Java RTIambassador.java §10.7; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError."""
        ...

    def getObjectInstanceName(self, objectInstance: ObjectInstanceHandle) -> str:
        """Source: Java RTIambassador.java §10.8; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError."""
        ...

    def getAttributeHandle(self, objectClass: ObjectClassHandle, attributeName: str) -> AttributeHandle:
        """Source: Java RTIambassador.java §10.9; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidObjectClassHandle, NameNotFound, NotConnected, RTIinternalError."""
        ...

    def getAttributeName(self, objectClass: ObjectClassHandle, attribute: AttributeHandle) -> str:
        """Source: Java RTIambassador.java §10.10; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, InvalidAttributeHandle, InvalidObjectClassHandle, NotConnected, RTIinternalError."""
        ...

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:
        """Source: Java RTIambassador.java §10.11; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidUpdateRateDesignator, NotConnected, RTIinternalError."""
        ...

    def getUpdateRateValueForAttribute(self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle) -> float:
        """Source: Java RTIambassador.java §10.12; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError."""
        ...

    def getInteractionClassHandle(self, interactionClassName: str) -> InteractionClassHandle:
        """Source: Java RTIambassador.java §10.13; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError."""
        ...

    def getInteractionClassName(self, interactionClass: InteractionClassHandle) -> str:
        """Source: Java RTIambassador.java §10.14; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidInteractionClassHandle, NotConnected, RTIinternalError."""
        ...

    def getParameterHandle(self, interactionClass: InteractionClassHandle, parameterName: str) -> ParameterHandle:
        """Source: Java RTIambassador.java §10.15; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidInteractionClassHandle, NameNotFound, NotConnected, RTIinternalError."""
        ...

    def getParameterName(self, interactionClass: InteractionClassHandle, parameter: ParameterHandle) -> str:
        """Source: Java RTIambassador.java §10.16; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InteractionParameterNotDefined, InvalidInteractionClassHandle, InvalidParameterHandle, NotConnected, RTIinternalError."""
        ...

    def getOrderType(self, orderTypeName: str) -> OrderType:
        """Source: Java RTIambassador.java §10.17; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidOrderName, NotConnected, RTIinternalError."""
        ...

    def getOrderName(self, orderType: OrderType) -> str:
        """Source: Java RTIambassador.java §10.18; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidOrderType, NotConnected, RTIinternalError."""
        ...

    def getTransportationTypeHandle(self, transportationTypeName: str) -> TransportationTypeHandle:
        """Source: Java RTIambassador.java §10.19; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidTransportationName, NotConnected, RTIinternalError."""
        ...

    def getTransportationTypeName(self, transportationType: TransportationTypeHandle) -> str:
        """Source: Java RTIambassador.java §10.20; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidTransportationTypeHandle, NotConnected, RTIinternalError."""
        ...

    def getAvailableDimensionsForObjectClass(self, objectClass: ObjectClassHandle) -> DimensionHandleSet:
        """Source: Java RTIambassador.java §10.21; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidObjectClassHandle, NotConnected, RTIinternalError."""
        ...

    def getAvailableDimensionsForInteractionClass(self, interactionClass: InteractionClassHandle) -> DimensionHandleSet:
        """Source: Java RTIambassador.java §10.22; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidInteractionClassHandle, NotConnected, RTIinternalError."""
        ...

    def getDimensionHandle(self, dimensionName: str) -> DimensionHandle:
        """Source: Java RTIambassador.java §10.23; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError."""
        ...

    def getDimensionName(self, dimension: DimensionHandle) -> str:
        """Source: Java RTIambassador.java §10.24; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidDimensionHandle, NotConnected, RTIinternalError."""
        ...

    def getDimensionUpperBound(self, dimension: DimensionHandle) -> int:
        """Source: Java RTIambassador.java §10.25; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidDimensionHandle, NotConnected, RTIinternalError."""
        ...

    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet:
        """Source: Java RTIambassador.java §10.26; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getRangeBounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:
        """Source: Java RTIambassador.java §10.27; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RegionDoesNotContainSpecifiedDimension, RestoreInProgress, SaveInProgress."""
        ...

    def setRangeBounds(self, region: RegionHandle, dimension: DimensionHandle, rangeBounds: RangeBounds) -> None:
        """Source: Java RTIambassador.java §10.28; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidRangeBound, InvalidRegion, NotConnected, RTIinternalError, RegionDoesNotContainSpecifiedDimension, RegionNotCreatedByThisFederate, RestoreInProgress, SaveInProgress."""
        ...

    def normalizeServiceGroup(self, serviceGroup: ServiceGroup) -> int:
        """Source: Java RTIambassador.java §10.29; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidServiceGroup, NotConnected, RTIinternalError."""
        ...

    def normalizeFederateHandle(self, federate: FederateHandle) -> int:
        """Source: Java RTIambassador.java §10.30; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidFederateHandle, NotConnected, RTIinternalError."""
        ...

    def normalizeObjectClassHandle(self, objectClass: ObjectClassHandle) -> int:
        """Source: Java RTIambassador.java §10.31; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidObjectClassHandle, NotConnected, RTIinternalError."""
        ...

    def normalizeInteractionClassHandle(self, interactionClass: InteractionClassHandle) -> int:
        """Source: Java RTIambassador.java §10.32; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidInteractionClassHandle, NotConnected, RTIinternalError."""
        ...

    def normalizeObjectInstanceHandle(self, objectInstance: ObjectInstanceHandle) -> int:
        """Source: Java RTIambassador.java §10.33; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, InvalidObjectInstanceHandle, NotConnected, RTIinternalError."""
        ...

    def getObjectClassRelevanceAdvisorySwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.34; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setObjectClassRelevanceAdvisorySwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.35; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAttributeRelevanceAdvisorySwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.36; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setAttributeRelevanceAdvisorySwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.37; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAttributeScopeAdvisorySwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.38; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setAttributeScopeAdvisorySwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.39; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getInteractionRelevanceAdvisorySwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.40; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setInteractionRelevanceAdvisorySwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.41; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getConveyRegionDesignatorSetsSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.42; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setConveyRegionDesignatorSetsSwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.43; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAutomaticResignDirective(self) -> ResignAction:
        """Source: Java RTIambassador.java §10.44; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setAutomaticResignDirective(self, value: ResignAction) -> None:
        """Source: Java RTIambassador.java §10.45; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getServiceReportingSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.46; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setServiceReportingSwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.47; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, ReportServiceInvocationsAreSubscribed, RestoreInProgress, SaveInProgress."""
        ...

    def getExceptionReportingSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.48; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setExceptionReportingSwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.49; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getSendServiceReportsToFileSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.50; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def setSendServiceReportsToFileSwitch(self, value: bool) -> None:
        """Source: Java RTIambassador.java §10.51; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAutoProvideSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.52; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getDelaySubscriptionEvaluationSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.53; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAdvisoriesUseKnownClassSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.54; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAllowRelaxedDDMSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.55; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getNonRegulatedGrantSwitch(self) -> bool:
        """Source: Java RTIambassador.java §10.56; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        """Source: Java RTIambassador.java §10.57; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: CallNotAllowedFromWithinCallback, RTIinternalError."""
        ...

    def evokeMultipleCallbacks(self, approximateMinimumTimeInSeconds: float, approximateMaximumTimeInSeconds: float) -> bool:
        """Source: Java RTIambassador.java §10.58; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: CallNotAllowedFromWithinCallback, RTIinternalError."""
        ...

    def enableCallbacks(self) -> None:
        """Source: Java RTIambassador.java §10.59; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def disableCallbacks(self) -> None:
        """Source: Java RTIambassador.java §10.60; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: RTIinternalError, RestoreInProgress, SaveInProgress."""
        ...

    def getAttributeHandleFactory(self) -> AttributeHandleFactory:
        """Source: Java RTIambassador.java §10.60; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:
        """Source: Java RTIambassador.java §10.60; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:
        """Source: Java RTIambassador.java §10.60; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:
        """Source: Java RTIambassador.java §10.60; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getDimensionHandleFactory(self) -> DimensionHandleFactory:
        """Source: Java RTIambassador.java §10.60; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getFederateHandleFactory(self) -> FederateHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getInteractionClassHandleSetFactory(self) -> InteractionClassHandleSetFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getParameterHandleFactory(self) -> ParameterHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getRegionHandleFactory(self) -> RegionHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getMessageRetractionHandleFactory(self) -> MessageRetractionHandleFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: FederateNotExecutionMember, NotConnected."""
        ...

    def getHLAversion(self) -> str:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 0. Java throws: not declared in Java source."""
        ...

    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeInteractionClassHandle(self, encodedValue: bytes) -> InteractionClassHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeObjectInstanceHandle(self, encodedValue: bytes) -> ObjectInstanceHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeMessageRetractionHandle(self, encodedValue: bytes) -> MessageRetractionHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 0; C++ overloads: 1. Java throws: not declared in Java source."""
        ...

    def getTimeFactory(self) -> LogicalTimeFactory:
        """Source: Java RTIambassador.java n/a; C++ RTIambassador.h. Java overloads: 1; C++ overloads: 1. Java throws: FederateNotExecutionMember, NotConnected."""
        ...


class UnimplementedRTIambassador(RTIambassador):
    """Concrete scaffold mirroring RTIambassador; runtime implementation raises/notifies as in the .py module."""
    ...
