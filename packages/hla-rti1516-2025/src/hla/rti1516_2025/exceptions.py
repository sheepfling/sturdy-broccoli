"""IEEE 1516.1-2025 RTI exception hierarchy.

Sources: Java hla/rti1516_2025/exceptions/*.java plus C++ RTI/Exception.h advisory-switch compatibility exceptions.
"""

class RTIexception(Exception):
    def __init__(self, message: str | None = None):
        if message is not None:
            super().__init__(message)
        else:
            super().__init__()

        self.message = message


class AlreadyConnected(RTIexception):
    pass


class AsynchronousDeliveryAlreadyDisabled(RTIexception):
    pass


class AsynchronousDeliveryAlreadyEnabled(RTIexception):
    pass


class AttributeAcquisitionWasNotRequested(RTIexception):
    pass


class AttributeAlreadyBeingAcquired(RTIexception):
    pass


class AttributeAlreadyBeingChanged(RTIexception):
    pass


class AttributeAlreadyBeingDivested(RTIexception):
    pass


class AttributeAlreadyOwned(RTIexception):
    pass


class AttributeDivestitureWasNotRequested(RTIexception):
    pass


class AttributeNotDefined(RTIexception):
    pass


class AttributeNotOwned(RTIexception):
    pass


class AttributeNotPublished(RTIexception):
    pass


class CallNotAllowedFromWithinCallback(RTIexception):
    pass


class ConnectionFailed(RTIexception):
    pass


class CouldNotCreateLogicalTimeFactory(RTIexception):
    pass


class CouldNotDecode(RTIexception):
    pass


class CouldNotEncode(RTIexception):
    pass


class CouldNotOpenFOM(RTIexception):
    pass


class CouldNotOpenMIM(RTIexception):
    pass


class DeletePrivilegeNotHeld(RTIexception):
    pass


class DesignatorIsHLAstandardMIM(RTIexception):
    pass


class ErrorReadingFOM(RTIexception):
    pass


class ErrorReadingMIM(RTIexception):
    pass


class FederateAlreadyExecutionMember(RTIexception):
    pass


class FederateHandleNotKnown(RTIexception):
    pass


class FederateHasNotBegunSave(RTIexception):
    pass


class FederateInternalError(RTIexception):
    pass


class FederateIsExecutionMember(RTIexception):
    pass


class FederateNameAlreadyInUse(RTIexception):
    pass


class FederateNotExecutionMember(RTIexception):
    pass


class FederateOwnsAttributes(RTIexception):
    pass


class FederatesCurrentlyJoined(RTIexception):
    pass


class FederateServiceInvocationsAreBeingReportedViaMOM(RTIexception):
    pass


class FederateUnableToUseTime(RTIexception):
    pass


class FederationExecutionAlreadyExists(RTIexception):
    pass


class FederationExecutionDoesNotExist(RTIexception):
    pass


class IllegalName(RTIexception):
    pass


class IllegalTimeArithmetic(RTIexception):
    pass


class InconsistentFOM(RTIexception):
    pass


class InteractionClassAlreadyBeingChanged(RTIexception):
    pass


class InteractionClassNotDefined(RTIexception):
    pass


class InteractionClassNotPublished(RTIexception):
    pass


class InteractionParameterNotDefined(RTIexception):
    pass


class InTimeAdvancingState(RTIexception):
    pass


class InvalidAttributeHandle(RTIexception):
    pass


class InvalidCredentials(RTIexception):
    pass


class InvalidDimensionHandle(RTIexception):
    pass


class InvalidFederateHandle(RTIexception):
    pass


class InvalidFOM(RTIexception):
    pass


class InvalidInteractionClassHandle(RTIexception):
    pass


class InvalidLogicalTime(RTIexception):
    pass


class InvalidLogicalTimeInterval(RTIexception):
    pass


class InvalidLookahead(RTIexception):
    pass


class InvalidMessageRetractionHandle(RTIexception):
    pass


class InvalidMIM(RTIexception):
    pass


class InvalidObjectClassHandle(RTIexception):
    pass


class InvalidObjectInstanceHandle(RTIexception):
    pass


class InvalidOrderName(RTIexception):
    pass


class InvalidOrderType(RTIexception):
    pass


class InvalidParameterHandle(RTIexception):
    pass


class InvalidRangeBound(RTIexception):
    pass


class InvalidRegion(RTIexception):
    pass


class InvalidRegionContext(RTIexception):
    pass


class InvalidResignAction(RTIexception):
    pass


class InvalidServiceGroup(RTIexception):
    pass


class InvalidTransportationName(RTIexception):
    pass


class InvalidTransportationTypeHandle(RTIexception):
    pass


class InvalidUpdateRateDesignator(RTIexception):
    pass


class LogicalTimeAlreadyPassed(RTIexception):
    pass


class MessageCanNoLongerBeRetracted(RTIexception):
    pass


class NameNotFound(RTIexception):
    pass


class NameSetWasEmpty(RTIexception):
    pass


class NoAcquisitionPending(RTIexception):
    pass


class NotConnected(RTIexception):
    pass


class ObjectClassNotDefined(RTIexception):
    pass


class ObjectClassNotPublished(RTIexception):
    pass


class ObjectInstanceNameInUse(RTIexception):
    pass


class ObjectInstanceNameNotReserved(RTIexception):
    pass


class ObjectInstanceNotKnown(RTIexception):
    pass


class OwnershipAcquisitionPending(RTIexception):
    pass


class RegionDoesNotContainSpecifiedDimension(RTIexception):
    pass


class RegionInUseForUpdateOrSubscription(RTIexception):
    pass


class RegionNotCreatedByThisFederate(RTIexception):
    pass


class ReportServiceInvocationsAreSubscribed(RTIexception):
    pass


class RequestForTimeConstrainedPending(RTIexception):
    pass


class RequestForTimeRegulationPending(RTIexception):
    pass


class RestoreInProgress(RTIexception):
    pass


class RestoreNotInProgress(RTIexception):
    pass


class RestoreNotRequested(RTIexception):
    pass


class RTIinternalError(RTIexception):
    pass


class SaveInProgress(RTIexception):
    pass


class SaveNotInitiated(RTIexception):
    pass


class SaveNotInProgress(RTIexception):
    pass


class SynchronizationPointLabelNotAnnounced(RTIexception):
    pass


class TimeConstrainedAlreadyEnabled(RTIexception):
    pass


class TimeConstrainedIsNotEnabled(RTIexception):
    pass


class TimeRegulationAlreadyEnabled(RTIexception):
    pass


class TimeRegulationIsNotEnabled(RTIexception):
    pass


class Unauthorized(RTIexception):
    pass


class UnsupportedCallbackModel(RTIexception):
    pass


# C++ 1516.1-2025 compatibility exceptions present in RTI/Exception.h but not
# in the Java exception package. They are included so this Python model covers
# the union of the Java and C++ API surfaces.
class AttributeRelevanceAdvisorySwitchIsOff(RTIexception):
    pass


class AttributeRelevanceAdvisorySwitchIsOn(RTIexception):
    pass


class AttributeScopeAdvisorySwitchIsOff(RTIexception):
    pass


class AttributeScopeAdvisorySwitchIsOn(RTIexception):
    pass


class InteractionRelevanceAdvisorySwitchIsOff(RTIexception):
    pass


class InteractionRelevanceAdvisorySwitchIsOn(RTIexception):
    pass


class ObjectClassRelevanceAdvisorySwitchIsOff(RTIexception):
    pass


class ObjectClassRelevanceAdvisorySwitchIsOn(RTIexception):
    pass


class InternalError(RTIexception):
    pass
