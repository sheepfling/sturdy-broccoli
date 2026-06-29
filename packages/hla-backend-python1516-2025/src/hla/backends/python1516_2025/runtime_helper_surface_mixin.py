"""Mechanical runtime-helper wrappers for the Python 2025 RTI ambassador."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Mapping, Protocol

from hla.rti1516_2025.datatypes import RangeBounds
from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
from hla.rti1516_2025.exceptions import (
    AttributeNotDefined,
    FederateNotExecutionMember,
    InvalidAttributeHandle,
    InvalidObjectInstanceHandle,
    InvalidRangeBound,
    InvalidRegion,
    InvalidUpdateRateDesignator,
)
from hla.rti1516_2025.handles import (
    AttributeHandle,
    FederateHandle,
    MessageRetractionHandle,
    ObjectInstanceHandle,
    RegionHandle,
    TransportationTypeHandle,
)

from .attribute_policy_runtime import (
    attribute_order_for,
    attribute_transportation_for,
    default_order_for,
    default_transportation_for,
    known_object_classes_for_federate,
    reflectable_attribute_names_for_subscriber,
)
from .attribute_scope_runtime import (
    deliver_forced_remove_callbacks,
    evaluate_attribute_scope_advisories,
)
from .callback_runtime import (
    deliver_callback,
    deliver_callback_now,
    deliver_mom_service_report,
    deliver_queued_callback,
    deliver_to_federate_handle,
    deliver_to_federate_handle_now,
)
from .catalog_access_runtime import (
    catalog,
    dimension_default_upper_bound,
    dimension_handles,
    dimension_spec,
    federation_record,
    interaction_class_handles,
    normalize_handle,
    object_class_handles,
    stable_handles,
    transportation_handles,
)
from .catalog_runtime import (
    attribute_handles,
    interaction_class_name,
    object_class_name,
    object_instance_record,
    object_instance_record_known,
    parameter_handles,
    synchronization_required_federates,
    transportation_handle_by_name,
)
from .ddm_default_attribute_policy import (
    ranges_overlap,
    region_owner_key,
    region_sets_overlap,
    regions_overlap_pair,
)
from .delivery_state_runtime import (
    add_attribute_candidate,
    canonicalize_retraction_handles,
    deliver_due_tso_callbacks,
    drop_retraction_group_member,
    finalize_retraction_group_if_inactive,
    has_attribute_candidate,
    pop_attribute_candidate,
    queue_tso_callback,
    register_retraction_group,
    remove_attribute_candidate,
    resolve_retraction_group,
)
from .federation_bootstrap_runtime import (
    coerce_callback_model,
    extract_additional_fom_modules,
    extract_create_federation_name,
    extract_federate_type,
    extract_federation_name,
    extract_fom_sources,
    extract_join_names,
    extract_logical_time_implementation_name,
    extract_mim_source,
    get_time_factory,
    merge_fom_modules,
    normalize_module_sources,
    resolve_fom_modules,
    select_logical_time_implementation,
    standard_mim_module,
    validate_credentials,
)
from .federation_state_runtime import (
    apply_resign_action,
    cancel_resigning_federate_pending_acquisitions,
    delete_objects_owned_by_resigning_federate,
    delete_objects_owned_by_specific_federate,
    divest_attributes_owned_by_specific_federate,
    divest_resigning_federate_attributes,
    prune_tso_state_for_departing_federate,
    release_join,
    resigning_federate_has_pending_acquisitions,
    resigning_federate_owns_attributes,
)
from .input_guard_runtime import (
    coerce_interval,
    coerce_time,
    normalize_reserved_object_instance_name,
    normalize_reserved_object_instance_name_set,
    require_connected,
    require_joined,
    require_no_save_or_restore,
)
from .interaction_policy_runtime import (
    coerce_order_type,
    interaction_class_names_from_handles,
    interaction_order_for,
    interaction_transportation_for,
    parameter_names_from_handles,
)
from .object_instance_runtime import (
    deliver_value_update_requests,
    request_instance_attribute_value_update,
)
from .object_model_runtime import (
    attribute_name_by_handle,
    attribute_names_from_handles,
    discover_existing_objects_for_current_subscription,
    has_object_registration_interest,
    matching_object_publishers,
    object_class_lineage,
    published_attributes_for_current_federate,
    subscribed_discovery_class_name,
)
from .object_region_runtime import (
    attribute_region_pairs,
    coerce_range_bounds,
    object_instance_region_values,
    region_values_from_handles,
)
from .update_rate_runtime import (
    apply_update_rate_reduction_for_subscriber,
    default_update_rate_designator_for_attribute,
    default_update_rate_for_attribute,
    resolve_update_rate_designator,
    subscribed_update_rate_for_attribute,
    time_scalar,
)

_DEFAULT_LOGICAL_TIME_IMPLEMENTATION = "HLAinteger64Time"
_SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS = frozenset({"HLAinteger64Time", "HLAfloat64Time"})

if TYPE_CHECKING:
    class _RuntimeHelperSurfaceContext(Protocol):
        _federate_name: str | None
        _federation_name: str | None
        _federate_handle: FederateHandle | None


if TYPE_CHECKING:
    class _RuntimeHelperSurfaceMixinBase(_RuntimeHelperSurfaceContext):
        pass
else:
    class _RuntimeHelperSurfaceMixinBase:
        pass


class RuntimeHelperSurfaceMixin(_RuntimeHelperSurfaceMixinBase):
    """Move mechanical helper delegation out of the main ambassador class body."""

    def _deliver_callback(self, method_name: str, *args: Any) -> None:
        deliver_callback(self, method_name, *args)

    def _deliver_callback_now(self, method_name: str, *args: Any) -> None:
        deliver_callback_now(self, method_name, *args)

    def _deliver_to_federate_handle(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        deliver_to_federate_handle(self, federate_handle, method_name, *args)

    def _deliver_to_federate_handle_now(self, federate_handle: FederateHandle, method_name: str, *args: Any) -> None:
        deliver_to_federate_handle_now(self, federate_handle, method_name, *args)

    def _deliver_queued_callback(self, queued: Any) -> None:
        deliver_queued_callback(self, queued)

    def _deliver_mom_service_report(self, report: Mapping[str, Any]) -> None:
        deliver_mom_service_report(self, report)

    def _queue_tso_callback(
        self,
        target_federate: FederateHandle,
        callback_time: Any,
        method_name: str,
        *args: Any,
        exposed_retraction_handle: MessageRetractionHandle | None = None,
    ) -> MessageRetractionHandle:
        return queue_tso_callback(
            self,
            target_federate,
            callback_time,
            method_name,
            *args,
            exposed_retraction_handle=exposed_retraction_handle,
        )

    @staticmethod
    def _register_retraction_group(
        federation: Any,
        member_handles: Iterable[MessageRetractionHandle],
    ) -> MessageRetractionHandle:
        return register_retraction_group(federation, member_handles)

    @staticmethod
    def _resolve_retraction_group(
        federation: Any,
        handle_value: int,
    ) -> tuple[int, set[int]]:
        return resolve_retraction_group(federation, handle_value)

    @staticmethod
    def _drop_retraction_group_member(federation: Any, handle_value: int) -> None:
        drop_retraction_group_member(federation, handle_value)

    @staticmethod
    def _finalize_retraction_group_if_inactive(federation: Any, canonical_handle: int) -> None:
        finalize_retraction_group_if_inactive(federation, canonical_handle)

    @classmethod
    def _canonicalize_retraction_handles(
        cls,
        federation: Any,
        handles: list[MessageRetractionHandle],
    ) -> MessageRetractionHandle:
        return canonicalize_retraction_handles(federation, handles)

    def _deliver_due_tso_callbacks(self) -> None:
        deliver_due_tso_callbacks(self)

    @staticmethod
    def _has_attribute_candidate(
        record: Any,
        attribute_name: str,
        federate_handle: FederateHandle | None,
    ) -> bool:
        return has_attribute_candidate(record, attribute_name, federate_handle)

    @staticmethod
    def _add_attribute_candidate(
        record: Any,
        attribute_name: str,
        federate_handle: FederateHandle | None,
        user_supplied_tag: bytes,
    ) -> None:
        add_attribute_candidate(record, attribute_name, federate_handle, user_supplied_tag)

    @staticmethod
    def _remove_attribute_candidate(
        record: Any,
        attribute_name: str,
        federate_handle: FederateHandle | None,
    ) -> None:
        remove_attribute_candidate(record, attribute_name, federate_handle)

    @staticmethod
    def _pop_attribute_candidate(
        record: Any,
        attribute_name: str,
    ) -> tuple[FederateHandle, bytes] | None:
        return pop_attribute_candidate(record, attribute_name)

    def _require_connected(self, method_name: str) -> None:
        require_connected(self, method_name)

    def _require_joined(self, method_name: str) -> None:
        require_joined(self, method_name)

    def _require_no_save_or_restore(self, method_name: str) -> None:
        require_no_save_or_restore(self, method_name)

    @staticmethod
    def _normalize_reserved_object_instance_name(object_instance_name: Any, *, method_name: str) -> str:
        return normalize_reserved_object_instance_name(object_instance_name, method_name=method_name)

    def _normalize_reserved_object_instance_name_set(self, object_instance_names: Any, *, method_name: str) -> set[str]:
        return normalize_reserved_object_instance_name_set(object_instance_names, method_name=method_name)

    def _extract_federation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        return extract_federation_name(args, kwargs)

    def _extract_create_federation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        return extract_create_federation_name(args, kwargs)

    def _extract_join_names(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[str, str | None]:
        return extract_join_names(args, kwargs)

    def _extract_federate_type(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        return extract_federate_type(args, kwargs)

    def _extract_logical_time_implementation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        return extract_logical_time_implementation_name(
            args,
            kwargs,
            supported_logical_time_implementations=_SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS,
            default_logical_time_implementation=_DEFAULT_LOGICAL_TIME_IMPLEMENTATION,
        )

    def _extract_fom_sources(
        self,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        with_mim: bool,
    ) -> tuple[Any, ...]:
        return extract_fom_sources(args, kwargs, with_mim=with_mim)

    def _extract_mim_source(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any | None:
        return extract_mim_source(args, kwargs)

    def _extract_additional_fom_modules(
        self,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[Any, ...]:
        return extract_additional_fom_modules(args, kwargs)

    @staticmethod
    def _normalize_module_sources(value: Any) -> tuple[Any, ...]:
        return normalize_module_sources(value)

    @staticmethod
    def _coerce_callback_model(value: Any) -> CallbackModel:
        return coerce_callback_model(value)

    def _coerce_time(self, value: Any) -> Any:
        return coerce_time(self, value)

    def _coerce_interval(self, value: Any) -> Any:
        return coerce_interval(self, value)

    @staticmethod
    def _validate_credentials(credentials: Any | None) -> None:
        validate_credentials(credentials)

    @staticmethod
    def _resolve_fom_modules(sources: tuple[Any, ...], *, mim: bool) -> tuple[Any, ...]:
        return resolve_fom_modules(sources, mim=mim)

    @staticmethod
    def _merge_fom_modules(modules: tuple[Any, ...], *, mim_module: Any) -> Any:
        return merge_fom_modules(modules, mim_module=mim_module)

    @staticmethod
    def _standard_mim_module() -> Any:
        return standard_mim_module()

    @staticmethod
    def _get_time_factory(name: str) -> Any:
        return get_time_factory(name)

    def _select_logical_time_implementation(self, name: str) -> None:
        select_logical_time_implementation(self, name)

    def _release_join(self) -> None:
        release_join(self)

    @staticmethod
    def _prune_tso_state_for_departing_federate(
        federation: Any,
        federate_handle: FederateHandle,
    ) -> None:
        prune_tso_state_for_departing_federate(federation, federate_handle)

    def _apply_resign_action(self, resign_action: ResignAction) -> None:
        apply_resign_action(self, resign_action)

    def _cancel_resigning_federate_pending_acquisitions(self) -> None:
        cancel_resigning_federate_pending_acquisitions(self)

    def _resigning_federate_has_pending_acquisitions(self) -> bool:
        return resigning_federate_has_pending_acquisitions(self)

    def _resigning_federate_owns_attributes(self) -> bool:
        return resigning_federate_owns_attributes(self)

    def _delete_objects_owned_by_resigning_federate(self) -> None:
        delete_objects_owned_by_resigning_federate(self)

    def _delete_objects_owned_by_specific_federate(
        self,
        federate_handle: FederateHandle,
        *,
        user_supplied_tag: bytes,
    ) -> None:
        delete_objects_owned_by_specific_federate(self, federate_handle, user_supplied_tag=user_supplied_tag)

    def _divest_resigning_federate_attributes(self) -> None:
        divest_resigning_federate_attributes(self)

    def _divest_attributes_owned_by_specific_federate(self, federate_handle: FederateHandle) -> None:
        divest_attributes_owned_by_specific_federate(self, federate_handle)

    def _matching_object_publishers(
        self,
        federation: Any,
        object_class_name: str,
        attribute_names: set[str],
    ) -> set[int]:
        return matching_object_publishers(federation, object_class_name, attribute_names)

    def _has_object_registration_interest(
        self,
        federation: Any,
        publisher_key: int,
        object_class_name: str,
    ) -> bool:
        return has_object_registration_interest(federation, publisher_key, object_class_name)

    def _matching_interaction_publishers(
        self,
        federation: Any,
        interaction_class_name: str,
    ) -> set[int]:
        publishers: set[int] = set()
        for federate_key, published in federation.published_interactions.items():
            if interaction_class_name in published:
                publishers.add(federate_key)
        return publishers

    def _has_interaction_interest(
        self,
        federation: Any,
        publisher_key: int,
        interaction_class_name: str,
    ) -> bool:
        if interaction_class_name not in federation.published_interactions.get(publisher_key, set()):
            return False
        for subscriber_key, subscribed in federation.subscribed_interactions.items():
            if subscriber_key == publisher_key:
                continue
            if interaction_class_name in subscribed:
                return True
        return False

    def _deliver_resign_remove_callbacks(self, object_instance: ObjectInstanceHandle, record: Any) -> None:
        self._deliver_forced_remove_callbacks(object_instance, record, self._current_federate_handle(), b"")

    def _deliver_forced_remove_callbacks(
        self,
        object_instance: ObjectInstanceHandle,
        record: Any,
        producing_federate: FederateHandle,
        user_supplied_tag: bytes,
    ) -> None:
        deliver_forced_remove_callbacks(
            self,
            object_instance,
            record,
            producing_federate,
            user_supplied_tag,
        )

    def _evaluate_attribute_scope_advisories(self) -> None:
        evaluate_attribute_scope_advisories(self)

    def _resign_reason_description(self, resign_action: ResignAction) -> str:
        action = getattr(resign_action, "name", str(resign_action))
        return f"federateName={self._federate_name}; federationName={self._federation_name}; resignAction={action}"

    @staticmethod
    def _normalize_handle(handle: Any, expected_type: type[Any], exception_type: type[Exception]) -> int:
        return normalize_handle(handle, expected_type, exception_type)

    def _federation_record(self) -> Any:
        return federation_record(self)

    def _catalog(self) -> Any:
        return catalog(self)

    @staticmethod
    def _stable_handles(names: Any) -> dict[str, int]:
        return stable_handles(names)

    @staticmethod
    def _invalid_object_instance_handle_type() -> type[Exception]:
        return InvalidObjectInstanceHandle

    def _object_class_handles(self) -> dict[str, int]:
        return object_class_handles(self)

    def _interaction_class_handles(self) -> dict[str, int]:
        return interaction_class_handles(self)

    def _dimension_handles(self) -> dict[str, int]:
        return dimension_handles(self)

    def _dimension_spec(self, dimension_name: str) -> Any | None:
        return dimension_spec(self, dimension_name)

    def _dimension_default_upper_bound(self, dimension_name: str) -> int:
        return dimension_default_upper_bound(self, dimension_name)

    def _transportation_handles(self) -> dict[str, int]:
        return transportation_handles(self)

    def _attribute_handles(self, object_class_name: str) -> dict[str, int]:
        return attribute_handles(self, object_class_name)

    def _parameter_handles(self, interaction_class_name: str) -> dict[str, int]:
        return parameter_handles(self, interaction_class_name)

    def _object_class_name(self, object_class: Any) -> str:
        return object_class_name(self, object_class)

    def _interaction_class_name(self, interaction_class: Any) -> str:
        return interaction_class_name(self, interaction_class)

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle:
        return transportation_handle_by_name(self, name)

    def _object_instance_record(self, object_instance: Any) -> Any:
        return object_instance_record(self, object_instance)

    def _object_instance_record_known(self, object_instance: Any) -> Any:
        return object_instance_record_known(self, object_instance)

    def _synchronization_required_federates(self, synchronization_set: Any | None) -> set[int]:
        return synchronization_required_federates(self, synchronization_set)

    def _request_instance_attribute_value_update(self, object_instance: ObjectInstanceHandle, attributes: Any, user_supplied_tag: bytes) -> None:
        request_instance_attribute_value_update(self, object_instance, attributes, user_supplied_tag)

    def _deliver_value_update_requests(
        self,
        object_instance: ObjectInstanceHandle,
        record: Any,
        attribute_handles: set[AttributeHandle],
        user_supplied_tag: bytes,
    ) -> None:
        deliver_value_update_requests(self, object_instance, record, attribute_handles, user_supplied_tag)

    def _current_federate_handle(self) -> FederateHandle:
        if self._federate_handle is None:
            raise FederateNotExecutionMember("Current federate handle is not available")
        return self._federate_handle

    def _current_federate_key(self) -> int:
        return self._current_federate_handle().value

    def _published_attributes_for_current_federate(self, object_class_name: str) -> set[str]:
        return published_attributes_for_current_federate(self, object_class_name)

    def _region_dimension_names(self, federate_key: int, region: Any) -> set[str]:
        region_value = self._normalize_handle(region, RegionHandle, InvalidRegion)
        try:
            return set(self._federation_record().member_regions[federate_key][region_value])
        except KeyError as exc:
            raise InvalidRegion(str(region)) from exc

    def _region_values_from_handles(self, regions: Any) -> set[int]:
        return region_values_from_handles(self, regions)

    def _coerce_range_bounds(self, value: Any) -> RangeBounds:
        return coerce_range_bounds(value, invalid_range_bound_exc=InvalidRangeBound)

    def _attribute_region_pairs(self, object_class_name: str, attributes_and_regions: Any) -> tuple[tuple[set[str], set[int]], ...]:
        return attribute_region_pairs(self, object_class_name, attributes_and_regions)

    @staticmethod
    def _ranges_overlap(left: RangeBounds, right: RangeBounds) -> bool:
        return ranges_overlap(left, right)

    def _region_owner_key(self, preferred_key: int, region_value: int) -> int | None:
        return region_owner_key(self, preferred_key, region_value)

    def _regions_overlap_pair(self, source_key: int, source_region: int, target_key: int, target_region: int) -> bool:
        return regions_overlap_pair(self, source_key, source_region, target_key, target_region)

    def _region_sets_overlap(self, source_key: int, source_regions: set[int], target_key: int, target_regions: set[int]) -> bool:
        return region_sets_overlap(self, source_key, source_regions, target_key, target_regions)

    def _object_instance_region_values(self, record: Any) -> set[int]:
        return object_instance_region_values(record)

    def _reflectable_attribute_names_for_subscriber(
        self,
        source_key: int,
        subscriber_key: int,
        record: Any,
        discovery_class_name: str,
        subscribed_names: set[str],
    ) -> set[str]:
        return reflectable_attribute_names_for_subscriber(
            self,
            source_key,
            subscriber_key,
            record,
            discovery_class_name,
            subscribed_names,
        )

    def _known_object_classes_for_federate(
        self,
        federate_key: int,
        object_instance: ObjectInstanceHandle,
        object_class_name: str,
    ) -> str | None:
        return known_object_classes_for_federate(
            self,
            federate_key,
            object_instance,
            object_class_name,
        )

    def _subscribed_discovery_class_name(self, federate_key: int, object_class_name: str) -> str | None:
        return subscribed_discovery_class_name(self, federate_key, object_class_name)

    def _object_class_lineage(self, object_class_name: str) -> tuple[str, ...]:
        return object_class_lineage(self, object_class_name)

    def _attribute_name_by_handle(self, object_class_name: str, attribute: AttributeHandle) -> str:
        return attribute_name_by_handle(
            self,
            object_class_name,
            attribute,
            expected_type=AttributeHandle,
            invalid_handle_exc=InvalidAttributeHandle,
        )

    def _attribute_names_from_handles(self, object_class_name: str, attributes: Any) -> tuple[str, ...]:
        return attribute_names_from_handles(
            self,
            object_class_name,
            attributes,
            expected_type=AttributeHandle,
            invalid_handle_exc=InvalidAttributeHandle,
            empty_set_exc=AttributeNotDefined,
        )

    def _resolve_update_rate_designator(self, *unused: Any) -> tuple[float | None, str | None]:
        return resolve_update_rate_designator(
            self,
            *unused,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def _default_update_rate_for_attribute(self, object_class_name: str, attribute_name: str) -> float | None:
        return default_update_rate_for_attribute(
            self,
            object_class_name,
            attribute_name,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def _default_update_rate_designator_for_attribute(self, object_class_name: str, attribute_name: str) -> str | None:
        return default_update_rate_designator_for_attribute(
            self,
            object_class_name,
            attribute_name,
            invalid_update_rate_designator_exc=InvalidUpdateRateDesignator,
        )

    def _subscribed_update_rate_for_attribute(
        self,
        federate_key: int,
        actual_class_name: str,
        attribute_name: str,
    ) -> float:
        return subscribed_update_rate_for_attribute(
            self,
            federate_key,
            actual_class_name,
            attribute_name,
        )

    @staticmethod
    def _time_scalar(value: Any) -> float | None:
        return time_scalar(value)

    def _apply_update_rate_reduction_for_subscriber(
        self,
        federate_key: int,
        object_instance: ObjectInstanceHandle,
        reflected_class_name: str,
        actual_class_name: str,
        reflected: Mapping[AttributeHandle, bytes],
        delivery_time: Any | None,
    ) -> dict[AttributeHandle, bytes]:
        return apply_update_rate_reduction_for_subscriber(
            self,
            federate_key,
            object_instance,
            reflected_class_name,
            actual_class_name,
            reflected,
            delivery_time,
        )

    def _parameter_names_from_handles(self, interaction_class_name: str, parameters: Any) -> tuple[str, ...]:
        return parameter_names_from_handles(self, interaction_class_name, parameters)

    def _interaction_class_names_from_handles(self, interaction_classes: Any) -> tuple[str, ...]:
        return interaction_class_names_from_handles(self, interaction_classes)

    def _default_transportation_for(self, object_class_name: str, values_by_handle: Mapping[AttributeHandle, bytes]) -> TransportationTypeHandle:
        return default_transportation_for(self, object_class_name, values_by_handle)

    def _attribute_transportation_for(self, record: Any, values_by_handle: Mapping[AttributeHandle, bytes]) -> TransportationTypeHandle:
        return attribute_transportation_for(self, record, values_by_handle)

    def _default_order_for(self, object_class_name: str, values_by_handle: Mapping[AttributeHandle, bytes]) -> OrderType:
        return default_order_for(self, object_class_name, values_by_handle)

    def _attribute_order_for(self, record: Any, values_by_handle: Mapping[AttributeHandle, bytes]) -> OrderType:
        return attribute_order_for(self, record, values_by_handle)

    def _interaction_order_for(self, interaction_class_name: str) -> OrderType:
        return interaction_order_for(self, interaction_class_name)

    def _interaction_transportation_for(self, interaction_class_name: str) -> TransportationTypeHandle:
        return interaction_transportation_for(self, interaction_class_name)

    @staticmethod
    def _coerce_order_type(order_type: Any) -> OrderType:
        return coerce_order_type(order_type)

    def _discover_existing_objects_for_current_subscription(self, object_class_name: str) -> None:
        discover_existing_objects_for_current_subscription(self, object_class_name)
