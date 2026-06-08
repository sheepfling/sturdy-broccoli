"""Federation lifecycle and connection services."""
from __future__ import annotations

from typing import Any, Iterable

from ... import mom_catalog as mom_table
from ...api import FederateAmbassador
from ...enums import CallbackModel, ResignAction
from ...exceptions import (
    AlreadyConnected,
    DesignatorIsHLAstandardMIM,
    FederateAlreadyExecutionMember,
    FederateIsExecutionMember,
    FederateOwnsAttributes,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    OwnershipAcquisitionPending,
    RTIinternalError,
)
from ...fom import standard_mim_module
from ...handles import FederateHandle
from ...time import TimeFactoryRegistry
from ...types import FederationExecutionInformation
from .state import FederationState


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


def _looks_like_time_factory_name(value: Any, registry: TimeFactoryRegistry) -> bool:
    return isinstance(value, str) and value in registry


def _parse_create_federation_args(
    raw_args: tuple[Any, ...],
    *,
    registry: TimeFactoryRegistry,
    default_time_name: str,
) -> tuple[tuple[Any, ...], Any | None, str | None]:
    foms: tuple[Any, ...] = ()
    mim: Any | None = None
    time_name: str | None = None
    args = tuple(raw_args)

    if not args:
        return foms, mim, time_name
    if len(args) == 1:
        if _looks_like_time_factory_name(args[0], registry):
            return (), None, str(args[0])
        return _as_tuple(args[0]), None, time_name
    if len(args) == 2:
        first, second = args
        if _looks_like_time_factory_name(second, registry):
            return _as_tuple(first), None, str(second)
        return _as_tuple(first), second, time_name
    if len(args) == 3:
        first, second, third = args
        if _looks_like_time_factory_name(third, registry):
            return _as_tuple(first), second, str(third)
        return args, None, time_name
    if _looks_like_time_factory_name(args[-1], registry):
        return tuple(args[:-1]), None, str(args[-1])
    return args, None, time_name


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
        return str(federate_name), str(federate_type), str(federation_name), _as_tuple(additional)
    raise RTIinternalError(f"Bad joinFederationExecution arguments: {args!r}")


