"""Reusable FederateAmbassador helpers for local RTI development."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable

from .runtime_api import FederateAmbassador
from .spec import FederateAmbassadorSpec
from .spec_refs import SpecReference, method_reference


def lower_camel_to_snake(name: str) -> str:
    """Convert a source HLA lowerCamelCase method name to snake_case."""

    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def invoke_federate_callback(ambassador: FederateAmbassador | FederateAmbassadorSpec, method_name: str, *args: Any, **kwargs: Any) -> Any:
    """Invoke a FederateAmbassador callback through an explicit method registry."""

    match method_name:
        case "announceSynchronizationPoint":
            return ambassador.announceSynchronizationPoint(*args, **kwargs)
        case "attributeIsNotOwned":
            return ambassador.attributeIsNotOwned(*args, **kwargs)
        case "attributeIsOwnedByRTI":
            return ambassador.attributeIsOwnedByRTI(*args, **kwargs)
        case "attributeOwnershipAcquisitionNotification":
            return ambassador.attributeOwnershipAcquisitionNotification(*args, **kwargs)
        case "attributeOwnershipUnavailable":
            return ambassador.attributeOwnershipUnavailable(*args, **kwargs)
        case "attributesInScope":
            return ambassador.attributesInScope(*args, **kwargs)
        case "attributesOutOfScope":
            return ambassador.attributesOutOfScope(*args, **kwargs)
        case "confirmAttributeOwnershipAcquisitionCancellation":
            return ambassador.confirmAttributeOwnershipAcquisitionCancellation(*args, **kwargs)
        case "confirmAttributeTransportationTypeChange":
            return ambassador.confirmAttributeTransportationTypeChange(*args, **kwargs)
        case "confirmInteractionTransportationTypeChange":
            return ambassador.confirmInteractionTransportationTypeChange(*args, **kwargs)
        case "connectionLost":
            return ambassador.connectionLost(*args, **kwargs)
        case "discoverObjectInstance":
            return ambassador.discoverObjectInstance(*args, **kwargs)
        case "federationNotRestored":
            return ambassador.federationNotRestored(*args, **kwargs)
        case "federationNotSaved":
            return ambassador.federationNotSaved(*args, **kwargs)
        case "federationRestoreBegun":
            return ambassador.federationRestoreBegun(*args, **kwargs)
        case "federationRestoreStatusResponse":
            return ambassador.federationRestoreStatusResponse(*args, **kwargs)
        case "federationRestored":
            return ambassador.federationRestored(*args, **kwargs)
        case "federationSaveStatusResponse":
            return ambassador.federationSaveStatusResponse(*args, **kwargs)
        case "federationSaved":
            return ambassador.federationSaved(*args, **kwargs)
        case "federationSynchronized":
            return ambassador.federationSynchronized(*args, **kwargs)
        case "getProducingFederate":
            return ambassador.getProducingFederate(*args, **kwargs)
        case "getSentRegions":
            return ambassador.getSentRegions(*args, **kwargs)
        case "hasProducingFederate":
            return ambassador.hasProducingFederate(*args, **kwargs)
        case "hasSentRegions":
            return ambassador.hasSentRegions(*args, **kwargs)
        case "informAttributeOwnership":
            return ambassador.informAttributeOwnership(*args, **kwargs)
        case "initiateFederateRestore":
            return ambassador.initiateFederateRestore(*args, **kwargs)
        case "initiateFederateSave":
            return ambassador.initiateFederateSave(*args, **kwargs)
        case "multipleObjectInstanceNameReservationFailed":
            return ambassador.multipleObjectInstanceNameReservationFailed(*args, **kwargs)
        case "multipleObjectInstanceNameReservationSucceeded":
            return ambassador.multipleObjectInstanceNameReservationSucceeded(*args, **kwargs)
        case "objectInstanceNameReservationFailed":
            return ambassador.objectInstanceNameReservationFailed(*args, **kwargs)
        case "objectInstanceNameReservationSucceeded":
            return ambassador.objectInstanceNameReservationSucceeded(*args, **kwargs)
        case "provideAttributeValueUpdate":
            return ambassador.provideAttributeValueUpdate(*args, **kwargs)
        case "receiveInteraction":
            return ambassador.receiveInteraction(*args, **kwargs)
        case "reflectAttributeValues":
            return ambassador.reflectAttributeValues(*args, **kwargs)
        case "removeObjectInstance":
            return ambassador.removeObjectInstance(*args, **kwargs)
        case "reportAttributeTransportationType":
            return ambassador.reportAttributeTransportationType(*args, **kwargs)
        case "reportFederationExecutions":
            return ambassador.reportFederationExecutions(*args, **kwargs)
        case "reportInteractionTransportationType":
            return ambassador.reportInteractionTransportationType(*args, **kwargs)
        case "requestAttributeOwnershipAssumption":
            return ambassador.requestAttributeOwnershipAssumption(*args, **kwargs)
        case "requestAttributeOwnershipRelease":
            return ambassador.requestAttributeOwnershipRelease(*args, **kwargs)
        case "requestDivestitureConfirmation":
            return ambassador.requestDivestitureConfirmation(*args, **kwargs)
        case "requestFederationRestoreFailed":
            return ambassador.requestFederationRestoreFailed(*args, **kwargs)
        case "requestFederationRestoreSucceeded":
            return ambassador.requestFederationRestoreSucceeded(*args, **kwargs)
        case "requestRetraction":
            return ambassador.requestRetraction(*args, **kwargs)
        case "startRegistrationForObjectClass":
            return ambassador.startRegistrationForObjectClass(*args, **kwargs)
        case "stopRegistrationForObjectClass":
            return ambassador.stopRegistrationForObjectClass(*args, **kwargs)
        case "synchronizationPointRegistrationFailed":
            return ambassador.synchronizationPointRegistrationFailed(*args, **kwargs)
        case "synchronizationPointRegistrationSucceeded":
            return ambassador.synchronizationPointRegistrationSucceeded(*args, **kwargs)
        case "timeAdvanceGrant":
            return ambassador.timeAdvanceGrant(*args, **kwargs)
        case "timeConstrainedEnabled":
            return ambassador.timeConstrainedEnabled(*args, **kwargs)
        case "timeRegulationEnabled":
            return ambassador.timeRegulationEnabled(*args, **kwargs)
        case "turnInteractionsOff":
            return ambassador.turnInteractionsOff(*args, **kwargs)
        case "turnInteractionsOn":
            return ambassador.turnInteractionsOn(*args, **kwargs)
        case "turnUpdatesOffForObjectInstance":
            return ambassador.turnUpdatesOffForObjectInstance(*args, **kwargs)
        case "turnUpdatesOnForObjectInstance":
            return ambassador.turnUpdatesOnForObjectInstance(*args, **kwargs)
        case _:
            raise AttributeError(method_name)


class NullFederateAmbassador(FederateAmbassador):
    """No-op FederateAmbassador implementation for tests and simple clients."""

    pass


@dataclass(frozen=True)
class CallbackRecord:
    """One RTI-initiated service invocation on a FederateAmbassador."""

    method_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    reference: SpecReference | None = None

    @property
    def snake_name(self) -> str:
        return lower_camel_to_snake(self.method_name)


class RecordingFederateAmbassador(FederateAmbassador):
    """FederateAmbassador that records every callback with its spec reference."""

    def __init__(self) -> None:
        self.records: list[CallbackRecord] = []

    @property
    def events(self) -> list[tuple[str, tuple[Any, ...]]]:
        return [(record.method_name, record.args) for record in self.records]

    def record_callback(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        record = CallbackRecord(method_name, tuple(args), dict(kwargs), method_reference(method_name))
        self.records.append(record)
        hook = getattr(self, f"on_{record.snake_name}", None)
        if callable(hook):
            return hook(*args, **kwargs)
        return None

    def clear(self) -> None:
        self.records.clear()

    def callbacks_named(self, method_name: str) -> list[CallbackRecord]:
        return [record for record in self.records if record.method_name == method_name or record.snake_name == method_name]

    def last_callback(self, method_name: str | None = None) -> CallbackRecord | None:
        if method_name is None:
            return self.records[-1] if self.records else None
        matches = self.callbacks_named(method_name)
        return matches[-1] if matches else None

    def connectionLost(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("connectionLost", *args, **kwargs)

    def connection_lost(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("connectionLost", *args, **kwargs)

    def reportFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("reportFederationExecutions", *args, **kwargs)

    def report_federation_executions(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reportFederationExecutions", *args, **kwargs)

    def synchronizationPointRegistrationSucceeded(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("synchronizationPointRegistrationSucceeded", *args, **kwargs)

    def synchronization_point_registration_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("synchronizationPointRegistrationSucceeded", *args, **kwargs)

    def synchronizationPointRegistrationFailed(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("synchronizationPointRegistrationFailed", *args, **kwargs)

    def synchronization_point_registration_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("synchronizationPointRegistrationFailed", *args, **kwargs)

    def announceSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("announceSynchronizationPoint", *args, **kwargs)

    def announce_synchronization_point(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("announceSynchronizationPoint", *args, **kwargs)

    def federationSynchronized(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationSynchronized", *args, **kwargs)

    def federation_synchronized(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationSynchronized", *args, **kwargs)

    def initiateFederateSave(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("initiateFederateSave", *args, **kwargs)

    def initiate_federate_save(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("initiateFederateSave", *args, **kwargs)

    def federationSaved(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationSaved", *args, **kwargs)

    def federation_saved(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationSaved", *args, **kwargs)

    def federationNotSaved(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationNotSaved", *args, **kwargs)

    def federation_not_saved(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationNotSaved", *args, **kwargs)

    def federationSaveStatusResponse(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationSaveStatusResponse", *args, **kwargs)

    def federation_save_status_response(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationSaveStatusResponse", *args, **kwargs)

    def requestFederationRestoreSucceeded(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("requestFederationRestoreSucceeded", *args, **kwargs)

    def request_federation_restore_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestFederationRestoreSucceeded", *args, **kwargs)

    def requestFederationRestoreFailed(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("requestFederationRestoreFailed", *args, **kwargs)

    def request_federation_restore_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestFederationRestoreFailed", *args, **kwargs)

    def federationRestoreBegun(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationRestoreBegun", *args, **kwargs)

    def federation_restore_begun(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationRestoreBegun", *args, **kwargs)

    def initiateFederateRestore(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("initiateFederateRestore", *args, **kwargs)

    def initiate_federate_restore(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("initiateFederateRestore", *args, **kwargs)

    def federationRestored(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationRestored", *args, **kwargs)

    def federation_restored(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationRestored", *args, **kwargs)

    def federationNotRestored(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationNotRestored", *args, **kwargs)

    def federation_not_restored(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationNotRestored", *args, **kwargs)

    def federationRestoreStatusResponse(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("federationRestoreStatusResponse", *args, **kwargs)

    def federation_restore_status_response(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationRestoreStatusResponse", *args, **kwargs)

    def startRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("startRegistrationForObjectClass", *args, **kwargs)

    def start_registration_for_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("startRegistrationForObjectClass", *args, **kwargs)

    def stopRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("stopRegistrationForObjectClass", *args, **kwargs)

    def stop_registration_for_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("stopRegistrationForObjectClass", *args, **kwargs)

    def turnInteractionsOn(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("turnInteractionsOn", *args, **kwargs)

    def turn_interactions_on(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnInteractionsOn", *args, **kwargs)

    def turnInteractionsOff(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("turnInteractionsOff", *args, **kwargs)

    def turn_interactions_off(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnInteractionsOff", *args, **kwargs)

    def objectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("objectInstanceNameReservationSucceeded", *args, **kwargs)

    def object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("objectInstanceNameReservationSucceeded", *args, **kwargs)

    def objectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("objectInstanceNameReservationFailed", *args, **kwargs)

    def object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("objectInstanceNameReservationFailed", *args, **kwargs)

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("multipleObjectInstanceNameReservationSucceeded", *args, **kwargs)

    def multiple_object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("multipleObjectInstanceNameReservationSucceeded", *args, **kwargs)

    def multipleObjectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("multipleObjectInstanceNameReservationFailed", *args, **kwargs)

    def multiple_object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("multipleObjectInstanceNameReservationFailed", *args, **kwargs)

    def discoverObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("discoverObjectInstance", *args, **kwargs)

    def discover_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("discoverObjectInstance", *args, **kwargs)

    def hasProducingFederate(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("hasProducingFederate", *args, **kwargs)

    def has_producing_federate(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("hasProducingFederate", *args, **kwargs)

    def hasSentRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("hasSentRegions", *args, **kwargs)

    def has_sent_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("hasSentRegions", *args, **kwargs)

    def getProducingFederate(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("getProducingFederate", *args, **kwargs)

    def get_producing_federate(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("getProducingFederate", *args, **kwargs)

    def getSentRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("getSentRegions", *args, **kwargs)

    def get_sent_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("getSentRegions", *args, **kwargs)

    def reflectAttributeValues(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("reflectAttributeValues", *args, **kwargs)

    def reflect_attribute_values(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reflectAttributeValues", *args, **kwargs)

    def receiveInteraction(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("receiveInteraction", *args, **kwargs)

    def receive_interaction(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("receiveInteraction", *args, **kwargs)

    def removeObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("removeObjectInstance", *args, **kwargs)

    def remove_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("removeObjectInstance", *args, **kwargs)

    def attributesInScope(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("attributesInScope", *args, **kwargs)

    def attributes_in_scope(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributesInScope", *args, **kwargs)

    def attributesOutOfScope(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("attributesOutOfScope", *args, **kwargs)

    def attributes_out_of_scope(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributesOutOfScope", *args, **kwargs)

    def provideAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("provideAttributeValueUpdate", *args, **kwargs)

    def provide_attribute_value_update(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("provideAttributeValueUpdate", *args, **kwargs)

    def turnUpdatesOnForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("turnUpdatesOnForObjectInstance", *args, **kwargs)

    def turn_updates_on_for_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnUpdatesOnForObjectInstance", *args, **kwargs)

    def turnUpdatesOffForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("turnUpdatesOffForObjectInstance", *args, **kwargs)

    def turn_updates_off_for_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnUpdatesOffForObjectInstance", *args, **kwargs)

    def confirmAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("confirmAttributeTransportationTypeChange", *args, **kwargs)

    def confirm_attribute_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("confirmAttributeTransportationTypeChange", *args, **kwargs)

    def reportAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("reportAttributeTransportationType", *args, **kwargs)

    def report_attribute_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reportAttributeTransportationType", *args, **kwargs)

    def confirmInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("confirmInteractionTransportationTypeChange", *args, **kwargs)

    def confirm_interaction_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("confirmInteractionTransportationTypeChange", *args, **kwargs)

    def reportInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("reportInteractionTransportationType", *args, **kwargs)

    def report_interaction_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reportInteractionTransportationType", *args, **kwargs)

    def requestAttributeOwnershipAssumption(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("requestAttributeOwnershipAssumption", *args, **kwargs)

    def request_attribute_ownership_assumption(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestAttributeOwnershipAssumption", *args, **kwargs)

    def requestDivestitureConfirmation(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("requestDivestitureConfirmation", *args, **kwargs)

    def request_divestiture_confirmation(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestDivestitureConfirmation", *args, **kwargs)

    def attributeOwnershipAcquisitionNotification(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("attributeOwnershipAcquisitionNotification", *args, **kwargs)

    def attribute_ownership_acquisition_notification(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeOwnershipAcquisitionNotification", *args, **kwargs)

    def attributeOwnershipUnavailable(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("attributeOwnershipUnavailable", *args, **kwargs)

    def attribute_ownership_unavailable(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeOwnershipUnavailable", *args, **kwargs)

    def requestAttributeOwnershipRelease(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("requestAttributeOwnershipRelease", *args, **kwargs)

    def request_attribute_ownership_release(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestAttributeOwnershipRelease", *args, **kwargs)

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("confirmAttributeOwnershipAcquisitionCancellation", *args, **kwargs)

    def confirm_attribute_ownership_acquisition_cancellation(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("confirmAttributeOwnershipAcquisitionCancellation", *args, **kwargs)

    def informAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("informAttributeOwnership", *args, **kwargs)

    def inform_attribute_ownership(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("informAttributeOwnership", *args, **kwargs)

    def attributeIsNotOwned(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("attributeIsNotOwned", *args, **kwargs)

    def attribute_is_not_owned(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeIsNotOwned", *args, **kwargs)

    def attributeIsOwnedByRTI(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("attributeIsOwnedByRTI", *args, **kwargs)

    def attribute_is_owned_by_rti(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeIsOwnedByRTI", *args, **kwargs)

    def timeRegulationEnabled(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("timeRegulationEnabled", *args, **kwargs)

    def time_regulation_enabled(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("timeRegulationEnabled", *args, **kwargs)

    def timeConstrainedEnabled(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("timeConstrainedEnabled", *args, **kwargs)

    def time_constrained_enabled(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("timeConstrainedEnabled", *args, **kwargs)

    def timeAdvanceGrant(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("timeAdvanceGrant", *args, **kwargs)

    def time_advance_grant(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("timeAdvanceGrant", *args, **kwargs)

    def requestRetraction(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        return self.record_callback("requestRetraction", *args, **kwargs)

    def request_retraction(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestRetraction", *args, **kwargs)


class FederateAmbassadorMultiplexer(FederateAmbassador):
    """Forward callbacks to multiple FederateAmbassador instances in order."""

    def __init__(self, ambassadors: Iterable[FederateAmbassador] = ()) -> None:
        self.ambassadors = list(ambassadors)

    def add(self, ambassador: FederateAmbassador) -> None:
        self.ambassadors.append(ambassador)

    def dispatch(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        for ambassador in list(self.ambassadors):
            invoke_federate_callback(ambassador, method_name, *args, **kwargs)

    def connectionLost(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("connectionLost", *args, **kwargs)

    def connection_lost(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("connectionLost", *args, **kwargs)

    def reportFederationExecutions(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("reportFederationExecutions", *args, **kwargs)

    def report_federation_executions(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("reportFederationExecutions", *args, **kwargs)

    def synchronizationPointRegistrationSucceeded(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("synchronizationPointRegistrationSucceeded", *args, **kwargs)

    def synchronization_point_registration_succeeded(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("synchronizationPointRegistrationSucceeded", *args, **kwargs)

    def synchronizationPointRegistrationFailed(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("synchronizationPointRegistrationFailed", *args, **kwargs)

    def synchronization_point_registration_failed(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("synchronizationPointRegistrationFailed", *args, **kwargs)

    def announceSynchronizationPoint(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("announceSynchronizationPoint", *args, **kwargs)

    def announce_synchronization_point(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("announceSynchronizationPoint", *args, **kwargs)

    def federationSynchronized(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationSynchronized", *args, **kwargs)

    def federation_synchronized(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationSynchronized", *args, **kwargs)

    def initiateFederateSave(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("initiateFederateSave", *args, **kwargs)

    def initiate_federate_save(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("initiateFederateSave", *args, **kwargs)

    def federationSaved(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationSaved", *args, **kwargs)

    def federation_saved(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationSaved", *args, **kwargs)

    def federationNotSaved(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationNotSaved", *args, **kwargs)

    def federation_not_saved(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationNotSaved", *args, **kwargs)

    def federationSaveStatusResponse(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationSaveStatusResponse", *args, **kwargs)

    def federation_save_status_response(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationSaveStatusResponse", *args, **kwargs)

    def requestFederationRestoreSucceeded(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("requestFederationRestoreSucceeded", *args, **kwargs)

    def request_federation_restore_succeeded(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("requestFederationRestoreSucceeded", *args, **kwargs)

    def requestFederationRestoreFailed(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("requestFederationRestoreFailed", *args, **kwargs)

    def request_federation_restore_failed(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("requestFederationRestoreFailed", *args, **kwargs)

    def federationRestoreBegun(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationRestoreBegun", *args, **kwargs)

    def federation_restore_begun(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationRestoreBegun", *args, **kwargs)

    def initiateFederateRestore(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("initiateFederateRestore", *args, **kwargs)

    def initiate_federate_restore(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("initiateFederateRestore", *args, **kwargs)

    def federationRestored(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationRestored", *args, **kwargs)

    def federation_restored(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationRestored", *args, **kwargs)

    def federationNotRestored(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationNotRestored", *args, **kwargs)

    def federation_not_restored(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationNotRestored", *args, **kwargs)

    def federationRestoreStatusResponse(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("federationRestoreStatusResponse", *args, **kwargs)

    def federation_restore_status_response(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("federationRestoreStatusResponse", *args, **kwargs)

    def startRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("startRegistrationForObjectClass", *args, **kwargs)

    def start_registration_for_object_class(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("startRegistrationForObjectClass", *args, **kwargs)

    def stopRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("stopRegistrationForObjectClass", *args, **kwargs)

    def stop_registration_for_object_class(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("stopRegistrationForObjectClass", *args, **kwargs)

    def turnInteractionsOn(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("turnInteractionsOn", *args, **kwargs)

    def turn_interactions_on(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("turnInteractionsOn", *args, **kwargs)

    def turnInteractionsOff(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("turnInteractionsOff", *args, **kwargs)

    def turn_interactions_off(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("turnInteractionsOff", *args, **kwargs)

    def objectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("objectInstanceNameReservationSucceeded", *args, **kwargs)

    def object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("objectInstanceNameReservationSucceeded", *args, **kwargs)

    def objectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("objectInstanceNameReservationFailed", *args, **kwargs)

    def object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("objectInstanceNameReservationFailed", *args, **kwargs)

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("multipleObjectInstanceNameReservationSucceeded", *args, **kwargs)

    def multiple_object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("multipleObjectInstanceNameReservationSucceeded", *args, **kwargs)

    def multipleObjectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("multipleObjectInstanceNameReservationFailed", *args, **kwargs)

    def multiple_object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("multipleObjectInstanceNameReservationFailed", *args, **kwargs)

    def discoverObjectInstance(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("discoverObjectInstance", *args, **kwargs)

    def discover_object_instance(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("discoverObjectInstance", *args, **kwargs)

    def hasProducingFederate(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("hasProducingFederate", *args, **kwargs)

    def has_producing_federate(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("hasProducingFederate", *args, **kwargs)

    def hasSentRegions(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("hasSentRegions", *args, **kwargs)

    def has_sent_regions(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("hasSentRegions", *args, **kwargs)

    def getProducingFederate(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("getProducingFederate", *args, **kwargs)

    def get_producing_federate(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("getProducingFederate", *args, **kwargs)

    def getSentRegions(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("getSentRegions", *args, **kwargs)

    def get_sent_regions(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("getSentRegions", *args, **kwargs)

    def reflectAttributeValues(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("reflectAttributeValues", *args, **kwargs)

    def reflect_attribute_values(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("reflectAttributeValues", *args, **kwargs)

    def receiveInteraction(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("receiveInteraction", *args, **kwargs)

    def receive_interaction(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("receiveInteraction", *args, **kwargs)

    def removeObjectInstance(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("removeObjectInstance", *args, **kwargs)

    def remove_object_instance(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("removeObjectInstance", *args, **kwargs)

    def attributesInScope(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("attributesInScope", *args, **kwargs)

    def attributes_in_scope(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("attributesInScope", *args, **kwargs)

    def attributesOutOfScope(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("attributesOutOfScope", *args, **kwargs)

    def attributes_out_of_scope(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("attributesOutOfScope", *args, **kwargs)

    def provideAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("provideAttributeValueUpdate", *args, **kwargs)

    def provide_attribute_value_update(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("provideAttributeValueUpdate", *args, **kwargs)

    def turnUpdatesOnForObjectInstance(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("turnUpdatesOnForObjectInstance", *args, **kwargs)

    def turn_updates_on_for_object_instance(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("turnUpdatesOnForObjectInstance", *args, **kwargs)

    def turnUpdatesOffForObjectInstance(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("turnUpdatesOffForObjectInstance", *args, **kwargs)

    def turn_updates_off_for_object_instance(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("turnUpdatesOffForObjectInstance", *args, **kwargs)

    def confirmAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("confirmAttributeTransportationTypeChange", *args, **kwargs)

    def confirm_attribute_transportation_type_change(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("confirmAttributeTransportationTypeChange", *args, **kwargs)

    def reportAttributeTransportationType(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("reportAttributeTransportationType", *args, **kwargs)

    def report_attribute_transportation_type(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("reportAttributeTransportationType", *args, **kwargs)

    def confirmInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("confirmInteractionTransportationTypeChange", *args, **kwargs)

    def confirm_interaction_transportation_type_change(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("confirmInteractionTransportationTypeChange", *args, **kwargs)

    def reportInteractionTransportationType(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("reportInteractionTransportationType", *args, **kwargs)

    def report_interaction_transportation_type(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("reportInteractionTransportationType", *args, **kwargs)

    def requestAttributeOwnershipAssumption(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("requestAttributeOwnershipAssumption", *args, **kwargs)

    def request_attribute_ownership_assumption(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("requestAttributeOwnershipAssumption", *args, **kwargs)

    def requestDivestitureConfirmation(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("requestDivestitureConfirmation", *args, **kwargs)

    def request_divestiture_confirmation(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("requestDivestitureConfirmation", *args, **kwargs)

    def attributeOwnershipAcquisitionNotification(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("attributeOwnershipAcquisitionNotification", *args, **kwargs)

    def attribute_ownership_acquisition_notification(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("attributeOwnershipAcquisitionNotification", *args, **kwargs)

    def attributeOwnershipUnavailable(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("attributeOwnershipUnavailable", *args, **kwargs)

    def attribute_ownership_unavailable(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("attributeOwnershipUnavailable", *args, **kwargs)

    def requestAttributeOwnershipRelease(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("requestAttributeOwnershipRelease", *args, **kwargs)

    def request_attribute_ownership_release(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("requestAttributeOwnershipRelease", *args, **kwargs)

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("confirmAttributeOwnershipAcquisitionCancellation", *args, **kwargs)

    def confirm_attribute_ownership_acquisition_cancellation(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("confirmAttributeOwnershipAcquisitionCancellation", *args, **kwargs)

    def informAttributeOwnership(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("informAttributeOwnership", *args, **kwargs)

    def inform_attribute_ownership(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("informAttributeOwnership", *args, **kwargs)

    def attributeIsNotOwned(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("attributeIsNotOwned", *args, **kwargs)

    def attribute_is_not_owned(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("attributeIsNotOwned", *args, **kwargs)

    def attributeIsOwnedByRTI(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("attributeIsOwnedByRTI", *args, **kwargs)

    def attribute_is_owned_by_rti(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("attributeIsOwnedByRTI", *args, **kwargs)

    def timeRegulationEnabled(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("timeRegulationEnabled", *args, **kwargs)

    def time_regulation_enabled(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("timeRegulationEnabled", *args, **kwargs)

    def timeConstrainedEnabled(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("timeConstrainedEnabled", *args, **kwargs)

    def time_constrained_enabled(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("timeConstrainedEnabled", *args, **kwargs)

    def timeAdvanceGrant(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("timeAdvanceGrant", *args, **kwargs)

    def time_advance_grant(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("timeAdvanceGrant", *args, **kwargs)

    def requestRetraction(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self.dispatch("requestRetraction", *args, **kwargs)

    def request_retraction(self, *args: Any, **kwargs: Any) -> None:
        self.dispatch("requestRetraction", *args, **kwargs)


__all__ = [
    "CallbackRecord",
    "NullFederateAmbassador",
    "FederateAmbassadorMultiplexer",
    "RecordingFederateAmbassador",
]
