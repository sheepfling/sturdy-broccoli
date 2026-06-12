"""Adapter classes for Java-profile CERTI backends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hla2010.spec import FederateAmbassadorSpec
from hla2010_rti_java_common import make_rti_ambassador
from hla2010_rti_certi.certi import CERTIConfig, create_certi_backend
from .runtime import from_java_like, to_java_like


class _CERTIJavaFederateAdapter(FederateAmbassadorSpec):
    """Adapter that forwards native CERTI callbacks into a Java-style proxy."""

    def __init__(self, java_proxy: Any) -> None:
        self._java_proxy = java_proxy

    def _forward_callback(self, method_name: str, *args: Any) -> Any:
        callback = getattr(self._java_proxy, method_name)
        return callback(*(to_java_like(arg) for arg in args))


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

    def __getattr__(self, name: str):
        target = getattr(self._rti, name, None)
        if target is None:
            raise AttributeError(name)

        def _invoke(*args: Any) -> Any:
            py_args = tuple(from_java_like(arg) for arg in args)
            result = target(*py_args)
            return to_java_like(result)

        return _invoke

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
        return self._rti.getHLAversion()


__all__ = ["CERTIJavaRTIShim", "_CERTIJavaFederateAdapter"]
