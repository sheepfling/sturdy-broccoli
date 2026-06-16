"""Discovery-class verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516e.enums import CallbackModel

from .scenario_support import drain_callbacks_pair

HIERARCHY_FOM_XML = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Hierarchy Test FOM</name>
    <type>FOM</type>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Base</name>
        <attribute><name>Payload</name><dataType>HLAunicodeString</dataType></attribute>
        <objectClass>
          <name>Child</name>
          <attribute><name>Extra</name><dataType>HLAunicodeString</dataType></attribute>
        </objectClass>
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


def write_hierarchy_fom(path: Any) -> str:
    path.write_text(HIERARCHY_FOM_XML, encoding="utf-8")
    return str(path)


@dataclass(frozen=True)
class DiscoveryClassScenarioConfig:
    federation_name: str = "DiscoveryClassFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "DiscoveryClassFederate"
    subscriber_class_name: str = "HLAobjectRoot.Base"
    publisher_class_name: str = "HLAobjectRoot.Base.Child"
    attribute_name: str = "Payload"
    object_instance_name: str = "Hierarchy-1"
    attribute_payload: bytes = b"payload"
    attribute_tag: bytes = b"tag"


def run_discovery_class_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: DiscoveryClassScenarioConfig,
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

    subscriber_class = subscriber_rti.get_object_class_handle(config.subscriber_class_name)
    publisher_class = publisher_rti.get_object_class_handle(config.publisher_class_name)
    subscriber_attribute = subscriber_rti.get_attribute_handle(subscriber_class, config.attribute_name)
    publisher_attribute = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)

    subscriber_rti.subscribe_object_class_attributes(subscriber_class, {subscriber_attribute})
    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attribute})
    object_instance = publisher_rti.register_object_instance(publisher_class, config.object_instance_name)
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    discovery = subscriber_federate.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == object_instance
    assert discovery.args[1] == subscriber_class
    assert discovery.args[2] == config.object_instance_name
    assert subscriber_rti.get_known_object_class_handle(object_instance) == subscriber_class

    publisher_rti.update_attribute_values(
        object_instance,
        {publisher_attribute: config.attribute_payload},
        config.attribute_tag,
    )
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

    reflection = subscriber_federate.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[0] == object_instance
    assert reflection.args[1] == {subscriber_attribute: config.attribute_payload}
    assert subscriber_rti.get_known_object_class_handle(object_instance) == subscriber_class

    return {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attribute,
        "subscriber_attribute": subscriber_attribute,
        "object_instance": object_instance,
        "discovery": discovery,
        "reflection": reflection,
    }


__all__ = [
    "DiscoveryClassScenarioConfig",
    "run_discovery_class_scenario",
    "write_hierarchy_fom",
]