class PythonRTIFederationLifecycleMixin:
    """Connection and federation lifecycle services."""

    def _svc_connect(
        self,
        federateReference: FederateAmbassador,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:
        if self.state.connected:
            raise AlreadyConnected("RTI ambassador is already connected")
        self.state.ambassador = federateReference
        self.state.callback_model = callbackModel
        self.state.local_settings_designator = localSettingsDesignator
        self.state.connected = True

    def _svc_disconnect(self) -> None:
        self._require_connected()
        if self.state.handle is not None:
            raise FederateIsExecutionMember("Resign before disconnecting")
        self.state.connected = False
        self.state.ambassador = None
        self.state.queue.clear()

    def _svc_createFederationExecution(
        self,
        federationExecutionName: str,
        *fomModules: Any,
    ) -> None:
        self._require_connected()
        fom_sources, mim_source, time_name = _parse_create_federation_args(
            tuple(fomModules),
            registry=self.engine.time_factories,
            default_time_name=self.config.default_logical_time_implementation_name,
        )
        if str(mim_source) == "HLAstandardMIM":
            raise DesignatorIsHLAstandardMIM(
                "Explicit MIM designator shall not be HLAstandardMIM"
            )
        require_foms = self.config.require_fom_modules or bool(fom_sources)
        resolved_foms = self._resolve_fom_modules(
            fom_sources,
            require_non_empty=require_foms,
        )
        resolved_mim = (
            self._resolve_fom_modules((mim_source,), mim=True)[0]
            if mim_source is not None
            else standard_mim_module()
        )
        catalog = self._combine_fom_catalog(resolved_foms, mim_module=resolved_mim)
        time_modules = tuple(
            module
            for module in ((resolved_mim,) if resolved_mim is not None else ()) + tuple(resolved_foms)
            if module is not None
        )
        time_factory = self._choose_time_factory(time_name, time_modules)
        with self.engine._lock:
            if federationExecutionName in self.engine.federations:
                raise FederationExecutionAlreadyExists(str(federationExecutionName))
            self.engine.install_fom_modules(
                [
                    module
                    for module in ((resolved_mim,) if resolved_mim is not None else ())
                    + tuple(resolved_foms)
                    if module is not None
                ]
            )
            federation = FederationState(
                name=str(federationExecutionName),
                fom_modules=tuple(resolved_foms),
                mim_module=resolved_mim,
                fom_catalog=catalog,
                mom_model=mom_table.build_mom_exposure_model(catalog),
                time_factory=time_factory,
            )
            self.engine.federations[str(federationExecutionName)] = federation
            self._ensure_mom_federation_object(federation)

    def _svc_createFederationExecutionWithMIM(
        self,
        federationExecutionName: str,
        *fomModules: Any,
    ) -> None:
        self._svc_createFederationExecution(federationExecutionName, *fomModules)

    def _svc_destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        with self.engine._lock:
            federation = self.engine.federations.get(str(federationExecutionName))
            if federation is None:
                raise FederationExecutionDoesNotExist(str(federationExecutionName))
            if federation.federates:
                raise FederatesCurrentlyJoined(str(federationExecutionName))
            del self.engine.federations[str(federationExecutionName)]

    def _svc_listFederationExecutions(self) -> None:
        self._require_connected()
        infos = {
            FederationExecutionInformation(
                federation.name,
                federation.time_factory.get_name(),
            )
            for federation in self.engine.federations.values()
        }
        self._deliver(self.state, "reportFederationExecutions", infos)

    def _svc_joinFederationExecution(self, *args: Any) -> FederateHandle:
        self._require_connected()
        if self.state.handle is not None:
            raise FederateAlreadyExecutionMember("Already joined")
        federate_name, federate_type, federation_name, additional_fom_sources = _parse_join_args(tuple(args))
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
                from ...exceptions import FederateNameAlreadyInUse

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
            from ...exceptions import InvalidResignAction

            raise InvalidResignAction(repr(resignAction))
        action_name = self._enum_name(resignAction)
        handle = self.state.handle
        assert handle is not None
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
        if acquisition_pending:
            raise OwnershipAcquisitionPending(repr(handle))
        divesting_actions = {
            "UNCONDITIONALLY_DIVEST_ATTRIBUTES",
            "DELETE_OBJECTS",
            "DELETE_OBJECTS_THEN_DIVEST",
            "CANCEL_PENDING_OWNERSHIP_ACQUISITIONS",
            "CANCEL_THEN_DELETE_THEN_DIVEST",
            "DIVEST_ATTRIBUTES_THEN_DELETE",
        }
        if owns_attributes and action_name not in divesting_actions:
            raise FederateOwnsAttributes(repr(handle))
        if action_name in {
            "DELETE_OBJECTS",
            "DELETE_OBJECTS_THEN_DIVEST",
            "CANCEL_THEN_DELETE_THEN_DIVEST",
        }:
            to_remove = [obj for obj in federation.objects.values() if obj.owner == handle]
            for obj in to_remove:
                self._remove_object(obj, b"resign")
        self._remove_federate_from_synchronization_points(federation, handle)
        mom_handle = federation.mom_federate_objects.pop(handle, None)
        if mom_handle is not None:
            mom_instance = federation.objects.pop(mom_handle, None)
            if mom_instance is not None:
                federation.object_names.pop(mom_instance.name, None)
        federation.federates.pop(handle, None)
        self._process_time_advances(federation)
        self._refresh_all_mom_objects(federation, notify=True)
        self.state.handle = None
        self.state.name = None
        self.state.federate_type = None
        self.state.federation = None
        self.state.published_objects.clear()
        self.state.subscribed_objects.clear()
        self.state.published_interactions.clear()
        self.state.subscribed_interactions.clear()
