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


def _rti_service(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_name = method_name  # type: ignore[attr-defined]
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name, method.__name__)
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

    @_rti_service("abortFederationRestore")
    @abstractmethod
    def abort_federation_restore(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("abortFederationSave")
    @abstractmethod
    def abort_federation_save(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("associateRegionsForUpdates")
    @abstractmethod
    def associate_regions_for_updates(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("attributeOwnershipAcquisition")
    @abstractmethod
    def attribute_ownership_acquisition(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("attributeOwnershipAcquisitionIfAvailable")
    @abstractmethod
    def attribute_ownership_acquisition_if_available(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("attributeOwnershipDivestitureIfWanted")
    @abstractmethod
    def attribute_ownership_divestiture_if_wanted(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("attributeOwnershipReleaseDenied")
    @abstractmethod
    def attribute_ownership_release_denied(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("cancelAttributeOwnershipAcquisition")
    @abstractmethod
    def cancel_attribute_ownership_acquisition(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("cancelNegotiatedAttributeOwnershipDivestiture")
    @abstractmethod
    def cancel_negotiated_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("changeAttributeOrderType")
    @abstractmethod
    def change_attribute_order_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("changeInteractionOrderType")
    @abstractmethod
    def change_interaction_order_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("commitRegionModifications")
    @abstractmethod
    def commit_region_modifications(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("confirmDivestiture")
    @abstractmethod
    def confirm_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("connect")
    @abstractmethod
    def connect(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("createFederationExecution")
    @abstractmethod
    def create_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("createFederationExecutionWithMIM")
    @abstractmethod
    def create_federation_execution_with_mim(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("createRegion")
    @abstractmethod
    def create_region(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeAttributeHandle")
    @abstractmethod
    def decode_attribute_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeDimensionHandle")
    @abstractmethod
    def decode_dimension_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeFederateHandle")
    @abstractmethod
    def decode_federate_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeInteractionClassHandle")
    @abstractmethod
    def decode_interaction_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeMessageRetractionHandle")
    @abstractmethod
    def decode_message_retraction_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeObjectClassHandle")
    @abstractmethod
    def decode_object_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeObjectInstanceHandle")
    @abstractmethod
    def decode_object_instance_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeParameterHandle")
    @abstractmethod
    def decode_parameter_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("decodeRegionHandle")
    @abstractmethod
    def decode_region_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("deleteObjectInstance")
    @abstractmethod
    def delete_object_instance(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("deleteRegion")
    @abstractmethod
    def delete_region(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("destroyFederationExecution")
    @abstractmethod
    def destroy_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableAsynchronousDelivery")
    @abstractmethod
    def disable_asynchronous_delivery(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableAttributeRelevanceAdvisorySwitch")
    @abstractmethod
    def disable_attribute_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableAttributeScopeAdvisorySwitch")
    @abstractmethod
    def disable_attribute_scope_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableCallbacks")
    @abstractmethod
    def disable_callbacks(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableInteractionRelevanceAdvisorySwitch")
    @abstractmethod
    def disable_interaction_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableObjectClassRelevanceAdvisorySwitch")
    @abstractmethod
    def disable_object_class_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableTimeConstrained")
    @abstractmethod
    def disable_time_constrained(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disableTimeRegulation")
    @abstractmethod
    def disable_time_regulation(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("disconnect")
    @abstractmethod
    def disconnect(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableAsynchronousDelivery")
    @abstractmethod
    def enable_asynchronous_delivery(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableAttributeRelevanceAdvisorySwitch")
    @abstractmethod
    def enable_attribute_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableAttributeScopeAdvisorySwitch")
    @abstractmethod
    def enable_attribute_scope_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableCallbacks")
    @abstractmethod
    def enable_callbacks(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableInteractionRelevanceAdvisorySwitch")
    @abstractmethod
    def enable_interaction_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableObjectClassRelevanceAdvisorySwitch")
    @abstractmethod
    def enable_object_class_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableTimeConstrained")
    @abstractmethod
    def enable_time_constrained(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("enableTimeRegulation")
    @abstractmethod
    def enable_time_regulation(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("evokeCallback")
    @abstractmethod
    def evoke_callback(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("evokeMultipleCallbacks")
    @abstractmethod
    def evoke_multiple_callbacks(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("federateRestoreComplete")
    @abstractmethod
    def federate_restore_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("federateRestoreNotComplete")
    @abstractmethod
    def federate_restore_not_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("federateSaveBegun")
    @abstractmethod
    def federate_save_begun(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("federateSaveComplete")
    @abstractmethod
    def federate_save_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("federateSaveNotComplete")
    @abstractmethod
    def federate_save_not_complete(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("flushQueueRequest")
    @abstractmethod
    def flush_queue_request(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAttributeHandle")
    @abstractmethod
    def get_attribute_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAttributeHandleFactory")
    @abstractmethod
    def get_attribute_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAttributeHandleSetFactory")
    @abstractmethod
    def get_attribute_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAttributeHandleValueMapFactory")
    @abstractmethod
    def get_attribute_handle_value_map_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAttributeName")
    @abstractmethod
    def get_attribute_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAttributeSetRegionSetPairListFactory")
    @abstractmethod
    def get_attribute_set_region_set_pair_list_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAutomaticResignDirective")
    @abstractmethod
    def get_automatic_resign_directive(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAvailableDimensionsForClassAttribute")
    @abstractmethod
    def get_available_dimensions_for_class_attribute(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getAvailableDimensionsForInteractionClass")
    @abstractmethod
    def get_available_dimensions_for_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getDimensionHandle")
    @abstractmethod
    def get_dimension_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getDimensionHandleFactory")
    @abstractmethod
    def get_dimension_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getDimensionHandleSet")
    @abstractmethod
    def get_dimension_handle_set(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getDimensionHandleSetFactory")
    @abstractmethod
    def get_dimension_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getDimensionName")
    @abstractmethod
    def get_dimension_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getDimensionUpperBound")
    @abstractmethod
    def get_dimension_upper_bound(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getFederateHandle")
    @abstractmethod
    def get_federate_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getFederateHandleFactory")
    @abstractmethod
    def get_federate_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getFederateHandleSetFactory")
    @abstractmethod
    def get_federate_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getFederateName")
    @abstractmethod
    def get_federate_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getHLAversion")
    @abstractmethod
    def get_hla_version(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getInteractionClassHandle")
    @abstractmethod
    def get_interaction_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getInteractionClassHandleFactory")
    @abstractmethod
    def get_interaction_class_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getInteractionClassName")
    @abstractmethod
    def get_interaction_class_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getKnownObjectClassHandle")
    @abstractmethod
    def get_known_object_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getObjectClassHandle")
    @abstractmethod
    def get_object_class_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getObjectClassHandleFactory")
    @abstractmethod
    def get_object_class_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getObjectClassName")
    @abstractmethod
    def get_object_class_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getObjectInstanceHandle")
    @abstractmethod
    def get_object_instance_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getObjectInstanceHandleFactory")
    @abstractmethod
    def get_object_instance_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getObjectInstanceName")
    @abstractmethod
    def get_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getOrderName")
    @abstractmethod
    def get_order_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getOrderType")
    @abstractmethod
    def get_order_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getParameterHandle")
    @abstractmethod
    def get_parameter_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getParameterHandleFactory")
    @abstractmethod
    def get_parameter_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getParameterHandleValueMapFactory")
    @abstractmethod
    def get_parameter_handle_value_map_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getParameterName")
    @abstractmethod
    def get_parameter_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getRangeBounds")
    @abstractmethod
    def get_range_bounds(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getRegionHandleSetFactory")
    @abstractmethod
    def get_region_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getTimeFactory")
    @abstractmethod
    def get_time_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getTransportationName")
    @abstractmethod
    def get_transportation_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getTransportationType")
    @abstractmethod
    def get_transportation_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getTransportationTypeHandle")
    @abstractmethod
    def get_transportation_type_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getTransportationTypeHandleFactory")
    @abstractmethod
    def get_transportation_type_handle_factory(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getTransportationTypeName")
    @abstractmethod
    def get_transportation_type_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getUpdateRateValue")
    @abstractmethod
    def get_update_rate_value(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("getUpdateRateValueForAttribute")
    @abstractmethod
    def get_update_rate_value_for_attribute(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("isAttributeOwnedByFederate")
    @abstractmethod
    def is_attribute_owned_by_federate(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("joinFederationExecution")
    @abstractmethod
    def join_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("listFederationExecutions")
    @abstractmethod
    def list_federation_executions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("localDeleteObjectInstance")
    @abstractmethod
    def local_delete_object_instance(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("modifyLookahead")
    @abstractmethod
    def modify_lookahead(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("negotiatedAttributeOwnershipDivestiture")
    @abstractmethod
    def negotiated_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("nextMessageRequest")
    @abstractmethod
    def next_message_request(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("nextMessageRequestAvailable")
    @abstractmethod
    def next_message_request_available(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("normalizeFederateHandle")
    @abstractmethod
    def normalize_federate_handle(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("normalizeServiceGroup")
    @abstractmethod
    def normalize_service_group(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("publishInteractionClass")
    @abstractmethod
    def publish_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("publishObjectClassAttributes")
    @abstractmethod
    def publish_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryAttributeOwnership")
    @abstractmethod
    def query_attribute_ownership(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryAttributeTransportationType")
    @abstractmethod
    def query_attribute_transportation_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryFederationRestoreStatus")
    @abstractmethod
    def query_federation_restore_status(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryFederationSaveStatus")
    @abstractmethod
    def query_federation_save_status(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryGALT")
    @abstractmethod
    def query_galt(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryInteractionTransportationType")
    @abstractmethod
    def query_interaction_transportation_type(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryLITS")
    @abstractmethod
    def query_lits(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryLogicalTime")
    @abstractmethod
    def query_logical_time(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("queryLookahead")
    @abstractmethod
    def query_lookahead(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("registerFederationSynchronizationPoint")
    @abstractmethod
    def register_federation_synchronization_point(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("registerObjectInstance")
    @abstractmethod
    def register_object_instance(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("registerObjectInstanceWithRegions")
    @abstractmethod
    def register_object_instance_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("releaseMultipleObjectInstanceName")
    @abstractmethod
    def release_multiple_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("releaseObjectInstanceName")
    @abstractmethod
    def release_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("requestAttributeTransportationTypeChange")
    @abstractmethod
    def request_attribute_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("requestAttributeValueUpdate")
    @abstractmethod
    def request_attribute_value_update(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("requestAttributeValueUpdateWithRegions")
    @abstractmethod
    def request_attribute_value_update_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("requestFederationRestore")
    @abstractmethod
    def request_federation_restore(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("requestFederationSave")
    @abstractmethod
    def request_federation_save(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("requestInteractionTransportationTypeChange")
    @abstractmethod
    def request_interaction_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("reserveMultipleObjectInstanceName")
    @abstractmethod
    def reserve_multiple_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("reserveObjectInstanceName")
    @abstractmethod
    def reserve_object_instance_name(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("resignFederationExecution")
    @abstractmethod
    def resign_federation_execution(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("retract")
    @abstractmethod
    def retract(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("sendInteraction")
    @abstractmethod
    def send_interaction(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("sendInteractionWithRegions")
    @abstractmethod
    def send_interaction_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("setAutomaticResignDirective")
    @abstractmethod
    def set_automatic_resign_directive(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("setRangeBounds")
    @abstractmethod
    def set_range_bounds(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeInteractionClass")
    @abstractmethod
    def subscribe_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeInteractionClassPassively")
    @abstractmethod
    def subscribe_interaction_class_passively(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeInteractionClassPassivelyWithRegions")
    @abstractmethod
    def subscribe_interaction_class_passively_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeInteractionClassWithRegions")
    @abstractmethod
    def subscribe_interaction_class_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeObjectClassAttributes")
    @abstractmethod
    def subscribe_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeObjectClassAttributesPassively")
    @abstractmethod
    def subscribe_object_class_attributes_passively(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeObjectClassAttributesPassivelyWithRegions")
    @abstractmethod
    def subscribe_object_class_attributes_passively_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("subscribeObjectClassAttributesWithRegions")
    @abstractmethod
    def subscribe_object_class_attributes_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("synchronizationPointAchieved")
    @abstractmethod
    def synchronization_point_achieved(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("timeAdvanceRequest")
    @abstractmethod
    def time_advance_request(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("timeAdvanceRequestAvailable")
    @abstractmethod
    def time_advance_request_available(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unassociateRegionsForUpdates")
    @abstractmethod
    def unassociate_regions_for_updates(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unconditionalAttributeOwnershipDivestiture")
    @abstractmethod
    def unconditional_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unpublishInteractionClass")
    @abstractmethod
    def unpublish_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unpublishObjectClass")
    @abstractmethod
    def unpublish_object_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unpublishObjectClassAttributes")
    @abstractmethod
    def unpublish_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unsubscribeInteractionClass")
    @abstractmethod
    def unsubscribe_interaction_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unsubscribeInteractionClassWithRegions")
    @abstractmethod
    def unsubscribe_interaction_class_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unsubscribeObjectClass")
    @abstractmethod
    def unsubscribe_object_class(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unsubscribeObjectClassAttributes")
    @abstractmethod
    def unsubscribe_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("unsubscribeObjectClassAttributesWithRegions")
    @abstractmethod
    def unsubscribe_object_class_attributes_with_regions(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    @_rti_service("updateAttributeValues")
    @abstractmethod
    def update_attribute_values(self, *args: object, **kwargs: object) -> object:
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
