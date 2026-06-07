"""Pythonic convenience layer for the HLA 1516.1-2010 API scaffold.

This layer adds snake_case aliases while retaining the source lowerCamelCase API.

Attribution: "Reprinted with permission from IEEE 1516.1(TM)-2010".
"""
from __future__ import annotations

from typing import Any

from .raw_api import FederateAmbassador as RawFederateAmbassador
from .raw_api import RTIambassador as RawRTIambassador


class PythonicRTIAmbassadorMixin:
    """Mixin that forwards snake_case service names to lowerCamelCase services."""

    def abort_federation_restore(self, *args: Any, **kwargs: Any) -> Any:
        return self.abortFederationRestore(*args, **kwargs)

    def abort_federation_save(self, *args: Any, **kwargs: Any) -> Any:
        return self.abortFederationSave(*args, **kwargs)

    def associate_regions_for_updates(self, *args: Any, **kwargs: Any) -> Any:
        return self.associateRegionsForUpdates(*args, **kwargs)

    def attribute_ownership_acquisition(self, *args: Any, **kwargs: Any) -> Any:
        return self.attributeOwnershipAcquisition(*args, **kwargs)

    def attribute_ownership_acquisition_if_available(self, *args: Any, **kwargs: Any) -> Any:
        return self.attributeOwnershipAcquisitionIfAvailable(*args, **kwargs)

    def attribute_ownership_divestiture_if_wanted(self, *args: Any, **kwargs: Any) -> Any:
        return self.attributeOwnershipDivestitureIfWanted(*args, **kwargs)

    def attribute_ownership_release_denied(self, *args: Any, **kwargs: Any) -> Any:
        return self.attributeOwnershipReleaseDenied(*args, **kwargs)

    def cancel_attribute_ownership_acquisition(self, *args: Any, **kwargs: Any) -> Any:
        return self.cancelAttributeOwnershipAcquisition(*args, **kwargs)

    def cancel_negotiated_attribute_ownership_divestiture(self, *args: Any, **kwargs: Any) -> Any:
        return self.cancelNegotiatedAttributeOwnershipDivestiture(*args, **kwargs)

    def change_attribute_order_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.changeAttributeOrderType(*args, **kwargs)

    def change_interaction_order_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.changeInteractionOrderType(*args, **kwargs)

    def commit_region_modifications(self, *args: Any, **kwargs: Any) -> Any:
        return self.commitRegionModifications(*args, **kwargs)

    def confirm_divestiture(self, *args: Any, **kwargs: Any) -> Any:
        return self.confirmDivestiture(*args, **kwargs)

    def create_federation_execution(self, *args: Any, **kwargs: Any) -> Any:
        return self.createFederationExecution(*args, **kwargs)

    def create_federation_execution_with_mim(self, *args: Any, **kwargs: Any) -> Any:
        return self.createFederationExecutionWithMIM(*args, **kwargs)

    def create_region(self, *args: Any, **kwargs: Any) -> Any:
        return self.createRegion(*args, **kwargs)

    def decode_attribute_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeAttributeHandle(*args, **kwargs)

    def decode_dimension_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeDimensionHandle(*args, **kwargs)

    def decode_federate_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeFederateHandle(*args, **kwargs)

    def decode_interaction_class_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeInteractionClassHandle(*args, **kwargs)

    def decode_message_retraction_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeMessageRetractionHandle(*args, **kwargs)

    def decode_object_class_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeObjectClassHandle(*args, **kwargs)

    def decode_object_instance_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeObjectInstanceHandle(*args, **kwargs)

    def decode_parameter_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeParameterHandle(*args, **kwargs)

    def decode_region_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.decodeRegionHandle(*args, **kwargs)

    def delete_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.deleteObjectInstance(*args, **kwargs)

    def delete_region(self, *args: Any, **kwargs: Any) -> Any:
        return self.deleteRegion(*args, **kwargs)

    def destroy_federation_execution(self, *args: Any, **kwargs: Any) -> Any:
        return self.destroyFederationExecution(*args, **kwargs)

    def disable_asynchronous_delivery(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableAsynchronousDelivery(*args, **kwargs)

    def disable_attribute_relevance_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableAttributeRelevanceAdvisorySwitch(*args, **kwargs)

    def disable_attribute_scope_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableAttributeScopeAdvisorySwitch(*args, **kwargs)

    def disable_callbacks(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableCallbacks(*args, **kwargs)

    def disable_interaction_relevance_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableInteractionRelevanceAdvisorySwitch(*args, **kwargs)

    def disable_object_class_relevance_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableObjectClassRelevanceAdvisorySwitch(*args, **kwargs)

    def disable_time_constrained(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableTimeConstrained(*args, **kwargs)

    def disable_time_regulation(self, *args: Any, **kwargs: Any) -> Any:
        return self.disableTimeRegulation(*args, **kwargs)

    def enable_asynchronous_delivery(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableAsynchronousDelivery(*args, **kwargs)

    def enable_attribute_relevance_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableAttributeRelevanceAdvisorySwitch(*args, **kwargs)

    def enable_attribute_scope_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableAttributeScopeAdvisorySwitch(*args, **kwargs)

    def enable_callbacks(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableCallbacks(*args, **kwargs)

    def enable_interaction_relevance_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableInteractionRelevanceAdvisorySwitch(*args, **kwargs)

    def enable_object_class_relevance_advisory_switch(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableObjectClassRelevanceAdvisorySwitch(*args, **kwargs)

    def enable_time_constrained(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableTimeConstrained(*args, **kwargs)

    def enable_time_regulation(self, *args: Any, **kwargs: Any) -> Any:
        return self.enableTimeRegulation(*args, **kwargs)

    def evoke_callback(self, *args: Any, **kwargs: Any) -> Any:
        return self.evokeCallback(*args, **kwargs)

    def evoke_multiple_callbacks(self, *args: Any, **kwargs: Any) -> Any:
        return self.evokeMultipleCallbacks(*args, **kwargs)

    def federate_restore_complete(self, *args: Any, **kwargs: Any) -> Any:
        return self.federateRestoreComplete(*args, **kwargs)

    def federate_restore_not_complete(self, *args: Any, **kwargs: Any) -> Any:
        return self.federateRestoreNotComplete(*args, **kwargs)

    def federate_save_begun(self, *args: Any, **kwargs: Any) -> Any:
        return self.federateSaveBegun(*args, **kwargs)

    def federate_save_complete(self, *args: Any, **kwargs: Any) -> Any:
        return self.federateSaveComplete(*args, **kwargs)

    def federate_save_not_complete(self, *args: Any, **kwargs: Any) -> Any:
        return self.federateSaveNotComplete(*args, **kwargs)

    def flush_queue_request(self, *args: Any, **kwargs: Any) -> Any:
        return self.flushQueueRequest(*args, **kwargs)

    def get_attribute_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAttributeHandle(*args, **kwargs)

    def get_attribute_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAttributeHandleFactory(*args, **kwargs)

    def get_attribute_handle_set_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAttributeHandleSetFactory(*args, **kwargs)

    def get_attribute_handle_value_map_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAttributeHandleValueMapFactory(*args, **kwargs)

    def get_attribute_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAttributeName(*args, **kwargs)

    def get_attribute_set_region_set_pair_list_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAttributeSetRegionSetPairListFactory(*args, **kwargs)

    def get_automatic_resign_directive(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAutomaticResignDirective(*args, **kwargs)

    def get_available_dimensions_for_class_attribute(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAvailableDimensionsForClassAttribute(*args, **kwargs)

    def get_available_dimensions_for_interaction_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.getAvailableDimensionsForInteractionClass(*args, **kwargs)

    def get_dimension_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getDimensionHandle(*args, **kwargs)

    def get_dimension_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getDimensionHandleFactory(*args, **kwargs)

    def get_dimension_handle_set(self, *args: Any, **kwargs: Any) -> Any:
        return self.getDimensionHandleSet(*args, **kwargs)

    def get_dimension_handle_set_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getDimensionHandleSetFactory(*args, **kwargs)

    def get_dimension_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getDimensionName(*args, **kwargs)

    def get_dimension_upper_bound(self, *args: Any, **kwargs: Any) -> Any:
        return self.getDimensionUpperBound(*args, **kwargs)

    def get_federate_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getFederateHandle(*args, **kwargs)

    def get_federate_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getFederateHandleFactory(*args, **kwargs)

    def get_federate_handle_set_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getFederateHandleSetFactory(*args, **kwargs)

    def get_federate_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getFederateName(*args, **kwargs)

    def get_hl_aversion(self, *args: Any, **kwargs: Any) -> Any:
        return self.getHLAversion(*args, **kwargs)

    def get_interaction_class_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getInteractionClassHandle(*args, **kwargs)

    def get_interaction_class_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getInteractionClassHandleFactory(*args, **kwargs)

    def get_interaction_class_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getInteractionClassName(*args, **kwargs)

    def get_known_object_class_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getKnownObjectClassHandle(*args, **kwargs)

    def get_object_class_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getObjectClassHandle(*args, **kwargs)

    def get_object_class_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getObjectClassHandleFactory(*args, **kwargs)

    def get_object_class_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getObjectClassName(*args, **kwargs)

    def get_object_instance_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getObjectInstanceHandle(*args, **kwargs)

    def get_object_instance_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getObjectInstanceHandleFactory(*args, **kwargs)

    def get_object_instance_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getObjectInstanceName(*args, **kwargs)

    def get_order_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getOrderName(*args, **kwargs)

    def get_order_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.getOrderType(*args, **kwargs)

    def get_parameter_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getParameterHandle(*args, **kwargs)

    def get_parameter_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getParameterHandleFactory(*args, **kwargs)

    def get_parameter_handle_value_map_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getParameterHandleValueMapFactory(*args, **kwargs)

    def get_parameter_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getParameterName(*args, **kwargs)

    def get_range_bounds(self, *args: Any, **kwargs: Any) -> Any:
        return self.getRangeBounds(*args, **kwargs)

    def get_region_handle_set_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getRegionHandleSetFactory(*args, **kwargs)

    def get_time_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getTimeFactory(*args, **kwargs)

    def get_transportation_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getTransportationName(*args, **kwargs)

    def get_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.getTransportationType(*args, **kwargs)

    def get_transportation_type_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.getTransportationTypeHandle(*args, **kwargs)

    def get_transportation_type_handle_factory(self, *args: Any, **kwargs: Any) -> Any:
        return self.getTransportationTypeHandleFactory(*args, **kwargs)

    def get_transportation_type_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.getTransportationTypeName(*args, **kwargs)

    def get_update_rate_value(self, *args: Any, **kwargs: Any) -> Any:
        return self.getUpdateRateValue(*args, **kwargs)

    def get_update_rate_value_for_attribute(self, *args: Any, **kwargs: Any) -> Any:
        return self.getUpdateRateValueForAttribute(*args, **kwargs)

    def is_attribute_owned_by_federate(self, *args: Any, **kwargs: Any) -> Any:
        return self.isAttributeOwnedByFederate(*args, **kwargs)

    def join_federation_execution(self, *args: Any, **kwargs: Any) -> Any:
        return self.joinFederationExecution(*args, **kwargs)

    def list_federation_executions(self, *args: Any, **kwargs: Any) -> Any:
        return self.listFederationExecutions(*args, **kwargs)

    def local_delete_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.localDeleteObjectInstance(*args, **kwargs)

    def modify_lookahead(self, *args: Any, **kwargs: Any) -> Any:
        return self.modifyLookahead(*args, **kwargs)

    def negotiated_attribute_ownership_divestiture(self, *args: Any, **kwargs: Any) -> Any:
        return self.negotiatedAttributeOwnershipDivestiture(*args, **kwargs)

    def next_message_request(self, *args: Any, **kwargs: Any) -> Any:
        return self.nextMessageRequest(*args, **kwargs)

    def next_message_request_available(self, *args: Any, **kwargs: Any) -> Any:
        return self.nextMessageRequestAvailable(*args, **kwargs)

    def normalize_federate_handle(self, *args: Any, **kwargs: Any) -> Any:
        return self.normalizeFederateHandle(*args, **kwargs)

    def normalize_service_group(self, *args: Any, **kwargs: Any) -> Any:
        return self.normalizeServiceGroup(*args, **kwargs)

    def publish_interaction_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.publishInteractionClass(*args, **kwargs)

    def publish_object_class_attributes(self, *args: Any, **kwargs: Any) -> Any:
        return self.publishObjectClassAttributes(*args, **kwargs)

    def query_attribute_ownership(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryAttributeOwnership(*args, **kwargs)

    def query_attribute_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryAttributeTransportationType(*args, **kwargs)

    def query_federation_restore_status(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryFederationRestoreStatus(*args, **kwargs)

    def query_federation_save_status(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryFederationSaveStatus(*args, **kwargs)

    def query_galt(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryGALT(*args, **kwargs)

    def query_interaction_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryInteractionTransportationType(*args, **kwargs)

    def query_lits(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryLITS(*args, **kwargs)

    def query_logical_time(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryLogicalTime(*args, **kwargs)

    def query_lookahead(self, *args: Any, **kwargs: Any) -> Any:
        return self.queryLookahead(*args, **kwargs)

    def register_federation_synchronization_point(self, *args: Any, **kwargs: Any) -> Any:
        return self.registerFederationSynchronizationPoint(*args, **kwargs)

    def register_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return self.registerObjectInstance(*args, **kwargs)

    def register_object_instance_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.registerObjectInstanceWithRegions(*args, **kwargs)

    def release_multiple_object_instance_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.releaseMultipleObjectInstanceName(*args, **kwargs)

    def release_object_instance_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.releaseObjectInstanceName(*args, **kwargs)

    def request_attribute_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return self.requestAttributeTransportationTypeChange(*args, **kwargs)

    def request_attribute_value_update(self, *args: Any, **kwargs: Any) -> Any:
        return self.requestAttributeValueUpdate(*args, **kwargs)

    def request_attribute_value_update_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.requestAttributeValueUpdateWithRegions(*args, **kwargs)

    def request_federation_restore(self, *args: Any, **kwargs: Any) -> Any:
        return self.requestFederationRestore(*args, **kwargs)

    def request_federation_save(self, *args: Any, **kwargs: Any) -> Any:
        return self.requestFederationSave(*args, **kwargs)

    def request_interaction_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return self.requestInteractionTransportationTypeChange(*args, **kwargs)

    def reserve_multiple_object_instance_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.reserveMultipleObjectInstanceName(*args, **kwargs)

    def reserve_object_instance_name(self, *args: Any, **kwargs: Any) -> Any:
        return self.reserveObjectInstanceName(*args, **kwargs)

    def resign_federation_execution(self, *args: Any, **kwargs: Any) -> Any:
        return self.resignFederationExecution(*args, **kwargs)

    def send_interaction(self, *args: Any, **kwargs: Any) -> Any:
        return self.sendInteraction(*args, **kwargs)

    def send_interaction_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.sendInteractionWithRegions(*args, **kwargs)

    def set_automatic_resign_directive(self, *args: Any, **kwargs: Any) -> Any:
        return self.setAutomaticResignDirective(*args, **kwargs)

    def set_range_bounds(self, *args: Any, **kwargs: Any) -> Any:
        return self.setRangeBounds(*args, **kwargs)

    def subscribe_interaction_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeInteractionClass(*args, **kwargs)

    def subscribe_interaction_class_passively(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeInteractionClassPassively(*args, **kwargs)

    def subscribe_interaction_class_passively_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeInteractionClassPassivelyWithRegions(*args, **kwargs)

    def subscribe_interaction_class_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeInteractionClassWithRegions(*args, **kwargs)

    def subscribe_object_class_attributes(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeObjectClassAttributes(*args, **kwargs)

    def subscribe_object_class_attributes_passively(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeObjectClassAttributesPassively(*args, **kwargs)

    def subscribe_object_class_attributes_passively_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeObjectClassAttributesPassivelyWithRegions(*args, **kwargs)

    def subscribe_object_class_attributes_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribeObjectClassAttributesWithRegions(*args, **kwargs)

    def synchronization_point_achieved(self, *args: Any, **kwargs: Any) -> Any:
        return self.synchronizationPointAchieved(*args, **kwargs)

    def time_advance_request(self, *args: Any, **kwargs: Any) -> Any:
        return self.timeAdvanceRequest(*args, **kwargs)

    def time_advance_request_available(self, *args: Any, **kwargs: Any) -> Any:
        return self.timeAdvanceRequestAvailable(*args, **kwargs)

    def unassociate_regions_for_updates(self, *args: Any, **kwargs: Any) -> Any:
        return self.unassociateRegionsForUpdates(*args, **kwargs)

    def unconditional_attribute_ownership_divestiture(self, *args: Any, **kwargs: Any) -> Any:
        return self.unconditionalAttributeOwnershipDivestiture(*args, **kwargs)

    def unpublish_interaction_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.unpublishInteractionClass(*args, **kwargs)

    def unpublish_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.unpublishObjectClass(*args, **kwargs)

    def unpublish_object_class_attributes(self, *args: Any, **kwargs: Any) -> Any:
        return self.unpublishObjectClassAttributes(*args, **kwargs)

    def unsubscribe_interaction_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.unsubscribeInteractionClass(*args, **kwargs)

    def unsubscribe_interaction_class_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.unsubscribeInteractionClassWithRegions(*args, **kwargs)

    def unsubscribe_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return self.unsubscribeObjectClass(*args, **kwargs)

    def unsubscribe_object_class_attributes(self, *args: Any, **kwargs: Any) -> Any:
        return self.unsubscribeObjectClassAttributes(*args, **kwargs)

    def unsubscribe_object_class_attributes_with_regions(self, *args: Any, **kwargs: Any) -> Any:
        return self.unsubscribeObjectClassAttributesWithRegions(*args, **kwargs)

    def update_attribute_values(self, *args: Any, **kwargs: Any) -> Any:
        return self.updateAttributeValues(*args, **kwargs)


    def get_hla_version(self, *args: Any, **kwargs: Any) -> Any:
        return self.getHLAversion(*args, **kwargs)

class RTIambassador(PythonicRTIAmbassadorMixin, RawRTIambassador):
    """Subclass point for Python RTI adapters."""
    pass

RTIAmbassador = RTIambassador

class FederateAmbassador(RawFederateAmbassador):
    """Federate callback base with snake_case hooks.

    Override either the source lowerCamelCase callback or the corresponding
    snake_case hook. The lowerCamelCase default forwards to the hook.
    """

    def announceSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:
        return self.announce_synchronization_point(*args, **kwargs)

    def announce_synchronization_point(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def attributeIsNotOwned(self, *args: Any, **kwargs: Any) -> Any:
        return self.attribute_is_not_owned(*args, **kwargs)

    def attribute_is_not_owned(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def attributeIsOwnedByRTI(self, *args: Any, **kwargs: Any) -> Any:
        return self.attribute_is_owned_by_rti(*args, **kwargs)

    def attribute_is_owned_by_rti(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def attributeOwnershipAcquisitionNotification(self, *args: Any, **kwargs: Any) -> Any:
        return self.attribute_ownership_acquisition_notification(*args, **kwargs)

    def attribute_ownership_acquisition_notification(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def attributeOwnershipUnavailable(self, *args: Any, **kwargs: Any) -> Any:
        return self.attribute_ownership_unavailable(*args, **kwargs)

    def attribute_ownership_unavailable(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def attributesInScope(self, *args: Any, **kwargs: Any) -> Any:
        return self.attributes_in_scope(*args, **kwargs)

    def attributes_in_scope(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def attributesOutOfScope(self, *args: Any, **kwargs: Any) -> Any:
        return self.attributes_out_of_scope(*args, **kwargs)

    def attributes_out_of_scope(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any, **kwargs: Any) -> Any:
        return self.confirm_attribute_ownership_acquisition_cancellation(*args, **kwargs)

    def confirm_attribute_ownership_acquisition_cancellation(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def confirmAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        return self.confirm_attribute_transportation_type_change(*args, **kwargs)

    def confirm_attribute_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def confirmInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        return self.confirm_interaction_transportation_type_change(*args, **kwargs)

    def confirm_interaction_transportation_type_change(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def connectionLost(self, *args: Any, **kwargs: Any) -> Any:
        return self.connection_lost(*args, **kwargs)

    def connection_lost(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def discoverObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        return self.discover_object_instance(*args, **kwargs)

    def discover_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationNotRestored(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_not_restored(*args, **kwargs)

    def federation_not_restored(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationNotSaved(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_not_saved(*args, **kwargs)

    def federation_not_saved(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationRestoreBegun(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_restore_begun(*args, **kwargs)

    def federation_restore_begun(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationRestoreStatusResponse(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_restore_status_response(*args, **kwargs)

    def federation_restore_status_response(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationRestored(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_restored(*args, **kwargs)

    def federation_restored(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationSaveStatusResponse(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_save_status_response(*args, **kwargs)

    def federation_save_status_response(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationSaved(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_saved(*args, **kwargs)

    def federation_saved(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def federationSynchronized(self, *args: Any, **kwargs: Any) -> Any:
        return self.federation_synchronized(*args, **kwargs)

    def federation_synchronized(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def getProducingFederate(self, *args: Any, **kwargs: Any) -> Any:
        return self.get_producing_federate(*args, **kwargs)

    def get_producing_federate(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def getSentRegions(self, *args: Any, **kwargs: Any) -> Any:
        return self.get_sent_regions(*args, **kwargs)

    def get_sent_regions(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def hasProducingFederate(self, *args: Any, **kwargs: Any) -> Any:
        return self.has_producing_federate(*args, **kwargs)

    def has_producing_federate(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def hasSentRegions(self, *args: Any, **kwargs: Any) -> Any:
        return self.has_sent_regions(*args, **kwargs)

    def has_sent_regions(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def informAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:
        return self.inform_attribute_ownership(*args, **kwargs)

    def inform_attribute_ownership(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def initiateFederateRestore(self, *args: Any, **kwargs: Any) -> Any:
        return self.initiate_federate_restore(*args, **kwargs)

    def initiate_federate_restore(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def initiateFederateSave(self, *args: Any, **kwargs: Any) -> Any:
        return self.initiate_federate_save(*args, **kwargs)

    def initiate_federate_save(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def multipleObjectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:
        return self.multiple_object_instance_name_reservation_failed(*args, **kwargs)

    def multiple_object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.multiple_object_instance_name_reservation_succeeded(*args, **kwargs)

    def multiple_object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def objectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:
        return self.object_instance_name_reservation_failed(*args, **kwargs)

    def object_instance_name_reservation_failed(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def objectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.object_instance_name_reservation_succeeded(*args, **kwargs)

    def object_instance_name_reservation_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def provideAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:
        return self.provide_attribute_value_update(*args, **kwargs)

    def provide_attribute_value_update(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def receiveInteraction(self, *args: Any, **kwargs: Any) -> Any:
        return self.receive_interaction(*args, **kwargs)

    def receive_interaction(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def reflectAttributeValues(self, *args: Any, **kwargs: Any) -> Any:
        return self.reflect_attribute_values(*args, **kwargs)

    def reflect_attribute_values(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def removeObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        return self.remove_object_instance(*args, **kwargs)

    def remove_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def reportAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        return self.report_attribute_transportation_type(*args, **kwargs)

    def report_attribute_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def reportFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:
        return self.report_federation_executions(*args, **kwargs)

    def report_federation_executions(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def reportInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        return self.report_interaction_transportation_type(*args, **kwargs)

    def report_interaction_transportation_type(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def requestAttributeOwnershipAssumption(self, *args: Any, **kwargs: Any) -> Any:
        return self.request_attribute_ownership_assumption(*args, **kwargs)

    def request_attribute_ownership_assumption(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def requestAttributeOwnershipRelease(self, *args: Any, **kwargs: Any) -> Any:
        return self.request_attribute_ownership_release(*args, **kwargs)

    def request_attribute_ownership_release(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def requestDivestitureConfirmation(self, *args: Any, **kwargs: Any) -> Any:
        return self.request_divestiture_confirmation(*args, **kwargs)

    def request_divestiture_confirmation(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def requestFederationRestoreFailed(self, *args: Any, **kwargs: Any) -> Any:
        return self.request_federation_restore_failed(*args, **kwargs)

    def request_federation_restore_failed(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def requestFederationRestoreSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.request_federation_restore_succeeded(*args, **kwargs)

    def request_federation_restore_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def requestRetraction(self, *args: Any, **kwargs: Any) -> Any:
        return self.request_retraction(*args, **kwargs)

    def request_retraction(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def startRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        return self.start_registration_for_object_class(*args, **kwargs)

    def start_registration_for_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def stopRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        return self.stop_registration_for_object_class(*args, **kwargs)

    def stop_registration_for_object_class(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def synchronizationPointRegistrationFailed(self, *args: Any, **kwargs: Any) -> Any:
        return self.synchronization_point_registration_failed(*args, **kwargs)

    def synchronization_point_registration_failed(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def synchronizationPointRegistrationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        return self.synchronization_point_registration_succeeded(*args, **kwargs)

    def synchronization_point_registration_succeeded(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def timeAdvanceGrant(self, *args: Any, **kwargs: Any) -> Any:
        return self.time_advance_grant(*args, **kwargs)

    def time_advance_grant(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def timeConstrainedEnabled(self, *args: Any, **kwargs: Any) -> Any:
        return self.time_constrained_enabled(*args, **kwargs)

    def time_constrained_enabled(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def timeRegulationEnabled(self, *args: Any, **kwargs: Any) -> Any:
        return self.time_regulation_enabled(*args, **kwargs)

    def time_regulation_enabled(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def turnInteractionsOff(self, *args: Any, **kwargs: Any) -> Any:
        return self.turn_interactions_off(*args, **kwargs)

    def turn_interactions_off(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def turnInteractionsOn(self, *args: Any, **kwargs: Any) -> Any:
        return self.turn_interactions_on(*args, **kwargs)

    def turn_interactions_on(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def turnUpdatesOffForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        return self.turn_updates_off_for_object_instance(*args, **kwargs)

    def turn_updates_off_for_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def turnUpdatesOnForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        return self.turn_updates_on_for_object_instance(*args, **kwargs)

    def turn_updates_on_for_object_instance(self, *args: Any, **kwargs: Any) -> Any:
        return None

NullFederateAmbassador = FederateAmbassador
__all__ = ['RTIambassador', 'RTIAmbassador', 'FederateAmbassador', 'NullFederateAmbassador', 'PythonicRTIAmbassadorMixin']
