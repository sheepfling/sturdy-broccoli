"""2025 RTI compatibility adapter for the backend-neutral Target/Radar scenario."""

from __future__ import annotations

from importlib import import_module
from importlib.resources import files
from pathlib import Path
from typing import Any


def _normalize_2025_callback_value(value: Any) -> Any:
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "")
    type_name = getattr(value_type, "__name__", "")

    if module_name == "hla.rti1516_2025.time" and type_name == "HLAinteger64Time":
        from hla.rti1516e.time import HLAinteger64Time

        return HLAinteger64Time(int(value.value))
    if module_name == "hla.rti1516_2025.time" and type_name == "HLAfloat64Time":
        from hla.rti1516e.time import HLAfloat64Time

        return HLAfloat64Time(float(value.value))
    if module_name == "hla.rti1516_2025.enums" and type_name == "OrderType":
        from hla.rti1516e.enums import OrderType

        return OrderType[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "SaveStatus":
        from hla.rti1516e.enums import SaveStatus

        return SaveStatus[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "RestoreStatus":
        from hla.rti1516e.enums import RestoreStatus

        return RestoreStatus[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "SaveFailureReason":
        from hla.rti1516e.enums import SaveFailureReason

        return SaveFailureReason[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "RestoreFailureReason":
        from hla.rti1516e.enums import RestoreFailureReason

        return RestoreFailureReason[value.name]
    if module_name == "hla.rti1516_2025.handles" and type_name in {
        "FederateHandle",
        "ObjectClassHandle",
        "InteractionClassHandle",
        "ObjectInstanceHandle",
        "AttributeHandle",
        "ParameterHandle",
        "DimensionHandle",
        "MessageRetractionHandle",
        "RegionHandle",
        "TransportationTypeHandle",
    }:
        from hla.rti1516e import handles as handles_2010

        return getattr(handles_2010, type_name)(int(value.value))
    if module_name == "hla.rti1516_2025.handles" and type_name.endswith("Set"):
        try:
            return {_normalize_2025_callback_value(item) for item in value}
        except TypeError:
            pass
    if module_name == "hla.rti1516_2025.datatypes" and type_name == "FederateHandleSaveStatusPair":
        from hla.rti1516e.datatypes import FederateHandleSaveStatusPair

        return FederateHandleSaveStatusPair(
            _normalize_2025_callback_value(value.handle),
            _normalize_2025_callback_value(value.status),
        )
    if module_name == "hla.rti1516_2025.datatypes" and type_name == "FederateRestoreStatus":
        from hla.rti1516e.datatypes import FederateRestoreStatus

        return FederateRestoreStatus(
            _normalize_2025_callback_value(value.preRestoreHandle),
            _normalize_2025_callback_value(value.postRestoreHandle),
            _normalize_2025_callback_value(value.status),
        )
    if module_name == "hla.rti1516_2025.datatypes" and type_name == "TimeQueryReturn":
        from hla.rti1516e.datatypes import TimeQueryReturn

        return TimeQueryReturn(
            bool(value.timeIsValid),
            _normalize_2025_callback_value(value.time),
        )
    if module_name == "hla.rti1516_2025.datatypes" and type_name == "MessageRetractionReturn":
        from hla.rti1516e.datatypes import MessageRetractionReturn

        return MessageRetractionReturn(
            bool(value.retractionHandleIsValid),
            _normalize_2025_callback_value(value.handle),
        )
    if isinstance(value, tuple):
        return tuple(_normalize_2025_callback_value(item) for item in value)
    if isinstance(value, list):
        return [_normalize_2025_callback_value(item) for item in value]
    if isinstance(value, set):
        return {_normalize_2025_callback_value(item) for item in value}
    if isinstance(value, dict):
        return {
            _normalize_2025_callback_value(key): _normalize_2025_callback_value(item)
            for key, item in value.items()
        }
    return value


class TargetRadar2025RTIAdapter:
    """Bridge the backend-neutral Target/Radar scenario onto the 2025 RTI surface."""

    _SPECIAL_METHOD_NAMES = {
        "create_federation_execution_with_mim": "createFederationExecutionWithMIM",
    }
    _HANDLE_CLASS_NAMES = (
        "FederateHandle",
        "ObjectClassHandle",
        "InteractionClassHandle",
        "ObjectInstanceHandle",
        "AttributeHandle",
        "ParameterHandle",
        "DimensionHandle",
        "MessageRetractionHandle",
        "RegionHandle",
        "TransportationTypeHandle",
    )

    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate
        self.backend_info = getattr(delegate, "backend_info", None)

    def _verification_spawn_like(self) -> "TargetRadar2025RTIAdapter":
        spawn = getattr(self._delegate, "_verification_spawn_like", None)
        if not callable(spawn):
            raise TypeError("TargetRadar2025RTIAdapter delegate does not support verification spawning")
        return type(self)(spawn())

    @staticmethod
    def _translate_exception(exc: Exception) -> Exception:
        exc_type = type(exc)
        if getattr(exc_type, "__module__", "") != "hla.rti1516_2025.exceptions":
            return exc
        from hla.rti1516e import exceptions as exceptions_2010

        compat_name = {
            "CouldNotOpenFOM": "CouldNotOpenFDD",
            "ErrorReadingFOM": "ErrorReadingFDD",
            "InconsistentFOM": "InconsistentFDD",
        }.get(exc_type.__name__, exc_type.__name__)
        compat_type = getattr(exceptions_2010, compat_name, None)
        if compat_type is None:
            return exc
        return compat_type(str(exc))

    def _call_compat(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            compat_exc = self._translate_exception(exc)
            if compat_exc is exc:
                raise
            raise compat_exc from exc

    def _delegate_callable(self, *names: str) -> Any:
        for name in names:
            candidate = getattr(self._delegate, name, None)
            if callable(candidate):
                return candidate
        raise AttributeError(names[0])

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        camel_name = self._SPECIAL_METHOD_NAMES.get(name)
        if camel_name is None and "_" in name:
            parts = name.split("_")
            camel_name = parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])
        if camel_name is not None:
            try:
                delegate_attr = getattr(self._delegate, camel_name)
                return (
                    (
                        lambda *args, **kwargs: _normalize_2025_callback_value(
                            self._call_compat(delegate_attr, *args, **kwargs)
                        )
                    )
                    if callable(delegate_attr)
                    else delegate_attr
                )
            except AttributeError:
                pass
        delegate_attr = getattr(self._delegate, name)
        return (
            (
                lambda *args, **kwargs: _normalize_2025_callback_value(
                    self._call_compat(delegate_attr, *args, **kwargs)
                )
            )
            if callable(delegate_attr)
            else delegate_attr
        )

    @staticmethod
    def _coerce_named_enum(enum_type: Any, value: Any) -> Any:
        member_name = getattr(value, "name", None)
        if isinstance(member_name, str) and member_name in enum_type.__members__:
            return enum_type[member_name]
        return value

    @staticmethod
    def _coerce_time_value(value: Any) -> Any:
        from hla.rti1516_2025.time import HLAfloat64Time, HLAinteger64Time

        if isinstance(value, (HLAinteger64Time, HLAfloat64Time)):
            return value
        if hasattr(value, "getValue"):
            scalar = value.getValue()
        elif hasattr(value, "value"):
            scalar = value.value
        else:
            scalar = value
        if isinstance(scalar, float):
            return HLAfloat64Time(float(scalar))
        return HLAinteger64Time(int(scalar))

    @classmethod
    def _to_2025_handle(cls, value: Any) -> Any:
        if value is None:
            return None
        value_type = type(value)
        if getattr(value_type, "__module__", "") == "hla.rti1516_2025.handles":
            return value
        type_name = getattr(value_type, "__name__", "")
        if getattr(value_type, "__module__", "") == "hla.rti1516e.handles" and type_name in cls._HANDLE_CLASS_NAMES:
            from hla.rti1516_2025 import handles as handles_2025

            return getattr(handles_2025, type_name)(int(value.value))
        return value

    @classmethod
    def _to_2010_handle(cls, value: Any) -> Any:
        if value is None:
            return None
        value_type = type(value)
        if getattr(value_type, "__module__", "") == "hla.rti1516e.handles":
            return value
        type_name = getattr(value_type, "__name__", "")
        if getattr(value_type, "__module__", "") == "hla.rti1516_2025.handles" and type_name in cls._HANDLE_CLASS_NAMES:
            from hla.rti1516e import handles as handles_2010

            return getattr(handles_2010, type_name)(int(value.value))
        return value

    @staticmethod
    def get_attribute_handle_factory():
        from hla.rti1516e.handles import AttributeHandleFactory

        return AttributeHandleFactory()

    @staticmethod
    def get_attribute_handle_set_factory():
        from hla.rti1516e.handles import AttributeHandleSetFactory

        return AttributeHandleSetFactory()

    @staticmethod
    def get_attribute_handle_value_map_factory():
        from hla.rti1516e.handles import AttributeHandleValueMapFactory

        return AttributeHandleValueMapFactory()

    @staticmethod
    def get_attribute_set_region_set_pair_list_factory():
        from hla.rti1516e.handles import AttributeSetRegionSetPairListFactory

        return AttributeSetRegionSetPairListFactory()

    @staticmethod
    def get_dimension_handle_factory():
        from hla.rti1516e.handles import DimensionHandleFactory

        return DimensionHandleFactory()

    @staticmethod
    def get_dimension_handle_set_factory():
        from hla.rti1516e.handles import DimensionHandleSetFactory

        return DimensionHandleSetFactory()

    @staticmethod
    def get_federate_handle_factory():
        from hla.rti1516e.handles import FederateHandleFactory

        return FederateHandleFactory()

    @staticmethod
    def get_federate_handle_set_factory():
        from hla.rti1516e.handles import FederateHandleSetFactory

        return FederateHandleSetFactory()

    @staticmethod
    def get_interaction_class_handle_factory():
        from hla.rti1516e.handles import InteractionClassHandleFactory

        return InteractionClassHandleFactory()

    @staticmethod
    def get_object_class_handle_factory():
        from hla.rti1516e.handles import ObjectClassHandleFactory

        return ObjectClassHandleFactory()

    @staticmethod
    def get_object_instance_handle_factory():
        from hla.rti1516e.handles import ObjectInstanceHandleFactory

        return ObjectInstanceHandleFactory()

    @staticmethod
    def get_parameter_handle_factory():
        from hla.rti1516e.handles import ParameterHandleFactory

        return ParameterHandleFactory()

    @staticmethod
    def get_parameter_handle_value_map_factory():
        from hla.rti1516e.handles import ParameterHandleValueMapFactory

        return ParameterHandleValueMapFactory()

    @staticmethod
    def get_region_handle_factory():
        from hla.rti1516e.handles import RegionHandleFactory

        return RegionHandleFactory()

    @staticmethod
    def get_region_handle_set_factory():
        from hla.rti1516e.handles import RegionHandleSetFactory

        return RegionHandleSetFactory()

    @staticmethod
    def get_message_retraction_handle_factory():
        from hla.rti1516e.handles import MessageRetractionHandleFactory

        return MessageRetractionHandleFactory()

    @staticmethod
    def get_transportation_type_handle_factory():
        from hla.rti1516e.handles import TransportationTypeHandleFactory

        return TransportationTypeHandleFactory()

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        pieces: list[str] = []
        for index, char in enumerate(name):
            if char.isupper() and index > 0:
                pieces.append("_")
            pieces.append(char.lower())
        return "".join(pieces)

    @classmethod
    def _wrap_federate_ambassador(cls, federate_ambassador: Any) -> Any:
        if federate_ambassador is None:
            return federate_ambassador

        class _CallbackCompatBridge:
            def __init__(self, delegate: Any) -> None:
                self._delegate = delegate

            def __getattr__(self, name: str) -> Any:
                snake_name = cls._camel_to_snake(name)
                snake_target = getattr(self._delegate, snake_name, None)
                if callable(snake_target):
                    def _wrapped(*args: Any, **kwargs: Any) -> Any:
                        normalized_args = tuple(_normalize_2025_callback_value(arg) for arg in args)
                        normalized_kwargs = {
                            key: _normalize_2025_callback_value(value)
                            for key, value in kwargs.items()
                        }
                        return snake_target(*normalized_args, **normalized_kwargs)

                    return _wrapped

                direct = getattr(self._delegate, name, None)
                if callable(direct):
                    return direct
                raise AttributeError(name)

        return _CallbackCompatBridge(federate_ambassador)

    def connect(self, federate_ambassador: Any, callback_model: Any) -> None:
        from hla.rti1516_2025.enums import CallbackModel

        self._call_compat(
            self._delegate.connect,
            self._wrap_federate_ambassador(federate_ambassador),
            self._coerce_named_enum(CallbackModel, callback_model),
        )

    def create_federation_execution(
        self,
        federation_name: str,
        fom_modules: Any,
        logical_time_implementation_name: str | None = None,
    ) -> None:
        if isinstance(fom_modules, (str, Path)):
            modules = [fom_modules]
        else:
            modules = list(fom_modules)
        standard_mim_designators = {"HLAstandardMIM", "HLAstandardMIM.xml", "resource:MIM.xml"}
        mim_modules = [module for module in modules if str(module) in standard_mim_designators]
        if mim_modules:
            fom_only_modules = [module for module in modules if str(module) not in standard_mim_designators]
            mim_module = mim_modules[0]
            if str(mim_module) in {"HLAstandardMIM", "HLAstandardMIM.xml"}:
                mim_module = str(files("hla.rti1516e.resources.foms").joinpath("HLAstandardMIM.xml"))
            create_with_mim = self._delegate_callable("createFederationExecutionWithMIM", "create_federation_execution_with_mim")
            self._call_compat(
                create_with_mim,
                federation_name,
                fom_only_modules,
                mim_module,
                logical_time_implementation_name,
            )
            return
        create = self._delegate_callable("createFederationExecution", "create_federation_execution")
        self._call_compat(create, federation_name, modules, logical_time_implementation_name)

    def join_federation_execution(
        self,
        federate_name: str,
        federate_type: str,
        federation_name: str,
        additional_fom_modules: Any = None,
    ) -> Any:
        join = self._delegate_callable("joinFederationExecution", "join_federation_execution")
        return self._to_2010_handle(
            self._call_compat(join, federate_name, federate_type, federation_name, additional_fom_modules)
        )

    def disconnect(self) -> None:
        self._call_compat(self._delegate_callable("disconnect"))

    def get_object_class_handle(self, object_class_name: str) -> Any:
        get_handle = self._delegate_callable("getObjectClassHandle", "get_object_class_handle")
        return self._to_2010_handle(self._call_compat(get_handle, object_class_name))

    def get_attribute_handle(self, object_class: Any, attribute_name: str) -> Any:
        get_handle = self._delegate_callable("getAttributeHandle", "get_attribute_handle")
        return self._to_2010_handle(
            self._call_compat(get_handle, self._to_2025_handle(object_class), attribute_name)
        )

    def publish_object_class_attributes(self, object_class: Any, attributes: Any) -> None:
        publish = self._delegate_callable("publishObjectClassAttributes", "publish_object_class_attributes")
        self._call_compat(
            publish,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def register_object_instance(self, object_class: Any, object_instance_name: str | None = None) -> Any:
        register = self._delegate_callable("registerObjectInstance", "register_object_instance")
        return self._to_2010_handle(
            self._call_compat(register, self._to_2025_handle(object_class), object_instance_name)
        )

    def update_attribute_values(self, object_instance: Any, attribute_values: Any, user_supplied_tag: bytes, time: Any = None) -> Any:
        normalized_values = {
            self._to_2025_handle(attribute): value
            for attribute, value in attribute_values.items()
        }
        update = self._delegate_callable("updateAttributeValues", "update_attribute_values")
        if time is None:
            return self._call_compat(
                update,
                self._to_2025_handle(object_instance),
                normalized_values,
                user_supplied_tag,
            )
        return self._call_compat(
            update,
            self._to_2025_handle(object_instance),
            normalized_values,
            user_supplied_tag,
            self._coerce_time_value(time),
        )

    def get_interaction_class_handle(self, interaction_class_name: str) -> Any:
        get_handle = self._delegate_callable("getInteractionClassHandle", "get_interaction_class_handle")
        return self._to_2010_handle(self._call_compat(get_handle, interaction_class_name))

    def get_parameter_handle(self, interaction_class: Any, parameter_name: str) -> Any:
        get_handle = self._delegate_callable("getParameterHandle", "get_parameter_handle")
        return self._to_2010_handle(
            self._call_compat(
                get_handle,
                self._to_2025_handle(interaction_class),
                parameter_name,
            )
        )

    def publish_interaction_class(self, interaction_class: Any) -> None:
        publish = self._delegate_callable("publishInteractionClass", "publish_interaction_class")
        self._call_compat(publish, self._to_2025_handle(interaction_class))

    def subscribe_object_class_attributes(self, object_class: Any, attributes: Any, *unused: Any, **kwargs: Any) -> None:
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"Unexpected subscription keyword arguments: {unexpected}")
        subscribe = self._delegate_callable("subscribeObjectClassAttributes", "subscribe_object_class_attributes")
        self._call_compat(
            subscribe,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
            *unused,
        )

    def request_attribute_value_update(self, object_instance: Any, attributes: Any, user_supplied_tag: bytes) -> None:
        request_update = self._delegate_callable("requestAttributeValueUpdate", "request_attribute_value_update")
        self._call_compat(
            request_update,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
            user_supplied_tag,
        )

    def send_interaction(self, interaction_class: Any, parameter_values: Any, user_supplied_tag: bytes, time: Any = None) -> Any:
        normalized_values = {
            self._to_2025_handle(parameter): value
            for parameter, value in parameter_values.items()
        }
        send = self._delegate_callable("sendInteraction", "send_interaction")
        if time is None:
            return _normalize_2025_callback_value(
                self._call_compat(
                    send,
                    self._to_2025_handle(interaction_class),
                    normalized_values,
                    user_supplied_tag,
                )
            )
        return _normalize_2025_callback_value(
            self._call_compat(
                send,
                self._to_2025_handle(interaction_class),
                normalized_values,
                user_supplied_tag,
                self._coerce_time_value(time),
            )
        )

    def time_advance_request(self, time: Any) -> None:
        request = self._delegate_callable("timeAdvanceRequest", "time_advance_request")
        request(self._coerce_time_value(time))

    def evoke_multiple_callbacks(self, minimum_seconds: float, maximum_seconds: float) -> bool:
        evoke = self._delegate_callable("evokeMultipleCallbacks", "evoke_multiple_callbacks")
        return evoke(minimum_seconds, maximum_seconds)

    def resign_federation_execution(self, resign_action: Any) -> None:
        from hla.rti1516_2025.enums import ResignAction

        resign = self._delegate_callable("resignFederationExecution", "resign_federation_execution")
        self._call_compat(
            resign,
            self._coerce_named_enum(ResignAction, resign_action),
        )

    def destroy_federation_execution(self, federation_name: str) -> None:
        destroy = self._delegate_callable("destroyFederationExecution", "destroy_federation_execution")
        self._call_compat(destroy, federation_name)


__all__ = ["TargetRadar2025RTIAdapter"]
