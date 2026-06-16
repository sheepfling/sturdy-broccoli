from __future__ import annotations

from typing import Protocol

from .datatypes import MessageRetractionReturn, RangeBounds, TimeQueryReturn
from .enums import OrderType, ResignAction, TransportationType
from .federate_ambassador import FederateAmbassador
from .handles import (
    AttributeHandle,
    AttributeHandleFactory,
    AttributeHandleSet,
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    DimensionHandle,
    DimensionHandleFactory,
    DimensionHandleSet,
    DimensionHandleSetFactory,
    FederateHandle,
    FederateHandleFactory,
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
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleSetFactory,
    TransportationTypeHandle,
    TransportationTypeHandleFactory,
)
from .time import LogicalTime, LogicalTimeFactory, LogicalTimeInterval

class RTIambassador(Protocol):
    """Runtime protocol surface. Strict overloads live in the .pyi stub and SOURCE_TRACE.md."""

    def connect(self, *args, **kwargs) -> None:
        ...

    def disconnect(self, *args, **kwargs) -> None:
        ...

    def createFederationExecution(self, *args, **kwargs) -> None:
        ...

    def destroyFederationExecution(self, *args, **kwargs) -> None:
        ...

    def listFederationExecutions(self, *args, **kwargs) -> None:
        ...

    def joinFederationExecution(self, *args, **kwargs) -> FederateHandle:
        ...

    def resignFederationExecution(self, *args, **kwargs) -> None:
        ...

    def registerFederationSynchronizationPoint(self, *args, **kwargs) -> None:
        ...

    def synchronizationPointAchieved(self, *args, **kwargs) -> None:
        ...

    def requestFederationSave(self, *args, **kwargs) -> None:
        ...

    def federateSaveBegun(self, *args, **kwargs) -> None:
        ...

    def federateSaveComplete(self, *args, **kwargs) -> None:
        ...

    def federateSaveNotComplete(self, *args, **kwargs) -> None:
        ...

    def abortFederationSave(self, *args, **kwargs) -> None:
        ...

    def queryFederationSaveStatus(self, *args, **kwargs) -> None:
        ...

    def requestFederationRestore(self, *args, **kwargs) -> None:
        ...

    def federateRestoreComplete(self, *args, **kwargs) -> None:
        ...

    def federateRestoreNotComplete(self, *args, **kwargs) -> None:
        ...

    def abortFederationRestore(self, *args, **kwargs) -> None:
        ...

    def queryFederationRestoreStatus(self, *args, **kwargs) -> None:
        ...

    def publishObjectClassAttributes(self, *args, **kwargs) -> None:
        ...

    def unpublishObjectClass(self, *args, **kwargs) -> None:
        ...

    def unpublishObjectClassAttributes(self, *args, **kwargs) -> None:
        ...

    def publishInteractionClass(self, *args, **kwargs) -> None:
        ...

    def unpublishInteractionClass(self, *args, **kwargs) -> None:
        ...

    def subscribeObjectClassAttributes(self, *args, **kwargs) -> None:
        ...

    def subscribeObjectClassAttributesPassively(self, *args, **kwargs) -> None:
        ...

    def unsubscribeObjectClass(self, *args, **kwargs) -> None:
        ...

    def unsubscribeObjectClassAttributes(self, *args, **kwargs) -> None:
        ...

    def subscribeInteractionClass(self, *args, **kwargs) -> None:
        ...

    def subscribeInteractionClassPassively(self, *args, **kwargs) -> None:
        ...

    def unsubscribeInteractionClass(self, *args, **kwargs) -> None:
        ...

    def reserveObjectInstanceName(self, *args, **kwargs) -> None:
        ...

    def releaseObjectInstanceName(self, *args, **kwargs) -> None:
        ...

    def reserveMultipleObjectInstanceName(self, *args, **kwargs) -> None:
        ...

    def releaseMultipleObjectInstanceName(self, *args, **kwargs) -> None:
        ...

    def registerObjectInstance(self, *args, **kwargs) -> ObjectInstanceHandle:
        ...

    def updateAttributeValues(self, *args, **kwargs) -> MessageRetractionReturn | None:
        ...

    def sendInteraction(self, *args, **kwargs) -> MessageRetractionReturn | None:
        ...

    def deleteObjectInstance(self, *args, **kwargs) -> MessageRetractionReturn | None:
        ...

    def localDeleteObjectInstance(self, *args, **kwargs) -> None:
        ...

    def requestAttributeValueUpdate(self, *args, **kwargs) -> None:
        ...

    def requestAttributeTransportationTypeChange(self, *args, **kwargs) -> None:
        ...

    def queryAttributeTransportationType(self, *args, **kwargs) -> None:
        ...

    def requestInteractionTransportationTypeChange(self, *args, **kwargs) -> None:
        ...

    def queryInteractionTransportationType(self, *args, **kwargs) -> None:
        ...

    def unconditionalAttributeOwnershipDivestiture(self, *args, **kwargs) -> None:
        ...

    def negotiatedAttributeOwnershipDivestiture(self, *args, **kwargs) -> None:
        ...

    def confirmDivestiture(self, *args, **kwargs) -> None:
        ...

    def attributeOwnershipAcquisition(self, *args, **kwargs) -> None:
        ...

    def attributeOwnershipAcquisitionIfAvailable(self, *args, **kwargs) -> None:
        ...

    def attributeOwnershipReleaseDenied(self, *args, **kwargs) -> None:
        ...

    def attributeOwnershipDivestitureIfWanted(self, *args, **kwargs) -> AttributeHandleSet:
        ...

    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args, **kwargs) -> None:
        ...

    def cancelAttributeOwnershipAcquisition(self, *args, **kwargs) -> None:
        ...

    def queryAttributeOwnership(self, *args, **kwargs) -> None:
        ...

    def isAttributeOwnedByFederate(self, *args, **kwargs) -> bool:
        ...

    def enableTimeRegulation(self, *args, **kwargs) -> None:
        ...

    def disableTimeRegulation(self, *args, **kwargs) -> None:
        ...

    def enableTimeConstrained(self, *args, **kwargs) -> None:
        ...

    def disableTimeConstrained(self, *args, **kwargs) -> None:
        ...

    def timeAdvanceRequest(self, *args, **kwargs) -> None:
        ...

    def timeAdvanceRequestAvailable(self, *args, **kwargs) -> None:
        ...

    def nextMessageRequest(self, *args, **kwargs) -> None:
        ...

    def nextMessageRequestAvailable(self, *args, **kwargs) -> None:
        ...

    def flushQueueRequest(self, *args, **kwargs) -> None:
        ...

    def enableAsynchronousDelivery(self, *args, **kwargs) -> None:
        ...

    def disableAsynchronousDelivery(self, *args, **kwargs) -> None:
        ...

    def queryGALT(self, *args, **kwargs) -> TimeQueryReturn:
        ...

    def queryLogicalTime(self, *args, **kwargs) -> LogicalTime:
        ...

    def queryLITS(self, *args, **kwargs) -> TimeQueryReturn:
        ...

    def modifyLookahead(self, *args, **kwargs) -> None:
        ...

    def queryLookahead(self, *args, **kwargs) -> LogicalTimeInterval:
        ...

    def retract(self, *args, **kwargs) -> None:
        ...

    def changeAttributeOrderType(self, *args, **kwargs) -> None:
        ...

    def changeInteractionOrderType(self, *args, **kwargs) -> None:
        ...

    def createRegion(self, *args, **kwargs) -> RegionHandle:
        ...

    def commitRegionModifications(self, *args, **kwargs) -> None:
        ...

    def deleteRegion(self, *args, **kwargs) -> None:
        ...

    def registerObjectInstanceWithRegions(self, *args, **kwargs) -> ObjectInstanceHandle:
        ...

    def associateRegionsForUpdates(self, *args, **kwargs) -> None:
        ...

    def unassociateRegionsForUpdates(self, *args, **kwargs) -> None:
        ...

    def subscribeObjectClassAttributesWithRegions(self, *args, **kwargs) -> None:
        ...

    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args, **kwargs) -> None:
        ...

    def unsubscribeObjectClassAttributesWithRegions(self, *args, **kwargs) -> None:
        ...

    def subscribeInteractionClassWithRegions(self, *args, **kwargs) -> None:
        ...

    def subscribeInteractionClassPassivelyWithRegions(self, *args, **kwargs) -> None:
        ...

    def unsubscribeInteractionClassWithRegions(self, *args, **kwargs) -> None:
        ...

    def sendInteractionWithRegions(self, *args, **kwargs) -> MessageRetractionReturn | None:
        ...

    def requestAttributeValueUpdateWithRegions(self, *args, **kwargs) -> None:
        ...

    def getAutomaticResignDirective(self, *args, **kwargs) -> ResignAction:
        ...

    def setAutomaticResignDirective(self, *args, **kwargs) -> None:
        ...

    def getFederateHandle(self, *args, **kwargs) -> FederateHandle:
        ...

    def getFederateName(self, *args, **kwargs) -> str:
        ...

    def getObjectClassHandle(self, *args, **kwargs) -> ObjectClassHandle:
        ...

    def getObjectClassName(self, *args, **kwargs) -> str:
        ...

    def getKnownObjectClassHandle(self, *args, **kwargs) -> ObjectClassHandle:
        ...

    def getObjectInstanceHandle(self, *args, **kwargs) -> ObjectInstanceHandle:
        ...

    def getObjectInstanceName(self, *args, **kwargs) -> str:
        ...

    def getAttributeHandle(self, *args, **kwargs) -> AttributeHandle:
        ...

    def getAttributeName(self, *args, **kwargs) -> str:
        ...

    def getUpdateRateValue(self, *args, **kwargs) -> float:
        ...

    def getUpdateRateValueForAttribute(self, *args, **kwargs) -> float:
        ...

    def getInteractionClassHandle(self, *args, **kwargs) -> InteractionClassHandle:
        ...

    def getInteractionClassName(self, *args, **kwargs) -> str:
        ...

    def getParameterHandle(self, *args, **kwargs) -> ParameterHandle:
        ...

    def getParameterName(self, *args, **kwargs) -> str:
        ...

    def getOrderType(self, *args, **kwargs) -> OrderType:
        ...

    def getOrderName(self, *args, **kwargs) -> str:
        ...

    def getTransportationTypeHandle(self, *args, **kwargs) -> TransportationTypeHandle:
        ...

    def getTransportationTypeName(self, *args, **kwargs) -> str:
        ...

    def getAvailableDimensionsForClassAttribute(self, *args, **kwargs) -> DimensionHandleSet:
        ...

    def getAvailableDimensionsForInteractionClass(self, *args, **kwargs) -> DimensionHandleSet:
        ...

    def getDimensionHandle(self, *args, **kwargs) -> DimensionHandle:
        ...

    def getDimensionName(self, *args, **kwargs) -> str:
        ...

    def getDimensionUpperBound(self, *args, **kwargs) -> int:
        ...

    def getDimensionHandleSet(self, *args, **kwargs) -> DimensionHandleSet:
        ...

    def getRangeBounds(self, *args, **kwargs) -> RangeBounds:
        ...

    def setRangeBounds(self, *args, **kwargs) -> None:
        ...

    def normalizeFederateHandle(self, *args, **kwargs) -> int:
        ...

    def normalizeServiceGroup(self, *args, **kwargs) -> int:
        ...

    def enableObjectClassRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def disableObjectClassRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def enableAttributeRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def disableAttributeRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def enableAttributeScopeAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def disableAttributeScopeAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def enableInteractionRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def disableInteractionRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        ...

    def evokeCallback(self, *args, **kwargs) -> bool:
        ...

    def evokeMultipleCallbacks(self, *args, **kwargs) -> bool:
        ...

    def enableCallbacks(self, *args, **kwargs) -> None:
        ...

    def disableCallbacks(self, *args, **kwargs) -> None:
        ...

    def getAttributeHandleFactory(self, *args, **kwargs) -> AttributeHandleFactory:
        ...

    def getAttributeHandleSetFactory(self, *args, **kwargs) -> AttributeHandleSetFactory:
        ...

    def getAttributeHandleValueMapFactory(self, *args, **kwargs) -> AttributeHandleValueMapFactory:
        ...

    def getAttributeSetRegionSetPairListFactory(self, *args, **kwargs) -> AttributeSetRegionSetPairListFactory:
        ...

    def getDimensionHandleFactory(self, *args, **kwargs) -> DimensionHandleFactory:
        ...

    def getDimensionHandleSetFactory(self, *args, **kwargs) -> DimensionHandleSetFactory:
        ...

    def getFederateHandleFactory(self, *args, **kwargs) -> FederateHandleFactory:
        ...

    def getFederateHandleSetFactory(self, *args, **kwargs) -> FederateHandleSetFactory:
        ...

    def getInteractionClassHandleFactory(self, *args, **kwargs) -> InteractionClassHandleFactory:
        ...

    def getObjectClassHandleFactory(self, *args, **kwargs) -> ObjectClassHandleFactory:
        ...

    def getObjectInstanceHandleFactory(self, *args, **kwargs) -> ObjectInstanceHandleFactory:
        ...

    def getParameterHandleFactory(self, *args, **kwargs) -> ParameterHandleFactory:
        ...

    def getParameterHandleValueMapFactory(self, *args, **kwargs) -> ParameterHandleValueMapFactory:
        ...

    def getRegionHandleSetFactory(self, *args, **kwargs) -> RegionHandleSetFactory:
        ...

    def getTransportationTypeHandleFactory(self, *args, **kwargs) -> TransportationTypeHandleFactory:
        ...

    def getHLAversion(self, *args, **kwargs) -> str:
        ...

    def getTimeFactory(self, *args, **kwargs) -> LogicalTimeFactory:
        ...

    def createFederationExecutionWithMIM(self, *args, **kwargs) -> None:
        ...

    def getTransportationType(self, *args, **kwargs) -> TransportationType:
        ...

    def getTransportationName(self, *args, **kwargs) -> str:
        ...

    def decodeFederateHandle(self, *args, **kwargs) -> FederateHandle:
        ...

    def decodeObjectClassHandle(self, *args, **kwargs) -> ObjectClassHandle:
        ...

    def decodeInteractionClassHandle(self, *args, **kwargs) -> InteractionClassHandle:
        ...

    def decodeObjectInstanceHandle(self, *args, **kwargs) -> ObjectInstanceHandle:
        ...

    def decodeAttributeHandle(self, *args, **kwargs) -> AttributeHandle:
        ...

    def decodeParameterHandle(self, *args, **kwargs) -> ParameterHandle:
        ...

    def decodeDimensionHandle(self, *args, **kwargs) -> DimensionHandle:
        ...

    def decodeMessageRetractionHandle(self, *args, **kwargs) -> MessageRetractionHandle:
        ...

    def decodeRegionHandle(self, *args, **kwargs) -> RegionHandle:
        ...

