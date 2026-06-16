"""Runtime-facing Pythonic HLA API facade."""
from __future__ import annotations

from ._spec_impl import FederateAmbassadorSpec, RTIambassadorSpec


class PythonicRTIAmbassadorMixin(RTIambassadorSpec):
    """Mixin that forwards snake_case RTI service names to source names."""

    def create_federation_execution(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `create_federation_execution` to `createFederationExecution`."""
        return self.createFederationExecution(*args, **kwargs)

    def destroy_federation_execution(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `destroy_federation_execution` to `destroyFederationExecution`."""
        return self.destroyFederationExecution(*args, **kwargs)

    def list_federation_executions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `list_federation_executions` to `listFederationExecutions`."""
        return self.listFederationExecutions(*args, **kwargs)

    def join_federation_execution(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `join_federation_execution` to `joinFederationExecution`."""
        return self.joinFederationExecution(*args, **kwargs)

    def resign_federation_execution(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `resign_federation_execution` to `resignFederationExecution`."""
        return self.resignFederationExecution(*args, **kwargs)

    def register_federation_synchronization_point(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `register_federation_synchronization_point` to `registerFederationSynchronizationPoint`."""
        return self.registerFederationSynchronizationPoint(*args, **kwargs)

    def synchronization_point_achieved(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `synchronization_point_achieved` to `synchronizationPointAchieved`."""
        return self.synchronizationPointAchieved(*args, **kwargs)

    def request_federation_save(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `request_federation_save` to `requestFederationSave`."""
        return self.requestFederationSave(*args, **kwargs)

    def federate_save_begun(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `federate_save_begun` to `federateSaveBegun`."""
        return self.federateSaveBegun(*args, **kwargs)

    def federate_save_complete(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `federate_save_complete` to `federateSaveComplete`."""
        return self.federateSaveComplete(*args, **kwargs)

    def federate_save_not_complete(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `federate_save_not_complete` to `federateSaveNotComplete`."""
        return self.federateSaveNotComplete(*args, **kwargs)

    def abort_federation_save(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `abort_federation_save` to `abortFederationSave`."""
        return self.abortFederationSave(*args, **kwargs)

    def query_federation_save_status(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_federation_save_status` to `queryFederationSaveStatus`."""
        return self.queryFederationSaveStatus(*args, **kwargs)

    def request_federation_restore(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `request_federation_restore` to `requestFederationRestore`."""
        return self.requestFederationRestore(*args, **kwargs)

    def federate_restore_complete(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `federate_restore_complete` to `federateRestoreComplete`."""
        return self.federateRestoreComplete(*args, **kwargs)

    def federate_restore_not_complete(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `federate_restore_not_complete` to `federateRestoreNotComplete`."""
        return self.federateRestoreNotComplete(*args, **kwargs)

    def abort_federation_restore(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `abort_federation_restore` to `abortFederationRestore`."""
        return self.abortFederationRestore(*args, **kwargs)

    def query_federation_restore_status(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_federation_restore_status` to `queryFederationRestoreStatus`."""
        return self.queryFederationRestoreStatus(*args, **kwargs)

    def publish_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `publish_object_class_attributes` to `publishObjectClassAttributes`."""
        return self.publishObjectClassAttributes(*args, **kwargs)

    def unpublish_object_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unpublish_object_class` to `unpublishObjectClass`."""
        return self.unpublishObjectClass(*args, **kwargs)

    def unpublish_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unpublish_object_class_attributes` to `unpublishObjectClassAttributes`."""
        return self.unpublishObjectClassAttributes(*args, **kwargs)

    def publish_interaction_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `publish_interaction_class` to `publishInteractionClass`."""
        return self.publishInteractionClass(*args, **kwargs)

    def unpublish_interaction_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unpublish_interaction_class` to `unpublishInteractionClass`."""
        return self.unpublishInteractionClass(*args, **kwargs)

    def subscribe_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_object_class_attributes` to `subscribeObjectClassAttributes`."""
        return self.subscribeObjectClassAttributes(*args, **kwargs)

    def subscribe_object_class_attributes_passively(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_object_class_attributes_passively` to `subscribeObjectClassAttributesPassively`."""
        return self.subscribeObjectClassAttributesPassively(*args, **kwargs)

    def unsubscribe_object_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unsubscribe_object_class` to `unsubscribeObjectClass`."""
        return self.unsubscribeObjectClass(*args, **kwargs)

    def unsubscribe_object_class_attributes(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unsubscribe_object_class_attributes` to `unsubscribeObjectClassAttributes`."""
        return self.unsubscribeObjectClassAttributes(*args, **kwargs)

    def subscribe_interaction_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_interaction_class` to `subscribeInteractionClass`."""
        return self.subscribeInteractionClass(*args, **kwargs)

    def subscribe_interaction_class_passively(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_interaction_class_passively` to `subscribeInteractionClassPassively`."""
        return self.subscribeInteractionClassPassively(*args, **kwargs)

    def unsubscribe_interaction_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unsubscribe_interaction_class` to `unsubscribeInteractionClass`."""
        return self.unsubscribeInteractionClass(*args, **kwargs)

    def reserve_object_instance_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `reserve_object_instance_name` to `reserveObjectInstanceName`."""
        return self.reserveObjectInstanceName(*args, **kwargs)

    def release_object_instance_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `release_object_instance_name` to `releaseObjectInstanceName`."""
        return self.releaseObjectInstanceName(*args, **kwargs)

    def reserve_multiple_object_instance_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `reserve_multiple_object_instance_name` to `reserveMultipleObjectInstanceName`."""
        return self.reserveMultipleObjectInstanceName(*args, **kwargs)

    def release_multiple_object_instance_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `release_multiple_object_instance_name` to `releaseMultipleObjectInstanceName`."""
        return self.releaseMultipleObjectInstanceName(*args, **kwargs)

    def register_object_instance(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `register_object_instance` to `registerObjectInstance`."""
        return self.registerObjectInstance(*args, **kwargs)

    def update_attribute_values(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `update_attribute_values` to `updateAttributeValues`."""
        return self.updateAttributeValues(*args, **kwargs)

    def send_interaction(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `send_interaction` to `sendInteraction`."""
        return self.sendInteraction(*args, **kwargs)

    def delete_object_instance(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `delete_object_instance` to `deleteObjectInstance`."""
        return self.deleteObjectInstance(*args, **kwargs)

    def local_delete_object_instance(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `local_delete_object_instance` to `localDeleteObjectInstance`."""
        return self.localDeleteObjectInstance(*args, **kwargs)

    def request_attribute_value_update(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `request_attribute_value_update` to `requestAttributeValueUpdate`."""
        return self.requestAttributeValueUpdate(*args, **kwargs)

    def request_attribute_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `request_attribute_transportation_type_change` to `requestAttributeTransportationTypeChange`."""
        return self.requestAttributeTransportationTypeChange(*args, **kwargs)

    def query_attribute_transportation_type(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_attribute_transportation_type` to `queryAttributeTransportationType`."""
        return self.queryAttributeTransportationType(*args, **kwargs)

    def request_interaction_transportation_type_change(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `request_interaction_transportation_type_change` to `requestInteractionTransportationTypeChange`."""
        return self.requestInteractionTransportationTypeChange(*args, **kwargs)

    def query_interaction_transportation_type(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_interaction_transportation_type` to `queryInteractionTransportationType`."""
        return self.queryInteractionTransportationType(*args, **kwargs)

    def unconditional_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unconditional_attribute_ownership_divestiture` to `unconditionalAttributeOwnershipDivestiture`."""
        return self.unconditionalAttributeOwnershipDivestiture(*args, **kwargs)

    def negotiated_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `negotiated_attribute_ownership_divestiture` to `negotiatedAttributeOwnershipDivestiture`."""
        return self.negotiatedAttributeOwnershipDivestiture(*args, **kwargs)

    def confirm_divestiture(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `confirm_divestiture` to `confirmDivestiture`."""
        return self.confirmDivestiture(*args, **kwargs)

    def attribute_ownership_acquisition(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `attribute_ownership_acquisition` to `attributeOwnershipAcquisition`."""
        return self.attributeOwnershipAcquisition(*args, **kwargs)

    def attribute_ownership_acquisition_if_available(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `attribute_ownership_acquisition_if_available` to `attributeOwnershipAcquisitionIfAvailable`."""
        return self.attributeOwnershipAcquisitionIfAvailable(*args, **kwargs)

    def attribute_ownership_release_denied(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `attribute_ownership_release_denied` to `attributeOwnershipReleaseDenied`."""
        return self.attributeOwnershipReleaseDenied(*args, **kwargs)

    def attribute_ownership_divestiture_if_wanted(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `attribute_ownership_divestiture_if_wanted` to `attributeOwnershipDivestitureIfWanted`."""
        return self.attributeOwnershipDivestitureIfWanted(*args, **kwargs)

    def cancel_negotiated_attribute_ownership_divestiture(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `cancel_negotiated_attribute_ownership_divestiture` to `cancelNegotiatedAttributeOwnershipDivestiture`."""
        return self.cancelNegotiatedAttributeOwnershipDivestiture(*args, **kwargs)

    def cancel_attribute_ownership_acquisition(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `cancel_attribute_ownership_acquisition` to `cancelAttributeOwnershipAcquisition`."""
        return self.cancelAttributeOwnershipAcquisition(*args, **kwargs)

    def query_attribute_ownership(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_attribute_ownership` to `queryAttributeOwnership`."""
        return self.queryAttributeOwnership(*args, **kwargs)

    def is_attribute_owned_by_federate(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `is_attribute_owned_by_federate` to `isAttributeOwnedByFederate`."""
        return self.isAttributeOwnedByFederate(*args, **kwargs)

    def enable_time_regulation(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_time_regulation` to `enableTimeRegulation`."""
        return self.enableTimeRegulation(*args, **kwargs)

    def disable_time_regulation(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_time_regulation` to `disableTimeRegulation`."""
        return self.disableTimeRegulation(*args, **kwargs)

    def enable_time_constrained(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_time_constrained` to `enableTimeConstrained`."""
        return self.enableTimeConstrained(*args, **kwargs)

    def disable_time_constrained(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_time_constrained` to `disableTimeConstrained`."""
        return self.disableTimeConstrained(*args, **kwargs)

    def time_advance_request(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `time_advance_request` to `timeAdvanceRequest`."""
        return self.timeAdvanceRequest(*args, **kwargs)

    def time_advance_request_available(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `time_advance_request_available` to `timeAdvanceRequestAvailable`."""
        return self.timeAdvanceRequestAvailable(*args, **kwargs)

    def next_message_request(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `next_message_request` to `nextMessageRequest`."""
        return self.nextMessageRequest(*args, **kwargs)

    def next_message_request_available(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `next_message_request_available` to `nextMessageRequestAvailable`."""
        return self.nextMessageRequestAvailable(*args, **kwargs)

    def flush_queue_request(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `flush_queue_request` to `flushQueueRequest`."""
        return self.flushQueueRequest(*args, **kwargs)

    def enable_asynchronous_delivery(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_asynchronous_delivery` to `enableAsynchronousDelivery`."""
        return self.enableAsynchronousDelivery(*args, **kwargs)

    def disable_asynchronous_delivery(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_asynchronous_delivery` to `disableAsynchronousDelivery`."""
        return self.disableAsynchronousDelivery(*args, **kwargs)

    def query_galt(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_galt` to `queryGALT`."""
        return self.queryGALT(*args, **kwargs)

    def query_logical_time(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_logical_time` to `queryLogicalTime`."""
        return self.queryLogicalTime(*args, **kwargs)

    def query_lits(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_lits` to `queryLITS`."""
        return self.queryLITS(*args, **kwargs)

    def modify_lookahead(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `modify_lookahead` to `modifyLookahead`."""
        return self.modifyLookahead(*args, **kwargs)

    def query_lookahead(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `query_lookahead` to `queryLookahead`."""
        return self.queryLookahead(*args, **kwargs)

    def change_attribute_order_type(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `change_attribute_order_type` to `changeAttributeOrderType`."""
        return self.changeAttributeOrderType(*args, **kwargs)

    def change_interaction_order_type(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `change_interaction_order_type` to `changeInteractionOrderType`."""
        return self.changeInteractionOrderType(*args, **kwargs)

    def create_region(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `create_region` to `createRegion`."""
        return self.createRegion(*args, **kwargs)

    def commit_region_modifications(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `commit_region_modifications` to `commitRegionModifications`."""
        return self.commitRegionModifications(*args, **kwargs)

    def delete_region(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `delete_region` to `deleteRegion`."""
        return self.deleteRegion(*args, **kwargs)

    def register_object_instance_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `register_object_instance_with_regions` to `registerObjectInstanceWithRegions`."""
        return self.registerObjectInstanceWithRegions(*args, **kwargs)

    def associate_regions_for_updates(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `associate_regions_for_updates` to `associateRegionsForUpdates`."""
        return self.associateRegionsForUpdates(*args, **kwargs)

    def unassociate_regions_for_updates(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unassociate_regions_for_updates` to `unassociateRegionsForUpdates`."""
        return self.unassociateRegionsForUpdates(*args, **kwargs)

    def subscribe_object_class_attributes_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_object_class_attributes_with_regions` to `subscribeObjectClassAttributesWithRegions`."""
        return self.subscribeObjectClassAttributesWithRegions(*args, **kwargs)

    def subscribe_object_class_attributes_passively_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_object_class_attributes_passively_with_regions` to `subscribeObjectClassAttributesPassivelyWithRegions`."""
        return self.subscribeObjectClassAttributesPassivelyWithRegions(*args, **kwargs)

    def unsubscribe_object_class_attributes_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unsubscribe_object_class_attributes_with_regions` to `unsubscribeObjectClassAttributesWithRegions`."""
        return self.unsubscribeObjectClassAttributesWithRegions(*args, **kwargs)

    def subscribe_interaction_class_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_interaction_class_with_regions` to `subscribeInteractionClassWithRegions`."""
        return self.subscribeInteractionClassWithRegions(*args, **kwargs)

    def subscribe_interaction_class_passively_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `subscribe_interaction_class_passively_with_regions` to `subscribeInteractionClassPassivelyWithRegions`."""
        return self.subscribeInteractionClassPassivelyWithRegions(*args, **kwargs)

    def unsubscribe_interaction_class_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `unsubscribe_interaction_class_with_regions` to `unsubscribeInteractionClassWithRegions`."""
        return self.unsubscribeInteractionClassWithRegions(*args, **kwargs)

    def send_interaction_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `send_interaction_with_regions` to `sendInteractionWithRegions`."""
        return self.sendInteractionWithRegions(*args, **kwargs)

    def request_attribute_value_update_with_regions(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `request_attribute_value_update_with_regions` to `requestAttributeValueUpdateWithRegions`."""
        return self.requestAttributeValueUpdateWithRegions(*args, **kwargs)

    def get_automatic_resign_directive(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_automatic_resign_directive` to `getAutomaticResignDirective`."""
        return self.getAutomaticResignDirective(*args, **kwargs)

    def set_automatic_resign_directive(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `set_automatic_resign_directive` to `setAutomaticResignDirective`."""
        return self.setAutomaticResignDirective(*args, **kwargs)

    def get_federate_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_federate_handle` to `getFederateHandle`."""
        return self.getFederateHandle(*args, **kwargs)

    def get_federate_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_federate_name` to `getFederateName`."""
        return self.getFederateName(*args, **kwargs)

    def get_object_class_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_object_class_handle` to `getObjectClassHandle`."""
        return self.getObjectClassHandle(*args, **kwargs)

    def get_object_class_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_object_class_name` to `getObjectClassName`."""
        return self.getObjectClassName(*args, **kwargs)

    def get_known_object_class_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_known_object_class_handle` to `getKnownObjectClassHandle`."""
        return self.getKnownObjectClassHandle(*args, **kwargs)

    def get_object_instance_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_object_instance_handle` to `getObjectInstanceHandle`."""
        return self.getObjectInstanceHandle(*args, **kwargs)

    def get_object_instance_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_object_instance_name` to `getObjectInstanceName`."""
        return self.getObjectInstanceName(*args, **kwargs)

    def get_attribute_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_attribute_handle` to `getAttributeHandle`."""
        return self.getAttributeHandle(*args, **kwargs)

    def get_attribute_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_attribute_name` to `getAttributeName`."""
        return self.getAttributeName(*args, **kwargs)

    def get_update_rate_value(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_update_rate_value` to `getUpdateRateValue`."""
        return self.getUpdateRateValue(*args, **kwargs)

    def get_update_rate_value_for_attribute(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_update_rate_value_for_attribute` to `getUpdateRateValueForAttribute`."""
        return self.getUpdateRateValueForAttribute(*args, **kwargs)

    def get_interaction_class_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_interaction_class_handle` to `getInteractionClassHandle`."""
        return self.getInteractionClassHandle(*args, **kwargs)

    def get_interaction_class_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_interaction_class_name` to `getInteractionClassName`."""
        return self.getInteractionClassName(*args, **kwargs)

    def get_parameter_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_parameter_handle` to `getParameterHandle`."""
        return self.getParameterHandle(*args, **kwargs)

    def get_parameter_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_parameter_name` to `getParameterName`."""
        return self.getParameterName(*args, **kwargs)

    def get_order_type(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_order_type` to `getOrderType`."""
        return self.getOrderType(*args, **kwargs)

    def get_order_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_order_name` to `getOrderName`."""
        return self.getOrderName(*args, **kwargs)

    def get_transportation_type_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_transportation_type_handle` to `getTransportationTypeHandle`."""
        return self.getTransportationTypeHandle(*args, **kwargs)

    def get_transportation_type_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_transportation_type_name` to `getTransportationTypeName`."""
        return self.getTransportationTypeName(*args, **kwargs)

    def get_available_dimensions_for_class_attribute(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_available_dimensions_for_class_attribute` to `getAvailableDimensionsForClassAttribute`."""
        return self.getAvailableDimensionsForClassAttribute(*args, **kwargs)

    def get_available_dimensions_for_interaction_class(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_available_dimensions_for_interaction_class` to `getAvailableDimensionsForInteractionClass`."""
        return self.getAvailableDimensionsForInteractionClass(*args, **kwargs)

    def get_dimension_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_dimension_handle` to `getDimensionHandle`."""
        return self.getDimensionHandle(*args, **kwargs)

    def get_dimension_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_dimension_name` to `getDimensionName`."""
        return self.getDimensionName(*args, **kwargs)

    def get_dimension_upper_bound(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_dimension_upper_bound` to `getDimensionUpperBound`."""
        return self.getDimensionUpperBound(*args, **kwargs)

    def get_dimension_handle_set(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_dimension_handle_set` to `getDimensionHandleSet`."""
        return self.getDimensionHandleSet(*args, **kwargs)

    def get_range_bounds(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_range_bounds` to `getRangeBounds`."""
        return self.getRangeBounds(*args, **kwargs)

    def set_range_bounds(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `set_range_bounds` to `setRangeBounds`."""
        return self.setRangeBounds(*args, **kwargs)

    def normalize_federate_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `normalize_federate_handle` to `normalizeFederateHandle`."""
        return self.normalizeFederateHandle(*args, **kwargs)

    def normalize_service_group(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `normalize_service_group` to `normalizeServiceGroup`."""
        return self.normalizeServiceGroup(*args, **kwargs)

    def enable_object_class_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_object_class_relevance_advisory_switch` to `enableObjectClassRelevanceAdvisorySwitch`."""
        return self.enableObjectClassRelevanceAdvisorySwitch(*args, **kwargs)

    def disable_object_class_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_object_class_relevance_advisory_switch` to `disableObjectClassRelevanceAdvisorySwitch`."""
        return self.disableObjectClassRelevanceAdvisorySwitch(*args, **kwargs)

    def enable_attribute_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_attribute_relevance_advisory_switch` to `enableAttributeRelevanceAdvisorySwitch`."""
        return self.enableAttributeRelevanceAdvisorySwitch(*args, **kwargs)

    def disable_attribute_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_attribute_relevance_advisory_switch` to `disableAttributeRelevanceAdvisorySwitch`."""
        return self.disableAttributeRelevanceAdvisorySwitch(*args, **kwargs)

    def enable_attribute_scope_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_attribute_scope_advisory_switch` to `enableAttributeScopeAdvisorySwitch`."""
        return self.enableAttributeScopeAdvisorySwitch(*args, **kwargs)

    def disable_attribute_scope_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_attribute_scope_advisory_switch` to `disableAttributeScopeAdvisorySwitch`."""
        return self.disableAttributeScopeAdvisorySwitch(*args, **kwargs)

    def enable_interaction_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_interaction_relevance_advisory_switch` to `enableInteractionRelevanceAdvisorySwitch`."""
        return self.enableInteractionRelevanceAdvisorySwitch(*args, **kwargs)

    def disable_interaction_relevance_advisory_switch(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_interaction_relevance_advisory_switch` to `disableInteractionRelevanceAdvisorySwitch`."""
        return self.disableInteractionRelevanceAdvisorySwitch(*args, **kwargs)

    def evoke_callback(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `evoke_callback` to `evokeCallback`."""
        return self.evokeCallback(*args, **kwargs)

    def evoke_multiple_callbacks(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `evoke_multiple_callbacks` to `evokeMultipleCallbacks`."""
        return self.evokeMultipleCallbacks(*args, **kwargs)

    def enable_callbacks(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `enable_callbacks` to `enableCallbacks`."""
        return self.enableCallbacks(*args, **kwargs)

    def disable_callbacks(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `disable_callbacks` to `disableCallbacks`."""
        return self.disableCallbacks(*args, **kwargs)

    def get_attribute_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_attribute_handle_factory` to `getAttributeHandleFactory`."""
        return self.getAttributeHandleFactory(*args, **kwargs)

    def get_attribute_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_attribute_handle_set_factory` to `getAttributeHandleSetFactory`."""
        return self.getAttributeHandleSetFactory(*args, **kwargs)

    def get_attribute_handle_value_map_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_attribute_handle_value_map_factory` to `getAttributeHandleValueMapFactory`."""
        return self.getAttributeHandleValueMapFactory(*args, **kwargs)

    def get_attribute_set_region_set_pair_list_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_attribute_set_region_set_pair_list_factory` to `getAttributeSetRegionSetPairListFactory`."""
        return self.getAttributeSetRegionSetPairListFactory(*args, **kwargs)

    def get_dimension_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_dimension_handle_factory` to `getDimensionHandleFactory`."""
        return self.getDimensionHandleFactory(*args, **kwargs)

    def get_dimension_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_dimension_handle_set_factory` to `getDimensionHandleSetFactory`."""
        return self.getDimensionHandleSetFactory(*args, **kwargs)

    def get_federate_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_federate_handle_factory` to `getFederateHandleFactory`."""
        return self.getFederateHandleFactory(*args, **kwargs)

    def get_federate_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_federate_handle_set_factory` to `getFederateHandleSetFactory`."""
        return self.getFederateHandleSetFactory(*args, **kwargs)

    def get_interaction_class_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_interaction_class_handle_factory` to `getInteractionClassHandleFactory`."""
        return self.getInteractionClassHandleFactory(*args, **kwargs)

    def get_object_class_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_object_class_handle_factory` to `getObjectClassHandleFactory`."""
        return self.getObjectClassHandleFactory(*args, **kwargs)

    def get_object_instance_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_object_instance_handle_factory` to `getObjectInstanceHandleFactory`."""
        return self.getObjectInstanceHandleFactory(*args, **kwargs)

    def get_parameter_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_parameter_handle_factory` to `getParameterHandleFactory`."""
        return self.getParameterHandleFactory(*args, **kwargs)

    def get_parameter_handle_value_map_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_parameter_handle_value_map_factory` to `getParameterHandleValueMapFactory`."""
        return self.getParameterHandleValueMapFactory(*args, **kwargs)

    def get_region_handle_set_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_region_handle_set_factory` to `getRegionHandleSetFactory`."""
        return self.getRegionHandleSetFactory(*args, **kwargs)

    def get_transportation_type_handle_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_transportation_type_handle_factory` to `getTransportationTypeHandleFactory`."""
        return self.getTransportationTypeHandleFactory(*args, **kwargs)

    def get_hla_version(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_hla_version` to `getHLAversion`."""
        return self.getHLAversion(*args, **kwargs)

    def get_time_factory(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_time_factory` to `getTimeFactory`."""
        return self.getTimeFactory(*args, **kwargs)

    def create_federation_execution_with_mim(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `create_federation_execution_with_mim` to `createFederationExecutionWithMIM`."""
        return self.createFederationExecutionWithMIM(*args, **kwargs)

    def get_transportation_type(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_transportation_type` to `getTransportationType`."""
        return self.getTransportationType(*args, **kwargs)

    def get_transportation_name(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `get_transportation_name` to `getTransportationName`."""
        return self.getTransportationName(*args, **kwargs)

    def decode_federate_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_federate_handle` to `decodeFederateHandle`."""
        return self.decodeFederateHandle(*args, **kwargs)

    def decode_object_class_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_object_class_handle` to `decodeObjectClassHandle`."""
        return self.decodeObjectClassHandle(*args, **kwargs)

    def decode_interaction_class_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_interaction_class_handle` to `decodeInteractionClassHandle`."""
        return self.decodeInteractionClassHandle(*args, **kwargs)

    def decode_object_instance_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_object_instance_handle` to `decodeObjectInstanceHandle`."""
        return self.decodeObjectInstanceHandle(*args, **kwargs)

    def decode_attribute_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_attribute_handle` to `decodeAttributeHandle`."""
        return self.decodeAttributeHandle(*args, **kwargs)

    def decode_parameter_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_parameter_handle` to `decodeParameterHandle`."""
        return self.decodeParameterHandle(*args, **kwargs)

    def decode_dimension_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_dimension_handle` to `decodeDimensionHandle`."""
        return self.decodeDimensionHandle(*args, **kwargs)

    def decode_message_retraction_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_message_retraction_handle` to `decodeMessageRetractionHandle`."""
        return self.decodeMessageRetractionHandle(*args, **kwargs)

    def decode_region_handle(self, *args: object, **kwargs: object) -> object:
        """Forward the Pythonic alias `decode_region_handle` to `decodeRegionHandle`."""
        return self.decodeRegionHandle(*args, **kwargs)


class RTIambassador(PythonicRTIAmbassadorMixin):
    """Concrete subclass point for Python RTI adapters."""


RTIAmbassador = RTIambassador


class FederateAmbassador(FederateAmbassadorSpec):
    """Prototype base for federate callback implementations."""


NullFederateAmbassador = FederateAmbassador

__all__ = [
    "FederateAmbassador",
    "NullFederateAmbassador",
    "PythonicRTIAmbassadorMixin",
    "RTIAmbassador",
    "RTIambassador",
]
