"""Ownership and negotiated-ownership scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from typing import Any

from hla2010.enums import CallbackModel
from hla2010.exceptions import RTIexception
from hla2010.handles import FederateHandle
from .scenario_support import drain_callbacks_pair, register_named_object_instance, wait_for_callback


@dataclass(frozen=True)
class OwnershipScenarioConfig:
    federation_name: str = "JavaProfileOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "OwnedObject-1"


@dataclass(frozen=True)
class NegotiatedOwnershipScenarioConfig:
    federation_name: str = "JavaProfileNegotiatedOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "NegotiatedOwnedObject-1"
    assumption_tag: bytes = b"assume-offer"
    request_tag: bytes = b"acquire-request"
    cancel_tag: bytes = b"cancel-request"


@dataclass(frozen=True)
class ReleaseRequestOwnershipScenarioConfig:
    federation_name: str = "JavaProfileReleaseRequestOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "ReleaseRequestOwnedObject-1"
    request_tag: bytes = b"acquire-request"
    confirm_tag: bytes = b"confirm-tag"
    owner_action: Literal["deny", "confirm", "ifwanted"] = "ifwanted"


def probe_negotiated_attribute_ownership_offer(
    owner_rti: Any,
    acquirer_rti: Any,
    *,
    config: NegotiatedOwnershipScenarioConfig,
    owner_federate: Any,
    acquirer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer_rti.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(config.federation_name, list(config.fom_modules), config.logical_time_implementation_name)
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    acquirer_handle = acquirer_rti.join_federation_execution(config.acquirer_name, config.federate_type, config.federation_name)
    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    acquirer_class = acquirer_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    acquirer_attr = acquirer_rti.get_attribute_handle(acquirer_class, config.attribute_name)
    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    acquirer_rti.publish_object_class_attributes(acquirer_class, {acquirer_attr})
    acquirer_rti.subscribe_object_class_attributes(acquirer_class, {acquirer_attr})
    object_instance = register_named_object_instance(owner_rti, owner_federate, owner_class, config.object_instance_name)
    discover = wait_for_callback(acquirer_rti, acquirer_federate, "discoverObjectInstance")
    assert discover is not None
    acquirer_object = acquirer_rti.get_object_instance_handle(config.object_instance_name)
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)

    assumption = None
    negotiated_divestiture_supported = False
    try:
        owner_rti.negotiated_attribute_ownership_divestiture(object_instance, {owner_attr}, config.assumption_tag)
        drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
        assumption = acquirer_federate.last_callback("requestAttributeOwnershipAssumption")
        negotiated_divestiture_supported = assumption is not None
    except RTIexception:
        assumption = None

    acquirer_rti.attribute_ownership_acquisition(acquirer_object, {acquirer_attr}, config.request_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    release = owner_federate.last_callback("requestAttributeOwnershipRelease")
    offered_acquired = acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification")
    divest_notice = owner_federate.last_callback("requestDivestitureConfirmation")
    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "assumption": assumption,
        "negotiated_divestiture_supported": negotiated_divestiture_supported,
        "release": release,
        "offered_acquired": offered_acquired,
        "divestiture_confirmation": divest_notice,
    }


def run_attribute_ownership_scenario(
    owner_rti: Any, acquirer_rti: Any, *, config: OwnershipScenarioConfig, owner_federate: Any, acquirer_federate: Any
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer_rti.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(config.federation_name, list(config.fom_modules), config.logical_time_implementation_name)
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    acquirer_handle = acquirer_rti.join_federation_execution(config.acquirer_name, config.federate_type, config.federation_name)
    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    acquirer_class = acquirer_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    acquirer_attr = acquirer_rti.get_attribute_handle(acquirer_class, config.attribute_name)
    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    acquirer_rti.publish_object_class_attributes(acquirer_class, {acquirer_attr})
    acquirer_rti.subscribe_object_class_attributes(acquirer_class, {acquirer_attr})
    object_instance = register_named_object_instance(owner_rti, owner_federate, owner_class, config.object_instance_name)
    discover = wait_for_callback(acquirer_rti, acquirer_federate, "discoverObjectInstance")
    assert discover is not None
    acquirer_object = acquirer_rti.get_object_instance_handle(config.object_instance_name)
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)
    owner_rti.unconditional_attribute_ownership_divestiture(object_instance, {owner_attr})
    assert not owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)
    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    not_owned = wait_for_callback(owner_rti, owner_federate, "attributeIsNotOwned", loops=120)
    assert not_owned is not None
    acquirer_rti.attribute_ownership_acquisition_if_available(acquirer_object, {acquirer_attr})
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    acquired = wait_for_callback(acquirer_rti, acquirer_federate, "attributeOwnershipAcquisitionNotification", loops=120)
    assert acquired is not None
    assert acquired.args[0] == acquirer_object
    assert acquirer_attr in acquired.args[1]
    assert acquirer_rti.is_attribute_owned_by_federate(acquirer_object, acquirer_attr)
    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    informed = wait_for_callback(owner_rti, owner_federate, "informAttributeOwnership", loops=120)
    assert informed is not None
    assert informed.args[0] == object_instance
    assert informed.args[1] == owner_attr
    assert isinstance(informed.args[2], FederateHandle)
    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_class": owner_class,
        "acquirer_class": acquirer_class,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "not_owned": not_owned,
        "acquired": acquired,
        "informed": informed,
    }


def run_negotiated_attribute_ownership_scenario(
    owner_rti: Any, acquirer_rti: Any, *, config: NegotiatedOwnershipScenarioConfig, owner_federate: Any, acquirer_federate: Any
) -> dict[str, Any]:
    probe_summary = probe_negotiated_attribute_ownership_offer(
        owner_rti,
        acquirer_rti,
        config=config,
        owner_federate=owner_federate,
        acquirer_federate=acquirer_federate,
    )
    owner_handle = probe_summary["owner_handle"]
    acquirer_handle = probe_summary["acquirer_handle"]
    object_instance = probe_summary["object_instance"]
    acquirer_object = probe_summary["acquirer_object_instance"]
    owner_attr = probe_summary["owner_attribute"]
    acquirer_attr = probe_summary["acquirer_attribute"]
    assumption = probe_summary["assumption"]
    offered_acquired = probe_summary["offered_acquired"]
    divest_notice = probe_summary["divestiture_confirmation"]
    negotiated_divestiture_supported = probe_summary["negotiated_divestiture_supported"]
    release = probe_summary["release"]
    release_object_instance = object_instance
    release_owner_attribute = owner_attr
    release_acquirer_object = acquirer_object
    release_acquirer_attribute = acquirer_attr
    if release is None:
        assert offered_acquired is not None
        pending_object_name = f"{config.object_instance_name}-pending"
        owner_class = owner_rti.get_object_class_handle(config.object_class_name)
        release_object_instance = register_named_object_instance(owner_rti, owner_federate, owner_class, pending_object_name)
        pending_discover = wait_for_callback(acquirer_rti, acquirer_federate, "discoverObjectInstance")
        assert pending_discover is not None
        release_acquirer_object = acquirer_rti.get_object_instance_handle(pending_object_name)
        acquirer_rti.attribute_ownership_acquisition(release_acquirer_object, {acquirer_attr}, config.request_tag)
        drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
        release = owner_federate.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args[2] == config.request_tag
    acquirer_rti.cancel_attribute_ownership_acquisition(release_acquirer_object, {release_acquirer_attribute})
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    cancellation = acquirer_federate.last_callback("confirmAttributeOwnershipAcquisitionCancellation")
    assert cancellation is not None
    acquirer_rti.attribute_ownership_acquisition(release_acquirer_object, {release_acquirer_attribute}, config.cancel_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    release = owner_federate.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args[2] == config.cancel_tag
    divested = owner_rti.attribute_ownership_divestiture_if_wanted(release_object_instance, {release_owner_attribute})
    assert divested == {release_owner_attribute}
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    acquired = acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquirer_rti.is_attribute_owned_by_federate(release_acquirer_object, release_acquirer_attribute)
    owner_rti.query_attribute_ownership(release_object_instance, release_owner_attribute)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    informed = owner_federate.last_callback("informAttributeOwnership")
    assert informed is not None
    assert isinstance(informed.args[2], FederateHandle)
    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "assumption": assumption,
        "offered_acquired": offered_acquired,
        "divestiture_confirmation": divest_notice,
        "negotiated_divestiture_supported": negotiated_divestiture_supported,
        "release_object_instance": release_object_instance,
        "release_acquirer_object_instance": release_acquirer_object,
        "release": release,
        "cancellation": cancellation,
        "divested": divested,
        "acquired": acquired,
        "informed": informed,
    }


def run_confirm_divestiture_negotiated_scenario(
    owner_rti: Any,
    acquirer_rti: Any,
    *,
    config: NegotiatedOwnershipScenarioConfig,
    owner_federate: Any,
    acquirer_federate: Any,
    confirm_tag: bytes = b"confirm-tag",
) -> dict[str, Any]:
    probe_summary = probe_negotiated_attribute_ownership_offer(
        owner_rti,
        acquirer_rti,
        config=config,
        owner_federate=owner_federate,
        acquirer_federate=acquirer_federate,
    )
    assert probe_summary["negotiated_divestiture_supported"] is True
    divest_notice = probe_summary["divestiture_confirmation"]
    assert divest_notice is not None

    object_instance = probe_summary["object_instance"]
    acquirer_object = probe_summary["acquirer_object_instance"]
    owner_attr = probe_summary["owner_attribute"]
    acquirer_attr = probe_summary["acquirer_attribute"]

    owner_rti.confirm_divestiture(object_instance, {owner_attr}, confirm_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)

    acquired = acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args[0] == acquirer_object
    assert acquired.args[1] == {acquirer_attr}
    assert acquired.args[2] == confirm_tag
    assert acquirer_rti.is_attribute_owned_by_federate(acquirer_object, acquirer_attr)

    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    informed = owner_federate.last_callback("informAttributeOwnership")
    assert informed is not None
    assert isinstance(informed.args[2], FederateHandle)

    return {
        "owner_handle": probe_summary["owner_handle"],
        "acquirer_handle": probe_summary["acquirer_handle"],
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "divestiture_confirmation": divest_notice,
        "acquired": acquired,
        "informed": informed,
        "confirm_tag": confirm_tag,
    }


def run_release_request_ownership_scenario(
    owner_rti: Any,
    acquirer_rti: Any,
    *,
    config: ReleaseRequestOwnershipScenarioConfig,
    owner_federate: Any,
    acquirer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer_rti.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(config.federation_name, list(config.fom_modules), config.logical_time_implementation_name)
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    acquirer_handle = acquirer_rti.join_federation_execution(config.acquirer_name, config.federate_type, config.federation_name)
    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    acquirer_class = acquirer_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    acquirer_attr = acquirer_rti.get_attribute_handle(acquirer_class, config.attribute_name)
    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    acquirer_rti.publish_object_class_attributes(acquirer_class, {acquirer_attr})
    acquirer_rti.subscribe_object_class_attributes(acquirer_class, {acquirer_attr})
    object_instance = register_named_object_instance(owner_rti, owner_federate, owner_class, config.object_instance_name)
    discover = wait_for_callback(acquirer_rti, acquirer_federate, "discoverObjectInstance")
    assert discover is not None
    acquirer_object = acquirer_rti.get_object_instance_handle(config.object_instance_name)
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)

    acquirer_rti.attribute_ownership_acquisition(acquirer_object, {acquirer_attr}, config.request_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    release = owner_federate.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args == (object_instance, {owner_attr}, config.request_tag)

    denied = False
    divested = None
    if config.owner_action == "deny":
        owner_rti.attribute_ownership_release_denied(object_instance, {owner_attr})
        denied = True
    elif config.owner_action == "confirm":
        owner_rti.confirm_divestiture(object_instance, {owner_attr}, config.confirm_tag)
    elif config.owner_action == "ifwanted":
        divested = owner_rti.attribute_ownership_divestiture_if_wanted(object_instance, {owner_attr})
        assert divested == {owner_attr}
    else:
        raise AssertionError(f"unexpected owner_action {config.owner_action!r}")

    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    acquired = acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification")

    if denied:
        assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)
        assert not acquirer_rti.is_attribute_owned_by_federate(acquirer_object, acquirer_attr)
        assert acquired is None
        return {
            "owner_handle": owner_handle,
            "acquirer_handle": acquirer_handle,
            "object_instance": object_instance,
            "acquirer_object_instance": acquirer_object,
            "owner_attribute": owner_attr,
            "acquirer_attribute": acquirer_attr,
            "release": release,
            "acquired": None,
            "owner_action": config.owner_action,
            "divested": divested,
        }

    assert acquired is not None
    assert acquired.args[0] == acquirer_object
    assert acquired.args[1] == {acquirer_attr}
    if config.owner_action == "ifwanted":
        assert acquired.args[2] == b""
    assert acquirer_rti.is_attribute_owned_by_federate(acquirer_object, acquirer_attr)
    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    informed = owner_federate.last_callback("informAttributeOwnership")
    assert informed is not None
    assert isinstance(informed.args[2], FederateHandle)
    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "release": release,
        "acquired": acquired,
        "informed": informed,
        "owner_action": config.owner_action,
        "divested": divested,
    }


__all__ = [
    "run_confirm_divestiture_negotiated_scenario",
    "NegotiatedOwnershipScenarioConfig",
    "OwnershipScenarioConfig",
    "ReleaseRequestOwnershipScenarioConfig",
    "probe_negotiated_attribute_ownership_offer",
    "run_attribute_ownership_scenario",
    "run_negotiated_attribute_ownership_scenario",
    "run_release_request_ownership_scenario",
]
