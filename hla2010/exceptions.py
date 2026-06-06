"""Exception hierarchy derived from the public IEEE 1516.1-2010 Java API files.

The Java binding declares checked exceptions on API methods. Python keeps the
standard names for adapter compatibility, but does not use checked exception
declarations.

Attribution: "Reprinted with permission from IEEE 1516.1(TM)-2010".
"""
from __future__ import annotations

class RTIexception(Exception):
    """Base class for HLA RTI exceptions."""

    def __init__(self, message: str | None = None, *, cause: BaseException | None = None):
        super().__init__(message if message is not None else self.__class__.__name__)
        self.cause = cause

# Python spelling alias; the Java API uses RTIexception.
RTIException = RTIexception

class AlreadyConnected(RTIexception):
    """HLA exception AlreadyConnected."""

class AsynchronousDeliveryAlreadyDisabled(RTIexception):
    """HLA exception AsynchronousDeliveryAlreadyDisabled."""

class AsynchronousDeliveryAlreadyEnabled(RTIexception):
    """HLA exception AsynchronousDeliveryAlreadyEnabled."""

class AttributeAcquisitionWasNotRequested(RTIexception):
    """HLA exception AttributeAcquisitionWasNotRequested."""

class AttributeAlreadyBeingAcquired(RTIexception):
    """HLA exception AttributeAlreadyBeingAcquired."""

class AttributeAlreadyBeingChanged(RTIexception):
    """HLA exception AttributeAlreadyBeingChanged."""

class AttributeAlreadyBeingDivested(RTIexception):
    """HLA exception AttributeAlreadyBeingDivested."""

class AttributeAlreadyOwned(RTIexception):
    """HLA exception AttributeAlreadyOwned."""

class AttributeDivestitureWasNotRequested(RTIexception):
    """HLA exception AttributeDivestitureWasNotRequested."""

class AttributeNotDefined(RTIexception):
    """HLA exception AttributeNotDefined."""

class AttributeNotOwned(RTIexception):
    """HLA exception AttributeNotOwned."""

class AttributeNotPublished(RTIexception):
    """HLA exception AttributeNotPublished."""

class AttributeNotRecognized(RTIexception):
    """HLA exception AttributeNotRecognized."""

class AttributeNotSubscribed(RTIexception):
    """HLA exception AttributeNotSubscribed."""

class AttributeRelevanceAdvisorySwitchIsOff(RTIexception):
    """HLA exception AttributeRelevanceAdvisorySwitchIsOff."""

class AttributeRelevanceAdvisorySwitchIsOn(RTIexception):
    """HLA exception AttributeRelevanceAdvisorySwitchIsOn."""

class AttributeScopeAdvisorySwitchIsOff(RTIexception):
    """HLA exception AttributeScopeAdvisorySwitchIsOff."""

class AttributeScopeAdvisorySwitchIsOn(RTIexception):
    """HLA exception AttributeScopeAdvisorySwitchIsOn."""

class CallNotAllowedFromWithinCallback(RTIexception):
    """HLA exception CallNotAllowedFromWithinCallback."""

class ConnectionFailed(RTIexception):
    """HLA exception ConnectionFailed."""

class CouldNotCreateLogicalTimeFactory(RTIexception):
    """HLA exception CouldNotCreateLogicalTimeFactory."""

class CouldNotDecode(RTIexception):
    """HLA exception CouldNotDecode."""

class CouldNotEncode(RTIexception):
    """HLA exception CouldNotEncode."""

class CouldNotOpenFDD(RTIexception):
    """HLA exception CouldNotOpenFDD."""

class CouldNotOpenMIM(RTIexception):
    """HLA exception CouldNotOpenMIM."""

class DeletePrivilegeNotHeld(RTIexception):
    """HLA exception DeletePrivilegeNotHeld."""

class DesignatorIsHLAstandardMIM(RTIexception):
    """HLA exception DesignatorIsHLAstandardMIM."""

class ErrorReadingFDD(RTIexception):
    """HLA exception ErrorReadingFDD."""

class ErrorReadingMIM(RTIexception):
    """HLA exception ErrorReadingMIM."""

class FederateAlreadyExecutionMember(RTIexception):
    """HLA exception FederateAlreadyExecutionMember."""

class FederateHandleNotKnown(RTIexception):
    """HLA exception FederateHandleNotKnown."""

