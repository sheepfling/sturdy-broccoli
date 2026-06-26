"""Source-derived raw API surface for HLA IEEE 1516.1-2010.

Method names intentionally preserve the Java/C++ lowerCamelCase spelling.  The
methods accept ``*args``/``**kwargs`` because Java and C++ overloads do not map
1:1 onto a single Python signature.  See ``API_METADATA`` for overload records.

"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from importlib import resources
from typing import Any


def _load_api_metadata() -> dict[str, dict[str, list[dict[str, Any]]]]:
    metadata = resources.files("hla.rti1516e").joinpath("api_metadata.json").read_text(encoding="utf-8")
    return json.loads(metadata)


API_METADATA = _load_api_metadata()
API_METADATA.setdefault("RTIambassador", {}).setdefault("getRegionHandleFactory", [])
API_METADATA.setdefault("RTIambassador", {}).setdefault("getMessageRetractionHandleFactory", [])


class RTIambassador(ABC):
    """Abstract RTI ambassador interface. RTI adapters implement these methods."""

    @abstractmethod
    def abortFederationRestore(self, *args: Any, **kwargs: Any) -> Any:
        """abortFederationRestore; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def abortFederationSave(self, *args: Any, **kwargs: Any) -> Any:
        """abortFederationSave; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def associateRegionsForUpdates(self, *args: Any, **kwargs: Any) -> Any:
        """associateRegionsForUpdates; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipAcquisition(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipAcquisition; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipAcquisitionIfAvailable(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipAcquisitionIfAvailable; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipDivestitureIfWanted(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipDivestitureIfWanted; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipReleaseDenied(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipReleaseDenied; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def cancelAttributeOwnershipAcquisition(self, *args: Any, **kwargs: Any) -> Any:
        """cancelAttributeOwnershipAcquisition; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """cancelNegotiatedAttributeOwnershipDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def changeAttributeOrderType(self, *args: Any, **kwargs: Any) -> Any:
        """changeAttributeOrderType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def changeInteractionOrderType(self, *args: Any, **kwargs: Any) -> Any:
        """changeInteractionOrderType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def commitRegionModifications(self, *args: Any, **kwargs: Any) -> Any:
        """commitRegionModifications; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def confirmDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """confirmDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def connect(self, *args: Any, **kwargs: Any) -> Any:
        """connect; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def createFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """createFederationExecution; 7 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def createFederationExecutionWithMIM(self, *args: Any, **kwargs: Any) -> Any:
        """createFederationExecutionWithMIM; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def createRegion(self, *args: Any, **kwargs: Any) -> Any:
        """createRegion; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeAttributeHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeAttributeHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeDimensionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeDimensionHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeFederateHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeFederateHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeInteractionClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeInteractionClassHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeMessageRetractionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeMessageRetractionHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeObjectClassHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeObjectInstanceHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeObjectInstanceHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeParameterHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeParameterHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeRegionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeRegionHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def deleteObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """deleteObjectInstance; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def deleteRegion(self, *args: Any, **kwargs: Any) -> Any:
        """deleteRegion; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """destroyFederationExecution; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableAsynchronousDelivery(self, *args: Any, **kwargs: Any) -> Any:
        """disableAsynchronousDelivery; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableAttributeRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableAttributeRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableAttributeScopeAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableAttributeScopeAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableCallbacks(self, *args: Any, **kwargs: Any) -> Any:
        """disableCallbacks; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableInteractionRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableInteractionRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableObjectClassRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableObjectClassRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableTimeConstrained(self, *args: Any, **kwargs: Any) -> Any:
        """disableTimeConstrained; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableTimeRegulation(self, *args: Any, **kwargs: Any) -> Any:
        """disableTimeRegulation; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, *args: Any, **kwargs: Any) -> Any:
        """disconnect; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableAsynchronousDelivery(self, *args: Any, **kwargs: Any) -> Any:
        """enableAsynchronousDelivery; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableAttributeRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableAttributeRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableAttributeScopeAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableAttributeScopeAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableCallbacks(self, *args: Any, **kwargs: Any) -> Any:
        """enableCallbacks; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableInteractionRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableInteractionRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableObjectClassRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableObjectClassRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableTimeConstrained(self, *args: Any, **kwargs: Any) -> Any:
        """enableTimeConstrained; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableTimeRegulation(self, *args: Any, **kwargs: Any) -> Any:
        """enableTimeRegulation; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def evokeCallback(self, *args: Any, **kwargs: Any) -> Any:
        """evokeCallback; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def evokeMultipleCallbacks(self, *args: Any, **kwargs: Any) -> Any:
        """evokeMultipleCallbacks; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateRestoreComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateRestoreComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateRestoreNotComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateRestoreNotComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateSaveBegun(self, *args: Any, **kwargs: Any) -> Any:
        """federateSaveBegun; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateSaveComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateSaveComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateSaveNotComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateSaveNotComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def flushQueueRequest(self, *args: Any, **kwargs: Any) -> Any:
        """flushQueueRequest; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandleValueMapFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandleValueMapFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeName(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeSetRegionSetPairListFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeSetRegionSetPairListFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAutomaticResignDirective(self, *args: Any, **kwargs: Any) -> Any:
        """getAutomaticResignDirective; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAvailableDimensionsForClassAttribute(self, *args: Any, **kwargs: Any) -> Any:
        """getAvailableDimensionsForClassAttribute; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAvailableDimensionsForInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """getAvailableDimensionsForInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandleSet(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandleSet; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionName(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionUpperBound(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionUpperBound; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateName(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getHLAversion(self, *args: Any, **kwargs: Any) -> Any:
        """getHLAversion; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getInteractionClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getInteractionClassHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getInteractionClassHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getInteractionClassHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getInteractionClassName(self, *args: Any, **kwargs: Any) -> Any:
        """getInteractionClassName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getKnownObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getKnownObjectClassHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectClassHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectClassHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectClassHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectClassName(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectClassName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectInstanceHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectInstanceHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectInstanceHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectInstanceHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getOrderName(self, *args: Any, **kwargs: Any) -> Any:
        """getOrderName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getOrderType(self, *args: Any, **kwargs: Any) -> Any:
        """getOrderType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterHandleValueMapFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterHandleValueMapFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterName(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getRangeBounds(self, *args: Any, **kwargs: Any) -> Any:
        """getRangeBounds; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getRegionHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getRegionHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getRegionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getRegionHandleFactory; compatibility/support-factory extension. See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getMessageRetractionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getMessageRetractionHandleFactory; compatibility/support-factory extension. See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTimeFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getTimeFactory; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationName(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationName; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationType; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationTypeHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationTypeHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationTypeHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationTypeHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationTypeName(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationTypeName; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getUpdateRateValue(self, *args: Any, **kwargs: Any) -> Any:
        """getUpdateRateValue; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getUpdateRateValueForAttribute(self, *args: Any, **kwargs: Any) -> Any:
        """getUpdateRateValueForAttribute; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def isAttributeOwnedByFederate(self, *args: Any, **kwargs: Any) -> Any:
        """isAttributeOwnedByFederate; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def joinFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """joinFederationExecution; 6 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def listFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:
        """listFederationExecutions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def localDeleteObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """localDeleteObjectInstance; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def modifyLookahead(self, *args: Any, **kwargs: Any) -> Any:
        """modifyLookahead; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def negotiatedAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """negotiatedAttributeOwnershipDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def nextMessageRequest(self, *args: Any, **kwargs: Any) -> Any:
        """nextMessageRequest; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def nextMessageRequestAvailable(self, *args: Any, **kwargs: Any) -> Any:
        """nextMessageRequestAvailable; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def normalizeFederateHandle(self, *args: Any, **kwargs: Any) -> Any:
        """normalizeFederateHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def normalizeServiceGroup(self, *args: Any, **kwargs: Any) -> Any:
        """normalizeServiceGroup; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def publishInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """publishInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def publishObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """publishObjectClassAttributes; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:
        """queryAttributeOwnership; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """queryAttributeTransportationType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryFederationRestoreStatus(self, *args: Any, **kwargs: Any) -> Any:
        """queryFederationRestoreStatus; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryFederationSaveStatus(self, *args: Any, **kwargs: Any) -> Any:
        """queryFederationSaveStatus; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryGALT(self, *args: Any, **kwargs: Any) -> Any:
        """queryGALT; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """queryInteractionTransportationType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryLITS(self, *args: Any, **kwargs: Any) -> Any:
        """queryLITS; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryLogicalTime(self, *args: Any, **kwargs: Any) -> Any:
        """queryLogicalTime; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryLookahead(self, *args: Any, **kwargs: Any) -> Any:
        """queryLookahead; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def registerFederationSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:
        """registerFederationSynchronizationPoint; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def registerObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """registerObjectInstance; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def registerObjectInstanceWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """registerObjectInstanceWithRegions; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def releaseMultipleObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """releaseMultipleObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def releaseObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """releaseObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeTransportationTypeChange; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeValueUpdate; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestAttributeValueUpdateWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeValueUpdateWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestFederationRestore(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationRestore; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestFederationSave(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationSave; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """requestInteractionTransportationTypeChange; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def reserveMultipleObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """reserveMultipleObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def reserveObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """reserveObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def resignFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """resignFederationExecution; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def retract(self, *args: Any, **kwargs: Any) -> Any:
        """retract; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def sendInteraction(self, *args: Any, **kwargs: Any) -> Any:
        """sendInteraction; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def sendInteractionWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """sendInteractionWithRegions; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def setAutomaticResignDirective(self, *args: Any, **kwargs: Any) -> Any:
        """setAutomaticResignDirective; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def setRangeBounds(self, *args: Any, **kwargs: Any) -> Any:
        """setRangeBounds; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClassPassively(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClassPassively; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClassPassivelyWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClassPassivelyWithRegions; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClassWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClassWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributes; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributesPassively(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributesPassively; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributesPassivelyWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributesWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributesWithRegions; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def synchronizationPointAchieved(self, *args: Any, **kwargs: Any) -> Any:
        """synchronizationPointAchieved; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def timeAdvanceRequest(self, *args: Any, **kwargs: Any) -> Any:
        """timeAdvanceRequest; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def timeAdvanceRequestAvailable(self, *args: Any, **kwargs: Any) -> Any:
        """timeAdvanceRequestAvailable; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unassociateRegionsForUpdates(self, *args: Any, **kwargs: Any) -> Any:
        """unassociateRegionsForUpdates; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unconditionalAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """unconditionalAttributeOwnershipDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unpublishInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """unpublishInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unpublishObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """unpublishObjectClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unpublishObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """unpublishObjectClassAttributes; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeInteractionClassWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeInteractionClassWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeObjectClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeObjectClassAttributes; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeObjectClassAttributesWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeObjectClassAttributesWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def updateAttributeValues(self, *args: Any, **kwargs: Any) -> Any:
        """updateAttributeValues; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

class FederateAmbassador:
    """No-op federate callback base preserving source method names."""

    def announceSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:
        """announceSynchronizationPoint; 2 source overload(s). Override in a federate."""
        return None

    def attributeIsNotOwned(self, *args: Any, **kwargs: Any) -> Any:
        """attributeIsNotOwned; 2 source overload(s). Override in a federate."""
        return None

    def attributeIsOwnedByRTI(self, *args: Any, **kwargs: Any) -> Any:
        """attributeIsOwnedByRTI; 2 source overload(s). Override in a federate."""
        return None

    def attributeOwnershipAcquisitionNotification(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipAcquisitionNotification; 2 source overload(s). Override in a federate."""
        return None

    def attributeOwnershipUnavailable(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipUnavailable; 2 source overload(s). Override in a federate."""
        return None

    def attributesInScope(self, *args: Any, **kwargs: Any) -> Any:
        """attributesInScope; 2 source overload(s). Override in a federate."""
        return None

    def attributesOutOfScope(self, *args: Any, **kwargs: Any) -> Any:
        """attributesOutOfScope; 2 source overload(s). Override in a federate."""
        return None

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any, **kwargs: Any) -> Any:
        """confirmAttributeOwnershipAcquisitionCancellation; 2 source overload(s). Override in a federate."""
        return None

    def confirmAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """confirmAttributeTransportationTypeChange; 2 source overload(s). Override in a federate."""
        return None

    def confirmInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """confirmInteractionTransportationTypeChange; 2 source overload(s). Override in a federate."""
        return None

    def connectionLost(self, *args: Any, **kwargs: Any) -> Any:
        """connectionLost; 2 source overload(s). Override in a federate."""
        return None

    def discoverObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """discoverObjectInstance; 4 source overload(s). Override in a federate."""
        return None

    def federationNotRestored(self, *args: Any, **kwargs: Any) -> Any:
        """federationNotRestored; 2 source overload(s). Override in a federate."""
        return None

    def federationNotSaved(self, *args: Any, **kwargs: Any) -> Any:
        """federationNotSaved; 2 source overload(s). Override in a federate."""
        return None

    def federationRestoreBegun(self, *args: Any, **kwargs: Any) -> Any:
        """federationRestoreBegun; 2 source overload(s). Override in a federate."""
        return None

    def federationRestoreStatusResponse(self, *args: Any, **kwargs: Any) -> Any:
        """federationRestoreStatusResponse; 2 source overload(s). Override in a federate."""
        return None

    def federationRestored(self, *args: Any, **kwargs: Any) -> Any:
        """federationRestored; 2 source overload(s). Override in a federate."""
        return None

    def federationSaveStatusResponse(self, *args: Any, **kwargs: Any) -> Any:
        """federationSaveStatusResponse; 2 source overload(s). Override in a federate."""
        return None

    def federationSaved(self, *args: Any, **kwargs: Any) -> Any:
        """federationSaved; 2 source overload(s). Override in a federate."""
        return None

    def federationSynchronized(self, *args: Any, **kwargs: Any) -> Any:
        """federationSynchronized; 2 source overload(s). Override in a federate."""
        return None

    def getProducingFederate(self, *args: Any, **kwargs: Any) -> Any:
        """getProducingFederate; 3 source overload(s). Override in a federate."""
        return None

    def getSentRegions(self, *args: Any, **kwargs: Any) -> Any:
        """getSentRegions; 2 source overload(s). Override in a federate."""
        return None

    def hasProducingFederate(self, *args: Any, **kwargs: Any) -> Any:
        """hasProducingFederate; 3 source overload(s). Override in a federate."""
        return None

    def hasSentRegions(self, *args: Any, **kwargs: Any) -> Any:
        """hasSentRegions; 2 source overload(s). Override in a federate."""
        return None

    def informAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:
        """informAttributeOwnership; 2 source overload(s). Override in a federate."""
        return None

    def initiateFederateRestore(self, *args: Any, **kwargs: Any) -> Any:
        """initiateFederateRestore; 2 source overload(s). Override in a federate."""
        return None

    def initiateFederateSave(self, *args: Any, **kwargs: Any) -> Any:
        """initiateFederateSave; 4 source overload(s). Override in a federate."""
        return None

    def multipleObjectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:
        """multipleObjectInstanceNameReservationFailed; 2 source overload(s). Override in a federate."""
        return None

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """multipleObjectInstanceNameReservationSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def objectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:
        """objectInstanceNameReservationFailed; 2 source overload(s). Override in a federate."""
        return None

    def objectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """objectInstanceNameReservationSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def provideAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:
        """provideAttributeValueUpdate; 2 source overload(s). Override in a federate."""
        return None

    def receiveInteraction(self, *args: Any, **kwargs: Any) -> Any:
        """receiveInteraction; 6 source overload(s). Override in a federate."""
        return None

    def reflectAttributeValues(self, *args: Any, **kwargs: Any) -> Any:
        """reflectAttributeValues; 6 source overload(s). Override in a federate."""
        return None

    def removeObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """removeObjectInstance; 6 source overload(s). Override in a federate."""
        return None

    def reportAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """reportAttributeTransportationType; 2 source overload(s). Override in a federate."""
        return None

    def reportFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:
        """reportFederationExecutions; 2 source overload(s). Override in a federate."""
        return None

    def reportInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """reportInteractionTransportationType; 2 source overload(s). Override in a federate."""
        return None

    def requestAttributeOwnershipAssumption(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeOwnershipAssumption; 2 source overload(s). Override in a federate."""
        return None

    def requestAttributeOwnershipRelease(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeOwnershipRelease; 2 source overload(s). Override in a federate."""
        return None

    def requestDivestitureConfirmation(self, *args: Any, **kwargs: Any) -> Any:
        """requestDivestitureConfirmation; 2 source overload(s). Override in a federate."""
        return None

    def requestFederationRestoreFailed(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationRestoreFailed; 2 source overload(s). Override in a federate."""
        return None

    def requestFederationRestoreSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationRestoreSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def requestRetraction(self, *args: Any, **kwargs: Any) -> Any:
        """requestRetraction; 2 source overload(s). Override in a federate."""
        return None

    def startRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """startRegistrationForObjectClass; 2 source overload(s). Override in a federate."""
        return None

    def stopRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """stopRegistrationForObjectClass; 2 source overload(s). Override in a federate."""
        return None

    def synchronizationPointRegistrationFailed(self, *args: Any, **kwargs: Any) -> Any:
        """synchronizationPointRegistrationFailed; 2 source overload(s). Override in a federate."""
        return None

    def synchronizationPointRegistrationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """synchronizationPointRegistrationSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def timeAdvanceGrant(self, *args: Any, **kwargs: Any) -> Any:
        """timeAdvanceGrant; 2 source overload(s). Override in a federate."""
        return None

    def timeConstrainedEnabled(self, *args: Any, **kwargs: Any) -> Any:
        """timeConstrainedEnabled; 2 source overload(s). Override in a federate."""
        return None

    def timeRegulationEnabled(self, *args: Any, **kwargs: Any) -> Any:
        """timeRegulationEnabled; 2 source overload(s). Override in a federate."""
        return None

    def turnInteractionsOff(self, *args: Any, **kwargs: Any) -> Any:
        """turnInteractionsOff; 2 source overload(s). Override in a federate."""
        return None

    def turnInteractionsOn(self, *args: Any, **kwargs: Any) -> Any:
        """turnInteractionsOn; 2 source overload(s). Override in a federate."""
        return None

    def turnUpdatesOffForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """turnUpdatesOffForObjectInstance; 2 source overload(s). Override in a federate."""
        return None

    def turnUpdatesOnForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """turnUpdatesOnForObjectInstance; 4 source overload(s). Override in a federate."""
        return None

RTIAmbassador = RTIambassador
NullFederateAmbassador = FederateAmbassador
__all__ = ["API_METADATA", "RTIambassador", "RTIAmbassador", "FederateAmbassador", "NullFederateAmbassador"]
