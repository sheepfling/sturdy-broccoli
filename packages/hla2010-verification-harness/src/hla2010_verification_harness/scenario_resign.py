"""Shared resign-precondition verification scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla2010.enums import CallbackModel, ResignAction
from hla2010.exceptions import (
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    InvalidResignAction,
    NotConnected,
    ObjectInstanceNotKnown,
    OwnershipAcquisitionPending,
)

from .scenario_support import drain_callbacks_pair, register_named_object_instance, wait_for_callback


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
        leader_rti.resignFederationExecution(ResignAction.NO_ACTION)
    except NotConnected as exc:
        not_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to raise NotConnected before connect")

    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.resignFederationExecution(ResignAction.NO_ACTION)
    except FederateNotExecutionMember as exc:
        not_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to raise FederateNotExecutionMember before join")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.joinFederationExecution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.joinFederationExecution(config.wing_name, config.federate_type, config.federation_name)

    object_class = leader_rti.getObjectClassHandle(config.object_class_name)
    attribute = leader_rti.getAttributeHandle(object_class, config.attribute_name)
    leader_rti.publishObjectClassAttributes(object_class, {attribute})
    wing_rti.publishObjectClassAttributes(object_class, {attribute})
    object_instance = register_named_object_instance(
        leader_rti,
        leader_federate,
        object_class,
        config.object_instance_name,
    )

    try:
        leader_rti.resignFederationExecution("bogus")
    except InvalidResignAction as exc:
        invalid_action = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to reject an invalid resign action")

    try:
        leader_rti.resignFederationExecution(ResignAction.NO_ACTION)
    except FederateOwnsAttributes as exc:
        owns_attributes = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to reject owned attributes without divest/delete")

    wing_rti.attributeOwnershipAcquisition(object_instance, {attribute}, b"req")
    drain_callbacks_pair(leader_rti, wing_rti, loops=16)
    try:
        wing_rti.resignFederationExecution(ResignAction.NO_ACTION)
    except OwnershipAcquisitionPending as exc:
        acquisition_pending = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resign_federation_execution to reject pending ownership acquisition")
    finally:
        try:
            leader_rti.attributeOwnershipReleaseDenied(object_instance, {attribute})
        except Exception:
            pass
        try:
            leader_rti.resignFederationExecution(ResignAction.DELETE_OBJECTS)
        except Exception:
            pass
        try:
            wing_rti.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            leader_rti.destroyFederationExecution(config.federation_name)
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
    leader_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.joinFederationExecution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.joinFederationExecution(config.wing_name, config.federate_type, config.federation_name)

    federation_class = leader_rti.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederation")
    federation_members = leader_rti.getAttributeHandle(federation_class, "HLAfederatesInFederation")
    federate_class = leader_rti.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederate")
    federate_name = leader_rti.getAttributeHandle(federate_class, "HLAfederateName")

    leader_rti.subscribeObjectClassAttributes(federation_class, {federation_members})
    leader_rti.subscribeObjectClassAttributes(federate_class, {federate_name})
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)

    wing_discoveries = [
        record for record in leader_federate.callbacks_named("discoverObjectInstance") if record.args[2].endswith(f".{config.wing_name}")
    ]
    assert wing_discoveries
    wing_mom_object = wing_discoveries[-1].args[0]

    leader_rti.requestAttributeValueUpdate(wing_mom_object, {federate_name}, b"wing-before-resign")
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)
    wing_before = wait_for_callback(leader_rti, leader_federate, "reflectAttributeValues", loops=120)
    assert wing_before is not None
    assert wing_before.args[0] == wing_mom_object
    assert wing_before.args[1][federate_name] == config.wing_name.encode()

    wing_rti.resignFederationExecution(ResignAction.NO_ACTION)
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)

    leader_rti.requestAttributeValueUpdate(federation_class, {federation_members}, b"after-resign-members")
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)
    federation_after = wait_for_callback(leader_rti, leader_federate, "reflectAttributeValues", loops=120)
    assert federation_after is not None
    assert federation_after.args[0] != wing_mom_object
    assert federation_members in federation_after.args[1]
    assert federation_after.args[1][federation_members] == config.leader_name.encode()

    try:
        leader_rti.requestAttributeValueUpdate(wing_mom_object, {federate_name}, b"wing-after-resign")
    except ObjectInstanceNotKnown as exc:
        object_instance_not_known = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected resigned MOM federate object to become unknown to observer updates")
    finally:
        try:
            leader_rti.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            leader_rti.destroyFederationExecution(config.federation_name)
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
    leader_rti.createFederationExecution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_rti.joinFederationExecution(config.leader_name, config.federate_type, config.federation_name)
    wing_rti.joinFederationExecution(config.wing_name, config.federate_type, config.federation_name)

    federation_class = wing_rti.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederation")
    federation_members = wing_rti.getAttributeHandle(federation_class, "HLAfederatesInFederation")
    federate_class = wing_rti.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederate")
    federate_name = wing_rti.getAttributeHandle(federate_class, "HLAfederateName")

    wing_rti.subscribeObjectClassAttributes(federation_class, {federation_members})
    wing_rti.subscribeObjectClassAttributes(federate_class, {federate_name})
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)

    leader_discoveries = [
        record for record in wing_federate.callbacks_named("discoverObjectInstance") if record.args[2].endswith(f".{config.leader_name}")
    ]
    assert leader_discoveries
    leader_mom_object = leader_discoveries[-1].args[0]

    wing_rti.requestAttributeValueUpdate(leader_mom_object, {federate_name}, b"leader-before-disconnect")
    drain_callbacks_pair(leader_rti, wing_rti, loops=24)
    leader_before = wait_for_callback(wing_rti, wing_federate, "reflectAttributeValues", loops=120)
    assert leader_before is not None
    assert leader_before.args[0] == leader_mom_object
    assert leader_before.args[1][federate_name] == config.leader_name.encode()

    leader_rti.resignFederationExecution(ResignAction.NO_ACTION)
    leader_rti.disconnect()
    for _ in range(24):
        drain_callbacks_pair(wing_rti, loops=1)

    wing_rti.requestAttributeValueUpdate(federation_class, {federation_members}, b"after-disconnect-members")
    for _ in range(24):
        drain_callbacks_pair(wing_rti, loops=1)
    federation_after = wait_for_callback(wing_rti, wing_federate, "reflectAttributeValues", loops=120)
    assert federation_after is not None
    assert federation_after.args[0] != leader_mom_object
    assert federation_members in federation_after.args[1]
    assert federation_after.args[1][federation_members] == config.wing_name.encode()

    try:
        wing_rti.requestAttributeValueUpdate(leader_mom_object, {federate_name}, b"leader-after-disconnect")
    except ObjectInstanceNotKnown as exc:
        object_instance_not_known = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected disconnected federate MOM object to become unknown to observer updates")
    finally:
        try:
            wing_rti.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            wing_rti.destroyFederationExecution(config.federation_name)
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
