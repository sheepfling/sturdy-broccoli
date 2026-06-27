"""MOM/MIM object-state helpers for the in-memory Python RTI backend."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol

import hla.fom.mom as hla_mom
from hla.rti1516e.enums import OrderType
from hla.fom import FOMModule
from hla.rti1516e.handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle
from . import mom_catalog as mom_table
from .mom_actions import PythonRTIMomActionsMixin
from .mom_reporting import PythonRTIMomReportingMixin
from .state import (
    MOM_FEDERATE_CLASS,
    MOM_FEDERATION_CLASS,
    MOM_TEXT_ENCODING,
    RTI_FEDERATE_HANDLE,
    FederationState,
    ObjectInstance,
    SupplementalReflectInfo,
)

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState, PythonRTIConfig


class _MomContext(Protocol):
    engine: "InMemoryRTIEngine"
    config: "PythonRTIConfig"

    def _object_matches_subscription(self, actual_class: object, subscribed_class: object) -> bool: ...

    def _deliver(self, target: "FederateState", method_name: str, *args: Any) -> None: ...

    def _attribute_subscription_intersection(
        self,
        federate: "FederateState",
        object_class: object,
        attributes: Mapping[AttributeHandle, bytes],
        instance: ObjectInstance | None = None,
        sent_regions_by_attribute: Mapping[AttributeHandle, set[Any]] | None = None,
    ) -> dict[AttributeHandle, bytes]: ...

    def _require_joined(self) -> FederationState: ...

    def _svc_getHLAversion(self) -> str: ...

    def _compute_galt(self, federation: FederationState, federate: Any) -> Any: ...

    def _compute_lits(self, federation: FederationState, federate: Any) -> Any: ...


if TYPE_CHECKING:
    class _MomMixinBase(PythonRTIMomActionsMixin, PythonRTIMomReportingMixin, _MomContext):
        pass
else:
    class _MomMixinBase(PythonRTIMomActionsMixin, PythonRTIMomReportingMixin):
        pass


def _as_mom_bytes(value: Any) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if hasattr(value, "encode") and not isinstance(value, str):
        try:
            return value.encode()
        except Exception:
            pass
    return str(value).encode(MOM_TEXT_ENCODING)


def _handle_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _time_value(value: Any) -> float | int:
    from hla.backends.common import time_management as tm

    return tm.time_value(value)


class PythonRTIMomMixin(_MomMixinBase):
    """HLA MOM/MIM refresh, object state, report exposure, and dispatch helpers."""

    def _class_handle_by_name(self, name: str) -> ObjectClassHandle:
        return self.engine.get_or_create_object_class(name).handle

    def _interaction_handle_by_name(self, name: str) -> InteractionClassHandle:
        return self.engine.get_or_create_interaction_class(name).handle

    def _attr_handle_by_name(self, class_name: str, attr_name: str) -> AttributeHandle:
        return self.engine.get_or_create_attribute(self._class_handle_by_name(class_name), attr_name)

    def _param_handle_by_name(self, interaction_name: str, param_name: str) -> ParameterHandle:
        return self.engine.get_or_create_parameter(self._interaction_handle_by_name(interaction_name), param_name)

    def _mom_parameter_map(self, interaction_name: str, values: Mapping[str, Any]) -> dict[ParameterHandle, bytes]:
        return {
            self._param_handle_by_name(interaction_name, name): _as_mom_bytes(value)
            for name, value in values.items()
        }

    def _mom_attribute_map(self, class_name: str, values: Mapping[str, Any]) -> dict[AttributeHandle, bytes]:
        return {
            self._attr_handle_by_name(class_name, name): _as_mom_bytes(value)
            for name, value in values.items()
        }

    def _make_internal_object(
        self,
        federation: FederationState,
        class_name: str,
        object_name: str,
    ) -> ObjectInstance:
        class_handle = self._class_handle_by_name(class_name)
        existing = federation.object_names.get(object_name)
        if existing is not None:
            return federation.objects[existing]
        handle = self.engine._alloc(ObjectInstanceHandle)
        instance = ObjectInstance(
            handle=handle,
            class_handle=class_handle,
            name=object_name,
            owner=RTI_FEDERATE_HANDLE,
        )
        federation.objects[handle] = instance
        federation.object_names[object_name] = handle
        for federate in list(federation.federates.values()):
            if any(
                self._object_matches_subscription(class_handle, subscribed)
                for subscribed in federate.subscribed_objects
            ):
                self._deliver(
                    federate,
                    "discoverObjectInstance",
                    handle,
                    class_handle,
                    object_name,
                    RTI_FEDERATE_HANDLE,
                )
        return instance

    def _reflect_internal_attribute_update(
        self,
        federation: FederationState,
        instance: ObjectInstance,
        attributes: Mapping[AttributeHandle, bytes],
    ) -> None:
        for federate in list(federation.federates.values()):
            reflected = self._attribute_subscription_intersection(
                federate,
                instance.class_handle,
                attributes,
                instance,
            )
            if reflected:
                self._deliver(
                    federate,
                    "reflectAttributeValues",
                    instance.handle,
                    reflected,
                    b"MOM",
                    OrderType.RECEIVE,
                    self.engine.transportation_reliable,
                    SupplementalReflectInfo(producing_federate=RTI_FEDERATE_HANDLE),
                )

    def _set_internal_attributes(
        self,
        federation: FederationState,
        instance: ObjectInstance,
        attributes: Mapping[AttributeHandle, bytes],
        *,
        notify: bool = True,
    ) -> None:
        changed: dict[AttributeHandle, bytes] = {}
        for handle, value in attributes.items():
            value_bytes = bytes(value)
            if instance.attributes.get(handle) != value_bytes:
                changed[handle] = value_bytes
                instance.attributes[handle] = value_bytes
            instance.attribute_owners[handle] = RTI_FEDERATE_HANDLE
        if changed and notify:
            self._reflect_internal_attribute_update(federation, instance, changed)

    def _fom_module_designator_list(self, federation: FederationState) -> str:
        return "\n".join(module.uri for module in federation.fom_modules)

    def _fdd_summary_text(self, federation: FederationState) -> str:
        summary = federation.fom_catalog.as_summary()
        lines = [
            f"MIM={summary.get('mim_uri') or ''}",
            "FOMs=" + ";".join(summary.get("module_uris", [])),
            "Objects=" + ";".join(summary.get("object_classes", [])),
            "Interactions=" + ";".join(summary.get("interaction_classes", [])),
            "Dimensions=" + ";".join(summary.get("dimensions", [])),
            f"Time={summary.get('logical_time_implementation') or federation.time_factory.get_name()}",
        ]
        return "\n".join(lines)

    def _module_xml_or_uri(self, module: FOMModule | None) -> bytes:
        if module is None:
            return b""
        if module.path is not None and module.path.exists():
            try:
                return module.path.read_bytes()
            except OSError:
                pass
        return _as_mom_bytes(module.uri)

    def _all_fom_module_data(self, federation: FederationState) -> bytes:
        payloads: list[bytes] = []
        for index, module in enumerate(federation.fom_modules):
            payloads.append(f"--- FOM module {index}: {module.uri}\n".encode(MOM_TEXT_ENCODING))
            payloads.append(self._module_xml_or_uri(module))
            payloads.append(b"\n")
        return b"".join(payloads) if payloads else b""

    def _ensure_mom_federation_object(self, federation: FederationState) -> None:
        instance = self._make_internal_object(
            federation,
            MOM_FEDERATION_CLASS,
            f"HLAmanager.HLAfederation.{federation.name}",
        )
        federation.mom_federation_object = instance.handle
        self._refresh_mom_federation_object(federation, notify=False)

    def _ensure_mom_federate_object(self, federation: FederationState, federate) -> None:
        if federate.handle is None:
            return
        name = f"HLAmanager.HLAfederate.{federate.handle.value}.{federate.name or 'unnamed'}"
        instance = self._make_internal_object(federation, MOM_FEDERATE_CLASS, name)
        federation.mom_federate_objects[federate.handle] = instance.handle
        federate.mom_federate_object = instance.handle
        self._refresh_mom_federate_object(federation, federate, notify=False)

    def _refresh_mom_federation_object(
        self,
        federation: FederationState,
        *,
        notify: bool = True,
    ) -> None:
        if federation.mom_federation_object is None:
            return
        instance = federation.objects.get(federation.mom_federation_object)
        if instance is None:
            return
        raw_values = {
            "HLAfederationName": federation.name,
            "HLAfederatesInFederation": ",".join(
                sorted(f.name or _handle_value(h) for h, f in federation.federates.items())
            ),
            "HLARTIversion": self._svc_getHLAversion(),
            "HLAMIMdesignator": (
                federation.mim_module.uri
                if federation.mim_module
                else "builtin:HLAstandardMIM"
            ),
            "HLAFOMmoduleDesignatorList": self._fom_module_designator_list(federation),
            "HLAcurrentFDD": self._fdd_summary_text(federation),
            "HLAtimeImplementationName": federation.time_factory.get_name(),
            "HLAlastSaveName": federation.save_label or "",
            "HLAnextSaveName": federation.save_label or "",
            "HLAautoProvide": str(federation.mom_auto_provide).lower(),
        }
        values = self._filter_mom_attribute_values(
            federation,
            MOM_FEDERATION_CLASS,
            {name: _as_mom_bytes(value) for name, value in raw_values.items()},
        )
        attrs = {
            self._mom_attribute_handle(MOM_FEDERATION_CLASS, name): data
            for name, data in values.items()
        }
        self._set_internal_attributes(federation, instance, attrs, notify=notify)

    def _refresh_mom_federate_object(
        self,
        federation: FederationState,
        federate,
        *,
        notify: bool = True,
    ) -> None:
        if federate.handle is None or federate.mom_federate_object is None:
            return
        instance = federation.objects.get(federate.mom_federate_object)
        if instance is None:
            return
        galt = self._compute_galt(federation, federate)
        lits = self._compute_lits(federation, federate)
        raw_values = {
            "HLAfederateHandle": _handle_value(federate.handle),
            "HLAfederateName": federate.name or "",
            "HLAfederateType": federate.federate_type or "",
            "HLAfederateHost": "local-python",
            "HLARTIversion": self._svc_getHLAversion(),
            "HLAFOMmoduleDesignatorList": self._fom_module_designator_list(federation),
            "HLAtimeConstrained": str(federate.time_constrained_enabled).lower(),
            "HLAtimeRegulating": str(federate.time_regulation_enabled).lower(),
            "HLAasynchronousDelivery": str(federate.asynchronous_delivery_enabled).lower(),
            "HLAfederateState": "TimeAdvancing" if federate.time_advancing else "Granted",
            "HLAtimeManagerState": (
                federate.pending_time_advance.mode
                if federate.pending_time_advance
                else "Granted"
            ),
            "HLAlogicalTime": _time_value(federate.current_time),
            "HLAlookahead": _time_value(federate.lookahead) if federate.lookahead is not None else "",
            "HLAGALT": _time_value(galt.time) if galt.time_is_valid else "",
            "HLALITS": _time_value(lits.time) if lits.time_is_valid else "",
            "HLAobjectClassRelevanceAdvisorySwitch": str(
                federate.object_class_relevance_advisory
            ).lower(),
            "HLAattributeRelevanceAdvisorySwitch": str(
                federate.attribute_relevance_advisory
            ).lower(),
            "HLAattributeScopeAdvisorySwitch": str(
                federate.attribute_scope_advisory
            ).lower(),
            "HLAinteractionRelevanceAdvisorySwitch": str(
                federate.interaction_relevance_advisory
            ).lower(),
        }
        values = self._filter_mom_attribute_values(
            federation,
            MOM_FEDERATE_CLASS,
            {name: _as_mom_bytes(value) for name, value in raw_values.items()},
        )
        attrs = {
            self._mom_attribute_handle(MOM_FEDERATE_CLASS, name): data
            for name, data in values.items()
        }
        self._set_internal_attributes(federation, instance, attrs, notify=notify)

    def _refresh_all_mom_objects(
        self,
        federation: FederationState,
        *,
        notify: bool = True,
    ) -> None:
        self._refresh_mom_federation_object(federation, notify=notify)
        for federate in list(federation.federates.values()):
            self._refresh_mom_federate_object(federation, federate, notify=notify)

    def current_mom_summary(self) -> dict[str, Any]:
        federation = self._require_joined()
        return {
            "federation_object": federation.mom_federation_object,
            "federate_objects": dict(federation.mom_federate_objects),
            "synchronization_labels": sorted(federation.synchronization_points),
            "synchronization_points": {
                label: {
                    "targets": sorted(point.targets, key=lambda handle: handle.value),
                    "announced": sorted(point.announced, key=lambda handle: handle.value),
                    "achieved": sorted(point.achieved, key=lambda handle: handle.value),
                    "failed": sorted(point.failed, key=lambda handle: handle.value),
                    "reported": sorted(point.reported(), key=lambda handle: handle.value),
                    "open_to_late_joiners": point.open_to_late_joiners,
                }
                for label, point in sorted(federation.synchronization_points.items())
            },
            "save_label": federation.save_label,
            "save_status": {handle: status.name for handle, status in sorted(federation.save_status.items(), key=lambda item: item[0].value)},
            "restore_label": federation.restore_label,
            "restore_status": {
                handle: status.name for handle, status in sorted(federation.restore_status.items(), key=lambda item: item[0].value)
            },
            "last_save_name": federation.last_save_name,
            "next_save_name": federation.next_save_name,
            "callback_counts": dict(sorted(self.state.callback_counts.items())),
            "recent_callbacks": list(self.state.recent_callbacks),
            "mim_uri": federation.mim_module.uri if federation.mim_module else None,
            "mom_object_classes": sorted(
                name for name in federation.fom_catalog.object_classes if ".HLAmanager" in name
            ),
            "mom_interaction_classes": sorted(
                name
                for name in federation.fom_catalog.interaction_classes
                if ".HLAmanager" in name
            ),
            "mom_model": self._mom_exposure_model(federation).as_summary(),
            "mom_interaction_matrix": self._mom_exposure_model(federation).interaction_matrix(),
            "mom_object_matrix": self._mom_exposure_model(federation).object_matrix(),
        }

    def _is_mom_object_instance(
        self,
        federation: FederationState,
        instance: ObjectInstance,
    ) -> bool:
        try:
            class_name = self.engine.object_class_for_handle(instance.class_handle).name
        except Exception:
            return False
        return self.config.enable_mom and hla_mom.is_mom_object_class_name(class_name)

    def _ensure_mom_objects(self, federation: FederationState) -> None:
        if not self.config.enable_mom:
            return
        self._ensure_mom_federation_object(federation)
        for federate in list(federation.federates.values()):
            self._ensure_mom_federate_object(federation, federate)
        self._refresh_mom_attribute_values(federation)

    def _mom_attribute_handle(self, class_name: str, attribute_name: str) -> AttributeHandle:
        class_handle = self.engine.get_or_create_object_class(class_name).handle
        return self.engine.get_or_create_attribute(class_handle, attribute_name)

    def _mom_parameter_handle(
        self,
        interaction_name: str,
        parameter_name: str,
    ) -> ParameterHandle:
        interaction_handle = self.engine.get_or_create_interaction_class(interaction_name).handle
        return self.engine.get_or_create_parameter(interaction_handle, parameter_name)

    def _filter_mom_attribute_values(
        self,
        federation: FederationState,
        class_name: str,
        values: Mapping[str, bytes],
    ) -> dict[str, bytes]:
        rule = self._mom_object_rule(federation, class_name) if federation.fom_catalog.object_classes else None
        if rule is None:
            return dict(values)
        filtered: dict[str, bytes] = {}
        for name, data in values.items():
            canonical = mom_table.canonical_attribute_name(rule, name)
            if canonical in rule.attributes:
                filtered[canonical] = data
        return filtered

    def _refresh_mom_attribute_values(self, federation: FederationState) -> None:
        if not self.config.enable_mom:
            return
        self._refresh_mom_federation_object(federation, notify=False)
        for federate in list(federation.federates.values()):
            self._refresh_mom_federate_object(federation, federate, notify=False)

    def _deliver_mom_attribute_update(
        self,
        instance: ObjectInstance,
        attrs: set[AttributeHandle],
        tag: bytes,
    ) -> None:
        federation = self._require_joined()
        self._refresh_mom_attribute_values(federation)
        reflected = {
            handle: data
            for handle, data in instance.attributes.items()
            if not attrs or handle in attrs
        }
        if reflected:
            self._deliver(
                self.state,
                "reflectAttributeValues",
                instance.handle,
                reflected,
                tag,
                OrderType.RECEIVE,
                self.engine.transportation_reliable,
                SupplementalReflectInfo(producing_federate=None),
            )

    def _mom_exposure_model(self, federation: FederationState) -> mom_table.MOMExposureModel:
        if federation.mom_model is None:
            federation.mom_model = mom_table.build_mom_exposure_model(federation.fom_catalog)
        return federation.mom_model

    def _mom_interaction_rule(
        self,
        federation: FederationState,
        interaction_name: str,
    ) -> mom_table.MOMInteractionRule | None:
        return self._mom_exposure_model(federation).interaction_rule(interaction_name)

    def _mom_object_rule(
        self,
        federation: FederationState,
        class_name: str,
    ) -> mom_table.MOMObjectClassRule | None:
        return self._mom_exposure_model(federation).object_rule(class_name)
