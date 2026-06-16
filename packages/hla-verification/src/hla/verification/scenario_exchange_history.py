"""History assertions and incremental rounds for exchange scenarios."""
from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516e.enums import OrderType
from .scenario_support import advance_time_beyond, order_value, wait_for_callback_count_pair
from .scenario_exchange_types import ExchangeRoundConfig, TwoFederateExchangeConfig


def assert_two_federate_exchange_callback_history(
    summary: Mapping[str, Any],
    *,
    publisher_federate: Any,
    subscriber_federate: Any,
    config: TwoFederateExchangeConfig,
    require_timed_delivery: bool = True,
) -> dict[str, Any]:
    discovers = subscriber_federate.callbacks_named("discoverObjectInstance")
    reflects = subscriber_federate.callbacks_named("reflectAttributeValues")
    interactions = subscriber_federate.callbacks_named("receiveInteraction")
    time_regulations = publisher_federate.callbacks_named("timeRegulationEnabled")
    time_constrained = subscriber_federate.callbacks_named("timeConstrainedEnabled")
    grants = subscriber_federate.callbacks_named("timeAdvanceGrant")
    receive_reflect = next(record for record in reflects if record.args[2] == config.attribute_tag)
    receive_interaction = next(record for record in interactions if record.args[2] == config.interaction_tag)

    assert len(discovers) == 1
    assert len(reflects) >= 1
    assert len(interactions) >= 1
    if config.enable_time_management:
        assert len(time_regulations) == 1
        assert len(time_constrained) == 1
    assert discovers[0].args[2] == config.object_instance_name
    assert receive_reflect.args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert receive_reflect.args[2] == config.attribute_tag
    assert receive_reflect.args[3] is OrderType.RECEIVE
    assert receive_interaction.args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert receive_interaction.args[2] == config.interaction_tag

    timestamp_reflect = None
    timestamp_interaction = None
    if require_timed_delivery:
        timestamp_reflect = next(record for record in reflects if record.args[2] == config.timestamped_attribute_tag)
        timestamp_interaction = next(record for record in interactions if record.args[2] == config.timestamped_interaction_tag)
        assert len(reflects) >= 2
        assert len(interactions) >= 2
        assert timestamp_reflect.args[1] == {summary["subscriber_attribute"]: config.timestamped_attribute_payload}
        assert timestamp_reflect.args[2] == config.timestamped_attribute_tag
        assert timestamp_reflect.args[3] is OrderType.TIMESTAMP
        assert timestamp_reflect.args[5] == config.timestamped_attribute_time
        assert timestamp_interaction.args[1] == {summary["subscriber_parameter"]: config.timestamped_interaction_payload}
        assert timestamp_interaction.args[2] == config.timestamped_interaction_tag
        assert timestamp_interaction.args[3] is OrderType.TIMESTAMP
        assert timestamp_interaction.args[5] == config.timestamped_interaction_time

    if config.enable_time_management:
        assert time_regulations[0] == summary["time_regulation"]
        assert time_constrained[0] == summary["time_constrained"]
        assert grants[-1].args[0] == config.advance_time

    return {
        "discovers": discovers,
        "reflects": reflects,
        "interactions": interactions,
        "time_regulations": time_regulations,
        "time_constrained": time_constrained,
        "grants": grants,
        "receive_reflect": receive_reflect,
        "timestamp_reflect": timestamp_reflect,
        "receive_interaction": receive_interaction,
        "timestamp_interaction": timestamp_interaction,
    }


def run_exchange_round(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    summary: Mapping[str, Any],
    subscriber_federate: Any,
    config: ExchangeRoundConfig,
) -> dict[str, Any]:
    baseline_reflects = len(subscriber_federate.callbacks_named("reflectAttributeValues"))
    baseline_interactions = len(subscriber_federate.callbacks_named("receiveInteraction"))

    if config.attribute_time is None:
        publisher_rti.update_attribute_values(
            summary["object_instance"],
            {summary["publisher_attribute"]: config.attribute_payload},
            config.attribute_tag,
        )
    else:
        publisher_rti.update_attribute_values(
            summary["object_instance"],
            {summary["publisher_attribute"]: config.attribute_payload},
            config.attribute_tag,
            config.attribute_time,
        )

    if config.interaction_time is None:
        publisher_rti.send_interaction(
            summary["publisher_interaction"],
            {summary["publisher_parameter"]: config.interaction_payload},
            config.interaction_tag,
        )
    else:
        publisher_rti.send_interaction(
            summary["publisher_interaction"],
            {summary["publisher_parameter"]: config.interaction_payload},
            config.interaction_tag,
            config.interaction_time,
        )

    if config.attribute_time is not None or config.interaction_time is not None:
        target_time = config.interaction_time if config.interaction_time is not None else config.attribute_time
        advance_time_beyond(publisher_rti, subscriber_rti, target_time)

    reflect_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "reflectAttributeValues",
        baseline_reflects + 1,
    )
    latest_reflect = reflect_records[-1]
    assert latest_reflect.args[0] == summary["discovered_object"]
    assert latest_reflect.args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert latest_reflect.args[2] == config.attribute_tag
    expected_reflect_order = OrderType.TIMESTAMP if config.attribute_time is not None else OrderType.RECEIVE
    assert order_value(latest_reflect.args[3]) == expected_reflect_order.value
    if config.attribute_time is not None:
        assert latest_reflect.args[5] == config.attribute_time

    interaction_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "receiveInteraction",
        baseline_interactions + 1,
    )
    latest_interaction = interaction_records[-1]
    assert latest_interaction.args[0] == summary["subscriber_interaction"]
    assert latest_interaction.args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert latest_interaction.args[2] == config.interaction_tag
    expected_interaction_order = OrderType.TIMESTAMP if config.interaction_time is not None else OrderType.RECEIVE
    assert order_value(latest_interaction.args[3]) == expected_interaction_order.value
    if config.interaction_time is not None:
        assert latest_interaction.args[5] == config.interaction_time

    return {
        "reflect": latest_reflect,
        "interaction": latest_interaction,
        "reflect_count": len(reflect_records),
        "interaction_count": len(interaction_records),
    }
