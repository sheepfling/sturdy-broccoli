"""Two-federate exchange scenario root."""
from __future__ import annotations

from typing import Any

from hla.rti1516e.enums import CallbackModel, OrderType
from hla.rti1516e.handles import FederateHandle
from hla.backends.common import UnsupportedBackendService
from .scenario_support import (
    drain_callbacks_pair,
    order_value,
    register_named_object_instance,
    wait_for_callback,
    wait_for_callback_count_pair,
)
from .scenario_exchange_history import (
    assert_two_federate_exchange_callback_history,
    run_exchange_round,
)
from .scenario_exchange_types import ExchangeRoundConfig, TwoFederateExchangeConfig


def _is_handle_like(value: Any) -> bool:
    return isinstance(getattr(value, "value", None), int)


def _same_handle_value(left: Any, right: Any) -> bool:
    return getattr(left, "value", None) == getattr(right, "value", None)


def _same_handle_map_values(left: dict[Any, Any], right: dict[Any, Any]) -> bool:
    left_normalized = {getattr(key, "value", None): value for key, value in left.items()}
    right_normalized = {getattr(key, "value", None): value for key, value in right.items()}
    return left_normalized == right_normalized


def _try_set_timestamp_order(
    publisher_rti: Any,
    object_instance: Any,
    publisher_attr: Any,
    publisher_interaction: Any,
) -> None:
    try:
        publisher_rti.change_attribute_order_type(
            object_instance,
            {publisher_attr},
            OrderType.TIMESTAMP,
        )
    except UnsupportedBackendService:
        return
    publisher_rti.change_interaction_order_type(
        publisher_interaction,
        OrderType.TIMESTAMP,
    )