class FederateHasNotBegunSave(RTIexception):
    """HLA exception FederateHasNotBegunSave."""

class FederateInternalError(RTIexception):
    """HLA exception FederateInternalError."""

class FederateIsExecutionMember(RTIexception):
    """HLA exception FederateIsExecutionMember."""

class FederateNameAlreadyInUse(RTIexception):
    """HLA exception FederateNameAlreadyInUse."""

class FederateNotExecutionMember(RTIexception):
    """HLA exception FederateNotExecutionMember."""

class FederateOwnsAttributes(RTIexception):
    """HLA exception FederateOwnsAttributes."""

class FederateServiceInvocationsAreBeingReportedViaMOM(RTIexception):
    """HLA exception FederateServiceInvocationsAreBeingReportedViaMOM."""

class FederateUnableToUseTime(RTIexception):
    """HLA exception FederateUnableToUseTime."""

class FederatesCurrentlyJoined(RTIexception):
    """HLA exception FederatesCurrentlyJoined."""

class FederationExecutionAlreadyExists(RTIexception):
    """HLA exception FederationExecutionAlreadyExists."""

class FederationExecutionDoesNotExist(RTIexception):
    """HLA exception FederationExecutionDoesNotExist."""

class IllegalName(RTIexception):
    """HLA exception IllegalName."""

class IllegalTimeArithmetic(RTIexception):
    """HLA exception IllegalTimeArithmetic."""

class InTimeAdvancingState(RTIexception):
    """HLA exception InTimeAdvancingState."""

class InconsistentFDD(RTIexception):
    """HLA exception InconsistentFDD."""

class InteractionClassAlreadyBeingChanged(RTIexception):
    """HLA exception InteractionClassAlreadyBeingChanged."""

class InteractionClassNotDefined(RTIexception):
    """HLA exception InteractionClassNotDefined."""

class InteractionClassNotPublished(RTIexception):
    """HLA exception InteractionClassNotPublished."""

class InteractionParameterNotDefined(RTIexception):
    """HLA exception InteractionParameterNotDefined."""

class InteractionRelevanceAdvisorySwitchIsOff(RTIexception):
    """HLA exception InteractionRelevanceAdvisorySwitchIsOff."""

class InteractionRelevanceAdvisorySwitchIsOn(RTIexception):
    """HLA exception InteractionRelevanceAdvisorySwitchIsOn."""

class InvalidAttributeHandle(RTIexception):
    """HLA exception InvalidAttributeHandle."""

class InvalidDimensionHandle(RTIexception):
    """HLA exception InvalidDimensionHandle."""

class InvalidFederateHandle(RTIexception):
    """HLA exception InvalidFederateHandle."""

class InvalidInteractionClassHandle(RTIexception):
    """HLA exception InvalidInteractionClassHandle."""

class InvalidLocalSettingsDesignator(RTIexception):
    """HLA exception InvalidLocalSettingsDesignator."""

class InvalidLogicalTime(RTIexception):
    """HLA exception InvalidLogicalTime."""

class InvalidLogicalTimeInterval(RTIexception):
    """HLA exception InvalidLogicalTimeInterval."""

class InvalidLookahead(RTIexception):
    """HLA exception InvalidLookahead."""

class InvalidMessageRetractionHandle(RTIexception):
    """HLA exception InvalidMessageRetractionHandle."""

class InvalidObjectClassHandle(RTIexception):
    """HLA exception InvalidObjectClassHandle."""

class InvalidOrderName(RTIexception):
    """HLA exception InvalidOrderName."""

class InvalidOrderType(RTIexception):
    """HLA exception InvalidOrderType."""

class InvalidParameterHandle(RTIexception):
    """HLA exception InvalidParameterHandle."""

class InvalidRangeBound(RTIexception):
    """HLA exception InvalidRangeBound."""

class InvalidRegion(RTIexception):
    """HLA exception InvalidRegion."""

class InvalidRegionContext(RTIexception):
    """HLA exception InvalidRegionContext."""

class InvalidResignAction(RTIexception):
    """HLA exception InvalidResignAction."""

class InvalidServiceGroup(RTIexception):
    """HLA exception InvalidServiceGroup."""

class InvalidTransportationName(RTIexception):
    """HLA exception InvalidTransportationName."""

