"""Shared resign-precondition verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516_2025.exceptions import (
    FederateNotExecutionMember as FederateNotExecutionMember2025,
)
from hla.rti1516_2025.exceptions import (
    FederateOwnsAttributes as FederateOwnsAttributes2025,
)
from hla.rti1516_2025.exceptions import (
    InvalidResignAction as InvalidResignAction2025,
)
from hla.rti1516_2025.exceptions import (
    NotConnected as NotConnected2025,
)
from hla.rti1516_2025.exceptions import (
    ObjectInstanceNotKnown as ObjectInstanceNotKnown2025,
)
from hla.rti1516_2025.exceptions import (
    OwnershipAcquisitionPending as OwnershipAcquisitionPending2025,
)
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.rti1516e.exceptions import (
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    InvalidResignAction,
    NotConnected,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
)

from .scenario_support import drain_callbacks_pair, register_named_object_instance, wait_for_callback


def _payload_value_by_handle(payload: dict[Any, bytes], expected_handle: Any) -> bytes | None:
    expected_value = getattr(expected_handle, "value", None)
    for handle, value in payload.items():
        if getattr(handle, "value", None) == expected_value:
            return value
    return None


@dataclass(frozen=True)
class ResignScenarioConfig:
    federation_name: str = "ResignFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    federate_type: str = "ResignFederate"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "Pending-Acquisition"


def run_resign_precondition_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: ResignScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    try:
        leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
    except (NotConnected, NotConnected2025) as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
    except (FederateNotExecutionMember, FederateNotExecutionMember2025) as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    object_class = leader_rti.get_object_class_handle(config.object_class_name)
    attribute = leader_rti.get_attribute_handle(object_class, config.attribute_name)
    leader_rti.publish_object_class_attributes(object_class, {attribute})
    wing_rti.publish_object_class_attributes(object_class, {attribute})
    object_instance = register_named_object_instance(
        leader_rti,
        leader_federate,
        object_class,
        config.object_instance_name,
    )

    try:
        leader_rti.resign_federation_execution("bogus")
    except (InvalidResignAction, InvalidResignAction2025) as exc:
        invalid_action = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to reject an invalid resign action")

    try:
        leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
    except (FederateOwnsAttributes, FederateOwnsAttributes2025) as exc:
        owns_attributes = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to reject owned attributes without divest/delete")

    wing_rti.attribute_ownership_acquisition(object_instance, {attribute}, b"req")
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    try:
        wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
    except (OwnershipAcquisitionPending, OwnershipAcquisitionPending2025) as exc:
        acquisition_pending = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to reject pending ownership acquisition")
    finally:
        try:
            leader_rti.attribute_ownership_release_denied(object_instance, {attribute})
        except Exception:
            pass
        try:
            leader_rti.resign_federation_execution(ResignAction.DELETE_OBJECTS)
        except Exception:
            pass
        try:
            wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            leader_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            wing_rti.disconnect()
        except Exception:
            pass
        try:
            leader_rti.disconnect()
        except Exception:
            pass

    return {
        "not_connected": not_connected,
        "not_joined": not_joined,
        "invalid_action": invalid_action,
        "owns_attributes": owns_attributes,
        "acquisition_pending": acquisition_pending,
        "object_instance": object_instance,
        "attribute": attribute,
    }


def run_resign_mom_cleanup_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: ResignScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    federation_class = leader_rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederation")
    federation_members = leader_rti.get_attribute_handle(federation_class, "HLAfederatesInFederation")
    federate_class = leader_rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederate")
    federate_name = leader_rti.get_attribute_handle(federate_class, "HLAfederateName")

    leader_rti.subscribe_object_class_attributes(federation_class, {federation_members})
    leader_rti.subscribe_object_class_attributes(federate_class, {federate_name})
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)

    wing_discoveries = [
        record for record in leader_federate.callbacks_named("discoverObjectInstance") if record.args[2].endswith(f".{config.wing_name}")
    ]
    assert wing_discoveries
    wing_mom_object = wing_discoveries[-1].args[0]

    leader_rti.request_attribute_value_update(wing_mom_object, {federate_name}, b"wing-before-resign")
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)
    wing_before = wait_for_callback(leader_rti, leader_federate, "reflectAttributeValues", loops=120)
    assert wing_before is not None
    assert wing_before.args[0] == wing_mom_object
    assert _payload_value_by_handle(wing_before.args[1], federate_name) == config.wing_name.encode()

    wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)

    leader_rti.request_attribute_value_update(federation_class, {federation_members}, b"after-resign-members")
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)
    federation_after = wait_for_callback(leader_rti, leader_federate, "reflectAttributeValues", loops=120)
    assert federation_after is not None
    assert federation_after.args[0] != wing_mom_object
    assert _payload_value_by_handle(federation_after.args[1], federation_members) == config.leader_name.encode()

    try:
        leader_rti.request_attribute_value_update(wing_mom_object, {federate_name}, b"wing-after-resign")
    except (ObjectInstanceNotKnown, ObjectInstanceNotKnown2025) as exc:
        object_instance_not_known = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resigned MOM federate object to become unknown to observer updates")
    finally:
        try:
            leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            leader_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            wing_rti.disconnect()
        except Exception:
            pass
        try:
            leader_rti.disconnect()
        except Exception:
            pass

    return {
        "wing_mom_object": wing_mom_object,
        "wing_before": wing_before,
        "federation_after": federation_after,
        "object_instance_not_known": object_instance_not_known,
    }


def run_disconnect_mom_cleanup_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: ResignScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    federation_class = wing_rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederation")
    federation_members = wing_rti.get_attribute_handle(federation_class, "HLAfederatesInFederation")
    federate_class = wing_rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederate")
    federate_name = wing_rti.get_attribute_handle(federate_class, "HLAfederateName")

    wing_rti.subscribe_object_class_attributes(federation_class, {federation_members})
    wing_rti.subscribe_object_class_attributes(federate_class, {federate_name})
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)

    leader_discoveries = [
        record for record in wing_federate.callbacks_named("discoverObjectInstance") if record.args[2].endswith(f".{config.leader_name}")
    ]
    assert leader_discoveries
    leader_mom_object = leader_discoveries[-1].args[0]

    wing_rti.request_attribute_value_update(leader_mom_object, {federate_name}, b"leader-before-disconnect")
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)
    leader_before = wait_for_callback(wing_rti, wing_federate, "reflectAttributeValues", loops=120)
    assert leader_before is not None
    assert leader_before.args[0] == leader_mom_object
    assert _payload_value_by_handle(leader_before.args[1], federate_name) == config.leader_name.encode()

    leader_rti.resign_federation_execution(ResignAction.NO_ACTION)
    leader_rti.disconnect()
    for _ in range(24):
        drain_callbacks_pair(wing_rti, loops=1)

    wing_rti.request_attribute_value_update(federation_class, {federation_members}, b"after-disconnect-members")
    for _ in range(24):
        drain_callbacks_pair(wing_rti, loops=1)
    federation_after = wait_for_callback(wing_rti, wing_federate, "reflectAttributeValues", loops=120)
    assert federation_after is not None
    assert federation_after.args[0] != leader_mom_object
    assert _payload_value_by_handle(federation_after.args[1], federation_members) == config.wing_name.encode()

    try:
        wing_rti.request_attribute_value_update(leader_mom_object, {federate_name}, b"leader-after-disconnect")
    except (ObjectInstanceNotKnown, ObjectInstanceNotKnown2025) as exc:
        object_instance_not_known = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected disconnected federate MOM object to become unknown to observer updates")
    finally:
        try:
            wing_rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            wing_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            wing_rti.disconnect()
        except Exception:
            pass

    return {
        "leader_mom_object": leader_mom_object,
        "leader_before": leader_before,
        "federation_after": federation_after,
        "object_instance_not_known": object_instance_not_known,
    }


__all__ = [
    "ResignScenarioConfig",
    "run_disconnect_mom_cleanup_scenario",
    "run_resign_mom_cleanup_scenario",
    "run_resign_precondition_scenario",
]
