"""Discovery metadata callback verification scenario."""
from __future__ import annotations

from typing import Any, Callable

from hla.rti1516e.handles import FederateHandle, ObjectClassHandle, ObjectInstanceHandle, RegionHandle, RegionHandleSet


def _handle_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _region_values(value: Any) -> tuple[Any, ...]:
    return tuple(sorted(_handle_value(item) for item in value))


def run_discovery_metadata_callback_scenario(
    invoke_discover_callback: Callable[..., Any],
    invoke_has_producing_federate_callback: Callable[..., Any],
    invoke_get_producing_federate_callback: Callable[..., Any],
    invoke_has_sent_regions_callback: Callable[..., Any],
    invoke_get_sent_regions_callback: Callable[..., Any],
    *,
    federate: Any,
    object_handle: ObjectInstanceHandle | None = None,
    object_class: ObjectClassHandle | None = None,
    object_name: str = "DiscoveryObject",
    producing_federate: FederateHandle | None = None,
    sent_regions: RegionHandleSet | None = None,
) -> dict[str, Any]:
    object_handle = object_handle or ObjectInstanceHandle(101)
    object_class = object_class or ObjectClassHandle(202)
    producing_federate = producing_federate or FederateHandle(303)
    sent_regions = sent_regions or RegionHandleSet({RegionHandle(11), RegionHandle(12)})

    invoke_discover_callback(object_handle, object_class, object_name, producing_federate)
    invoke_has_producing_federate_callback(object_handle, producing_federate)
    invoke_get_producing_federate_callback(object_handle, producing_federate)
    invoke_has_sent_regions_callback(object_handle, sent_regions)
    invoke_get_sent_regions_callback(object_handle, sent_regions)

    discover_record = federate.last_callback("discoverObjectInstance")
    has_producing_record = federate.last_callback("hasProducingFederate")
    get_producing_record = federate.last_callback("getProducingFederate")
    has_regions_record = federate.last_callback("hasSentRegions")
    get_regions_record = federate.last_callback("getSentRegions")

    assert discover_record is not None
    assert has_producing_record is not None
    assert get_producing_record is not None
    assert has_regions_record is not None
    assert get_regions_record is not None

    assert len(discover_record.args) == 4, discover_record.args
    assert isinstance(discover_record.args[0], ObjectInstanceHandle), discover_record.args
    assert isinstance(discover_record.args[1], ObjectClassHandle), discover_record.args
    assert discover_record.args[2] == object_name, discover_record.args
    assert isinstance(discover_record.args[3], FederateHandle), discover_record.args

    assert len(has_producing_record.args) == 2
    assert has_producing_record.args[0] == discover_record.args[0]
    assert has_producing_record.args[1] == discover_record.args[3]

    assert len(get_producing_record.args) == 2
    assert get_producing_record.args[0] == discover_record.args[0]
    assert get_producing_record.args[1] == discover_record.args[3]

    assert len(has_regions_record.args) == 2
    assert has_regions_record.args[0] == discover_record.args[0]
    assert len(_region_values(has_regions_record.args[1])) == len(_region_values(sent_regions)), has_regions_record.args

    assert len(get_regions_record.args) == 2
    assert get_regions_record.args[0] == discover_record.args[0]
    assert _region_values(get_regions_record.args[1]) == _region_values(has_regions_record.args[1]), (
        has_regions_record.args,
        get_regions_record.args,
    )

    return {
        "object_handle": object_handle,
        "object_class": object_class,
        "object_name": object_name,
        "producing_federate": producing_federate,
        "sent_regions": sent_regions,
        "discover_record": discover_record,
        "has_producing_record": has_producing_record,
        "get_producing_record": get_producing_record,
        "has_regions_record": has_regions_record,
        "get_regions_record": get_regions_record,
    }


__all__ = ["run_discovery_metadata_callback_scenario"]
