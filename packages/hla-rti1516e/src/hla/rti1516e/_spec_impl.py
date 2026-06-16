"""Pythonic source-backed HLA 1516.1-2010 API spec.

This module is the clean, Python-facing contract layer. Method definitions are
checked in explicitly so import-time package behavior is visible to static tools.
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


def _method_doc(method_name: str, snake_name: str) -> str:
    ref = method_reference(method_name)
    source_summary = method_source_summary(method_name)
    doc_parts = [f"{snake_name} ({method_name})."]
    if ref is not None:
        doc_parts.append(f"IEEE reference: {ref.label}.")
    if source_summary:
        doc_parts.append(f"Sources: {source_summary}.")
    return " ".join(doc_parts)


def _rti_abstract(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name, lower_camel_to_snake(method_name))
        return abstractmethod(method)

    return _decorate


def _rti_alias(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name, lower_camel_to_snake(method_name))
        return method

    return _decorate


def _callback(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name, lower_camel_to_snake(method_name))
        return method

    return _decorate


class RTIambassadorSpec(ABC):
    """Pythonic abstract contract for an HLA RTI ambassador."""

    @_rti_abstract("connect")
    def connect(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_abstract("disconnect")
    def disconnect(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_abstract("createFederationExecution")
    def create_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("createFederationExecution")
    def createFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.create_federation_execution(*args, **kwargs)

    @_rti_abstract("destroyFederationExecution")
    def destroy_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("destroyFederationExecution")
    def destroyFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.destroy_federation_execution(*args, **kwargs)

    @_rti_abstract("listFederationExecutions")
    def list_federation_executions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("listFederationExecutions")
    def listFederationExecutions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.list_federation_executions(*args, **kwargs)

    @_rti_abstract("joinFederationExecution")
    def join_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("joinFederationExecution")
    def joinFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.join_federation_execution(*args, **kwargs)

    @_rti_abstract("resignFederationExecution")
    def resign_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("resignFederationExecution")
    def resignFederationExecution(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.resign_federation_execution(*args, **kwargs)

    @_rti_abstract("registerFederationSynchronizationPoint")
    def register_federation_synchronization_point(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("registerFederationSynchronizationPoint")
    def registerFederationSynchronizationPoint(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.register_federation_synchronization_point(*args, **kwargs)

    @_rti_abstract("synchronizationPointAchieved")
    def synchronization_point_achieved(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("synchronizationPointAchieved")
    def synchronizationPointAchieved(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.synchronization_point_achieved(*args, **kwargs)

    @_rti_abstract("requestFederationSave")
    def request_federation_save(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("requestFederationSave")
    def requestFederationSave(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_federation_save(*args, **kwargs)

    @_rti_abstract("federateSaveBegun")
    def federate_save_begun(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("federateSaveBegun")
    def federateSaveBegun(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federate_save_begun(*args, **kwargs)

    @_rti_abstract("federateSaveComplete")
    def federate_save_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("federateSaveComplete")
    def federateSaveComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federate_save_complete(*args, **kwargs)

    @_rti_abstract("federateSaveNotComplete")
    def federate_save_not_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("federateSaveNotComplete")
    def federateSaveNotComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federate_save_not_complete(*args, **kwargs)

    @_rti_abstract("abortFederationSave")
    def abort_federation_save(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("abortFederationSave")
    def abortFederationSave(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.abort_federation_save(*args, **kwargs)

    @_rti_abstract("queryFederationSaveStatus")
    def query_federation_save_status(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryFederationSaveStatus")
    def queryFederationSaveStatus(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_federation_save_status(*args, **kwargs)

    @_rti_abstract("requestFederationRestore")
    def request_federation_restore(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("requestFederationRestore")
    def requestFederationRestore(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_federation_restore(*args, **kwargs)

    @_rti_abstract("federateRestoreComplete")
    def federate_restore_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("federateRestoreComplete")
    def federateRestoreComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federate_restore_complete(*args, **kwargs)

    @_rti_abstract("federateRestoreNotComplete")
    def federate_restore_not_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("federateRestoreNotComplete")
    def federateRestoreNotComplete(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federate_restore_not_complete(*args, **kwargs)

    @_rti_abstract("abortFederationRestore")
    def abort_federation_restore(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("abortFederationRestore")
    def abortFederationRestore(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.abort_federation_restore(*args, **kwargs)

    @_rti_abstract("queryFederationRestoreStatus")
    def query_federation_restore_status(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryFederationRestoreStatus")
    def queryFederationRestoreStatus(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_federation_restore_status(*args, **kwargs)

    @_rti_abstract("publishObjectClassAttributes")
    def publish_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("publishObjectClassAttributes")
    def publishObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.publish_object_class_attributes(*args, **kwargs)

    @_rti_abstract("unpublishObjectClass")
    def unpublish_object_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unpublishObjectClass")
    def unpublishObjectClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unpublish_object_class(*args, **kwargs)

    @_rti_abstract("unpublishObjectClassAttributes")
    def unpublish_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unpublishObjectClassAttributes")
    def unpublishObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unpublish_object_class_attributes(*args, **kwargs)

    @_rti_abstract("publishInteractionClass")
    def publish_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("publishInteractionClass")
    def publishInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.publish_interaction_class(*args, **kwargs)

    @_rti_abstract("unpublishInteractionClass")
    def unpublish_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unpublishInteractionClass")
    def unpublishInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unpublish_interaction_class(*args, **kwargs)

    @_rti_abstract("subscribeObjectClassAttributes")
    def subscribe_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeObjectClassAttributes")
    def subscribeObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_object_class_attributes(*args, **kwargs)

    @_rti_abstract("subscribeObjectClassAttributesPassively")
    def subscribe_object_class_attributes_passively(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeObjectClassAttributesPassively")
    def subscribeObjectClassAttributesPassively(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_object_class_attributes_passively(*args, **kwargs)

    @_rti_abstract("unsubscribeObjectClass")
    def unsubscribe_object_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unsubscribeObjectClass")
    def unsubscribeObjectClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unsubscribe_object_class(*args, **kwargs)

    @_rti_abstract("unsubscribeObjectClassAttributes")
    def unsubscribe_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unsubscribeObjectClassAttributes")
    def unsubscribeObjectClassAttributes(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unsubscribe_object_class_attributes(*args, **kwargs)

    @_rti_abstract("subscribeInteractionClass")
    def subscribe_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeInteractionClass")
    def subscribeInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_interaction_class(*args, **kwargs)

    @_rti_abstract("subscribeInteractionClassPassively")
    def subscribe_interaction_class_passively(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeInteractionClassPassively")
    def subscribeInteractionClassPassively(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_interaction_class_passively(*args, **kwargs)

    @_rti_abstract("unsubscribeInteractionClass")
    def unsubscribe_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unsubscribeInteractionClass")
    def unsubscribeInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unsubscribe_interaction_class(*args, **kwargs)

    @_rti_abstract("reserveObjectInstanceName")
    def reserve_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("reserveObjectInstanceName")
    def reserveObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.reserve_object_instance_name(*args, **kwargs)

    @_rti_abstract("releaseObjectInstanceName")
    def release_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("releaseObjectInstanceName")
    def releaseObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.release_object_instance_name(*args, **kwargs)

    @_rti_abstract("reserveMultipleObjectInstanceName")
    def reserve_multiple_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("reserveMultipleObjectInstanceName")
    def reserveMultipleObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.reserve_multiple_object_instance_name(*args, **kwargs)

    @_rti_abstract("releaseMultipleObjectInstanceName")
    def release_multiple_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("releaseMultipleObjectInstanceName")
    def releaseMultipleObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.release_multiple_object_instance_name(*args, **kwargs)

    @_rti_abstract("registerObjectInstance")
    def register_object_instance(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("registerObjectInstance")
    def registerObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.register_object_instance(*args, **kwargs)

    @_rti_abstract("updateAttributeValues")
    def update_attribute_values(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("updateAttributeValues")
    def updateAttributeValues(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.update_attribute_values(*args, **kwargs)

    @_rti_abstract("sendInteraction")
    def send_interaction(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("sendInteraction")
    def sendInteraction(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.send_interaction(*args, **kwargs)

    @_rti_abstract("deleteObjectInstance")
    def delete_object_instance(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("deleteObjectInstance")
    def deleteObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.delete_object_instance(*args, **kwargs)

    @_rti_abstract("localDeleteObjectInstance")
    def local_delete_object_instance(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("localDeleteObjectInstance")
    def localDeleteObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.local_delete_object_instance(*args, **kwargs)

    @_rti_abstract("requestAttributeValueUpdate")
    def request_attribute_value_update(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("requestAttributeValueUpdate")
    def requestAttributeValueUpdate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_attribute_value_update(*args, **kwargs)

    @_rti_abstract("requestAttributeTransportationTypeChange")
    def request_attribute_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("requestAttributeTransportationTypeChange")
    def requestAttributeTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_attribute_transportation_type_change(*args, **kwargs)

    @_rti_abstract("queryAttributeTransportationType")
    def query_attribute_transportation_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryAttributeTransportationType")
    def queryAttributeTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_attribute_transportation_type(*args, **kwargs)

    @_rti_abstract("requestInteractionTransportationTypeChange")
    def request_interaction_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("requestInteractionTransportationTypeChange")
    def requestInteractionTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_interaction_transportation_type_change(*args, **kwargs)

    @_rti_abstract("queryInteractionTransportationType")
    def query_interaction_transportation_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryInteractionTransportationType")
    def queryInteractionTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_interaction_transportation_type(*args, **kwargs)

    @_rti_abstract("unconditionalAttributeOwnershipDivestiture")
    def unconditional_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unconditionalAttributeOwnershipDivestiture")
    def unconditionalAttributeOwnershipDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unconditional_attribute_ownership_divestiture(*args, **kwargs)

    @_rti_abstract("negotiatedAttributeOwnershipDivestiture")
    def negotiated_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("negotiatedAttributeOwnershipDivestiture")
    def negotiatedAttributeOwnershipDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.negotiated_attribute_ownership_divestiture(*args, **kwargs)

    @_rti_abstract("confirmDivestiture")
    def confirm_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("confirmDivestiture")
    def confirmDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_divestiture(*args, **kwargs)

    @_rti_abstract("attributeOwnershipAcquisition")
    def attribute_ownership_acquisition(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("attributeOwnershipAcquisition")
    def attributeOwnershipAcquisition(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_ownership_acquisition(*args, **kwargs)

    @_rti_abstract("attributeOwnershipAcquisitionIfAvailable")
    def attribute_ownership_acquisition_if_available(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("attributeOwnershipAcquisitionIfAvailable")
    def attributeOwnershipAcquisitionIfAvailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_ownership_acquisition_if_available(*args, **kwargs)

    @_rti_abstract("attributeOwnershipReleaseDenied")
    def attribute_ownership_release_denied(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("attributeOwnershipReleaseDenied")
    def attributeOwnershipReleaseDenied(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_ownership_release_denied(*args, **kwargs)

    @_rti_abstract("attributeOwnershipDivestitureIfWanted")
    def attribute_ownership_divestiture_if_wanted(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("attributeOwnershipDivestitureIfWanted")
    def attributeOwnershipDivestitureIfWanted(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.attribute_ownership_divestiture_if_wanted(*args, **kwargs)

    @_rti_abstract("cancelNegotiatedAttributeOwnershipDivestiture")
    def cancel_negotiated_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("cancelNegotiatedAttributeOwnershipDivestiture")
    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.cancel_negotiated_attribute_ownership_divestiture(*args, **kwargs)

    @_rti_abstract("cancelAttributeOwnershipAcquisition")
    def cancel_attribute_ownership_acquisition(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("cancelAttributeOwnershipAcquisition")
    def cancelAttributeOwnershipAcquisition(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.cancel_attribute_ownership_acquisition(*args, **kwargs)

    @_rti_abstract("queryAttributeOwnership")
    def query_attribute_ownership(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryAttributeOwnership")
    def queryAttributeOwnership(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_attribute_ownership(*args, **kwargs)

    @_rti_abstract("isAttributeOwnedByFederate")
    def is_attribute_owned_by_federate(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("isAttributeOwnedByFederate")
    def isAttributeOwnedByFederate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.is_attribute_owned_by_federate(*args, **kwargs)

    @_rti_abstract("enableTimeRegulation")
    def enable_time_regulation(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableTimeRegulation")
    def enableTimeRegulation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_time_regulation(*args, **kwargs)

    @_rti_abstract("disableTimeRegulation")
    def disable_time_regulation(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableTimeRegulation")
    def disableTimeRegulation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_time_regulation(*args, **kwargs)

    @_rti_abstract("enableTimeConstrained")
    def enable_time_constrained(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableTimeConstrained")
    def enableTimeConstrained(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_time_constrained(*args, **kwargs)

    @_rti_abstract("disableTimeConstrained")
    def disable_time_constrained(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableTimeConstrained")
    def disableTimeConstrained(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_time_constrained(*args, **kwargs)

    @_rti_abstract("timeAdvanceRequest")
    def time_advance_request(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("timeAdvanceRequest")
    def timeAdvanceRequest(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_advance_request(*args, **kwargs)

    @_rti_abstract("timeAdvanceRequestAvailable")
    def time_advance_request_available(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("timeAdvanceRequestAvailable")
    def timeAdvanceRequestAvailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_advance_request_available(*args, **kwargs)

    @_rti_abstract("nextMessageRequest")
    def next_message_request(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("nextMessageRequest")
    def nextMessageRequest(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.next_message_request(*args, **kwargs)

    @_rti_abstract("nextMessageRequestAvailable")
    def next_message_request_available(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("nextMessageRequestAvailable")
    def nextMessageRequestAvailable(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.next_message_request_available(*args, **kwargs)

    @_rti_abstract("flushQueueRequest")
    def flush_queue_request(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("flushQueueRequest")
    def flushQueueRequest(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.flush_queue_request(*args, **kwargs)

    @_rti_abstract("enableAsynchronousDelivery")
    def enable_asynchronous_delivery(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableAsynchronousDelivery")
    def enableAsynchronousDelivery(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_asynchronous_delivery(*args, **kwargs)

    @_rti_abstract("disableAsynchronousDelivery")
    def disable_asynchronous_delivery(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableAsynchronousDelivery")
    def disableAsynchronousDelivery(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_asynchronous_delivery(*args, **kwargs)

    @_rti_abstract("queryGALT")
    def query_galt(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryGALT")
    def queryGALT(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_galt(*args, **kwargs)

    @_rti_abstract("queryLogicalTime")
    def query_logical_time(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryLogicalTime")
    def queryLogicalTime(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_logical_time(*args, **kwargs)

    @_rti_abstract("queryLITS")
    def query_lits(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryLITS")
    def queryLITS(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_lits(*args, **kwargs)

    @_rti_abstract("modifyLookahead")
    def modify_lookahead(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("modifyLookahead")
    def modifyLookahead(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.modify_lookahead(*args, **kwargs)

    @_rti_abstract("queryLookahead")
    def query_lookahead(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("queryLookahead")
    def queryLookahead(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.query_lookahead(*args, **kwargs)

    @_rti_abstract("retract")
    def retract(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_abstract("changeAttributeOrderType")
    def change_attribute_order_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("changeAttributeOrderType")
    def changeAttributeOrderType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.change_attribute_order_type(*args, **kwargs)

    @_rti_abstract("changeInteractionOrderType")
    def change_interaction_order_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("changeInteractionOrderType")
    def changeInteractionOrderType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.change_interaction_order_type(*args, **kwargs)

    @_rti_abstract("createRegion")
    def create_region(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("createRegion")
    def createRegion(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.create_region(*args, **kwargs)

    @_rti_abstract("commitRegionModifications")
    def commit_region_modifications(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("commitRegionModifications")
    def commitRegionModifications(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.commit_region_modifications(*args, **kwargs)

    @_rti_abstract("deleteRegion")
    def delete_region(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("deleteRegion")
    def deleteRegion(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.delete_region(*args, **kwargs)

    @_rti_abstract("registerObjectInstanceWithRegions")
    def register_object_instance_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("registerObjectInstanceWithRegions")
    def registerObjectInstanceWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.register_object_instance_with_regions(*args, **kwargs)

    @_rti_abstract("associateRegionsForUpdates")
    def associate_regions_for_updates(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("associateRegionsForUpdates")
    def associateRegionsForUpdates(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.associate_regions_for_updates(*args, **kwargs)

    @_rti_abstract("unassociateRegionsForUpdates")
    def unassociate_regions_for_updates(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unassociateRegionsForUpdates")
    def unassociateRegionsForUpdates(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unassociate_regions_for_updates(*args, **kwargs)

    @_rti_abstract("subscribeObjectClassAttributesWithRegions")
    def subscribe_object_class_attributes_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeObjectClassAttributesWithRegions")
    def subscribeObjectClassAttributesWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_object_class_attributes_with_regions(*args, **kwargs)

    @_rti_abstract("subscribeObjectClassAttributesPassivelyWithRegions")
    def subscribe_object_class_attributes_passively_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeObjectClassAttributesPassivelyWithRegions")
    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_object_class_attributes_passively_with_regions(*args, **kwargs)

    @_rti_abstract("unsubscribeObjectClassAttributesWithRegions")
    def unsubscribe_object_class_attributes_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unsubscribeObjectClassAttributesWithRegions")
    def unsubscribeObjectClassAttributesWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unsubscribe_object_class_attributes_with_regions(*args, **kwargs)

    @_rti_abstract("subscribeInteractionClassWithRegions")
    def subscribe_interaction_class_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeInteractionClassWithRegions")
    def subscribeInteractionClassWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_interaction_class_with_regions(*args, **kwargs)

    @_rti_abstract("subscribeInteractionClassPassivelyWithRegions")
    def subscribe_interaction_class_passively_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("subscribeInteractionClassPassivelyWithRegions")
    def subscribeInteractionClassPassivelyWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.subscribe_interaction_class_passively_with_regions(*args, **kwargs)

    @_rti_abstract("unsubscribeInteractionClassWithRegions")
    def unsubscribe_interaction_class_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("unsubscribeInteractionClassWithRegions")
    def unsubscribeInteractionClassWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.unsubscribe_interaction_class_with_regions(*args, **kwargs)

    @_rti_abstract("sendInteractionWithRegions")
    def send_interaction_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("sendInteractionWithRegions")
    def sendInteractionWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.send_interaction_with_regions(*args, **kwargs)

    @_rti_abstract("requestAttributeValueUpdateWithRegions")
    def request_attribute_value_update_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("requestAttributeValueUpdateWithRegions")
    def requestAttributeValueUpdateWithRegions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_attribute_value_update_with_regions(*args, **kwargs)

    @_rti_abstract("getAutomaticResignDirective")
    def get_automatic_resign_directive(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAutomaticResignDirective")
    def getAutomaticResignDirective(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_automatic_resign_directive(*args, **kwargs)

    @_rti_abstract("setAutomaticResignDirective")
    def set_automatic_resign_directive(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("setAutomaticResignDirective")
    def setAutomaticResignDirective(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.set_automatic_resign_directive(*args, **kwargs)

    @_rti_abstract("getFederateHandle")
    def get_federate_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getFederateHandle")
    def getFederateHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_federate_handle(*args, **kwargs)

    @_rti_abstract("getFederateName")
    def get_federate_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getFederateName")
    def getFederateName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_federate_name(*args, **kwargs)

    @_rti_abstract("getObjectClassHandle")
    def get_object_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getObjectClassHandle")
    def getObjectClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_object_class_handle(*args, **kwargs)

    @_rti_abstract("getObjectClassName")
    def get_object_class_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getObjectClassName")
    def getObjectClassName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_object_class_name(*args, **kwargs)

    @_rti_abstract("getKnownObjectClassHandle")
    def get_known_object_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getKnownObjectClassHandle")
    def getKnownObjectClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_known_object_class_handle(*args, **kwargs)

    @_rti_abstract("getObjectInstanceHandle")
    def get_object_instance_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getObjectInstanceHandle")
    def getObjectInstanceHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_object_instance_handle(*args, **kwargs)

    @_rti_abstract("getObjectInstanceName")
    def get_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getObjectInstanceName")
    def getObjectInstanceName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_object_instance_name(*args, **kwargs)

    @_rti_abstract("getAttributeHandle")
    def get_attribute_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAttributeHandle")
    def getAttributeHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_attribute_handle(*args, **kwargs)

    @_rti_abstract("getAttributeName")
    def get_attribute_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAttributeName")
    def getAttributeName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_attribute_name(*args, **kwargs)

    @_rti_abstract("getUpdateRateValue")
    def get_update_rate_value(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getUpdateRateValue")
    def getUpdateRateValue(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_update_rate_value(*args, **kwargs)

    @_rti_abstract("getUpdateRateValueForAttribute")
    def get_update_rate_value_for_attribute(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getUpdateRateValueForAttribute")
    def getUpdateRateValueForAttribute(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_update_rate_value_for_attribute(*args, **kwargs)

    @_rti_abstract("getInteractionClassHandle")
    def get_interaction_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getInteractionClassHandle")
    def getInteractionClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_interaction_class_handle(*args, **kwargs)

    @_rti_abstract("getInteractionClassName")
    def get_interaction_class_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getInteractionClassName")
    def getInteractionClassName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_interaction_class_name(*args, **kwargs)

    @_rti_abstract("getParameterHandle")
    def get_parameter_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getParameterHandle")
    def getParameterHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_parameter_handle(*args, **kwargs)

    @_rti_abstract("getParameterName")
    def get_parameter_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getParameterName")
    def getParameterName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_parameter_name(*args, **kwargs)

    @_rti_abstract("getOrderType")
    def get_order_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getOrderType")
    def getOrderType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_order_type(*args, **kwargs)

    @_rti_abstract("getOrderName")
    def get_order_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getOrderName")
    def getOrderName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_order_name(*args, **kwargs)

    @_rti_abstract("getTransportationTypeHandle")
    def get_transportation_type_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getTransportationTypeHandle")
    def getTransportationTypeHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_transportation_type_handle(*args, **kwargs)

    @_rti_abstract("getTransportationTypeName")
    def get_transportation_type_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getTransportationTypeName")
    def getTransportationTypeName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_transportation_type_name(*args, **kwargs)

    @_rti_abstract("getAvailableDimensionsForClassAttribute")
    def get_available_dimensions_for_class_attribute(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAvailableDimensionsForClassAttribute")
    def getAvailableDimensionsForClassAttribute(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_available_dimensions_for_class_attribute(*args, **kwargs)

    @_rti_abstract("getAvailableDimensionsForInteractionClass")
    def get_available_dimensions_for_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAvailableDimensionsForInteractionClass")
    def getAvailableDimensionsForInteractionClass(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_available_dimensions_for_interaction_class(*args, **kwargs)

    @_rti_abstract("getDimensionHandle")
    def get_dimension_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getDimensionHandle")
    def getDimensionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_dimension_handle(*args, **kwargs)

    @_rti_abstract("getDimensionName")
    def get_dimension_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getDimensionName")
    def getDimensionName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_dimension_name(*args, **kwargs)

    @_rti_abstract("getDimensionUpperBound")
    def get_dimension_upper_bound(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getDimensionUpperBound")
    def getDimensionUpperBound(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_dimension_upper_bound(*args, **kwargs)

    @_rti_abstract("getDimensionHandleSet")
    def get_dimension_handle_set(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getDimensionHandleSet")
    def getDimensionHandleSet(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_dimension_handle_set(*args, **kwargs)

    @_rti_abstract("getRangeBounds")
    def get_range_bounds(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getRangeBounds")
    def getRangeBounds(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_range_bounds(*args, **kwargs)

    @_rti_abstract("setRangeBounds")
    def set_range_bounds(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("setRangeBounds")
    def setRangeBounds(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.set_range_bounds(*args, **kwargs)

    @_rti_abstract("normalizeFederateHandle")
    def normalize_federate_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("normalizeFederateHandle")
    def normalizeFederateHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.normalize_federate_handle(*args, **kwargs)

    @_rti_abstract("normalizeServiceGroup")
    def normalize_service_group(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("normalizeServiceGroup")
    def normalizeServiceGroup(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.normalize_service_group(*args, **kwargs)

    @_rti_abstract("enableObjectClassRelevanceAdvisorySwitch")
    def enable_object_class_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableObjectClassRelevanceAdvisorySwitch")
    def enableObjectClassRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_object_class_relevance_advisory_switch(*args, **kwargs)

    @_rti_abstract("disableObjectClassRelevanceAdvisorySwitch")
    def disable_object_class_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableObjectClassRelevanceAdvisorySwitch")
    def disableObjectClassRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_object_class_relevance_advisory_switch(*args, **kwargs)

    @_rti_abstract("enableAttributeRelevanceAdvisorySwitch")
    def enable_attribute_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableAttributeRelevanceAdvisorySwitch")
    def enableAttributeRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_attribute_relevance_advisory_switch(*args, **kwargs)

    @_rti_abstract("disableAttributeRelevanceAdvisorySwitch")
    def disable_attribute_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableAttributeRelevanceAdvisorySwitch")
    def disableAttributeRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_attribute_relevance_advisory_switch(*args, **kwargs)

    @_rti_abstract("enableAttributeScopeAdvisorySwitch")
    def enable_attribute_scope_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableAttributeScopeAdvisorySwitch")
    def enableAttributeScopeAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_attribute_scope_advisory_switch(*args, **kwargs)

    @_rti_abstract("disableAttributeScopeAdvisorySwitch")
    def disable_attribute_scope_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableAttributeScopeAdvisorySwitch")
    def disableAttributeScopeAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_attribute_scope_advisory_switch(*args, **kwargs)

    @_rti_abstract("enableInteractionRelevanceAdvisorySwitch")
    def enable_interaction_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableInteractionRelevanceAdvisorySwitch")
    def enableInteractionRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_interaction_relevance_advisory_switch(*args, **kwargs)

    @_rti_abstract("disableInteractionRelevanceAdvisorySwitch")
    def disable_interaction_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableInteractionRelevanceAdvisorySwitch")
    def disableInteractionRelevanceAdvisorySwitch(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_interaction_relevance_advisory_switch(*args, **kwargs)

    @_rti_abstract("evokeCallback")
    def evoke_callback(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("evokeCallback")
    def evokeCallback(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.evoke_callback(*args, **kwargs)

    @_rti_abstract("evokeMultipleCallbacks")
    def evoke_multiple_callbacks(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("evokeMultipleCallbacks")
    def evokeMultipleCallbacks(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.evoke_multiple_callbacks(*args, **kwargs)

    @_rti_abstract("enableCallbacks")
    def enable_callbacks(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("enableCallbacks")
    def enableCallbacks(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.enable_callbacks(*args, **kwargs)

    @_rti_abstract("disableCallbacks")
    def disable_callbacks(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("disableCallbacks")
    def disableCallbacks(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.disable_callbacks(*args, **kwargs)

    @_rti_abstract("getAttributeHandleFactory")
    def get_attribute_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAttributeHandleFactory")
    def getAttributeHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_attribute_handle_factory(*args, **kwargs)

    @_rti_abstract("getAttributeHandleSetFactory")
    def get_attribute_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAttributeHandleSetFactory")
    def getAttributeHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_attribute_handle_set_factory(*args, **kwargs)

    @_rti_abstract("getAttributeHandleValueMapFactory")
    def get_attribute_handle_value_map_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAttributeHandleValueMapFactory")
    def getAttributeHandleValueMapFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_attribute_handle_value_map_factory(*args, **kwargs)

    @_rti_abstract("getAttributeSetRegionSetPairListFactory")
    def get_attribute_set_region_set_pair_list_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getAttributeSetRegionSetPairListFactory")
    def getAttributeSetRegionSetPairListFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_attribute_set_region_set_pair_list_factory(*args, **kwargs)

    @_rti_abstract("getDimensionHandleFactory")
    def get_dimension_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getDimensionHandleFactory")
    def getDimensionHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_dimension_handle_factory(*args, **kwargs)

    @_rti_abstract("getDimensionHandleSetFactory")
    def get_dimension_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getDimensionHandleSetFactory")
    def getDimensionHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_dimension_handle_set_factory(*args, **kwargs)

    @_rti_abstract("getFederateHandleFactory")
    def get_federate_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getFederateHandleFactory")
    def getFederateHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_federate_handle_factory(*args, **kwargs)

    @_rti_abstract("getFederateHandleSetFactory")
    def get_federate_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getFederateHandleSetFactory")
    def getFederateHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_federate_handle_set_factory(*args, **kwargs)

    @_rti_abstract("getInteractionClassHandleFactory")
    def get_interaction_class_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getInteractionClassHandleFactory")
    def getInteractionClassHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_interaction_class_handle_factory(*args, **kwargs)

    @_rti_abstract("getObjectClassHandleFactory")
    def get_object_class_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getObjectClassHandleFactory")
    def getObjectClassHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_object_class_handle_factory(*args, **kwargs)

    @_rti_abstract("getObjectInstanceHandleFactory")
    def get_object_instance_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getObjectInstanceHandleFactory")
    def getObjectInstanceHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_object_instance_handle_factory(*args, **kwargs)

    @_rti_abstract("getParameterHandleFactory")
    def get_parameter_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getParameterHandleFactory")
    def getParameterHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_parameter_handle_factory(*args, **kwargs)

    @_rti_abstract("getParameterHandleValueMapFactory")
    def get_parameter_handle_value_map_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getParameterHandleValueMapFactory")
    def getParameterHandleValueMapFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_parameter_handle_value_map_factory(*args, **kwargs)

    @_rti_abstract("getRegionHandleSetFactory")
    def get_region_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getRegionHandleSetFactory")
    def getRegionHandleSetFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_region_handle_set_factory(*args, **kwargs)

    @_rti_abstract("getTransportationTypeHandleFactory")
    def get_transportation_type_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getTransportationTypeHandleFactory")
    def getTransportationTypeHandleFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_transportation_type_handle_factory(*args, **kwargs)

    @_rti_abstract("getHLAversion")
    def get_hla_version(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getHLAversion")
    def getHLAversion(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_hla_version(*args, **kwargs)

    @_rti_abstract("getTimeFactory")
    def get_time_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getTimeFactory")
    def getTimeFactory(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_time_factory(*args, **kwargs)

    @_rti_abstract("createFederationExecutionWithMIM")
    def create_federation_execution_with_mim(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("createFederationExecutionWithMIM")
    def createFederationExecutionWithMIM(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.create_federation_execution_with_mim(*args, **kwargs)

    @_rti_abstract("getTransportationType")
    def get_transportation_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getTransportationType")
    def getTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_transportation_type(*args, **kwargs)

    @_rti_abstract("getTransportationName")
    def get_transportation_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("getTransportationName")
    def getTransportationName(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.get_transportation_name(*args, **kwargs)

    @_rti_abstract("decodeFederateHandle")
    def decode_federate_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeFederateHandle")
    def decodeFederateHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_federate_handle(*args, **kwargs)

    @_rti_abstract("decodeObjectClassHandle")
    def decode_object_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeObjectClassHandle")
    def decodeObjectClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_object_class_handle(*args, **kwargs)

    @_rti_abstract("decodeInteractionClassHandle")
    def decode_interaction_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeInteractionClassHandle")
    def decodeInteractionClassHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_interaction_class_handle(*args, **kwargs)

    @_rti_abstract("decodeObjectInstanceHandle")
    def decode_object_instance_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeObjectInstanceHandle")
    def decodeObjectInstanceHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_object_instance_handle(*args, **kwargs)

    @_rti_abstract("decodeAttributeHandle")
    def decode_attribute_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeAttributeHandle")
    def decodeAttributeHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_attribute_handle(*args, **kwargs)

    @_rti_abstract("decodeParameterHandle")
    def decode_parameter_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeParameterHandle")
    def decodeParameterHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_parameter_handle(*args, **kwargs)

    @_rti_abstract("decodeDimensionHandle")
    def decode_dimension_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeDimensionHandle")
    def decodeDimensionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_dimension_handle(*args, **kwargs)

    @_rti_abstract("decodeMessageRetractionHandle")
    def decode_message_retraction_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeMessageRetractionHandle")
    def decodeMessageRetractionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_message_retraction_handle(*args, **kwargs)

    @_rti_abstract("decodeRegionHandle")
    def decode_region_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_alias("decodeRegionHandle")
    def decodeRegionHandle(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.decode_region_handle(*args, **kwargs)


class FederateAmbassadorSpec:
    """Pythonic no-op prototype base for federate callbacks."""

    @_callback("connectionLost")
    def connection_lost(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("connectionLost")
    def connectionLost(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.connection_lost(*args, **kwargs)

    @_callback("reportFederationExecutions")
    def report_federation_executions(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reportFederationExecutions")
    def reportFederationExecutions(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.report_federation_executions(*args, **kwargs)

    @_callback("synchronizationPointRegistrationSucceeded")
    def synchronization_point_registration_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("synchronizationPointRegistrationSucceeded")
    def synchronizationPointRegistrationSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.synchronization_point_registration_succeeded(*args, **kwargs)

    @_callback("synchronizationPointRegistrationFailed")
    def synchronization_point_registration_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("synchronizationPointRegistrationFailed")
    def synchronizationPointRegistrationFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.synchronization_point_registration_failed(*args, **kwargs)

    @_callback("announceSynchronizationPoint")
    def announce_synchronization_point(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("announceSynchronizationPoint")
    def announceSynchronizationPoint(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.announce_synchronization_point(*args, **kwargs)

    @_callback("federationSynchronized")
    def federation_synchronized(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationSynchronized")
    def federationSynchronized(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_synchronized(*args, **kwargs)

    @_callback("initiateFederateSave")
    def initiate_federate_save(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("initiateFederateSave")
    def initiateFederateSave(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.initiate_federate_save(*args, **kwargs)

    @_callback("federationSaved")
    def federation_saved(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationSaved")
    def federationSaved(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_saved(*args, **kwargs)

    @_callback("federationNotSaved")
    def federation_not_saved(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationNotSaved")
    def federationNotSaved(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_not_saved(*args, **kwargs)

    @_callback("federationSaveStatusResponse")
    def federation_save_status_response(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationSaveStatusResponse")
    def federationSaveStatusResponse(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_save_status_response(*args, **kwargs)

    @_callback("requestFederationRestoreSucceeded")
    def request_federation_restore_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestFederationRestoreSucceeded")
    def requestFederationRestoreSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_federation_restore_succeeded(*args, **kwargs)

    @_callback("requestFederationRestoreFailed")
    def request_federation_restore_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestFederationRestoreFailed")
    def requestFederationRestoreFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_federation_restore_failed(*args, **kwargs)

    @_callback("federationRestoreBegun")
    def federation_restore_begun(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationRestoreBegun")
    def federationRestoreBegun(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_restore_begun(*args, **kwargs)

    @_callback("initiateFederateRestore")
    def initiate_federate_restore(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("initiateFederateRestore")
    def initiateFederateRestore(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.initiate_federate_restore(*args, **kwargs)

    @_callback("federationRestored")
    def federation_restored(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationRestored")
    def federationRestored(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_restored(*args, **kwargs)

    @_callback("federationNotRestored")
    def federation_not_restored(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationNotRestored")
    def federationNotRestored(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_not_restored(*args, **kwargs)

    @_callback("federationRestoreStatusResponse")
    def federation_restore_status_response(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("federationRestoreStatusResponse")
    def federationRestoreStatusResponse(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.federation_restore_status_response(*args, **kwargs)

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

    @_callback("turnInteractionsOn")
    def turn_interactions_on(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnInteractionsOn")
    def turnInteractionsOn(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_interactions_on(*args, **kwargs)

    @_callback("turnInteractionsOff")
    def turn_interactions_off(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnInteractionsOff")
    def turnInteractionsOff(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_interactions_off(*args, **kwargs)

    @_callback("objectInstanceNameReservationSucceeded")
    def object_instance_name_reservation_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("objectInstanceNameReservationSucceeded")
    def objectInstanceNameReservationSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.object_instance_name_reservation_succeeded(*args, **kwargs)

    @_callback("objectInstanceNameReservationFailed")
    def object_instance_name_reservation_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("objectInstanceNameReservationFailed")
    def objectInstanceNameReservationFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.object_instance_name_reservation_failed(*args, **kwargs)

    @_callback("multipleObjectInstanceNameReservationSucceeded")
    def multiple_object_instance_name_reservation_succeeded(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("multipleObjectInstanceNameReservationSucceeded")
    def multipleObjectInstanceNameReservationSucceeded(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.multiple_object_instance_name_reservation_succeeded(*args, **kwargs)

    @_callback("multipleObjectInstanceNameReservationFailed")
    def multiple_object_instance_name_reservation_failed(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("multipleObjectInstanceNameReservationFailed")
    def multipleObjectInstanceNameReservationFailed(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.multiple_object_instance_name_reservation_failed(*args, **kwargs)

    @_callback("discoverObjectInstance")
    def discover_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("discoverObjectInstance")
    def discoverObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.discover_object_instance(*args, **kwargs)

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

    @_callback("reflectAttributeValues")
    def reflect_attribute_values(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reflectAttributeValues")
    def reflectAttributeValues(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.reflect_attribute_values(*args, **kwargs)

    @_callback("receiveInteraction")
    def receive_interaction(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("receiveInteraction")
    def receiveInteraction(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.receive_interaction(*args, **kwargs)

    @_callback("removeObjectInstance")
    def remove_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("removeObjectInstance")
    def removeObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.remove_object_instance(*args, **kwargs)

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

    @_callback("provideAttributeValueUpdate")
    def provide_attribute_value_update(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("provideAttributeValueUpdate")
    def provideAttributeValueUpdate(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.provide_attribute_value_update(*args, **kwargs)

    @_callback("turnUpdatesOnForObjectInstance")
    def turn_updates_on_for_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnUpdatesOnForObjectInstance")
    def turnUpdatesOnForObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_updates_on_for_object_instance(*args, **kwargs)

    @_callback("turnUpdatesOffForObjectInstance")
    def turn_updates_off_for_object_instance(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("turnUpdatesOffForObjectInstance")
    def turnUpdatesOffForObjectInstance(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.turn_updates_off_for_object_instance(*args, **kwargs)

    @_callback("confirmAttributeTransportationTypeChange")
    def confirm_attribute_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("confirmAttributeTransportationTypeChange")
    def confirmAttributeTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_attribute_transportation_type_change(*args, **kwargs)

    @_callback("reportAttributeTransportationType")
    def report_attribute_transportation_type(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("reportAttributeTransportationType")
    def reportAttributeTransportationType(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.report_attribute_transportation_type(*args, **kwargs)

    @_callback("confirmInteractionTransportationTypeChange")
    def confirm_interaction_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("confirmInteractionTransportationTypeChange")
    def confirmInteractionTransportationTypeChange(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_interaction_transportation_type_change(*args, **kwargs)

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

    @_callback("requestDivestitureConfirmation")
    def request_divestiture_confirmation(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestDivestitureConfirmation")
    def requestDivestitureConfirmation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_divestiture_confirmation(*args, **kwargs)

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

    @_callback("requestAttributeOwnershipRelease")
    def request_attribute_ownership_release(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestAttributeOwnershipRelease")
    def requestAttributeOwnershipRelease(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_attribute_ownership_release(*args, **kwargs)

    @_callback("confirmAttributeOwnershipAcquisitionCancellation")
    def confirm_attribute_ownership_acquisition_cancellation(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("confirmAttributeOwnershipAcquisitionCancellation")
    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.confirm_attribute_ownership_acquisition_cancellation(*args, **kwargs)

    @_callback("informAttributeOwnership")
    def inform_attribute_ownership(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("informAttributeOwnership")
    def informAttributeOwnership(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.inform_attribute_ownership(*args, **kwargs)

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

    @_callback("timeRegulationEnabled")
    def time_regulation_enabled(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("timeRegulationEnabled")
    def timeRegulationEnabled(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_regulation_enabled(*args, **kwargs)

    @_callback("timeConstrainedEnabled")
    def time_constrained_enabled(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("timeConstrainedEnabled")
    def timeConstrainedEnabled(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_constrained_enabled(*args, **kwargs)

    @_callback("timeAdvanceGrant")
    def time_advance_grant(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("timeAdvanceGrant")
    def timeAdvanceGrant(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.time_advance_grant(*args, **kwargs)

    @_callback("requestRetraction")
    def request_retraction(self, *args: object, **kwargs: object) -> object:
        return None

    @_callback("requestRetraction")
    def requestRetraction(self, *args: object, **kwargs: object) -> object:  # noqa: N802
        return self.request_retraction(*args, **kwargs)


__all__ = [
    "FederateAmbassador",
    "FederateAmbassadorSpec",
    "NullFederateAmbassador",
    "RTIambassador",
    "RTIambassadorSpec",
    "lower_camel_to_snake",
]

RTIambassador = RTIambassadorSpec
FederateAmbassador = FederateAmbassadorSpec
NullFederateAmbassador = FederateAmbassadorSpec
