"""Federation join and resign lifecycle services."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol

from hla.rti1516e.enums import ResignAction
from hla.rti1516e.exceptions import (
    FederateAlreadyExecutionMember,
    FederateOwnsAttributes,
    FederationExecutionDoesNotExist,
    OwnershipAcquisitionPending,
    RTIinternalError,
)
from hla.rti1516e.handles import FederateHandle

from . import mom_catalog as mom_table

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState, FederationState, PythonRTIConfig


class _FederationMembershipContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: "FederateState"
    config: "PythonRTIConfig"

    def _require_connected(self) -> None: ...

    def _require_joined(self) -> "FederationState": ...

    def _ensure_no_save_or_restore_in_progress(self, federation: "FederationState") -> None: ...

    def _resolve_fom_modules(self, sources: Iterable[Any], *, require_non_empty: bool = False, mim: bool = False) -> tuple[Any, ...]: ...

    def _combine_fom_catalog(self, modules: Iterable[Any], *, mim_module: Any | None = None, base_catalog: Any | None = None) -> Any: ...

    def _choose_time_factory(self, requested_name: str | None, modules: Iterable[Any]) -> Any: ...

    def _ensure_service_report_file(self, federation: "FederationState", federate: "FederateState") -> str: ...

    def _ensure_mom_federation_object(self, federation: "FederationState") -> None: ...

    def _ensure_mom_federate_object(self, federation: "FederationState", federate: "FederateState") -> None: ...

    def _refresh_all_mom_objects(self, federation: "FederationState", *, notify: bool = True) -> None: ...

    def _announce_open_synchronization_points_to_joiner(self, federation: "FederationState", handle: FederateHandle) -> None: ...

    def _process_time_advances(self, federation: "FederationState") -> None: ...

    def _enum_name(self, value: Any) -> str: ...

    def _remove_object(
        self,
        instance: Any,
        tag: bytes,
        *,
        timestamp: Any | None = None,
        retraction_handle: Any | None = None,
    ) -> None: ...

    def _remove_federate_from_synchronization_points(self, federation: "FederationState", handle: FederateHandle) -> None: ...

    def _svc_unconditionalAttributeOwnershipDivestiture(self, theObject: Any, theAttributes: Iterable[Any]) -> None: ...


if TYPE_CHECKING:
    class _FederationMembershipMixinBase(_FederationMembershipContext):
        pass
else:
    class _FederationMembershipMixinBase:
        pass


def _is_non_string_sequence(value: Any) -> bool:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return False
    return isinstance(value, Iterable)


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if _is_non_string_sequence(value):
        return tuple(value)
    return (value,)


def _parse_join_args(args: tuple[Any, ...]) -> tuple[str, str, str, tuple[Any, ...]]:
    if len(args) == 2:
        federate_type, federation_name = args
        return "", str(federate_type), str(federation_name), ()
    if len(args) == 3:
        a, b, c = args
        if _is_non_string_sequence(c):
            return "", str(a), str(b), _as_tuple(c)
        return str(a), str(b), str(c), ()
    if len(args) >= 4:
        federate_name, federate_type, federation_name, additional = args[:4]
        return (
            str(federate_name),
            str(federate_type),
            str(federation_name),
            _as_tuple(additional),
        )
    raise RTIinternalError(f"Bad joinFederationExecution arguments: {args!r}")


class PythonRTIFederationMembershipMixin(_FederationMembershipMixinBase):
    """Federation join/resign services."""

    def _apply_departure_resign_action(
        self,
        federation: "FederationState",
        federate: "FederateState",
        action_name: str,
        *,
        removal_tag: bytes,
    ) -> None:
        handle = federate.handle
        assert handle is not None
        cancel_pending_acquisition_actions = {
            "CANCEL_PENDING_OWNERSHIP_ACQUISITIONS",
            "CANCEL_THEN_DELETE_THEN_DIVEST",
        }
        owns_attributes = False
        acquisition_pending = False
        for obj in federation.objects.values():
            if any(handle in candidates for candidates in obj.attribute_candidates.values()):
                acquisition_pending = True
                break
            if obj.owner == handle:
                owns_attributes = True
                break
            if any(owner == handle for owner in obj.attribute_owners.values()):
                owns_attributes = True
                break
        if acquisition_pending and action_name not in cancel_pending_acquisition_actions:
            raise OwnershipAcquisitionPending(repr(handle))
        if acquisition_pending:
            for obj in federation.objects.values():
                stale_attrs = []
                for attr, candidates in obj.attribute_candidates.items():
                    if handle in candidates:
                        candidates.discard(handle)
                        if not candidates:
                            stale_attrs.append(attr)
                for attr in stale_attrs:
                    obj.attribute_candidates.pop(attr, None)
        delete_object_actions = {
            "DELETE_OBJECTS",
            "DELETE_OBJECTS_THEN_DIVEST",
            "CANCEL_THEN_DELETE_THEN_DIVEST",
        }
        attribute_divesting_actions = {
            "UNCONDITIONALLY_DIVEST_ATTRIBUTES",
            "DELETE_OBJECTS_THEN_DIVEST",
            "CANCEL_THEN_DELETE_THEN_DIVEST",
        }
        if owns_attributes and action_name not in (delete_object_actions | attribute_divesting_actions):
            raise FederateOwnsAttributes(repr(handle))
        if action_name in delete_object_actions:
            to_remove = [obj for obj in federation.objects.values() if obj.owner == handle]
            for obj in to_remove:
                self._remove_object(obj, removal_tag)
        if action_name in attribute_divesting_actions:
            for obj in tuple(federation.objects.values()):
                object_def = self.engine.object_class_for_handle(obj.class_handle)
                owned_attrs = {
                    attr
                    for attr in object_def.attribute_names
                    if obj.attribute_owners.get(attr, obj.owner) == handle
                }
                for attr in owned_attrs:
                    old_owner = obj.attribute_owners.get(attr, obj.owner)
                    if self._attribute_has_candidates(obj, attr):
                        new_owner = self._pop_first_candidate(obj, attr)
                        self._complete_immediate_attribute_transfer(
                            federation,
                            obj,
                            attr,
                            new_owner,
                            old_owner=old_owner,
                            acquisition_tag=b"",
                            notify_previous_owner=False,
                        )
                    else:
                        obj.attribute_owners[attr] = None
                        obj.attribute_divesting.discard(attr)

    def _finalize_departed_federate_membership(
        self,
        federation: "FederationState",
        federate: "FederateState",
    ) -> None:
        handle = federate.handle
        assert handle is not None
        self._remove_federate_from_synchronization_points(federation, handle)
        mom_handle = federation.mom_federate_objects.pop(handle, None)
        if mom_handle is not None:
            mom_instance = federation.objects.pop(mom_handle, None)
            if mom_instance is not None:
                federation.object_names.pop(mom_instance.name, None)
        for region in tuple(federate.regions):
            federation.region_owners.pop(region, None)
        federation.federates.pop(handle, None)
        self._process_time_advances(federation)
        self._refresh_all_mom_objects(federation, notify=True)
        federate.last_reporting_handle = handle
        federate.last_reporting_name = federate.name
        federate.last_reporting_federation = federation
        federate.handle = None
        federate.name = None
        federate.federate_type = None
        federate.federation = None
        federate.published_objects.clear()
        federate.subscribed_objects.clear()
        federate.registration_interest_classes.clear()
        federate.published_interactions.clear()
        federate.subscribed_interactions.clear()
        federate.interaction_interest_classes.clear()
        federate.regions.clear()
        federate.region_bounds.clear()
        federate.update_regions.clear()
        federate.object_region_subscriptions.clear()
        federate.interaction_region_subscriptions.clear()

    def _svc_joinFederationExecution(self, *args: Any) -> FederateHandle:
        self._require_connected()
        if self.state.handle is not None:
            raise FederateAlreadyExecutionMember("Already joined")
        federate_name, federate_type, federation_name, additional_fom_sources = _parse_join_args(
            tuple(args)
        )
        if not federate_name:
            federate_name = f"federate-{self.state.backend_id}"
        with self.engine._lock:
            federation = self.engine.federations.get(str(federation_name))
            if federation is None:
                raise FederationExecutionDoesNotExist(str(federation_name))
            self._ensure_no_save_or_restore_in_progress(federation)
            additional_modules = self._resolve_fom_modules(additional_fom_sources)
            new_catalog = federation.fom_catalog
            if additional_modules:
                new_catalog = self._combine_fom_catalog(
                    additional_modules,
                    base_catalog=federation.fom_catalog,
                )
            if any(
                federate.name == str(federate_name)
                for federate in federation.federates.values()
            ):
                from hla.rti1516e.exceptions import FederateNameAlreadyInUse

                raise FederateNameAlreadyInUse(str(federate_name))
            if additional_modules:
                self.engine.install_fom_modules(additional_modules)
                federation.fom_modules = tuple((*federation.fom_modules, *additional_modules))
                federation.fom_catalog = new_catalog
                federation.mom_model = mom_table.build_mom_exposure_model(new_catalog)
            self._choose_time_factory(None, additional_modules)
            handle = self.engine._alloc(FederateHandle)
            self.state.handle = handle
            self.state.name = str(federate_name)
            self.state.federate_type = str(federate_type)
            self.state.federation = federation
            self.state.last_reporting_handle = handle
            self.state.last_reporting_name = str(federate_name)
            self.state.last_reporting_federation = federation
            self.state.current_time = federation.time_factory.make_initial()
            self.state.lookahead = federation.time_factory.make_zero()
            self.state.service_reports_to_file = bool(
                self.config.service_report_file_on_by_default
            )
            if self.state.service_reports_to_file:
                self._ensure_service_report_file(federation, self.state)
            federation.federates[handle] = self.state
            self._ensure_mom_federation_object(federation)
            self._ensure_mom_federate_object(federation, self.state)
            self._refresh_all_mom_objects(federation, notify=True)
            self._announce_open_synchronization_points_to_joiner(federation, handle)
            self._process_time_advances(federation)
            return handle

    def _svc_resignFederationExecution(self, resignAction: ResignAction) -> None:
        federation = self._require_joined()
        if not isinstance(resignAction, ResignAction):
            from hla.rti1516e.exceptions import InvalidResignAction

            raise InvalidResignAction(repr(resignAction))
        action_name = self._enum_name(resignAction)
        self._apply_departure_resign_action(
            federation,
            self.state,
            action_name,
            removal_tag=b"resign",
        )
        self._finalize_departed_federate_membership(federation, self.state)
