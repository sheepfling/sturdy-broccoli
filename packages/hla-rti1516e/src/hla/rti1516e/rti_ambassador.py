from __future__ import annotations

from typing import Protocol, Sequence, Set, overload

from .datatypes import MessageRetractionReturn, RangeBounds, TimeQueryReturn
from .enums import CallbackModel, OrderType, ResignAction, ServiceGroup, TransportationType
from .federate_ambassador import FederateAmbassador
from .handles import (
    AttributeHandle,
    AttributeHandleFactory,
    AttributeHandleSet,
    AttributeHandleSetFactory,
    AttributeHandleValueMap,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairList,
    AttributeSetRegionSetPairListFactory,
    DimensionHandle,
    DimensionHandleFactory,
    DimensionHandleSet,
    DimensionHandleSetFactory,
    FederateHandle,
    FederateHandleFactory,
    FederateHandleSet,
    FederateHandleSetFactory,
    InteractionClassHandle,
    InteractionClassHandleFactory,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMap,
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleSet,
    RegionHandleSetFactory,
    TransportationTypeHandle,
    TransportationTypeHandleFactory,
)
from .time import LogicalTime, LogicalTimeFactory, LogicalTimeInterval


class RTIambassador(Protocol):
    """Runtime protocol surface for IEEE 1516.1-2010 RTIambassador."""

    @overload
    def connect(
        self,
        federateReference: FederateAmbassador,
        callbackModel: CallbackModel,
    ) -> None:
        ...

    @overload
    def connect(
        self,
        federateReference: FederateAmbassador,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:
        ...

    def connect(
        self,
        federateReference: FederateAmbassador,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def createFederationExecution(
        self,
        federationExecutionName: str,
        fomModule: str | None = None,
        fomModules: Sequence[str] | None = None,
        *,
        mimModule: str | None = None,
        logicalTimeImplementationName: str | None = None,
    ) -> None:
        ...

    def destroyFederationExecution(self, federationExecutionName: str) -> None:
        ...

    def listFederationExecutions(self) -> None:
        ...

    @overload
    def joinFederationExecution(
        self,
        *,
        federateType: str,
        federationExecutionName: str,
    ) -> FederateHandle:
        ...

    @overload
    def joinFederationExecution(
        self,
        *,
        federateType: str,
        federationExecutionName: str,
        additionalFomModules: Sequence[str],
    ) -> FederateHandle:
        ...

    @overload
    def joinFederationExecution(
        self,
        *,
        federateName: str,
        federateType: str,
        federationExecutionName: str,
    ) -> FederateHandle:
        ...

    def joinFederationExecution(
        self,
        *,
        federateType: str,
        federationExecutionName: str,
        federateName: str | None = None,
        additionalFomModules: Sequence[str] | None = None,
    ) -> FederateHandle:
        ...

    def resignFederationExecution(self, resignAction: ResignAction) -> None:
        ...

    def registerFederationSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: bytes,
        synchronizationSet: FederateHandleSet | None = None,
    ) -> None:
        ...

    def synchronizationPointAchieved(
        self,
        synchronizationPointLabel: str,
        successIndicator: bool | None = None,
    ) -> None:
        ...

    def requestFederationSave(self, label: str, theTime: LogicalTime | None = None) -> None:
        ...

    def federateSaveBegun(self) -> None:
        ...

    def federateSaveComplete(self) -> None:
        ...

    def federateSaveNotComplete(self) -> None:
        ...

    def abortFederationSave(self) -> None:
        ...

    def queryFederationSaveStatus(self) -> None:
        ...

    def requestFederationRestore(self, label: str) -> None:
        ...

    def federateRestoreComplete(self) -> None:
        ...

    def federateRestoreNotComplete(self) -> None:
        ...

    def abortFederationRestore(self) -> None:
        ...

    def queryFederationRestoreStatus(self) -> None:
        ...

    def publishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet) -> None:
        ...

    def unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:
        ...

    def unpublishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet) -> None:
        ...

    def publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        ...

    def unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        ...

    def subscribeObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:
        ...

    def subscribeObjectClassAttributesPassively(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:
        ...

    def unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:
        ...

    def unsubscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet) -> None:
        ...

    def subscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        ...

    def subscribeInteractionClassPassively(self, theClass: InteractionClassHandle) -> None:
        ...

    def unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        ...

    def reserveObjectInstanceName(self, theObjectName: str) -> None:
        ...

    def releaseObjectInstanceName(self, theObjectInstanceName: str) -> None:
        ...

    def reserveMultipleObjectInstanceName(self, theObjectNames: Set[str]) -> None:
        ...

    def releaseMultipleObjectInstanceName(self, theObjectNames: Set[str]) -> None:
        ...

    def registerObjectInstance(
        self,
        theClass: ObjectClassHandle,
        theObjectName: str | None = None,
    ) -> ObjectInstanceHandle:
        ...

    def updateAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleValueMap,
        userSuppliedTag: bytes,
        theTime: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        ...

    def sendInteraction(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        userSuppliedTag: bytes,
        theTime: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        ...

    def deleteObjectInstance(
        self,
        objectHandle: ObjectInstanceHandle,
        userSuppliedTag: bytes,
        theTime: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        ...

    def localDeleteObjectInstance(self, objectHandle: ObjectInstanceHandle) -> None:
        ...

    @overload
    def requestAttributeValueUpdate(
        self,
        target: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    @overload
    def requestAttributeValueUpdate(
        self,
        target: ObjectClassHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def requestAttributeValueUpdate(
        self,
        target: ObjectInstanceHandle | ObjectClassHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def requestAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theType: TransportationTypeHandle,
    ) -> None:
        ...

    def queryAttributeTransportationType(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        ...

    def requestInteractionTransportationTypeChange(
        self,
        theClass: InteractionClassHandle,
        theType: TransportationTypeHandle,
    ) -> None:
        ...

    def queryInteractionTransportationType(self, theFederate: FederateHandle, theInteraction: InteractionClassHandle) -> None:
        ...

    def unconditionalAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:
        ...

    def negotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def confirmDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def attributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def attributeOwnershipAcquisitionIfAvailable(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
    ) -> None:
        ...

    def attributeOwnershipReleaseDenied(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        ...

    def attributeOwnershipDivestitureIfWanted(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> AttributeHandleSet:
        ...

    def cancelNegotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:
        ...

    def cancelAttributeOwnershipAcquisition(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        ...

    def queryAttributeOwnership(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        ...

    def isAttributeOwnedByFederate(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> bool:
        ...

    def enableTimeRegulation(self, theLookahead: LogicalTimeInterval) -> None:
        ...

    def disableTimeRegulation(self) -> None:
        ...

    def enableTimeConstrained(self) -> None:
        ...

    def disableTimeConstrained(self) -> None:
        ...

    def timeAdvanceRequest(self, theTime: LogicalTime) -> None:
        ...

    def timeAdvanceRequestAvailable(self, theTime: LogicalTime) -> None:
        ...

    def nextMessageRequest(self, theTime: LogicalTime) -> None:
        ...

    def nextMessageRequestAvailable(self, theTime: LogicalTime) -> None:
        ...

    def flushQueueRequest(self, theTime: LogicalTime) -> None:
        ...

    def enableAsynchronousDelivery(self) -> None:
        ...

    def disableAsynchronousDelivery(self) -> None:
        ...

    def queryGALT(self) -> TimeQueryReturn:
        ...

    def queryLogicalTime(self) -> LogicalTime:
        ...

    def queryLITS(self) -> TimeQueryReturn:
        ...

    def modifyLookahead(self, theLookahead: LogicalTimeInterval) -> None:
        ...

    def queryLookahead(self) -> LogicalTimeInterval:
        ...

    def retract(self, theHandle: MessageRetractionHandle) -> None:
        ...

    def changeAttributeOrderType(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theType: OrderType,
    ) -> None:
        ...

    def changeInteractionOrderType(self, theClass: InteractionClassHandle, theType: OrderType) -> None:
        ...

    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle:
        ...

    def commitRegionModifications(self, regions: RegionHandleSet) -> None:
        ...

    def deleteRegion(self, theRegion: RegionHandle) -> None:
        ...

    def registerObjectInstanceWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        theObject: str | None = None,
    ) -> ObjectInstanceHandle:
        ...

    def associateRegionsForUpdates(
        self,
        theObject: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:
        ...

    def unassociateRegionsForUpdates(
        self,
        theObject: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:
        ...

    def subscribeObjectClassAttributesWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None,
    ) -> None:
        ...

    def subscribeObjectClassAttributesPassivelyWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None,
    ) -> None:
        ...

    def unsubscribeObjectClassAttributesWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:
        ...

    def subscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        ...

    def subscribeInteractionClassPassivelyWithRegions(self, theClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        ...

    def unsubscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        ...

    def sendInteractionWithRegions(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        regions: RegionHandleSet,
        userSuppliedTag: bytes,
        theTime: LogicalTime | None = None,
    ) -> MessageRetractionReturn | None:
        ...

    def requestAttributeValueUpdateWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        userSuppliedTag: bytes,
    ) -> None:
        ...

    def getAutomaticResignDirective(self) -> ResignAction:
        ...

    def setAutomaticResignDirective(self, resignAction: ResignAction) -> None:
        ...

    def getFederateHandle(self, theName: str) -> FederateHandle:
        ...

    def getFederateName(self, theHandle: FederateHandle) -> str:
        ...

    def getObjectClassHandle(self, theName: str) -> ObjectClassHandle:
        ...

    def getObjectClassName(self, theHandle: ObjectClassHandle) -> str:
        ...

    def getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:
        ...

    def getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:
        ...

    def getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:
        ...

    def getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:
        ...

    def getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:
        ...

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:
        ...

    def getUpdateRateValueForAttribute(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> float:
        ...

    def getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:
        ...

    def getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:
        ...

    def getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:
        ...

    def getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:
        ...

    def getOrderType(self, theName: str) -> OrderType:
        ...

    def getOrderName(self, theType: OrderType) -> str:
        ...

    def getTransportationTypeHandle(self, theName: str) -> TransportationTypeHandle:
        ...

    def getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:
        ...

    def getAvailableDimensionsForClassAttribute(
        self,
        whichClass: ObjectClassHandle,
        theHandle: AttributeHandle,
    ) -> DimensionHandleSet:
        ...

    def getAvailableDimensionsForInteractionClass(self, theHandle: InteractionClassHandle) -> DimensionHandleSet:
        ...

    def getDimensionHandle(self, theName: str) -> DimensionHandle:
        ...

    def getDimensionName(self, theHandle: DimensionHandle) -> str:
        ...

    def getDimensionUpperBound(self, theHandle: DimensionHandle) -> int:
        ...

    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet:
        ...

    def getRangeBounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:
        ...

    def setRangeBounds(self, region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds) -> None:
        ...

    def normalizeFederateHandle(self, federateHandle: FederateHandle) -> int:
        ...

    def normalizeServiceGroup(self, group: ServiceGroup) -> int:
        ...

    def enableObjectClassRelevanceAdvisorySwitch(self) -> None:
        ...

    def disableObjectClassRelevanceAdvisorySwitch(self) -> None:
        ...

    def enableAttributeRelevanceAdvisorySwitch(self) -> None:
        ...

    def disableAttributeRelevanceAdvisorySwitch(self) -> None:
        ...

    def enableAttributeScopeAdvisorySwitch(self) -> None:
        ...

    def disableAttributeScopeAdvisorySwitch(self) -> None:
        ...

    def enableInteractionRelevanceAdvisorySwitch(self) -> None:
        ...

    def disableInteractionRelevanceAdvisorySwitch(self) -> None:
        ...

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        ...

    def evokeMultipleCallbacks(
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:
        ...

    def enableCallbacks(self) -> None:
        ...

    def disableCallbacks(self) -> None:
        ...

    def getAttributeHandleFactory(self) -> AttributeHandleFactory:
        ...

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:
        ...

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:
        ...

    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:
        ...

    def getDimensionHandleFactory(self) -> DimensionHandleFactory:
        ...

    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:
        ...

    def getFederateHandleFactory(self) -> FederateHandleFactory:
        ...

    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:
        ...

    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:
        ...

    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:
        ...

    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:
        ...

    def getParameterHandleFactory(self) -> ParameterHandleFactory:
        ...

    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:
        ...

    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:
        ...

    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:
        ...

    def getHLAversion(self) -> str:
        ...

    def getTimeFactory(self) -> LogicalTimeFactory:
        ...

    def createFederationExecutionWithMIM(
        self,
        federationExecutionName: str,
        fomModules: Sequence[str],
        mimModule: str,
        logicalTimeImplementationName: str | None = None,
    ) -> None:
        ...

    def getTransportationType(self, transportationName: str) -> TransportationType:
        ...

    def getTransportationName(self, transportationType: TransportationType) -> str:
        ...

    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle:
        ...

    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle:
        ...

    def decodeInteractionClassHandle(self, encodedValue: bytes) -> InteractionClassHandle:
        ...

    def decodeObjectInstanceHandle(self, encodedValue: bytes) -> ObjectInstanceHandle:
        ...

    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle:
        ...

    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle:
        ...

    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle:
        ...

    def decodeMessageRetractionHandle(self, encodedValue: bytes) -> MessageRetractionHandle:
        ...

    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle:
        ...

class UnimplementedRTIambassador(RTIambassador):
    def connect(self, federateReference: FederateAmbassador, callbackModel: CallbackModel, localSettingsDesignator: str | None=None) -> None:
        raise NotImplementedError()

    def disconnect(self) -> None:
        raise NotImplementedError()

    def createFederationExecution(self, federationExecutionName: str, fomModule: str | None=None, fomModules: Sequence[str] | None=None, *, mimModule: str | None=None, logicalTimeImplementationName: str | None=None) -> None:
        raise NotImplementedError()

    def destroyFederationExecution(self, federationExecutionName: str) -> None:
        raise NotImplementedError()

    def listFederationExecutions(self) -> None:
        raise NotImplementedError()

    def joinFederationExecution(self, *, federateType: str, federationExecutionName: str, federateName: str | None=None, additionalFomModules: Sequence[str] | None=None) -> FederateHandle:
        raise NotImplementedError()

    def resignFederationExecution(self, resignAction: ResignAction) -> None:
        raise NotImplementedError()

    def registerFederationSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: bytes, synchronizationSet: FederateHandleSet | None=None) -> None:
        raise NotImplementedError()

    def synchronizationPointAchieved(self, synchronizationPointLabel: str, successIndicator: bool | None=None) -> None:
        raise NotImplementedError()

    def requestFederationSave(self, label: str, theTime: LogicalTime | None=None) -> None:
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

    def publishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:
        raise NotImplementedError()

    def unpublishObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet, updateRateDesignator: str | None=None) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesPassively(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet, updateRateDesignator: str | None=None) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassAttributes(self, theClass: ObjectClassHandle, attributeList: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def subscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassPassively(self, theClass: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def reserveObjectInstanceName(self, theObjectName: str) -> None:
        raise NotImplementedError()

    def releaseObjectInstanceName(self, theObjectInstanceName: str) -> None:
        raise NotImplementedError()

    def reserveMultipleObjectInstanceName(self, theObjectNames: Set[str]) -> None:
        raise NotImplementedError()

    def releaseMultipleObjectInstanceName(self, theObjectNames: Set[str]) -> None:
        raise NotImplementedError()

    def registerObjectInstance(self, theClass: ObjectClassHandle, theObjectName: str | None=None) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def updateAttributeValues(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleValueMap, userSuppliedTag: bytes, theTime: LogicalTime | None=None) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def sendInteraction(self, theInteraction: InteractionClassHandle, theParameters: ParameterHandleValueMap, userSuppliedTag: bytes, theTime: LogicalTime | None=None) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def deleteObjectInstance(self, objectHandle: ObjectInstanceHandle, userSuppliedTag: bytes, theTime: LogicalTime | None=None) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def localDeleteObjectInstance(self, objectHandle: ObjectInstanceHandle) -> None:
        raise NotImplementedError()

    def requestAttributeValueUpdate(self, target: ObjectInstanceHandle | ObjectClassHandle, theAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def requestAttributeTransportationTypeChange(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, theType: TransportationTypeHandle) -> None:
        raise NotImplementedError()

    def queryAttributeTransportationType(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        raise NotImplementedError()

    def requestInteractionTransportationTypeChange(self, theClass: InteractionClassHandle, theType: TransportationTypeHandle) -> None:
        raise NotImplementedError()

    def queryInteractionTransportationType(self, theFederate: FederateHandle, theInteraction: InteractionClassHandle) -> None:
        raise NotImplementedError()

    def unconditionalAttributeOwnershipDivestiture(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def negotiatedAttributeOwnershipDivestiture(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def confirmDivestiture(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisition(self, theObject: ObjectInstanceHandle, desiredAttributes: AttributeHandleSet, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisitionIfAvailable(self, theObject: ObjectInstanceHandle, desiredAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def attributeOwnershipReleaseDenied(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def attributeOwnershipDivestitureIfWanted(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> AttributeHandleSet:
        raise NotImplementedError()

    def cancelNegotiatedAttributeOwnershipDivestiture(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def cancelAttributeOwnershipAcquisition(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:
        raise NotImplementedError()

    def queryAttributeOwnership(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:
        raise NotImplementedError()

    def isAttributeOwnedByFederate(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> bool:
        raise NotImplementedError()

    def enableTimeRegulation(self, theLookahead: LogicalTimeInterval) -> None:
        raise NotImplementedError()

    def disableTimeRegulation(self) -> None:
        raise NotImplementedError()

    def enableTimeConstrained(self) -> None:
        raise NotImplementedError()

    def disableTimeConstrained(self) -> None:
        raise NotImplementedError()

    def timeAdvanceRequest(self, theTime: LogicalTime) -> None:
        raise NotImplementedError()

    def timeAdvanceRequestAvailable(self, theTime: LogicalTime) -> None:
        raise NotImplementedError()

    def nextMessageRequest(self, theTime: LogicalTime) -> None:
        raise NotImplementedError()

    def nextMessageRequestAvailable(self, theTime: LogicalTime) -> None:
        raise NotImplementedError()

    def flushQueueRequest(self, theTime: LogicalTime) -> None:
        raise NotImplementedError()

    def enableAsynchronousDelivery(self) -> None:
        raise NotImplementedError()

    def disableAsynchronousDelivery(self) -> None:
        raise NotImplementedError()

    def queryGALT(self) -> TimeQueryReturn:
        raise NotImplementedError()

    def queryLogicalTime(self) -> LogicalTime:
        raise NotImplementedError()

    def queryLITS(self) -> TimeQueryReturn:
        raise NotImplementedError()

    def modifyLookahead(self, theLookahead: LogicalTimeInterval) -> None:
        raise NotImplementedError()

    def queryLookahead(self) -> LogicalTimeInterval:
        raise NotImplementedError()

    def retract(self, theHandle: MessageRetractionHandle) -> None:
        raise NotImplementedError()

    def changeAttributeOrderType(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet, theType: OrderType) -> None:
        raise NotImplementedError()

    def changeInteractionOrderType(self, theClass: InteractionClassHandle, theType: OrderType) -> None:
        raise NotImplementedError()

    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle:
        raise NotImplementedError()

    def commitRegionModifications(self, regions: RegionHandleSet) -> None:
        raise NotImplementedError()

    def deleteRegion(self, theRegion: RegionHandle) -> None:
        raise NotImplementedError()

    def registerObjectInstanceWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, theObject: str | None=None) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def associateRegionsForUpdates(self, theObject: ObjectInstanceHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None:
        raise NotImplementedError()

    def unassociateRegionsForUpdates(self, theObject: ObjectInstanceHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, updateRateDesignator: str | None=None) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesPassivelyWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, updateRateDesignator: str | None=None) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassAttributesWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassPassivelyWithRegions(self, theClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        raise NotImplementedError()

    def unsubscribeInteractionClassWithRegions(self, theClass: InteractionClassHandle, regions: RegionHandleSet) -> None:
        raise NotImplementedError()

    def sendInteractionWithRegions(self, theInteraction: InteractionClassHandle, theParameters: ParameterHandleValueMap, regions: RegionHandleSet, userSuppliedTag: bytes, theTime: LogicalTime | None=None) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def requestAttributeValueUpdateWithRegions(self, theClass: ObjectClassHandle, attributesAndRegions: AttributeSetRegionSetPairList, userSuppliedTag: bytes) -> None:
        raise NotImplementedError()

    def getAutomaticResignDirective(self) -> ResignAction:
        raise NotImplementedError()

    def setAutomaticResignDirective(self, resignAction: ResignAction) -> None:
        raise NotImplementedError()

    def getFederateHandle(self, theName: str) -> FederateHandle:
        raise NotImplementedError()

    def getFederateName(self, theHandle: FederateHandle) -> str:
        raise NotImplementedError()

    def getObjectClassHandle(self, theName: str) -> ObjectClassHandle:
        raise NotImplementedError()

    def getObjectClassName(self, theHandle: ObjectClassHandle) -> str:
        raise NotImplementedError()

    def getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:
        raise NotImplementedError()

    def getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:
        raise NotImplementedError()

    def getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:
        raise NotImplementedError()

    def getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:
        raise NotImplementedError()

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:
        raise NotImplementedError()

    def getUpdateRateValueForAttribute(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> float:
        raise NotImplementedError()

    def getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:
        raise NotImplementedError()

    def getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:
        raise NotImplementedError()

    def getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:
        raise NotImplementedError()

    def getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:
        raise NotImplementedError()

    def getOrderType(self, theName: str) -> OrderType:
        raise NotImplementedError()

    def getOrderName(self, theType: OrderType) -> str:
        raise NotImplementedError()

    def getTransportationTypeHandle(self, theName: str) -> TransportationTypeHandle:
        raise NotImplementedError()

    def getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:
        raise NotImplementedError()

    def getAvailableDimensionsForClassAttribute(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> DimensionHandleSet:
        raise NotImplementedError()

    def getAvailableDimensionsForInteractionClass(self, theHandle: InteractionClassHandle) -> DimensionHandleSet:
        raise NotImplementedError()

    def getDimensionHandle(self, theName: str) -> DimensionHandle:
        raise NotImplementedError()

    def getDimensionName(self, theHandle: DimensionHandle) -> str:
        raise NotImplementedError()

    def getDimensionUpperBound(self, theHandle: DimensionHandle) -> int:
        raise NotImplementedError()

    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet:
        raise NotImplementedError()

    def getRangeBounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:
        raise NotImplementedError()

    def setRangeBounds(self, region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds) -> None:
        raise NotImplementedError()

    def normalizeFederateHandle(self, federateHandle: FederateHandle) -> int:
        raise NotImplementedError()

    def normalizeServiceGroup(self, group: ServiceGroup) -> int:
        raise NotImplementedError()

    def enableObjectClassRelevanceAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def disableObjectClassRelevanceAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def enableAttributeRelevanceAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def disableAttributeRelevanceAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def enableAttributeScopeAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def disableAttributeScopeAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def enableInteractionRelevanceAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def disableInteractionRelevanceAdvisorySwitch(self) -> None:
        raise NotImplementedError()

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        raise NotImplementedError()

    def evokeMultipleCallbacks(self, approximateMinimumTimeInSeconds: float, approximateMaximumTimeInSeconds: float) -> bool:
        raise NotImplementedError()

    def enableCallbacks(self) -> None:
        raise NotImplementedError()

    def disableCallbacks(self) -> None:
        raise NotImplementedError()

    def getAttributeHandleFactory(self) -> AttributeHandleFactory:
        raise NotImplementedError()

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:
        raise NotImplementedError()

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:
        raise NotImplementedError()

    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:
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

    def getHLAversion(self) -> str:
        raise NotImplementedError()

    def getTimeFactory(self) -> LogicalTimeFactory:
        raise NotImplementedError()

    def createFederationExecutionWithMIM(self, federationExecutionName: str, fomModules: Sequence[str], mimModule: str, logicalTimeImplementationName: str | None=None) -> None:
        raise NotImplementedError()

    def getTransportationType(self, transportationName: str) -> TransportationType:
        raise NotImplementedError()

    def getTransportationName(self, transportationType: TransportationType) -> str:
        raise NotImplementedError()

    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle:
        raise NotImplementedError()

    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle:
        raise NotImplementedError()

    def decodeInteractionClassHandle(self, encodedValue: bytes) -> InteractionClassHandle:
        raise NotImplementedError()

    def decodeObjectInstanceHandle(self, encodedValue: bytes) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle:
        raise NotImplementedError()

    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle:
        raise NotImplementedError()

    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle:
        raise NotImplementedError()

    def decodeMessageRetractionHandle(self, encodedValue: bytes) -> MessageRetractionHandle:
        raise NotImplementedError()

    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle:
        raise NotImplementedError()
