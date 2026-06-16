"""RTIambassador model for IEEE 1516.1-2025.

Sources: Java RTIambassador.java and C++ RTIambassador.h.
"""

from typing import Protocol, Sequence, Set

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
    """Runtime protocol surface for the RTI ambassador.

For strict overloads and per-method source trace, see
rti_ambassador.pyi and requirements/2025/SOURCE_TRACE.md.
"""

    # ========= Federation Management Services =========
    def connect(
        self,
        federateAmbassador: FederateAmbassador,
        callbackModel: CallbackModel,
        configuration: RtiConfiguration | None = None,
        credentials: Credentials | None = None,
    ) -> ConfigurationResult: ...

    def disconnect(self) -> None: ...

    def createFederationExecution(
        self,
        federationName: str,
        fomModule: str | None = None,
        fomModules: Sequence[str] | None = None,
        logicalTimeImplementationName: str | None = None,
    ) -> None: ...

    def createFederationExecutionWithMIM(
        self,
        federationName: str,
        fomModules: Sequence[str],
        mimModule: str,
        logicalTimeImplementationName: str | None = None,
    ) -> None: ...

    def destroyFederationExecution(self, federationName: str) -> None: ...

    def listFederationExecutions(self) -> None: ...

    def listFederationExecutionMembers(self, federationName: str) -> None: ...

    # the overloads for this one are really terrible so we will force kwarg
    def joinFederationExecution(
        self,
        *,
        federateType: str,
        federateName: str | None = None,
        federationName: str,
        additionalFomModules: Sequence[str] | None = None,
    ) -> FederateHandle: ...

    def resignFederationExecution(self, resignAction: ResignAction) -> None: ...

    def registerFederationSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: bytes,
        synchronizationSet: FederateHandleSet | None = None,
    ) -> None: ...

    def synchronizationPointAchieved(
        self, synchronizationPointLabel: str, successfully: bool = True
    ) -> None: ...

    def requestFederationSave(
        self, label: str, time: LogicalTime | None = None
    ) -> None: ...

    def federateSaveBegun(self) -> None: ...

    def federateSaveComplete(self) -> None: ...

    def federateSaveNotComplete(self) -> None: ...

    def abortFederationSave(self) -> None: ...

    def queryFederationSaveStatus(self) -> None: ...

    def requestFederationRestore(self, label: str) -> None: ...

    def federateRestoreComplete(self) -> None: ...

    def federateRestoreNotComplete(self) -> None: ...

    def abortFederationRestore(self) -> None: ...

    def queryFederationRestoreStatus(self) -> None: ...

    # ========= Declaration Management Services =========

    def publishObjectClassAttributes(
        self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def unpublishObjectClass(self, objectClass: ObjectClassHandle) -> None: ...

    def unpublishObjectClassAttributes(
        self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def publishInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None: ...

    def unpublishInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None: ...

    def publishObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet,
    ) -> None: ...

    def unpublishObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet | None = None,
    ) -> None: ...

    def subscribeObjectClassAttributes(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None: ...

    # not in C++
    def subscribeObjectClassAttributesPassively(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None: ...

    def unsubscribeObjectClass(self, objectClass: ObjectClassHandle) -> None: ...

    def unsubscribeObjectClassAttributes(
        self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def subscribeInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None: ...

    # not in C++
    def subscribeInteractionClassPassively(
        self, interactionClass: InteractionClassHandle
    ) -> None: ...

    def unsubscribeInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None: ...

    def subscribeObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet,
    ) -> None: ...

    # not in C++
    def subscribeObjectClassDirectedInteractionsUniversally(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet,
    ) -> None: ...

    def unsubscribeObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet | None = None,
    ) -> None: ...

    # ========= Object Management =========

    def reserveObjectInstanceName(self, objectInstanceName: str) -> None: ...

    def releaseObjectInstanceName(self, objectInstanceName: str) -> None: ...

    def reserveMultipleObjectInstanceNames(
        self, objectInstanceNames: Set[str]
    ) -> None: ...

    def releaseMultipleObjectInstanceNames(
        self, objectInstanceNames: Set[str]
    ) -> None: ...

    def registerObjectInstance(
        self, objectClass: ObjectClassHandle, objectInstanceName: str | None = None
    ) -> ObjectInstanceHandle: ...

    def updateAttributeValues(
        self,
        objectInstance: ObjectInstanceHandle,
        attributeValues: AttributeHandleValueMap,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None: ...

    def sendInteraction(
        self,
        interactionClass: InteractionClassHandle,
        parameterValues: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None: ...

    def sendDirectedInteraction(
        self,
        interactionClass: InteractionClassHandle,
        objectInstance: ObjectInstanceHandle,
        parameterValues: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None: ...

    def deleteObjectInstance(
        self,
        objectInstance: ObjectInstanceHandle,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None: ...

    def localDeleteObjectInstance(
        self, objectInstance: ObjectInstanceHandle
    ) -> None: ...

    def requestAttributeValueUpdate(
        self,
        objectClassOrInstance: ObjectClassHandle | ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def requestAttributeTransportationTypeChange(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def changeDefaultAttributeTransportationType(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def queryAttributeTransportationType(
        self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle
    ) -> None: ...

    def requestInteractionTransportationTypeChange(
        self,
        interactionClass: InteractionClassHandle,
        transportationType: TransportationTypeHandle,
    ) -> None: ...

    def queryInteractionTransportationType(
        self, federate: FederateHandle, interactionClass: InteractionClassHandle
    ) -> None: ...

    # ========= Ownership Management =========

    def unconditionalAttributeOwnershipDivestiture(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def negotiatedAttributeOwnershipDivestiture(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def confirmDivestiture(
        self,
        objectInstance: ObjectInstanceHandle,
        confirmedAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def attributeOwnershipAcquisition(
        self,
        objectInstance: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def attributeOwnershipAcquisitionIfAvailable(
        self,
        objectInstance: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def attributeOwnershipReleaseDenied(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None: ...

    def attributeOwnershipDivestitureIfWanted(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> AttributeHandleSet: ...

    def cancelNegotiatedAttributeOwnershipDivestiture(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def cancelAttributeOwnershipAcquisition(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def queryAttributeOwnership(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None: ...

    def isAttributeOwnedByFederate(
        self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle
    ) -> bool: ...

    # ========= Time Management =========

    def enableTimeRegulation(self, lookahead: LogicalTimeInterval) -> None: ...
    def disableTimeRegulation(self) -> None: ...

    def enableTimeConstrained(self) -> None: ...
    def disableTimeConstrained(self) -> None: ...

    def timeAdvanceRequest(self, time: LogicalTime) -> None: ...
    def timeAdvanceRequestAvailable(self, time: LogicalTime) -> None: ...
    def nextMessageRequest(self, time: LogicalTime) -> None: ...
    def nextMessageRequestAvailable(self, time: LogicalTime) -> None: ...
    def flushQueueRequest(self, time: LogicalTime) -> None: ...

    def enableAsynchronousDelivery(self) -> None: ...
    def disableAsynchronousDelivery(self) -> None: ...

    # in C++ this simply returns a logical time by ref
    def queryGALT(self) -> TimeQueryReturn: ...
    def queryLogicalTime(self) -> LogicalTime: ...
    def queryLITS(self) -> TimeQueryReturn: ...

    def modifyLookahead(self, lookahead: LogicalTimeInterval) -> None: ...
    def queryLookahead(self) -> LogicalTimeInterval: ...

    def retract(self, retraction: MessageRetractionHandle) -> None: ...

    def changeAttributeOrderType(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        orderType: OrderType,
    ) -> None: ...

    def changeDefaultAttributeOrderType(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        orderType: OrderType,
    ) -> None: ...

    def changeInteractionOrderType(
        self, interactionClass: InteractionClassHandle, orderType: OrderType
    ) -> None: ...

    # ========= Data Distribution Management =========

    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle: ...

    def commitRegionModifications(self, regions: RegionHandleSet) -> None: ...

    def deleteRegion(self, region: RegionHandle) -> None: ...

    def registerObjectInstanceWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        objectInstanceName: str | None = None,
    ) -> ObjectInstanceHandle: ...

    def associateRegionsForUpdates(
        self,
        objectInstance: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None: ...

    def unassociateRegionsForUpdates(
        self,
        objectInstance: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None: ...

    def subscribeObjectClassAttributesWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None,
    ) -> None: ...

    # not in C++
    def subscribeObjectClassAttributesPassivelyWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None
    ) -> None: ...

    def unsubscribeObjectClassAttributesWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None: ...

    def subscribeInteractionClassWithRegions(
        self, interactionClass: InteractionClassHandle, regions: RegionHandleSet
    ) -> None: ...

    # not in C++
    def subscribeInteractionClassPassivelyWithRegions(
        self, interactionClass: InteractionClassHandle, regions: RegionHandleSet
    ) -> None: ...

    def unsubscribeInteractionClassWithRegions(
        self, interactionClass: InteractionClassHandle, regions: RegionHandleSet
    ) -> None: ...

    def sendInteractionWithRegions(
        self,
        interactionClass: InteractionClassHandle,
        parameterValues: ParameterHandleValueMap,
        regions: RegionHandleSet,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None: ...

    def requestAttributeValueUpdateWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        userSuppliedTag: bytes,
    ) -> None: ...

    # ========= Support Services =========

    def getFederateHandle(self, federateName: str) -> FederateHandle: ...
    def getFederateName(self, federate: FederateHandle) -> str: ...

    def getObjectClassHandle(self, objectClassName: str) -> ObjectClassHandle: ...
    def getObjectClassName(self, objectClass: ObjectClassHandle) -> str: ...

    def getKnownObjectClassHandle(
        self, objectInstance: ObjectInstanceHandle
    ) -> ObjectClassHandle: ...

    def getObjectInstanceHandle(
        self, objectInstanceName: str
    ) -> ObjectInstanceHandle: ...
    def getObjectInstanceName(self, objectInstance: ObjectInstanceHandle) -> str: ...

    def getAttributeHandle(
        self, objectClass: ObjectClassHandle, attributeName: str
    ) -> AttributeHandle: ...
    def getAttributeName(
        self, objectClass: ObjectClassHandle, attribute: AttributeHandle
    ) -> str: ...

    def getUpdateRateValue(self, updateRateDesignator: str) -> float: ...
    def getUpdateRateValueForAttribute(
        self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle
    ) -> float: ...

    def getInteractionClassHandle(
        self, interactionClassName: str
    ) -> InteractionClassHandle: ...
    def getInteractionClassName(
        self, interactionClass: InteractionClassHandle
    ) -> str: ...

    def getParameterHandle(
        self, interactionClass: InteractionClassHandle, parameterName: str
    ) -> ParameterHandle: ...

    def getParameterName(
        self, interactionClass: InteractionClassHandle, parameter: ParameterHandle
    ) -> str: ...

    def getOrderType(self, orderTypeName: str) -> OrderType: ...
    def getOrderName(self, orderType: OrderType) -> str: ...

    def getTransportationTypeHandle(
        self, transportationTypeName: str
    ) -> TransportationTypeHandle: ...
    def getTransportationTypeName(
        self, transportationType: TransportationTypeHandle
    ) -> str: ...

    def getAvailableDimensionsForObjectClass(
        self, objectClass: ObjectClassHandle
    ) -> DimensionHandleSet: ...
    def getAvailableDimensionsForInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> DimensionHandleSet: ...

    def getDimensionHandle(self, dimensionName: str) -> DimensionHandle: ...
    def getDimensionName(self, dimension: DimensionHandle) -> str: ...

    def getDimensionUpperBound(self, dimension: DimensionHandle) -> int: ...

    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet: ...

    def getRangeBounds(
        self, region: RegionHandle, dimension: DimensionHandle
    ) -> RangeBounds: ...

    def setRangeBounds(
        self, region: RegionHandle, dimension: DimensionHandle, rangeBounds: RangeBounds
    ) -> None: ...

    def normalizeServiceGroup(self, serviceGroup: ServiceGroup) -> int: ...

    def normalizeFederateHandle(self, federate: FederateHandle) -> int: ...
    def normalizeObjectClassHandle(self, objectClass: ObjectClassHandle) -> int: ...
    def normalizeInteractionClassHandle(
        self, interactionClass: InteractionClassHandle
    ) -> int: ...
    def normalizeObjectInstanceHandle(
        self, objectInstance: ObjectInstanceHandle
    ) -> int: ...

    def getObjectClassRelevanceAdvisorySwitch(self) -> bool: ...
    def setObjectClassRelevanceAdvisorySwitch(self, value: bool) -> None: ...
    def getAttributeRelevanceAdvisorySwitch(self) -> bool: ...
    def setAttributeRelevanceAdvisorySwitch(self, value: bool) -> None: ...
    def getAttributeScopeAdvisorySwitch(self) -> bool: ...
    def setAttributeScopeAdvisorySwitch(self, value: bool) -> None: ...
    def getInteractionRelevanceAdvisorySwitch(self) -> bool: ...
    def setInteractionRelevanceAdvisorySwitch(self, value: bool) -> None: ...
    def getConveyRegionDesignatorSetsSwitch(self) -> bool: ...
    def setConveyRegionDesignatorSetsSwitch(self, value: bool) -> None: ...
    def getAutomaticResignDirective(self) -> ResignAction: ...
    def setAutomaticResignDirective(self, value: ResignAction) -> None: ...
    def getServiceReportingSwitch(self) -> bool: ...
    def setServiceReportingSwitch(self, value: bool) -> None: ...
    def getExceptionReportingSwitch(self) -> bool: ...
    def setExceptionReportingSwitch(self, value: bool) -> None: ...
    def getSendServiceReportsToFileSwitch(self) -> bool: ...
    def setSendServiceReportsToFileSwitch(self, value: bool) -> None: ...
    def getAutoProvideSwitch(self) -> bool: ...
    def getDelaySubscriptionEvaluationSwitch(self) -> bool: ...
    def getAdvisoriesUseKnownClassSwitch(self) -> bool: ...
    def getAllowRelaxedDDMSwitch(self) -> bool: ...
    def getNonRegulatedGrantSwitch(self) -> bool: ...

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool: ...
    def evokeMultipleCallbacks(
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool: ...
    def enableCallbacks(self) -> None: ...
    def disableCallbacks(self) -> None: ...

    # Java API-specific services
    def getAttributeHandleFactory(self) -> AttributeHandleFactory: ...
    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory: ...
    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory: ...
    def getAttributeSetRegionSetPairListFactory(
        self,
    ) -> AttributeSetRegionSetPairListFactory: ...
    def getDimensionHandleFactory(self) -> DimensionHandleFactory: ...
    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory: ...
    def getFederateHandleFactory(self) -> FederateHandleFactory: ...
    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory: ...
    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory: ...
    def getInteractionClassHandleSetFactory(
        self,
    ) -> InteractionClassHandleSetFactory: ...
    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory: ...
    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory: ...
    def getParameterHandleFactory(self) -> ParameterHandleFactory: ...
    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory: ...
    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory: ...
    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory: ...
    def getRegionHandleFactory(self) -> RegionHandleFactory: ...
    def getMessageRetractionHandleFactory(self) -> MessageRetractionHandleFactory: ...
    def getHLAversion(self) -> str: ...

    # C++ API-specific services
    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle: ...
    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle: ...
    def decodeInteractionClassHandle(
        self, encodedValue: bytes
    ) -> InteractionClassHandle: ...
    def decodeObjectInstanceHandle(
        self, encodedValue: bytes
    ) -> ObjectInstanceHandle: ...
    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle: ...
    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle: ...
    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle: ...
    def decodeMessageRetractionHandle(
        self, encodedValue: bytes
    ) -> MessageRetractionHandle: ...
    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle: ...

    # C++ and Java services
    def getTimeFactory(self) -> LogicalTimeFactory: ...


class UnimplementedRTIambassador(RTIambassador):

    # ========= Federation Management Services =========

    def connect(
        self,
        federateAmbassador: FederateAmbassador,
        callbackModel: CallbackModel,
        configuration: RtiConfiguration | None = None,
        credentials: Credentials | None = None,
    ) -> ConfigurationResult:
        raise NotImplementedError()

    def disconnect(self) -> None:
        raise NotImplementedError()

    def createFederationExecution(
        self,
        federationName: str,
        fomModule: str | None = None,
        fomModules: Sequence[str] | None = None,
        logicalTimeImplementationName: str | None = None,
    ) -> None:
        raise NotImplementedError()

    def createFederationExecutionWithMIM(
        self,
        federationName: str,
        fomModules: Sequence[str],
        mimModule: str,
        logicalTimeImplementationName: str | None = None,
    ) -> None:
        raise NotImplementedError()

    def destroyFederationExecution(self, federationName: str) -> None:
        raise NotImplementedError()

    def listFederationExecutions(self) -> None:
        raise NotImplementedError()

    def listFederationExecutionMembers(self, federationName: str) -> None:
        raise NotImplementedError()

    def joinFederationExecution(
        self,
        *,
        federateType: str,
        federateName: str | None = None,
        federationName: str,
        additionalFomModules: Sequence[str] | None = None,
    ) -> FederateHandle:
        raise NotImplementedError()

    def resignFederationExecution(self, resignAction: ResignAction) -> None:
        raise NotImplementedError()

    def registerFederationSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: bytes,
        synchronizationSet: FederateHandleSet | None = None,
    ) -> None:
        raise NotImplementedError()

    def synchronizationPointAchieved(
        self, synchronizationPointLabel: str, successfully: bool = True
    ) -> None:
        raise NotImplementedError()

    def requestFederationSave(
        self, label: str, time: LogicalTime | None = None
    ) -> None:
        raise NotImplementedError()

    def federateSaveBegun(self) -> None:
        raise NotImplementedError()

    def federateSaveComplete(self) -> None:
        raise NotImplementedError()

    def federateSaveNotComplete(self) -> None:
        raise NotImplementedError()

    def abortFederationSave(self) -> None:
        raise NotImplementedError()

    def queryFederationSaveStatus(self) -> None:
        raise NotImplementedError()

    def requestFederationRestore(self, label: str) -> None:
        raise NotImplementedError()

    def federateRestoreComplete(self) -> None:
        raise NotImplementedError()

    def federateRestoreNotComplete(self) -> None:
        raise NotImplementedError()

    def abortFederationRestore(self) -> None:
        raise NotImplementedError()

    def queryFederationRestoreStatus(self) -> None:
        raise NotImplementedError()

    # ========= Declaration Management Services =========

    def publishObjectClassAttributes(
        self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet
    ) -> None:
        raise NotImplementedError()

    def unpublishObjectClass(self, objectClass: ObjectClassHandle) -> None:
        raise NotImplementedError()

    def unpublishObjectClassAttributes(
        self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet
    ) -> None:
        raise NotImplementedError()

    def publishInteractionClass(self, interactionClass: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def unpublishInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None:
        raise NotImplementedError()

    def publishObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet,
    ) -> None:
        raise NotImplementedError()

    def unpublishObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet | None = None,
    ) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributes(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:
        raise NotImplementedError()

    # not in C++
    def subscribeObjectClassAttributesPassively(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClass(self, objectClass: ObjectClassHandle) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassAttributes(
        self, objectClass: ObjectClassHandle, attributes: AttributeHandleSet
    ) -> None:
        raise NotImplementedError()

    def subscribeInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None:
        raise NotImplementedError()

    # not in C++
    def subscribeInteractionClassPassively(
        self, interactionClass: InteractionClassHandle
    ) -> None:
        raise NotImplementedError()

    def unsubscribeInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> None:
        raise NotImplementedError()

    def subscribeObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet,
    ) -> None:
        raise NotImplementedError()

    # not in C++
    def subscribeObjectClassDirectedInteractionsUniversally(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet,
    ) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassDirectedInteractions(
        self,
        objectClass: ObjectClassHandle,
        interactionClasses: InteractionClassHandleSet | None = None,
    ) -> None:
        raise NotImplementedError()

    # ========= Object Management =========

    def reserveObjectInstanceName(self, objectInstanceName: str) -> None:
        raise NotImplementedError()

    def releaseObjectInstanceName(self, objectInstanceName: str) -> None:
        raise NotImplementedError()

    def reserveMultipleObjectInstanceNames(self, objectInstanceNames: Set[str]) -> None:
        raise NotImplementedError()

    def releaseMultipleObjectInstanceNames(self, objectInstanceNames: Set[str]) -> None:
        raise NotImplementedError()

    def registerObjectInstance(
        self, objectClass: ObjectClassHandle, objectInstanceName: str | None = None
    ) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def updateAttributeValues(
        self,
        objectInstance: ObjectInstanceHandle,
        attributeValues: AttributeHandleValueMap,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def sendInteraction(
        self,
        interactionClass: InteractionClassHandle,
        parameterValues: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def sendDirectedInteraction(
        self,
        interactionClass: InteractionClassHandle,
        objectInstance: ObjectInstanceHandle,
        parameterValues: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def deleteObjectInstance(
        self,
        objectInstance: ObjectInstanceHandle,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def localDeleteObjectInstance(self, objectInstance: ObjectInstanceHandle) -> None:
        raise NotImplementedError()

    def requestAttributeValueUpdate(
        self,
        objectClassOrInstance: ObjectClassHandle | ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def requestAttributeTransportationTypeChange(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        transportationType: TransportationTypeHandle,
    ) -> None:
        raise NotImplementedError()

    def changeDefaultAttributeTransportationType(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        transportationType: TransportationTypeHandle,
    ) -> None:
        raise NotImplementedError()

    def queryAttributeTransportationType(
        self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle
    ) -> None:
        raise NotImplementedError()

    def requestInteractionTransportationTypeChange(
        self,
        interactionClass: InteractionClassHandle,
        transportationType: TransportationTypeHandle,
    ) -> None:
        raise NotImplementedError()

    def queryInteractionTransportationType(
        self, federate: FederateHandle, interactionClass: InteractionClassHandle
    ) -> None:
        raise NotImplementedError()

    # ========= Ownership Management =========

    def unconditionalAttributeOwnershipDivestiture(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def negotiatedAttributeOwnershipDivestiture(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def confirmDivestiture(
        self,
        objectInstance: ObjectInstanceHandle,
        confirmedAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisition(
        self,
        objectInstance: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisitionIfAvailable(
        self,
        objectInstance: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def attributeOwnershipReleaseDenied(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    def attributeOwnershipDivestitureIfWanted(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> AttributeHandleSet:
        raise NotImplementedError()

    def cancelNegotiatedAttributeOwnershipDivestiture(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None:
        raise NotImplementedError()

    def cancelAttributeOwnershipAcquisition(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None:
        raise NotImplementedError()

    def queryAttributeOwnership(
        self, objectInstance: ObjectInstanceHandle, attributes: AttributeHandleSet
    ) -> None:
        raise NotImplementedError()

    def isAttributeOwnedByFederate(
        self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle
    ) -> bool:
        raise NotImplementedError()

    # ========= Time Management =========

    def enableTimeRegulation(self, lookahead: LogicalTimeInterval) -> None:
        raise NotImplementedError()

    def disableTimeRegulation(self) -> None:
        raise NotImplementedError()

    def enableTimeConstrained(self) -> None:
        raise NotImplementedError()

    def disableTimeConstrained(self) -> None:
        raise NotImplementedError()

    def timeAdvanceRequest(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def timeAdvanceRequestAvailable(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def nextMessageRequest(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def nextMessageRequestAvailable(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def flushQueueRequest(self, time: LogicalTime) -> None:
        raise NotImplementedError()

    def enableAsynchronousDelivery(self) -> None:
        raise NotImplementedError()

    def disableAsynchronousDelivery(self) -> None:
        raise NotImplementedError()

    # in C++ this simply returns a logical time by ref
    def queryGALT(self) -> TimeQueryReturn:
        raise NotImplementedError()

    def queryLogicalTime(self) -> LogicalTime:
        raise NotImplementedError()

    def queryLITS(self) -> TimeQueryReturn:
        raise NotImplementedError()

    def modifyLookahead(self, lookahead: LogicalTimeInterval) -> None:
        raise NotImplementedError()

    def queryLookahead(self) -> LogicalTimeInterval:
        raise NotImplementedError()

    def retract(self, retraction: MessageRetractionHandle) -> None:
        raise NotImplementedError()

    def changeAttributeOrderType(
        self,
        objectInstance: ObjectInstanceHandle,
        attributes: AttributeHandleSet,
        orderType: OrderType,
    ) -> None:
        raise NotImplementedError()

    def changeDefaultAttributeOrderType(
        self,
        objectClass: ObjectClassHandle,
        attributes: AttributeHandleSet,
        orderType: OrderType,
    ) -> None:
        raise NotImplementedError()

    def changeInteractionOrderType(
        self, interactionClass: InteractionClassHandle, orderType: OrderType
    ) -> None:
        raise NotImplementedError()

    # ========= Data Distribution Management =========

    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle:
        raise NotImplementedError()

    def commitRegionModifications(self, regions: RegionHandleSet) -> None:
        raise NotImplementedError()

    def deleteRegion(self, region: RegionHandle) -> None:
        raise NotImplementedError()

    def registerObjectInstanceWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        objectInstanceName: str | None = None,
    ) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def associateRegionsForUpdates(
        self,
        objectInstance: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:
        raise NotImplementedError()

    def unassociateRegionsForUpdates(
        self,
        objectInstance: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None,
    ) -> None:
        raise NotImplementedError()

    # not in C++
    def subscribeObjectClassAttributesPassivelyWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None
    ) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassAttributesWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassWithRegions(
        self, interactionClass: InteractionClassHandle, regions: RegionHandleSet
    ) -> None:
        raise NotImplementedError()

    # not in C++
    def subscribeInteractionClassPassivelyWithRegions(
        self, interactionClass: InteractionClassHandle, regions: RegionHandleSet
    ) -> None:
        raise NotImplementedError()

    def unsubscribeInteractionClassWithRegions(
        self, interactionClass: InteractionClassHandle, regions: RegionHandleSet
    ) -> None:
        raise NotImplementedError()

    def sendInteractionWithRegions(
        self,
        interactionClass: InteractionClassHandle,
        parameterValues: ParameterHandleValueMap,
        regions: RegionHandleSet,
        userSuppliedTag: bytes,
        time: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def requestAttributeValueUpdateWithRegions(
        self,
        objectClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        userSuppliedTag: bytes,
    ) -> None:
        raise NotImplementedError()

    # ========= Support Services =========

    def getFederateHandle(self, federateName: str) -> FederateHandle:
        raise NotImplementedError()

    def getFederateName(self, federate: FederateHandle) -> str:
        raise NotImplementedError()

    def getObjectClassHandle(self, objectClassName: str) -> ObjectClassHandle:
        raise NotImplementedError()

    def getObjectClassName(self, objectClass: ObjectClassHandle) -> str:
        raise NotImplementedError()

    def getKnownObjectClassHandle(
        self, objectInstance: ObjectInstanceHandle
    ) -> ObjectClassHandle:
        raise NotImplementedError()

    def getObjectInstanceHandle(self, objectInstanceName: str) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def getObjectInstanceName(self, objectInstance: ObjectInstanceHandle) -> str:
        raise NotImplementedError()

    def getAttributeHandle(
        self, objectClass: ObjectClassHandle, attributeName: str
    ) -> AttributeHandle:
        raise NotImplementedError()

    def getAttributeName(
        self, objectClass: ObjectClassHandle, attribute: AttributeHandle
    ) -> str:
        raise NotImplementedError()

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:
        raise NotImplementedError()

    def getUpdateRateValueForAttribute(
        self, objectInstance: ObjectInstanceHandle, attribute: AttributeHandle
    ) -> float:
        raise NotImplementedError()

    def getInteractionClassHandle(
        self, interactionClassName: str
    ) -> InteractionClassHandle:
        raise NotImplementedError()

    def getInteractionClassName(self, interactionClass: InteractionClassHandle) -> str:
        raise NotImplementedError()

    def getParameterHandle(
        self, interactionClass: InteractionClassHandle, parameterName: str
    ) -> ParameterHandle:
        raise NotImplementedError()

    def getParameterName(
        self, interactionClass: InteractionClassHandle, parameter: ParameterHandle
    ) -> str:
        raise NotImplementedError()

    def getOrderType(self, orderTypeName: str) -> OrderType:
        raise NotImplementedError()

    def getOrderName(self, orderType: OrderType) -> str:
        raise NotImplementedError()

    def getTransportationTypeHandle(
        self, transportationTypeName: str
    ) -> TransportationTypeHandle:
        raise NotImplementedError()

    def getTransportationTypeName(
        self, transportationType: TransportationTypeHandle
    ) -> str:
        raise NotImplementedError()

    def getAvailableDimensionsForObjectClass(
        self, objectClass: ObjectClassHandle
    ) -> DimensionHandleSet:
        raise NotImplementedError()

    def getAvailableDimensionsForInteractionClass(
        self, interactionClass: InteractionClassHandle
    ) -> DimensionHandleSet:
        raise NotImplementedError()

    def getDimensionHandle(self, dimensionName: str) -> DimensionHandle:
        raise NotImplementedError()

    def getDimensionName(self, dimension: DimensionHandle) -> str:
        raise NotImplementedError()

    def getDimensionUpperBound(self, dimension: DimensionHandle) -> int:
        raise NotImplementedError()

    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet:
        raise NotImplementedError()

    def getRangeBounds(
        self, region: RegionHandle, dimension: DimensionHandle
    ) -> RangeBounds:
        raise NotImplementedError()

    def setRangeBounds(
        self, region: RegionHandle, dimension: DimensionHandle, rangeBounds: RangeBounds
    ) -> None:
        raise NotImplementedError()

    def normalizeServiceGroup(self, serviceGroup: ServiceGroup) -> int:
        raise NotImplementedError()

    def normalizeFederateHandle(self, federate: FederateHandle) -> int:
        raise NotImplementedError()

    def normalizeObjectClassHandle(self, objectClass: ObjectClassHandle) -> int:
        raise NotImplementedError()

    def normalizeInteractionClassHandle(
        self, interactionClass: InteractionClassHandle
    ) -> int:
        raise NotImplementedError()

    def normalizeObjectInstanceHandle(
        self, objectInstance: ObjectInstanceHandle
    ) -> int:
        raise NotImplementedError()

    def getObjectClassRelevanceAdvisorySwitch(self) -> bool:
        raise NotImplementedError()

    def setObjectClassRelevanceAdvisorySwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getAttributeRelevanceAdvisorySwitch(self) -> bool:
        raise NotImplementedError()

    def setAttributeRelevanceAdvisorySwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getAttributeScopeAdvisorySwitch(self) -> bool:
        raise NotImplementedError()

    def setAttributeScopeAdvisorySwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getInteractionRelevanceAdvisorySwitch(self) -> bool:
        raise NotImplementedError()

    def setInteractionRelevanceAdvisorySwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getConveyRegionDesignatorSetsSwitch(self) -> bool:
        raise NotImplementedError()

    def setConveyRegionDesignatorSetsSwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getAutomaticResignDirective(self) -> ResignAction:
        raise NotImplementedError()

    def setAutomaticResignDirective(self, value: ResignAction) -> None:
        raise NotImplementedError()

    def getServiceReportingSwitch(self) -> bool:
        raise NotImplementedError()

    def setServiceReportingSwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getExceptionReportingSwitch(self) -> bool:
        raise NotImplementedError()

    def setExceptionReportingSwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getSendServiceReportsToFileSwitch(self) -> bool:
        raise NotImplementedError()

    def setSendServiceReportsToFileSwitch(self, value: bool) -> None:
        raise NotImplementedError()

    def getAutoProvideSwitch(self) -> bool:
        raise NotImplementedError()

    def getDelaySubscriptionEvaluationSwitch(self) -> bool:
        raise NotImplementedError()

    def getAdvisoriesUseKnownClassSwitch(self) -> bool:
        raise NotImplementedError()

    def getAllowRelaxedDDMSwitch(self) -> bool:
        raise NotImplementedError()

    def getNonRegulatedGrantSwitch(self) -> bool:
        raise NotImplementedError()

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        raise NotImplementedError()

    def evokeMultipleCallbacks(
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:
        raise NotImplementedError()

    def enableCallbacks(self) -> None:
        raise NotImplementedError()

    def disableCallbacks(self) -> None:
        raise NotImplementedError()

    # Java API-specific services
    def getAttributeHandleFactory(self) -> AttributeHandleFactory:
        raise NotImplementedError()

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:
        raise NotImplementedError()

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:
        raise NotImplementedError()

    def getAttributeSetRegionSetPairListFactory(
        self,
    ) -> AttributeSetRegionSetPairListFactory:
        raise NotImplementedError()

    def getDimensionHandleFactory(self) -> DimensionHandleFactory:
        raise NotImplementedError()

    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:
        raise NotImplementedError()

    def getFederateHandleFactory(self) -> FederateHandleFactory:
        raise NotImplementedError()

    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:
        raise NotImplementedError()

    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:
        raise NotImplementedError()

    def getInteractionClassHandleSetFactory(
        self,
    ) -> InteractionClassHandleSetFactory:
        raise NotImplementedError()

    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:
        raise NotImplementedError()

    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:
        raise NotImplementedError()

    def getParameterHandleFactory(self) -> ParameterHandleFactory:
        raise NotImplementedError()

    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:
        raise NotImplementedError()

    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:
        raise NotImplementedError()

    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:
        raise NotImplementedError()

    def getRegionHandleFactory(self) -> RegionHandleFactory:
        raise NotImplementedError()

    def getMessageRetractionHandleFactory(self) -> MessageRetractionHandleFactory:
        raise NotImplementedError()

    def getHLAversion(self) -> str:
        raise NotImplementedError()

    # C++ API-specific services
    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle:
        raise NotImplementedError()

    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle:
        raise NotImplementedError()

    def decodeInteractionClassHandle(
        self, encodedValue: bytes
    ) -> InteractionClassHandle:
        raise NotImplementedError()

    def decodeObjectInstanceHandle(self, encodedValue: bytes) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle:
        raise NotImplementedError()

    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle:
        raise NotImplementedError()

    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle:
        raise NotImplementedError()

    def decodeMessageRetractionHandle(
        self, encodedValue: bytes
    ) -> MessageRetractionHandle:
        raise NotImplementedError()

    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle:
        raise NotImplementedError()

    # C++ and Java services
    def getTimeFactory(self) -> LogicalTimeFactory:
        raise NotImplementedError()
