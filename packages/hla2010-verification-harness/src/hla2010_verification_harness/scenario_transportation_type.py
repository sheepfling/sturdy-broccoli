"""Transportation-type verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel
from hla2010.enums import OrderType
from hla2010.exceptions import (
    AttributeNotDefined,
    AttributeNotOwned,
    InvalidInteractionClassHandle,
    InvalidTransportationType,
    ObjectInstanceNotKnown,
    RestoreInProgress,
    SaveInProgress,
)

from .scenario_support import drain_callbacks_pair, register_named_object_instance, wait_for_callback


@dataclass(frozen=True)
class TransportationTypeScenarioConfig:
    federation_name: str = "TransportationTypeFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    observer_name: str = "Observer"
    federate_type: str = "TransportationFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    interaction_class_name: str = "HLAinteractionRoot.SmokeInteraction"
    object_instance_name: str = "Transport-Object-1"
    transportation_name: str = "HLAbestEffort"
    second_attribute_name: str = "RCS"
    parameter_name: str = "TrackId"
    reliable_transportation_name: str = "HLAreliable"
    best_effort_attribute_payload: bytes = b"best-effort-attribute"
    reliable_attribute_payload: bytes = b"reliable-attribute"
    interaction_payload: bytes = b"best-effort-interaction"
    update_tag: bytes = b"transport-mixed-update"
    interaction_tag: bytes = b"transport-best-effort-interaction"
    save_name: str = "TRANSPORT-SAVE"


def run_transportation_type_scenario(
    owner_rti: Any,
    observer_rti: Any,
    *,
    config: TransportationTypeScenarioConfig,
    owner_federate: Any,
    observer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    observer_handle = observer_rti.join_federation_execution(config.observer_name, config.federate_type, config.federation_name)

    object_class = owner_rti.get_object_class_handle(config.object_class_name)
    attribute = owner_rti.get_attribute_handle(object_class, config.attribute_name)
    interaction = owner_rti.get_interaction_class_handle(config.interaction_class_name)
    transport = owner_rti.get_transportation_type_handle(config.transportation_name)

    owner_rti.publish_object_class_attributes(object_class, {attribute})
    owner_rti.publish_interaction_class(interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    object_instance = register_named_object_instance(
        owner_rti,
        owner_federate,
        object_class,
        config.object_instance_name,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)
    owner_federate.clear()

    owner_rti.request_attribute_transportation_type_change(object_instance, {attribute}, transport)
    owner_rti.query_attribute_transportation_type(object_instance, attribute)
    owner_rti.request_interaction_transportation_type_change(interaction, transport)
    owner_rti.query_interaction_transportation_type(interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    confirm_attribute = owner_federate.last_callback("confirmAttributeTransportationTypeChange")
    report_attribute = owner_federate.last_callback("reportAttributeTransportationType")
    confirm_interaction = owner_federate.last_callback("confirmInteractionTransportationTypeChange")
    report_interaction = owner_federate.last_callback("reportInteractionTransportationType")

    assert confirm_attribute is not None
    assert report_attribute is not None
    assert confirm_interaction is not None
    assert report_interaction is not None

    assert confirm_attribute.args == (object_instance, {attribute}, transport)
    assert report_attribute.args == (object_instance, attribute, transport)
    assert confirm_interaction.args == (interaction, transport)
    assert report_interaction.args[1:] == (interaction, transport)

    return {
        "owner_handle": owner_handle,
        "observer_handle": observer_handle,
        "object_class": object_class,
        "attribute": attribute,
        "interaction": interaction,
        "transport": transport,
        "object_instance": object_instance,
        "confirm_attribute": confirm_attribute,
        "report_attribute": report_attribute,
        "confirm_interaction": confirm_interaction,
        "report_interaction": report_interaction,
    }


def run_transportation_type_restore_persistence_scenario(
    owner_rti: Any,
    observer_rti: Any,
    *,
    config: TransportationTypeScenarioConfig,
    owner_federate: Any,
    observer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    observer_handle = observer_rti.join_federation_execution(config.observer_name, config.federate_type, config.federation_name)

    object_class = owner_rti.get_object_class_handle(config.object_class_name)
    reliable_attribute = owner_rti.get_attribute_handle(object_class, config.attribute_name)
    best_effort_attribute = owner_rti.get_attribute_handle(object_class, config.second_attribute_name)
    observer_object_class = observer_rti.get_object_class_handle(config.object_class_name)
    observer_reliable_attribute = observer_rti.get_attribute_handle(observer_object_class, config.attribute_name)
    observer_best_effort_attribute = observer_rti.get_attribute_handle(observer_object_class, config.second_attribute_name)
    interaction = owner_rti.get_interaction_class_handle(config.interaction_class_name)
    observer_interaction = observer_rti.get_interaction_class_handle(config.interaction_class_name)
    parameter = owner_rti.get_parameter_handle(interaction, config.parameter_name)
    observer_parameter = observer_rti.get_parameter_handle(observer_interaction, config.parameter_name)
    reliable_transport = owner_rti.get_transportation_type_handle(config.reliable_transportation_name)
    best_effort_transport = owner_rti.get_transportation_type_handle(config.transportation_name)

    owner_rti.publish_object_class_attributes(object_class, {reliable_attribute, best_effort_attribute})
    observer_rti.subscribe_object_class_attributes(observer_object_class, {observer_reliable_attribute, observer_best_effort_attribute})
    owner_rti.publish_interaction_class(interaction)
    observer_rti.subscribe_interaction_class(observer_interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    object_instance = register_named_object_instance(
        owner_rti,
        owner_federate,
        object_class,
        config.object_instance_name,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    owner_rti.request_attribute_transportation_type_change(object_instance, {reliable_attribute}, reliable_transport)
    owner_rti.request_attribute_transportation_type_change(object_instance, {best_effort_attribute}, best_effort_transport)
    owner_rti.request_interaction_transportation_type_change(interaction, best_effort_transport)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    observer_federate.clear()
    owner_rti.update_attribute_values(
        object_instance,
        {
            reliable_attribute: config.reliable_attribute_payload,
            best_effort_attribute: config.best_effort_attribute_payload,
        },
        config.update_tag,
    )
    owner_rti.send_interaction(
        interaction,
        {parameter: config.interaction_payload},
        config.interaction_tag,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    pre_restore_reflects = observer_federate.callbacks_named("reflectAttributeValues")
    pre_restore_interaction = observer_federate.last_callback("receiveInteraction")
    assert len(pre_restore_reflects) == 2
    assert pre_restore_interaction is not None
    reflected_by_transport = {record.args[4]: record.args[1] for record in pre_restore_reflects}
    assert reflected_by_transport[reliable_transport] == {observer_reliable_attribute: config.reliable_attribute_payload}
    assert reflected_by_transport[best_effort_transport] == {observer_best_effort_attribute: config.best_effort_attribute_payload}
    assert pre_restore_interaction.args[0] == observer_interaction
    assert pre_restore_interaction.args[1] == {observer_parameter: config.interaction_payload}
    assert pre_restore_interaction.args[2] == config.interaction_tag
    assert pre_restore_interaction.args[3] is OrderType.RECEIVE
    assert pre_restore_interaction.args[4] == best_effort_transport

    owner_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    owner_initiate_save = wait_for_callback(owner_rti, owner_federate, "initiateFederateSave", loops=120)
    observer_initiate_save = wait_for_callback(observer_rti, observer_federate, "initiateFederateSave", loops=120)
    assert owner_initiate_save is not None
    assert observer_initiate_save is not None

    owner_rti.federate_save_begun()
    observer_rti.federate_save_begun()
    owner_rti.federate_save_complete()
    observer_rti.federate_save_complete()
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    owner_saved = wait_for_callback(owner_rti, owner_federate, "federationSaved", loops=120)
    observer_saved = wait_for_callback(observer_rti, observer_federate, "federationSaved", loops=120)
    assert owner_saved is not None
    assert observer_saved is not None

    owner_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    restore_succeeded = wait_for_callback(owner_rti, owner_federate, "requestFederationRestoreSucceeded", loops=120)
    restore_begun = wait_for_callback(owner_rti, owner_federate, "federationRestoreBegun", loops=120)
    observer_initiate_restore = wait_for_callback(observer_rti, observer_federate, "initiateFederateRestore", loops=120)
    assert restore_succeeded is not None
    assert restore_begun is not None
    assert observer_initiate_restore is not None

    owner_rti.federate_restore_complete()
    observer_rti.federate_restore_complete()
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    owner_restored = wait_for_callback(owner_rti, owner_federate, "federationRestored", loops=120)
    observer_restored = wait_for_callback(observer_rti, observer_federate, "federationRestored", loops=120)
    assert owner_restored is not None
    assert observer_restored is not None

    owner_federate.clear()
    observer_federate.clear()
    owner_rti.query_attribute_transportation_type(object_instance, reliable_attribute)
    owner_rti.query_attribute_transportation_type(object_instance, best_effort_attribute)
    owner_rti.query_interaction_transportation_type(interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    post_restore_attribute_reports = owner_federate.callbacks_named("reportAttributeTransportationType")
    post_restore_interaction_report = owner_federate.last_callback("reportInteractionTransportationType")
    assert len(post_restore_attribute_reports) >= 2
    reported_attribute_transports = {record.args[1]: record.args[2] for record in post_restore_attribute_reports}
    assert reported_attribute_transports[reliable_attribute] == reliable_transport
    assert reported_attribute_transports[best_effort_attribute] == best_effort_transport
    assert post_restore_interaction_report is not None
    assert post_restore_interaction_report.args[1:] == (interaction, best_effort_transport)

    owner_rti.update_attribute_values(
        object_instance,
        {
            reliable_attribute: config.reliable_attribute_payload,
            best_effort_attribute: config.best_effort_attribute_payload,
        },
        config.update_tag,
    )
    owner_rti.send_interaction(
        interaction,
        {parameter: config.interaction_payload},
        config.interaction_tag,
    )
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    post_restore_reflects = observer_federate.callbacks_named("reflectAttributeValues")
    post_restore_interaction = observer_federate.last_callback("receiveInteraction")
    assert len(post_restore_reflects) == 2
    post_restore_by_transport = {record.args[4]: record.args[1] for record in post_restore_reflects}
    assert post_restore_by_transport[reliable_transport] == {observer_reliable_attribute: config.reliable_attribute_payload}
    assert post_restore_by_transport[best_effort_transport] == {observer_best_effort_attribute: config.best_effort_attribute_payload}
    assert post_restore_interaction is not None
    assert post_restore_interaction.args[4] == best_effort_transport

    return {
        "owner_handle": owner_handle,
        "observer_handle": observer_handle,
        "object_instance": object_instance,
        "reliable_attribute": reliable_attribute,
        "best_effort_attribute": best_effort_attribute,
        "interaction": interaction,
        "reliable_transport": reliable_transport,
        "best_effort_transport": best_effort_transport,
        "pre_restore_reflects": pre_restore_reflects,
        "pre_restore_interaction": pre_restore_interaction,
        "post_restore_attribute_reports": post_restore_attribute_reports,
        "post_restore_interaction_report": post_restore_interaction_report,
        "post_restore_reflects": post_restore_reflects,
        "post_restore_interaction": post_restore_interaction,
    }


def run_transportation_type_rejection_scenario(
    owner_rti: Any,
    observer_rti: Any,
    *,
    config: TransportationTypeScenarioConfig,
    owner_federate: Any,
    observer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    observer_handle = observer_rti.join_federation_execution(config.observer_name, config.federate_type, config.federation_name)

    object_class = owner_rti.get_object_class_handle(config.object_class_name)
    attribute = owner_rti.get_attribute_handle(object_class, config.attribute_name)
    observer_object_class = observer_rti.get_object_class_handle(config.object_class_name)
    observer_attribute = observer_rti.get_attribute_handle(observer_object_class, config.attribute_name)
    interaction = owner_rti.get_interaction_class_handle(config.interaction_class_name)
    reliable_transport = owner_rti.get_transportation_type_handle(config.reliable_transportation_name)
    invalid_transport = type(reliable_transport)(reliable_transport.value + 1000)
    invalid_attribute = type(attribute)(attribute.value + 1000)
    invalid_interaction = type(interaction)(interaction.value + 1000)

    owner_rti.publish_object_class_attributes(object_class, {attribute})
    observer_rti.subscribe_object_class_attributes(observer_object_class, {observer_attribute})
    owner_rti.publish_interaction_class(interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    object_instance = register_named_object_instance(
        owner_rti,
        owner_federate,
        object_class,
        config.object_instance_name,
    )
    invalid_object_instance = type(object_instance)(999999)
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    owner_federate.clear()
    observer_federate.clear()

    with _expect_exception(ObjectInstanceNotKnown):
        owner_rti.request_attribute_transportation_type_change(invalid_object_instance, {attribute}, reliable_transport)
    with _expect_exception(AttributeNotDefined):
        owner_rti.request_attribute_transportation_type_change(object_instance, {invalid_attribute}, reliable_transport)
    with _expect_exception(InvalidTransportationType):
        owner_rti.request_attribute_transportation_type_change(object_instance, {attribute}, invalid_transport)
    with _expect_exception(AttributeNotOwned):
        observer_rti.request_attribute_transportation_type_change(object_instance, {observer_attribute}, reliable_transport)
    with _expect_exception(ObjectInstanceNotKnown):
        owner_rti.query_attribute_transportation_type(invalid_object_instance, attribute)
    with _expect_exception(AttributeNotDefined):
        owner_rti.query_attribute_transportation_type(object_instance, invalid_attribute)
    with _expect_exception(InvalidInteractionClassHandle):
        owner_rti.request_interaction_transportation_type_change(invalid_interaction, reliable_transport)
    with _expect_exception(InvalidTransportationType):
        owner_rti.request_interaction_transportation_type_change(interaction, invalid_transport)
    with _expect_exception(InvalidInteractionClassHandle):
        owner_rti.query_interaction_transportation_type(invalid_interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    assert owner_federate.callbacks_named("confirmAttributeTransportationTypeChange") == []
    assert owner_federate.callbacks_named("reportAttributeTransportationType") == []
    assert owner_federate.callbacks_named("confirmInteractionTransportationTypeChange") == []
    assert owner_federate.callbacks_named("reportInteractionTransportationType") == []
    assert observer_federate.callbacks_named("confirmAttributeTransportationTypeChange") == []

    owner_rti.request_federation_save(config.save_name)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    with _expect_exception(SaveInProgress):
        owner_rti.request_attribute_transportation_type_change(object_instance, {attribute}, reliable_transport)
    with _expect_exception(SaveInProgress):
        owner_rti.query_attribute_transportation_type(object_instance, attribute)
    with _expect_exception(SaveInProgress):
        owner_rti.request_interaction_transportation_type_change(interaction, reliable_transport)
    with _expect_exception(SaveInProgress):
        owner_rti.query_interaction_transportation_type(interaction)

    owner_rti.federate_save_begun()
    observer_rti.federate_save_begun()
    owner_rti.federate_save_complete()
    observer_rti.federate_save_complete()
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    owner_rti.request_federation_restore(config.save_name)
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)
    with _expect_exception(RestoreInProgress):
        owner_rti.request_attribute_transportation_type_change(object_instance, {attribute}, reliable_transport)
    with _expect_exception(RestoreInProgress):
        owner_rti.query_attribute_transportation_type(object_instance, attribute)
    with _expect_exception(RestoreInProgress):
        owner_rti.request_interaction_transportation_type_change(interaction, reliable_transport)
    with _expect_exception(RestoreInProgress):
        owner_rti.query_interaction_transportation_type(interaction)
    drain_callbacks_pair(owner_rti, observer_rti, loops=8)

    assert owner_federate.callbacks_named("confirmAttributeTransportationTypeChange") == []
    assert owner_federate.callbacks_named("reportAttributeTransportationType") == []
    assert owner_federate.callbacks_named("confirmInteractionTransportationTypeChange") == []
    assert owner_federate.callbacks_named("reportInteractionTransportationType") == []

    owner_rti.abort_federation_restore()
    drain_callbacks_pair(owner_rti, observer_rti, loops=16)

    return {
        "owner_handle": owner_handle,
        "observer_handle": observer_handle,
        "object_instance": object_instance,
        "attribute": attribute,
        "observer_attribute": observer_attribute,
        "interaction": interaction,
        "reliable_transport": reliable_transport,
    }


class _expect_exception:
    def __init__(self, expected: type[BaseException]) -> None:
        self.expected = expected

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, _tb: Any) -> bool:
        if exc_type is None:
            raise AssertionError(f"Expected {self.expected.__name__} to be raised")
        if not issubclass(exc_type, self.expected):
            return False
        return True


__all__ = [
    "TransportationTypeScenarioConfig",
    "run_transportation_type_rejection_scenario",
    "run_transportation_type_restore_persistence_scenario",
    "run_transportation_type_scenario",
]
