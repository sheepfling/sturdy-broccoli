"""Transport, ordering, and attribute-filter helpers for object delivery."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol

from hla.rti1516e.exceptions import CouldNotDecode, InvalidTransportationType
from hla.fom import validate_encoded_datatype_value
from hla.rti1516e.handles import (
    AttributeHandle,
    InteractionClassHandle,
    ObjectInstanceHandle,
    RegionHandle,
    TransportationTypeHandle,
)

from .state import FederateState, FederationState, ObjectInstance

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine


class _ObjectDeliveryContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: FederateState
    config: Any

    def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle | None: ...

    def _object_matches_subscription(self, actual_class: object, subscribed_class: object) -> bool: ...

    def _find_object(self, theObject: ObjectInstanceHandle) -> tuple[FederationState, ObjectInstance]: ...

    def _attribute_subscription_intersection(
        self,
        federate: FederateState,
        object_class: object,
        attributes: Mapping[AttributeHandle, bytes],
        instance: ObjectInstance | None = None,
        sent_regions_by_attribute: Mapping[AttributeHandle, set["RegionHandle"]] | None = None,
    ) -> dict[AttributeHandle, bytes]: ...

    def _interaction_matches_subscription(
        self,
        actual_class: InteractionClassHandle,
        subscribed_class: InteractionClassHandle,
    ) -> bool: ...


if TYPE_CHECKING:
    class _ObjectDeliveryTransportMixinBase(_ObjectDeliveryContext):
        pass
else:
    class _ObjectDeliveryTransportMixinBase:
        pass


class PythonRTIObjectTransportMixin(_ObjectDeliveryTransportMixinBase):
    """Shared transport and filtering helpers used by object delivery services."""

    def _transportation_handle_from_fom_name(self, name: str | None) -> TransportationTypeHandle:
        normalized = str(name or "").strip()
        handle = self._transportation_handle_by_name(normalized)
        if handle is None:
            return self.engine.transportation_reliable
        return handle

    def _default_transportation_type_for_attribute(
        self,
        object_handle: ObjectInstanceHandle,
        attribute: AttributeHandle,
    ) -> TransportationTypeHandle:
        federation = self.state.federation
        if federation is None:
            return self.engine.transportation_reliable
        try:
            instance = federation.objects[object_handle]
        except KeyError:
            return self.engine.transportation_reliable
        class_name = self.engine.object_class_for_handle(instance.class_handle).name
        spec = federation.fom_catalog.object_classes.get(class_name)
        if spec is None:
            return self.engine.transportation_reliable
        attribute_name = self.engine.attribute_name(instance.class_handle, attribute)
        return self._transportation_handle_from_fom_name(
            dict(spec.attribute_transportations).get(attribute_name)
        )

    def _default_transportation_type_for_interaction(
        self,
        interaction: InteractionClassHandle,
    ) -> TransportationTypeHandle:
        federation = self.state.federation
        if federation is None:
            return self.engine.transportation_reliable
        class_name = self.engine.interaction_for_handle(interaction).name
        spec = federation.fom_catalog.interaction_classes.get(class_name)
        if spec is None:
            return self.engine.transportation_reliable
        return self._transportation_handle_from_fom_name(spec.transportation)

    def _subscribed_update_rate_for_attribute(
        self,
        federate: FederateState,
        instance: ObjectInstance,
        attribute: AttributeHandle,
    ) -> float:
        try:
            attribute_name = self.engine.attribute_name(instance.class_handle, attribute)
        except Exception:
            known_class = federate.known_object_classes.get(instance.handle)
            if known_class is None:
                return 0.0
            attribute_name = self.engine.attribute_name(known_class, attribute)
        matches: list[tuple[int, float]] = []
        for subscribed_class, rate_map in federate.subscribed_object_update_rates.items():
            if not self._object_matches_subscription(instance.class_handle, subscribed_class):
                continue
            subscribed_attr = self.engine.object_class_for_handle(
                subscribed_class
            ).attributes_by_name.get(attribute_name)
            if subscribed_attr is None:
                continue
            if subscribed_attr not in rate_map:
                continue
            specificity = len(self.engine.object_class_for_handle(subscribed_class).name)
            matches.append((specificity, float(rate_map[subscribed_attr])))
        if not matches:
            return 0.0
        return max(matches, key=lambda item: item[0])[1]

    def _transportation_type_for_attribute(
        self,
        object_handle: ObjectInstanceHandle,
        attribute: AttributeHandle,
    ) -> TransportationTypeHandle:
        return self.state.attribute_transportation_overrides.get(
            (object_handle, attribute),
            self._default_transportation_type_for_attribute(object_handle, attribute),
        )

    def _transportation_type_for_reflected_attribute(
        self,
        federate: FederateState,
        instance: ObjectInstance,
        reflected_attribute: AttributeHandle,
    ) -> TransportationTypeHandle:
        try:
            return self._transportation_type_for_attribute(instance.handle, reflected_attribute)
        except Exception:
            known_class = federate.known_object_classes.get(instance.handle)
            if known_class is None:
                raise
            attribute_name = self.engine.attribute_name(known_class, reflected_attribute)
            source_attribute = self.engine.object_class_for_handle(
                instance.class_handle
            ).attributes_by_name.get(attribute_name)
            if source_attribute is None:
                raise
            return self._transportation_type_for_attribute(instance.handle, source_attribute)

    def _transportation_type_for_interaction(
        self,
        interaction: InteractionClassHandle,
    ) -> TransportationTypeHandle:
        return self.state.interaction_transportation_overrides.get(
            interaction,
            self._default_transportation_type_for_interaction(interaction),
        )

    def _validate_transportation_type(
        self,
        theType: TransportationTypeHandle,
    ) -> None:
        if theType not in {
            self.engine.transportation_reliable,
            self.engine.transportation_best_effort,
        }:
            raise InvalidTransportationType(repr(theType))

    @staticmethod
    def _time_scalar(value: Any) -> float | None:
        if value is None:
            return None
        scalar = getattr(value, "value", value)
        try:
            return float(scalar)
        except Exception:
            return None

    def _apply_update_rate_reduction(
        self,
        federate: FederateState,
        instance: ObjectInstance,
        attributes: Mapping[AttributeHandle, bytes],
        delivery_time: Any | None,
    ) -> dict[AttributeHandle, bytes]:
        scalar_time = self._time_scalar(delivery_time)
        if scalar_time is None and (
            self.state.time_regulation_enabled or self.state.time_constrained_enabled
        ):
            scalar_time = self._time_scalar(self.state.current_time)
        if scalar_time is None:
            return dict(attributes)
        filtered: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            rate = self._subscribed_update_rate_for_attribute(federate, instance, handle)
            if rate <= 0.0:
                filtered[handle] = value
                federate.last_reflect_logical_times[(instance.handle, handle)] = scalar_time
                continue
            min_interval = 1.0 / rate
            last_time = federate.last_reflect_logical_times.get((instance.handle, handle))
            if last_time is None or (scalar_time - last_time) >= min_interval:
                filtered[handle] = value
                federate.last_reflect_logical_times[(instance.handle, handle)] = scalar_time
        return filtered

    def _validate_user_supplied_tag(
        self,
        federation: FederationState,
        category: str,
        user_supplied_tag: bytes,
    ) -> None:
        metadata = federation.fom_catalog.tag_representations.get(str(category), {})
        datatype = str(metadata.get("datatype", "")).strip()
        if not datatype or datatype in {"", "NA", "N/A"}:
            return
        try:
            validate_encoded_datatype_value(
                bytes(user_supplied_tag), datatype, federation.fom_catalog
            )
        except CouldNotDecode as exc:
            raise CouldNotDecode(f"Could not decode {category} as {datatype}") from exc