class UnimplementedRTIambassador(RTIambassador):

    def connect(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disconnect(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def createFederationExecution(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def destroyFederationExecution(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def listFederationExecutions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def joinFederationExecution(self, *args, **kwargs) -> FederateHandle:
        raise NotImplementedError()

    def resignFederationExecution(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def registerFederationSynchronizationPoint(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def synchronizationPointAchieved(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestFederationSave(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federateSaveBegun(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federateSaveComplete(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federateSaveNotComplete(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def abortFederationSave(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryFederationSaveStatus(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestFederationRestore(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federateRestoreComplete(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federateRestoreNotComplete(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def abortFederationRestore(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryFederationRestoreStatus(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def publishObjectClassAttributes(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unpublishObjectClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unpublishObjectClassAttributes(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def publishInteractionClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unpublishInteractionClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributes(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesPassively(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassAttributes(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeInteractionClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassPassively(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unsubscribeInteractionClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def reserveObjectInstanceName(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def releaseObjectInstanceName(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def reserveMultipleObjectInstanceName(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def releaseMultipleObjectInstanceName(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def registerObjectInstance(self, *args, **kwargs) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def updateAttributeValues(self, *args, **kwargs) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def sendInteraction(self, *args, **kwargs) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def deleteObjectInstance(self, *args, **kwargs) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def localDeleteObjectInstance(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestAttributeValueUpdate(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestAttributeTransportationTypeChange(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryAttributeTransportationType(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestInteractionTransportationTypeChange(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryInteractionTransportationType(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unconditionalAttributeOwnershipDivestiture(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def negotiatedAttributeOwnershipDivestiture(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def confirmDivestiture(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisition(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisitionIfAvailable(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeOwnershipReleaseDenied(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeOwnershipDivestitureIfWanted(self, *args, **kwargs) -> AttributeHandleSet:
        raise NotImplementedError()

    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def cancelAttributeOwnershipAcquisition(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryAttributeOwnership(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def isAttributeOwnedByFederate(self, *args, **kwargs) -> bool:
        raise NotImplementedError()

    def enableTimeRegulation(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableTimeRegulation(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def enableTimeConstrained(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableTimeConstrained(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def timeAdvanceRequest(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def timeAdvanceRequestAvailable(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def nextMessageRequest(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def nextMessageRequestAvailable(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def flushQueueRequest(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def enableAsynchronousDelivery(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableAsynchronousDelivery(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryGALT(self, *args, **kwargs) -> TimeQueryReturn:
        raise NotImplementedError()

    def queryLogicalTime(self, *args, **kwargs) -> LogicalTime:
        raise NotImplementedError()

    def queryLITS(self, *args, **kwargs) -> TimeQueryReturn:
        raise NotImplementedError()

    def modifyLookahead(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def queryLookahead(self, *args, **kwargs) -> LogicalTimeInterval:
        raise NotImplementedError()

    def retract(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def changeAttributeOrderType(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def changeInteractionOrderType(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def createRegion(self, *args, **kwargs) -> RegionHandle:
        raise NotImplementedError()

    def commitRegionModifications(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def deleteRegion(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def registerObjectInstanceWithRegions(self, *args, **kwargs) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def associateRegionsForUpdates(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unassociateRegionsForUpdates(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unsubscribeObjectClassAttributesWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def subscribeInteractionClassPassivelyWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def unsubscribeInteractionClassWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def sendInteractionWithRegions(self, *args, **kwargs) -> MessageRetractionReturn | None:
        raise NotImplementedError()

    def requestAttributeValueUpdateWithRegions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def getAutomaticResignDirective(self, *args, **kwargs) -> ResignAction:
        raise NotImplementedError()

    def setAutomaticResignDirective(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def getFederateHandle(self, *args, **kwargs) -> FederateHandle:
        raise NotImplementedError()

    def getFederateName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getObjectClassHandle(self, *args, **kwargs) -> ObjectClassHandle:
        raise NotImplementedError()

    def getObjectClassName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getKnownObjectClassHandle(self, *args, **kwargs) -> ObjectClassHandle:
        raise NotImplementedError()

    def getObjectInstanceHandle(self, *args, **kwargs) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def getObjectInstanceName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getAttributeHandle(self, *args, **kwargs) -> AttributeHandle:
        raise NotImplementedError()

    def getAttributeName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getUpdateRateValue(self, *args, **kwargs) -> float:
        raise NotImplementedError()

    def getUpdateRateValueForAttribute(self, *args, **kwargs) -> float:
        raise NotImplementedError()

    def getInteractionClassHandle(self, *args, **kwargs) -> InteractionClassHandle:
        raise NotImplementedError()

    def getInteractionClassName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getParameterHandle(self, *args, **kwargs) -> ParameterHandle:
        raise NotImplementedError()

    def getParameterName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getOrderType(self, *args, **kwargs) -> OrderType:
        raise NotImplementedError()

    def getOrderName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getTransportationTypeHandle(self, *args, **kwargs) -> TransportationTypeHandle:
        raise NotImplementedError()

    def getTransportationTypeName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getAvailableDimensionsForClassAttribute(self, *args, **kwargs) -> DimensionHandleSet:
        raise NotImplementedError()

    def getAvailableDimensionsForInteractionClass(self, *args, **kwargs) -> DimensionHandleSet:
        raise NotImplementedError()

    def getDimensionHandle(self, *args, **kwargs) -> DimensionHandle:
        raise NotImplementedError()

    def getDimensionName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getDimensionUpperBound(self, *args, **kwargs) -> int:
        raise NotImplementedError()

    def getDimensionHandleSet(self, *args, **kwargs) -> DimensionHandleSet:
        raise NotImplementedError()

    def getRangeBounds(self, *args, **kwargs) -> RangeBounds:
        raise NotImplementedError()

    def setRangeBounds(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def normalizeFederateHandle(self, *args, **kwargs) -> int:
        raise NotImplementedError()

    def normalizeServiceGroup(self, *args, **kwargs) -> int:
        raise NotImplementedError()

    def enableObjectClassRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableObjectClassRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def enableAttributeRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableAttributeRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def enableAttributeScopeAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableAttributeScopeAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def enableInteractionRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableInteractionRelevanceAdvisorySwitch(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def evokeCallback(self, *args, **kwargs) -> bool:
        raise NotImplementedError()

    def evokeMultipleCallbacks(self, *args, **kwargs) -> bool:
        raise NotImplementedError()

    def enableCallbacks(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def disableCallbacks(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def getAttributeHandleFactory(self, *args, **kwargs) -> AttributeHandleFactory:
        raise NotImplementedError()

    def getAttributeHandleSetFactory(self, *args, **kwargs) -> AttributeHandleSetFactory:
        raise NotImplementedError()

    def getAttributeHandleValueMapFactory(self, *args, **kwargs) -> AttributeHandleValueMapFactory:
        raise NotImplementedError()

    def getAttributeSetRegionSetPairListFactory(self, *args, **kwargs) -> AttributeSetRegionSetPairListFactory:
        raise NotImplementedError()

    def getDimensionHandleFactory(self, *args, **kwargs) -> DimensionHandleFactory:
        raise NotImplementedError()

    def getDimensionHandleSetFactory(self, *args, **kwargs) -> DimensionHandleSetFactory:
        raise NotImplementedError()

    def getFederateHandleFactory(self, *args, **kwargs) -> FederateHandleFactory:
        raise NotImplementedError()

    def getFederateHandleSetFactory(self, *args, **kwargs) -> FederateHandleSetFactory:
        raise NotImplementedError()

    def getInteractionClassHandleFactory(self, *args, **kwargs) -> InteractionClassHandleFactory:
        raise NotImplementedError()

    def getObjectClassHandleFactory(self, *args, **kwargs) -> ObjectClassHandleFactory:
        raise NotImplementedError()

    def getObjectInstanceHandleFactory(self, *args, **kwargs) -> ObjectInstanceHandleFactory:
        raise NotImplementedError()

    def getParameterHandleFactory(self, *args, **kwargs) -> ParameterHandleFactory:
        raise NotImplementedError()

    def getParameterHandleValueMapFactory(self, *args, **kwargs) -> ParameterHandleValueMapFactory:
        raise NotImplementedError()

    def getRegionHandleSetFactory(self, *args, **kwargs) -> RegionHandleSetFactory:
        raise NotImplementedError()

    def getTransportationTypeHandleFactory(self, *args, **kwargs) -> TransportationTypeHandleFactory:
        raise NotImplementedError()

    def getHLAversion(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def getTimeFactory(self, *args, **kwargs) -> LogicalTimeFactory:
        raise NotImplementedError()

    def createFederationExecutionWithMIM(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def getTransportationType(self, *args, **kwargs) -> TransportationType:
        raise NotImplementedError()

    def getTransportationName(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def decodeFederateHandle(self, *args, **kwargs) -> FederateHandle:
        raise NotImplementedError()

    def decodeObjectClassHandle(self, *args, **kwargs) -> ObjectClassHandle:
        raise NotImplementedError()

    def decodeInteractionClassHandle(self, *args, **kwargs) -> InteractionClassHandle:
        raise NotImplementedError()

    def decodeObjectInstanceHandle(self, *args, **kwargs) -> ObjectInstanceHandle:
        raise NotImplementedError()

    def decodeAttributeHandle(self, *args, **kwargs) -> AttributeHandle:
        raise NotImplementedError()

    def decodeParameterHandle(self, *args, **kwargs) -> ParameterHandle:
        raise NotImplementedError()

    def decodeDimensionHandle(self, *args, **kwargs) -> DimensionHandle:
        raise NotImplementedError()

    def decodeMessageRetractionHandle(self, *args, **kwargs) -> MessageRetractionHandle:
        raise NotImplementedError()

    def decodeRegionHandle(self, *args, **kwargs) -> RegionHandle:
        raise NotImplementedError()