def run_two_federate_exchange_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: TwoFederateExchangeConfig,
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
    assert isinstance(publisher_handle, FederateHandle) or _is_handle_like(publisher_handle)
    assert isinstance(subscriber_handle, FederateHandle) or _is_handle_like(subscriber_handle)

    publisher_class = publisher_rti.get_object_class_handle(config.object_class_name)
    subscriber_class = subscriber_rti.get_object_class_handle(config.object_class_name)
    publisher_attr = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)
    subscriber_attr = subscriber_rti.get_attribute_handle(subscriber_class, config.attribute_name)
    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attr})
    subscriber_rti.subscribe_object_class_attributes(
        the_class=subscriber_class,
        attribute_list={subscriber_attr},
    )

    publisher_interaction = publisher_rti.get_interaction_class_handle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.get_interaction_class_handle(config.interaction_class_name)
    publisher_param = publisher_rti.get_parameter_handle(publisher_interaction, config.parameter_name)
    subscriber_param = subscriber_rti.get_parameter_handle(subscriber_interaction, config.parameter_name)
    publisher_rti.publish_interaction_class(publisher_interaction)
    subscriber_rti.subscribe_interaction_class(subscriber_interaction)
    drain_callbacks_pair(publisher_rti, subscriber_rti)

    discover_baseline = len(subscriber_federate.callbacks_named("discoverObjectInstance"))
    object_instance = register_named_object_instance(
        publisher_rti,
        publisher_federate,
        publisher_class,
        config.object_instance_name,
    )
    discovers = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "discoverObjectInstance",
        discover_baseline + 1,
        loops=120,
    )
    discover = discovers[-1] if len(discovers) > discover_baseline else None
    assert discover is not None
    discovered_object, discovered_class, discovered_name = discover.args[:3]
    assert _same_handle_value(discovered_class, subscriber_class)
    assert discovered_name == config.object_instance_name
    assert _same_handle_value(subscriber_rti.get_object_instance_handle(config.object_instance_name), discovered_object)
    assert _same_handle_value(subscriber_rti.get_known_object_class_handle(discovered_object), subscriber_class)

    reflect_baseline = len(subscriber_federate.callbacks_named("reflectAttributeValues"))
    publisher_rti.update_attribute_values(
        object_instance,
        {publisher_attr: config.attribute_payload},
        config.attribute_tag,
    )
    reflects = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "reflectAttributeValues",
        reflect_baseline + 1,
        loops=120,
    )
    reflect = next(
        (record for record in reflects[reflect_baseline:] if record.args[2] == config.attribute_tag),
        None,
    )
    assert reflect is not None
    assert _same_handle_value(reflect.args[0], discovered_object)
    assert _same_handle_map_values(reflect.args[1], {subscriber_attr: config.attribute_payload})
    assert reflect.args[2] == config.attribute_tag
    assert order_value(reflect.args[3]) == OrderType.RECEIVE.value
    assert int(reflect.args[4].value) >= 1

    interaction_baseline = len(subscriber_federate.callbacks_named("receiveInteraction"))
    publisher_rti.send_interaction(
        publisher_interaction,
        {publisher_param: config.interaction_payload},
        config.interaction_tag,
    )
    interactions = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "receiveInteraction",
        interaction_baseline + 1,
        loops=120,
    )
    interaction = next(
        (record for record in interactions[interaction_baseline:] if record.args[2] == config.interaction_tag),
        None,
    )
    assert interaction is not None
    assert _same_handle_value(interaction.args[0], subscriber_interaction)
    assert _same_handle_map_values(interaction.args[1], {subscriber_param: config.interaction_payload})
    assert interaction.args[2] == config.interaction_tag
    assert int(interaction.args[4].value) >= 1

    summary: dict[str, Any] = {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "object_instance": object_instance,
        "discovered_object": discovered_object,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attr,
        "subscriber_attribute": subscriber_attr,
        "publisher_interaction": publisher_interaction,
        "subscriber_interaction": subscriber_interaction,
        "publisher_parameter": publisher_param,
        "subscriber_parameter": subscriber_param,
        "discover": discover,
        "reflect": reflect,
        "interaction": interaction,
    }

    if config.enable_time_management:
        publisher_rti.enable_time_regulation(config.lookahead)
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

        _try_set_timestamp_order(
            publisher_rti,
            object_instance,
            publisher_attr,
            publisher_interaction,
        )
        drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

        timed_reflect_baseline = len(subscriber_federate.callbacks_named("reflectAttributeValues"))
        timed_interaction_baseline = len(subscriber_federate.callbacks_named("receiveInteraction"))
        publisher_rti.update_attribute_values(
            object_instance,
            {publisher_attr: config.timestamped_attribute_payload},
            config.timestamped_attribute_tag,
            config.timestamped_attribute_time,
        )
        publisher_rti.send_interaction(
            publisher_interaction,
            {publisher_param: config.timestamped_interaction_payload},
            config.timestamped_interaction_tag,
            config.timestamped_interaction_time,
        )
        publisher_rti.time_advance_request(config.advance_time)
        subscriber_rti.time_advance_request(config.advance_time)
        drain_callbacks_pair(publisher_rti, subscriber_rti, loops=120)

        timed_reflect_records = wait_for_callback_count_pair(
            publisher_rti,
            subscriber_rti,
            subscriber_federate,
            "reflectAttributeValues",
            timed_reflect_baseline + 1,
            loops=120,
        )
        timed_reflect = next(
            (
                record
                for record in timed_reflect_records[timed_reflect_baseline:]
                if record.args[2] == config.timestamped_attribute_tag
            ),
            None,
        )
        assert timed_reflect is not None
        assert _same_handle_map_values(timed_reflect.args[1], {subscriber_attr: config.timestamped_attribute_payload})
        assert timed_reflect.args[2] == config.timestamped_attribute_tag
        assert order_value(timed_reflect.args[3]) == OrderType.TIMESTAMP.value
        assert _same_handle_value(timed_reflect.args[5], config.timestamped_attribute_time)

        timed_interaction_records = wait_for_callback_count_pair(
            publisher_rti,
            subscriber_rti,
            subscriber_federate,
            "receiveInteraction",
            timed_interaction_baseline + 1,
            loops=120,
        )
        timed_interaction = next(
            (
                record
                for record in timed_interaction_records[timed_interaction_baseline:]
                if record.args[2] == config.timestamped_interaction_tag
            ),
            None,
        )
        assert timed_interaction is not None
        assert _same_handle_map_values(
            timed_interaction.args[1],
            {subscriber_param: config.timestamped_interaction_payload},
        )
        assert timed_interaction.args[2] == config.timestamped_interaction_tag
        assert order_value(timed_interaction.args[3]) == OrderType.TIMESTAMP.value
        assert _same_handle_value(timed_interaction.args[5], config.timestamped_interaction_time)

        advance_grant = wait_for_callback(
            subscriber_rti,
            subscriber_federate,
            "timeAdvanceGrant",
            loops=120,
        )
        assert advance_grant is not None
        assert _same_handle_value(advance_grant.args[0], config.advance_time)
        summary.update(
            {
                "time_regulation": time_regulation,
                "time_constrained": time_constrained,
                "timed_reflect": timed_reflect,
                "timed_interaction": timed_interaction,
                "advance_grant": advance_grant,
            }
        )

    remove_baseline = len(subscriber_federate.callbacks_named("removeObjectInstance"))
    try:
        publisher_rti.delete_object_instance(object_instance, config.delete_tag)
    except UnsupportedBackendService:
        publisher_rti.unconditional_attribute_ownership_divestiture(
            object_instance,
            {publisher_attr},
        )
        drain_callbacks_pair(publisher_rti, subscriber_rti, loops=24)
        summary["cleanup"] = "divest"
    else:
        removes = wait_for_callback_count_pair(
            publisher_rti,
            subscriber_rti,
            subscriber_federate,
            "removeObjectInstance",
            remove_baseline + 1,
            loops=120,
        )
        removed = next(
            (
                record
                for record in removes[remove_baseline:]
                if record.args[0] == discovered_object and record.args[1] == config.delete_tag
            ),
            None,
        )
        if removed is not None:
            summary["cleanup"] = "delete"
            summary["remove"] = removed
        else:
            # Real vendor runtimes can complete the exchange and time-managed
            # delivery path while still dropping the late remove callback during
            # teardown. Keep cleanup best-effort so the scenario reports the
            # exchange result rather than masking it with a teardown-only miss.
            drain_callbacks_pair(publisher_rti, subscriber_rti, loops=24)
            summary["cleanup"] = "delete-unconfirmed"
            summary["remove"] = None

    return summary


__all__ = [
    "ExchangeRoundConfig",
    "TwoFederateExchangeConfig",
    "assert_two_federate_exchange_callback_history",
    "run_exchange_round",
    "run_two_federate_exchange_scenario",
]
