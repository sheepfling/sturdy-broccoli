"""Shared lost-federate observer verification scenario."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from hla2010 import mom as hla_mom
from hla2010.enums import CallbackModel, ResignAction
from hla2010.exceptions import ObjectInstanceNotKnown

from .scenario_support import drain_callbacks, drain_callbacks_pair, register_named_object_instance, wait_for_callback


@dataclass(frozen=True)
class LostFederateScenarioConfig:
    federation_name: str = "LostFederateFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    observer_name: str = "Observer"
    victim_name: str = "Victim"
    federate_type: str = "LostFederateProbe"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "lost-object"
    fault_description: str = "simulated federate fault"
    automatic_resign_directive: ResignAction = ResignAction.DELETE_OBJECTS


@dataclass
class ExternalLostFederateVictimSession:
    victim_handle_bytes: bytes
    victim_name: str
    victim_time_bytes: bytes
    induce_loss: Callable[[], None]
    cleanup: Callable[[], None] = lambda: None
    describe: Callable[[], str] = lambda: ""


def run_lost_federate_mom_scenario(
    observer_rti: Any,
    victim_rti: Any,
    *,
    config: LostFederateScenarioConfig,
    observer_federate: Any,
    victim_federate: Any,
    induce_loss: Callable[[Any, str], None],
) -> dict[str, Any]:
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    victim_rti.connect(victim_federate, CallbackModel.HLA_EVOKED)
    observer_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    observer_handle = observer_rti.join_federation_execution(
        config.observer_name,
        config.federate_type,
        config.federation_name,
    )
    victim_handle = victim_rti.join_federation_execution(
        config.victim_name,
        config.federate_type,
        config.federation_name,
    )

    observer_object_class = observer_rti.get_object_class_handle(config.object_class_name)
    observer_attribute = observer_rti.get_attribute_handle(observer_object_class, config.attribute_name)
    observer_rti.subscribe_object_class_attributes(observer_object_class, {observer_attribute})

    lost_report = observer_rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFederateLost"
    )
    report_federate = observer_rti.get_parameter_handle(lost_report, "HLAfederate")
    report_federate_name = observer_rti.get_parameter_handle(lost_report, "HLAfederateName")
    report_timestamp = observer_rti.get_parameter_handle(lost_report, "HLAtimeStamp")
    report_fault = observer_rti.get_parameter_handle(lost_report, "HLAfaultDescription")
    observer_rti.subscribe_interaction_class(lost_report)

    victim_object_class = victim_rti.get_object_class_handle(config.object_class_name)
    victim_attribute = victim_rti.get_attribute_handle(victim_object_class, config.attribute_name)
    victim_rti.set_automatic_resign_directive(config.automatic_resign_directive)
    victim_rti.publish_object_class_attributes(victim_object_class, {victim_attribute})
    object_instance = register_named_object_instance(
        victim_rti,
        victim_federate,
        victim_object_class,
        config.object_instance_name,
    )
    drain_callbacks_pair(observer_rti, victim_rti, loops=24)

    discovery = wait_for_callback(observer_rti, observer_federate, "discoverObjectInstance", loops=120)
    assert discovery is not None
    assert discovery.args[2] == config.object_instance_name
    observed_object_instance = discovery.args[0]

    victim_time_before_loss = victim_rti.query_logical_time()
    induce_loss(victim_handle, config.fault_description)
    for _ in range(32):
        drain_callbacks(observer_rti)

    loss_record = wait_for_callback(observer_rti, observer_federate, "receiveInteraction", loops=120)
    assert loss_record is not None
    assert loss_record.args[0] == lost_report
    assert loss_record.args[1][report_federate] == victim_handle.encode()
    assert hla_mom.decode_text(loss_record.args[1][report_federate_name]) == config.victim_name
    assert loss_record.args[1][report_timestamp] == victim_time_before_loss.encode()
    assert hla_mom.decode_text(loss_record.args[1][report_fault]) == config.fault_description

    removal = wait_for_callback(observer_rti, observer_federate, "removeObjectInstance", loops=120)
    assert removal is not None
    assert removal.args[0] == observed_object_instance
    assert removal.args[1] == b"lost"
    assert removal.args[3].producing_federate == victim_handle

    try:
        observer_rti.request_attribute_value_update(observed_object_instance, {observer_attribute}, b"post-loss")
    except ObjectInstanceNotKnown as exc:
        object_instance_not_known = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected lost federate object to be removed under DELETE_OBJECTS automatic resign")
    finally:
        try:
            observer_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            victim_rti.disconnect()
        except Exception:
            pass
        try:
            observer_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            observer_rti.disconnect()
        except Exception:
            pass

    return {
        "observer_handle": observer_handle,
        "victim_handle": victim_handle,
        "object_instance": observed_object_instance,
        "discovery": discovery,
        "loss_record": loss_record,
        "removal": removal,
        "object_instance_not_known": object_instance_not_known,
    }


def run_external_lost_federate_observer_scenario(
    observer_rti: Any,
    *,
    config: LostFederateScenarioConfig,
    observer_federate: Any,
    launch_victim: Callable[[LostFederateScenarioConfig], ExternalLostFederateVictimSession],
) -> dict[str, Any]:
    observer_rti.connect(observer_federate, CallbackModel.HLA_EVOKED)
    observer_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    observer_handle = observer_rti.join_federation_execution(
        config.observer_name,
        config.federate_type,
        config.federation_name,
    )

    observer_object_class = observer_rti.get_object_class_handle(config.object_class_name)
    observer_attribute = observer_rti.get_attribute_handle(observer_object_class, config.attribute_name)
    observer_rti.subscribe_object_class_attributes(observer_object_class, {observer_attribute})

    lost_report = observer_rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFederateLost"
    )
    report_federate = observer_rti.get_parameter_handle(lost_report, "HLAfederate")
    report_federate_name = observer_rti.get_parameter_handle(lost_report, "HLAfederateName")
    report_timestamp = observer_rti.get_parameter_handle(lost_report, "HLAtimeStamp")
    report_fault = observer_rti.get_parameter_handle(lost_report, "HLAfaultDescription")
    observer_rti.subscribe_interaction_class(lost_report)

    victim_session = launch_victim(config)
    try:
        discovery = wait_for_callback(observer_rti, observer_federate, "discoverObjectInstance", loops=120)
        assert discovery is not None
        assert discovery.args[2] == config.object_instance_name
        object_instance = discovery.args[0]

        victim_session.induce_loss()

        loss_record = wait_for_callback(observer_rti, observer_federate, "receiveInteraction", loops=320)
        assert loss_record is not None, victim_session.describe()
        assert loss_record.args[0] == lost_report
        assert loss_record.args[1][report_federate] == victim_session.victim_handle_bytes
        assert hla_mom.decode_text(loss_record.args[1][report_federate_name]) == victim_session.victim_name
        assert loss_record.args[1][report_timestamp] == victim_session.victim_time_bytes
        assert hla_mom.decode_text(loss_record.args[1][report_fault]) == config.fault_description

        removal = wait_for_callback(observer_rti, observer_federate, "removeObjectInstance", loops=320)
        assert removal is not None, victim_session.describe()
        assert removal.args[0] == object_instance
        assert removal.args[1] == b"lost"

        try:
            observer_rti.request_attribute_value_update(object_instance, {observer_attribute}, b"post-loss")
        except ObjectInstanceNotKnown as exc:
            object_instance_not_known = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected lost federate object to be removed under DELETE_OBJECTS automatic resign")
    finally:
        try:
            victim_session.cleanup()
        except Exception:
            pass
        try:
            observer_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            observer_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            observer_rti.disconnect()
        except Exception:
            pass

    return {
        "observer_handle": observer_handle,
        "object_instance": object_instance,
        "discovery": discovery,
        "loss_record": loss_record,
        "removal": removal,
        "object_instance_not_known": object_instance_not_known,
    }


__all__ = [
    "ExternalLostFederateVictimSession",
    "LostFederateScenarioConfig",
    "run_external_lost_federate_observer_scenario",
    "run_lost_federate_mom_scenario",
]
