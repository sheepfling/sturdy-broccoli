"""Source-named HLA 1516.1-2010 API spec.

This module keeps the RTI ambassador surface close to the Java/C++ service
names while checking in explicit method definitions for static tools.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import Callable

from .spec_refs import method_reference
from .spec_sources import method_source_summary


def lower_camel_to_snake(name: str) -> str:
    """Convert a lowerCamelCase HLA method name to snake_case."""

    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def _method_doc(method_name: str) -> str:
    ref = method_reference(method_name)
    source_summary = method_source_summary(method_name)
    doc_parts = [method_name]
    if ref is not None:
        doc_parts.append(f"IEEE reference: {ref.label}.")
    if source_summary:
        doc_parts.append(f"Sources: {source_summary}.")
    return " ".join(doc_parts)


def _service_metadata(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_name = method_name  # type: ignore[attr-defined]
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name)
        return method

    return _decorate


def _callback(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_name = method_name  # type: ignore[attr-defined]
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name)
        return method

    return _decorate


class RTIambassadorSpec(ABC):
    """Source-named abstract contract for an HLA RTI ambassador."""

    @_service_metadata("abortFederationRestore")
    @abstractmethod
    def abortFederationRestore(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("abortFederationSave")
    @abstractmethod
    def abortFederationSave(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("associateRegionsForUpdates")
    @abstractmethod
    def associateRegionsForUpdates(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipAcquisition")
    @abstractmethod
    def attributeOwnershipAcquisition(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipAcquisitionIfAvailable")
    @abstractmethod
    def attributeOwnershipAcquisitionIfAvailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipDivestitureIfWanted")
    @abstractmethod
    def attributeOwnershipDivestitureIfWanted(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipReleaseDenied")
    @abstractmethod
    def attributeOwnershipReleaseDenied(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("cancelAttributeOwnershipAcquisition")
    @abstractmethod
    def cancelAttributeOwnershipAcquisition(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("cancelNegotiatedAttributeOwnershipDivestiture")
    @abstractmethod
    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("changeAttributeOrderType")
    @abstractmethod
    def changeAttributeOrderType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("changeInteractionOrderType")
    @abstractmethod
    def changeInteractionOrderType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("commitRegionModifications")
    @abstractmethod
    def commitRegionModifications(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("confirmDivestiture")
    @abstractmethod
    def confirmDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("connect")
    @abstractmethod
    def connect(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createFederationExecution")
    @abstractmethod
    def createFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createFederationExecutionWithMIM")
    @abstractmethod
    def createFederationExecutionWithMIM(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createRegion")
    @abstractmethod
    def createRegion(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeAttributeHandle")
    @abstractmethod
    def decodeAttributeHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeDimensionHandle")
    @abstractmethod
    def decodeDimensionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeFederateHandle")
    @abstractmethod
    def decodeFederateHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeInteractionClassHandle")
    @abstractmethod
    def decodeInteractionClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeMessageRetractionHandle")
    @abstractmethod
    def decodeMessageRetractionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeObjectClassHandle")
    @abstractmethod
    def decodeObjectClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeObjectInstanceHandle")
    @abstractmethod
    def decodeObjectInstanceHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeParameterHandle")
    @abstractmethod
    def decodeParameterHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeRegionHandle")
    @abstractmethod
    def decodeRegionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("deleteObjectInstance")
    @abstractmethod
    def deleteObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("deleteRegion")
    @abstractmethod
    def deleteRegion(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("destroyFederationExecution")
    @abstractmethod
    def destroyFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableAsynchronousDelivery")
    @abstractmethod
    def disableAsynchronousDelivery(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableAttributeRelevanceAdvisorySwitch")
    @abstractmethod
    def disableAttributeRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableAttributeScopeAdvisorySwitch")
    @abstractmethod
    def disableAttributeScopeAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableCallbacks")
    @abstractmethod
    def disableCallbacks(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableInteractionRelevanceAdvisorySwitch")
    @abstractmethod
    def disableInteractionRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableObjectClassRelevanceAdvisorySwitch")
    @abstractmethod
    def disableObjectClassRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableTimeConstrained")
    @abstractmethod
    def disableTimeConstrained(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableTimeRegulation")
    @abstractmethod
    def disableTimeRegulation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disconnect")
    @abstractmethod
    def disconnect(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAsynchronousDelivery")
    @abstractmethod
    def enableAsynchronousDelivery(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAttributeRelevanceAdvisorySwitch")
    @abstractmethod
    def enableAttributeRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAttributeScopeAdvisorySwitch")
    @abstractmethod
    def enableAttributeScopeAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableCallbacks")
    @abstractmethod
    def enableCallbacks(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableInteractionRelevanceAdvisorySwitch")
    @abstractmethod
    def enableInteractionRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableObjectClassRelevanceAdvisorySwitch")
    @abstractmethod
    def enableObjectClassRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableTimeConstrained")
    @abstractmethod
    def enableTimeConstrained(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableTimeRegulation")
    @abstractmethod
    def enableTimeRegulation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("evokeCallback")
    @abstractmethod
    def evokeCallback(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("evokeMultipleCallbacks")
    @abstractmethod
    def evokeMultipleCallbacks(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateRestoreComplete")
    @abstractmethod
    def federateRestoreComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateRestoreNotComplete")
    @abstractmethod
    def federateRestoreNotComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateSaveBegun")
    @abstractmethod
    def federateSaveBegun(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateSaveComplete")
    @abstractmethod
    def federateSaveComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateSaveNotComplete")
    @abstractmethod
    def federateSaveNotComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("flushQueueRequest")
    @abstractmethod
    def flushQueueRequest(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandle")
    @abstractmethod
    def getAttributeHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandleFactory")
    @abstractmethod
    def getAttributeHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandleSetFactory")
    @abstractmethod
    def getAttributeHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandleValueMapFactory")
    @abstractmethod
    def getAttributeHandleValueMapFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeName")
    @abstractmethod
    def getAttributeName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeSetRegionSetPairListFactory")
    @abstractmethod
    def getAttributeSetRegionSetPairListFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAutomaticResignDirective")
    @abstractmethod
    def getAutomaticResignDirective(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAvailableDimensionsForClassAttribute")
    @abstractmethod
    def getAvailableDimensionsForClassAttribute(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAvailableDimensionsForInteractionClass")
    @abstractmethod
    def getAvailableDimensionsForInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandle")
    @abstractmethod
    def getDimensionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandleFactory")
    @abstractmethod
    def getDimensionHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandleSet")
    @abstractmethod
    def getDimensionHandleSet(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandleSetFactory")
    @abstractmethod
    def getDimensionHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionName")
    @abstractmethod
    def getDimensionName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionUpperBound")
    @abstractmethod
    def getDimensionUpperBound(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateHandle")
    @abstractmethod
    def getFederateHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateHandleFactory")
    @abstractmethod
    def getFederateHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateHandleSetFactory")
    @abstractmethod
    def getFederateHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateName")
    @abstractmethod
    def getFederateName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getHLAversion")
    @abstractmethod
    def getHLAversion(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getInteractionClassHandle")
    @abstractmethod
    def getInteractionClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getInteractionClassHandleFactory")
    @abstractmethod
    def getInteractionClassHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getInteractionClassName")
    @abstractmethod
    def getInteractionClassName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getKnownObjectClassHandle")
    @abstractmethod
    def getKnownObjectClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectClassHandle")
    @abstractmethod
    def getObjectClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectClassHandleFactory")
    @abstractmethod
    def getObjectClassHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectClassName")
    @abstractmethod
    def getObjectClassName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectInstanceHandle")
    @abstractmethod
    def getObjectInstanceHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectInstanceHandleFactory")
    @abstractmethod
    def getObjectInstanceHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectInstanceName")
    @abstractmethod
    def getObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getOrderName")
    @abstractmethod
    def getOrderName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getOrderType")
    @abstractmethod
    def getOrderType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterHandle")
    @abstractmethod
    def getParameterHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterHandleFactory")
    @abstractmethod
    def getParameterHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterHandleValueMapFactory")
    @abstractmethod
    def getParameterHandleValueMapFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterName")
    @abstractmethod
    def getParameterName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getRangeBounds")
    @abstractmethod
    def getRangeBounds(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getRegionHandleSetFactory")
    @abstractmethod
    def getRegionHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTimeFactory")
    @abstractmethod
    def getTimeFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationName")
    @abstractmethod
    def getTransportationName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationType")
    @abstractmethod
    def getTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationTypeHandle")
    @abstractmethod
    def getTransportationTypeHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationTypeHandleFactory")
    @abstractmethod
    def getTransportationTypeHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationTypeName")
    @abstractmethod
    def getTransportationTypeName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getUpdateRateValue")
    @abstractmethod
    def getUpdateRateValue(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getUpdateRateValueForAttribute")
    @abstractmethod
    def getUpdateRateValueForAttribute(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("isAttributeOwnedByFederate")
    @abstractmethod
    def isAttributeOwnedByFederate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("joinFederationExecution")
    @abstractmethod
    def joinFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("listFederationExecutions")
    @abstractmethod
    def listFederationExecutions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("localDeleteObjectInstance")
    @abstractmethod
    def localDeleteObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("modifyLookahead")
    @abstractmethod
    def modifyLookahead(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("negotiatedAttributeOwnershipDivestiture")
    @abstractmethod
    def negotiatedAttributeOwnershipDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("nextMessageRequest")
    @abstractmethod
    def nextMessageRequest(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("nextMessageRequestAvailable")
    @abstractmethod
    def nextMessageRequestAvailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("normalizeFederateHandle")
    @abstractmethod
    def normalizeFederateHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("normalizeServiceGroup")
    @abstractmethod
    def normalizeServiceGroup(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("publishInteractionClass")
    @abstractmethod
    def publishInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("publishObjectClassAttributes")
    @abstractmethod
    def publishObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryAttributeOwnership")
    @abstractmethod
    def queryAttributeOwnership(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryAttributeTransportationType")
    @abstractmethod
    def queryAttributeTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryFederationRestoreStatus")
    @abstractmethod
    def queryFederationRestoreStatus(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryFederationSaveStatus")
    @abstractmethod
    def queryFederationSaveStatus(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryGALT")
    @abstractmethod
    def queryGALT(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryInteractionTransportationType")
    @abstractmethod
    def queryInteractionTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryLITS")
    @abstractmethod
    def queryLITS(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryLogicalTime")
    @abstractmethod
    def queryLogicalTime(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryLookahead")
    @abstractmethod
    def queryLookahead(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("registerFederationSynchronizationPoint")
    @abstractmethod
    def registerFederationSynchronizationPoint(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("registerObjectInstance")
    @abstractmethod
    def registerObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("registerObjectInstanceWithRegions")
    @abstractmethod
    def registerObjectInstanceWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("releaseMultipleObjectInstanceName")
    @abstractmethod
    def releaseMultipleObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("releaseObjectInstanceName")
    @abstractmethod
    def releaseObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestAttributeTransportationTypeChange")
    @abstractmethod
    def requestAttributeTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestAttributeValueUpdate")
    @abstractmethod
    def requestAttributeValueUpdate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestAttributeValueUpdateWithRegions")
    @abstractmethod
    def requestAttributeValueUpdateWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestFederationRestore")
    @abstractmethod
    def requestFederationRestore(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestFederationSave")
    @abstractmethod
    def requestFederationSave(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestInteractionTransportationTypeChange")
    @abstractmethod
    def requestInteractionTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("reserveMultipleObjectInstanceName")
    @abstractmethod
    def reserveMultipleObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("reserveObjectInstanceName")
    @abstractmethod
    def reserveObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("resignFederationExecution")
    @abstractmethod
    def resignFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("retract")
    @abstractmethod
    def retract(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("sendInteraction")
    @abstractmethod
    def sendInteraction(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("sendInteractionWithRegions")
    @abstractmethod
    def sendInteractionWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("setAutomaticResignDirective")
    @abstractmethod
    def setAutomaticResignDirective(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("setRangeBounds")
    @abstractmethod
    def setRangeBounds(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClass")
    @abstractmethod
    def subscribeInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClassPassively")
    @abstractmethod
    def subscribeInteractionClassPassively(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClassPassivelyWithRegions")
    @abstractmethod
    def subscribeInteractionClassPassivelyWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClassWithRegions")
    @abstractmethod
    def subscribeInteractionClassWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributes")
    @abstractmethod
    def subscribeObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributesPassively")
    @abstractmethod
    def subscribeObjectClassAttributesPassively(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributesPassivelyWithRegions")
    @abstractmethod
    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributesWithRegions")
    @abstractmethod
    def subscribeObjectClassAttributesWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("synchronizationPointAchieved")
    @abstractmethod
    def synchronizationPointAchieved(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("timeAdvanceRequest")
    @abstractmethod
    def timeAdvanceRequest(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("timeAdvanceRequestAvailable")
    @abstractmethod
    def timeAdvanceRequestAvailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unassociateRegionsForUpdates")
    @abstractmethod
    def unassociateRegionsForUpdates(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unconditionalAttributeOwnershipDivestiture")
    @abstractmethod
    def unconditionalAttributeOwnershipDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unpublishInteractionClass")
    @abstractmethod
    def unpublishInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unpublishObjectClass")
    @abstractmethod
    def unpublishObjectClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unpublishObjectClassAttributes")
    @abstractmethod
    def unpublishObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeInteractionClass")
    @abstractmethod
    def unsubscribeInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeInteractionClassWithRegions")
    @abstractmethod
    def unsubscribeInteractionClassWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeObjectClass")
    @abstractmethod
    def unsubscribeObjectClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeObjectClassAttributes")
    @abstractmethod
    def unsubscribeObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeObjectClassAttributesWithRegions")
    @abstractmethod
    def unsubscribeObjectClassAttributesWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("updateAttributeValues")
    @abstractmethod
    def updateAttributeValues(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        raise NotImplementedError

class FederateAmbassadorSpec:
    """No-op prototype base for HLA federate callbacks."""

    @_callback("announceSynchronizationPoint")
    def announce_synchronization_point(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("announceSynchronizationPoint")
    def announceSynchronizationPoint(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.announce_synchronization_point(*args, **kwargs)

    @_callback("attributeIsNotOwned")
    def attribute_is_not_owned(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("attributeIsNotOwned")
    def attributeIsNotOwned(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_is_not_owned(*args, **kwargs)

    @_callback("attributeIsOwnedByRTI")
    def attribute_is_owned_by_rti(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("attributeIsOwnedByRTI")
    def attributeIsOwnedByRTI(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_is_owned_by_rti(*args, **kwargs)

    @_callback("attributeOwnershipAcquisitionNotification")
    def attribute_ownership_acquisition_notification(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("attributeOwnershipAcquisitionNotification")
    def attributeOwnershipAcquisitionNotification(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_ownership_acquisition_notification(*args, **kwargs)

    @_callback("attributeOwnershipUnavailable")
    def attribute_ownership_unavailable(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("attributeOwnershipUnavailable")
    def attributeOwnershipUnavailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_ownership_unavailable(*args, **kwargs)

    @_callback("attributesInScope")
    def attributes_in_scope(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("attributesInScope")
    def attributesInScope(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attributes_in_scope(*args, **kwargs)

    @_callback("attributesOutOfScope")
    def attributes_out_of_scope(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("attributesOutOfScope")
    def attributesOutOfScope(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attributes_out_of_scope(*args, **kwargs)

    @_callback("confirmAttributeOwnershipAcquisitionCancellation")
    def confirm_attribute_ownership_acquisition_cancellation(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("confirmAttributeOwnershipAcquisitionCancellation")
    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_attribute_ownership_acquisition_cancellation(*args, **kwargs)

    @_callback("confirmAttributeTransportationTypeChange")
    def confirm_attribute_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("confirmAttributeTransportationTypeChange")
    def confirmAttributeTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_attribute_transportation_type_change(*args, **kwargs)

    @_callback("confirmInteractionTransportationTypeChange")
    def confirm_interaction_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("confirmInteractionTransportationTypeChange")
    def confirmInteractionTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_interaction_transportation_type_change(*args, **kwargs)

    @_callback("connectionLost")
    def connection_lost(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("connectionLost")
    def connectionLost(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.connection_lost(*args, **kwargs)

    @_callback("discoverObjectInstance")
    def discover_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("discoverObjectInstance")
    def discoverObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.discover_object_instance(*args, **kwargs)

    @_callback("federationNotRestored")
    def federation_not_restored(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationNotRestored")
    def federationNotRestored(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_not_restored(*args, **kwargs)

    @_callback("federationNotSaved")
    def federation_not_saved(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationNotSaved")
    def federationNotSaved(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_not_saved(*args, **kwargs)

    @_callback("federationRestoreBegun")
    def federation_restore_begun(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationRestoreBegun")
    def federationRestoreBegun(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_restore_begun(*args, **kwargs)

    @_callback("federationRestoreStatusResponse")
    def federation_restore_status_response(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationRestoreStatusResponse")
    def federationRestoreStatusResponse(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_restore_status_response(*args, **kwargs)

    @_callback("federationRestored")
    def federation_restored(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationRestored")
    def federationRestored(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_restored(*args, **kwargs)

    @_callback("federationSaveStatusResponse")
    def federation_save_status_response(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationSaveStatusResponse")
    def federationSaveStatusResponse(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_save_status_response(*args, **kwargs)

    @_callback("federationSaved")
    def federation_saved(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationSaved")
    def federationSaved(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_saved(*args, **kwargs)

    @_callback("federationSynchronized")
    def federation_synchronized(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationSynchronized")
    def federationSynchronized(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_synchronized(*args, **kwargs)

    @_callback("getProducingFederate")
    def get_producing_federate(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("getProducingFederate")
    def getProducingFederate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_producing_federate(*args, **kwargs)

    @_callback("getSentRegions")
    def get_sent_regions(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("getSentRegions")
    def getSentRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_sent_regions(*args, **kwargs)

    @_callback("hasProducingFederate")
    def has_producing_federate(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("hasProducingFederate")
    def hasProducingFederate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.has_producing_federate(*args, **kwargs)

    @_callback("hasSentRegions")
    def has_sent_regions(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("hasSentRegions")
    def hasSentRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.has_sent_regions(*args, **kwargs)

    @_callback("informAttributeOwnership")
    def inform_attribute_ownership(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("informAttributeOwnership")
    def informAttributeOwnership(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.inform_attribute_ownership(*args, **kwargs)

    @_callback("initiateFederateRestore")
    def initiate_federate_restore(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("initiateFederateRestore")
    def initiateFederateRestore(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.initiate_federate_restore(*args, **kwargs)

    @_callback("initiateFederateSave")
    def initiate_federate_save(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("initiateFederateSave")
    def initiateFederateSave(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.initiate_federate_save(*args, **kwargs)

    @_callback("multipleObjectInstanceNameReservationFailed")
    def multiple_object_instance_name_reservation_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("multipleObjectInstanceNameReservationFailed")
    def multipleObjectInstanceNameReservationFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.multiple_object_instance_name_reservation_failed(*args, **kwargs)

    @_callback("multipleObjectInstanceNameReservationSucceeded")
    def multiple_object_instance_name_reservation_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("multipleObjectInstanceNameReservationSucceeded")
    def multipleObjectInstanceNameReservationSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.multiple_object_instance_name_reservation_succeeded(*args, **kwargs)

    @_callback("objectInstanceNameReservationFailed")
    def object_instance_name_reservation_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("objectInstanceNameReservationFailed")
    def objectInstanceNameReservationFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.object_instance_name_reservation_failed(*args, **kwargs)

    @_callback("objectInstanceNameReservationSucceeded")
    def object_instance_name_reservation_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("objectInstanceNameReservationSucceeded")
    def objectInstanceNameReservationSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.object_instance_name_reservation_succeeded(*args, **kwargs)

    @_callback("provideAttributeValueUpdate")
    def provide_attribute_value_update(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("provideAttributeValueUpdate")
    def provideAttributeValueUpdate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.provide_attribute_value_update(*args, **kwargs)

    @_callback("receiveInteraction")
    def receive_interaction(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("receiveInteraction")
    def receiveInteraction(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.receive_interaction(*args, **kwargs)

    @_callback("reflectAttributeValues")
    def reflect_attribute_values(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reflectAttributeValues")
    def reflectAttributeValues(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.reflect_attribute_values(*args, **kwargs)

    @_callback("removeObjectInstance")
    def remove_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("removeObjectInstance")
    def removeObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.remove_object_instance(*args, **kwargs)

    @_callback("reportAttributeTransportationType")
    def report_attribute_transportation_type(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reportAttributeTransportationType")
    def reportAttributeTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.report_attribute_transportation_type(*args, **kwargs)

    @_callback("reportFederationExecutions")
    def report_federation_executions(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reportFederationExecutions")
    def reportFederationExecutions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.report_federation_executions(*args, **kwargs)

    @_callback("reportInteractionTransportationType")
    def report_interaction_transportation_type(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reportInteractionTransportationType")
    def reportInteractionTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.report_interaction_transportation_type(*args, **kwargs)

    @_callback("requestAttributeOwnershipAssumption")
    def request_attribute_ownership_assumption(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestAttributeOwnershipAssumption")
    def requestAttributeOwnershipAssumption(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_attribute_ownership_assumption(*args, **kwargs)

    @_callback("requestAttributeOwnershipRelease")
    def request_attribute_ownership_release(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestAttributeOwnershipRelease")
    def requestAttributeOwnershipRelease(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_attribute_ownership_release(*args, **kwargs)

    @_callback("requestDivestitureConfirmation")
    def request_divestiture_confirmation(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestDivestitureConfirmation")
    def requestDivestitureConfirmation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_divestiture_confirmation(*args, **kwargs)

    @_callback("requestFederationRestoreFailed")
    def request_federation_restore_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestFederationRestoreFailed")
    def requestFederationRestoreFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_federation_restore_failed(*args, **kwargs)

    @_callback("requestFederationRestoreSucceeded")
    def request_federation_restore_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestFederationRestoreSucceeded")
    def requestFederationRestoreSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_federation_restore_succeeded(*args, **kwargs)

    @_callback("requestRetraction")
    def request_retraction(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestRetraction")
    def requestRetraction(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_retraction(*args, **kwargs)

    @_callback("startRegistrationForObjectClass")
    def start_registration_for_object_class(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("startRegistrationForObjectClass")
    def startRegistrationForObjectClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.start_registration_for_object_class(*args, **kwargs)

    @_callback("stopRegistrationForObjectClass")
    def stop_registration_for_object_class(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("stopRegistrationForObjectClass")
    def stopRegistrationForObjectClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.stop_registration_for_object_class(*args, **kwargs)

    @_callback("synchronizationPointRegistrationFailed")
    def synchronization_point_registration_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("synchronizationPointRegistrationFailed")
    def synchronizationPointRegistrationFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.synchronization_point_registration_failed(*args, **kwargs)

    @_callback("synchronizationPointRegistrationSucceeded")
    def synchronization_point_registration_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("synchronizationPointRegistrationSucceeded")
    def synchronizationPointRegistrationSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.synchronization_point_registration_succeeded(*args, **kwargs)

    @_callback("timeAdvanceGrant")
    def time_advance_grant(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("timeAdvanceGrant")
    def timeAdvanceGrant(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_advance_grant(*args, **kwargs)

    @_callback("timeConstrainedEnabled")
    def time_constrained_enabled(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("timeConstrainedEnabled")
    def timeConstrainedEnabled(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_constrained_enabled(*args, **kwargs)

    @_callback("timeRegulationEnabled")
    def time_regulation_enabled(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("timeRegulationEnabled")
    def timeRegulationEnabled(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_regulation_enabled(*args, **kwargs)

    @_callback("turnInteractionsOff")
    def turn_interactions_off(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnInteractionsOff")
    def turnInteractionsOff(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_interactions_off(*args, **kwargs)

    @_callback("turnInteractionsOn")
    def turn_interactions_on(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnInteractionsOn")
    def turnInteractionsOn(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_interactions_on(*args, **kwargs)

    @_callback("turnUpdatesOffForObjectInstance")
    def turn_updates_off_for_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnUpdatesOffForObjectInstance")
    def turnUpdatesOffForObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_updates_off_for_object_instance(*args, **kwargs)

    @_callback("turnUpdatesOnForObjectInstance")
    def turn_updates_on_for_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnUpdatesOnForObjectInstance")
    def turnUpdatesOnForObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_updates_on_for_object_instance(*args, **kwargs)

__all__ = [
    "FederateAmbassadorSpec",
    "RTIambassadorSpec",
    "lower_camel_to_snake",
]
