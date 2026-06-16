"""Update-rate verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.enums import CallbackModel

from .scenario_support import drain_callbacks_pair

UPDATE_RATE_FOM_XML = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Update Rate Test FOM</name>
    <type>FOM</type>
  </modelIdentification>
  <updateRates>
    <updateRate><name>HLAdefault</name><rate>0.0</rate></updateRate>
    <updateRate><name>Fast</name><rate>2.0</rate></updateRate>
  </updateRates>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RateObject</name>
        <attribute><name>Payload</name><dataType>HLAunicodeString</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dataTypes>
    <basicDataRepresentations>
      <basicData representation="HLAunicodeString"/>
    </basicDataRepresentations>
  </dataTypes>
</objectModel>
"""


def write_update_rate_fom(path: Any) -> str:
    path.write_text(UPDATE_RATE_FOM_XML, encoding="utf-8")
    return str(path)


@dataclass(frozen=True)
class UpdateRateScenarioConfig:
    federation_name: str = "UpdateRateFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "UpdateRateFederate"
    object_class_name: str = "HLAobjectRoot.RateObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "Rate-1"
    update_rate_designator: str = "Fast"
    timestamp_1: float = 1.0
    timestamp_2: float = 1.2
    timestamp_3: float = 1.6
    advance_time: float = 2.0


def run_update_rate_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: UpdateRateScenarioConfig,
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

    object_class = publisher_rti.get_object_class_handle(config.object_class_name)
    attribute = publisher_rti.get_attribute_handle(object_class, config.attribute_name)
    subscriber_class = subscriber_rti.get_object_class_handle(config.object_class_name)
    subscriber_attribute = subscriber_rti.get_attribute_handle(subscriber_class, config.attribute_name)
    time_factory = publisher_rti.get_time_factory()

    publisher_rti.publish_object_class_attributes(object_class, {attribute})
    subscriber_rti.subscribe_object_class_attributes(
        subscriber_class,
        {subscriber_attribute},
        config.update_rate_designator,
    )
    publisher_rti.enable_time_regulation(time_factory.make_interval(0.1))
    subscriber_rti.enable_time_constrained()
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    object_instance = publisher_rti.register_object_instance(object_class, config.object_instance_name)
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)
    subscriber_federate.clear()

    publisher_rti.update_attribute_values(
        object_instance,
        {attribute: b"t1"},
        b"tag1",
        time_factory.make_time(config.timestamp_1),
    )
    publisher_rti.update_attribute_values(
        object_instance,
        {attribute: b"t12"},
        b"tag12",
        time_factory.make_time(config.timestamp_2),
    )
    publisher_rti.update_attribute_values(
        object_instance,
        {attribute: b"t16"},
        b"tag16",
        time_factory.make_time(config.timestamp_3),
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    publisher_rti.time_advance_request(time_factory.make_time(config.advance_time))
    subscriber_rti.next_message_request_available(time_factory.make_time(config.advance_time))
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)
    subscriber_rti.next_message_request_available(time_factory.make_time(config.advance_time))
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    reflections = subscriber_federate.callbacks_named("reflectAttributeValues")
    values = [record.args[1][subscriber_attribute] for record in reflections]
    assert values == [b"t1", b"t16"]
    assert subscriber_rti.get_update_rate_value(config.update_rate_designator) == 2.0

    return {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "object_instance": object_instance,
        "subscriber_attribute": subscriber_attribute,
        "reflections": reflections,
        "values": values,
    }


__all__ = [
    "UpdateRateScenarioConfig",
    "run_update_rate_scenario",
    "write_update_rate_fom",
]