class InvalidTransportationType(RTIexception):
    """HLA exception InvalidTransportationType."""

class InvalidUpdateRateDesignator(RTIexception):
    """HLA exception InvalidUpdateRateDesignator."""

class LogicalTimeAlreadyPassed(RTIexception):
    """HLA exception LogicalTimeAlreadyPassed."""

class MessageCanNoLongerBeRetracted(RTIexception):
    """HLA exception MessageCanNoLongerBeRetracted."""

class NameNotFound(RTIexception):
    """HLA exception NameNotFound."""

class NameSetWasEmpty(RTIexception):
    """HLA exception NameSetWasEmpty."""

class NoAcquisitionPending(RTIexception):
    """HLA exception NoAcquisitionPending."""

class NoRequestToEnableTimeConstrainedWasPending(RTIexception):
    """HLA exception NoRequestToEnableTimeConstrainedWasPending."""

class NoRequestToEnableTimeRegulationWasPending(RTIexception):
    """HLA exception NoRequestToEnableTimeRegulationWasPending."""

class NotConnected(RTIexception):
    """HLA exception NotConnected."""

class ObjectClassNotDefined(RTIexception):
    """HLA exception ObjectClassNotDefined."""

class ObjectClassNotPublished(RTIexception):
    """HLA exception ObjectClassNotPublished."""

class ObjectClassRelevanceAdvisorySwitchIsOff(RTIexception):
    """HLA exception ObjectClassRelevanceAdvisorySwitchIsOff."""

class ObjectClassRelevanceAdvisorySwitchIsOn(RTIexception):
    """HLA exception ObjectClassRelevanceAdvisorySwitchIsOn."""

class ObjectInstanceNameInUse(RTIexception):
    """HLA exception ObjectInstanceNameInUse."""

class ObjectInstanceNameNotReserved(RTIexception):
    """HLA exception ObjectInstanceNameNotReserved."""

class ObjectInstanceNotKnown(RTIexception):
    """HLA exception ObjectInstanceNotKnown."""

class OwnershipAcquisitionPending(RTIexception):
    """HLA exception OwnershipAcquisitionPending."""

class RTIinternalError(RTIexception):
    """HLA exception RTIinternalError."""

class RegionDoesNotContainSpecifiedDimension(RTIexception):
    """HLA exception RegionDoesNotContainSpecifiedDimension."""

class RegionInUseForUpdateOrSubscription(RTIexception):
    """HLA exception RegionInUseForUpdateOrSubscription."""

class RegionNotCreatedByThisFederate(RTIexception):
    """HLA exception RegionNotCreatedByThisFederate."""

class RequestForTimeConstrainedPending(RTIexception):
    """HLA exception RequestForTimeConstrainedPending."""

class RequestForTimeRegulationPending(RTIexception):
    """HLA exception RequestForTimeRegulationPending."""

class RestoreInProgress(RTIexception):
    """HLA exception RestoreInProgress."""

class RestoreNotInProgress(RTIexception):
    """HLA exception RestoreNotInProgress."""

class RestoreNotRequested(RTIexception):
    """HLA exception RestoreNotRequested."""

class SaveInProgress(RTIexception):
    """HLA exception SaveInProgress."""

class SaveNotInProgress(RTIexception):
    """HLA exception SaveNotInProgress."""

class SaveNotInitiated(RTIexception):
    """HLA exception SaveNotInitiated."""

class SynchronizationPointLabelNotAnnounced(RTIexception):
    """HLA exception SynchronizationPointLabelNotAnnounced."""

class TimeConstrainedAlreadyEnabled(RTIexception):
    """HLA exception TimeConstrainedAlreadyEnabled."""

class TimeConstrainedIsNotEnabled(RTIexception):
    """HLA exception TimeConstrainedIsNotEnabled."""

class TimeRegulationAlreadyEnabled(RTIexception):
    """HLA exception TimeRegulationAlreadyEnabled."""

class TimeRegulationIsNotEnabled(RTIexception):
    """HLA exception TimeRegulationIsNotEnabled."""

class UnableToPerformSave(RTIexception):
    """HLA exception UnableToPerformSave."""

class UnknownName(RTIexception):
    """HLA exception UnknownName."""

class UnsupportedCallbackModel(RTIexception):
    """HLA exception UnsupportedCallbackModel."""

