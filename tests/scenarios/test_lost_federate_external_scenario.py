from __future__ import annotations

from dataclasses import dataclass, field

from hla2010 import mom as hla_mom
from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010.enums import OrderType
from hla2010.exceptions import ObjectInstanceNotKnown
from hla2010.handles import AttributeHandle, FederateHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle, TransportationTypeHandle
from hla2010.ambassadors import invoke_federate_callback
from hla2010.time import HLAinteger64Time
from hla2010_verification_harness import (
    ExternalLostFederateVictimSession,
    LostFederateScenarioConfig,
    run_external_lost_federate_observer_scenario,
)


@dataclass
class _FakeObserverRTI:
    federate: RecordingFederateAmbassador | None = None
    queue: list[tuple[str, tuple[object, ...]]] = field(default_factory=list)
    object_removed: bool = False
    interaction_handle: InteractionClassHandle = field(default_factory=lambda: InteractionClassHandle(31))
    object_class_handle: ObjectClassHandle = field(default_factory=lambda: ObjectClassHandle(11))
    attribute_handle: AttributeHandle = field(default_factory=lambda: AttributeHandle(12))
    object_instance: ObjectInstanceHandle = field(default_factory=lambda: ObjectInstanceHandle(41))
    parameter_handles: dict[str, ParameterHandle] = field(
        default_factory=lambda: {
            "HLAfederate": ParameterHandle(51),
            "HLAfederateName": ParameterHandle(52),
            "HLAtimeStamp": ParameterHandle(53),
            "HLAfaultDescription": ParameterHandle(54),
        }
    )

    def connect(self, federate, callback_model):
        self.federate = federate

    def create_federation_execution(self, federation_name, fom_modules, logical_time_implementation_name):
        return None

    def createFederationExecution(self, federation_name, fom_modules, logical_time_implementation_name):  # noqa: N802
        return self.create_federation_execution(
            federation_name,
            fom_modules,
            logical_time_implementation_name,
        )

    def join_federation_execution(self, federate_name, federate_type, federation_name):
        return FederateHandle(1)

    def joinFederationExecution(self, federate_name, federate_type, federation_name):  # noqa: N802
        return self.join_federation_execution(federate_name, federate_type, federation_name)

    def get_object_class_handle(self, name):
        return self.object_class_handle

    def getObjectClassHandle(self, name):  # noqa: N802
        return self.get_object_class_handle(name)

    def get_attribute_handle(self, object_class, name):
        return self.attribute_handle

    def getAttributeHandle(self, object_class, name):  # noqa: N802
        return self.get_attribute_handle(object_class, name)

    def subscribe_object_class_attributes(self, object_class, attributes):
        return None

    def subscribeObjectClassAttributes(self, object_class, attributes):  # noqa: N802
        return self.subscribe_object_class_attributes(object_class, attributes)

    def get_interaction_class_handle(self, name):
        return self.interaction_handle

    def getInteractionClassHandle(self, name):  # noqa: N802
        return self.get_interaction_class_handle(name)

    def get_parameter_handle(self, interaction, name):
        return self.parameter_handles[name]

    def getParameterHandle(self, interaction, name):  # noqa: N802
        return self.get_parameter_handle(interaction, name)

    def subscribe_interaction_class(self, interaction):
        return None

    def subscribeInteractionClass(self, interaction):  # noqa: N802
        return self.subscribe_interaction_class(interaction)

    def evoke_multiple_callbacks(self, min_seconds, max_seconds):
        if not self.queue:
            return False
        method_name, args = self.queue.pop(0)
        invoke_federate_callback(self.federate, method_name, *args)
        return bool(self.queue)

    def evokeMultipleCallbacks(self, min_seconds, max_seconds):  # noqa: N802
        return self.evoke_multiple_callbacks(min_seconds, max_seconds)

    def request_attribute_value_update(self, object_instance, attributes, tag):
        if self.object_removed:
            raise ObjectInstanceNotKnown(repr(object_instance))
        return None

    def requestAttributeValueUpdate(self, object_instance, attributes, tag):  # noqa: N802
        return self.request_attribute_value_update(object_instance, attributes, tag)

    def resign_federation_execution(self, resign_action):
        return None

    def resignFederationExecution(self, resign_action):  # noqa: N802
        return self.resign_federation_execution(resign_action)

    def destroy_federation_execution(self, federation_name):
        return None

    def destroyFederationExecution(self, federation_name):  # noqa: N802
        return self.destroy_federation_execution(federation_name)

    def disconnect(self):
        return None


def test_external_lost_federate_observer_scenario_orchestrates_callbacks():
    observer = _FakeObserverRTI()
    observer_federate = RecordingFederateAmbassador()
    config = LostFederateScenarioConfig(
        federation_name="external-lost-fed",
        observer_name="Observer",
        victim_name="Victim",
        object_instance_name="lost-object",
        fault_description="external process killed",
    )
    victim_handle = FederateHandle(7)
    victim_time = HLAinteger64Time(0)

    def launch_victim(_config: LostFederateScenarioConfig) -> ExternalLostFederateVictimSession:
        observer.queue.append(
            (
                "discoverObjectInstance",
                (observer.object_instance, observer.object_class_handle, config.object_instance_name),
            )
        )

        def induce_loss() -> None:
            observer.queue.append(
                (
                    "receiveInteraction",
                    (
                        observer.interaction_handle,
                        {
                            observer.parameter_handles["HLAfederate"]: victim_handle.encode(),
                            observer.parameter_handles["HLAfederateName"]: hla_mom.encode_text(config.victim_name),
                            observer.parameter_handles["HLAtimeStamp"]: victim_time.encode(),
                            observer.parameter_handles["HLAfaultDescription"]: hla_mom.encode_text(config.fault_description),
                        },
                        b"lost",
                        OrderType.RECEIVE,
                        TransportationTypeHandle(1),
                        victim_time,
                    ),
                )
            )
            observer.queue.append(
                (
                    "removeObjectInstance",
                    (
                        observer.object_instance,
                        b"lost",
                        OrderType.RECEIVE,
                        victim_time,
                        None,
                        None,
                        type("Removed", (), {"producing_federate": victim_handle})(),
                    ),
                )
            )
            observer.object_removed = True

        return ExternalLostFederateVictimSession(
            victim_handle_bytes=victim_handle.encode(),
            victim_name=config.victim_name,
            victim_time_bytes=victim_time.encode(),
            induce_loss=induce_loss,
        )

    summary = run_external_lost_federate_observer_scenario(
        observer,
        config=config,
        observer_federate=observer_federate,
        launch_victim=launch_victim,
    )

    assert summary["discovery"].args[0] == observer.object_instance
    assert summary["loss_record"].args[1][observer.parameter_handles["HLAfederate"]] == victim_handle.encode()
    assert summary["removal"].args[0] == observer.object_instance
    assert isinstance(summary["object_instance_not_known"], ObjectInstanceNotKnown)
