"""Runtime state records for the Python 2025 RTI backend."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hla.rti1516_2025.enums import OrderType, RestoreStatus, SaveStatus
from hla.rti1516_2025.federate_ambassador import FederateAmbassador
from hla.rti1516_2025.handles import FederateHandle


@dataclass(slots=True)
class FederationRecord:
    logical_time_implementation_name: str
    fom_modules: tuple[Any, ...] = ()
    mim_module: Any | None = None
    fom_catalog: Any | None = None
    members: dict[str, str] = field(default_factory=dict)
    member_handles: dict[str, FederateHandle] = field(default_factory=dict)
    member_ambassadors: dict[int, FederateAmbassador] = field(default_factory=dict)
    member_rtis: dict[int, Any] = field(default_factory=dict)
    published_object_attributes: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_object_attributes: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_object_regions: dict[int, dict[str, dict[str, set[int]]]] = field(default_factory=dict)
    published_interactions: dict[int, set[str]] = field(default_factory=dict)
    subscribed_interactions: dict[int, set[str]] = field(default_factory=dict)
    subscribed_interaction_regions: dict[int, dict[str, set[int]]] = field(default_factory=dict)
    directed_interaction_region_gates: dict[int, set[str]] = field(default_factory=dict)
    published_directed_interactions: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    subscribed_directed_interactions: dict[int, dict[str, set[str]]] = field(default_factory=dict)
    interaction_order: dict[tuple[int, str], OrderType] = field(default_factory=dict)
    member_regions: dict[int, dict[int, set[str]]] = field(default_factory=dict)
    member_region_bounds: dict[int, dict[int, dict[str, Any]]] = field(default_factory=dict)
    object_instances: dict[int, "ObjectInstanceRecord"] = field(default_factory=dict)
    object_instance_names: dict[str, int] = field(default_factory=dict)
    reserved_object_instance_names: dict[str, int] = field(default_factory=dict)
    mom_object_instances_updated: dict[tuple[int, str], int] = field(default_factory=dict)
    mom_object_instances_reflected: dict[tuple[int, str], int] = field(default_factory=dict)
    mom_updates_sent: dict[tuple[int, str, str], int] = field(default_factory=dict)
    mom_reflections_received: dict[tuple[int, str, str], int] = field(default_factory=dict)
    mom_interactions_sent: dict[tuple[int, str, str], int] = field(default_factory=dict)
    mom_interactions_received: dict[tuple[int, str, str], int] = field(default_factory=dict)
    attribute_scope_state: dict[tuple[int, int, str], bool] = field(default_factory=dict)
    interaction_transportation: dict[tuple[int, str], str] = field(default_factory=dict)
    queued_tso_callbacks: dict[int, "QueuedTsoCallback"] = field(default_factory=dict)
    delivered_retraction_handles: set[int] = field(default_factory=set)
    delivered_retraction_targets: dict[int, FederateHandle] = field(default_factory=dict)
    retraction_groups: dict[int, set[int]] = field(default_factory=dict)
    retraction_group_lookup: dict[int, int] = field(default_factory=dict)
    saved_labels: set[str] = field(default_factory=set)
    saved_object_instances: dict[str, dict[int, "ObjectInstanceRecord"]] = field(default_factory=dict)
    saved_object_instance_names: dict[str, dict[str, int]] = field(default_factory=dict)
    saved_reserved_object_instance_names: dict[str, dict[str, int]] = field(default_factory=dict)
    saved_next_object_instance_handles: dict[str, int] = field(default_factory=dict)
    saved_member_logical_times: dict[str, dict[int, Any]] = field(default_factory=dict)
    saved_member_time_states: dict[str, dict[int, dict[str, Any]]] = field(default_factory=dict)
    saved_member_known_objects: dict[str, dict[int, dict[str, Any]]] = field(default_factory=dict)
    saved_published_object_attributes: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_subscribed_object_attributes: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_subscribed_object_regions: dict[str, dict[int, dict[str, dict[str, set[int]]]]] = field(default_factory=dict)
    saved_published_interactions: dict[str, dict[int, set[str]]] = field(default_factory=dict)
    saved_subscribed_interactions: dict[str, dict[int, set[str]]] = field(default_factory=dict)
    saved_subscribed_interaction_regions: dict[str, dict[int, dict[str, set[int]]]] = field(default_factory=dict)
    saved_directed_interaction_region_gates: dict[str, dict[int, set[str]]] = field(default_factory=dict)
    saved_published_directed_interactions: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_subscribed_directed_interactions: dict[str, dict[int, dict[str, set[str]]]] = field(default_factory=dict)
    saved_member_regions: dict[str, dict[int, dict[int, set[str]]]] = field(default_factory=dict)
    saved_member_region_bounds: dict[str, dict[int, dict[int, dict[str, Any]]]] = field(default_factory=dict)
    saved_interaction_order: dict[str, dict[tuple[int, str], OrderType]] = field(default_factory=dict)
    saved_interaction_transportation: dict[str, dict[tuple[int, str], str]] = field(default_factory=dict)
    saved_queued_tso_callbacks: dict[str, dict[int, "QueuedTsoCallback"]] = field(default_factory=dict)
    saved_delivered_retraction_handles: dict[str, set[int]] = field(default_factory=dict)
    saved_delivered_retraction_targets: dict[str, dict[int, FederateHandle]] = field(default_factory=dict)
    saved_retraction_groups: dict[str, dict[int, set[int]]] = field(default_factory=dict)
    saved_retraction_group_lookup: dict[str, dict[int, int]] = field(default_factory=dict)
    save_label: str | None = None
    next_save_name: str | None = None
    next_save_time: Any | None = None
    save_status: dict[int, SaveStatus] = field(default_factory=dict)
    restore_label: str | None = None
    restore_status: dict[int, RestoreStatus] = field(default_factory=dict)
    synchronization_points: dict[str, "SynchronizationPointRecord"] = field(default_factory=dict)
    next_federate_handle: int = 1
    next_object_instance_handle: int = 1
    next_region_handle: int = 1
    next_message_retraction_handle: int = 1


@dataclass(slots=True)
class ObjectInstanceRecord:
    object_class_name: str
    object_instance_name: str | None
    producing_federate: FederateHandle | None = None
    attribute_values: dict[str, bytes] = field(default_factory=dict)
    attribute_owners: dict[str, FederateHandle | None] = field(default_factory=dict)
    attribute_divesting: set[str] = field(default_factory=set)
    attribute_candidates: dict[str, list[tuple[FederateHandle, bytes]]] = field(default_factory=dict)
    update_regions: dict[str, set[int]] = field(default_factory=dict)
    attribute_transportation: dict[str, str] = field(default_factory=dict)
    attribute_order: dict[str, OrderType] = field(default_factory=dict)


@dataclass(slots=True)
class SynchronizationPointRecord:
    user_supplied_tag: bytes
    required_federates: set[int]
    achieved_federates: set[int] = field(default_factory=set)
    failed_federates: set[int] = field(default_factory=set)
    synchronized: bool = False


@dataclass(slots=True)
class QueuedTsoCallback:
    target_federate: FederateHandle
    callback_time: Any
    serial: int
    method_name: str
    args: tuple[Any, ...]


FEDERATION_REGISTRY: dict[str, FederationRecord] = {}
