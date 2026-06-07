"""Concrete in-memory Python RTI backend implementation."""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable, Mapping

from ... import handles as hla_handles
from ... import time_management as tm
from ...exceptions import (
    AttributeRelevanceAdvisorySwitchIsOff,
    AttributeRelevanceAdvisorySwitchIsOn,
    AttributeNotDefined,
    AttributeScopeAdvisorySwitchIsOff,
    AttributeScopeAdvisorySwitchIsOn,
    CallNotAllowedFromWithinCallback,
    CouldNotCreateLogicalTimeFactory,
    CouldNotOpenFDD,
    FederateHandleNotKnown,
    FederateInternalError,
    FederateNotExecutionMember,
    InconsistentFDD,
    InvalidDimensionHandle,
    InvalidFederateHandle,
    InvalidInteractionClassHandle,
    InvalidLogicalTime,
    InvalidLookahead,
    InvalidObjectClassHandle,
    InvalidOrderName,
    InvalidOrderType,
    InvalidRegion,
    InvalidResignAction,
    InvalidServiceGroup,
    InvalidTransportationName,
    InvalidTransportationType,
    InvalidUpdateRateDesignator,
    NameNotFound,
    NotConnected,
    ObjectClassRelevanceAdvisorySwitchIsOff,
    ObjectClassRelevanceAdvisorySwitchIsOn,
    ObjectInstanceNotKnown,
    InteractionRelevanceAdvisorySwitchIsOff,
    InteractionRelevanceAdvisorySwitchIsOn,
    RTIexception,
)
from ...fom import FOMCatalog, FOMMergeError, FOMModule, FOMResolutionError, FOMResolver, merge_fom_modules, standard_mim_module
from ...handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    TransportationTypeHandle,
)
from ...service_reporting import ServiceReportSink
from ...time import LogicalTimeFactory
from .callbacks import PythonRTICallbacksMixin
from .declaration import PythonRTIDeclarationMixin
from .ddm import PythonRTIDdmMixin
from .engine import InMemoryRTIEngine
from .federation import PythonRTIFederationMixin
from .mom import PythonRTIMomMixin
from .object import PythonRTIObjectMixin
from .ownership import PythonRTIOwnershipMixin
from .reporting import PythonRTIServiceReportFiles
from .save_restore import PythonRTISaveRestoreMixin
from .state import (
    CallbackEvent,
    FederateState,
    FederationState,
    MOM_TEXT_ENCODING,
    ObjectInstance,
    PythonRTIConfig,
    RTI_FEDERATE_HANDLE,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
)
from .time import PythonRTITimeMixin
from ..base import BackendInfo, Invocation, RTIBackend, UnsupportedBackendService
from ..java_common import resolve_java_arguments


def _enum_name(value: Any) -> str:
    name_attr = getattr(value, "name", None)
    if isinstance(name_attr, str):
        return name_attr
    if callable(name_attr):
        try:
            return str(name_attr())
        except Exception:
            pass
    return str(value)


def _as_mom_bytes(value: Any) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return str(value).encode(MOM_TEXT_ENCODING)


def _handle_value(value: Any) -> str:
    return str(getattr(value, "value", value))


