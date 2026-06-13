"""Shared callback-recording ambassador helpers for split packages."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hla2010.spec import FederateAmbassadorSpec
from hla2010.spec_refs import SpecReference, method_reference

from .base import lower_camel_to_snake


@dataclass(frozen=True)
class CallbackRecord:
    """One RTI-initiated callback captured from a federate ambassador."""

    method_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    reference: SpecReference | None = None

    @property
    def snake_name(self) -> str:
        return lower_camel_to_snake(self.method_name)


class RecordingFederateAmbassador(FederateAmbassadorSpec):
    """Federate ambassador that records callbacks with spec references."""

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
        return [
            record
            for record in self.records
            if record.method_name == method_name or record.snake_name == method_name
        ]

    def last_callback(self, method_name: str | None = None) -> CallbackRecord | None:
        if method_name is None:
            return self.records[-1] if self.records else None
        matches = self.callbacks_named(method_name)
        return matches[-1] if matches else None

    def connection_lost(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("connectionLost", *args, **kwargs)

    def report_federation_executions(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reportFederationExecutions", *args, **kwargs)

    def synchronization_point_registration_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("synchronizationPointRegistrationSucceeded", *args, **kwargs)

    def synchronization_point_registration_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("synchronizationPointRegistrationFailed", *args, **kwargs)

    def announce_synchronization_point(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("announceSynchronizationPoint", *args, **kwargs)

    def federation_synchronized(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationSynchronized", *args, **kwargs)

    def initiate_federate_save(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("initiateFederateSave", *args, **kwargs)

    def federation_saved(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationSaved", *args, **kwargs)

    def federation_not_saved(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationNotSaved", *args, **kwargs)

    def federation_save_status_response(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationSaveStatusResponse", *args, **kwargs)

    def request_federation_restore_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestFederationRestoreSucceeded", *args, **kwargs)

    def request_federation_restore_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestFederationRestoreFailed", *args, **kwargs)

    def federation_restore_begun(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationRestoreBegun", *args, **kwargs)

    def initiate_federate_restore(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("initiateFederateRestore", *args, **kwargs)

    def federation_restored(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationRestored", *args, **kwargs)

    def federation_not_restored(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationNotRestored", *args, **kwargs)

    def federation_restore_status_response(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("federationRestoreStatusResponse", *args, **kwargs)

    def start_registration_for_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("startRegistrationForObjectClass", *args, **kwargs)

    def stop_registration_for_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("stopRegistrationForObjectClass", *args, **kwargs)

    def turn_interactions_on(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnInteractionsOn", *args, **kwargs)

    def turn_interactions_off(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnInteractionsOff", *args, **kwargs)

    def object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("objectInstanceNameReservationSucceeded", *args, **kwargs)

    def object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("objectInstanceNameReservationFailed", *args, **kwargs)

    def multiple_object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("multipleObjectInstanceNameReservationSucceeded", *args, **kwargs)

    def multiple_object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("multipleObjectInstanceNameReservationFailed", *args, **kwargs)

    def discover_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("discoverObjectInstance", *args, **kwargs)

    def has_producing_federate(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("hasProducingFederate", *args, **kwargs)

    def has_sent_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("hasSentRegions", *args, **kwargs)

    def get_producing_federate(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("getProducingFederate", *args, **kwargs)

    def get_sent_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("getSentRegions", *args, **kwargs)

    def reflect_attribute_values(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reflectAttributeValues", *args, **kwargs)

    def receive_interaction(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("receiveInteraction", *args, **kwargs)

    def remove_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("removeObjectInstance", *args, **kwargs)

    def attributes_in_scope(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributesInScope", *args, **kwargs)

    def attributes_out_of_scope(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributesOutOfScope", *args, **kwargs)

    def provide_attribute_value_update(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("provideAttributeValueUpdate", *args, **kwargs)

    def turn_updates_on_for_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnUpdatesOnForObjectInstance", *args, **kwargs)

    def turn_updates_off_for_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("turnUpdatesOffForObjectInstance", *args, **kwargs)

    def confirm_attribute_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("confirmAttributeTransportationTypeChange", *args, **kwargs)

    def report_attribute_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reportAttributeTransportationType", *args, **kwargs)

    def confirm_interaction_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("confirmInteractionTransportationTypeChange", *args, **kwargs)

    def report_interaction_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("reportInteractionTransportationType", *args, **kwargs)

    def request_attribute_ownership_assumption(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestAttributeOwnershipAssumption", *args, **kwargs)

    def request_divestiture_confirmation(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestDivestitureConfirmation", *args, **kwargs)

    def attribute_ownership_acquisition_notification(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeOwnershipAcquisitionNotification", *args, **kwargs)

    def attribute_ownership_unavailable(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeOwnershipUnavailable", *args, **kwargs)

    def request_attribute_ownership_release(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestAttributeOwnershipRelease", *args, **kwargs)

    def confirm_attribute_ownership_acquisition_cancellation(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("confirmAttributeOwnershipAcquisitionCancellation", *args, **kwargs)

    def inform_attribute_ownership(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("informAttributeOwnership", *args, **kwargs)

    def attribute_is_not_owned(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeIsNotOwned", *args, **kwargs)

    def attribute_is_owned_by_rti(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("attributeIsOwnedByRTI", *args, **kwargs)

    def time_regulation_enabled(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("timeRegulationEnabled", *args, **kwargs)

    def time_constrained_enabled(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("timeConstrainedEnabled", *args, **kwargs)

    def time_advance_grant(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("timeAdvanceGrant", *args, **kwargs)

    def request_retraction(self, *args: Any, **kwargs: Any) -> Any:
        return self.record_callback("requestRetraction", *args, **kwargs)


__all__ = [
    "CallbackRecord",
    "RecordingFederateAmbassador",
]