__all__ = ['RTIexception', 'RTIException', 'AlreadyConnected', 'AsynchronousDeliveryAlreadyDisabled', 'AsynchronousDeliveryAlreadyEnabled', 'AttributeAcquisitionWasNotRequested', 'AttributeAlreadyBeingAcquired', 'AttributeAlreadyBeingChanged', 'AttributeAlreadyBeingDivested', 'AttributeAlreadyOwned', 'AttributeDivestitureWasNotRequested', 'AttributeNotDefined', 'AttributeNotOwned', 'AttributeNotPublished', 'AttributeNotRecognized', 'AttributeNotSubscribed', 'AttributeRelevanceAdvisorySwitchIsOff', 'AttributeRelevanceAdvisorySwitchIsOn', 'AttributeScopeAdvisorySwitchIsOff', 'AttributeScopeAdvisorySwitchIsOn', 'CallNotAllowedFromWithinCallback', 'ConnectionFailed', 'CouldNotCreateLogicalTimeFactory', 'CouldNotDecode', 'CouldNotEncode', 'CouldNotOpenFDD', 'CouldNotOpenMIM', 'DeletePrivilegeNotHeld', 'DesignatorIsHLAstandardMIM', 'ErrorReadingFDD', 'ErrorReadingMIM', 'FederateAlreadyExecutionMember', 'FederateHandleNotKnown', 'FederateHasNotBegunSave', 'FederateInternalError', 'FederateIsExecutionMember', 'FederateNameAlreadyInUse', 'FederateNotExecutionMember', 'FederateOwnsAttributes', 'FederateServiceInvocationsAreBeingReportedViaMOM', 'FederateUnableToUseTime', 'FederatesCurrentlyJoined', 'FederationExecutionAlreadyExists', 'FederationExecutionDoesNotExist', 'IllegalName', 'IllegalTimeArithmetic', 'InTimeAdvancingState', 'InconsistentFDD', 'InteractionClassAlreadyBeingChanged', 'InteractionClassNotDefined', 'InteractionClassNotPublished', 'InteractionParameterNotDefined', 'InteractionRelevanceAdvisorySwitchIsOff', 'InteractionRelevanceAdvisorySwitchIsOn', 'InvalidAttributeHandle', 'InvalidDimensionHandle', 'InvalidFederateHandle', 'InvalidInteractionClassHandle', 'InvalidLocalSettingsDesignator', 'InvalidLogicalTime', 'InvalidLogicalTimeInterval', 'InvalidLookahead', 'InvalidMessageRetractionHandle', 'InvalidObjectClassHandle', 'InvalidOrderName', 'InvalidOrderType', 'InvalidParameterHandle', 'InvalidRangeBound', 'InvalidRegion', 'InvalidRegionContext', 'InvalidResignAction', 'InvalidServiceGroup', 'InvalidTransportationName', 'InvalidTransportationType', 'InvalidUpdateRateDesignator', 'LogicalTimeAlreadyPassed', 'MessageCanNoLongerBeRetracted', 'NameNotFound', 'NameSetWasEmpty', 'NoAcquisitionPending', 'NoRequestToEnableTimeConstrainedWasPending', 'NoRequestToEnableTimeRegulationWasPending', 'NotConnected', 'ObjectClassNotDefined', 'ObjectClassNotPublished', 'ObjectClassRelevanceAdvisorySwitchIsOff', 'ObjectClassRelevanceAdvisorySwitchIsOn', 'ObjectInstanceNameInUse', 'ObjectInstanceNameNotReserved', 'ObjectInstanceNotKnown', 'OwnershipAcquisitionPending', 'RTIinternalError', 'RegionDoesNotContainSpecifiedDimension', 'RegionInUseForUpdateOrSubscription', 'RegionNotCreatedByThisFederate', 'RequestForTimeConstrainedPending', 'RequestForTimeRegulationPending', 'RestoreInProgress', 'RestoreNotInProgress', 'RestoreNotRequested', 'SaveInProgress', 'SaveNotInProgress', 'SaveNotInitiated', 'SynchronizationPointLabelNotAnnounced', 'TimeConstrainedAlreadyEnabled', 'TimeConstrainedIsNotEnabled', 'TimeRegulationAlreadyEnabled', 'TimeRegulationIsNotEnabled', 'UnableToPerformSave', 'UnknownName', 'UnsupportedCallbackModel']
