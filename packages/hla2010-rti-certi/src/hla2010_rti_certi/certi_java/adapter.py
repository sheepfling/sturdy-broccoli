"""Adapter classes for Java-profile CERTI backends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hla2010.spec import FederateAmbassadorSpec, lower_camel_to_snake
from hla2010_rti_java_common import make_rti_ambassador
from hla2010_rti_java_common.java_common import invoke_java_federate_proxy_callback
from hla2010_rti_certi.certi import CERTIConfig, create_certi_backend
from .runtime import from_java_like, to_java_like


class _CERTIJavaFederateAdapter(FederateAmbassadorSpec):
    """Adapter that forwards native CERTI callbacks into a Java-style proxy."""

    def __init__(self, java_proxy: Any) -> None:
        self._java_proxy = java_proxy

    def _forward_callback(self, method_name: str, *args: Any) -> Any:
        return invoke_java_federate_proxy_callback(
            self._java_proxy,
            method_name,
            *(to_java_like(arg) for arg in args),
        )


    def connectionLost(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("connectionLost", *args)

    def connection_lost(self, *args: Any) -> Any:
        return self._forward_callback("connectionLost", *args)

    def reportFederationExecutions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("reportFederationExecutions", *args)

    def report_federation_executions(self, *args: Any) -> Any:
        return self._forward_callback("reportFederationExecutions", *args)

    def synchronizationPointRegistrationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("synchronizationPointRegistrationSucceeded", *args)

    def synchronization_point_registration_succeeded(self, *args: Any) -> Any:
        return self._forward_callback("synchronizationPointRegistrationSucceeded", *args)

    def synchronizationPointRegistrationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("synchronizationPointRegistrationFailed", *args)

    def synchronization_point_registration_failed(self, *args: Any) -> Any:
        return self._forward_callback("synchronizationPointRegistrationFailed", *args)

    def announceSynchronizationPoint(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("announceSynchronizationPoint", *args)

    def announce_synchronization_point(self, *args: Any) -> Any:
        return self._forward_callback("announceSynchronizationPoint", *args)

    def federationSynchronized(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationSynchronized", *args)

    def federation_synchronized(self, *args: Any) -> Any:
        return self._forward_callback("federationSynchronized", *args)

    def initiateFederateSave(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("initiateFederateSave", *args)

    def initiate_federate_save(self, *args: Any) -> Any:
        return self._forward_callback("initiateFederateSave", *args)

    def federationSaved(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationSaved", *args)

    def federation_saved(self, *args: Any) -> Any:
        return self._forward_callback("federationSaved", *args)

    def federationNotSaved(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationNotSaved", *args)

    def federation_not_saved(self, *args: Any) -> Any:
        return self._forward_callback("federationNotSaved", *args)

    def federationSaveStatusResponse(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationSaveStatusResponse", *args)

    def federation_save_status_response(self, *args: Any) -> Any:
        return self._forward_callback("federationSaveStatusResponse", *args)

    def requestFederationRestoreSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("requestFederationRestoreSucceeded", *args)

    def request_federation_restore_succeeded(self, *args: Any) -> Any:
        return self._forward_callback("requestFederationRestoreSucceeded", *args)

    def requestFederationRestoreFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("requestFederationRestoreFailed", *args)

    def request_federation_restore_failed(self, *args: Any) -> Any:
        return self._forward_callback("requestFederationRestoreFailed", *args)

    def federationRestoreBegun(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationRestoreBegun", *args)

    def federation_restore_begun(self, *args: Any) -> Any:
        return self._forward_callback("federationRestoreBegun", *args)

    def initiateFederateRestore(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("initiateFederateRestore", *args)

    def initiate_federate_restore(self, *args: Any) -> Any:
        return self._forward_callback("initiateFederateRestore", *args)

    def federationRestored(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationRestored", *args)

    def federation_restored(self, *args: Any) -> Any:
        return self._forward_callback("federationRestored", *args)

    def federationNotRestored(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationNotRestored", *args)

    def federation_not_restored(self, *args: Any) -> Any:
        return self._forward_callback("federationNotRestored", *args)

    def federationRestoreStatusResponse(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("federationRestoreStatusResponse", *args)

    def federation_restore_status_response(self, *args: Any) -> Any:
        return self._forward_callback("federationRestoreStatusResponse", *args)

    def startRegistrationForObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("startRegistrationForObjectClass", *args)

    def start_registration_for_object_class(self, *args: Any) -> Any:
        return self._forward_callback("startRegistrationForObjectClass", *args)

    def stopRegistrationForObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("stopRegistrationForObjectClass", *args)

    def stop_registration_for_object_class(self, *args: Any) -> Any:
        return self._forward_callback("stopRegistrationForObjectClass", *args)

    def turnInteractionsOn(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("turnInteractionsOn", *args)

    def turn_interactions_on(self, *args: Any) -> Any:
        return self._forward_callback("turnInteractionsOn", *args)

    def turnInteractionsOff(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("turnInteractionsOff", *args)

    def turn_interactions_off(self, *args: Any) -> Any:
        return self._forward_callback("turnInteractionsOff", *args)

    def objectInstanceNameReservationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("objectInstanceNameReservationSucceeded", *args)

    def object_instance_name_reservation_succeeded(self, *args: Any) -> Any:
        return self._forward_callback("objectInstanceNameReservationSucceeded", *args)

    def objectInstanceNameReservationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("objectInstanceNameReservationFailed", *args)

    def object_instance_name_reservation_failed(self, *args: Any) -> Any:
        return self._forward_callback("objectInstanceNameReservationFailed", *args)

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("multipleObjectInstanceNameReservationSucceeded", *args)

    def multiple_object_instance_name_reservation_succeeded(self, *args: Any) -> Any:
        return self._forward_callback("multipleObjectInstanceNameReservationSucceeded", *args)

    def multipleObjectInstanceNameReservationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("multipleObjectInstanceNameReservationFailed", *args)

    def multiple_object_instance_name_reservation_failed(self, *args: Any) -> Any:
        return self._forward_callback("multipleObjectInstanceNameReservationFailed", *args)

    def discoverObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("discoverObjectInstance", *args)

    def discover_object_instance(self, *args: Any) -> Any:
        return self._forward_callback("discoverObjectInstance", *args)

    def hasProducingFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("hasProducingFederate", *args)

    def has_producing_federate(self, *args: Any) -> Any:
        return self._forward_callback("hasProducingFederate", *args)

    def hasSentRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("hasSentRegions", *args)

    def has_sent_regions(self, *args: Any) -> Any:
        return self._forward_callback("hasSentRegions", *args)

    def getProducingFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("getProducingFederate", *args)

    def get_producing_federate(self, *args: Any) -> Any:
        return self._forward_callback("getProducingFederate", *args)

    def getSentRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("getSentRegions", *args)

    def get_sent_regions(self, *args: Any) -> Any:
        return self._forward_callback("getSentRegions", *args)

    def reflectAttributeValues(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("reflectAttributeValues", *args)

    def reflect_attribute_values(self, *args: Any) -> Any:
        return self._forward_callback("reflectAttributeValues", *args)

    def receiveInteraction(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("receiveInteraction", *args)

    def receive_interaction(self, *args: Any) -> Any:
        return self._forward_callback("receiveInteraction", *args)

    def removeObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("removeObjectInstance", *args)

    def remove_object_instance(self, *args: Any) -> Any:
        return self._forward_callback("removeObjectInstance", *args)

    def attributesInScope(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("attributesInScope", *args)

    def attributes_in_scope(self, *args: Any) -> Any:
        return self._forward_callback("attributesInScope", *args)

    def attributesOutOfScope(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("attributesOutOfScope", *args)

    def attributes_out_of_scope(self, *args: Any) -> Any:
        return self._forward_callback("attributesOutOfScope", *args)

    def provideAttributeValueUpdate(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("provideAttributeValueUpdate", *args)

    def provide_attribute_value_update(self, *args: Any) -> Any:
        return self._forward_callback("provideAttributeValueUpdate", *args)

    def turnUpdatesOnForObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("turnUpdatesOnForObjectInstance", *args)

    def turn_updates_on_for_object_instance(self, *args: Any) -> Any:
        return self._forward_callback("turnUpdatesOnForObjectInstance", *args)

    def turnUpdatesOffForObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("turnUpdatesOffForObjectInstance", *args)

    def turn_updates_off_for_object_instance(self, *args: Any) -> Any:
        return self._forward_callback("turnUpdatesOffForObjectInstance", *args)

    def confirmAttributeTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("confirmAttributeTransportationTypeChange", *args)

    def confirm_attribute_transportation_type_change(self, *args: Any) -> Any:
        return self._forward_callback("confirmAttributeTransportationTypeChange", *args)

    def reportAttributeTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("reportAttributeTransportationType", *args)

    def report_attribute_transportation_type(self, *args: Any) -> Any:
        return self._forward_callback("reportAttributeTransportationType", *args)

    def confirmInteractionTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("confirmInteractionTransportationTypeChange", *args)

    def confirm_interaction_transportation_type_change(self, *args: Any) -> Any:
        return self._forward_callback("confirmInteractionTransportationTypeChange", *args)

    def reportInteractionTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("reportInteractionTransportationType", *args)

    def report_interaction_transportation_type(self, *args: Any) -> Any:
        return self._forward_callback("reportInteractionTransportationType", *args)

    def requestAttributeOwnershipAssumption(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("requestAttributeOwnershipAssumption", *args)

    def request_attribute_ownership_assumption(self, *args: Any) -> Any:
        return self._forward_callback("requestAttributeOwnershipAssumption", *args)

    def requestDivestitureConfirmation(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("requestDivestitureConfirmation", *args)

    def request_divestiture_confirmation(self, *args: Any) -> Any:
        return self._forward_callback("requestDivestitureConfirmation", *args)

    def attributeOwnershipAcquisitionNotification(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("attributeOwnershipAcquisitionNotification", *args)

    def attribute_ownership_acquisition_notification(self, *args: Any) -> Any:
        return self._forward_callback("attributeOwnershipAcquisitionNotification", *args)

    def attributeOwnershipUnavailable(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("attributeOwnershipUnavailable", *args)

    def attribute_ownership_unavailable(self, *args: Any) -> Any:
        return self._forward_callback("attributeOwnershipUnavailable", *args)

    def requestAttributeOwnershipRelease(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("requestAttributeOwnershipRelease", *args)

    def request_attribute_ownership_release(self, *args: Any) -> Any:
        return self._forward_callback("requestAttributeOwnershipRelease", *args)

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("confirmAttributeOwnershipAcquisitionCancellation", *args)

    def confirm_attribute_ownership_acquisition_cancellation(self, *args: Any) -> Any:
        return self._forward_callback("confirmAttributeOwnershipAcquisitionCancellation", *args)

    def informAttributeOwnership(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("informAttributeOwnership", *args)

    def inform_attribute_ownership(self, *args: Any) -> Any:
        return self._forward_callback("informAttributeOwnership", *args)

    def attributeIsNotOwned(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("attributeIsNotOwned", *args)

    def attribute_is_not_owned(self, *args: Any) -> Any:
        return self._forward_callback("attributeIsNotOwned", *args)

    def attributeIsOwnedByRTI(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("attributeIsOwnedByRTI", *args)

    def attribute_is_owned_by_rti(self, *args: Any) -> Any:
        return self._forward_callback("attributeIsOwnedByRTI", *args)

    def timeRegulationEnabled(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("timeRegulationEnabled", *args)

    def time_regulation_enabled(self, *args: Any) -> Any:
        return self._forward_callback("timeRegulationEnabled", *args)

    def timeConstrainedEnabled(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("timeConstrainedEnabled", *args)

    def time_constrained_enabled(self, *args: Any) -> Any:
        return self._forward_callback("timeConstrainedEnabled", *args)

    def timeAdvanceGrant(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("timeAdvanceGrant", *args)

    def time_advance_grant(self, *args: Any) -> Any:
        return self._forward_callback("timeAdvanceGrant", *args)

    def requestRetraction(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_callback("requestRetraction", *args)

    def request_retraction(self, *args: Any) -> Any:
        return self._forward_callback("requestRetraction", *args)


@dataclass
class CERTIJavaRTIShim:
    """Java-shaped facade for a real CERTI-backed RTI ambassador."""

    profile: str
    config: CERTIConfig = CERTIConfig()

    def __post_init__(self) -> None:
        self._rti = make_rti_ambassador(create_certi_backend(self.config))
        self._java_proxy = None

    def _forward_service(self, method_name: str, *args: Any) -> Any:
        target = getattr(self._rti, lower_camel_to_snake(method_name))
        py_args = tuple(from_java_like(arg) for arg in args)
        result = target(*py_args)
        return to_java_like(result)

    def abortFederationRestore(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("abortFederationRestore", *args)

    def abortFederationSave(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("abortFederationSave", *args)

    def associateRegionsForUpdates(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("associateRegionsForUpdates", *args)

    def attributeOwnershipAcquisition(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("attributeOwnershipAcquisition", *args)

    def attributeOwnershipAcquisitionIfAvailable(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("attributeOwnershipAcquisitionIfAvailable", *args)

    def attributeOwnershipDivestitureIfWanted(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("attributeOwnershipDivestitureIfWanted", *args)

    def attributeOwnershipReleaseDenied(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("attributeOwnershipReleaseDenied", *args)

    def cancelAttributeOwnershipAcquisition(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("cancelAttributeOwnershipAcquisition", *args)

    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("cancelNegotiatedAttributeOwnershipDivestiture", *args)

    def changeAttributeOrderType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("changeAttributeOrderType", *args)

    def changeInteractionOrderType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("changeInteractionOrderType", *args)

    def commitRegionModifications(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("commitRegionModifications", *args)

    def confirmDivestiture(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("confirmDivestiture", *args)

    def createFederationExecution(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("createFederationExecution", *args)

    def createFederationExecutionWithMIM(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("createFederationExecutionWithMIM", *args)

    def createRegion(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("createRegion", *args)

    def decodeAttributeHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeAttributeHandle", *args)

    def decodeDimensionHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeDimensionHandle", *args)

    def decodeFederateHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeFederateHandle", *args)

    def decodeInteractionClassHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeInteractionClassHandle", *args)

    def decodeMessageRetractionHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeMessageRetractionHandle", *args)

    def decodeObjectClassHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeObjectClassHandle", *args)

    def decodeObjectInstanceHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeObjectInstanceHandle", *args)

    def decodeParameterHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeParameterHandle", *args)

    def decodeRegionHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("decodeRegionHandle", *args)

    def deleteObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("deleteObjectInstance", *args)

    def deleteRegion(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("deleteRegion", *args)

    def destroyFederationExecution(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("destroyFederationExecution", *args)

    def disableAsynchronousDelivery(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableAsynchronousDelivery", *args)

    def disableAttributeRelevanceAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableAttributeRelevanceAdvisorySwitch", *args)

    def disableAttributeScopeAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableAttributeScopeAdvisorySwitch", *args)

    def disableCallbacks(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableCallbacks", *args)

    def disableInteractionRelevanceAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableInteractionRelevanceAdvisorySwitch", *args)

    def disableObjectClassRelevanceAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableObjectClassRelevanceAdvisorySwitch", *args)

    def disableTimeConstrained(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableTimeConstrained", *args)

    def disableTimeRegulation(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disableTimeRegulation", *args)

    def disconnect(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("disconnect", *args)

    def enableAsynchronousDelivery(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableAsynchronousDelivery", *args)

    def enableAttributeRelevanceAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableAttributeRelevanceAdvisorySwitch", *args)

    def enableAttributeScopeAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableAttributeScopeAdvisorySwitch", *args)

    def enableCallbacks(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableCallbacks", *args)

    def enableInteractionRelevanceAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableInteractionRelevanceAdvisorySwitch", *args)

    def enableObjectClassRelevanceAdvisorySwitch(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableObjectClassRelevanceAdvisorySwitch", *args)

    def enableTimeConstrained(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableTimeConstrained", *args)

    def enableTimeRegulation(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("enableTimeRegulation", *args)

    def evokeCallback(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("evokeCallback", *args)

    def evokeMultipleCallbacks(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("evokeMultipleCallbacks", *args)

    def federateRestoreComplete(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("federateRestoreComplete", *args)

    def federateRestoreNotComplete(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("federateRestoreNotComplete", *args)

    def federateSaveBegun(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("federateSaveBegun", *args)

    def federateSaveComplete(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("federateSaveComplete", *args)

    def federateSaveNotComplete(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("federateSaveNotComplete", *args)

    def flushQueueRequest(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("flushQueueRequest", *args)

    def getAttributeHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAttributeHandle", *args)

    def getAttributeHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAttributeHandleFactory", *args)

    def getAttributeHandleSetFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAttributeHandleSetFactory", *args)

    def getAttributeHandleValueMapFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAttributeHandleValueMapFactory", *args)

    def getAttributeName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAttributeName", *args)

    def getAttributeSetRegionSetPairListFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAttributeSetRegionSetPairListFactory", *args)

    def getAutomaticResignDirective(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAutomaticResignDirective", *args)

    def getAvailableDimensionsForClassAttribute(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAvailableDimensionsForClassAttribute", *args)

    def getAvailableDimensionsForInteractionClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getAvailableDimensionsForInteractionClass", *args)

    def getDimensionHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getDimensionHandle", *args)

    def getDimensionHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getDimensionHandleFactory", *args)

    def getDimensionHandleSet(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getDimensionHandleSet", *args)

    def getDimensionHandleSetFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getDimensionHandleSetFactory", *args)

    def getDimensionName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getDimensionName", *args)

    def getDimensionUpperBound(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getDimensionUpperBound", *args)

    def getFederateHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getFederateHandle", *args)

    def getFederateHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getFederateHandleFactory", *args)

    def getFederateHandleSetFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getFederateHandleSetFactory", *args)

    def getFederateName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getFederateName", *args)

    def getInteractionClassHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getInteractionClassHandle", *args)

    def getInteractionClassHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getInteractionClassHandleFactory", *args)

    def getInteractionClassName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getInteractionClassName", *args)

    def getKnownObjectClassHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getKnownObjectClassHandle", *args)

    def getObjectClassHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getObjectClassHandle", *args)

    def getObjectClassHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getObjectClassHandleFactory", *args)

    def getObjectClassName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getObjectClassName", *args)

    def getObjectInstanceHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getObjectInstanceHandle", *args)

    def getObjectInstanceHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getObjectInstanceHandleFactory", *args)

    def getObjectInstanceName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getObjectInstanceName", *args)

    def getOrderName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getOrderName", *args)

    def getOrderType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getOrderType", *args)

    def getParameterHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getParameterHandle", *args)

    def getParameterHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getParameterHandleFactory", *args)

    def getParameterHandleValueMapFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getParameterHandleValueMapFactory", *args)

    def getParameterName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getParameterName", *args)

    def getRangeBounds(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getRangeBounds", *args)

    def getRegionHandleSetFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getRegionHandleSetFactory", *args)

    def getTimeFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getTimeFactory", *args)

    def getTransportationName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getTransportationName", *args)

    def getTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getTransportationType", *args)

    def getTransportationTypeHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getTransportationTypeHandle", *args)

    def getTransportationTypeHandleFactory(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getTransportationTypeHandleFactory", *args)

    def getTransportationTypeName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getTransportationTypeName", *args)

    def getUpdateRateValue(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getUpdateRateValue", *args)

    def getUpdateRateValueForAttribute(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("getUpdateRateValueForAttribute", *args)

    def isAttributeOwnedByFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("isAttributeOwnedByFederate", *args)

    def joinFederationExecution(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("joinFederationExecution", *args)

    def listFederationExecutions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("listFederationExecutions", *args)

    def localDeleteObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("localDeleteObjectInstance", *args)

    def modifyLookahead(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("modifyLookahead", *args)

    def negotiatedAttributeOwnershipDivestiture(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("negotiatedAttributeOwnershipDivestiture", *args)

    def nextMessageRequest(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("nextMessageRequest", *args)

    def nextMessageRequestAvailable(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("nextMessageRequestAvailable", *args)

    def normalizeFederateHandle(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("normalizeFederateHandle", *args)

    def normalizeServiceGroup(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("normalizeServiceGroup", *args)

    def publishInteractionClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("publishInteractionClass", *args)

    def publishObjectClassAttributes(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("publishObjectClassAttributes", *args)

    def queryAttributeOwnership(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryAttributeOwnership", *args)

    def queryAttributeTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryAttributeTransportationType", *args)

    def queryFederationRestoreStatus(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryFederationRestoreStatus", *args)

    def queryFederationSaveStatus(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryFederationSaveStatus", *args)

    def queryGALT(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryGALT", *args)

    def queryInteractionTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryInteractionTransportationType", *args)

    def queryLITS(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryLITS", *args)

    def queryLogicalTime(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryLogicalTime", *args)

    def queryLookahead(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("queryLookahead", *args)

    def registerFederationSynchronizationPoint(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("registerFederationSynchronizationPoint", *args)

    def registerObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("registerObjectInstance", *args)

    def registerObjectInstanceWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("registerObjectInstanceWithRegions", *args)

    def releaseMultipleObjectInstanceName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("releaseMultipleObjectInstanceName", *args)

    def releaseObjectInstanceName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("releaseObjectInstanceName", *args)

    def requestAttributeTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("requestAttributeTransportationTypeChange", *args)

    def requestAttributeValueUpdate(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("requestAttributeValueUpdate", *args)

    def requestAttributeValueUpdateWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("requestAttributeValueUpdateWithRegions", *args)

    def requestFederationRestore(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("requestFederationRestore", *args)

    def requestFederationSave(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("requestFederationSave", *args)

    def requestInteractionTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("requestInteractionTransportationTypeChange", *args)

    def reserveMultipleObjectInstanceName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("reserveMultipleObjectInstanceName", *args)

    def reserveObjectInstanceName(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("reserveObjectInstanceName", *args)

    def resignFederationExecution(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("resignFederationExecution", *args)

    def retract(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("retract", *args)

    def sendInteraction(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("sendInteraction", *args)

    def sendInteractionWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("sendInteractionWithRegions", *args)

    def setAutomaticResignDirective(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("setAutomaticResignDirective", *args)

    def setRangeBounds(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("setRangeBounds", *args)

    def subscribeInteractionClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeInteractionClass", *args)

    def subscribeInteractionClassPassively(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeInteractionClassPassively", *args)

    def subscribeInteractionClassPassivelyWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeInteractionClassPassivelyWithRegions", *args)

    def subscribeInteractionClassWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeInteractionClassWithRegions", *args)

    def subscribeObjectClassAttributes(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeObjectClassAttributes", *args)

    def subscribeObjectClassAttributesPassively(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeObjectClassAttributesPassively", *args)

    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeObjectClassAttributesPassivelyWithRegions", *args)

    def subscribeObjectClassAttributesWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("subscribeObjectClassAttributesWithRegions", *args)

    def synchronizationPointAchieved(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("synchronizationPointAchieved", *args)

    def timeAdvanceRequest(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("timeAdvanceRequest", *args)

    def timeAdvanceRequestAvailable(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("timeAdvanceRequestAvailable", *args)

    def unassociateRegionsForUpdates(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unassociateRegionsForUpdates", *args)

    def unconditionalAttributeOwnershipDivestiture(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unconditionalAttributeOwnershipDivestiture", *args)

    def unpublishInteractionClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unpublishInteractionClass", *args)

    def unpublishObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unpublishObjectClass", *args)

    def unpublishObjectClassAttributes(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unpublishObjectClassAttributes", *args)

    def unsubscribeInteractionClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unsubscribeInteractionClass", *args)

    def unsubscribeInteractionClassWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unsubscribeInteractionClassWithRegions", *args)

    def unsubscribeObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unsubscribeObjectClass", *args)

    def unsubscribeObjectClassAttributes(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unsubscribeObjectClassAttributes", *args)

    def unsubscribeObjectClassAttributesWithRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("unsubscribeObjectClassAttributesWithRegions", *args)

    def updateAttributeValues(self, *args: Any) -> Any:  # noqa: N802
        return self._forward_service("updateAttributeValues", *args)

    def connect(self, federateReference: Any, callbackModel: Any, localSettingsDesignator: str | None = None) -> None:
        self._java_proxy = federateReference
        python_ambassador = _CERTIJavaFederateAdapter(federateReference)
        callback_model = from_java_like(callbackModel)
        if localSettingsDesignator is None:
            self._rti.connect(python_ambassador, callback_model)
        else:
            self._rti.connect(python_ambassador, callback_model, localSettingsDesignator)

    def close(self) -> None:
        self._rti.close()

    def getHLAversion(self) -> str:
        return self._rti.get_hla_version()


__all__ = ["CERTIJavaRTIShim", "_CERTIJavaFederateAdapter"]
