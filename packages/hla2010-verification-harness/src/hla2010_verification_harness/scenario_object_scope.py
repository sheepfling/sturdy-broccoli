"""Object-scope and relevance verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel
from hla2010.exceptions import AttributeNotOwned
from hla2010.handles import AttributeHandleSet, RegionHandleSet
from hla2010.types import RangeBounds
from hla2010.types import AttributeRegionAssociation

from .scenario_support import drain_callbacks_pair


@dataclass(frozen=True)
class ObjectScopeScenarioConfig:
    federation_name: str = "ObjectScopeFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    observer_name: str = "Observer"
    federate_type: str = "ObjectScopeFederate"
    object_class_name: str = "HLAobjectRoot.Target"
    attribute_name: str = "Position"
    object_instance_name: str = "Relevance-1"
    in_scope_payload: bytes = b"owner-in-scope"
    out_of_scope_payload: bytes = b"owner-out-of-scope"
    acquired_payload: bytes = b"new-owner-in-scope"
    acquisition_tag: bytes = b"relevance-acquire"
    owner_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(0, 10))
    in_scope_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(0, 10))
    observer_initial_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(90, 100))
    out_of_scope_bounds: RangeBounds = field(default_factory=lambda: RangeBounds(90, 100))


def run_object_scope_relevance_scenario(
    owner_rti: Any,
    acquirer_rti: Any,
    observer_rti: Any,
    *,
    config: ObjectScopeScenarioConfig,
    owner_federate: Any,
    acquirer_federate: Any,
    observer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer_rti.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.joinFederationExecution(config.owner_name, config.federate_type, config.federation_name)
    acquirer_handle = acquirer_rti.joinFederationExecution(
        config.acquirer_name,
        config.federate_type,
        config.federation_name,
    )
    observer_handle = observer_rti.joinFederationExecution(
        config.observer_name,
        config.federate_type,
        config.federation_name,
    )

    owner_class = owner_rti.getObjectClassHandle(config.object_class_name)
    acquirer_class = acquirer_rti.getObjectClassHandle(config.object_class_name)
    observer_class = observer_rti.getObjectClassHandle(config.object_class_name)
    owner_attribute = owner_rti.getAttributeHandle(owner_class, config.attribute_name)
    acquirer_attribute = acquirer_rti.getAttributeHandle(acquirer_class, config.attribute_name)
    observer_attribute = observer_rti.getAttributeHandle(observer_class, config.attribute_name)
    owner_dimension = owner_rti.getDimensionHandle("HLAdefaultRoutingSpace")
    acquirer_dimension = acquirer_rti.getDimensionHandle("HLAdefaultRoutingSpace")
    observer_dimension = observer_rti.getDimensionHandle("HLAdefaultRoutingSpace")

    owner_region = owner_rti.createRegion({owner_dimension})
    acquirer_region = acquirer_rti.createRegion({acquirer_dimension})
    observer_region = observer_rti.createRegion({observer_dimension})
    owner_rti.setRangeBounds(owner_region, owner_dimension, config.owner_bounds)
    acquirer_rti.setRangeBounds(acquirer_region, acquirer_dimension, config.in_scope_bounds)
    observer_rti.setRangeBounds(observer_region, observer_dimension, config.observer_initial_bounds)
    owner_rti.commitRegionModifications({owner_region})
    acquirer_rti.commitRegionModifications({acquirer_region})
    observer_rti.commitRegionModifications({observer_region})

    owner_rti.publishObjectClassAttributes(owner_class, {owner_attribute})
    acquirer_rti.publishObjectClassAttributes(acquirer_class, {acquirer_attribute})
    observer_rti.enableAttributeScopeAdvisorySwitch()
    observer_rti.subscribeObjectClassAttributesWithRegions(
        observer_class,
        [AttributeRegionAssociation(AttributeHandleSet({observer_attribute}), RegionHandleSet({observer_region}))],
    )

    object_instance = owner_rti.registerObjectInstanceWithRegions(
        owner_class,
        [AttributeRegionAssociation(AttributeHandleSet({owner_attribute}), RegionHandleSet({owner_region}))],
        config.object_instance_name,
    )
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=24)
    assert observer_federate.last_callback("discoverObjectInstance") is not None
    assert not observer_federate.callbacks_named("attributesInScope")
    assert not observer_federate.callbacks_named("attributesOutOfScope")

    observer_rti.setRangeBounds(observer_region, observer_dimension, config.in_scope_bounds)
    observer_rti.commitRegionModifications({observer_region})
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=16)
    initial_in_scope = observer_federate.last_callback("attributesInScope")
    assert initial_in_scope is not None
    assert initial_in_scope.args[0] == object_instance
    assert initial_in_scope.args[1] == {observer_attribute}

    observer_federate.clear()
    owner_rti.updateAttributeValues(object_instance, {owner_attribute: config.in_scope_payload}, b"\x00\x00\x00\x00")
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=16)
    initial_reflection = observer_federate.last_callback("reflectAttributeValues")
    assert initial_reflection is not None
    assert initial_reflection.args[1] == {observer_attribute: config.in_scope_payload}

    observer_rti.setRangeBounds(observer_region, observer_dimension, config.out_of_scope_bounds)
    observer_rti.commitRegionModifications({observer_region})
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=16)
    out_of_scope = observer_federate.last_callback("attributesOutOfScope")
    assert out_of_scope is not None
    assert out_of_scope.args[0] == object_instance
    assert out_of_scope.args[1] == {observer_attribute}
    observer_federate.clear()
    owner_rti.updateAttributeValues(object_instance, {owner_attribute: config.out_of_scope_payload}, b"\x00\x00\x00\x00")
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=16)
    suppressed_reflection = observer_federate.last_callback("reflectAttributeValues")
    assert suppressed_reflection is None

    acquirer_rti.attributeOwnershipAcquisition(object_instance, {acquirer_attribute}, config.acquisition_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=24)
    owner_rti.attributeOwnershipDivestitureIfWanted(object_instance, {owner_attribute})
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=24)

    owner_rti.setRangeBounds(owner_region, owner_dimension, config.in_scope_bounds)
    observer_rti.setRangeBounds(observer_region, observer_dimension, config.in_scope_bounds)
    owner_rti.commitRegionModifications({owner_region})
    observer_rti.commitRegionModifications({observer_region})
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=16)
    reacquired_in_scope = observer_federate.last_callback("attributesInScope")
    assert reacquired_in_scope is not None
    assert reacquired_in_scope.args[0] == object_instance
    assert reacquired_in_scope.args[1] == {observer_attribute}

    owner_not_owned = False
    try:
        owner_rti.updateAttributeValues(object_instance, {owner_attribute: b"stale-owner"}, b"\x00\x00\x00\x00")
    except AttributeNotOwned:
        owner_not_owned = True
    assert owner_not_owned

    observer_federate.clear()
    acquirer_rti.updateAttributeValues(
        object_instance,
        {acquirer_attribute: config.acquired_payload},
        b"\x00\x00\x00\x00",
    )
    drain_callbacks_pair(owner_rti, acquirer_rti, observer_rti, loops=16)
    acquired_reflection = observer_federate.last_callback("reflectAttributeValues")
    assert acquired_reflection is not None
    assert acquired_reflection.args[1] == {observer_attribute: config.acquired_payload}

    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "observer_handle": observer_handle,
        "owner_class": owner_class,
        "observer_class": observer_class,
        "object_instance": object_instance,
        "observer_attribute": observer_attribute,
        "initial_in_scope": initial_in_scope,
        "out_of_scope": out_of_scope,
        "reacquired_in_scope": reacquired_in_scope,
        "initial_reflection": initial_reflection,
        "suppressed_reflection": suppressed_reflection,
        "acquired_reflection": acquired_reflection,
    }


__all__ = [
    "ObjectScopeScenarioConfig",
    "run_object_scope_relevance_scenario",
]
