# HLA Interface Contracts

Generated from `specs/hla2010_api.json`.

Java lowerCamelCase method names are preserved as canonical HLA service and callback names. Python aliases mirror those names in snake_case.

## RTIambassador

| Java name | Python alias | Signature | Returns |
| --- | --- | --- | --- |
| `abortFederationRestore` | `abort_federation_restore` | `abort_federation_restore()` | `None` |
| `abortFederationSave` | `abort_federation_save` | `abort_federation_save()` | `None` |
| `associateRegionsForUpdates` | `associate_regions_for_updates` | `associate_regions_for_updates(the_object: ObjectInstanceHandle, attributes_and_regions: AttributeSetRegionSetPairList)` | `None` |
| `attributeOwnershipAcquisition` | `attribute_ownership_acquisition` | `attribute_ownership_acquisition(the_object: ObjectInstanceHandle, desired_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `attributeOwnershipAcquisitionIfAvailable` | `attribute_ownership_acquisition_if_available` | `attribute_ownership_acquisition_if_available(the_object: ObjectInstanceHandle, desired_attributes: AttributeHandleSet)` | `None` |
| `attributeOwnershipDivestitureIfWanted` | `attribute_ownership_divestiture_if_wanted` | `attribute_ownership_divestiture_if_wanted(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `AttributeHandleSet` |
| `attributeOwnershipReleaseDenied` | `attribute_ownership_release_denied` | `attribute_ownership_release_denied(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `cancelAttributeOwnershipAcquisition` | `cancel_attribute_ownership_acquisition` | `cancel_attribute_ownership_acquisition(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `cancelNegotiatedAttributeOwnershipDivestiture` | `cancel_negotiated_attribute_ownership_divestiture` | `cancel_negotiated_attribute_ownership_divestiture(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `changeAttributeOrderType` | `change_attribute_order_type` | `change_attribute_order_type(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, the_type: OrderType)` | `None` |
| `changeInteractionOrderType` | `change_interaction_order_type` | `change_interaction_order_type(the_class: InteractionClassHandle, the_type: OrderType)` | `None` |
| `commitRegionModifications` | `commit_region_modifications` | `commit_region_modifications(regions: RegionHandleSet)` | `None` |
| `confirmDivestiture` | `confirm_divestiture` | `confirm_divestiture(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `connect` | `connect` | `connect(federate_reference: FederateAmbassadorSpec, callback_model: CallbackModel, local_settings_designator: str | None = None)` | `None` |
| `createFederationExecution` | `create_federation_execution` | `create_federation_execution(federation_execution_name: str, fom_modules: FomModuleLike, *, mim_module: URLLike | None = None, logical_time_implementation_name: str | None = None)` | `None` |
| `createFederationExecutionWithMIM` | `create_federation_execution_with_mim` | `create_federation_execution_with_mim(federation_execution_name: str, fom_modules: Sequence[URLLike], mim_module: str, logical_time_implementation_name: str | None = None)` | `None` |
| `createRegion` | `create_region` | `create_region(dimensions: DimensionHandleSet)` | `RegionHandle` |
| `decodeAttributeHandle` | `decode_attribute_handle` | `decode_attribute_handle(encoded_value: VariableLengthDataLike)` | `AttributeHandle` |
| `decodeDimensionHandle` | `decode_dimension_handle` | `decode_dimension_handle(encoded_value: VariableLengthDataLike)` | `DimensionHandle` |
| `decodeFederateHandle` | `decode_federate_handle` | `decode_federate_handle(encoded_value: VariableLengthDataLike)` | `FederateHandle` |
| `decodeInteractionClassHandle` | `decode_interaction_class_handle` | `decode_interaction_class_handle(encoded_value: VariableLengthDataLike)` | `InteractionClassHandle` |
| `decodeMessageRetractionHandle` | `decode_message_retraction_handle` | `decode_message_retraction_handle(encoded_value: VariableLengthDataLike)` | `MessageRetractionHandle` |
| `decodeObjectClassHandle` | `decode_object_class_handle` | `decode_object_class_handle(encoded_value: VariableLengthDataLike)` | `ObjectClassHandle` |
| `decodeObjectInstanceHandle` | `decode_object_instance_handle` | `decode_object_instance_handle(encoded_value: VariableLengthDataLike)` | `ObjectInstanceHandle` |
| `decodeParameterHandle` | `decode_parameter_handle` | `decode_parameter_handle(encoded_value: VariableLengthDataLike)` | `ParameterHandle` |
| `decodeRegionHandle` | `decode_region_handle` | `decode_region_handle(encoded_value: VariableLengthDataLike)` | `RegionHandle` |
| `deleteObjectInstance` | `delete_object_instance` | `delete_object_instance(object_handle: ObjectInstanceHandle, user_supplied_tag: VariableLengthDataLike, the_time: LogicalTimeLike | None = None)` | `None` |
| `deleteRegion` | `delete_region` | `delete_region(the_region: RegionHandle)` | `None` |
| `destroyFederationExecution` | `destroy_federation_execution` | `destroy_federation_execution(federation_execution_name: str)` | `None` |
| `disableAsynchronousDelivery` | `disable_asynchronous_delivery` | `disable_asynchronous_delivery()` | `None` |
| `disableAttributeRelevanceAdvisorySwitch` | `disable_attribute_relevance_advisory_switch` | `disable_attribute_relevance_advisory_switch()` | `None` |
| `disableAttributeScopeAdvisorySwitch` | `disable_attribute_scope_advisory_switch` | `disable_attribute_scope_advisory_switch()` | `None` |
| `disableCallbacks` | `disable_callbacks` | `disable_callbacks()` | `None` |
| `disableInteractionRelevanceAdvisorySwitch` | `disable_interaction_relevance_advisory_switch` | `disable_interaction_relevance_advisory_switch()` | `None` |
| `disableObjectClassRelevanceAdvisorySwitch` | `disable_object_class_relevance_advisory_switch` | `disable_object_class_relevance_advisory_switch()` | `None` |
| `disableTimeConstrained` | `disable_time_constrained` | `disable_time_constrained()` | `None` |
| `disableTimeRegulation` | `disable_time_regulation` | `disable_time_regulation()` | `None` |
| `disconnect` | `disconnect` | `disconnect()` | `None` |
| `enableAsynchronousDelivery` | `enable_asynchronous_delivery` | `enable_asynchronous_delivery()` | `None` |
| `enableAttributeRelevanceAdvisorySwitch` | `enable_attribute_relevance_advisory_switch` | `enable_attribute_relevance_advisory_switch()` | `None` |
| `enableAttributeScopeAdvisorySwitch` | `enable_attribute_scope_advisory_switch` | `enable_attribute_scope_advisory_switch()` | `None` |
| `enableCallbacks` | `enable_callbacks` | `enable_callbacks()` | `None` |
| `enableInteractionRelevanceAdvisorySwitch` | `enable_interaction_relevance_advisory_switch` | `enable_interaction_relevance_advisory_switch()` | `None` |
| `enableObjectClassRelevanceAdvisorySwitch` | `enable_object_class_relevance_advisory_switch` | `enable_object_class_relevance_advisory_switch()` | `None` |
| `enableTimeConstrained` | `enable_time_constrained` | `enable_time_constrained()` | `None` |
| `enableTimeRegulation` | `enable_time_regulation` | `enable_time_regulation(the_lookahead: LogicalTimeIntervalLike)` | `None` |
| `evokeCallback` | `evoke_callback` | `evoke_callback(approximate_minimum_time_in_seconds: float)` | `bool` |
| `evokeMultipleCallbacks` | `evoke_multiple_callbacks` | `evoke_multiple_callbacks(approximate_minimum_time_in_seconds: float, approximate_maximum_time_in_seconds: float)` | `bool` |
| `federateRestoreComplete` | `federate_restore_complete` | `federate_restore_complete()` | `None` |
| `federateRestoreNotComplete` | `federate_restore_not_complete` | `federate_restore_not_complete()` | `None` |
| `federateSaveBegun` | `federate_save_begun` | `federate_save_begun()` | `None` |
| `federateSaveComplete` | `federate_save_complete` | `federate_save_complete()` | `None` |
| `federateSaveNotComplete` | `federate_save_not_complete` | `federate_save_not_complete()` | `None` |
| `flushQueueRequest` | `flush_queue_request` | `flush_queue_request(the_time: LogicalTimeLike)` | `None` |
| `getAttributeHandle` | `get_attribute_handle` | `get_attribute_handle(which_class: ObjectClassHandle, the_name: str)` | `AttributeHandle` |
| `getAttributeHandleFactory` | `get_attribute_handle_factory` | `get_attribute_handle_factory()` | `AttributeHandleFactory` |
| `getAttributeHandleSetFactory` | `get_attribute_handle_set_factory` | `get_attribute_handle_set_factory()` | `AttributeHandleSetFactory` |
| `getAttributeHandleValueMapFactory` | `get_attribute_handle_value_map_factory` | `get_attribute_handle_value_map_factory()` | `AttributeHandleValueMapFactory` |
| `getAttributeName` | `get_attribute_name` | `get_attribute_name(which_class: ObjectClassHandle, the_handle: AttributeHandle)` | `str` |
| `getAttributeSetRegionSetPairListFactory` | `get_attribute_set_region_set_pair_list_factory` | `get_attribute_set_region_set_pair_list_factory()` | `AttributeSetRegionSetPairListFactory` |
| `getAutomaticResignDirective` | `get_automatic_resign_directive` | `get_automatic_resign_directive()` | `ResignAction` |
| `getAvailableDimensionsForClassAttribute` | `get_available_dimensions_for_class_attribute` | `get_available_dimensions_for_class_attribute(which_class: ObjectClassHandle, the_handle: AttributeHandle)` | `DimensionHandleSet` |
| `getAvailableDimensionsForInteractionClass` | `get_available_dimensions_for_interaction_class` | `get_available_dimensions_for_interaction_class(the_handle: InteractionClassHandle)` | `DimensionHandleSet` |
| `getDimensionHandle` | `get_dimension_handle` | `get_dimension_handle(the_name: str)` | `DimensionHandle` |
| `getDimensionHandleFactory` | `get_dimension_handle_factory` | `get_dimension_handle_factory()` | `DimensionHandleFactory` |
| `getDimensionHandleSet` | `get_dimension_handle_set` | `get_dimension_handle_set(region: RegionHandle)` | `DimensionHandleSet` |
| `getDimensionHandleSetFactory` | `get_dimension_handle_set_factory` | `get_dimension_handle_set_factory()` | `DimensionHandleSetFactory` |
| `getDimensionName` | `get_dimension_name` | `get_dimension_name(the_handle: DimensionHandle)` | `str` |
| `getDimensionUpperBound` | `get_dimension_upper_bound` | `get_dimension_upper_bound(the_handle: DimensionHandle)` | `int` |
| `getFederateHandle` | `get_federate_handle` | `get_federate_handle(the_name: str)` | `FederateHandle` |
| `getFederateHandleFactory` | `get_federate_handle_factory` | `get_federate_handle_factory()` | `FederateHandleFactory` |
| `getFederateHandleSetFactory` | `get_federate_handle_set_factory` | `get_federate_handle_set_factory()` | `FederateHandleSetFactory` |
| `getFederateName` | `get_federate_name` | `get_federate_name(the_handle: FederateHandle)` | `str` |
| `getHLAversion` | `get_hla_version` | `get_hla_version()` | `str` |
| `getInteractionClassHandle` | `get_interaction_class_handle` | `get_interaction_class_handle(the_name: str)` | `InteractionClassHandle` |
| `getInteractionClassHandleFactory` | `get_interaction_class_handle_factory` | `get_interaction_class_handle_factory()` | `InteractionClassHandleFactory` |
| `getInteractionClassName` | `get_interaction_class_name` | `get_interaction_class_name(the_handle: InteractionClassHandle)` | `str` |
| `getKnownObjectClassHandle` | `get_known_object_class_handle` | `get_known_object_class_handle(the_object: ObjectInstanceHandle)` | `ObjectClassHandle` |
| `getObjectClassHandle` | `get_object_class_handle` | `get_object_class_handle(the_name: str)` | `ObjectClassHandle` |
| `getObjectClassHandleFactory` | `get_object_class_handle_factory` | `get_object_class_handle_factory()` | `ObjectClassHandleFactory` |
| `getObjectClassName` | `get_object_class_name` | `get_object_class_name(the_handle: ObjectClassHandle)` | `str` |
| `getObjectInstanceHandle` | `get_object_instance_handle` | `get_object_instance_handle(the_name: str)` | `ObjectInstanceHandle` |
| `getObjectInstanceHandleFactory` | `get_object_instance_handle_factory` | `get_object_instance_handle_factory()` | `ObjectInstanceHandleFactory` |
| `getObjectInstanceName` | `get_object_instance_name` | `get_object_instance_name(the_handle: ObjectInstanceHandle)` | `str` |
| `getOrderName` | `get_order_name` | `get_order_name(the_type: OrderType)` | `str` |
| `getOrderType` | `get_order_type` | `get_order_type(the_name: str)` | `OrderType` |
| `getParameterHandle` | `get_parameter_handle` | `get_parameter_handle(which_class: InteractionClassHandle, the_name: str)` | `ParameterHandle` |
| `getParameterHandleFactory` | `get_parameter_handle_factory` | `get_parameter_handle_factory()` | `ParameterHandleFactory` |
| `getParameterHandleValueMapFactory` | `get_parameter_handle_value_map_factory` | `get_parameter_handle_value_map_factory()` | `ParameterHandleValueMapFactory` |
| `getParameterName` | `get_parameter_name` | `get_parameter_name(which_class: InteractionClassHandle, the_handle: ParameterHandle)` | `str` |
| `getRangeBounds` | `get_range_bounds` | `get_range_bounds(region: RegionHandle, dimension: DimensionHandle)` | `RangeBounds` |
| `getRegionHandleSetFactory` | `get_region_handle_set_factory` | `get_region_handle_set_factory()` | `RegionHandleSetFactory` |
| `getTimeFactory` | `get_time_factory` | `get_time_factory()` | `LogicalTimeFactoryLike` |
| `getTransportationName` | `get_transportation_name` | `get_transportation_name(transportation_type: TransportationType)` | `str` |
| `getTransportationType` | `get_transportation_type` | `get_transportation_type(transportation_name: str)` | `TransportationType` |
| `getTransportationTypeHandle` | `get_transportation_type_handle` | `get_transportation_type_handle(the_name: str)` | `TransportationTypeHandle` |
| `getTransportationTypeHandleFactory` | `get_transportation_type_handle_factory` | `get_transportation_type_handle_factory()` | `TransportationTypeHandleFactory` |
| `getTransportationTypeName` | `get_transportation_type_name` | `get_transportation_type_name(the_handle: TransportationTypeHandle)` | `str` |
| `getUpdateRateValue` | `get_update_rate_value` | `get_update_rate_value(update_rate_designator: str)` | `float` |
| `getUpdateRateValueForAttribute` | `get_update_rate_value_for_attribute` | `get_update_rate_value_for_attribute(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle)` | `float` |
| `isAttributeOwnedByFederate` | `is_attribute_owned_by_federate` | `is_attribute_owned_by_federate(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle)` | `bool` |
| `joinFederationExecution` | `join_federation_execution` | `join_federation_execution(federate_type: str, federation_execution_name: str, *, federate_name: str | None = None, additional_fom_modules: Sequence[URLLike] | None = None)` | `FederateHandle` |
| `listFederationExecutions` | `list_federation_executions` | `list_federation_executions()` | `None` |
| `localDeleteObjectInstance` | `local_delete_object_instance` | `local_delete_object_instance(object_handle: ObjectInstanceHandle)` | `None` |
| `modifyLookahead` | `modify_lookahead` | `modify_lookahead(the_lookahead: LogicalTimeIntervalLike)` | `None` |
| `negotiatedAttributeOwnershipDivestiture` | `negotiated_attribute_ownership_divestiture` | `negotiated_attribute_ownership_divestiture(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `nextMessageRequest` | `next_message_request` | `next_message_request(the_time: LogicalTimeLike)` | `None` |
| `nextMessageRequestAvailable` | `next_message_request_available` | `next_message_request_available(the_time: LogicalTimeLike)` | `None` |
| `normalizeFederateHandle` | `normalize_federate_handle` | `normalize_federate_handle(federate_handle: FederateHandle)` | `int` |
| `normalizeServiceGroup` | `normalize_service_group` | `normalize_service_group(group: ServiceGroup)` | `int` |
| `publishInteractionClass` | `publish_interaction_class` | `publish_interaction_class(the_interaction: InteractionClassHandle)` | `None` |
| `publishObjectClassAttributes` | `publish_object_class_attributes` | `publish_object_class_attributes(the_class: ObjectClassHandle, attribute_list: AttributeHandleSet)` | `None` |
| `queryAttributeOwnership` | `query_attribute_ownership` | `query_attribute_ownership(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle)` | `None` |
| `queryAttributeTransportationType` | `query_attribute_transportation_type` | `query_attribute_transportation_type(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle)` | `None` |
| `queryFederationRestoreStatus` | `query_federation_restore_status` | `query_federation_restore_status()` | `None` |
| `queryFederationSaveStatus` | `query_federation_save_status` | `query_federation_save_status()` | `None` |
| `queryGALT` | `query_galt` | `query_galt()` | `TimeQueryReturn` |
| `queryInteractionTransportationType` | `query_interaction_transportation_type` | `query_interaction_transportation_type(the_federate: FederateHandle, the_interaction: InteractionClassHandle)` | `None` |
| `queryLITS` | `query_lits` | `query_lits()` | `TimeQueryReturn` |
| `queryLogicalTime` | `query_logical_time` | `query_logical_time()` | `LogicalTimeLike` |
| `queryLookahead` | `query_lookahead` | `query_lookahead()` | `LogicalTimeIntervalLike` |
| `registerFederationSynchronizationPoint` | `register_federation_synchronization_point` | `register_federation_synchronization_point(synchronization_point_label: str, user_supplied_tag: VariableLengthDataLike, synchronization_set: FederateHandleSet | None = None)` | `None` |
| `registerObjectInstance` | `register_object_instance` | `register_object_instance(the_class: ObjectClassHandle, the_object_name: str | None = None)` | `ObjectInstanceHandle` |
| `registerObjectInstanceWithRegions` | `register_object_instance_with_regions` | `register_object_instance_with_regions(the_class: ObjectClassHandle, attributes_and_regions: AttributeSetRegionSetPairList, the_object: str | None = None)` | `ObjectInstanceHandle` |
| `releaseMultipleObjectInstanceName` | `release_multiple_object_instance_name` | `release_multiple_object_instance_name(the_object_names: set[str])` | `None` |
| `releaseObjectInstanceName` | `release_object_instance_name` | `release_object_instance_name(the_object_instance_name: str)` | `None` |
| `requestAttributeTransportationTypeChange` | `request_attribute_transportation_type_change` | `request_attribute_transportation_type_change(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, the_type: TransportationTypeHandle)` | `None` |
| `requestAttributeValueUpdate` | `request_attribute_value_update` | `request_attribute_value_update(target: ObjectInstanceHandle | ObjectClassHandle, the_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `requestAttributeValueUpdateWithRegions` | `request_attribute_value_update_with_regions` | `request_attribute_value_update_with_regions(the_class: ObjectClassHandle, attributes_and_regions: AttributeSetRegionSetPairList, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `requestFederationRestore` | `request_federation_restore` | `request_federation_restore(label: str)` | `None` |
| `requestFederationSave` | `request_federation_save` | `request_federation_save(label: str, the_time: LogicalTimeLike | None = None)` | `None` |
| `requestInteractionTransportationTypeChange` | `request_interaction_transportation_type_change` | `request_interaction_transportation_type_change(the_class: InteractionClassHandle, the_type: TransportationTypeHandle)` | `None` |
| `reserveMultipleObjectInstanceName` | `reserve_multiple_object_instance_name` | `reserve_multiple_object_instance_name(the_object_names: set[str])` | `None` |
| `reserveObjectInstanceName` | `reserve_object_instance_name` | `reserve_object_instance_name(the_object_name: str)` | `None` |
| `resignFederationExecution` | `resign_federation_execution` | `resign_federation_execution(resign_action: ResignAction)` | `None` |
| `retract` | `retract` | `retract(the_handle: MessageRetractionHandle)` | `None` |
| `sendInteraction` | `send_interaction` | `send_interaction(the_interaction: InteractionClassHandle, the_parameters: ParameterHandleValueMap, user_supplied_tag: VariableLengthDataLike, the_time: LogicalTimeLike | None = None)` | `None` |
| `sendInteractionWithRegions` | `send_interaction_with_regions` | `send_interaction_with_regions(the_interaction: InteractionClassHandle, the_parameters: ParameterHandleValueMap, regions: RegionHandleSet, user_supplied_tag: VariableLengthDataLike, the_time: LogicalTimeLike | None = None)` | `None` |
| `setAutomaticResignDirective` | `set_automatic_resign_directive` | `set_automatic_resign_directive(resign_action: ResignAction)` | `None` |
| `setRangeBounds` | `set_range_bounds` | `set_range_bounds(region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds)` | `None` |
| `subscribeInteractionClass` | `subscribe_interaction_class` | `subscribe_interaction_class(the_class: InteractionClassHandle)` | `None` |
| `subscribeInteractionClassPassively` | `subscribe_interaction_class_passively` | `subscribe_interaction_class_passively(the_class: InteractionClassHandle)` | `None` |
| `subscribeInteractionClassPassivelyWithRegions` | `subscribe_interaction_class_passively_with_regions` | `subscribe_interaction_class_passively_with_regions(the_class: InteractionClassHandle, regions: RegionHandleSet)` | `None` |
| `subscribeInteractionClassWithRegions` | `subscribe_interaction_class_with_regions` | `subscribe_interaction_class_with_regions(the_class: InteractionClassHandle, regions: RegionHandleSet)` | `None` |
| `subscribeObjectClassAttributes` | `subscribe_object_class_attributes` | `subscribe_object_class_attributes(the_class: ObjectClassHandle, attribute_list: AttributeHandleSet, update_rate_designator: str | None = None)` | `None` |
| `subscribeObjectClassAttributesPassively` | `subscribe_object_class_attributes_passively` | `subscribe_object_class_attributes_passively(the_class: ObjectClassHandle, attribute_list: AttributeHandleSet, update_rate_designator: str | None = None)` | `None` |
| `subscribeObjectClassAttributesPassivelyWithRegions` | `subscribe_object_class_attributes_passively_with_regions` | `subscribe_object_class_attributes_passively_with_regions(the_class: ObjectClassHandle, attributes_and_regions: AttributeSetRegionSetPairList, update_rate_designator: str | None = None)` | `None` |
| `subscribeObjectClassAttributesWithRegions` | `subscribe_object_class_attributes_with_regions` | `subscribe_object_class_attributes_with_regions(the_class: ObjectClassHandle, attributes_and_regions: AttributeSetRegionSetPairList, update_rate_designator: str | None = None)` | `None` |
| `synchronizationPointAchieved` | `synchronization_point_achieved` | `synchronization_point_achieved(synchronization_point_label: str, success_indicator: bool | None = None)` | `None` |
| `timeAdvanceRequest` | `time_advance_request` | `time_advance_request(the_time: LogicalTimeLike)` | `None` |
| `timeAdvanceRequestAvailable` | `time_advance_request_available` | `time_advance_request_available(the_time: LogicalTimeLike)` | `None` |
| `unassociateRegionsForUpdates` | `unassociate_regions_for_updates` | `unassociate_regions_for_updates(the_object: ObjectInstanceHandle, attributes_and_regions: AttributeSetRegionSetPairList)` | `None` |
| `unconditionalAttributeOwnershipDivestiture` | `unconditional_attribute_ownership_divestiture` | `unconditional_attribute_ownership_divestiture(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `unpublishInteractionClass` | `unpublish_interaction_class` | `unpublish_interaction_class(the_interaction: InteractionClassHandle)` | `None` |
| `unpublishObjectClass` | `unpublish_object_class` | `unpublish_object_class(the_class: ObjectClassHandle)` | `None` |
| `unpublishObjectClassAttributes` | `unpublish_object_class_attributes` | `unpublish_object_class_attributes(the_class: ObjectClassHandle, attribute_list: AttributeHandleSet)` | `None` |
| `unsubscribeInteractionClass` | `unsubscribe_interaction_class` | `unsubscribe_interaction_class(the_class: InteractionClassHandle)` | `None` |
| `unsubscribeInteractionClassWithRegions` | `unsubscribe_interaction_class_with_regions` | `unsubscribe_interaction_class_with_regions(the_class: InteractionClassHandle, regions: RegionHandleSet)` | `None` |
| `unsubscribeObjectClass` | `unsubscribe_object_class` | `unsubscribe_object_class(the_class: ObjectClassHandle)` | `None` |
| `unsubscribeObjectClassAttributes` | `unsubscribe_object_class_attributes` | `unsubscribe_object_class_attributes(the_class: ObjectClassHandle, attribute_list: AttributeHandleSet)` | `None` |
| `unsubscribeObjectClassAttributesWithRegions` | `unsubscribe_object_class_attributes_with_regions` | `unsubscribe_object_class_attributes_with_regions(the_class: ObjectClassHandle, attributes_and_regions: AttributeSetRegionSetPairList)` | `None` |
| `updateAttributeValues` | `update_attribute_values` | `update_attribute_values(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleValueMap, user_supplied_tag: VariableLengthDataLike, the_time: LogicalTimeLike | None = None)` | `None` |

## FederateAmbassador

| Java name | Python alias | Signature | Returns |
| --- | --- | --- | --- |
| `announceSynchronizationPoint` | `announce_synchronization_point` | `announce_synchronization_point(synchronization_point_label: str, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `attributeIsNotOwned` | `attribute_is_not_owned` | `attribute_is_not_owned(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle)` | `None` |
| `attributeIsOwnedByRTI` | `attribute_is_owned_by_rti` | `attribute_is_owned_by_rti(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle)` | `None` |
| `attributeOwnershipAcquisitionNotification` | `attribute_ownership_acquisition_notification` | `attribute_ownership_acquisition_notification(the_object: ObjectInstanceHandle, secured_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `attributeOwnershipUnavailable` | `attribute_ownership_unavailable` | `attribute_ownership_unavailable(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `attributesInScope` | `attributes_in_scope` | `attributes_in_scope(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `attributesOutOfScope` | `attributes_out_of_scope` | `attributes_out_of_scope(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `confirmAttributeOwnershipAcquisitionCancellation` | `confirm_attribute_ownership_acquisition_cancellation` | `confirm_attribute_ownership_acquisition_cancellation(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `confirmAttributeTransportationTypeChange` | `confirm_attribute_transportation_type_change` | `confirm_attribute_transportation_type_change(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, the_transportation: TransportationTypeHandle)` | `None` |
| `confirmInteractionTransportationTypeChange` | `confirm_interaction_transportation_type_change` | `confirm_interaction_transportation_type_change(the_interaction: InteractionClassHandle, the_transportation: TransportationTypeHandle)` | `None` |
| `connectionLost` | `connection_lost` | `connection_lost(fault_description: str)` | `None` |
| `discoverObjectInstance` | `discover_object_instance` | `discover_object_instance(the_object: ObjectInstanceHandle, the_object_class: ObjectClassHandle, object_name: str, producing_federate: FederateHandle | None = None)` | `None` |
| `federationNotRestored` | `federation_not_restored` | `federation_not_restored(reason: RestoreFailureReason)` | `None` |
| `federationNotSaved` | `federation_not_saved` | `federation_not_saved(reason: SaveFailureReason)` | `None` |
| `federationRestoreBegun` | `federation_restore_begun` | `federation_restore_begun()` | `None` |
| `federationRestoreStatusResponse` | `federation_restore_status_response` | `federation_restore_status_response(response: Sequence[FederateRestoreStatus])` | `None` |
| `federationRestored` | `federation_restored` | `federation_restored()` | `None` |
| `federationSaveStatusResponse` | `federation_save_status_response` | `federation_save_status_response(response: Sequence[FederateHandleSaveStatusPair])` | `None` |
| `federationSaved` | `federation_saved` | `federation_saved()` | `None` |
| `federationSynchronized` | `federation_synchronized` | `federation_synchronized(synchronization_point_label: str, failed_to_sync_set: FederateHandleSet)` | `None` |
| `getProducingFederate` | `get_producing_federate` | `get_producing_federate()` | `FederateHandle` |
| `getSentRegions` | `get_sent_regions` | `get_sent_regions()` | `RegionHandleSet` |
| `hasProducingFederate` | `has_producing_federate` | `has_producing_federate()` | `bool` |
| `hasSentRegions` | `has_sent_regions` | `has_sent_regions()` | `bool` |
| `informAttributeOwnership` | `inform_attribute_ownership` | `inform_attribute_ownership(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle, the_owner: FederateHandle)` | `None` |
| `initiateFederateRestore` | `initiate_federate_restore` | `initiate_federate_restore(label: str, federate_name: str, federate_handle: FederateHandle)` | `None` |
| `initiateFederateSave` | `initiate_federate_save` | `initiate_federate_save(label: str, time: LogicalTimeLike | None = None)` | `None` |
| `multipleObjectInstanceNameReservationFailed` | `multiple_object_instance_name_reservation_failed` | `multiple_object_instance_name_reservation_failed(object_names: set[str])` | `None` |
| `multipleObjectInstanceNameReservationSucceeded` | `multiple_object_instance_name_reservation_succeeded` | `multiple_object_instance_name_reservation_succeeded(object_names: set[str])` | `None` |
| `objectInstanceNameReservationFailed` | `object_instance_name_reservation_failed` | `object_instance_name_reservation_failed(object_name: str)` | `None` |
| `objectInstanceNameReservationSucceeded` | `object_instance_name_reservation_succeeded` | `object_instance_name_reservation_succeeded(object_name: str)` | `None` |
| `provideAttributeValueUpdate` | `provide_attribute_value_update` | `provide_attribute_value_update(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `receiveInteraction` | `receive_interaction` | `receive_interaction(interaction_class: InteractionClassHandle, the_parameters: ParameterHandleValueMap, user_supplied_tag: VariableLengthDataLike, sent_ordering: OrderType, the_transport: TransportationTypeHandle, the_time: LogicalTimeLike, received_ordering: OrderType | None = None, retraction_handle: MessageRetractionHandle | None = None, receive_info: SupplementalReceiveInfo | None = None)` | `None` |
| `reflectAttributeValues` | `reflect_attribute_values` | `reflect_attribute_values(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleValueMap, user_supplied_tag: VariableLengthDataLike, sent_ordering: OrderType, the_transport: TransportationTypeHandle, the_time: LogicalTimeLike, received_ordering: OrderType | None = None, retraction_handle: MessageRetractionHandle | None = None, reflect_info: SupplementalReflectInfo | None = None)` | `None` |
| `removeObjectInstance` | `remove_object_instance` | `remove_object_instance(the_object: ObjectInstanceHandle, user_supplied_tag: VariableLengthDataLike, sent_ordering: OrderType, the_time: LogicalTimeLike, received_ordering: OrderType | None = None, retraction_handle: MessageRetractionHandle | None = None, remove_info: SupplementalRemoveInfo | None = None)` | `None` |
| `reportAttributeTransportationType` | `report_attribute_transportation_type` | `report_attribute_transportation_type(the_object: ObjectInstanceHandle, the_attribute: AttributeHandle, the_transportation: TransportationTypeHandle)` | `None` |
| `reportFederationExecutions` | `report_federation_executions` | `report_federation_executions(the_federation_execution_information_set: FederationExecutionInformationSet)` | `None` |
| `reportInteractionTransportationType` | `report_interaction_transportation_type` | `report_interaction_transportation_type(the_federate: FederateHandle, the_interaction: InteractionClassHandle, the_transportation: TransportationTypeHandle)` | `None` |
| `requestAttributeOwnershipAssumption` | `request_attribute_ownership_assumption` | `request_attribute_ownership_assumption(the_object: ObjectInstanceHandle, offered_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `requestAttributeOwnershipRelease` | `request_attribute_ownership_release` | `request_attribute_ownership_release(the_object: ObjectInstanceHandle, candidate_attributes: AttributeHandleSet, user_supplied_tag: VariableLengthDataLike)` | `None` |
| `requestDivestitureConfirmation` | `request_divestiture_confirmation` | `request_divestiture_confirmation(the_object: ObjectInstanceHandle, offered_attributes: AttributeHandleSet)` | `None` |
| `requestFederationRestoreFailed` | `request_federation_restore_failed` | `request_federation_restore_failed(label: str)` | `None` |
| `requestFederationRestoreSucceeded` | `request_federation_restore_succeeded` | `request_federation_restore_succeeded(label: str)` | `None` |
| `requestRetraction` | `request_retraction` | `request_retraction(the_handle: MessageRetractionHandle)` | `None` |
| `startRegistrationForObjectClass` | `start_registration_for_object_class` | `start_registration_for_object_class(the_class: ObjectClassHandle)` | `None` |
| `stopRegistrationForObjectClass` | `stop_registration_for_object_class` | `stop_registration_for_object_class(the_class: ObjectClassHandle)` | `None` |
| `synchronizationPointRegistrationFailed` | `synchronization_point_registration_failed` | `synchronization_point_registration_failed(synchronization_point_label: str, reason: SynchronizationPointFailureReason)` | `None` |
| `synchronizationPointRegistrationSucceeded` | `synchronization_point_registration_succeeded` | `synchronization_point_registration_succeeded(synchronization_point_label: str)` | `None` |
| `timeAdvanceGrant` | `time_advance_grant` | `time_advance_grant(the_time: LogicalTimeLike)` | `None` |
| `timeConstrainedEnabled` | `time_constrained_enabled` | `time_constrained_enabled(time: LogicalTimeLike)` | `None` |
| `timeRegulationEnabled` | `time_regulation_enabled` | `time_regulation_enabled(time: LogicalTimeLike)` | `None` |
| `turnInteractionsOff` | `turn_interactions_off` | `turn_interactions_off(the_handle: InteractionClassHandle)` | `None` |
| `turnInteractionsOn` | `turn_interactions_on` | `turn_interactions_on(the_handle: InteractionClassHandle)` | `None` |
| `turnUpdatesOffForObjectInstance` | `turn_updates_off_for_object_instance` | `turn_updates_off_for_object_instance(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet)` | `None` |
| `turnUpdatesOnForObjectInstance` | `turn_updates_on_for_object_instance` | `turn_updates_on_for_object_instance(the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet, update_rate_designator: str | None = None)` | `None` |