class PythonRTIBackend(
    PythonRTIFederationMixin,
    PythonRTISaveRestoreMixin,
    PythonRTICallbacksMixin,
    PythonRTIDeclarationMixin,
    PythonRTIObjectMixin,
    PythonRTIMomMixin,
    PythonRTIOwnershipMixin,
    PythonRTITimeMixin,
    PythonRTIDdmMixin,
    RTIBackend,
):
    """A dependency-free RTIBackend implemented entirely in Python."""

    def __init__(
        self,
        *,
        engine: InMemoryRTIEngine | None = None,
        config: PythonRTIConfig | None = None,
        federate_state: FederateState | None = None,
    ) -> None:
        self.engine = engine or InMemoryRTIEngine()
        self.config = config or PythonRTIConfig(name=self.engine.name)
        self.fom_resolver = (
            FOMResolver(
                base_paths=tuple(self.config.fom_search_paths),
                require_local_parse=(self.config.require_fom_parse or self.config.strict_fom_loading),
            )
            if (self.config.fom_search_paths or self.config.require_fom_parse or self.config.strict_fom_loading)
            else self.engine.fom_resolver
        )
        self.state = federate_state or self.engine.new_federate_state()
        self.delivered_callback_count = 0
        self.service_report_sink = (
            ServiceReportSink(self.config.service_report_file, truncate=self.config.service_report_file_truncate)
            if self.config.service_report_file
            else None
        )
        self.service_report_files = PythonRTIServiceReportFiles(directory=self.config.service_report_directory)
        self.info = BackendInfo(
            name=self.config.name,
            kind="python/in-memory",
            version=self.config.version,
            details={"engine": self.engine.name, "backend_id": self.state.backend_id},
        )

    def invoke(self, invocation: Invocation) -> Any:
        service = getattr(self, f"_svc_{invocation.method_name}", None)
        if service is None:
            raise UnsupportedBackendService(f"Python in-memory RTI does not yet implement {invocation.method_name}")
        args = resolve_java_arguments(invocation)
        try:
            result = service(*args)
        except RTIexception as exc:
            self._report_service_invocation(invocation.method_name, success=False, exception_name=exc.__class__.__name__, args=args)
            raise
        except Exception as exc:
            self._report_service_invocation(invocation.method_name, success=False, exception_name=exc.__class__.__name__, args=args)
            raise
        self._report_service_invocation(invocation.method_name, success=True, exception_name="", args=args, result=result)
        return result

    def pending_callback_count(self) -> int:
        return len(self.state.queue)

    def current_fom_catalog(self) -> FOMCatalog:
        federation = self._require_joined()
        return federation.fom_catalog

    def current_fom_summary(self) -> dict[str, Any]:
        return self.current_fom_catalog().as_summary()

    def close(self) -> None:
        try:
            if self.state.connected and self.state.handle is not None:
                from ...enums import ResignAction

                self._svc_resignFederationExecution(ResignAction.NO_ACTION)
            if self.state.connected:
                self._svc_disconnect()
        except Exception:
            pass

    def _enum_name(self, value: Any) -> str:
        return _enum_name(value)

    def _require_connected(self) -> None:
        if not self.state.connected:
            raise NotConnected("RTI ambassador is not connected")

    def _require_joined(self) -> FederationState:
        self._require_connected()
        federation = self.state.federation
        if self.state.handle is None or federation is None:
            raise FederateNotExecutionMember("Federate has not joined a federation execution")
        return federation

    def _federate_name(self, state: FederateState | None = None) -> str:
        state = state or self.state
        return state.name or f"Federate-{state.backend_id}"

    def _enforce_fom_names(self, federation: FederationState) -> bool:
        return bool(self.config.strict_fom_lookup and federation.fom_catalog.modules)

    def _time_factory(self) -> LogicalTimeFactory[Any, Any]:
        federation = self.state.federation
        if federation is not None:
            return federation.time_factory
        return self.engine.time_factories.get(self.config.default_logical_time_implementation_name)

    def _coerce_time(self, value: Any) -> Any:
        try:
            return self._time_factory().coerce_time(value)
        except Exception as exc:
            raise InvalidLogicalTime(repr(value)) from exc

    def _coerce_interval(self, value: Any) -> Any:
        try:
            return self._time_factory().coerce_interval(value)
        except Exception as exc:
            raise InvalidLookahead(repr(value)) from exc

    def _time_lt(self, a: Any, b: Any) -> bool:
        return tm.time_lt(a, b)

    def _time_le(self, a: Any, b: Any) -> bool:
        return tm.time_le(a, b)

    def _queued_tso_messages(self, federation: FederationState, fed: FederateState):
        return tm.queued_tso_messages(federation, fed)

    def _compute_grant_decision(self, federation: FederationState, fed: FederateState, request: Any, **kwargs: Any):
        return tm.compute_grant_decision(federation, fed, request, **kwargs)

    def _scheduled_save_time_reached(self, fed: FederateState, save_time: Any, *, next_grant_time: Any | None = None) -> bool:
        return tm.scheduled_save_time_reached(fed, save_time, next_grant_time=next_grant_time)

    def _resolve_fom_modules(
        self,
        sources: Iterable[Any] | Any | None,
        *,
        require_non_empty: bool = False,
        mim: bool = False,
    ) -> tuple[FOMModule, ...]:
        try:
            modules = self.fom_resolver.resolve_many(sources)
            if mim:
                modules = tuple(replace(module, is_mim=True) for module in modules)
            if require_non_empty and not modules:
                raise FOMResolutionError("At least one FOM module designator is required")
            if self.config.require_fom_parse or self.config.strict_fom_loading:
                for module in modules:
                    if module.uri.startswith("builtin:"):
                        continue
                    if not module.parsed:
                        raise FOMResolutionError(f"FOM module could not be parsed locally by the Python RTI: {module.uri}")
            return modules
        except FOMResolutionError as exc:
            if mim:
                from ...exceptions import CouldNotOpenMIM

                raise CouldNotOpenMIM(str(exc)) from exc
            raise CouldNotOpenFDD(str(exc)) from exc

    def _combine_fom_catalog(
        self,
        modules: Iterable[FOMModule],
        *,
        mim_module: FOMModule | None = None,
        base_catalog: FOMCatalog | None = None,
    ) -> FOMCatalog:
        try:
            base_modules = tuple(base_catalog.modules) if base_catalog is not None else ()
            effective_mim = mim_module if mim_module is not None else (base_catalog.mim_module if base_catalog is not None else standard_mim_module())
            return merge_fom_modules((*base_modules, *tuple(modules)), mim_module=effective_mim)
        except FOMMergeError as exc:
            raise InconsistentFDD(str(exc)) from exc

    def _current_fom_summary(self, federation: FederationState | None = None) -> dict[str, Any]:
        federation = federation or self._require_joined()
        return federation.fom_catalog.as_summary()

    def _choose_time_factory(self, requested_name: str | None, modules: Iterable[FOMModule]) -> LogicalTimeFactory[Any, Any]:
        name = requested_name or self.config.default_logical_time_implementation_name
        if self.config.infer_time_factory_from_fom and not requested_name:
            for module in modules:
                if module.inferred_time_implementation:
                    name = module.inferred_time_implementation
                    break
        try:
            return self.engine.time_factories.get(name)
        except KeyError as exc:
            raise CouldNotCreateLogicalTimeFactory(str(exc)) from exc

    def _deliver(self, target: FederateState, method_name: str, *args: Any) -> None:
        from ...enums import CallbackModel

        if target.ambassador is None:
            return
        if target.callback_model is CallbackModel.HLA_IMMEDIATE and self.config.immediate_callbacks_inline:
            self._invoke_callback(target, method_name, args)
        else:
            target.queue.append(CallbackEvent(method_name, tuple(args)))

    def _invoke_callback(self, target: FederateState, method_name: str, args: tuple[Any, ...]) -> None:
        if target.ambassador is None:
            return
        if target.in_callback:
            raise CallNotAllowedFromWithinCallback("Nested callback invocation is not allowed")
        try:
            target.in_callback = True
            getattr(target.ambassador, method_name)(*args)
            self.delivered_callback_count += 1
        except FederateInternalError:
            raise
        except BaseException as exc:
            raise FederateInternalError(f"Python FederateAmbassador.{method_name} failed: {exc}", cause=exc) from exc
        finally:
            target.in_callback = False

    def _find_object(self, handle: ObjectInstanceHandle) -> tuple[FederationState, ObjectInstance]:
        federation = self._require_joined()
        try:
            return federation, federation.objects[handle]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(handle)) from exc

    def _object_matches_subscription(self, instance_class: ObjectClassHandle, subscribed_class: ObjectClassHandle) -> bool:
        try:
            return self.engine.object_class_is_a(instance_class, subscribed_class)
        except InvalidObjectClassHandle:
            return instance_class == subscribed_class

    def _interaction_matches_subscription(self, interaction_class: InteractionClassHandle, subscribed_class: InteractionClassHandle) -> bool:
        try:
            return self.engine.interaction_class_is_a(interaction_class, subscribed_class)
        except InvalidInteractionClassHandle:
            return interaction_class == subscribed_class

    def _discover_existing_objects(self, subscriber: FederateState, object_class: ObjectClassHandle) -> None:
        federation = subscriber.federation
        if federation is None:
            return
        for instance in federation.objects.values():
            if self._object_matches_subscription(instance.class_handle, object_class):
                self._deliver(subscriber, "discoverObjectInstance", instance.handle, instance.class_handle, instance.name, instance.owner or RTI_FEDERATE_HANDLE)

    def _subscribed_attributes_for(self, subscriber: FederateState, object_class: ObjectClassHandle) -> set[AttributeHandle]:
        result: set[AttributeHandle] = set()
        for subscribed_class, attrs in subscriber.subscribed_objects.items():
            if self._object_matches_subscription(object_class, subscribed_class):
                result.update(attrs)
        return result

    def _attribute_region_allows(self, subscriber: FederateState, instance: ObjectInstance, attribute: AttributeHandle, sent_regions: set[RegionHandle] | None) -> bool:
        federation = subscriber.federation
        if federation is None:
            return True
        subscription_regions: set[RegionHandle] = set()
        for subscribed_class, attr_regions in subscriber.object_region_subscriptions.items():
            if self._object_matches_subscription(instance.class_handle, subscribed_class):
                subscription_regions.update(attr_regions.get(attribute, set()))
        if not subscription_regions:
            return True
        return self._region_sets_overlap(self.state, set(sent_regions or set()), subscriber, subscription_regions)

    def _interaction_region_allows(self, subscriber: FederateState, interaction_class: InteractionClassHandle, sent_regions: set[RegionHandle] | None) -> bool:
        federation = subscriber.federation
        if federation is None:
            return True
        subscription_regions: set[RegionHandle] = set()
        for subscribed_class, regions in subscriber.interaction_region_subscriptions.items():
            if self._interaction_matches_subscription(interaction_class, subscribed_class):
                subscription_regions.update(regions)
        if not subscription_regions:
            return True
        return self._region_sets_overlap(self.state, set(sent_regions or set()), subscriber, subscription_regions)

    def _attribute_subscription_intersection(
        self,
        subscriber: FederateState,
        object_class: ObjectClassHandle,
        attributes: Mapping[AttributeHandle, bytes],
        instance: ObjectInstance | None = None,
        sent_regions_by_attribute: Mapping[AttributeHandle, set[RegionHandle]] | None = None,
    ) -> dict[AttributeHandle, bytes]:
        subscribed = self._subscribed_attributes_for(subscriber, object_class)
        if not subscribed:
            return {}
        reflected: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            if handle not in subscribed:
                continue
            if instance is not None and not self._attribute_region_allows(subscriber, instance, handle, set((sent_regions_by_attribute or {}).get(handle, set()))):
                continue
            reflected[handle] = value
        return reflected

    def _svc_getAutomaticResignDirective(self):
        self._require_joined()
        return self.state.automatic_resign_directive

    def _svc_setAutomaticResignDirective(self, resignAction: Any) -> None:
        from ...enums import ResignAction

        self._require_joined()
        if not isinstance(resignAction, ResignAction):
            raise InvalidResignAction(repr(resignAction))
        self.state.automatic_resign_directive = resignAction

    def _svc_enableObjectClassRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.object_class_relevance_advisory:
            raise ObjectClassRelevanceAdvisorySwitchIsOn("Object class relevance advisory switch is already enabled")
        self.state.object_class_relevance_advisory = True

    def _svc_disableObjectClassRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.object_class_relevance_advisory:
            raise ObjectClassRelevanceAdvisorySwitchIsOff("Object class relevance advisory switch is already disabled")
        self.state.object_class_relevance_advisory = False

    def _svc_enableAttributeRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.attribute_relevance_advisory:
            raise AttributeRelevanceAdvisorySwitchIsOn("Attribute relevance advisory switch is already enabled")
        self.state.attribute_relevance_advisory = True

    def _svc_disableAttributeRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.attribute_relevance_advisory:
            raise AttributeRelevanceAdvisorySwitchIsOff("Attribute relevance advisory switch is already disabled")
        self.state.attribute_relevance_advisory = False

    def _svc_enableAttributeScopeAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.attribute_scope_advisory:
            raise AttributeScopeAdvisorySwitchIsOn("Attribute scope advisory switch is already enabled")
        self.state.attribute_scope_advisory = True

    def _svc_disableAttributeScopeAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.attribute_scope_advisory:
            raise AttributeScopeAdvisorySwitchIsOff("Attribute scope advisory switch is already disabled")
        self.state.attribute_scope_advisory = False

    def _svc_enableInteractionRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.interaction_relevance_advisory:
            raise InteractionRelevanceAdvisorySwitchIsOn("Interaction relevance advisory switch is already enabled")
        self.state.interaction_relevance_advisory = True

    def _svc_disableInteractionRelevanceAdvisorySwitch(self) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.interaction_relevance_advisory:
            raise InteractionRelevanceAdvisorySwitchIsOff("Interaction relevance advisory switch is already disabled")
        self.state.interaction_relevance_advisory = False

    def _svc_getFederateName(self, theHandle: FederateHandle | None = None) -> str:
        federation = self._require_joined()
        if theHandle is None:
            if self.state.name is None:
                raise FederateHandleNotKnown("Current federate has no name")
            return self.state.name
        if not isinstance(theHandle, FederateHandle):
            raise InvalidFederateHandle(repr(theHandle))
        target = federation.federates.get(theHandle)
        if target is None or target.name is None:
            raise FederateHandleNotKnown(repr(theHandle))
        return target.name

    def _svc_getFederateHandle(self, theName: str) -> FederateHandle:
        federation = self._require_joined()
        for handle, federate in federation.federates.items():
            if federate.name == theName:
                return handle
        raise NameNotFound(str(theName))

    def _svc_getObjectClassHandle(self, theName: str) -> ObjectClassHandle:
        federation = self._require_joined()
        name = str(theName)
        if self._enforce_fom_names(federation) and name not in federation.fom_catalog.object_classes:
            raise NameNotFound(name)
        return self.engine.get_or_create_object_class(name).handle

    def _svc_getObjectClassName(self, theHandle: ObjectClassHandle) -> str:
        self._require_joined()
        return self.engine.object_class_for_handle(theHandle).name

    def _svc_getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:
        federation = self._require_joined()
        class_def = self.engine.object_class_for_handle(whichClass)
        name = str(theName)
        if self._enforce_fom_names(federation):
            spec = federation.fom_catalog.object_classes.get(class_def.name)
            if spec is None or name not in spec.attributes:
                raise NameNotFound(name)
        return self.engine.get_or_create_attribute(whichClass, name)

    def _svc_getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:
        self._require_joined()
        return self.engine.attribute_name(whichClass, theHandle)

    def _svc_getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:
        federation = self._require_joined()
        name = str(theName)
        if self._enforce_fom_names(federation) and name not in federation.fom_catalog.interaction_classes:
            raise NameNotFound(name)
        return self.engine.get_or_create_interaction_class(name).handle

    def _svc_getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:
        self._require_joined()
        return self.engine.interaction_for_handle(theHandle).name

    def _svc_getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:
        federation = self._require_joined()
        class_def = self.engine.interaction_for_handle(whichClass)
        name = str(theName)
        if self._enforce_fom_names(federation):
            spec = federation.fom_catalog.interaction_classes.get(class_def.name)
            if spec is None or name not in spec.parameters:
                raise NameNotFound(name)
        return self.engine.get_or_create_parameter(whichClass, name)

    def _svc_getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:
        self._require_joined()
        return self.engine.parameter_name(whichClass, theHandle)

    def _svc_getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:
        federation = self._require_joined()
        try:
            return federation.object_names[str(theName)]
        except KeyError as exc:
            raise ObjectInstanceNotKnown(str(theName)) from exc

    def _svc_getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:
        federation = self._require_joined()
        try:
            return federation.objects[theHandle].name
        except KeyError as exc:
            raise ObjectInstanceNotKnown(repr(theHandle)) from exc

    def _svc_getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:
        _, instance = self._find_object(theObject)
        return instance.class_handle

    def _svc_getDimensionHandle(self, theName: str) -> DimensionHandle:
        federation = self._require_joined()
        name = str(theName)
        if self._enforce_fom_names(federation) and federation.fom_catalog.dimensions and name not in federation.fom_catalog.dimensions:
            raise NameNotFound(name)
        return self.engine.get_or_create_dimension(name)

    def _svc_getDimensionName(self, theHandle: DimensionHandle) -> str:
        self._require_joined()
        return self.engine.dimension_name(theHandle)

    def _svc_getTransportationTypeHandle(self, transportationType: str | None = None) -> TransportationTypeHandle:
        self._require_joined()
        if transportationType not in (None, "", "HLAreliable"):
            raise InvalidTransportationName(str(transportationType))
        return self.engine.transportation_reliable

    def _svc_getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:
        self._require_joined()
        if theHandle == self.engine.transportation_reliable:
            return "HLAreliable"
        raise InvalidTransportationType(repr(theHandle))

    def _svc_getHLAversion(self) -> str:
        return "HLA 1516-2010 Python in-memory RTI subset"

    def _svc_getTimeFactory(self) -> LogicalTimeFactory[Any, Any]:
        self._require_joined()
        return self._time_factory()

    def _svc_getDimensionHandleSet(self, region: RegionHandle) -> hla_handles.DimensionHandleSet:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        try:
            return hla_handles.DimensionHandleSet(self.state.regions[region])
        except KeyError as exc:
            raise InvalidRegion(repr(region)) from exc

    def _svc_getOrderName(self, orderType: Any) -> str:
        from ...enums import OrderType
        self._require_joined()
        if not isinstance(orderType, OrderType):
            raise InvalidOrderType(repr(orderType))
        return orderType.name

    def _svc_getOrderType(self, orderName: str):
        from ...enums import OrderType
        self._require_joined()
        normalized = str(orderName).replace("HLA", "").replace("_", "").replace(" ", "").upper()
        if normalized in {"RECEIVE", "RECEIVEORDER"}:
            return OrderType.RECEIVE
        if normalized in {"TIMESTAMP", "TIMESTAMPORDER", "TSO"}:
            return OrderType.TIMESTAMP
        raise InvalidOrderName(str(orderName))

    def _svc_getTransportationType(self, transportationName: str | None = None) -> TransportationTypeHandle:
        return self._svc_getTransportationTypeHandle(transportationName)

    def _svc_getTransportationName(self, transportationType: TransportationTypeHandle) -> str:
        return self._svc_getTransportationTypeName(transportationType)

    def _all_known_dimensions(self) -> hla_handles.DimensionHandleSet:
        if not self.engine.dimensions_by_name:
            return hla_handles.DimensionHandleSet([self.engine.get_or_create_dimension("HLAdefaultRoutingSpace")])
        return hla_handles.DimensionHandleSet(self.engine.dimensions_by_name.values())

    def _svc_getAvailableDimensionsForClassAttribute(self, theClass: ObjectClassHandle, theAttribute: AttributeHandle) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.attribute_name(theClass, theAttribute)
        return self._all_known_dimensions()

    def _svc_getAvailableDimensionsForInteractionClass(self, theClass: InteractionClassHandle) -> hla_handles.DimensionHandleSet:
        self._require_joined()
        self.engine.interaction_for_handle(theClass)
        return self._all_known_dimensions()

    def _svc_getUpdateRateValue(self, updateRateDesignator: str) -> float:
        self._require_joined()
        if str(updateRateDesignator) not in {"default", "HLAdefault"}:
            raise InvalidUpdateRateDesignator(str(updateRateDesignator))
        return 0.0

    def _svc_getUpdateRateValueForAttribute(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> float:
        _, instance = self._find_object(theObject)
        self.engine.attribute_name(instance.class_handle, theAttribute)
        return 0.0

    def _svc_normalizeFederateHandle(self, theFederateHandle: FederateHandle) -> FederateHandle:
        federation = self._require_joined()
        if not isinstance(theFederateHandle, FederateHandle) or theFederateHandle not in federation.federates:
            raise InvalidFederateHandle(repr(theFederateHandle))
        return theFederateHandle

    def _svc_normalizeServiceGroup(self, theServiceGroup: Any):
        from ...enums import ServiceGroup
        self._require_joined()
        if isinstance(theServiceGroup, ServiceGroup):
            return theServiceGroup
        key = str(theServiceGroup).replace(" ", "_").replace("-", "_").upper()
        try:
            return ServiceGroup[key]
        except KeyError as exc:
            raise InvalidServiceGroup(str(theServiceGroup)) from exc

    def _svc_getAttributeHandleFactory(self) -> hla_handles.AttributeHandleFactory:
        self._require_joined()
        return hla_handles.AttributeHandleFactory()

    def _svc_getAttributeHandleSetFactory(self) -> hla_handles.AttributeHandleSetFactory:
        self._require_joined()
        return hla_handles.AttributeHandleSetFactory()

    def _svc_getAttributeHandleValueMapFactory(self) -> hla_handles.AttributeHandleValueMapFactory:
        self._require_joined()
        return hla_handles.AttributeHandleValueMapFactory()

    def _svc_getAttributeSetRegionSetPairListFactory(self) -> hla_handles.AttributeSetRegionSetPairListFactory:
        self._require_joined()
        return hla_handles.AttributeSetRegionSetPairListFactory()

    def _svc_getDimensionHandleFactory(self) -> hla_handles.DimensionHandleFactory:
        self._require_joined()
        return hla_handles.DimensionHandleFactory()

    def _svc_getDimensionHandleSetFactory(self) -> hla_handles.DimensionHandleSetFactory:
        self._require_joined()
        return hla_handles.DimensionHandleSetFactory()

    def _svc_getFederateHandleFactory(self) -> hla_handles.FederateHandleFactory:
        self._require_joined()
        return hla_handles.FederateHandleFactory()

    def _svc_getFederateHandleSetFactory(self) -> hla_handles.FederateHandleSetFactory:
        self._require_joined()
        return hla_handles.FederateHandleSetFactory()

    def _svc_getInteractionClassHandleFactory(self) -> hla_handles.InteractionClassHandleFactory:
        self._require_joined()
        return hla_handles.InteractionClassHandleFactory()

    def _svc_getObjectClassHandleFactory(self) -> hla_handles.ObjectClassHandleFactory:
        self._require_joined()
        return hla_handles.ObjectClassHandleFactory()

    def _svc_getObjectInstanceHandleFactory(self) -> hla_handles.ObjectInstanceHandleFactory:
        self._require_joined()
        return hla_handles.ObjectInstanceHandleFactory()

    def _svc_getParameterHandleFactory(self) -> hla_handles.ParameterHandleFactory:
        self._require_joined()
        return hla_handles.ParameterHandleFactory()

    def _svc_getParameterHandleValueMapFactory(self) -> hla_handles.ParameterHandleValueMapFactory:
        self._require_joined()
        return hla_handles.ParameterHandleValueMapFactory()

    def _svc_getRegionHandleSetFactory(self) -> hla_handles.RegionHandleSetFactory:
        self._require_joined()
        return hla_handles.RegionHandleSetFactory()

    def _svc_getTransportationTypeHandleFactory(self) -> hla_handles.TransportationTypeHandleFactory:
        self._require_joined()
        return hla_handles.TransportationTypeHandleFactory()

    def _svc_decodeMessageRetractionHandle(self, buffer: bytes) -> MessageRetractionHandle:
        return MessageRetractionHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeFederateHandle(self, buffer: bytes) -> FederateHandle:
        return FederateHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeObjectClassHandle(self, buffer: bytes) -> ObjectClassHandle:
        return ObjectClassHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeAttributeHandle(self, buffer: bytes) -> AttributeHandle:
        return AttributeHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeObjectInstanceHandle(self, buffer: bytes) -> ObjectInstanceHandle:
        return ObjectInstanceHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeInteractionClassHandle(self, buffer: bytes) -> InteractionClassHandle:
        return InteractionClassHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeParameterHandle(self, buffer: bytes) -> ParameterHandle:
        return ParameterHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeDimensionHandle(self, buffer: bytes) -> DimensionHandle:
        return DimensionHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeRegionHandle(self, buffer: bytes) -> RegionHandle:
        return RegionHandle.decode(buffer)  # type: ignore[return-value]


__all__ = [
    "PythonRTIBackend",
    "InMemoryRTIEngine",
    "PythonRTIConfig",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
]
