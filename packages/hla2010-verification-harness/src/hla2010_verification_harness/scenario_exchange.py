"""Two-federate exchange scenario root."""
from __future__ import annotations

from typing import Any

from hla2010.enums import CallbackModel, OrderType
from hla2010.handles import FederateHandle
from hla2010_rti_backend_common import UnsupportedBackendService
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


def _try_set_timestamp_order(
    publisher_rti: Any,
    object_instance: Any,
    publisher_attr: Any,
    publisher_interaction: Any,
) -> None:
    try:
        publisher_rti.changeAttributeOrderType(
            object_instance,
            {publisher_attr},
            OrderType.TIMESTAMP,
        )
    except UnsupportedBackendService:
        return
    publisher_rti.changeInteractionOrderType(
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
    publisher_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.joinFederationExecution(
        config.publisher_name,
        config.federate_type,
        config.federation_name,
    )
    subscriber_handle = subscriber_rti.joinFederationExecution(
        config.subscriber_name,
        config.federate_type,
        config.federation_name,
    )
    assert isinstance(publisher_handle, FederateHandle)
    assert isinstance(subscriber_handle, FederateHandle)

    publisher_class = publisher_rti.getObjectClassHandle(config.object_class_name)
    subscriber_class = subscriber_rti.getObjectClassHandle(config.object_class_name)
    publisher_attr = publisher_rti.getAttributeHandle(publisher_class, config.attribute_name)
    subscriber_attr = subscriber_rti.getAttributeHandle(subscriber_class, config.attribute_name)
    publisher_rti.publishObjectClassAttributes(publisher_class, {publisher_attr})
    subscriber_rti.subscribeObjectClassAttributes(
        the_class=subscriber_class,
        attribute_list={subscriber_attr},
    )

    publisher_interaction = publisher_rti.getInteractionClassHandle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.getInteractionClassHandle(config.interaction_class_name)
    publisher_param = publisher_rti.getParameterHandle(publisher_interaction, config.parameter_name)
    subscriber_param = subscriber_rti.getParameterHandle(subscriber_interaction, config.parameter_name)
    publisher_rti.publishInteractionClass(publisher_interaction)
    subscriber_rti.subscribeInteractionClass(subscriber_interaction)
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
    assert discovered_class == subscriber_class
    assert discovered_name == config.object_instance_name
    assert subscriber_rti.getObjectInstanceHandle(config.object_instance_name) == discovered_object
    assert subscriber_rti.getKnownObjectClassHandle(discovered_object) == subscriber_class

    reflect_baseline = len(subscriber_federate.callbacks_named("reflectAttributeValues"))
    publisher_rti.updateAttributeValues(
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
    assert reflect.args[0] == discovered_object
    assert reflect.args[1] == {subscriber_attr: config.attribute_payload}
    assert reflect.args[2] == config.attribute_tag
    assert order_value(reflect.args[3]) == OrderType.RECEIVE.value
    assert int(reflect.args[4].value) >= 1

    interaction_baseline = len(subscriber_federate.callbacks_named("receiveInteraction"))
    publisher_rti.sendInteraction(
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
    assert interaction.args[0] == subscriber_interaction
    assert interaction.args[1] == {subscriber_param: config.interaction_payload}
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
        publisher_rti.enableTimeRegulation(config.lookahead)
        subscriber_rti.enableTimeConstrained()
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
        publisher_rti.updateAttributeValues(
            object_instance,
            {publisher_attr: config.timestamped_attribute_payload},
            config.timestamped_attribute_tag,
            config.timestamped_attribute_time,
        )
        publisher_rti.sendInteraction(
            publisher_interaction,
            {publisher_param: config.timestamped_interaction_payload},
            config.timestamped_interaction_tag,
            config.timestamped_interaction_time,
        )
        publisher_rti.timeAdvanceRequest(config.advance_time)
        subscriber_rti.timeAdvanceRequest(config.advance_time)
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
        assert timed_reflect.args[1] == {subscriber_attr: config.timestamped_attribute_payload}
        assert timed_reflect.args[2] == config.timestamped_attribute_tag
        assert order_value(timed_reflect.args[3]) == OrderType.TIMESTAMP.value
        assert timed_reflect.args[5] == config.timestamped_attribute_time

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
        assert timed_interaction.args[1] == {
            subscriber_param: config.timestamped_interaction_payload
        }
        assert timed_interaction.args[2] == config.timestamped_interaction_tag
        assert order_value(timed_interaction.args[3]) == OrderType.TIMESTAMP.value
        assert timed_interaction.args[5] == config.timestamped_interaction_time

        advance_grant = wait_for_callback(
            subscriber_rti,
            subscriber_federate,
            "timeAdvanceGrant",
            loops=120,
        )
        assert advance_grant is not None
        assert advance_grant.args[0] == config.advance_time
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
        publisher_rti.deleteObjectInstance(object_instance, config.delete_tag)
    except UnsupportedBackendService:
        publisher_rti.unconditionalAttributeOwnershipDivestiture(
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
