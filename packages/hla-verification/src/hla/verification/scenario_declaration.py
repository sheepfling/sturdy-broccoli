"""Shared declaration-management verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from hla.rti1516e.exceptions import (
    AttributeNotDefined,
    AttributeNotPublished,
    InteractionClassNotPublished,
    ObjectClassNotPublished,
    RTIexception,
)
from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.handles import FederateHandle
from hla.rti1516e.time import HLAinteger64Interval
from .scenario_support import (
    drain_callbacks_pair,
    register_named_object_instance,
    wait_for_callback,
    wait_for_callback_count_pair,
)


@dataclass(frozen=True)
class DeclarationManagementScenarioConfig:
    federation_name: str = "DeclarationManagementFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "SmokeFederate"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    interaction_class_name: str = "HLAinteractionRoot.DemoInteraction"
    parameter_name: str = "Message"
    object_instance_name: str = "DeclarationObject-1"
    attribute_payload: bytes = b"declaration-payload"
    attribute_tag: bytes = b"declaration-tag"
    interaction_payload: bytes = b"declaration-interaction"
    interaction_tag: bytes = b"declaration-interaction-tag"
    use_passive_object_subscription: bool = False
    use_passive_interaction_subscription: bool = False
    use_full_object_unpublish: bool = False
    use_full_object_unsubscribe: bool = False
    declaration_lookahead: Any = HLAinteger64Interval(1)
    before_object_unpublish_rejection_probe: Callable[[Any], None] | None = None
    before_interaction_unpublish_rejection_probe: Callable[[Any], None] | None = None
    expected_object_unpublish_rejection_exceptions: tuple[type[RTIexception], ...] = (
        AttributeNotPublished,
        ObjectClassNotPublished,
    )
    expected_interaction_unpublish_rejection_exceptions: tuple[type[RTIexception], ...] = (
        InteractionClassNotPublished,
    )


def run_declaration_management_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: DeclarationManagementScenarioConfig,
    publisher_federate: Any,
    subscriber_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.join_federation_execution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    subscriber_handle = subscriber_rti.join_federation_execution(
        config.subscriber_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(publisher_handle, FederateHandle)
    assert isinstance(subscriber_handle, FederateHandle)

    publisher_class = publisher_rti.get_object_class_handle(config.object_class_name)
    subscriber_class = subscriber_rti.get_object_class_handle(config.object_class_name)
    publisher_attribute = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)
    subscriber_attribute = subscriber_rti.get_attribute_handle(subscriber_class, config.attribute_name)
    publisher_interaction = publisher_rti.get_interaction_class_handle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.get_interaction_class_handle(config.interaction_class_name)
    publisher_parameter = publisher_rti.get_parameter_handle(publisher_interaction, config.parameter_name)
    subscriber_parameter = subscriber_rti.get_parameter_handle(subscriber_interaction, config.parameter_name)

    if config.use_passive_object_subscription:
        subscriber_rti.subscribe_object_class_attributes_passively(subscriber_class, {subscriber_attribute})
    else:
        subscriber_rti.subscribe_object_class_attributes(subscriber_class, {subscriber_attribute})
    if config.use_passive_interaction_subscription:
        subscriber_rti.subscribe_interaction_class_passively(subscriber_interaction)
    else:
        subscriber_rti.subscribe_interaction_class(subscriber_interaction)
    drain_callbacks_pair(publisher_rti, subscriber_rti)

    start_baseline = len(publisher_federate.callbacks_named("startRegistrationForObjectClass"))
    stop_baseline = len(publisher_federate.callbacks_named("stopRegistrationForObjectClass"))
    turn_on_baseline = len(publisher_federate.callbacks_named("turnInteractionsOn"))
    turn_off_baseline = len(publisher_federate.callbacks_named("turnInteractionsOff"))
    assert start_baseline == 0
    assert stop_baseline == 0
    assert turn_on_baseline == 0
    assert turn_off_baseline == 0

    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attribute})
    publisher_rti.publish_interaction_class(publisher_interaction)
    start_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "startRegistrationForObjectClass",
        start_baseline + 1,
        loops=120,
    )
    turn_on_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "turnInteractionsOn",
        turn_on_baseline + 1,
        loops=120,
    )
    start_record = start_records[-1]
    turn_on_record = turn_on_records[-1]
    assert start_record.args == (publisher_class,)
    assert turn_on_record.args == (publisher_interaction,)

    object_instance = register_named_object_instance(
        publisher_rti,
        publisher_federate,
        publisher_class,
        config.object_instance_name,
    )
    discover_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "discoverObjectInstance",
        len(subscriber_federate.callbacks_named("discoverObjectInstance")) + 1,
        loops=120,
    )
    discover_record = discover_records[-1]
    assert discover_record.args[1] == subscriber_class
    assert discover_record.args[2] == config.object_instance_name

    publisher_rti.update_attribute_values(
        object_instance,
        {publisher_attribute: config.attribute_payload},
        config.attribute_tag,
    )
    reflect_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "reflectAttributeValues",
        len(subscriber_federate.callbacks_named("reflectAttributeValues")) + 1,
        loops=120,
    )
    reflect_record = reflect_records[-1]
    assert reflect_record.args[0] == discover_record.args[0]
    assert reflect_record.args[1] == {subscriber_attribute: config.attribute_payload}
    assert reflect_record.args[2] == config.attribute_tag

    publisher_rti.send_interaction(
        publisher_interaction,
        {publisher_parameter: config.interaction_payload},
        config.interaction_tag,
    )
    interaction_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "receiveInteraction",
        len(subscriber_federate.callbacks_named("receiveInteraction")) + 1,
        loops=120,
    )
    interaction_record = interaction_records[-1]
    assert interaction_record.args[0] == subscriber_interaction
    assert interaction_record.args[1] == {subscriber_parameter: config.interaction_payload}
    assert interaction_record.args[2] == config.interaction_tag

    if config.use_full_object_unpublish:
        publisher_rti.unpublish_object_class(publisher_class)
    else:
        publisher_rti.unpublish_object_class_attributes(publisher_class, {publisher_attribute})
    publisher_rti.unpublish_interaction_class(publisher_interaction)
    stop_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "stopRegistrationForObjectClass",
        stop_baseline + 1,
        loops=120,
    )
    turn_off_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "turnInteractionsOff",
        turn_off_baseline + 1,
        loops=120,
    )
    first_stop_record = stop_records[-1]
    first_turn_off_record = turn_off_records[-1]
    assert first_stop_record.args == (publisher_class,)
    assert first_turn_off_record.args == (publisher_interaction,)

    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attribute})
    publisher_rti.publish_interaction_class(publisher_interaction)
    start_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "startRegistrationForObjectClass",
        start_baseline + 2,
        loops=120,
    )
    turn_on_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "turnInteractionsOn",
        turn_on_baseline + 2,
        loops=120,
    )
    second_start_record = start_records[-1]
    second_turn_on_record = turn_on_records[-1]
    assert second_start_record.args == (publisher_class,)
    assert second_turn_on_record.args == (publisher_interaction,)

    if config.use_full_object_unsubscribe:
        subscriber_rti.unsubscribe_object_class(subscriber_class)
    else:
        subscriber_rti.unsubscribe_object_class_attributes(subscriber_class, {subscriber_attribute})
    subscriber_rti.unsubscribe_interaction_class(subscriber_interaction)
    expected_second_stop_count = stop_baseline + (1 if config.use_full_object_unsubscribe else 2)
    stop_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "stopRegistrationForObjectClass",
        expected_second_stop_count,
        loops=120,
    )
    turn_off_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "turnInteractionsOff",
        turn_off_baseline + 2,
        loops=120,
    )
    second_stop_record = stop_records[-1] if len(stop_records) > stop_baseline + 1 else None
    second_turn_off_record = turn_off_records[-1]
    if second_stop_record is not None:
        assert second_stop_record.args == (publisher_class,)
    assert second_turn_off_record.args == (publisher_interaction,)

    suppressed_reflect_baseline = len(subscriber_federate.callbacks_named("reflectAttributeValues"))
    suppressed_interaction_baseline = len(subscriber_federate.callbacks_named("receiveInteraction"))
    publisher_rti.update_attribute_values(
        object_instance,
        {publisher_attribute: b"after-unsubscribe"},
        b"after-unsubscribe",
    )
    publisher_rti.send_interaction(
        publisher_interaction,
        {publisher_parameter: b"after-unsubscribe"},
        b"after-unsubscribe",
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=24)
    suppressed_reflects = subscriber_federate.callbacks_named("reflectAttributeValues")
    suppressed_interactions = subscriber_federate.callbacks_named("receiveInteraction")
    assert len(suppressed_reflects) == suppressed_reflect_baseline
    assert len(suppressed_interactions) == suppressed_interaction_baseline

    return {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attribute,
        "subscriber_attribute": subscriber_attribute,
        "publisher_interaction": publisher_interaction,
        "subscriber_interaction": subscriber_interaction,
        "publisher_parameter": publisher_parameter,
        "subscriber_parameter": subscriber_parameter,
        "object_instance": object_instance,
        "discover_record": discover_record,
        "reflect_record": reflect_record,
        "interaction_record": interaction_record,
        "start_records": start_records,
        "stop_records": stop_records,
        "turn_on_records": turn_on_records,
        "turn_off_records": turn_off_records,
        "first_start_record": start_record,
        "first_stop_record": first_stop_record,
        "second_start_record": second_start_record,
        "second_stop_record": second_stop_record,
        "first_turn_on_record": turn_on_record,
        "first_turn_off_record": first_turn_off_record,
        "second_turn_on_record": second_turn_on_record,
        "second_turn_off_record": second_turn_off_record,
        "suppressed_reflect_count": len(suppressed_reflects),
        "suppressed_interaction_count": len(suppressed_interactions),
    }

def run_declaration_invalid_attribute_publication_scenario(
    publisher_rti: Any,
    *,
    config: DeclarationManagementScenarioConfig,
    publisher_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.join_federation_execution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(publisher_handle, FederateHandle)

    publisher_class = publisher_rti.get_object_class_handle(config.object_class_name)
    publisher_attribute = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)
    invalid_attribute = type(publisher_attribute)(publisher_attribute.value + 1000)

    try:
        publisher_rti.publish_object_class_attributes(publisher_class, {invalid_attribute})
    except AttributeNotDefined as exc:
        return {
            "publisher_handle": publisher_handle,
            "publisher_class": publisher_class,
            "publisher_attribute": publisher_attribute,
            "invalid_attribute": invalid_attribute,
            "exception": exc,
        }
    raise AssertionError("publish_object_class_attributes accepted an unavailable attribute")


def run_declaration_unpublish_rejection_scenario(
    publisher_rti: Any,
    *,
    config: DeclarationManagementScenarioConfig,
    publisher_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.join_federation_execution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(publisher_handle, FederateHandle)

    publisher_class = publisher_rti.get_object_class_handle(config.object_class_name)
    publisher_attribute = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)
    publisher_interaction = publisher_rti.get_interaction_class_handle(config.interaction_class_name)
    publisher_parameter = publisher_rti.get_parameter_handle(publisher_interaction, config.parameter_name)

    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attribute})
    publisher_rti.publish_interaction_class(publisher_interaction)
    object_instance = register_named_object_instance(
        publisher_rti,
        publisher_federate,
        publisher_class,
        config.object_instance_name,
    )

    publisher_rti.unpublish_object_class_attributes(publisher_class, {publisher_attribute})
    if config.before_object_unpublish_rejection_probe is not None:
        config.before_object_unpublish_rejection_probe(publisher_rti)
    try:
        publisher_rti.update_attribute_values(
            object_instance,
            {publisher_attribute: config.attribute_payload},
            config.attribute_tag,
        )
    except config.expected_object_unpublish_rejection_exceptions as exc:
        object_unpublish_error = exc
    else:
        raise AssertionError("update_attribute_values succeeded after unpublish_object_class_attributes")

    publisher_rti.unpublish_interaction_class(publisher_interaction)
    if config.before_interaction_unpublish_rejection_probe is not None:
        config.before_interaction_unpublish_rejection_probe(publisher_rti)
    try:
        publisher_rti.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.interaction_payload},
            config.interaction_tag,
        )
    except config.expected_interaction_unpublish_rejection_exceptions as exc:
        interaction_unpublish_error = exc
    else:
        raise AssertionError("send_interaction succeeded after unpublish_interaction_class")

    return {
        "publisher_handle": publisher_handle,
        "publisher_class": publisher_class,
        "publisher_attribute": publisher_attribute,
        "publisher_interaction": publisher_interaction,
        "publisher_parameter": publisher_parameter,
        "object_instance": object_instance,
        "object_unpublish_error": object_unpublish_error,
        "interaction_unpublish_error": interaction_unpublish_error,
    }


def run_time_managed_declaration_independence_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: DeclarationManagementScenarioConfig,
    publisher_federate: Any,
    subscriber_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.join_federation_execution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    subscriber_handle = subscriber_rti.join_federation_execution(
        config.subscriber_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(publisher_handle, FederateHandle)
    assert isinstance(subscriber_handle, FederateHandle)

    publisher_class = publisher_rti.get_object_class_handle(config.object_class_name)
    subscriber_class = subscriber_rti.get_object_class_handle(config.object_class_name)
    publisher_attribute = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)
    subscriber_attribute = subscriber_rti.get_attribute_handle(subscriber_class, config.attribute_name)
    publisher_interaction = publisher_rti.get_interaction_class_handle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.get_interaction_class_handle(config.interaction_class_name)
    publisher_parameter = publisher_rti.get_parameter_handle(publisher_interaction, config.parameter_name)
    subscriber_parameter = subscriber_rti.get_parameter_handle(subscriber_interaction, config.parameter_name)

    publisher_rti.enable_time_regulation(config.declaration_lookahead)
    subscriber_rti.enable_time_constrained()
    time_regulation = wait_for_callback(
        publisher_rti,
        publisher_federate,
        "timeRegulationEnabled",
        loops=120,
    )
    time_constrained = wait_for_callback(
        subscriber_rti,
        subscriber_federate,
        "timeConstrainedEnabled",
        loops=120,
    )
    assert time_regulation is not None
    assert time_constrained is not None

    subscriber_rti.subscribe_object_class_attributes(subscriber_class, {subscriber_attribute})
    subscriber_rti.subscribe_interaction_class(subscriber_interaction)
    drain_callbacks_pair(publisher_rti, subscriber_rti)

    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attribute})
    publisher_rti.publish_interaction_class(publisher_interaction)
    start_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "startRegistrationForObjectClass",
        1,
        loops=120,
    )
    turn_on_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        publisher_federate,
        "turnInteractionsOn",
        1,
        loops=120,
    )
    start_record = start_records[-1]
    turn_on_record = turn_on_records[-1]
    assert start_record.args == (publisher_class,)
    assert turn_on_record.args == (publisher_interaction,)

    object_instance = register_named_object_instance(
        publisher_rti,
        publisher_federate,
        publisher_class,
        config.object_instance_name,
    )
    discover_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "discoverObjectInstance",
        1,
        loops=120,
    )
    discover_record = discover_records[-1]
    assert discover_record.args[1] == subscriber_class
    assert discover_record.args[2] == config.object_instance_name

    publisher_rti.update_attribute_values(
        object_instance,
        {publisher_attribute: config.attribute_payload},
        config.attribute_tag,
    )
    reflect_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "reflectAttributeValues",
        1,
        loops=120,
    )
    reflect_record = reflect_records[-1]
    assert reflect_record.args[0] == discover_record.args[0]
    assert reflect_record.args[1] == {subscriber_attribute: config.attribute_payload}
    assert reflect_record.args[2] == config.attribute_tag

    publisher_rti.send_interaction(
        publisher_interaction,
        {publisher_parameter: config.interaction_payload},
        config.interaction_tag,
    )
    interaction_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "receiveInteraction",
        1,
        loops=120,
    )
    interaction_record = interaction_records[-1]
    assert interaction_record.args[0] == subscriber_interaction
    assert interaction_record.args[1] == {subscriber_parameter: config.interaction_payload}
    assert interaction_record.args[2] == config.interaction_tag

    return {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attribute,
        "subscriber_attribute": subscriber_attribute,
        "publisher_interaction": publisher_interaction,
        "subscriber_interaction": subscriber_interaction,
        "publisher_parameter": publisher_parameter,
        "subscriber_parameter": subscriber_parameter,
        "object_instance": object_instance,
        "time_regulation": time_regulation,
        "time_constrained": time_constrained,
        "start_record": start_record,
        "turn_on_record": turn_on_record,
        "discover_record": discover_record,
        "reflect_record": reflect_record,
        "interaction_record": interaction_record,
    }


__all__ = [
    "DeclarationManagementScenarioConfig",
    "run_declaration_invalid_attribute_publication_scenario",
    "run_declaration_management_scenario",
    "run_declaration_unpublish_rejection_scenario",
    "run_time_managed_declaration_independence_scenario",
]
