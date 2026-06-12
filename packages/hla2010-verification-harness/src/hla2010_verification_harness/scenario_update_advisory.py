"""Update-advisory callback verification scenario."""
from __future__ import annotations

from typing import Any, Callable

from hla2010.handles import AttributeHandle, ObjectInstanceHandle


def _handle_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _attribute_values(value: Any) -> tuple[Any, ...]:
    return tuple(sorted(_handle_value(item) for item in value))


def run_update_advisory_callback_scenario(
    invoke_attributes_in_scope_callback: Callable[..., Any],
    invoke_attributes_out_of_scope_callback: Callable[..., Any],
    invoke_provide_attribute_value_update_callback: Callable[..., Any],
    invoke_turn_updates_on_callback: Callable[..., Any],
    invoke_turn_updates_off_callback: Callable[..., Any],
    *,
    federate: Any,
    object_handle: ObjectInstanceHandle | None = None,
    attribute_handle: AttributeHandle | None = None,
    tag: bytes = b"update-advisory",
    designator: str = "HLAdefault",
) -> dict[str, Any]:
    object_handle = object_handle or ObjectInstanceHandle(404)
    attribute_handle = attribute_handle or AttributeHandle(505)
    attributes = {attribute_handle}

    invoke_attributes_in_scope_callback(object_handle, attributes)
    invoke_attributes_out_of_scope_callback(object_handle, attributes)
    invoke_provide_attribute_value_update_callback(object_handle, attributes, tag)
    invoke_turn_updates_on_callback(object_handle, attributes, designator)
    invoke_turn_updates_off_callback(object_handle, attributes)

    in_scope_record = federate.last_callback("attributesInScope")
    out_of_scope_record = federate.last_callback("attributesOutOfScope")
    provide_record = federate.last_callback("provideAttributeValueUpdate")
    turn_on_record = federate.last_callback("turnUpdatesOnForObjectInstance")
    turn_off_record = federate.last_callback("turnUpdatesOffForObjectInstance")

    assert in_scope_record is not None
    assert out_of_scope_record is not None
    assert provide_record is not None
    assert turn_on_record is not None
    assert turn_off_record is not None

    assert len(in_scope_record.args) == 2
    assert isinstance(in_scope_record.args[0], ObjectInstanceHandle)
    assert len(_attribute_values(in_scope_record.args[1])) == len(_attribute_values(attributes))

    assert len(out_of_scope_record.args) == 2
    assert out_of_scope_record.args[0] == in_scope_record.args[0]
    assert _attribute_values(out_of_scope_record.args[1]) == _attribute_values(in_scope_record.args[1])

    assert len(provide_record.args) == 3
    assert provide_record.args[0] == in_scope_record.args[0]
    assert _attribute_values(provide_record.args[1]) == _attribute_values(in_scope_record.args[1])
    assert provide_record.args[2] == tag

    assert len(turn_on_record.args) == 3
    assert turn_on_record.args[0] == in_scope_record.args[0]
    assert _attribute_values(turn_on_record.args[1]) == _attribute_values(in_scope_record.args[1])
    assert turn_on_record.args[2] == designator

    assert len(turn_off_record.args) == 2
    assert turn_off_record.args[0] == in_scope_record.args[0]
    assert _attribute_values(turn_off_record.args[1]) == _attribute_values(in_scope_record.args[1])

    return {
        "object_handle": object_handle,
        "attributes": attributes,
        "tag": tag,
        "designator": designator,
        "in_scope_record": in_scope_record,
        "out_of_scope_record": out_of_scope_record,
        "provide_record": provide_record,
        "turn_on_record": turn_on_record,
        "turn_off_record": turn_off_record,
    }


__all__ = ["run_update_advisory_callback_scenario"]
