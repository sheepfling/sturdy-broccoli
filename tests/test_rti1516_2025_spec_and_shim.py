from __future__ import annotations

import ast
import inspect
import json
import struct
import uuid
import xml.etree.ElementTree as ET
from importlib.resources import files
from pathlib import Path

import pytest
from hla.backends.common import RecordingFederateAmbassador as CommonRecordingFederateAmbassador


class Recording2025FederateAmbassador:
    def __init__(self) -> None:
        self.callbacks: list[tuple[str, tuple[object, ...]]] = []

    def connectionLost(self, faultDescription) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("connectionLost", (faultDescription,)))

    def reportFederationExecutions(self, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutions", (report,)))

    def reportFederationExecutionMembers(self, federationName, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionMembers", (federationName, report)))

    def reportFederationExecutionDoesNotExist(self, federationName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionDoesNotExist", (federationName,)))

    def federateResigned(self, reasonForResignDescription) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federateResigned", (reasonForResignDescription,)))

    def synchronizationPointRegistrationSucceeded(self, synchronizationPointLabel) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("synchronizationPointRegistrationSucceeded", (synchronizationPointLabel,)))

    def synchronizationPointRegistrationFailed(self, synchronizationPointLabel, reason) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("synchronizationPointRegistrationFailed", (synchronizationPointLabel, reason)))

    def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("announceSynchronizationPoint", (synchronizationPointLabel, userSuppliedTag)))

    def federationSynchronized(self, synchronizationPointLabel, failedToSyncSet) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationSynchronized", (synchronizationPointLabel, failedToSyncSet)))

    def initiateFederateSave(self, label, time=None) -> None:  # noqa: N802, ANN001
        args = (label,) if time is None else (label, time)
        self.callbacks.append(("initiateFederateSave", args))

    def federationSaved(self) -> None:  # noqa: N802
        self.callbacks.append(("federationSaved", ()))

    def federationNotSaved(self, reason) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationNotSaved", (reason,)))

    def federationSaveStatusResponse(self, response) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationSaveStatusResponse", (response,)))

    def requestFederationRestoreSucceeded(self, label) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestFederationRestoreSucceeded", (label,)))

    def requestFederationRestoreFailed(self, label) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestFederationRestoreFailed", (label,)))

    def federationRestoreBegun(self) -> None:  # noqa: N802
        self.callbacks.append(("federationRestoreBegun", ()))

    def initiateFederateRestore(self, label, federateName, postRestoreFederateHandle) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("initiateFederateRestore", (label, federateName, postRestoreFederateHandle)))

    def federationRestored(self) -> None:  # noqa: N802
        self.callbacks.append(("federationRestored", ()))

    def federationNotRestored(self, reason) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationNotRestored", (reason,)))

    def federationRestoreStatusResponse(self, response) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federationRestoreStatusResponse", (response,)))

    def timeRegulationEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeRegulationEnabled", (time,)))

    def timeConstrainedEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeConstrainedEnabled", (time,)))

    def timeAdvanceGrant(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeAdvanceGrant", (time,)))

    def flushQueueGrant(self, time, optimisticTime) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("flushQueueGrant", (time, optimisticTime)))

    def requestRetraction(self, retraction) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestRetraction", (retraction,)))

    def momServiceReport(self, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("momServiceReport", (report,)))

    def objectInstanceNameReservationSucceeded(self, objectInstanceName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("objectInstanceNameReservationSucceeded", (objectInstanceName,)))

    def objectInstanceNameReservationFailed(self, objectInstanceName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("objectInstanceNameReservationFailed", (objectInstanceName,)))

    def multipleObjectInstanceNameReservationSucceeded(self, objectInstanceNames) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("multipleObjectInstanceNameReservationSucceeded", (objectInstanceNames,)))

    def multipleObjectInstanceNameReservationFailed(self, objectInstanceNames) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("multipleObjectInstanceNameReservationFailed", (objectInstanceNames,)))

    def discoverObjectInstance(self, objectInstance, objectClass, objectInstanceName, producingFederate) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("discoverObjectInstance", (objectInstance, objectClass, objectInstanceName, producingFederate)))

    def reflectAttributeValues(  # noqa: N802, ANN001
        self,
        objectInstance,
        attributeValues,
        userSuppliedTag,
        transportationType,
        producingFederate,
        optionalSentRegions,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "reflectAttributeValues",
                (
                    objectInstance,
                    attributeValues,
                    userSuppliedTag,
                    transportationType,
                    producingFederate,
                    optionalSentRegions,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def receiveInteraction(  # noqa: N802, ANN001
        self,
        interactionClass,
        parameterValues,
        userSuppliedTag,
        transportationType,
        producingFederate,
        optionalSentRegions,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "receiveInteraction",
                (
                    interactionClass,
                    parameterValues,
                    userSuppliedTag,
                    transportationType,
                    producingFederate,
                    optionalSentRegions,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def receiveDirectedInteraction(  # noqa: N802, ANN001
        self,
        interactionClass,
        objectInstance,
        parameterValues,
        userSuppliedTag,
        transportationType,
        producingFederate,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "receiveDirectedInteraction",
                (
                    interactionClass,
                    objectInstance,
                    parameterValues,
                    userSuppliedTag,
                    transportationType,
                    producingFederate,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def removeObjectInstance(  # noqa: N802, ANN001
        self,
        objectInstance,
        userSuppliedTag,
        producingFederate,
        time=None,
        sentOrderType=None,
        receivedOrderType=None,
        optionalRetraction=None,
    ) -> None:
        self.callbacks.append(
            (
                "removeObjectInstance",
                (
                    objectInstance,
                    userSuppliedTag,
                    producingFederate,
                    time,
                    sentOrderType,
                    receivedOrderType,
                    optionalRetraction,
                ),
            )
        )

    def attributesInScope(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributesInScope", (objectInstance, attributes)))

    def attributesOutOfScope(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributesOutOfScope", (objectInstance, attributes)))

    def provideAttributeValueUpdate(self, objectInstance, attributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("provideAttributeValueUpdate", (objectInstance, attributes, userSuppliedTag)))

    def confirmAttributeTransportationTypeChange(self, objectInstance, attributes, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("confirmAttributeTransportationTypeChange", (objectInstance, attributes, transportationType)))

    def reportAttributeTransportationType(self, objectInstance, attribute, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportAttributeTransportationType", (objectInstance, attribute, transportationType)))

    def confirmInteractionTransportationTypeChange(self, interactionClass, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("confirmInteractionTransportationTypeChange", (interactionClass, transportationType)))

    def reportInteractionTransportationType(self, federate, interactionClass, transportationType) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportInteractionTransportationType", (federate, interactionClass, transportationType)))

    def attributeOwnershipAcquisitionNotification(  # noqa: N802, ANN001
        self,
        objectInstance,
        securedAttributes,
        userSuppliedTag,
    ) -> None:
        self.callbacks.append(("attributeOwnershipAcquisitionNotification", (objectInstance, securedAttributes, userSuppliedTag)))

    def attributeOwnershipUnavailable(self, objectInstance, attributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributeOwnershipUnavailable", (objectInstance, attributes, userSuppliedTag)))

    def requestAttributeOwnershipAssumption(self, objectInstance, offeredAttributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestAttributeOwnershipAssumption", (objectInstance, offeredAttributes, userSuppliedTag)))

    def requestDivestitureConfirmation(self, objectInstance, releasedAttributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestDivestitureConfirmation", (objectInstance, releasedAttributes, userSuppliedTag)))

    def requestAttributeOwnershipRelease(self, objectInstance, candidateAttributes, userSuppliedTag) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("requestAttributeOwnershipRelease", (objectInstance, candidateAttributes, userSuppliedTag)))

    def confirmAttributeOwnershipAcquisitionCancellation(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("confirmAttributeOwnershipAcquisitionCancellation", (objectInstance, attributes)))

    def informAttributeOwnership(self, objectInstance, attributes, owner) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("informAttributeOwnership", (objectInstance, attributes, owner)))

    def attributeIsNotOwned(self, objectInstance, attributes) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("attributeIsNotOwned", (objectInstance, attributes)))

    def last_callback(self, method_name: str) -> tuple[object, ...] | None:
        for recorded_name, args in reversed(self.callbacks):
            if recorded_name == method_name:
                return args
        return None


def _callbacks_named_2025(
    federate: Recording2025FederateAmbassador,
    method_name: str,
) -> list[tuple[object, ...]]:
    return [args for recorded_name, args in federate.callbacks if recorded_name == method_name]


def _normalize_2025_callback_value(value):  # noqa: ANN001, ANN201
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "")
    type_name = getattr(value_type, "__name__", "")

    if module_name == "hla.rti1516_2025.time" and type_name == "HLAinteger64Time":
        from hla.rti1516e.time import HLAinteger64Time

        return HLAinteger64Time(int(value.value))
    if module_name == "hla.rti1516_2025.time" and type_name == "HLAinteger64Interval":
        from hla.rti1516e.time import HLAinteger64Interval

        return HLAinteger64Interval(int(value.value))
    if module_name == "hla.rti1516_2025.enums" and type_name == "OrderType":
        from hla.rti1516e.enums import OrderType

        return OrderType[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "SaveStatus":
        from hla.rti1516e.enums import SaveStatus

        return SaveStatus[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "RestoreStatus":
        from hla.rti1516e.enums import RestoreStatus

        return RestoreStatus[value.name]
    if module_name == "hla.rti1516_2025.enums" and type_name == "SynchronizationPointFailureReason":
        from hla.rti1516e.enums import SynchronizationPointFailureReason

        return SynchronizationPointFailureReason[value.name]
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


class _TargetRadar2025RTIAdapter:
    """Minimal version bridge for the backend-neutral target/radar scenario."""

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

    def __init__(self, delegate) -> None:  # noqa: ANN001
        self._delegate = delegate
        self.backend_info = getattr(delegate, "backend_info", None)
        self._joined_federate_handle = None

    @staticmethod
    def _translate_exception(exc: Exception) -> Exception:
        exc_type = type(exc)
        if getattr(exc_type, "__module__", "") != "hla.rti1516_2025.exceptions":
            return exc
        from hla.rti1516e import exceptions as exceptions_2010

        compat_type = getattr(exceptions_2010, exc_type.__name__, None)
        if compat_type is None:
            return exc
        return compat_type(str(exc))

    def _call_compat(self, func, *args, **kwargs):  # noqa: ANN001, ANN201
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            compat_exc = self._translate_exception(exc)
            if compat_exc is exc:
                raise
            raise compat_exc from exc

    def __getattr__(self, name: str):  # noqa: ANN201
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
                    (lambda *args, **kwargs: self._call_compat(delegate_attr, *args, **kwargs))
                    if callable(delegate_attr)
                    else delegate_attr
                )
            except AttributeError:
                pass
        try:
            delegate_attr = getattr(self._delegate, name)
            return (
                (lambda *args, **kwargs: self._call_compat(delegate_attr, *args, **kwargs))
                if callable(delegate_attr)
                else delegate_attr
            )
        except AttributeError as exc:
            raise exc

    @staticmethod
    def _coerce_named_enum(enum_type, value):  # noqa: ANN001, ANN205
        member_name = getattr(value, "name", None)
        if isinstance(member_name, str) and member_name in enum_type.__members__:
            return enum_type[member_name]
        return value

    @staticmethod
    def _coerce_time_value(value):  # noqa: ANN001, ANN205
        from hla.rti1516_2025.time import HLAinteger64Time

        if isinstance(value, HLAinteger64Time):
            return value
        if hasattr(value, "getValue"):
            return HLAinteger64Time(int(value.getValue()))
        if hasattr(value, "value"):
            return HLAinteger64Time(int(value.value))
        return HLAinteger64Time(int(value))

    @staticmethod
    def _coerce_interval_value(value):  # noqa: ANN001, ANN205
        from hla.rti1516_2025.time import HLAinteger64Interval

        if isinstance(value, HLAinteger64Interval):
            return value
        if hasattr(value, "getValue"):
            return HLAinteger64Interval(int(value.getValue()))
        if hasattr(value, "value"):
            return HLAinteger64Interval(int(value.value))
        return HLAinteger64Interval(int(value))

    @classmethod
    def _to_2025_handle(cls, value):  # noqa: ANN001, ANN205
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
    def _to_2010_handle(cls, value):  # noqa: ANN001, ANN205
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

    def connect(self, federate_ambassador, callback_model) -> None:  # noqa: ANN001
        from hla.rti1516_2025.enums import CallbackModel

        self._call_compat(
            self._delegate.connect,
            federate_ambassador,
            self._coerce_named_enum(CallbackModel, callback_model),
        )

    def create_federation_execution(
        self,
        federation_name: str,
        fom_modules,
        logical_time_implementation_name: str | None = None,
    ) -> None:  # noqa: ANN001
        modules = list(fom_modules)
        kwargs = {"federationName": federation_name}
        if len(modules) == 1:
            kwargs["fomModule"] = modules[0]
        else:
            kwargs["fomModules"] = modules
        if logical_time_implementation_name is not None:
            kwargs["logicalTimeImplementationName"] = logical_time_implementation_name
        self._call_compat(self._delegate.createFederationExecution, **kwargs)

    def create_federation_execution_with_mim(
        self,
        federation_name: str,
        fom_modules,
        logical_time_implementation_name: str | None = None,
    ) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.createFederationExecutionWithMIM,
            federationName=federation_name,
            fomModules=list(fom_modules),
            mimModule="resource:MIM.xml",
            logicalTimeImplementationName=logical_time_implementation_name,
        )

    def join_federation_execution(self, federate_name: str, federate_type: str, federation_name: str):  # noqa: ANN201
        handle = self._call_compat(
            self._delegate.joinFederationExecution,
            federateName=federate_name,
            federateType=federate_type,
            federationName=federation_name,
        )
        self._joined_federate_handle = self._to_2010_handle(handle)
        handle_type = type(handle)
        if getattr(handle_type, "__module__", "") == "hla.rti1516_2025.handles" and getattr(handle_type, "__name__", "") == "FederateHandle":
            from hla.rti1516e.handles import FederateHandle

            return FederateHandle(int(handle.value))
        return handle

    def disconnect(self) -> None:
        self._call_compat(self._delegate.disconnect)

    def get_federate_handle(self, federate_name: str):  # noqa: ANN201
        handle = self._call_compat(self._delegate.getFederateHandle, federate_name)
        handle_type = type(handle)
        if getattr(handle_type, "__module__", "") == "hla.rti1516_2025.handles" and getattr(handle_type, "__name__", "") == "FederateHandle":
            from hla.rti1516e.handles import FederateHandle

            return FederateHandle(int(handle.value))
        return handle

    def get_federate_name(self, federate_handle):  # noqa: ANN001, ANN201
        return self._delegate.getFederateName(self._to_2025_handle(federate_handle))

    def reserve_object_instance_name(self, object_instance_name: str) -> None:
        self._delegate.reserveObjectInstanceName(object_instance_name)

    def time_advance_request(self, time) -> None:  # noqa: ANN001
        self._delegate.timeAdvanceRequest(self._coerce_time_value(time))

    def time_advance_request_available(self, time) -> None:  # noqa: ANN001
        self._delegate.timeAdvanceRequestAvailable(self._coerce_time_value(time))

    def next_message_request_available(self, time) -> None:  # noqa: ANN001
        self._delegate.nextMessageRequestAvailable(self._coerce_time_value(time))

    def next_message_request(self, time) -> None:  # noqa: ANN001
        self._delegate.nextMessageRequest(self._coerce_time_value(time))

    def get_object_class_handle(self, object_class_name: str):  # noqa: ANN201
        return self._to_2010_handle(self._call_compat(self._delegate.getObjectClassHandle, object_class_name))

    def get_attribute_handle(self, object_class, attribute_name: str):  # noqa: ANN001, ANN201
        return self._to_2010_handle(
            self._call_compat(self._delegate.getAttributeHandle, self._to_2025_handle(object_class), attribute_name)
        )

    def publish_object_class_attributes(self, object_class, attributes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.publishObjectClassAttributes,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def subscribe_object_class_attributes(self, object_class, attributes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.subscribeObjectClassAttributes,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def subscribe_object_class_attributes_passively(self, object_class, attributes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.subscribeObjectClassAttributesPassively,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def unsubscribe_object_class_attributes(self, object_class, attributes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.unsubscribeObjectClassAttributes,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def unsubscribe_object_class(self, object_class) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.unsubscribeObjectClass,
            self._to_2025_handle(object_class),
        )

    def unpublish_object_class(self, object_class) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.unpublishObjectClass,
            self._to_2025_handle(object_class),
        )

    def unpublish_object_class_attributes(self, object_class, attributes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.unpublishObjectClassAttributes,
            self._to_2025_handle(object_class),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def register_object_instance(self, object_class, object_instance_name: str | None = None):  # noqa: ANN001, ANN201
        return self._to_2010_handle(
            self._call_compat(self._delegate.registerObjectInstance, self._to_2025_handle(object_class), object_instance_name)
        )

    def update_attribute_values(self, object_instance, attribute_values, user_supplied_tag: bytes, time=None) -> None:  # noqa: ANN001
        normalized_values = {
            self._to_2025_handle(attribute): value
            for attribute, value in attribute_values.items()
        }
        if time is None:
            self._call_compat(
                self._delegate.updateAttributeValues,
                self._to_2025_handle(object_instance),
                normalized_values,
                user_supplied_tag,
            )
            return
        self._call_compat(
            self._delegate.updateAttributeValues,
            self._to_2025_handle(object_instance),
            normalized_values,
            user_supplied_tag,
            self._coerce_time_value(time),
        )

    def request_attribute_value_update(self, object_instance, attributes, user_supplied_tag: bytes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.requestAttributeValueUpdate,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
            user_supplied_tag,
        )

    def request_attribute_transportation_type_change(
        self,
        object_instance,
        attributes,
        transportation_type,
    ) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.requestAttributeTransportationTypeChange,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
            self._to_2025_handle(transportation_type),
        )

    def query_attribute_transportation_type(self, object_instance, attribute) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.queryAttributeTransportationType,
            self._to_2025_handle(object_instance),
            self._to_2025_handle(attribute),
        )

    def request_interaction_transportation_type_change(self, interaction_class, transportation_type) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.requestInteractionTransportationTypeChange,
            self._to_2025_handle(interaction_class),
            self._to_2025_handle(transportation_type),
        )

    def query_interaction_transportation_type(self, interaction_class) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.queryInteractionTransportationType,
            self._to_2025_handle(self._joined_federate_handle),
            self._to_2025_handle(interaction_class),
        )

    def unconditional_attribute_ownership_divestiture(
        self,
        object_instance,
        attributes,
        user_supplied_tag: bytes = b"",
    ) -> None:  # noqa: ANN001
        self._delegate.unconditionalAttributeOwnershipDivestiture(
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
            user_supplied_tag,
        )

    def attribute_ownership_acquisition_if_available(
        self,
        object_instance,
        desired_attributes,
        user_supplied_tag: bytes = b"",
    ) -> None:  # noqa: ANN001
        self._delegate.attributeOwnershipAcquisitionIfAvailable(
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in desired_attributes},
            user_supplied_tag,
        )

    def attribute_ownership_acquisition(
        self,
        object_instance,
        desired_attributes,
        user_supplied_tag: bytes = b"",
    ) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.attributeOwnershipAcquisition,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in desired_attributes},
            user_supplied_tag,
        )

    def negotiated_attribute_ownership_divestiture(
        self,
        object_instance,
        attributes,
        user_supplied_tag: bytes = b"",
    ) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.negotiatedAttributeOwnershipDivestiture,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
            user_supplied_tag,
        )

    def confirm_divestiture(
        self,
        object_instance,
        confirmed_attributes,
        user_supplied_tag: bytes = b"",
    ) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.confirmDivestiture,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in confirmed_attributes},
            user_supplied_tag,
        )

    def attribute_ownership_divestiture_if_wanted(self, object_instance, attributes):  # noqa: ANN001, ANN201
        return {
            self._to_2010_handle(attribute)
            for attribute in self._call_compat(
                self._delegate.attributeOwnershipDivestitureIfWanted,
                self._to_2025_handle(object_instance),
                {self._to_2025_handle(attribute) for attribute in attributes},
            )
        }

    def cancel_attribute_ownership_acquisition(self, object_instance, attributes) -> None:  # noqa: ANN001
        self._call_compat(
            self._delegate.cancelAttributeOwnershipAcquisition,
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
        )

    def attribute_ownership_release_denied(
        self,
        object_instance,
        attributes,
        user_supplied_tag: bytes = b"",
    ) -> None:  # noqa: ANN001
        try:
            self._call_compat(
                self._delegate.attributeOwnershipReleaseDenied,
                self._to_2025_handle(object_instance),
                {self._to_2025_handle(attribute) for attribute in attributes},
                user_supplied_tag,
            )
        except TypeError:
            self._call_compat(
                self._delegate.attributeOwnershipReleaseDenied,
                self._to_2025_handle(object_instance),
                {self._to_2025_handle(attribute) for attribute in attributes},
            )

    def query_attribute_ownership(self, object_instance, attributes) -> None:  # noqa: ANN001
        normalized_attributes = attributes
        if not isinstance(attributes, (set, frozenset, list, tuple)):
            normalized_attributes = {attributes}
        self._delegate.queryAttributeOwnership(
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in normalized_attributes},
        )

    def change_attribute_order_type(self, object_instance, attributes, order_type) -> None:  # noqa: ANN001
        from hla.rti1516_2025.enums import OrderType

        self._delegate.changeAttributeOrderType(
            self._to_2025_handle(object_instance),
            {self._to_2025_handle(attribute) for attribute in attributes},
            self._coerce_named_enum(OrderType, order_type),
        )

    def get_interaction_class_handle(self, interaction_class_name: str):  # noqa: ANN201
        return self._to_2010_handle(self._call_compat(self._delegate.getInteractionClassHandle, interaction_class_name))

    def get_parameter_handle(self, interaction_class, parameter_name: str):  # noqa: ANN001, ANN201
        return self._to_2010_handle(
            self._call_compat(
                self._delegate.getParameterHandle,
                self._to_2025_handle(interaction_class),
                parameter_name,
            )
        )

    def publish_interaction_class(self, interaction_class) -> None:  # noqa: ANN001
        self._call_compat(self._delegate.publishInteractionClass, self._to_2025_handle(interaction_class))

    def subscribe_interaction_class(self, interaction_class) -> None:  # noqa: ANN001
        self._call_compat(self._delegate.subscribeInteractionClass, self._to_2025_handle(interaction_class))

    def subscribe_interaction_class_passively(self, interaction_class) -> None:  # noqa: ANN001
        self._call_compat(self._delegate.subscribeInteractionClassPassively, self._to_2025_handle(interaction_class))

    def unsubscribe_interaction_class(self, interaction_class) -> None:  # noqa: ANN001
        self._call_compat(self._delegate.unsubscribeInteractionClass, self._to_2025_handle(interaction_class))

    def unpublish_interaction_class(self, interaction_class) -> None:  # noqa: ANN001
        self._call_compat(self._delegate.unpublishInteractionClass, self._to_2025_handle(interaction_class))

    def send_interaction(self, interaction_class, parameter_values, user_supplied_tag: bytes, time=None) -> None:  # noqa: ANN001
        from hla.rti1516_2025.exceptions import InvalidLogicalTime as InvalidLogicalTime2025
        from hla.rti1516e.exceptions import InvalidLogicalTime as InvalidLogicalTime2010

        if time is None:
            self._call_compat(
                self._delegate.sendInteraction,
                self._to_2025_handle(interaction_class),
                {self._to_2025_handle(parameter): value for parameter, value in parameter_values.items()},
                user_supplied_tag,
            )
            return
        try:
            self._call_compat(
                self._delegate.sendInteraction,
                self._to_2025_handle(interaction_class),
                {self._to_2025_handle(parameter): value for parameter, value in parameter_values.items()},
                user_supplied_tag,
                self._coerce_time_value(time),
            )
        except InvalidLogicalTime2025 as exc:
            raise InvalidLogicalTime2010(str(exc)) from exc

    def enable_time_regulation(self, lookahead) -> None:  # noqa: ANN001
        self._delegate.enableTimeRegulation(self._coerce_interval_value(lookahead))

    def enable_time_constrained(self) -> None:
        self._delegate.enableTimeConstrained()

    def query_galt(self):  # noqa: ANN201
        return self._delegate.queryGALT()

    def query_lits(self):  # noqa: ANN201
        return self._delegate.queryLITS()

    def query_logical_time(self):  # noqa: ANN201
        return _normalize_2025_callback_value(self._delegate.queryLogicalTime())

    def get_time_factory(self):  # noqa: ANN201
        from hla.rti1516e.time import HLAfloat64TimeFactory, HLAinteger64TimeFactory

        factory = self._delegate.getTimeFactory()
        factory_name = getattr(factory, "name", None) or getattr(factory, "NAME", None) or factory.getName()
        if factory_name == "HLAinteger64Time":
            return HLAinteger64TimeFactory()
        if factory_name == "HLAfloat64Time":
            return HLAfloat64TimeFactory()
        raise AssertionError(f"Unsupported 2025 time factory for compat adapter: {factory_name}")

    def get_attribute_name(self, object_class, attribute) -> str:  # noqa: ANN001
        return self._call_compat(
            self._delegate.getAttributeName,
            self._to_2025_handle(object_class),
            self._to_2025_handle(attribute),
        )

    def get_interaction_class_name(self, interaction_class) -> str:  # noqa: ANN001
        return self._call_compat(self._delegate.getInteractionClassName, self._to_2025_handle(interaction_class))

    def get_known_object_class_handle(self, object_instance):  # noqa: ANN001, ANN201
        return self._to_2010_handle(
            self._call_compat(self._delegate.getKnownObjectClassHandle, self._to_2025_handle(object_instance))
        )

    def get_object_class_name(self, object_class) -> str:  # noqa: ANN001
        return self._call_compat(self._delegate.getObjectClassName, self._to_2025_handle(object_class))

    def get_object_instance_handle(self, object_instance_name: str):  # noqa: ANN201
        return self._to_2010_handle(self._call_compat(self._delegate.getObjectInstanceHandle, object_instance_name))

    def get_object_instance_name(self, object_instance) -> str:  # noqa: ANN001
        return self._call_compat(self._delegate.getObjectInstanceName, self._to_2025_handle(object_instance))

    def get_order_name(self, order_type) -> str:  # noqa: ANN001
        from hla.rti1516_2025.enums import OrderType

        return self._call_compat(self._delegate.getOrderName, self._coerce_named_enum(OrderType, order_type))

    def get_order_type(self, order_type_name: str):  # noqa: ANN201
        from hla.rti1516e.enums import OrderType as OrderType2010

        order_type = self._call_compat(self._delegate.getOrderType, order_type_name)
        return OrderType2010[getattr(order_type, "name", str(order_type))]

    def get_parameter_name(self, interaction_class, parameter) -> str:  # noqa: ANN001
        return self._call_compat(
            self._delegate.getParameterName,
            self._to_2025_handle(interaction_class),
            self._to_2025_handle(parameter),
        )

    def get_transportation_type_handle(self, transportation_type_name: str):  # noqa: ANN201
        return self._to_2010_handle(self._call_compat(self._delegate.getTransportationTypeHandle, transportation_type_name))

    def get_transportation_type_name(self, transportation_type) -> str:  # noqa: ANN001
        return self._call_compat(self._delegate.getTransportationTypeName, self._to_2025_handle(transportation_type))

    @staticmethod
    def get_transportation_type(transportation_name: str):  # noqa: ANN201
        from hla.rti1516e.enums import TransportationType

        normalized = transportation_name.strip()
        mapping = {
            "HLAreliable": TransportationType.RELIABLE,
            "HLAbestEffort": TransportationType.BEST_EFFORT,
        }
        return mapping[normalized]

    @staticmethod
    def get_transportation_name(transportation_type) -> str:  # noqa: ANN001
        member_name = getattr(transportation_type, "name", "")
        mapping = {
            "RELIABLE": "HLAreliable",
            "BEST_EFFORT": "HLAbestEffort",
        }
        return mapping[member_name]

    @staticmethod
    def get_attribute_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import AttributeHandleFactory

        return AttributeHandleFactory()

    @staticmethod
    def get_attribute_handle_set_factory():  # noqa: ANN201
        from hla.rti1516e.handles import AttributeHandleSetFactory

        return AttributeHandleSetFactory()

    @staticmethod
    def get_attribute_handle_value_map_factory():  # noqa: ANN201
        from hla.rti1516e.handles import AttributeHandleValueMapFactory

        return AttributeHandleValueMapFactory()

    @staticmethod
    def get_attribute_set_region_set_pair_list_factory():  # noqa: ANN201
        from hla.rti1516e.handles import AttributeSetRegionSetPairListFactory

        return AttributeSetRegionSetPairListFactory()

    @staticmethod
    def get_dimension_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import DimensionHandleFactory

        return DimensionHandleFactory()

    @staticmethod
    def get_dimension_handle_set_factory():  # noqa: ANN201
        from hla.rti1516e.handles import DimensionHandleSetFactory

        return DimensionHandleSetFactory()

    @staticmethod
    def get_federate_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import FederateHandleFactory

        return FederateHandleFactory()

    @staticmethod
    def get_federate_handle_set_factory():  # noqa: ANN201
        from hla.rti1516e.handles import FederateHandleSetFactory

        return FederateHandleSetFactory()

    @staticmethod
    def get_interaction_class_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import InteractionClassHandleFactory

        return InteractionClassHandleFactory()

    @staticmethod
    def get_object_class_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import ObjectClassHandleFactory

        return ObjectClassHandleFactory()

    @staticmethod
    def get_object_instance_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import ObjectInstanceHandleFactory

        return ObjectInstanceHandleFactory()

    @staticmethod
    def get_parameter_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import ParameterHandleFactory

        return ParameterHandleFactory()

    @staticmethod
    def get_parameter_handle_value_map_factory():  # noqa: ANN201
        from hla.rti1516e.handles import ParameterHandleValueMapFactory

        return ParameterHandleValueMapFactory()

    @staticmethod
    def get_region_handle_set_factory():  # noqa: ANN201
        from hla.rti1516e.handles import RegionHandleSetFactory

        return RegionHandleSetFactory()

    @staticmethod
    def get_transportation_type_handle_factory():  # noqa: ANN201
        from hla.rti1516e.handles import TransportationTypeHandleFactory

        return TransportationTypeHandleFactory()

    def normalize_federate_handle(self, federate_handle) -> int:  # noqa: ANN001
        return int(self._call_compat(self._delegate.normalizeFederateHandle, self._to_2025_handle(federate_handle)))

    @staticmethod
    def decode_attribute_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import AttributeHandle

        return AttributeHandle.decode(data, offset)

    @staticmethod
    def decode_dimension_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import DimensionHandle

        return DimensionHandle.decode(data, offset)

    @staticmethod
    def decode_federate_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import FederateHandle

        return FederateHandle.decode(data, offset)

    @staticmethod
    def decode_interaction_class_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import InteractionClassHandle

        return InteractionClassHandle.decode(data, offset)

    @staticmethod
    def decode_message_retraction_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import MessageRetractionHandle

        return MessageRetractionHandle.decode(data, offset)

    @staticmethod
    def decode_object_class_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import ObjectClassHandle

        return ObjectClassHandle.decode(data, offset)

    @staticmethod
    def decode_object_instance_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import ObjectInstanceHandle

        return ObjectInstanceHandle.decode(data, offset)

    @staticmethod
    def decode_parameter_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import ParameterHandle

        return ParameterHandle.decode(data, offset)

    @staticmethod
    def decode_region_handle(data: bytes, offset: int = 0):  # noqa: ANN201
        from hla.rti1516e.handles import RegionHandle

        return RegionHandle.decode(data, offset)

    def change_interaction_order_type(self, interaction_class, order_type) -> None:  # noqa: ANN001
        from hla.rti1516_2025.enums import OrderType

        self._delegate.changeInteractionOrderType(
            self._to_2025_handle(interaction_class),
            self._coerce_named_enum(OrderType, order_type),
        )

    def request_federation_save(self, label: str, time=None) -> None:  # noqa: ANN001
        if time is None:
            self._call_compat(self._delegate.requestFederationSave, label)
            return
        self._call_compat(self._delegate.requestFederationSave, label, self._coerce_time_value(time))

    def federate_save_begun(self) -> None:
        self._delegate.federateSaveBegun()

    def federate_save_complete(self) -> None:
        self._delegate.federateSaveComplete()

    def request_federation_restore(self, label: str) -> None:
        self._call_compat(self._delegate.requestFederationRestore, label)

    def federate_restore_complete(self) -> None:
        self._delegate.federateRestoreComplete()

    def federate_save_not_complete(self) -> None:
        self._delegate.federateSaveNotComplete()

    def federate_restore_not_complete(self) -> None:
        self._delegate.federateRestoreNotComplete()

    def abort_federation_save(self) -> None:
        self._call_compat(self._delegate.abortFederationSave)

    def abort_federation_restore(self) -> None:
        self._call_compat(self._delegate.abortFederationRestore)

    def delete_object_instance(self, object_instance, user_supplied_tag: bytes, time=None) -> None:  # noqa: ANN001
        if time is None:
            self._call_compat(
                self._delegate.deleteObjectInstance,
                self._to_2025_handle(object_instance),
                user_supplied_tag,
            )
            return
        self._call_compat(
            self._delegate.deleteObjectInstance,
            self._to_2025_handle(object_instance),
            user_supplied_tag,
            self._coerce_time_value(time),
        )

    def is_attribute_owned_by_federate(self, object_instance, attribute) -> bool:  # noqa: ANN001
        return bool(
            self._call_compat(
                self._delegate.isAttributeOwnedByFederate,
                self._to_2025_handle(object_instance),
                self._to_2025_handle(attribute),
            )
        )

    def query_federation_save_status(self) -> None:
        self._call_compat(self._delegate.queryFederationSaveStatus)

    def query_federation_restore_status(self) -> None:
        self._call_compat(self._delegate.queryFederationRestoreStatus)

    def resign_federation_execution(self, resign_action) -> None:  # noqa: ANN001
        from hla.rti1516_2025.enums import ResignAction

        self._call_compat(
            self._delegate.resignFederationExecution,
            self._coerce_named_enum(ResignAction, resign_action),
        )

    def destroy_federation_execution(self, federation_name: str) -> None:
        self._call_compat(self._delegate.destroyFederationExecution, federationName=federation_name)

    def enable_callbacks(self) -> None:
        self._delegate.enableCallbacks()

    def disable_callbacks(self) -> None:
        self._delegate.disableCallbacks()

    def evoke_callback(self, minimum_seconds: float) -> bool:
        return self._delegate.evokeMultipleCallbacks(minimum_seconds, minimum_seconds)

    def evoke_multiple_callbacks(self, minimum_seconds: float, maximum_seconds: float) -> bool:
        return self._delegate.evokeMultipleCallbacks(minimum_seconds, maximum_seconds)


def _adapter_service_methods(cls: type[object]) -> set[str]:
    return {
        name
        for name, value in cls.__dict__.items()
        if callable(value) and not name.startswith("_")
    }


def _scan_target_radar_rti_methods(path: Path) -> set[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()

    class _Visitor(ast.NodeVisitor):
        def visit_Attribute(self, node: ast.Attribute) -> None:
            if isinstance(node.value, ast.Name) and node.value.id.endswith("_rti"):
                names.add(node.attr)
            self.generic_visit(node)

    _Visitor().visit(module)
    return names


class _CompatRecordingFederateAmbassador(CommonRecordingFederateAmbassador):
    """Record callbacks after normalizing 2025 callback values to 2010-compatible types."""

    def record_callback(self, method_name: str, *args, **kwargs):  # noqa: ANN001, ANN201
        if method_name == "reportFederationExecutions" and len(args) == 1 and isinstance(args[0], set):
            if all(isinstance(item, tuple) and len(item) == 2 for item in args[0]):
                args = (
                    [
                        {
                            "federationExecutionName": federation_name,
                            "logicalTimeImplementationName": logical_time_name,
                        }
                        for federation_name, logical_time_name in args[0]
                    ],
                )
            else:
                args = (list(args[0]),)
        if method_name == "reportFederationExecutionMembers" and len(args) == 2 and isinstance(args[1], set):
            if all(isinstance(item, tuple) and len(item) == 2 for item in args[1]):
                args = (
                    args[0],
                    [
                        {
                            "federateName": federate_name,
                            "federateType": federate_type,
                        }
                        for federate_name, federate_type in args[1]
                    ],
                )
            else:
                args = (args[0], list(args[1]))
        if method_name == "reflectAttributeValues" and len(args) >= 10:
            args = (
                args[0],
                args[1],
                args[2],
                args[7],
                args[3],
                args[6],
                args[6],
                args[7],
                args[8],
                args[9],
            )
        if method_name == "receiveInteraction" and len(args) >= 10:
            args = (
                args[0],
                args[1],
                args[2],
                args[7],
                args[3],
                args[6],
                args[4],
                args[5],
                args[8],
                args[9],
            )
        normalized_args = tuple(_normalize_2025_callback_value(arg) for arg in args)
        normalized_kwargs = {
            key: _normalize_2025_callback_value(value)
            for key, value in kwargs.items()
        }
        return super().record_callback(method_name, *normalized_args, **normalized_kwargs)


def test_2025_target_radar_adapter_explicitly_covers_time_window_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "scenario_target_radar_time.py"
    )
    required_methods = _scan_target_radar_rti_methods(scenario_path)
    adapter_methods = _adapter_service_methods(_TargetRadar2025RTIAdapter)
    missing = sorted(required_methods - adapter_methods)

    assert missing == [], (
        "Target/Radar 2025 compat adapter is missing explicit wrappers for "
        f"time-window scenario services: {missing}"
    )


def test_2025_target_radar_adapter_explicitly_covers_support_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "scenario_support_services.py"
    )
    required_methods = _scan_target_radar_rti_methods(scenario_path)
    adapter_methods = _adapter_service_methods(_TargetRadar2025RTIAdapter)
    missing = sorted(required_methods - adapter_methods)

    assert missing == [], (
        "Target/Radar 2025 compat adapter is missing explicit wrappers for "
        f"support-services scenario services: {missing}"
    )


def test_2025_target_radar_adapter_explicitly_covers_save_restore_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "scenario_save_restore.py"
    )
    required_methods = _scan_target_radar_rti_methods(scenario_path)
    adapter_methods = _adapter_service_methods(_TargetRadar2025RTIAdapter)
    missing = sorted(required_methods - adapter_methods)

    assert missing == [], (
        "Target/Radar 2025 compat adapter is missing explicit wrappers for "
        f"save-restore scenario services: {missing}"
    )


def test_2025_target_radar_adapter_explicitly_covers_ownership_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "scenario_ownership.py"
    )
    required_methods = _scan_target_radar_rti_methods(scenario_path)
    adapter_methods = _adapter_service_methods(_TargetRadar2025RTIAdapter)
    missing = sorted(required_methods - adapter_methods)

    assert missing == [], (
        "Target/Radar 2025 compat adapter is missing explicit wrappers for "
        f"ownership scenario services: {missing}"
    )


def test_2025_target_radar_adapter_explicitly_covers_transportation_type_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "scenario_transportation_type.py"
    )
    required_methods = _scan_target_radar_rti_methods(scenario_path)
    adapter_methods = _adapter_service_methods(_TargetRadar2025RTIAdapter)
    missing = sorted(required_methods - adapter_methods)

    assert missing == [], (
        "Target/Radar 2025 compat adapter is missing explicit wrappers for "
        f"transportation-type scenario services: {missing}"
    )


def test_2025_target_radar_adapter_explicitly_covers_declaration_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-verification"
        / "src"
        / "hla"
        / "verification"
        / "scenario_declaration.py"
    )
    required_methods = _scan_target_radar_rti_methods(scenario_path)
    adapter_methods = _adapter_service_methods(_TargetRadar2025RTIAdapter)
    missing = sorted(required_methods - adapter_methods)

    assert missing == [], (
        "Target/Radar 2025 compat adapter is missing explicit wrappers for "
        f"declaration scenario services: {missing}"
    )


class _OwnershipCompatRecordingFederateAmbassador(CommonRecordingFederateAmbassador):
    """Narrow ownership callback bridge for shared scenario oracles."""

    def record_callback(self, method_name: str, *args, **kwargs):  # noqa: ANN001, ANN201
        if method_name == "informAttributeOwnership" and len(args) == 3:
            attributes = args[1]
            owner = args[2]
            if isinstance(attributes, set) and len(attributes) == 1:
                args = (args[0], next(iter(attributes)), owner)
            owner_type = type(owner)
            if getattr(owner_type, "__module__", "") == "hla.rti1516_2025.handles" and getattr(owner_type, "__name__", "") == "FederateHandle":
                from hla.rti1516e.handles import FederateHandle

                args = (args[0], args[1], FederateHandle(int(owner.value)))
        if method_name == "attributeIsNotOwned" and len(args) == 2 and isinstance(args[1], set) and len(args[1]) == 1:
            args = (args[0], next(iter(args[1])))
        normalized_args = tuple(_normalize_2025_callback_value(arg) for arg in args)
        normalized_kwargs = {
            key: _normalize_2025_callback_value(value)
            for key, value in kwargs.items()
        }
        return super().record_callback(method_name, *normalized_args, **normalized_kwargs)


def _write_proto2025_resign_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<objectModel>
  <modelIdentification>
    <name>Proto2025 Resign Precondition FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <purpose>Direct 2025 ownership-enabled resign precondition verification.</purpose>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>ResignObject</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Conditional</updateType>
          <ownership>DivestAcquire</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
    <lookahead><dataType>HLAinteger64BE</dataType></lookahead>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )


def _write_proto2025_smoke_object_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<objectModel>
  <modelIdentification>
    <name>Proto2025 Smoke Object FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <purpose>Direct 2025 smoke object routing verification.</purpose>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>SmokeObject</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Conditional</updateType>
          <ownership>DivestAcquire</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
    <lookahead><dataType>HLAinteger64BE</dataType></lookahead>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )


def _write_proto2025_declaration_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<objectModel>
  <modelIdentification>
    <name>Proto2025 Declaration FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <purpose>Direct 2025 declaration management verification.</purpose>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>DemoObject</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Conditional</updateType>
          <ownership>NoTransfer</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>DemoInteraction</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>Message</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
    <lookahead><dataType>HLAinteger64BE</dataType></lookahead>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )


def _write_proto2025_hierarchy_fom(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<objectModel>
  <modelIdentification>
    <name>Proto2025 Hierarchy FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <purpose>Direct 2025 discovery class verification.</purpose>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Base</name>
        <attribute><name>Payload</name><dataType>HLAunicodeString</dataType></attribute>
        <objectClass>
          <name>Child</name>
          <attribute><name>Extra</name><dataType>HLAunicodeString</dataType></attribute>
        </objectClass>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>HLAinteger64BE</dataType></timeStamp>
    <lookahead><dataType>HLAinteger64BE</dataType></lookahead>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )


def _enable_strict_object_publication_probe(rti) -> None:  # noqa: ANN001
    rti._delegate.backend.config.strict_object_publication = True


def _enable_strict_interaction_publication_probe(rti) -> None:  # noqa: ANN001
    rti._delegate.backend.config.strict_interaction_publication = True


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004")
def test_2025_spec_package_exposes_authoritative_surface_without_replacing_2010() -> None:
    import hla.rti1516_2025 as rti2025
    import hla.rti1516e as rti1516e
    from hla.rti1516_2025.plugin import plugin as rti2025_plugin

    assert rti2025.RTIambassador is not rti1516e.RTIambassador
    assert rti2025.FederateAmbassador is not rti1516e.FederateAmbassador
    assert hasattr(rti2025, "RtiConfiguration")
    assert hasattr(rti2025, "Credentials")
    assert hasattr(rti2025, "AuthorizationResultCode")
    assert hasattr(rti2025, "InconsistentFOM")
    assert not hasattr(rti1516e, "RtiConfiguration")
    assert "grpc" in rti2025_plugin().spec.capabilities


@pytest.mark.requirements("HLA2025-REQ-001")
def test_2025_spec_aliases_and_backend_discovery_are_spec_aware() -> None:
    from hla.rti import discover_rti_backends, resolve_spec

    spec = resolve_spec("hla4")
    assert spec.name == "rti1516_2025"
    assert spec.year == 2025
    assert spec.python_package == "hla.rti1516_2025"

    backends = {row.name: row for row in discover_rti_backends(spec="1516-2025")}
    assert set(backends) == {
        "cpp-shim-grpc",
        "cpp-shim-pybind",
        "cpp-2025-sdk-grpc",
        "cpp-2025-sdk-pybind",
        "cpp-standard-2025-grpc",
        "cpp-standard-2025-pybind",
        "java-2025-jpype",
        "java-2025-py4j",
        "java-shim-jpype",
        "java-shim-py4j",
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "shim",
    }
    assert backends["shim"].supports == ("rti1516_2025",)
    assert backends["java-shim-jpype"].supports == ("rti1516e", "rti1516_2025")
    assert backends["java-shim-py4j"].supports == ("rti1516e", "rti1516_2025")
    assert backends["cpp-shim-pybind"].supports == ("rti1516e", "rti1516_2025")
    assert backends["cpp-shim-grpc"].supports == ("rti1516e", "rti1516_2025")
    assert backends["java-standard-2025-jpype"].supports == ("rti1516_2025",)
    assert backends["java-standard-2025-py4j"].supports == ("rti1516_2025",)
    assert backends["cpp-standard-2025-pybind"].supports == ("rti1516_2025",)
    assert backends["cpp-standard-2025-grpc"].supports == ("rti1516_2025",)
    assert backends["cpp-2025-sdk-pybind"].supports == ("rti1516_2025",)
    assert backends["cpp-2025-sdk-grpc"].supports == ("rti1516_2025",)
    assert backends["java-2025-jpype"].supports == ("rti1516_2025",)
    assert backends["java-2025-py4j"].supports == ("rti1516_2025",)


@pytest.mark.requirements("HLA2025-MOD-004", "HLA2025-RET-002", "HLA2025-FI-001")
def test_2025_callback_surface_uses_direct_context_parameters_not_supplemental_helpers() -> None:
    import hla.rti1516_2025 as rti2025
    from hla.rti1516_2025.federate_ambassador import FederateAmbassador

    callback_parameters = {
        "discoverObjectInstance": ("objectInstance", "objectClass", "objectInstanceName", "producingFederate"),
        "reflectAttributeValues": (
            "objectInstance",
            "attributeValues",
            "userSuppliedTag",
            "transportationType",
            "producingFederate",
            "optionalSentRegions",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
        "receiveInteraction": (
            "interactionClass",
            "parameterValues",
            "userSuppliedTag",
            "transportationType",
            "producingFederate",
            "optionalSentRegions",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
        "receiveDirectedInteraction": (
            "interactionClass",
            "objectInstance",
            "parameterValues",
            "userSuppliedTag",
            "transportationType",
            "producingFederate",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
        "removeObjectInstance": (
            "objectInstance",
            "userSuppliedTag",
            "producingFederate",
            "time",
            "sentOrderType",
            "receivedOrderType",
            "optionalRetraction",
        ),
    }

    for method_name, expected in callback_parameters.items():
        signature = inspect.signature(getattr(FederateAmbassador, method_name))
        assert tuple(name for name in signature.parameters if name != "self") == expected
        assert not any("Supplemental" in name for name in signature.parameters)

    assert not hasattr(rti2025, "SupplementalReflectInfo")
    assert not hasattr(rti2025, "SupplementalReceiveInfo")
    assert not hasattr(rti2025, "SupplementalRemoveInfo")


@pytest.mark.requirements(
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-MOD-004",
    "HLA2025-MOD-006",
    "HLA2025-FI-SVC-035",
    "HLA2025-FI-SVC-036",
    "HLA2025-FI-SVC-041",
    "HLA2025-FI-SVC-042",
    "HLA2025-FI-SVC-047",
    "HLA2025-FI-SVC-049",
    "HLA2025-FI-SVC-057",
    "HLA2025-FI-SVC-058",
    "HLA2025-FI-SVC-059",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-061",
    "HLA2025-FI-SVC-062",
    "HLA2025-FI-SVC-123",
    "HLA2025-FI-SVC-124",
    "HLA2025-FI-SVC-125",
)
def test_2025_shim_runs_two_federate_object_and_interaction_exchange(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished, ObjectClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "Exchange2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Exchange 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused exchange fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-exchange-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    subscriber.subscribeObjectClassAttributes(object_class, {attribute})
    subscriber.subscribeInteractionClass(interaction_class)
    object_instance = publisher.registerObjectInstance(object_class, "Target-Exchange-1")
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "Target-Exchange-1",
        publisher_handle,
    )

    with pytest.raises(ObjectClassNotPublished):
        publisher.updateAttributeValues(object_instance, {attribute: b"blocked"}, b"not-published")
    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.TIMESTAMP)
    publisher.updateAttributeValues(object_instance, {attribute: b"123,456"}, b"update-tag")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"123,456"},
        b"update-tag",
        reliable,
        publisher_handle,
        set(),
    )
    assert reflection[6:] == (None, OrderType.TIMESTAMP, OrderType.TIMESTAMP, None)

    publisher.changeAttributeOrderType(object_instance, {attribute}, OrderType.RECEIVE)
    subscriber_callbacks.callbacks.clear()
    publisher.updateAttributeValues(object_instance, {attribute: b"receive-ordered"}, b"receive-order-tag")
    receive_order_reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert receive_order_reflection is not None
    assert receive_order_reflection[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    with pytest.raises(InteractionClassNotPublished):
        publisher.sendInteraction(interaction_class, {parameter: b"T-1"}, b"not-published")
    publisher.publishInteractionClass(interaction_class)
    publisher.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)
    publisher.sendInteraction(interaction_class, {parameter: b"T-1"}, b"interaction-tag")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[:6] == (
        interaction_class,
        {parameter: b"T-1"},
        b"interaction-tag",
        reliable,
        publisher_handle,
        set(),
    )
    assert received[6:] == (None, OrderType.TIMESTAMP, OrderType.TIMESTAMP, None)

    subscriber.unsubscribeObjectClassAttributes(object_class, {attribute})
    subscriber_callbacks.callbacks.clear()
    publisher.updateAttributeValues(object_instance, {attribute: b"after-unsubscribe"}, b"update-after")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None

    subscriber.unsubscribeInteractionClass(interaction_class)
    publisher.sendInteraction(interaction_class, {parameter: b"T-2"}, b"interaction-after")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_example_target_radar_scenario_end_to_end() -> None:
    from hla.foms.target_radar._internal import Vec3, run_target_radar_scenario, target_radar_fom_path
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-2025-target-radar-{uuid.uuid4().hex[:8]}"
    pair_by_role: dict[str, _TargetRadar2025RTIAdapter] = {}

    def factory(role: str) -> _TargetRadar2025RTIAdapter:
        if role not in pair_by_role:
            pair_by_role[role] = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
        return pair_by_role[role]

    result = run_target_radar_scenario(
        factory,
        federation_name=federation_name,
        steps=3,
        fom_modules=[target_radar_fom_path()],
    )

    assert result.backend_kinds == ("shim/2025", "shim/2025")
    assert result.target_name == "Target-1"
    assert result.final_target_position == Vec3(10_750.0, 1_090.0, 2_000.0)
    assert [report.track_id for report in result.track_reports] == ["TRK-001", "TRK-002", "TRK-003"]
    assert all(report.target_name == "Target-1" for report in result.track_reports)
    assert [event_name for event_name, _payload in result.target_events].count("provide_attribute_value_update") == 3
    assert [event_name for event_name, _payload in result.radar_events].count("query_rcs") == 3
    assert [event_name for event_name, _payload in result.radar_events].count("track") == 3
    assert result.track_reports[-1].position == result.final_target_position


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002")
def test_2025_shim_runs_federation_lifecycle_scenario_end_to_end() -> None:
    from hla.verification import FederationLifecycleScenarioConfig, run_federation_lifecycle_scenario
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-2025-lifecycle-{uuid.uuid4().hex[:8]}"
    rti = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = FederationLifecycleScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_federation_lifecycle_scenario(
        rti,
        config=config,
        federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["federate_handle"] is not None
    assert summary["resign_action"] == config.resign_action
    assert summary["use_mim_create"] is False


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-003")
def test_2025_shim_runs_federation_lifecycle_negative_scenario_end_to_end() -> None:
    from hla.verification import FederationLifecycleScenarioConfig, run_federation_lifecycle_negative_scenario
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-2025-lifecycle-negative-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = FederationLifecycleScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_federation_lifecycle_negative_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert type(summary["already_connected"]).__name__ == "AlreadyConnected"
    assert type(summary["duplicate_create"]).__name__ == "FederationExecutionAlreadyExists"
    assert type(summary["disconnect_while_joined"]).__name__ == "FederateIsExecutionMember"
    assert type(summary["destroy_with_joined"]).__name__ == "FederatesCurrentlyJoined"
    assert type(summary["destroy_missing"]).__name__ == "FederationExecutionDoesNotExist"


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-002")
def test_2025_shim_runs_federation_listing_scenario_end_to_end() -> None:
    from hla.verification import FederationLifecycleScenarioConfig, run_federation_listing_scenario
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-2025-listing-{uuid.uuid4().hex[:8]}"
    rti = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = FederationLifecycleScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_federation_listing_scenario(
        rti,
        config=config,
        federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert config.federation_name in summary["reported_names"]
    assert config.federation_name not in summary["post_destroy_reported_names"]


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-008")
def test_2025_shim_runs_multi_participation_scenario_end_to_end() -> None:
    from hla.verification import FederationLifecycleScenarioConfig, run_multi_participation_scenario
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-2025-multi-participation-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    shadow = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = FederationLifecycleScenarioConfig(
        federation_name=federation_name,
        secondary_federation_name=f"{federation_name}-secondary",
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        federate_name="Leader",
        second_federate_name="Wing",
        secondary_federate_name="Shadow",
        federate_type="LifecycleType",
    )

    summary = run_multi_participation_scenario(
        leader,
        wing,
        shadow,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
        shadow_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["primary_federation_name"] == config.federation_name
    assert summary["secondary_federation_name"] == config.secondary_federation_name
    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert summary["shadow_handle"] is not None


@pytest.mark.requirements(
    "HLA2025-FR-001",
    "HLA2025-FI-001",
    "HLA2025-FI-002",
    "HLA2025-FI-SVC-004",
    "HLA2025-FI-SVC-005",
    "HLA2025-FI-SVC-006",
    "HLA2025-FI-SVC-007",
)
def test_2025_shim_runs_join_precondition_scenario_end_to_end() -> None:
    from hla.verification import JoinScenarioConfig, run_join_precondition_scenario
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-2025-join-preconditions-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    late = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = JoinScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        late_name="Late",
        federate_type="JoinFederate",
        save_name="JOIN-BLOCK",
    )

    summary = run_join_precondition_scenario(
        leader,
        wing,
        late,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
        late_federate=_CompatRecordingFederateAmbassador(),
    )

    assert type(summary["not_connected"]).__name__ == "NotConnected"
    assert type(summary["missing_federation"]).__name__ == "FederationExecutionDoesNotExist"
    assert type(summary["duplicate_name"]).__name__ == "FederateNameAlreadyInUse"
    assert type(summary["already_joined"]).__name__ == "FederateAlreadyExecutionMember"
    assert type(summary["save_in_progress"]).__name__ == "SaveInProgress"
    assert type(summary["restore_in_progress"]).__name__ == "RestoreInProgress"


@pytest.mark.requirements(
    "HLA2025-FR-001",
    "HLA2025-FI-001",
    "HLA2025-FI-002",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-016",
)
def test_2025_shim_runs_resign_precondition_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import ResignScenarioConfig, run_resign_precondition_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025ResignFOM.xml"
    _write_proto2025_resign_fom(fom_path)

    federation_name = f"shim-2025-resign-preconditions-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = ResignScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="ResignFederate",
        object_class_name="HLAobjectRoot.ResignObject",
        attribute_name="Payload",
        object_instance_name="Pending-Acquisition",
    )

    summary = run_resign_precondition_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_OwnershipCompatRecordingFederateAmbassador(),
        wing_federate=_OwnershipCompatRecordingFederateAmbassador(),
    )

    assert type(summary["not_connected"]).__name__ == "NotConnected"
    assert type(summary["not_joined"]).__name__ == "FederateNotExecutionMember"
    assert type(summary["invalid_action"]).__name__ == "InvalidResignAction"
    assert type(summary["owns_attributes"]).__name__ == "FederateOwnsAttributes"
    assert type(summary["acquisition_pending"]).__name__ == "OwnershipAcquisitionPending"
    assert summary["object_instance"] is not None
    assert summary["attribute"] is not None


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-017")
def test_2025_shim_runs_request_attribute_value_update_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import RequestAttributeValueUpdateScenarioConfig, run_request_attribute_value_update_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025SmokeObjectFOM.xml"
    _write_proto2025_smoke_object_fom(fom_path)

    federation_name = f"shim-2025-request-avu-{uuid.uuid4().hex[:8]}"
    owner = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    requester = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = RequestAttributeValueUpdateScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        requester_name="Requester",
        federate_type="RequestAttributeValueUpdateFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name="Request-Update-Object-1",
        request_tag=b"request-update",
    )

    summary = run_request_attribute_value_update_scenario(
        owner,
        requester,
        config=config,
        owner_federate=_CompatRecordingFederateAmbassador(),
        requester_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["owner_handle"] is not None
    assert summary["requester_handle"] is not None
    assert summary["object_instance"] is not None
    assert summary["provide_record"].args[0] == summary["object_instance"]
    assert summary["provide_record"].args[1] == {summary["owner_attribute"]}
    assert summary["provide_record"].args[2] == config.request_tag


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-018")
def test_2025_shim_runs_request_attribute_value_update_routing_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import RequestAttributeValueUpdateScenarioConfig, run_request_attribute_value_update_routing_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025SmokeObjectFOM.xml"
    _write_proto2025_smoke_object_fom(fom_path)

    federation_name = f"shim-2025-request-avu-routing-{uuid.uuid4().hex[:8]}"
    owner_a = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    owner_b = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    requester = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = RequestAttributeValueUpdateScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="OwnerA",
        requester_name="Requester",
        federate_type="RequestAttributeValueUpdateFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name="Request-Update-Object-1",
        request_tag=b"request-update",
    )

    summary = run_request_attribute_value_update_routing_scenario(
        owner_a,
        owner_b,
        requester,
        config=config,
        owner_a_federate=_CompatRecordingFederateAmbassador(),
        owner_b_federate=_CompatRecordingFederateAmbassador(),
        requester_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["owner_a_handle"] is not None
    assert summary["owner_b_handle"] is not None
    assert summary["requester_handle"] is not None
    assert summary["object_target_provide_a"].args[0] == summary["object_a"]
    assert summary["object_target_provide_a"].args[2] == config.request_tag
    assert summary["object_target_provide_b"] is None
    assert summary["class_target_provide_a"].args[0] == summary["object_a"]
    assert summary["class_target_provide_a"].args[2] == b"class-wide"
    assert summary["class_target_provide_b"].args[0] == summary["object_b"]
    assert summary["class_target_provide_b"].args[2] == b"class-wide"


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-019", "HLA2025-FI-SVC-020")
def test_2025_shim_runs_declaration_management_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import DeclarationManagementScenarioConfig, run_declaration_management_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025DeclarationFOM.xml"
    _write_proto2025_declaration_fom(fom_path)

    federation_name = f"shim-2025-declaration-{uuid.uuid4().hex[:8]}"
    publisher = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    subscriber = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = DeclarationManagementScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        publisher_name="Publisher",
        subscriber_name="Subscriber",
        federate_type="SmokeFederate",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name="DeclarationObject-1",
        attribute_payload=b"declaration-payload",
        attribute_tag=b"declaration-tag",
        interaction_payload=b"declaration-interaction",
        interaction_tag=b"declaration-interaction-tag",
        before_object_unpublish_rejection_probe=_enable_strict_object_publication_probe,
        before_interaction_unpublish_rejection_probe=_enable_strict_interaction_publication_probe,
    )

    summary = run_declaration_management_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=_CompatRecordingFederateAmbassador(),
        subscriber_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["publisher_handle"] is not None
    assert summary["subscriber_handle"] is not None
    assert summary["first_start_record"].args == (summary["publisher_class"],)
    assert summary["first_turn_on_record"].args == (summary["publisher_interaction"],)
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["reflect_record"].args[2] == config.attribute_tag
    assert summary["interaction_record"].args[0] == summary["subscriber_interaction"]
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert summary["interaction_record"].args[2] == config.interaction_tag
    assert summary["first_stop_record"].args == (summary["publisher_class"],)
    assert summary["first_turn_off_record"].args == (summary["publisher_interaction"],)
    assert summary["second_start_record"].args == (summary["publisher_class"],)
    assert summary["second_turn_on_record"].args == (summary["publisher_interaction"],)
    assert summary["second_turn_off_record"].args == (summary["publisher_interaction"],)


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-021")
def test_2025_shim_runs_declaration_invalid_attribute_publication_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import (
        DeclarationManagementScenarioConfig,
        run_declaration_invalid_attribute_publication_scenario,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025DeclarationFOM.xml"
    _write_proto2025_declaration_fom(fom_path)

    federation_name = f"shim-2025-declaration-invalid-{uuid.uuid4().hex[:8]}"
    publisher = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = DeclarationManagementScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        publisher_name="Publisher",
        federate_type="SmokeFederate",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
    )

    summary = run_declaration_invalid_attribute_publication_scenario(
        publisher,
        config=config,
        publisher_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["publisher_handle"] is not None
    assert summary["publisher_class"] is not None
    assert summary["publisher_attribute"] is not None
    assert summary["invalid_attribute"] is not None
    assert type(summary["exception"]).__name__ == "AttributeNotDefined"


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-022", "HLA2025-FI-SVC-023")
def test_2025_shim_runs_declaration_unpublish_rejection_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import (
        DeclarationManagementScenarioConfig,
        run_declaration_unpublish_rejection_scenario,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025DeclarationFOM.xml"
    _write_proto2025_declaration_fom(fom_path)

    federation_name = f"shim-2025-declaration-unpublish-{uuid.uuid4().hex[:8]}"
    publisher = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = DeclarationManagementScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        publisher_name="Publisher",
        federate_type="SmokeFederate",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name="DeclarationObject-1",
        attribute_payload=b"declaration-payload",
        attribute_tag=b"declaration-tag",
        interaction_payload=b"declaration-interaction",
        interaction_tag=b"declaration-interaction-tag",
    )

    summary = run_declaration_unpublish_rejection_scenario(
        publisher,
        config=config,
        publisher_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["publisher_handle"] is not None
    assert summary["object_instance"] is not None
    assert type(summary["object_unpublish_error"]).__name__ in {"AttributeNotPublished", "ObjectClassNotPublished"}
    assert type(summary["interaction_unpublish_error"]).__name__ == "InteractionClassNotPublished"


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-024", "HLA2025-MIL-004")
def test_2025_shim_runs_time_managed_declaration_independence_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import (
        DeclarationManagementScenarioConfig,
        run_time_managed_declaration_independence_scenario,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025DeclarationFOM.xml"
    _write_proto2025_declaration_fom(fom_path)

    federation_name = f"shim-2025-declaration-time-{uuid.uuid4().hex[:8]}"
    publisher = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    subscriber = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = DeclarationManagementScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        publisher_name="Publisher",
        subscriber_name="Subscriber",
        federate_type="SmokeFederate",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name="DeclarationObject-1",
        attribute_payload=b"declaration-payload",
        attribute_tag=b"declaration-tag",
        interaction_payload=b"declaration-interaction",
        interaction_tag=b"declaration-interaction-tag",
    )

    summary = run_time_managed_declaration_independence_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=_CompatRecordingFederateAmbassador(),
        subscriber_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["publisher_handle"] is not None
    assert summary["subscriber_handle"] is not None
    assert summary["time_regulation"].args[0].value == 0
    assert summary["time_constrained"].args[0].value == 0
    assert summary["start_record"].args == (summary["publisher_class"],)
    assert summary["turn_on_record"].args == (summary["publisher_interaction"],)


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-019", "HLA2025-FI-SVC-020")
def test_2025_shim_runs_passive_full_declaration_scenario_via_compat_adapter(tmp_path: Path) -> None:
    from hla.verification import DeclarationManagementScenarioConfig, run_declaration_management_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025DeclarationPassiveFullFOM.xml"
    _write_proto2025_declaration_fom(fom_path)

    federation_name = f"shim-2025-declaration-passive-full-{uuid.uuid4().hex[:8]}"
    publisher = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    subscriber = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = DeclarationManagementScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        publisher_name="Publisher",
        subscriber_name="Subscriber",
        federate_type="SmokeFederate",
        object_class_name="HLAobjectRoot.DemoObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.DemoInteraction",
        parameter_name="Message",
        object_instance_name="DeclarationPassiveFullObject-1",
        attribute_payload=b"declaration-passive-full-payload",
        attribute_tag=b"declaration-passive-full-tag",
        interaction_payload=b"declaration-passive-full-interaction",
        interaction_tag=b"declaration-passive-full-interaction-tag",
        use_passive_object_subscription=True,
        use_passive_interaction_subscription=True,
        use_full_object_unpublish=True,
        use_full_object_unsubscribe=True,
        before_object_unpublish_rejection_probe=_enable_strict_object_publication_probe,
        before_interaction_unpublish_rejection_probe=_enable_strict_interaction_publication_probe,
    )

    summary = run_declaration_management_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=_CompatRecordingFederateAmbassador(),
        subscriber_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["publisher_handle"] is not None
    assert summary["subscriber_handle"] is not None
    assert summary["first_start_record"].args == (summary["publisher_class"],)
    assert summary["first_turn_on_record"].args == (summary["publisher_interaction"],)
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert summary["first_stop_record"].args == (summary["publisher_class"],)
    assert summary["first_turn_off_record"].args == (summary["publisher_interaction"],)
    assert summary["second_start_record"].args == (summary["publisher_class"],)
    assert summary["second_turn_on_record"].args == (summary["publisher_interaction"],)
    assert summary["second_stop_record"].args == (summary["publisher_class"],)
    assert summary["second_turn_off_record"].args == (summary["publisher_interaction"],)
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["reflect_record"].args[2] == config.attribute_tag
    assert summary["interaction_record"].args[0] == summary["subscriber_interaction"]
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert summary["interaction_record"].args[2] == config.interaction_tag


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-025")
def test_2025_shim_runs_discovery_class_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import DiscoveryClassScenarioConfig, run_discovery_class_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025HierarchyFOM.xml"
    _write_proto2025_hierarchy_fom(fom_path)

    federation_name = f"shim-2025-discovery-class-{uuid.uuid4().hex[:8]}"
    publisher = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    subscriber = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = DiscoveryClassScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        publisher_name="Publisher",
        subscriber_name="Subscriber",
        federate_type="DiscoveryClassFederate",
        subscriber_class_name="HLAobjectRoot.Base",
        publisher_class_name="HLAobjectRoot.Base.Child",
        attribute_name="Payload",
        object_instance_name="Hierarchy-1",
        attribute_payload=b"payload",
        attribute_tag=b"tag",
    )

    summary = run_discovery_class_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=_CompatRecordingFederateAmbassador(),
        subscriber_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["publisher_handle"] is not None
    assert summary["subscriber_handle"] is not None
    assert summary["discovery"].args[0] == summary["object_instance"]
    assert summary["discovery"].args[1] == summary["subscriber_class"]
    assert summary["discovery"].args[2] == config.object_instance_name
    assert summary["reflection"].args[0] == summary["object_instance"]
    assert summary["reflection"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["reflection"].args[2] == config.attribute_tag


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-SVC-026")
def test_2025_shim_runs_local_delete_scenario_end_to_end(tmp_path: Path) -> None:
    from hla.verification import LocalDeleteScenarioConfig, run_local_delete_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom_path = tmp_path / "Proto2025SmokeObjectFOM.xml"
    _write_proto2025_smoke_object_fom(fom_path)

    federation_name = f"shim-2025-local-delete-{uuid.uuid4().hex[:8]}"
    owner = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    observer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = LocalDeleteScenarioConfig(
        federation_name=federation_name,
        fom_modules=(str(fom_path),),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        observer_name="Observer",
        federate_type="LocalDeleteFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name="Local-Delete-Object-1",
        rediscover_payload=b"rediscover",
        rediscover_tag=b"local-delete-rediscover",
    )

    summary = run_local_delete_scenario(
        owner,
        observer,
        config=config,
        owner_federate=_CompatRecordingFederateAmbassador(),
        observer_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["owner_handle"] is not None
    assert summary["observer_handle"] is not None
    assert summary["discovery"].args[0] == summary["object_instance"]
    assert summary["discovery"].args[2] == config.object_instance_name
    assert summary["reflection"].args[0] == summary["object_instance"]
    assert summary["reflection"].args[1] == {summary["observer_attribute"]: config.rediscover_payload}
    assert summary["reflection"].args[2] == config.rediscover_tag


@pytest.mark.requirements(
    "HLA2025-SS-001",
    "HLA2025-SS-002",
    "HLA2025-SS-003",
    "HLA2025-SS-006",
    "HLA2025-FI-001",
)
def test_2025_shim_runs_support_lookup_and_normalization_route_end_to_end() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths

    federation_name = f"shim-2025-support-route-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    callbacks = Recording2025FederateAmbassador()

    rti.connect(callbacks, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModules=scenario_fom_paths("message-test"),
        logicalTimeImplementationName="HLAinteger64Time",
    )
    federate_handle = rti.joinFederationExecution(
        federateName="Support",
        federateType="SupportFederate",
        federationName=federation_name,
    )

    object_class = rti.getObjectClassHandle("HLAobjectRoot.Proto2025.MessageTest.TestSuite")
    attribute = rti.getAttributeHandle(object_class, "SuiteId")
    interaction_class = rti.getInteractionClassHandle("HLAinteractionRoot.Proto2025.MessageTest.SendStimulus")
    parameter = rti.getParameterHandle(interaction_class, "TestCaseId")
    rti.publishObjectClassAttributes(object_class, {attribute})
    rti.reserveObjectInstanceName("support-suite")
    assert callbacks.last_callback("objectInstanceNameReservationSucceeded") == ("support-suite",)
    object_instance = rti.registerObjectInstance(object_class, "support-suite")

    assert rti.getFederateName(federate_handle) == "Support"
    assert rti.normalizeFederateHandle(federate_handle) == federate_handle.value
    assert rti.getObjectClassName(object_class) == "HLAobjectRoot.Proto2025.MessageTest.TestSuite"
    assert rti.getAttributeName(object_class, attribute) == "SuiteId"
    assert rti.getInteractionClassName(interaction_class) == "HLAinteractionRoot.Proto2025.MessageTest.SendStimulus"
    assert rti.getParameterName(interaction_class, parameter) == "TestCaseId"
    assert rti.getObjectInstanceName(object_instance) == "support-suite"
    assert rti.getObjectInstanceHandle("support-suite") == object_instance
    assert rti.getKnownObjectClassHandle(object_instance) == object_class
    assert rti.getOrderName(OrderType.RECEIVE) == "HLAreceive"
    assert rti.getOrderType("HLAtimestamp") is OrderType.TIMESTAMP
    assert rti.getTransportationTypeName(rti.getTransportationTypeHandle("HLAreliable")) == "HLAreliable"
    assert rti.getTransportationTypeName(rti.getTransportationTypeHandle("HLAbestEffort")) == "HLAbestEffort"
    assert rti.getHLAversion() == "IEEE 1516.1-2025"

    rti.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-SS-001",
    "HLA2025-SS-002",
    "HLA2025-SS-003",
    "HLA2025-SS-004",
    "HLA2025-SS-005",
    "HLA2025-SS-006",
    "HLA2025-FI-001",
)
def test_2025_shim_runs_support_factory_and_decode_scenario_via_compat_adapter() -> None:
    from hla.verification import SupportServicesScenarioConfig, run_support_factory_and_decode_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516e.enums import OrderType, TransportationType
    from hla.rti1516e.handles import (
        AttributeHandleFactory,
        AttributeHandleSetFactory,
        AttributeHandleValueMapFactory,
        AttributeSetRegionSetPairListFactory,
        DimensionHandleFactory,
        DimensionHandleSetFactory,
        FederateHandleFactory,
        FederateHandleSetFactory,
        InteractionClassHandleFactory,
        ObjectClassHandleFactory,
        ObjectInstanceHandleFactory,
        ParameterHandleFactory,
        ParameterHandleValueMapFactory,
        RegionHandleSetFactory,
        TransportationTypeHandleFactory,
    )

    federation_name = f"shim-2025-support-adapter-{uuid.uuid4().hex[:8]}"
    rti = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SupportServicesScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.Proto2025.MessageTest.TestSuite",
        attribute_name="SuiteId",
        interaction_class_name="HLAinteractionRoot.Proto2025.MessageTest.SendStimulus",
        parameter_name="TestCaseId",
        object_instance_name="support-adapter-suite",
    )

    summary = run_support_factory_and_decode_scenario(
        rti,
        config=config,
        federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["lookup_summary"] == {
        "federate_name": config.federate_name,
        "normalized_federate_handle": summary["federate_handle"].value,
        "object_class_name": config.object_class_name,
        "attribute_name": config.attribute_name,
        "interaction_class_name": config.interaction_class_name,
        "parameter_name": config.parameter_name,
        "object_instance_name": config.object_instance_name,
        "object_instance_handle": summary["object_instance"],
        "known_object_class": summary["object_class"],
        "receive_order_name": "HLAreceive",
        "timestamp_order_type": OrderType.TIMESTAMP,
        "reliable_transport_name": "HLAreliable",
        "best_effort_transport_name": "HLAbestEffort",
        "reliable_transport_enum_name": "HLAreliable",
        "best_effort_transport_enum_name": "HLAbestEffort",
    }

    assert isinstance(summary["factory_summary"]["attribute_factory"], AttributeHandleFactory)
    assert isinstance(summary["factory_summary"]["attribute_set_factory"], AttributeHandleSetFactory)
    assert isinstance(summary["factory_summary"]["attribute_value_map_factory"], AttributeHandleValueMapFactory)
    assert isinstance(
        summary["factory_summary"]["attribute_region_pair_list_factory"],
        AttributeSetRegionSetPairListFactory,
    )
    assert isinstance(summary["factory_summary"]["dimension_factory"], DimensionHandleFactory)
    assert isinstance(summary["factory_summary"]["dimension_set_factory"], DimensionHandleSetFactory)
    assert isinstance(summary["factory_summary"]["federate_factory"], FederateHandleFactory)
    assert isinstance(summary["factory_summary"]["federate_set_factory"], FederateHandleSetFactory)
    assert isinstance(summary["factory_summary"]["interaction_factory"], InteractionClassHandleFactory)
    assert isinstance(summary["factory_summary"]["object_class_factory"], ObjectClassHandleFactory)
    assert isinstance(summary["factory_summary"]["object_instance_factory"], ObjectInstanceHandleFactory)
    assert isinstance(summary["factory_summary"]["parameter_factory"], ParameterHandleFactory)
    assert isinstance(summary["factory_summary"]["parameter_value_map_factory"], ParameterHandleValueMapFactory)
    assert isinstance(summary["factory_summary"]["region_set_factory"], RegionHandleSetFactory)
    assert isinstance(summary["factory_summary"]["transportation_factory"], TransportationTypeHandleFactory)

    assert summary["decoded_summary"]["federate_handle"] == summary["federate_handle"]
    assert summary["decoded_summary"]["object_class_handle"] == summary["object_class"]
    assert summary["decoded_summary"]["interaction_class_handle"] == summary["interaction_class"]
    assert summary["decoded_summary"]["object_instance_handle"] == summary["object_instance"]
    assert summary["decoded_summary"]["attribute_handle"] == summary["attribute"]
    assert summary["decoded_summary"]["parameter_handle"] == summary["parameter"]
    assert rti.get_transportation_type("HLAreliable") is TransportationType.RELIABLE
    assert rti.get_transportation_type("HLAbestEffort") is TransportationType.BEST_EFFORT
    assert rti.get_transportation_name(TransportationType.RELIABLE) == "HLAreliable"
    assert rti.get_transportation_name(TransportationType.BEST_EFFORT) == "HLAbestEffort"


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-019",
    "HLA2025-FI-SVC-020",
    "HLA2025-FI-SVC-021",
    "HLA2025-FI-SVC-022",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-024",
    "HLA2025-FI-SVC-025",
    "HLA2025-FI-SVC-026",
    "HLA2025-FI-SVC-027",
    "HLA2025-FI-SVC-028",
    "HLA2025-FI-SVC-029",
    "HLA2025-FI-SVC-030",
    "HLA2025-FI-SVC-031",
    "HLA2025-FI-SVC-032",
)
def test_2025_shim_runs_backend_neutral_save_restore_scenario_via_compat_adapter() -> None:
    from hla.verification import SaveRestoreScenarioConfig, run_save_restore_scenario
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.rti1516e.enums import RestoreStatus, SaveStatus

    federation_name = f"shim-2025-save-restore-adapter-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SaveRestoreScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SaveRestoreFederate",
        save_name="SAVE-COMPAT-ADAPTER",
    )

    summary = run_save_restore_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
    )

    pending_save = {pair.federate_handle: pair.save_status for pair in summary["save_status_pending"].args[0]}
    cleared_save = {pair.federate_handle: pair.save_status for pair in summary["save_status_cleared"].args[0]}
    pending_restore = {pair.pre_restore_handle: pair.restore_status for pair in summary["restore_status_pending"].args[0]}
    cleared_restore = {pair.pre_restore_handle: pair.restore_status for pair in summary["restore_status_cleared"].args[0]}

    assert summary["leader_handle"] in pending_save
    assert summary["wing_handle"] in pending_save
    assert pending_save[summary["leader_handle"]] is not SaveStatus.NO_SAVE_IN_PROGRESS
    assert pending_save[summary["wing_handle"]] is not SaveStatus.NO_SAVE_IN_PROGRESS
    assert cleared_save == {
        summary["leader_handle"]: SaveStatus.NO_SAVE_IN_PROGRESS,
        summary["wing_handle"]: SaveStatus.NO_SAVE_IN_PROGRESS,
    }
    assert summary["leader_restore_succeeded"].args == (config.save_name,)
    assert summary["wing_initiate_restore"].args[0] == config.save_name
    assert summary["leader_handle"] in pending_restore
    assert summary["wing_handle"] in pending_restore
    assert pending_restore[summary["leader_handle"]] is not RestoreStatus.NO_RESTORE_IN_PROGRESS
    assert pending_restore[summary["wing_handle"]] is not RestoreStatus.NO_RESTORE_IN_PROGRESS
    assert cleared_restore == {
        summary["leader_handle"]: RestoreStatus.NO_RESTORE_IN_PROGRESS,
        summary["wing_handle"]: RestoreStatus.NO_RESTORE_IN_PROGRESS,
    }


@pytest.mark.requirements(
    "HLA2025-SS-043",
    "HLA2025-SS-044",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
)
def test_2025_shim_runs_callback_control_route_with_object_reflection_end_to_end() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths

    federation_name = f"shim-2025-callback-object-{uuid.uuid4().hex[:8]}"
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(
        federationName=federation_name,
        fomModules=scenario_fom_paths("message-test"),
        logicalTimeImplementationName="HLAinteger64Time",
    )
    publisher_handle = publisher.joinFederationExecution(
        federateName="Publisher",
        federateType="CallbackFederate",
        federationName=federation_name,
    )
    subscriber.joinFederationExecution(
        federateName="Subscriber",
        federateType="CallbackFederate",
        federationName=federation_name,
    )

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Proto2025.MessageTest.TestSuite")
    attribute = publisher.getAttributeHandle(object_class, "SuiteId")
    subscriber_object_class = subscriber.getObjectClassHandle("HLAobjectRoot.Proto2025.MessageTest.TestSuite")
    subscriber_attribute = subscriber.getAttributeHandle(subscriber_object_class, "SuiteId")
    publisher.publishObjectClassAttributes(object_class, {attribute})
    subscriber.subscribeObjectClassAttributes(subscriber_object_class, {subscriber_attribute})

    publisher.reserveObjectInstanceName("callback-suite")
    assert publisher_callbacks.last_callback("objectInstanceNameReservationSucceeded") == ("callback-suite",)
    object_instance = publisher.registerObjectInstance(object_class, "callback-suite")
    first_discovery = subscriber_callbacks.last_callback("discoverObjectInstance")
    assert first_discovery is not None
    assert first_discovery[0] == object_instance
    assert first_discovery[1] == subscriber_object_class
    assert first_discovery[2] == "callback-suite"
    subscriber_callbacks.callbacks.clear()

    subscriber.disableCallbacks()
    publisher.updateAttributeValues(object_instance, {attribute: b"one"}, b"queued-one")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None

    assert subscriber.evokeCallback(0.0) is False

    subscriber.enableCallbacks()
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is True
    first_reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert first_reflection is not None
    assert first_reflection[0] == object_instance
    assert first_reflection[1] == {subscriber_attribute: b"one"}
    assert first_reflection[2] == b"queued-one"
    assert first_reflection[4] == publisher_handle
    assert subscriber.getFederateName(first_reflection[4]) == "Publisher"

    subscriber_callbacks.callbacks.clear()
    subscriber.disableCallbacks()
    publisher.updateAttributeValues(object_instance, {attribute: b"two"}, b"queued-two")
    publisher.updateAttributeValues(object_instance, {attribute: b"three"}, b"queued-three")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is False

    subscriber.enableCallbacks()
    drained = 0
    while drained < 8 and subscriber.evokeMultipleCallbacks(0.0, 0.0):
        drained += 1
    reflections = _callbacks_named_2025(subscriber_callbacks, "reflectAttributeValues")
    assert [record[2] for record in reflections] == [b"queued-two", b"queued-three"]
    assert [record[1] for record in reflections] == [
        {subscriber_attribute: b"two"},
        {subscriber_attribute: b"three"},
    ]
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is False

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-FI-005", "HLA2025-FI-SVC-121", "HLA2025-FI-SVC-122")
def test_2025_shim_runs_attribute_ownership_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import OwnershipScenarioConfig, run_attribute_ownership_scenario

    federation_name = f"shim-2025-ownership-{uuid.uuid4().hex[:8]}"
    owner = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    acquirer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = OwnershipScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.Proto2025.MessageTest.TestSuite",
        attribute_name="SuiteId",
        object_instance_name=f"ownership-suite-{uuid.uuid4().hex[:8]}",
    )

    summary = run_attribute_ownership_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=_OwnershipCompatRecordingFederateAmbassador(),
        acquirer_federate=_OwnershipCompatRecordingFederateAmbassador(),
    )

    assert summary["not_owned"].args == (summary["object_instance"], summary["owner_attribute"])
    assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
    assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
    assert summary["informed"].args[0] == summary["object_instance"]
    assert summary["informed"].args[1] == summary["owner_attribute"]
    assert summary["informed_federate_name"] == config.acquirer_name


@pytest.mark.requirements(
    "HLA2025-FI-SVC-123",
    "HLA2025-FI-SVC-124",
    "HLA2025-FI-SVC-125",
    "HLA2025-FI-SVC-126",
)
def test_2025_shim_runs_negotiated_ownership_flow_via_compat_adapter() -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import NegotiatedOwnershipScenarioConfig

    federation_name = f"shim-2025-negotiated-adapter-{uuid.uuid4().hex[:8]}"
    owner = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    acquirer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    owner_federate = _OwnershipCompatRecordingFederateAmbassador()
    acquirer_federate = _OwnershipCompatRecordingFederateAmbassador()
    config = NegotiatedOwnershipScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="NegotiatedOwnershipFederate",
        object_class_name="HLAobjectRoot.Proto2025.MessageTest.TestSuite",
        attribute_name="SuiteId",
        object_instance_name=f"negotiated-suite-{uuid.uuid4().hex[:8]}",
        assumption_tag=b"offer-tag",
        request_tag=b"request-tag",
        cancel_tag=b"cancel-tag",
    )

    owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    owner.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    acquirer.join_federation_execution(config.acquirer_name, config.federate_type, config.federation_name)

    object_class = owner.get_object_class_handle(config.object_class_name)
    attribute = owner.get_attribute_handle(object_class, config.attribute_name)

    offered = owner.register_object_instance(object_class, "Compat-Negotiated-1")
    owner.negotiated_attribute_ownership_divestiture(offered, {attribute}, config.assumption_tag)
    assert acquirer_federate.last_callback("requestAttributeOwnershipAssumption").args == (
        offered,
        {attribute},
        config.assumption_tag,
    )

    acquirer.attribute_ownership_acquisition(offered, {attribute}, b"acquire-tag")
    assert owner_federate.last_callback("requestDivestitureConfirmation").args == (
        offered,
        {attribute},
        b"acquire-tag",
    )
    owner.confirm_divestiture(offered, {attribute}, b"acquire-confirmed")
    assert acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification").args == (
        offered,
        {attribute},
        b"acquire-confirmed",
    )
    assert acquirer.is_attribute_owned_by_federate(offered, attribute) is True

    pending = owner.register_object_instance(object_class, "Compat-Pending-1")
    acquirer.attribute_ownership_acquisition(pending, {attribute}, config.request_tag)
    assert owner_federate.last_callback("requestAttributeOwnershipRelease").args == (
        pending,
        {attribute},
        config.request_tag,
    )
    acquirer.cancel_attribute_ownership_acquisition(pending, {attribute})
    assert acquirer_federate.last_callback("confirmAttributeOwnershipAcquisitionCancellation").args == (
        pending,
        {attribute},
    )

    acquirer.attribute_ownership_acquisition(pending, {attribute}, config.cancel_tag)
    divested = owner.attribute_ownership_divestiture_if_wanted(pending, {attribute})
    assert divested == {attribute}
    assert acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification").args == (
        pending,
        {attribute},
        b"",
    )
    assert acquirer.is_attribute_owned_by_federate(pending, attribute) is True

    confirmable = owner.register_object_instance(object_class, "Compat-Confirm-1")
    owner.negotiated_attribute_ownership_divestiture(confirmable, {attribute}, b"confirm-offer")
    assert acquirer_federate.last_callback("requestAttributeOwnershipAssumption").args == (
        confirmable,
        {attribute},
        b"confirm-offer",
    )
    acquirer.attribute_ownership_acquisition(confirmable, {attribute}, b"confirm-request")
    assert owner_federate.last_callback("requestDivestitureConfirmation").args == (
        confirmable,
        {attribute},
        b"confirm-request",
    )
    owner.confirm_divestiture(confirmable, {attribute}, b"confirm-divest")
    assert acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification").args == (
        confirmable,
        {attribute},
        b"confirm-divest",
    )
    assert acquirer.is_attribute_owned_by_federate(confirmable, attribute) is True


@pytest.mark.requirements(
    "HLA2025-FI-SVC-065",
    "HLA2025-FI-SVC-066",
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-068",
)
def test_2025_shim_runs_transportation_type_scenario_via_compat_adapter() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import TransportationTypeScenarioConfig, run_transportation_type_scenario

    federation_name = f"shim-2025-transport-adapter-{uuid.uuid4().hex[:8]}"
    owner = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    observer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = TransportationTypeScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        observer_name="Observer",
        federate_type="TransportationFederate",
        object_class_name="HLAobjectRoot.Proto2025.MessageTest.TestSuite",
        attribute_name="SuiteId",
        interaction_class_name="HLAinteractionRoot.Proto2025.MessageTest.SendStimulus",
        object_instance_name=f"transport-suite-{uuid.uuid4().hex[:8]}",
        transportation_name="HLAbestEffort",
        second_attribute_name="Name",
        parameter_name="Payload",
    )

    summary = run_transportation_type_scenario(
        owner,
        observer,
        config=config,
        owner_federate=_CompatRecordingFederateAmbassador(),
        observer_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["confirm_attribute"].args == (
        summary["object_instance"],
        {summary["attribute"]},
        summary["transport"],
    )
    assert summary["report_attribute"].args == (
        summary["object_instance"],
        summary["attribute"],
        summary["transport"],
    )
    assert summary["confirm_interaction"].args == (
        summary["interaction"],
        summary["transport"],
    )
    assert summary["report_interaction"].args[1:] == (
        summary["interaction"],
        summary["transport"],
    )


@pytest.mark.requirements(
    "HLA2025-FI-SVC-065",
    "HLA2025-FI-SVC-066",
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-068",
    "HLA2025-FI-SVC-069",
    "HLA2025-FI-SVC-070",
)
def test_2025_shim_restores_transportation_type_state_via_compat_adapter(tmp_path: Path) -> None:
    from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "CompatTransportRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Compat Transport Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused transport restore compat fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
        <attribute>
          <name>Velocity</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-transport-restore-adapter-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-TRANSPORT-COMPAT"
    owner = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    observer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    owner_federate = _CompatRecordingFederateAmbassador()
    observer_federate = _CompatRecordingFederateAmbassador()

    owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
    observer.connect(observer_federate, CallbackModel.HLA_EVOKED)
    owner.create_federation_execution(federation_name, [str(fom)])
    owner_handle = owner.join_federation_execution("Owner", "TransportationFederate", federation_name)
    observer.join_federation_execution("Observer", "TransportationFederate", federation_name)

    object_class = owner.get_object_class_handle("HLAobjectRoot.Target")
    observer_object_class = observer.get_object_class_handle("HLAobjectRoot.Target")
    reliable_attribute = owner.get_attribute_handle(object_class, "Position")
    best_effort_attribute = owner.get_attribute_handle(object_class, "Velocity")
    observer_reliable_attribute = observer.get_attribute_handle(observer_object_class, "Position")
    observer_best_effort_attribute = observer.get_attribute_handle(observer_object_class, "Velocity")
    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    observer_interaction = observer.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    parameter = owner.get_parameter_handle(interaction, "TrackId")
    reliable_transport = owner.get_transportation_type_handle("HLAreliable")
    best_effort_transport = owner.get_transportation_type_handle("HLAbestEffort")

    owner.publish_object_class_attributes(object_class, {reliable_attribute, best_effort_attribute})
    owner.publish_interaction_class(interaction)
    observer.subscribe_object_class_attributes(
        observer_object_class,
        {observer_reliable_attribute, observer_best_effort_attribute},
    )
    observer.subscribe_interaction_class(observer_interaction)

    object_instance = owner.register_object_instance(object_class, f"CompatTransportTarget-{uuid.uuid4().hex[:8]}")
    owner.request_attribute_transportation_type_change(object_instance, {reliable_attribute}, reliable_transport)
    owner.request_attribute_transportation_type_change(object_instance, {best_effort_attribute}, best_effort_transport)
    owner.request_interaction_transportation_type_change(interaction, best_effort_transport)

    owner.request_federation_save(save_label)
    assert owner_federate.last_callback("initiateFederateSave").args == (save_label,)
    assert observer_federate.last_callback("initiateFederateSave").args == (save_label,)
    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    assert owner_federate.last_callback("federationSaved").args == ()
    assert observer_federate.last_callback("federationSaved").args == ()

    owner.request_attribute_transportation_type_change(object_instance, {best_effort_attribute}, reliable_transport)
    owner.request_interaction_transportation_type_change(interaction, reliable_transport)

    owner.request_federation_restore(save_label)
    assert owner_federate.last_callback("requestFederationRestoreSucceeded").args == (save_label,)
    assert owner_federate.last_callback("federationRestoreBegun").args == ()
    assert observer_federate.last_callback("federationRestoreBegun").args == ()
    owner.federate_restore_complete()
    observer.federate_restore_complete()
    assert owner_federate.last_callback("federationRestored").args == ()
    assert observer_federate.last_callback("federationRestored").args == ()

    owner_federate.clear()
    observer_federate.clear()
    owner.query_attribute_transportation_type(object_instance, reliable_attribute)
    owner.query_attribute_transportation_type(object_instance, best_effort_attribute)
    owner.query_interaction_transportation_type(interaction)

    attribute_reports = owner_federate.callbacks_named("reportAttributeTransportationType")
    attribute_transports = {record.args[1]: record.args[2] for record in attribute_reports}
    assert attribute_transports[reliable_attribute] == reliable_transport
    assert attribute_transports[best_effort_attribute] == best_effort_transport
    assert owner_federate.last_callback("reportInteractionTransportationType").args == (
        owner_handle,
        interaction,
        best_effort_transport,
    )

    observer_federate.clear()
    owner.update_attribute_values(object_instance, {reliable_attribute: b"restored-reliable"}, b"restored-reliable-tag")
    reliable_reflect = observer_federate.last_callback("reflectAttributeValues")
    assert reliable_reflect is not None
    assert reliable_reflect.args[0] == object_instance
    assert reliable_reflect.args[1] == {observer_reliable_attribute: b"restored-reliable"}
    assert reliable_reflect.args[2] == b"restored-reliable-tag"
    assert reliable_reflect.args[4] == reliable_transport
    assert reliable_reflect.args[8:] == (OrderType.RECEIVE, None)

    owner.update_attribute_values(object_instance, {best_effort_attribute: b"restored-best-effort"}, b"restored-best-effort-tag")
    best_effort_reflect = observer_federate.last_callback("reflectAttributeValues")
    assert best_effort_reflect is not None
    assert best_effort_reflect.args[0] == object_instance
    assert best_effort_reflect.args[1] == {observer_best_effort_attribute: b"restored-best-effort"}
    assert best_effort_reflect.args[2] == b"restored-best-effort-tag"
    assert best_effort_reflect.args[8:] == (OrderType.RECEIVE, None)

    owner.send_interaction(interaction, {parameter: b"restored-track"}, b"restored-track-tag")
    received = observer_federate.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == observer_interaction
    assert received.args[1] == {observer.get_parameter_handle(observer_interaction, "TrackId"): b"restored-track"}
    assert received.args[2] == b"restored-track-tag"
    assert received.args[4] == best_effort_transport
    assert received.args[8] == OrderType.RECEIVE

    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.resign_federation_execution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    owner.destroy_federation_execution(federation_name=federation_name)
    observer.disconnect()
    owner.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-009")
def test_2025_shim_runs_synchronization_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import SynchronizationScenarioConfig, run_synchronization_scenario

    federation_name = f"shim-2025-sync-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SynchronizationScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"sync-tag",
    )

    summary = run_synchronization_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert summary["leader_registration"].args == (config.label,)
    assert summary["leader_announce"].args[:2] == (config.label, config.tag)
    assert summary["wing_announce"].args[:2] == (config.label, config.tag)
    assert summary["leader_sync"].args == (config.label, set())
    assert summary["wing_sync"].args == (config.label, set())


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-010")
def test_2025_shim_runs_synchronization_registration_failure_scenario_end_to_end() -> None:
    from hla.rti1516e.enums import SynchronizationPointFailureReason
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import SynchronizationScenarioConfig, run_synchronization_registration_failure_scenario

    federation_name = f"shim-2025-sync-failure-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SynchronizationScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"sync-tag",
    )

    summary = run_synchronization_registration_failure_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert summary["registration_success"].args == (config.label,)
    assert summary["registration_failure"].args == (
        config.label,
        SynchronizationPointFailureReason.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
    )


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-011")
def test_2025_shim_runs_failed_federate_synchronization_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import SynchronizationScenarioConfig, run_failed_federate_synchronization_scenario

    federation_name = f"shim-2025-sync-failed-set-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SynchronizationScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"sync-tag",
    )

    summary = run_failed_federate_synchronization_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
        leader_success=True,
        wing_success=False,
    )

    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert summary["leader_registration"].args == (config.label,)
    assert summary["leader_announce"].args[:2] == (config.label, config.tag)
    assert summary["wing_announce"].args[:2] == (config.label, config.tag)
    assert summary["leader_sync"].args[0] == config.label
    assert summary["wing_sync"].args[0] == config.label
    assert summary["leader_sync"].args[1] == {summary["wing_handle"]}
    assert summary["wing_sync"].args[1] == {summary["wing_handle"]}


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-012")
def test_2025_shim_runs_late_join_synchronization_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import SynchronizationScenarioConfig, run_late_join_synchronization_scenario

    federation_name = f"shim-2025-sync-late-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    late = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SynchronizationScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        late_name="Late",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"sync-tag",
    )

    summary = run_late_join_synchronization_scenario(
        leader,
        wing,
        late,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
        late_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert summary["late_handle"] is not None
    assert summary["leader_announce"].args[:2] == (config.label, config.tag)
    assert summary["wing_announce"].args[:2] == (config.label, config.tag)
    assert summary["late_announce"].args[:2] == (config.label, config.tag)
    assert summary["leader_sync"].args == (config.label, set())
    assert summary["wing_sync"].args == (config.label, set())
    assert summary["late_sync"].args == (config.label, set())


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-001", "HLA2025-FI-002", "HLA2025-FI-SVC-013")
def test_2025_shim_runs_multiple_synchronization_points_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.foms import scenario_fom_paths
    from hla.verification import SynchronizationScenarioConfig, run_multiple_synchronization_points_scenario

    federation_name = f"shim-2025-sync-multi-{uuid.uuid4().hex[:8]}"
    leader = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    wing = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    config = SynchronizationScenarioConfig(
        federation_name=federation_name,
        fom_modules=tuple(scenario_fom_paths("message-test")),
        logical_time_implementation_name="HLAinteger64Time",
        leader_name="Leader",
        wing_name="Wing",
        federate_type="SyncFederate",
        label="ReadyToRun",
        tag=b"sync-tag",
        second_label="PreRun",
        second_tag=b"prerun-tag",
    )

    summary = run_multiple_synchronization_points_scenario(
        leader,
        wing,
        config=config,
        leader_federate=_CompatRecordingFederateAmbassador(),
        wing_federate=_CompatRecordingFederateAmbassador(),
    )

    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert {record.args[:2] for record in summary["leader_announces"]} == {
        (config.label, config.tag),
        (config.second_label, config.second_tag),
    }
    assert {record.args[:2] for record in summary["wing_announces"]} == {
        (config.label, config.tag),
        (config.second_label, config.second_tag),
    }
    assert summary["first_sync_leader"].args == (config.label, set())
    assert summary["first_sync_wing"].args == (config.label, set())
    assert summary["second_sync_leader"].args == (config.second_label, set())
    assert summary["second_sync_wing"].args == (config.second_label, set())


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_integrated_time_window_gauntlet_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarTimeWindowConfig, run_target_radar_time_window_gauntlet_scenario

    federation_name = f"shim-2025-time-window-gauntlet-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    sensor = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    fast = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    slow = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    for adapter in (truth, sensor, radar, consumer, fast, slow):
        setattr(
            adapter,
            "_verification_spawn_like",
            lambda: _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim")),
        )
    truth_federate = _CompatRecordingFederateAmbassador()
    sensor_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    fast_federate = _CompatRecordingFederateAmbassador()
    slow_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarTimeWindowConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_gauntlet_scenario(
        truth,
        sensor,
        radar,
        consumer,
        fast,
        slow,
        config=config,
        truth_federate=truth_federate,
        sensor_federate=sensor_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
        fast_federate=fast_federate,
        slow_federate=slow_federate,
    )

    assert summary["certification_target"] == "lookahead-processing-window-certified"
    assert set(summary["subproofs"]) == {
        "core",
        "future_exclusion",
        "output_delivery",
        "consumer_order",
        "pipeline",
    }
    assert summary["subproofs"]["core"]["certification_target"] == "time-window-core"
    assert summary["subproofs"]["future_exclusion"]["certification_target"] == "time-window-future-exclusion"
    assert summary["subproofs"]["output_delivery"]["certification_target"] == "time-window-output-delivery"
    assert summary["subproofs"]["consumer_order"]["certification_target"] == "time-window-consumer-order"
    assert summary["subproofs"]["pipeline"]["certification_target"] == "time-window-pipeline-two-scans"
    assert summary["oracle_report"]["certification_target"] == "lookahead-processing-window-certified"
    assert summary["oracle_report"]["assertions"] == {
        "future_exclusion_blocked_until_window_safe": True,
        "core_window_closure_proved": True,
        "closed_window_output_delivered_legally": True,
        "consumer_observed_timestamp_order": True,
        "pipeline_overlapping_windows_proved": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_future_exclusion_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarFutureExclusionConfig, run_target_radar_time_window_future_exclusion_scenario

    federation_name = f"shim-2025-time-window-future-exclusion-{uuid.uuid4().hex[:8]}"
    slow = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    slow_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarFutureExclusionConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_future_exclusion_scenario(
        slow,
        radar,
        config=config,
        slow_federate=slow_federate,
        radar_federate=radar_federate,
    )

    assert summary["certification_target"] == "time-window-future-exclusion"
    assert summary["oracle_report"]["certification_target"] == "time-window-future-exclusion"
    assert summary["initial_slow_grant"].args[0].value == config.slow_initial_time
    assert summary["blocked_galt"].time.value == config.slow_initial_time + config.slow_lookahead
    assert summary["blocked_lits"].time.value == config.slow_initial_time + config.slow_lookahead
    assert summary["blocked_grant"] is None
    assert summary["clearance_slow_grant"].args[0].value == config.slow_clearance_time
    assert summary["cleared_galt"].time.value == config.scan_window_end
    assert summary["cleared_lits"].time.value == config.scan_window_end
    assert summary["final_grant"].args[0].value == config.scan_window_end
    assert summary["late_send_rejected"] is True
    assert summary["boundary_receive"].args[2] == b"boundary-track-110"
    assert summary["boundary_receive"].args[5].value == config.legal_boundary_time
    assert summary["oracle_report"]["assertions"] == {
        "radar_not_granted_to_window_end_while_future_input_possible": True,
        "blocked_grant_matches_current_galt_or_none": True,
        "future_input_exclusion_reaches_window_end": True,
        "radar_granted_to_window_end_only_after_future_input_excluded": True,
        "late_timestamp_into_closed_window_rejected": True,
        "boundary_timestamp_delivered_after_window_closure": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_output_delivery_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarOutputDeliveryConfig, run_target_radar_time_window_output_delivery_scenario

    federation_name = f"shim-2025-time-window-output-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarOutputDeliveryConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_output_delivery_scenario(
        truth,
        radar,
        consumer,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
    )

    assert summary["certification_target"] == "time-window-output-delivery"
    assert summary["oracle_report"]["certification_target"] == "time-window-output-delivery"
    assert summary["oracle_report"]["state_model"] == "OPEN -> CLOSED -> OUTPUT_PUBLISHED -> CONSUMED"
    assert summary["window_close_grant"].args[0].value == config.scan_window_end
    assert summary["consumer_receive"].args[2] == b"radar-track-output"
    assert summary["consumer_receive"].args[5].value == config.radar_output_time
    assert list(summary["consumer_receive"].args[1].values()) == [config.output_track_id.encode("utf-8")]
    assert len(summary["post_delivery_receives"]) == 1
    assert summary["oracle_report"]["assertions"] == {
        "window_closed_before_output": True,
        "output_timestamp_not_before_window_end": True,
        "consumer_received_single_track_output": True,
        "consumer_received_output_at_expected_time": True,
        "output_payload_tied_to_closed_window_inputs": True,
        "no_duplicate_output_after_consumer_readvance": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_consumer_order_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarConsumerOrderConfig, run_target_radar_time_window_consumer_order_scenario

    federation_name = f"shim-2025-time-window-order-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    other = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    other_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarConsumerOrderConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_consumer_order_scenario(
        truth,
        radar,
        other,
        consumer,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
        other_federate=other_federate,
        consumer_federate=consumer_federate,
    )

    delivered = [(record.args[2], record.args[5].value) for record in summary["consumer_receives"]]
    assert delivered == [
        (b"other-track-output", config.competing_event_time),
        (b"radar-track-output", config.radar_output_time),
    ]
    assert list(summary["consumer_receives"][0].args[1].values()) == [config.competing_track_id.encode("utf-8")]
    assert list(summary["consumer_receives"][1].args[1].values()) == [config.radar_output_track_id.encode("utf-8")]
    assert len(summary["post_readvance_receives"]) == 2
    assert summary["certification_target"] == "time-window-consumer-order"
    assert summary["oracle_report"]["certification_target"] == "time-window-consumer-order"
    assert summary["oracle_report"]["assertions"] == {
        "consumer_delivery_timestamps_sorted": True,
        "competing_event_arrives_before_radar_output": True,
        "radar_output_timestamp_not_before_window_end": True,
        "consumer_payloads_match_competing_and_radar_sources": True,
        "no_duplicate_consumer_replay_after_readvance": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_pipeline_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarPipelineConfig, run_target_radar_time_window_pipeline_scenario

    federation_name = f"shim-2025-time-window-pipeline-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarPipelineConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_pipeline_scenario(
        truth,
        radar,
        consumer,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
    )

    delivered = [(record.args[2], record.args[5].value) for record in summary["consumer_receives"]]
    assert delivered == [
        (b"scan1-track-output", config.scan1_output_time),
        (b"scan2-track-output", config.scan2_output_time),
    ]
    assert list(summary["consumer_receives"][0].args[1].values()) == [config.scan1_track_id.encode("utf-8")]
    assert list(summary["consumer_receives"][1].args[1].values()) == [config.scan2_track_id.encode("utf-8")]
    assert len(summary["post_readvance_receives"]) == 2
    assert summary["scan1_close_grant"].args[0].value == config.scan1_end
    assert summary["scan2_close_grant"].args[0].value == config.scan2_end
    assert summary["scan2_reflect"].args[2] == b"scan2-input"
    assert summary["certification_target"] == "time-window-pipeline-two-scans"
    assert summary["oracle_report"]["certification_target"] == "time-window-pipeline-two-scans"
    assert summary["oracle_report"]["assertions"] == {
        "scan1_closes_before_scan2_input": True,
        "scan2_input_collected_while_scan1_output_pending": True,
        "scan1_output_precedes_scan2_output": True,
        "no_cross_window_contamination": True,
        "scan_outputs_tied_to_their_own_window_inputs": True,
        "no_duplicate_pipeline_replay_after_readvance": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_pipeline_restore_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarPipelineRestoreConfig, run_target_radar_time_window_pipeline_restore_scenario

    federation_name = f"shim-2025-time-window-pipeline-restore-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarPipelineRestoreConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_pipeline_restore_scenario(
        truth,
        radar,
        consumer,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
    )

    assert summary["saved_radar_time"].value == config.scan2_input_time
    assert summary["saved_consumer_time"].value == config.scan1_end
    assert [record.args[2] for record in summary["dirty_consumer_receives"]] == [
        b"dirty-scan1-track-output",
        b"dirty-scan2-track-output",
    ]
    assert summary["restored_radar_time"].value == config.scan2_input_time
    assert summary["restored_consumer_time"].value == config.scan1_end
    assert summary["post_restore_scan2_reflects"] == []
    assert [record.args[2] for record in summary["restored_consumer_receives"]] == [
        b"restored-scan1-track-output",
        b"restored-scan2-track-output",
    ]
    assert list(summary["restored_consumer_receives"][0].args[1].values()) == [
        config.restored_scan1_track_id.encode("utf-8")
    ]
    assert list(summary["restored_consumer_receives"][1].args[1].values()) == [
        config.restored_scan2_track_id.encode("utf-8")
    ]
    assert len(summary["post_restore_duplicate_receives"]) == 2
    assert summary["certification_target"] == "time-window-save-restore-pipeline-resume"
    assert summary["oracle_report"]["certification_target"] == "time-window-save-restore-pipeline-resume"
    assert summary["oracle_report"]["assertions"] == {
        "restore_reinstates_saved_radar_time": True,
        "restore_reinstates_saved_consumer_time": True,
        "dirty_pipeline_outputs_do_not_replay": True,
        "scan2_collected_state_restored_without_reflection_replay": True,
        "restored_outputs_match_saved_window_inputs": True,
        "no_duplicate_restored_pipeline_outputs_after_readvance": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_receive_order_poison_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516e.enums import OrderType
    from hla.verification import TargetRadarReceiveOrderPoisonConfig, run_target_radar_time_window_receive_order_poison_scenario

    federation_name = f"shim-2025-time-window-receive-order-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarReceiveOrderPoisonConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_receive_order_poison_scenario(
        truth,
        radar,
        consumer,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
    )

    assert summary["window_close_grant"].args[0].value == config.scan_window_end
    assert summary["closed_window_tags_before"] == [b"truth-105", b"truth-106"]
    assert summary["closed_window_tags_after"] == [b"truth-105", b"truth-106"]
    assert summary["poison_reflection"].args[2] == b"receive-order-poison"
    if len(summary["poison_reflection"].args) > 8:
        assert summary["poison_reflection"].args[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)
    assert summary["consumer_receive"].args[2] == b"radar-track-output"
    assert summary["consumer_receive"].args[5].value == config.radar_output_time
    assert summary["certification_target"] == "time-window-receive-order-poison"
    assert summary["oracle_report"]["certification_target"] == "time-window-receive-order-poison"
    assert summary["oracle_report"]["assertions"] == {
        "closed_window_tags_unchanged_after_receive_order_poison": True,
        "poison_reflection_has_no_timestamp": True,
        "poison_reflection_is_receive_order": True,
        "consumer_output_still_delivered_at_expected_time": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_restore_state_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarWindowRestoreConfig, run_target_radar_time_window_restore_state_scenario

    federation_name = f"shim-2025-time-window-restore-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarWindowRestoreConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_restore_state_scenario(
        truth,
        radar,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
    )

    assert summary["first_grant"].args[0].value == config.first_input_time
    assert summary["dirty_close_grant"].args[0].value == config.scan_window_end
    assert summary["open_restored_truth_time"].value == config.first_input_time
    assert summary["open_restored_radar_time"].value == config.first_input_time
    assert summary["reclosed_grant"].args[0].value == config.scan_window_end
    assert summary["closed_restored_truth_time"].value == config.scan_window_end
    assert summary["closed_restored_radar_time"].value == config.scan_window_end
    assert summary["post_closed_restore_reflects"] == []
    assert summary["saved_open_state"]["window_closed"] is False
    assert summary["restored_open_state"]["window_closed"] is False
    assert summary["saved_closed_state"]["window_closed"] is True
    assert summary["restored_closed_state"]["window_closed"] is True
    assert summary["dirty_post_close_reflect"].args[2] == b"dirty-post-close"
    assert summary["certification_target"] == "time-window-save-restore-window-state"
    assert summary["oracle_report"]["certification_target"] == "time-window-save-restore-window-state"
    assert summary["oracle_report"]["assertions"] == {
        "open_restore_reinstates_preclosure_time": True,
        "open_restore_reinstates_open_window_state": True,
        "restored_open_branch_recloses_at_window_end": True,
        "closed_restore_reinstates_window_end_time": True,
        "closed_restore_reinstates_closed_window_state": True,
        "closed_restore_discards_dirty_post_close_callbacks": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_restore_output_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarWindowRestoreOutputConfig, run_target_radar_time_window_restore_output_scenario

    federation_name = f"shim-2025-time-window-restore-output-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarWindowRestoreOutputConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_restore_output_scenario(
        truth,
        radar,
        consumer,
        config=config,
        truth_federate=truth_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
    )

    assert summary["window_close_grant"].args[0].value == config.scan_window_end
    assert summary["saved_consumer_time"].value == config.scan_window_end
    assert summary["dirty_consumer_receive"].args[2] == b"dirty-track-output"
    assert summary["dirty_consumer_receive"].args[5].value == config.radar_output_time
    assert summary["restored_truth_time"].value == config.scan_window_end
    assert summary["restored_radar_time"].value == config.scan_window_end
    assert summary["restored_consumer_time"].value == config.scan_window_end
    assert [record.args[2] for record in summary["post_restore_receives"]] == [b"restored-track-output"]
    assert summary["restored_consumer_receive"].args[5].value == config.radar_output_time
    assert summary["certification_target"] == "time-window-save-restore-output-resume"
    assert summary["oracle_report"]["certification_target"] == "time-window-save-restore-output-resume"
    assert summary["oracle_report"]["assertions"] == {
        "closed_window_saved_before_output": True,
        "dirty_branch_output_published_before_restore": True,
        "restored_timeline_republishes_legal_output": True,
        "dirty_output_not_replayed_after_restore": True,
        "single_post_restore_output_delivery": True,
    }


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_runs_time_window_core_scenario_end_to_end() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.verification import TargetRadarTimeWindowConfig, run_target_radar_time_window_core_scenario

    federation_name = f"shim-2025-time-window-core-{uuid.uuid4().hex[:8]}"
    truth = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    sensor = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    radar = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    consumer = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    fast = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    slow = _TargetRadar2025RTIAdapter(create_rti_ambassador(backend="shim"))
    truth_federate = _CompatRecordingFederateAmbassador()
    sensor_federate = _CompatRecordingFederateAmbassador()
    radar_federate = _CompatRecordingFederateAmbassador()
    consumer_federate = _CompatRecordingFederateAmbassador()
    fast_federate = _CompatRecordingFederateAmbassador()
    slow_federate = _CompatRecordingFederateAmbassador()
    config = TargetRadarTimeWindowConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    summary = run_target_radar_time_window_core_scenario(
        truth,
        sensor,
        radar,
        consumer,
        fast,
        slow,
        config=config,
        truth_federate=truth_federate,
        sensor_federate=sensor_federate,
        radar_federate=radar_federate,
        consumer_federate=consumer_federate,
        fast_federate=fast_federate,
        slow_federate=slow_federate,
    )

    assert summary["first_grant"].args[0].value == config.truth_update_time
    assert summary["second_grant"].args[0].value == config.sensor_detection_time
    assert summary["window_close_grant"].args[0].value == config.scan_window_end
    assert summary["late_rejections"] == [
        config.scan_window_start,
        config.truth_update_time,
        config.scan_window_end - 1,
    ]
    assert int(getattr(summary["processing_progress"]["fast_time"], "value", 0)) > config.scan_window_end
    assert summary["published_output_time"].value == config.radar_output_time
    assert summary["published_output_tag"] == b"radar-track-output"
    assert all(timestamp >= config.scan_window_end for timestamp in summary["post_close_inputs"])
    assert summary["certification_target"] == "time-window-core"
    assert summary["oracle_report"]["certification_target"] == "time-window-core"
    assert summary["oracle_report"]["state_model"] == "OPEN -> CLOSABLE -> CLOSED"
    assert summary["oracle_report"]["assertions"] == {
        "pending_timestamped_messages_not_skipped": True,
        "window_not_closed_before_truth_update": True,
        "window_not_closed_before_sensor_update": True,
        "window_closed_only_at_end": True,
        "no_post_close_input_less_than_window_end": True,
    }


@pytest.mark.requirements(
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-MOD-006",
    "HLA2025-MOD-007",
    "HLA2025-FI-SVC-037",
    "HLA2025-FI-SVC-038",
    "HLA2025-FI-SVC-043",
    "HLA2025-FI-SVC-044",
)
def test_2025_shim_passive_and_universal_subscription_aliases_match_active_exchange(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "AliasExchange2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Alias Exchange 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Passive and universal alias exchange fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-alias-exchange-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("AliasPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("AliasSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    object_instance = publisher.registerObjectInstance(object_class, "AliasTarget-1")

    subscriber.subscribeObjectClassAttributesPassively(object_class, {attribute})
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "AliasTarget-1",
        publisher_handle,
    )

    publisher.publishObjectClassAttributes(object_class, {attribute})
    subscriber_callbacks.callbacks.clear()
    publisher.updateAttributeValues(object_instance, {attribute: b"alias-position"}, b"alias-update")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"alias-position"},
        b"alias-update",
        reliable,
        publisher_handle,
        set(),
    )
    assert reflection[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    subscriber.subscribeInteractionClassPassively(interaction_class)
    publisher.publishInteractionClass(interaction_class)
    subscriber_callbacks.callbacks.clear()
    publisher.sendInteraction(interaction_class, {parameter: b"passive-track"}, b"passive-interaction")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[:6] == (
        interaction_class,
        {parameter: b"passive-track"},
        b"passive-interaction",
        reliable,
        publisher_handle,
        set(),
    )
    assert received[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    subscriber.subscribeObjectClassDirectedInteractionsUniversally(object_class, {interaction_class})
    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber_callbacks.callbacks.clear()
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"universal-track"}, b"universal-directed")
    directed = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert directed is not None
    assert directed[:6] == (
        interaction_class,
        object_instance,
        {parameter: b"universal-track"},
        b"universal-directed",
        reliable,
        publisher_handle,
    )
    assert directed[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-FI-005", "HLA2025-FI-006", "HLA2025-FI-SVC-001", "HLA2025-FI-SVC-002")
def test_2025_shim_is_first_green_runtime_path() -> None:
    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import AdditionalSettingsResultCode, CallbackModel
    from hla.rti1516_2025.exceptions import FederateNotExecutionMember, NotConnected

    rti = create_rti_ambassador(spec="2025", backend="shim")
    assert rti.backend_info.details["spec"] == "rti1516_2025"
    assert rti.getHLAversion() == "IEEE 1516.1-2025"

    with pytest.raises(NotConnected):
        rti.evokeCallback(0.0)

    result = rti.connect(object(), CallbackModel.HLA_EVOKED)
    assert result.additionalSettingsResultCode is AdditionalSettingsResultCode.SETTINGS_IGNORED
    assert rti.connected is True
    assert rti.evokeMultipleCallbacks(0.0, 0.1) is False

    with pytest.raises(FederateNotExecutionMember, match="publishObjectClassAttributes"):
        rti.publishObjectClassAttributes(object(), object())

    rti.disconnect()
    assert rti.connected is False


@pytest.mark.requirements("HLA2025-FI-SVC-003")
def test_2025_shim_connection_lost_callback_tears_down_connection() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import NotConnected
    from hla.rti1516_2025.factory import create_rti_ambassador

    callbacks = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    rti.connect(callbacks, CallbackModel.HLA_EVOKED)

    rti.forceConnectionLost("transport fault")

    assert callbacks.last_callback("connectionLost") == ("transport fault",)
    assert rti.connected is False
    with pytest.raises(NotConnected):
        rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-193",
    "HLA2025-FI-SVC-194",
    "HLA2025-FI-SVC-195",
    "HLA2025-FI-SVC-196",
)
def test_2025_shim_enable_disable_callbacks_controls_evoked_delivery(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "CallbackControl2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Callback Control 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused callback control fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>CallbackPing</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>Value</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-callback-control-{uuid.uuid4().hex[:8]}"
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.CallbackPing")
    parameter = publisher.getParameterHandle(interaction_class, "Value")
    publisher.publishInteractionClass(interaction_class)
    subscriber.subscribeInteractionClass(interaction_class)

    subscriber.disableCallbacks()
    publisher.sendInteraction(interaction_class, {parameter: b"one"}, b"queued-one")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None
    assert subscriber.evokeCallback(0.0) is False

    subscriber.enableCallbacks()
    assert subscriber.evokeCallback(0.0) is True
    first = subscriber_callbacks.last_callback("receiveInteraction")
    assert first is not None
    assert first[:3] == (interaction_class, {parameter: b"one"}, b"queued-one")
    assert first[4] == publisher_handle

    subscriber_callbacks.callbacks.clear()
    subscriber.disableCallbacks()
    publisher.sendInteraction(interaction_class, {parameter: b"two"}, b"queued-two")
    publisher.sendInteraction(interaction_class, {parameter: b"three"}, b"queued-three")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.enableCallbacks()
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is True
    received_tags = [
        args[2]
        for callback_name, args in subscriber_callbacks.callbacks
        if callback_name == "receiveInteraction"
    ]
    assert received_tags == [b"queued-two", b"queued-three"]
    assert subscriber.evokeMultipleCallbacks(0.0, 0.0) is False

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-REQ-002",
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-019",
    "HLA2025-FI-SVC-020",
    "HLA2025-FI-SVC-021",
    "HLA2025-FI-SVC-022",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-024",
    "HLA2025-FI-SVC-025",
    "HLA2025-FI-SVC-026",
    "HLA2025-FI-SVC-027",
    "HLA2025-FI-SVC-028",
    "HLA2025-FI-SVC-029",
    "HLA2025-FI-SVC-030",
    "HLA2025-FI-SVC-031",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-033",
    "HLA2025-FI-SVC-034",
)
def test_2025_shim_runs_federation_save_restore_lifecycle(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction, RestoreFailureReason, RestoreStatus, SaveFailureReason, SaveStatus
    from hla.rti1516_2025.exceptions import ObjectInstanceNotKnown, RestoreNotRequested, SaveInProgress, SaveNotInitiated
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "SaveRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Save Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused save/restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>SavedTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-save-restore-{uuid.uuid4().hex[:8]}"
    leader_callbacks = Recording2025FederateAmbassador()
    wing_callbacks = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")

    leader.connect(leader_callbacks, CallbackModel.HLA_EVOKED)
    wing.connect(wing_callbacks, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    leader_handle = leader.joinFederationExecution("Leader", "TestFederate", federation_name)
    wing_handle = wing.joinFederationExecution("Wing", "TestFederate", federation_name)
    object_class = leader.getObjectClassHandle("HLAobjectRoot.SavedTarget")
    wing_object_class = wing.getObjectClassHandle("HLAobjectRoot.SavedTarget")
    attribute = leader.getAttributeHandle(object_class, "Position")
    wing_attribute = wing.getAttributeHandle(wing_object_class, "Position")
    leader.publishObjectClassAttributes(object_class, {attribute})
    wing.subscribeObjectClassAttributes(wing_object_class, {wing_attribute})
    object_instance = leader.registerObjectInstance(object_class, "Saved-Target-1")
    leader.timeAdvanceRequest(leader.getTimeFactory().makeTime(5))
    assert leader.queryLogicalTime() == leader.getTimeFactory().makeTime(5)

    with pytest.raises(SaveNotInitiated):
        leader.federateSaveComplete()
    leader.requestFederationSave("SAVE-1")
    assert leader_callbacks.last_callback("initiateFederateSave") == ("SAVE-1",)
    assert wing_callbacks.last_callback("initiateFederateSave") == ("SAVE-1",)
    with pytest.raises(SaveInProgress):
        wing.requestFederationSave("SAVE-2")
    leader.federateSaveBegun()
    leader.queryFederationSaveStatus()
    save_status = {pair.handle: pair.status for pair in leader_callbacks.last_callback("federationSaveStatusResponse")[0]}
    assert save_status[leader_handle] is SaveStatus.FEDERATE_SAVING
    assert save_status[wing_handle] is SaveStatus.FEDERATE_INSTRUCTED_TO_SAVE
    wing.federateSaveBegun()
    leader.federateSaveComplete()
    assert leader_callbacks.last_callback("federationSaved") is None
    wing.federateSaveComplete()
    assert leader_callbacks.last_callback("federationSaved") == ()
    assert wing_callbacks.last_callback("federationSaved") == ()
    leader.timeAdvanceRequest(leader.getTimeFactory().makeTime(9))
    leader.deleteObjectInstance(object_instance, b"deleted-after-save")
    with pytest.raises(ObjectInstanceNotKnown):
        wing.requestAttributeValueUpdate(object_instance, {wing_attribute}, b"deleted")
    leader.queryFederationSaveStatus()
    save_status = {pair.handle: pair.status for pair in leader_callbacks.last_callback("federationSaveStatusResponse")[0]}
    assert save_status == {
        leader_handle: SaveStatus.NO_SAVE_IN_PROGRESS,
        wing_handle: SaveStatus.NO_SAVE_IN_PROGRESS,
    }

    leader.requestFederationRestore("MISSING-SAVE")
    assert leader_callbacks.last_callback("requestFederationRestoreFailed") == ("MISSING-SAVE",)
    leader.requestFederationRestore("SAVE-1")
    assert leader_callbacks.last_callback("requestFederationRestoreSucceeded") == ("SAVE-1",)
    assert leader_callbacks.last_callback("federationRestoreBegun") == ()
    assert wing_callbacks.last_callback("initiateFederateRestore") == ("SAVE-1", "Wing", wing_handle)
    leader.queryFederationRestoreStatus()
    restore_status = {pair.preRestoreHandle: pair.status for pair in leader_callbacks.last_callback("federationRestoreStatusResponse")[0]}
    assert restore_status[leader_handle] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
    assert restore_status[wing_handle] is RestoreStatus.FEDERATE_RESTORE_REQUEST_PENDING
    leader.federateRestoreComplete()
    assert leader_callbacks.last_callback("federationRestored") is None
    wing.federateRestoreComplete()
    assert leader_callbacks.last_callback("federationRestored") == ()
    assert wing_callbacks.last_callback("federationRestored") == ()
    assert leader.queryLogicalTime() == leader.getTimeFactory().makeTime(5)
    wing.requestAttributeValueUpdate(object_instance, {wing_attribute}, b"after-restore")
    assert leader_callbacks.last_callback("provideAttributeValueUpdate") == (object_instance, {attribute}, b"after-restore")
    with pytest.raises(RestoreNotRequested):
        leader.federateRestoreComplete()

    leader.requestFederationSave("SAVE-FAIL")
    leader.federateSaveBegun()
    wing.federateSaveBegun()
    leader.federateSaveComplete()
    wing.federateSaveNotComplete()
    assert leader_callbacks.last_callback("federationNotSaved") == (SaveFailureReason.FEDERATE_REPORTED_FAILURE_DURING_SAVE,)

    leader.requestFederationSave("SAVE-ABORT")
    leader.abortFederationSave()
    assert wing_callbacks.last_callback("federationNotSaved") == (SaveFailureReason.SAVE_ABORTED,)

    leader.requestFederationRestore("SAVE-1")
    leader.abortFederationRestore()
    assert wing_callbacks.last_callback("federationNotRestored") == (RestoreFailureReason.RESTORE_ABORTED,)

    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    leader.destroyFederationExecution(federationName=federation_name)
    leader.disconnect()
    wing.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
)
def test_2025_shim_runs_example_fom_save_restore_gauntlet() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-save-restore-gauntlet-{uuid.uuid4().hex[:8]}"
    save_name = f"SAVE-GAUNTLET-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    mirror_federate = Recording2025FederateAmbassador()
    sender_federate = Recording2025FederateAmbassador()
    observer_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    mirror = create_rti_ambassador(backend="shim")
    sender = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")

    def advance_ledger(ledger: dict[str, object], *, phase: str) -> None:
        next_state = (int(ledger["random_state"]) * 1_103_515_245 + 12_345) % (2**31)
        ledger["random_state"] = next_state
        ledger["sequence_counter"] = int(ledger["sequence_counter"]) + 1
        ledger["phase"] = phase

    try:
        for rti, federate in (
            (owner, owner_federate),
            (mirror, mirror_federate),
            (sender, sender_federate),
            (observer, observer_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        owner_handle = owner.joinFederationExecution("Owner", "SaveRestoreGauntlet", federation_name)
        mirror_handle = mirror.joinFederationExecution("Mirror", "SaveRestoreGauntlet", federation_name)
        sender_handle = sender.joinFederationExecution("Owner-Sender", "SaveRestoreGauntlet", federation_name)
        observer_handle = observer.joinFederationExecution("Mirror-Observer", "SaveRestoreGauntlet", federation_name)

        role_ledgers = {
            "owner": {"role": "owner", "random_state": 101, "sequence_counter": 0, "phase": "bootstrap"},
            "mirror": {"role": "mirror", "random_state": 202, "sequence_counter": 0, "phase": "bootstrap"},
            "sender": {"role": "sender", "random_state": 303, "sequence_counter": 0, "phase": "bootstrap"},
            "observer": {"role": "observer", "random_state": 404, "sequence_counter": 0, "phase": "bootstrap"},
        }

        target_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        mirror_target_class = mirror.getObjectClassHandle("HLAobjectRoot.Target")
        owner_position = owner.getAttributeHandle(target_class, "Position")
        owner_velocity = owner.getAttributeHandle(target_class, "Velocity")
        owner_rcs = owner.getAttributeHandle(target_class, "RCS")
        mirror_position = mirror.getAttributeHandle(mirror_target_class, "Position")
        mirror_velocity = mirror.getAttributeHandle(mirror_target_class, "Velocity")
        mirror_rcs = mirror.getAttributeHandle(mirror_target_class, "RCS")
        interaction_class = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        observer_interaction_class = observer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        interaction_parameter = sender.getParameterHandle(interaction_class, "TrackId")
        observer_parameter = observer.getParameterHandle(observer_interaction_class, "TrackId")

        owner.publishObjectClassAttributes(target_class, {owner_position, owner_velocity, owner_rcs})
        mirror.subscribeObjectClassAttributes(mirror_target_class, {mirror_position, mirror_velocity, mirror_rcs})
        sender.publishInteractionClass(interaction_class)
        observer.subscribeInteractionClass(observer_interaction_class)

        owner.enableTimeRegulation(HLAinteger64Interval(1))
        sender.enableTimeRegulation(HLAinteger64Interval(1))
        mirror.enableTimeConstrained()
        observer.enableTimeConstrained()
        sender.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)

        object_instance = owner.registerObjectInstance(target_class, "Target-Checkpoint-1")
        owner.changeAttributeOrderType(object_instance, {owner_position, owner_velocity, owner_rcs}, OrderType.TIMESTAMP)
        mirror_object_instance = mirror.getObjectInstanceHandle("Target-Checkpoint-1")

        saved_position = struct.pack(">ddd", 10_000.0, 1_000.0, 2_000.0)
        saved_velocity = struct.pack(">ddd", 250.0, 30.0, 0.0)
        saved_rcs = struct.pack(">d", 12.5)
        dirty_position = struct.pack(">ddd", 99_999.0, 88_888.0, 77_777.0)
        dirty_velocity = struct.pack(">ddd", 0.0, 0.0, 0.0)
        dirty_rcs = struct.pack(">d", 0.5)
        branch_position = struct.pack(">ddd", 10_250.0, 1_030.0, 2_000.0)

        owner.updateAttributeValues(
            object_instance,
            {owner_position: saved_position, owner_velocity: saved_velocity, owner_rcs: saved_rcs},
            b"baseline-attributes",
            HLAinteger64Time(4),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"baseline-track"},
            b"baseline-track",
            HLAinteger64Time(5),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(5))

        baseline_reflect = mirror_federate.last_callback("reflectAttributeValues")
        baseline_interaction = observer_federate.last_callback("receiveInteraction")
        assert baseline_reflect is not None
        assert baseline_interaction is not None
        assert baseline_reflect[0] == mirror_object_instance
        assert baseline_reflect[1][mirror_position] == saved_position
        assert baseline_reflect[1][mirror_velocity] == saved_velocity
        assert baseline_reflect[1][mirror_rcs] == saved_rcs
        assert baseline_interaction[0] == observer_interaction_class
        assert baseline_interaction[1] == {observer_parameter: b"baseline-track"}

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="saved")
        saved_ledgers = {role: dict(ledger) for role, ledger in role_ledgers.items()}
        saved_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in saved_ledgers.items()}

        owner.requestFederationSave(save_name)
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("initiateFederateSave") == (save_name,)
        for rti in (owner, mirror, sender, observer):
            rti.federateSaveBegun()
        for rti in (owner, mirror, sender, observer):
            rti.federateSaveComplete()
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("federationSaved") == ()

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="dirty")
        dirty_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in role_ledgers.items()}
        assert dirty_fingerprints != saved_fingerprints

        owner.updateAttributeValues(
            object_instance,
            {owner_position: dirty_position, owner_velocity: dirty_velocity, owner_rcs: dirty_rcs},
            b"dirty-attributes",
            HLAinteger64Time(7),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"dirty-track"},
            b"dirty-track",
            HLAinteger64Time(8),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(8))
        dirty_reflect = _callbacks_named_2025(mirror_federate, "reflectAttributeValues")[-1]
        dirty_interaction = _callbacks_named_2025(observer_federate, "receiveInteraction")[-1]
        assert dirty_reflect[1][mirror_position] == dirty_position
        assert dirty_interaction[1] == {observer_parameter: b"dirty-track"}

        owner.deleteObjectInstance(object_instance, b"dirty-delete")
        dirty_remove = mirror_federate.last_callback("removeObjectInstance")
        assert dirty_remove is not None
        assert dirty_remove[0] == mirror_object_instance
        assert dirty_remove[1] == b"dirty-delete"

        owner.requestFederationRestore(save_name)
        assert owner_federate.last_callback("requestFederationRestoreSucceeded") == (save_name,)
        assert owner_federate.last_callback("initiateFederateRestore") == (save_name, "Owner", owner_handle)
        assert mirror_federate.last_callback("initiateFederateRestore") == (save_name, "Mirror", mirror_handle)
        assert sender_federate.last_callback("initiateFederateRestore") == (save_name, "Owner-Sender", sender_handle)
        assert observer_federate.last_callback("initiateFederateRestore") == (save_name, "Mirror-Observer", observer_handle)

        restored_ledgers = {role: dict(ledger) for role, ledger in saved_ledgers.items()}
        for rti in (owner, mirror, sender, observer):
            rti.federateRestoreComplete()
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("federationRestored") == ()

        restored_times = {
            "owner": owner.queryLogicalTime(),
            "mirror": mirror.queryLogicalTime(),
            "sender": sender.queryLogicalTime(),
            "observer": observer.queryLogicalTime(),
        }
        assert all(time == HLAinteger64Time(5) for time in restored_times.values())
        restored_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in restored_ledgers.items()}
        assert restored_fingerprints == saved_fingerprints
        assert owner.getObjectInstanceName(object_instance) == "Target-Checkpoint-1"

        mirror_federate.callbacks.clear()
        observer_federate.callbacks.clear()
        owner.updateAttributeValues(
            object_instance,
            {owner_position: branch_position, owner_velocity: saved_velocity, owner_rcs: saved_rcs},
            b"branch-attributes",
            HLAinteger64Time(7),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"branch-track"},
            b"branch-track",
            HLAinteger64Time(7),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(8))

        branch_reflect = mirror_federate.last_callback("reflectAttributeValues")
        branch_interaction = observer_federate.last_callback("receiveInteraction")
        assert branch_reflect is not None
        assert branch_interaction is not None
        assert branch_reflect[0] == mirror_object_instance
        assert branch_reflect[1][mirror_position] == branch_position
        assert branch_interaction[1] == {observer_parameter: b"branch-track"}
        branch_tags = {args[2] for name, args in mirror_federate.callbacks if name == "reflectAttributeValues"}
        branch_tags.update(args[2] for name, args in observer_federate.callbacks if name == "receiveInteraction")
        assert b"dirty-attributes" not in branch_tags
        assert b"dirty-track" not in branch_tags
        remove_tags = {args[1] for name, args in mirror_federate.callbacks if name == "removeObjectInstance"}
        assert b"dirty-delete" not in remove_tags
    finally:
        for rti in (observer, sender, mirror, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (observer, sender, mirror, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-097",
)
def test_2025_shim_runs_smoke_fom_save_restore_ownership_gauntlet(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    smoke_fom = tmp_path / "SmokeSaveRestore2025.xml"
    smoke_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Smoke Save Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused smoke FOM for save/restore ownership rollback.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter>
          <name>TrackId</name>
          <dataType>HLAunicodeString</dataType>
        </parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )
    federation_name = f"shim-2025-smoke-ownership-restore-{uuid.uuid4().hex[:8]}"
    save_name = f"SAVE-OWNERSHIP-GAUNTLET-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    mirror_federate = Recording2025FederateAmbassador()
    sender_federate = Recording2025FederateAmbassador()
    observer_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    mirror = create_rti_ambassador(backend="shim")
    sender = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")

    def advance_ledger(ledger: dict[str, object], *, phase: str) -> None:
        next_state = (int(ledger["random_state"]) * 1_103_515_245 + 12_345) % (2**31)
        ledger["random_state"] = next_state
        ledger["sequence_counter"] = int(ledger["sequence_counter"]) + 1
        ledger["phase"] = phase

    try:
        for rti, federate in (
            (owner, owner_federate),
            (mirror, mirror_federate),
            (sender, sender_federate),
            (observer, observer_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(
            federationName=federation_name,
            fomModule=str(smoke_fom),
            logicalTimeImplementationName="HLAinteger64Time",
        )
        owner_handle = owner.joinFederationExecution("Owner", "SaveRestoreGauntlet", federation_name)
        mirror.joinFederationExecution("Mirror", "SaveRestoreGauntlet", federation_name)
        sender.joinFederationExecution("Owner-Sender", "SaveRestoreGauntlet", federation_name)
        observer.joinFederationExecution("Mirror-Observer", "SaveRestoreGauntlet", federation_name)

        role_ledgers = {
            "owner": {"role": "owner", "random_state": 111, "sequence_counter": 0, "phase": "bootstrap"},
            "mirror": {"role": "mirror", "random_state": 222, "sequence_counter": 0, "phase": "bootstrap"},
            "sender": {"role": "sender", "random_state": 333, "sequence_counter": 0, "phase": "bootstrap"},
            "observer": {"role": "observer", "random_state": 444, "sequence_counter": 0, "phase": "bootstrap"},
        }

        owner_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        mirror_class = mirror.getObjectClassHandle("HLAobjectRoot.Target")
        observer_class = observer.getObjectClassHandle("HLAobjectRoot.Target")
        owner_attribute = owner.getAttributeHandle(owner_class, "Position")
        mirror_attribute = mirror.getAttributeHandle(mirror_class, "Position")
        observer_attribute = observer.getAttributeHandle(observer_class, "Position")
        interaction_class = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        observer_interaction = observer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        interaction_parameter = sender.getParameterHandle(interaction_class, "TrackId")
        observer_parameter = observer.getParameterHandle(observer_interaction, "TrackId")

        owner.publishObjectClassAttributes(owner_class, {owner_attribute})
        mirror.publishObjectClassAttributes(mirror_class, {mirror_attribute})
        mirror.subscribeObjectClassAttributes(mirror_class, {mirror_attribute})
        observer.subscribeObjectClassAttributes(observer_class, {observer_attribute})
        sender.publishInteractionClass(interaction_class)
        observer.subscribeInteractionClass(observer_interaction)

        owner.enableTimeRegulation(HLAinteger64Interval(1))
        sender.enableTimeRegulation(HLAinteger64Interval(1))
        mirror.enableTimeConstrained()
        observer.enableTimeConstrained()
        sender.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)

        object_instance = owner.registerObjectInstance(owner_class, "Owned-Target-Checkpoint-1")
        owner.changeAttributeOrderType(object_instance, {owner_attribute}, OrderType.TIMESTAMP)
        mirror_object_instance = mirror.getObjectInstanceHandle("Owned-Target-Checkpoint-1")
        observer_object_instance = observer.getObjectInstanceHandle("Owned-Target-Checkpoint-1")

        saved_payload = b"saved-payload"
        dirty_payload = b"dirty-payload"
        branch_payload = b"branch-payload"

        owner.updateAttributeValues(
            object_instance,
            {owner_attribute: saved_payload},
            b"baseline-attributes",
            HLAinteger64Time(4),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"baseline-message"},
            b"baseline-message",
            HLAinteger64Time(5),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(5))

        baseline_reflect = observer_federate.last_callback("reflectAttributeValues")
        baseline_interaction = observer_federate.last_callback("receiveInteraction")
        assert baseline_reflect is not None
        assert baseline_interaction is not None
        assert baseline_reflect[0] == observer_object_instance
        assert baseline_reflect[1] == {observer_attribute: saved_payload}
        assert baseline_interaction[1] == {observer_parameter: b"baseline-message"}
        assert owner.isAttributeOwnedByFederate(object_instance, owner_attribute) is True
        assert mirror.isAttributeOwnedByFederate(mirror_object_instance, mirror_attribute) is False

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="saved")
        saved_ledgers = {role: dict(ledger) for role, ledger in role_ledgers.items()}
        saved_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in saved_ledgers.items()}

        owner.requestFederationSave(save_name)
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("initiateFederateSave") == (save_name,)
        for rti in (owner, mirror, sender, observer):
            rti.federateSaveBegun()
        for rti in (owner, mirror, sender, observer):
            rti.federateSaveComplete()
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("federationSaved") == ()

        for ledger in role_ledgers.values():
            advance_ledger(ledger, phase="dirty")
        dirty_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in role_ledgers.items()}
        assert dirty_fingerprints != saved_fingerprints

        owner.unconditionalAttributeOwnershipDivestiture(object_instance, {owner_attribute}, b"dirty-divest")
        owner.queryAttributeOwnership(object_instance, {owner_attribute})
        assert owner_federate.last_callback("attributeIsNotOwned") == (object_instance, {owner_attribute})

        mirror.attributeOwnershipAcquisitionIfAvailable(mirror_object_instance, {mirror_attribute}, b"claim")
        dirty_acquired = mirror_federate.last_callback("attributeOwnershipAcquisitionNotification")
        assert dirty_acquired == (mirror_object_instance, {mirror_attribute}, b"claim")
        assert mirror.isAttributeOwnedByFederate(mirror_object_instance, mirror_attribute) is True
        assert owner.isAttributeOwnedByFederate(object_instance, owner_attribute) is False

        mirror.updateAttributeValues(mirror_object_instance, {mirror_attribute: dirty_payload}, b"dirty-attributes")
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"dirty-message"},
            b"dirty-message",
            HLAinteger64Time(8),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(8))

        dirty_reflect = _callbacks_named_2025(observer_federate, "reflectAttributeValues")[-1]
        dirty_interaction = _callbacks_named_2025(observer_federate, "receiveInteraction")[-1]
        assert dirty_reflect[0] == observer_object_instance
        assert dirty_reflect[1] == {observer_attribute: dirty_payload}
        assert dirty_interaction[1] == {observer_parameter: b"dirty-message"}

        owner.requestFederationRestore(save_name)
        assert owner_federate.last_callback("requestFederationRestoreSucceeded") == (save_name,)
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("initiateFederateRestore")[0] == save_name
        restored_ledgers = {role: dict(ledger) for role, ledger in saved_ledgers.items()}

        for rti in (owner, mirror, sender, observer):
            rti.federateRestoreComplete()
        for federate in (owner_federate, mirror_federate, sender_federate, observer_federate):
            assert federate.last_callback("federationRestored") == ()

        restored_times = {
            "owner": owner.queryLogicalTime(),
            "mirror": mirror.queryLogicalTime(),
            "sender": sender.queryLogicalTime(),
            "observer": observer.queryLogicalTime(),
        }
        assert all(time == HLAinteger64Time(5) for time in restored_times.values())
        restored_fingerprints = {role: json.dumps(ledger, sort_keys=True) for role, ledger in restored_ledgers.items()}
        assert restored_fingerprints == saved_fingerprints

        owner_federate.callbacks.clear()
        observer_federate.callbacks.clear()

        owner.queryAttributeOwnership(object_instance, {owner_attribute})
        restored_informed = owner_federate.last_callback("informAttributeOwnership")
        assert restored_informed == (object_instance, {owner_attribute}, owner_handle)
        assert owner.isAttributeOwnedByFederate(object_instance, owner_attribute) is True
        assert mirror.isAttributeOwnedByFederate(mirror_object_instance, mirror_attribute) is False

        owner.updateAttributeValues(
            object_instance,
            {owner_attribute: branch_payload},
            b"branch-attributes",
            HLAinteger64Time(7),
        )
        sender.sendInteraction(
            interaction_class,
            {interaction_parameter: b"branch-message"},
            b"branch-message",
            HLAinteger64Time(7),
        )
        for rti in (owner, mirror, sender, observer):
            rti.timeAdvanceRequestAvailable(HLAinteger64Time(8))

        branch_reflect = observer_federate.last_callback("reflectAttributeValues")
        branch_interaction = observer_federate.last_callback("receiveInteraction")
        assert branch_reflect is not None
        assert branch_interaction is not None
        assert branch_reflect[0] == observer_object_instance
        assert branch_reflect[1] == {observer_attribute: branch_payload}
        assert branch_interaction[1] == {observer_parameter: b"branch-message"}
        branch_tags = {args[2] for name, args in observer_federate.callbacks if name == "reflectAttributeValues"}
        branch_tags.update(args[2] for name, args in observer_federate.callbacks if name == "receiveInteraction")
        assert b"dirty-attributes" not in branch_tags
        assert b"dirty-message" not in branch_tags
    finally:
        for rti, action in (
            (observer, ResignAction.NO_ACTION),
            (sender, ResignAction.NO_ACTION),
            (mirror, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),
            (owner, ResignAction.DELETE_OBJECTS),
        ):
            try:
                rti.resignFederationExecution(action)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (observer, sender, mirror, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
)
def test_2025_shim_routes_directed_interactions_to_object_class_subscribers(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "DirectedInteraction2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Directed Interaction 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused directed interaction fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(
        federationName=federation_name,
        fomModule=str(fom),
    )
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")
    object_instance = publisher.registerObjectInstance(object_class, "Directed-Target-1")

    with pytest.raises(InteractionClassNotPublished):
        publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-1"}, b"not-published")

    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {interaction_class})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-1"}, b"directed-tag")

    received = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert received == (
        interaction_class,
        object_instance,
        {parameter: b"T-1"},
        b"directed-tag",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeObjectClassDirectedInteractions(object_class, {interaction_class})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-2"}, b"after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    publisher.unpublishObjectClassDirectedInteractions(object_class, {interaction_class})
    with pytest.raises(InteractionClassNotPublished):
        publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"T-3"}, b"after-unpublish")

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FR-010",
    "HLA2025-FI-SVC-112",
)
def test_2025_shim_queues_timestamped_directed_interactions_until_time_advance(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import MessageCanNoLongerBeRetracted
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    fom = tmp_path / "TimedDirectedInteraction2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Timed Directed Interaction 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-20</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Timestamped directed interaction fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Timestamp</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Timestamp</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-tso-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)
    subscriber.enableTimeConstrained()

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")
    object_instance = publisher.registerObjectInstance(object_class, "Directed-Target-TSO")

    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {interaction_class})

    late = publisher.sendDirectedInteraction(
        interaction_class,
        object_instance,
        {parameter: b"late"},
        b"late",
        HLAinteger64Time(20),
    )
    retracted = publisher.sendDirectedInteraction(
        interaction_class,
        object_instance,
        {parameter: b"retracted"},
        b"retracted",
        HLAinteger64Time(15),
    )
    assert late.retractionHandleIsValid is True
    assert retracted.retractionHandleIsValid is True
    publisher.retract(retracted.handle)

    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None
    subscriber.timeAdvanceRequest(HLAinteger64Time(12))
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    subscriber.timeAdvanceRequest(HLAinteger64Time(25))
    received = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert received is not None
    assert received[:6] == (
        interaction_class,
        object_instance,
        {parameter: b"late"},
        b"late",
        reliable,
        publisher_handle,
    )
    assert received[6:] == (HLAinteger64Time(20), OrderType.TIMESTAMP, OrderType.TIMESTAMP, late.handle)
    publisher.retract(late.handle)
    request_retraction = subscriber_callbacks.last_callback("requestRetraction")
    assert request_retraction == (late.handle,)
    with pytest.raises(MessageCanNoLongerBeRetracted):
        publisher.retract(late.handle)

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-129",
    "HLA2025-FI-SVC-134",
    "HLA2025-FI-SVC-135",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
)
def test_2025_shim_filters_directed_interactions_by_ddm_region_overlap(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "DirectedInteractionRegionDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Directed Interaction Region DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Directed interaction DDM overlap fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-ddm-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishObjectClassDirectedInteractions(object_class, {interaction_class})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {interaction_class})
    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstanceWithRegions(
        object_class,
        [({attribute}, {publisher_region})],
        "Directed-Region-Target-1",
    )
    subscriber.subscribeInteractionClassWithRegions(interaction_class, {subscriber_region})

    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"outside"}, b"outside-region")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"inside"}, b"inside-region")
    received = subscriber_callbacks.last_callback("receiveDirectedInteraction")
    assert received == (
        interaction_class,
        object_instance,
        {parameter: b"inside"},
        b"inside-region",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeInteractionClassWithRegions(interaction_class, {subscriber_region})
    publisher.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"after"}, b"after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-001",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-039",
    "HLA2025-FI-SVC-040",
    "HLA2025-FI-SVC-045",
    "HLA2025-FI-SVC-046",
)
def test_2025_shim_directed_interaction_set_unsubscribe_and_unpublish_are_selective(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "SelectiveDirectedInteraction2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Selective Directed Interaction 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Directed interaction selective set fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
      <interactionClass>
        <name>AlertReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>AlertId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-directed-set-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("DirectedPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("DirectedSubscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.Target")
    track_report = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    alert_report = publisher.getInteractionClassHandle("HLAinteractionRoot.AlertReport")
    track_parameter = publisher.getParameterHandle(track_report, "TrackId")
    alert_parameter = publisher.getParameterHandle(alert_report, "AlertId")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")
    object_instance = publisher.registerObjectInstance(object_class, "Directed-Selective-Target-1")

    publisher.publishObjectClassDirectedInteractions(object_class, {track_report, alert_report})
    subscriber.subscribeObjectClassDirectedInteractions(object_class, {track_report, alert_report})

    publisher.sendDirectedInteraction(track_report, object_instance, {track_parameter: b"T-1"}, b"track-before")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") == (
        track_report,
        object_instance,
        {track_parameter: b"T-1"},
        b"track-before",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeObjectClassDirectedInteractions(object_class, {track_report})
    publisher.sendDirectedInteraction(track_report, object_instance, {track_parameter: b"T-2"}, b"track-after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") is None

    publisher.sendDirectedInteraction(alert_report, object_instance, {alert_parameter: b"A-1"}, b"alert-still-subscribed")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") == (
        alert_report,
        object_instance,
        {alert_parameter: b"A-1"},
        b"alert-still-subscribed",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    publisher.unpublishObjectClassDirectedInteractions(object_class, {track_report})
    with pytest.raises(InteractionClassNotPublished):
        publisher.sendDirectedInteraction(track_report, object_instance, {track_parameter: b"T-3"}, b"track-after-unpublish")

    publisher.sendDirectedInteraction(alert_report, object_instance, {alert_parameter: b"A-2"}, b"alert-still-published")
    assert subscriber_callbacks.last_callback("receiveDirectedInteraction") == (
        alert_report,
        object_instance,
        {alert_parameter: b"A-2"},
        b"alert-still-published",
        reliable,
        publisher_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    subscriber.disconnect()
    publisher.disconnect()


@pytest.mark.requirements("HLA2025-FI-SVC-051", "HLA2025-FI-SVC-052", "HLA2025-FI-SVC-053", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_supports_single_object_instance_name_reservation_callback_and_release() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateNotExecutionMember,
        NotConnected,
        ObjectInstanceNameNotReserved,
        RestoreInProgress,
        SaveInProgress,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    unjoined = create_rti_ambassador(backend="shim")
    with pytest.raises(NotConnected):
        unjoined.releaseObjectInstanceName("PreJoin-A")

    unjoined.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        unjoined.releaseObjectInstanceName("PreJoin-A")
    unjoined.disconnect()

    federation_name = f"shim-single-name-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    rival_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    rival = create_rti_ambassador(backend="shim")
    owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
    rival.connect(rival_federate, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule="TargetRadarFOMmodule.xml")
    owner.joinFederationExecution(
        federateName="Owner",
        federateType="TestFederate",
        federationName=federation_name,
    )
    rival.joinFederationExecution(
        federateName="Rival",
        federateType="TestFederate",
        federationName=federation_name,
    )

    reserved_name = "Reserved-Solo"
    owner.reserveObjectInstanceName(reserved_name)
    assert owner_federate.last_callback("objectInstanceNameReservationSucceeded") == (reserved_name,)

    rival.reserveObjectInstanceName(reserved_name)
    assert rival_federate.last_callback("objectInstanceNameReservationFailed") == (reserved_name,)

    owner.requestFederationSave("SINGLE-NAME-SAVE")
    with pytest.raises(SaveInProgress):
        owner.releaseObjectInstanceName(reserved_name)
    owner.abortFederationSave()

    owner.requestFederationSave("SINGLE-NAME-RESTORE")
    owner.federateSaveBegun()
    rival.federateSaveBegun()
    owner.federateSaveComplete()
    rival.federateSaveComplete()
    owner.requestFederationRestore("SINGLE-NAME-RESTORE")
    with pytest.raises(RestoreInProgress):
        owner.releaseObjectInstanceName(reserved_name)
    owner.federateRestoreComplete()
    rival.federateRestoreComplete()

    rival.reserveObjectInstanceName(reserved_name)
    assert rival_federate.last_callback("objectInstanceNameReservationFailed") == (reserved_name,)

    owner.releaseObjectInstanceName(reserved_name)
    rival.reserveObjectInstanceName(reserved_name)
    assert rival_federate.last_callback("objectInstanceNameReservationSucceeded") == (reserved_name,)

    with pytest.raises(ObjectInstanceNameNotReserved):
        owner.releaseObjectInstanceName(reserved_name)

    rival.releaseObjectInstanceName(reserved_name)

    rival.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    rival.disconnect()
    owner.disconnect()


@pytest.mark.requirements("HLA2025-FI-SVC-054", "HLA2025-FI-SVC-055", "HLA2025-FI-SVC-056", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_supports_multiple_object_instance_name_reservation_and_release() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateNotExecutionMember,
        NotConnected,
        ObjectInstanceNameNotReserved,
        RTIinternalError,
        RestoreInProgress,
        SaveInProgress,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    unjoined = create_rti_ambassador(backend="shim")
    with pytest.raises(NotConnected):
        unjoined.reserveMultipleObjectInstanceNames({"PreJoin-A"})
    with pytest.raises(NotConnected):
        unjoined.releaseMultipleObjectInstanceNames({"PreJoin-A"})

    unjoined.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        unjoined.reserveMultipleObjectInstanceNames({"PreJoin-A"})
    with pytest.raises(FederateNotExecutionMember):
        unjoined.releaseMultipleObjectInstanceNames({"PreJoin-A"})
    unjoined.disconnect()

    federation_name = f"shim-multi-name-{uuid.uuid4().hex[:8]}"
    owner_federate = Recording2025FederateAmbassador()
    rival_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    rival = create_rti_ambassador(backend="shim")
    owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
    rival.connect(rival_federate, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule="TargetRadarFOMmodule.xml")
    owner.joinFederationExecution(
        federateName="Owner",
        federateType="TestFederate",
        federationName=federation_name,
    )
    rival.joinFederationExecution(
        federateName="Rival",
        federateType="TestFederate",
        federationName=federation_name,
    )

    names = {"Reserve-A", "Reserve-B"}
    owner.reserveMultipleObjectInstanceNames(names)
    assert owner_federate.last_callback("multipleObjectInstanceNameReservationSucceeded") == (names,)

    rival.reserveMultipleObjectInstanceNames(names)
    assert rival_federate.last_callback("multipleObjectInstanceNameReservationFailed") == (names,)

    with pytest.raises(RTIinternalError):
        owner.reserveMultipleObjectInstanceNames(set())
    with pytest.raises(RTIinternalError):
        owner.releaseMultipleObjectInstanceNames(set())

    owner.requestFederationSave("MULTI-NAME-SAVE")
    with pytest.raises(SaveInProgress):
        owner.reserveMultipleObjectInstanceNames({"Save-Blocked"})
    with pytest.raises(SaveInProgress):
        owner.releaseMultipleObjectInstanceNames(names)
    owner.abortFederationSave()

    owner.reserveMultipleObjectInstanceNames({"Restore-Blocked"})
    owner.requestFederationSave("MULTI-NAME-RESTORE")
    owner.federateSaveBegun()
    rival.federateSaveBegun()
    owner.federateSaveComplete()
    rival.federateSaveComplete()
    owner.requestFederationRestore("MULTI-NAME-RESTORE")
    with pytest.raises(RestoreInProgress):
        owner.reserveMultipleObjectInstanceNames({"Restore-Locked"})
    with pytest.raises(RestoreInProgress):
        owner.releaseMultipleObjectInstanceNames({"Restore-Blocked"})
    owner.federateRestoreComplete()
    rival.federateRestoreComplete()
    rival.reserveMultipleObjectInstanceNames({"Restore-Blocked"})
    assert rival_federate.last_callback("multipleObjectInstanceNameReservationFailed") == ({"Restore-Blocked"},)
    owner.releaseMultipleObjectInstanceNames({"Restore-Blocked"})

    owner.releaseMultipleObjectInstanceNames(names)
    rival.reserveMultipleObjectInstanceNames(names)
    assert rival_federate.last_callback("multipleObjectInstanceNameReservationSucceeded") == (names,)

    with pytest.raises(ObjectInstanceNameNotReserved):
        owner.releaseMultipleObjectInstanceNames(names)

    rival.releaseMultipleObjectInstanceNames(names)

    rival.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    rival.disconnect()
    owner.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-NEW-004",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-162",
    "HLA2025-FI-SVC-163",
    "HLA2025-FI-SVC-164",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-076",
    "HLA2025-FI-SVC-124",
    "HLA2025-FI-SVC-157",
)
def test_2025_shim_implements_fom_backed_ddm_lookup_and_default_attribute_policy(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import (
        AttributeNotDefined,
        InvalidAttributeHandle,
        InvalidDimensionHandle,
        InvalidObjectClassHandle,
        InvalidOrderType,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import AttributeHandle, DimensionHandle, ObjectClassHandle

    fom = tmp_path / "PolicyDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Policy DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused DDM/default attribute policy fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>PolicyTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>1024</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-ddm-policy-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    rti.joinFederationExecution(
        federateName="PolicyFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    object_class = rti.getObjectClassHandle("HLAobjectRoot.PolicyTarget")
    assert rti.getObjectClassName(object_class) == "HLAobjectRoot.PolicyTarget"
    attribute = rti.getAttributeHandle(object_class, "Position")
    assert rti.getAttributeName(object_class, attribute) == "Position"
    dimension = rti.getDimensionHandle("RoutingSpace")
    assert rti.getDimensionName(dimension) == "RoutingSpace"
    assert rti.getDimensionUpperBound(dimension) == 1024
    available_dimensions = rti.getAvailableDimensionsForObjectClass(object_class)
    assert dimension in available_dimensions
    assert {rti.getDimensionName(handle) for handle in available_dimensions} >= {"RoutingSpace"}
    assert rti.getTransportationTypeName(rti.getTransportationTypeHandle("HLAbestEffort")) == "HLAbestEffort"
    region = rti.createRegion({dimension})
    rti.setRangeBounds(region, dimension, RangeBounds(0, 10))
    assert dimension in rti.getDimensionHandleSet(region)
    assert rti.getRangeBounds(region, dimension) == RangeBounds(0, 10)

    rti.changeDefaultAttributeTransportationType(
        object_class,
        {attribute},
        rti.getTransportationTypeHandle("HLAbestEffort"),
    )
    rti.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.TIMESTAMP)
    assert rti.defaultAttributePolicySnapshot() == {
        "transportation": {"HLAobjectRoot.PolicyTarget.Position": "HLAbestEffort"},
        "order": {"HLAobjectRoot.PolicyTarget.Position": "TIMESTAMP"},
    }

    with pytest.raises(InvalidObjectClassHandle):
        rti.getAvailableDimensionsForObjectClass(ObjectClassHandle(9999))
    with pytest.raises(InvalidDimensionHandle):
        rti.getDimensionUpperBound(DimensionHandle(9999))
    with pytest.raises(AttributeNotDefined):
        rti.getAttributeHandle(object_class, "Missing")
    with pytest.raises(InvalidAttributeHandle):
        rti.changeDefaultAttributeOrderType(object_class, {AttributeHandle(9999)}, OrderType.RECEIVE)
    with pytest.raises(InvalidOrderType):
        rti.changeDefaultAttributeOrderType(object_class, {attribute}, "bad-order")

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-130",
    "HLA2025-FI-SVC-132",
)
def test_2025_shim_filters_object_reflections_by_ddm_region_overlap(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "RegionDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Region DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused region overlap fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RegionalTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-ddm-region-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)
    subscriber.setAttributeScopeAdvisorySwitch(True)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.RegionalTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    publisher.publishObjectClassAttributes(object_class, {attribute})

    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstance(object_class, "Region-Target-1")
    publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])

    assert subscriber_callbacks.last_callback("discoverObjectInstance") is None
    assert subscriber_callbacks.last_callback("attributesInScope") is None
    assert subscriber_callbacks.last_callback("attributesOutOfScope") is None
    publisher.updateAttributeValues(object_instance, {attribute: b"outside"}, b"outside-region")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
    assert subscriber_callbacks.last_callback("attributesInScope") == (object_instance, {attribute})
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "Region-Target-1",
        publisher_handle,
    )

    publisher.updateAttributeValues(object_instance, {attribute: b"inside"}, b"inside-region")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"inside"},
        b"inside-region",
        publisher.getTransportationTypeHandle("HLAreliable"),
        publisher_handle,
        {publisher_region},
    )

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    subscriber.commitRegionModifications({subscriber_region})
    assert subscriber_callbacks.last_callback("attributesOutOfScope") == (object_instance, {attribute})
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(0, 10))
    subscriber.commitRegionModifications({subscriber_region})
    assert subscriber_callbacks.last_callback("attributesInScope") == (object_instance, {attribute})

    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-134",
    "HLA2025-FI-SVC-135",
    "HLA2025-FI-SVC-136",
)
def test_2025_shim_filters_interactions_by_ddm_region_overlap(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "InteractionRegionDDM2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Interaction Region DDM 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused interaction DDM overlap fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>RegionalReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-interaction-ddm-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishInteractionClass(interaction_class)
    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})

    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"outside"}, {publisher_region}, b"outside-region")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"inside"}, {publisher_region}, b"inside-region")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received == (
        interaction_class,
        {parameter: b"inside"},
        b"inside-region",
        reliable,
        publisher_handle,
        {publisher_region},
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"after"}, {publisher_region}, b"after-unsubscribe")
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


def test_2025_shim_preserves_direct_callback_context_for_timed_region_delivery(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    fom = tmp_path / "TimedRegionContext2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Timed Region Context 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Timed regional callback-context fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RegionalTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>RegionalReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-timed-region-context-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.RegionalTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.publishInteractionClass(interaction_class)

    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(0, 10))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstance(object_class, "TimedRegionTarget-1")
    publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
    subscriber.subscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
    subscriber.subscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})

    publisher.enableTimeRegulation(HLAinteger64Interval(1))
    subscriber.enableTimeConstrained()
    publisher.changeAttributeOrderType(object_instance, {attribute}, OrderType.TIMESTAMP)
    publisher.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)

    attribute_result = publisher.updateAttributeValues(
        object_instance,
        {attribute: b"inside"},
        b"inside-tag",
        HLAinteger64Time(10),
    )
    interaction_result = publisher.sendInteractionWithRegions(
        interaction_class,
        {parameter: b"track"},
        {publisher_region},
        b"track-tag",
        HLAinteger64Time(12),
    )
    remove_result = publisher.deleteObjectInstance(
        object_instance,
        b"gone",
        HLAinteger64Time(14),
    )
    assert attribute_result is not None and attribute_result.retractionHandleIsValid is True
    assert interaction_result is None
    assert remove_result is None

    publisher.timeAdvanceRequest(HLAinteger64Time(20))
    subscriber.timeAdvanceRequest(HLAinteger64Time(20))

    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "TimedRegionTarget-1",
        publisher_handle,
    )
    assert subscriber_callbacks.last_callback("reflectAttributeValues") == (
        object_instance,
        {attribute: b"inside"},
        b"inside-tag",
        reliable,
        publisher_handle,
        {publisher_region},
        HLAinteger64Time(10),
        OrderType.TIMESTAMP,
        OrderType.TIMESTAMP,
        attribute_result.handle,
    )
    assert subscriber_callbacks.last_callback("receiveInteraction") == (
        interaction_class,
        {parameter: b"track"},
        b"track-tag",
        reliable,
        publisher_handle,
        {publisher_region},
        HLAinteger64Time(12),
        OrderType.TIMESTAMP,
        OrderType.TIMESTAMP,
        None,
    )
    assert subscriber_callbacks.last_callback("removeObjectInstance") == (
        object_instance,
        b"gone",
        publisher_handle,
        HLAinteger64Time(14),
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-007",
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-SVC-126",
    "HLA2025-FI-SVC-127",
    "HLA2025-FI-SVC-130",
    "HLA2025-FI-SVC-132",
    "HLA2025-FI-SVC-133",
    "HLA2025-FI-SVC-134",
    "HLA2025-FI-SVC-135",
    "HLA2025-FI-SVC-136",
)
def test_2025_shim_passive_ddm_region_subscription_aliases_match_active_region_delivery(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "PassiveRegionAlias2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Passive Region Alias 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Passive region subscription alias fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RegionalTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <dimension>RoutingSpace</dimension>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>RegionalReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <dimension>RoutingSpace</dimension>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <dataType>HLAinteger32BE</dataType>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-passive-region-alias-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher_handle = publisher.joinFederationExecution("PassiveRegionPublisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("PassiveRegionSubscriber", "TestFederate", federation_name)
    subscriber.setAttributeScopeAdvisorySwitch(True)

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.RegionalTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.RegionalReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    dimension = publisher.getDimensionHandle("RoutingSpace")
    subscriber_dimension = subscriber.getDimensionHandle("RoutingSpace")
    reliable = publisher.getTransportationTypeHandle("HLAreliable")

    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.publishInteractionClass(interaction_class)

    publisher_region = publisher.createRegion({dimension})
    subscriber_region = subscriber.createRegion({subscriber_dimension})
    publisher.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(50, 60))
    publisher.commitRegionModifications({publisher_region})
    subscriber.commitRegionModifications({subscriber_region})

    object_instance = publisher.registerObjectInstance(object_class, "PassiveRegionTarget-1")
    publisher.associateRegionsForUpdates(object_instance, [({attribute}, {publisher_region})])
    subscriber.subscribeObjectClassAttributesPassivelyWithRegions(object_class, [({attribute}, {subscriber_region})])
    subscriber.subscribeInteractionClassPassivelyWithRegions(subscriber_interaction_class, {subscriber_region})

    assert subscriber_callbacks.last_callback("discoverObjectInstance") is None
    publisher.updateAttributeValues(object_instance, {attribute: b"outside"}, b"outside-attr")
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"outside"}, {publisher_region}, b"outside-interaction")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.setRangeBounds(subscriber_region, subscriber_dimension, RangeBounds(5, 15))
    subscriber.commitRegionModifications({subscriber_region})
    subscriber.subscribeObjectClassAttributesPassivelyWithRegions(object_class, [({attribute}, {subscriber_region})])

    assert subscriber_callbacks.last_callback("attributesInScope") == (object_instance, {attribute})
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        object_class,
        "PassiveRegionTarget-1",
        publisher_handle,
    )

    publisher.updateAttributeValues(object_instance, {attribute: b"inside-attr"}, b"inside-attr")
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:6] == (
        object_instance,
        {attribute: b"inside-attr"},
        b"inside-attr",
        reliable,
        publisher_handle,
        {publisher_region},
    )

    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"inside-interaction"}, {publisher_region}, b"inside-interaction")
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received == (
        interaction_class,
        {parameter: b"inside-interaction"},
        b"inside-interaction",
        reliable,
        publisher_handle,
        {publisher_region},
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )

    subscriber_callbacks.callbacks.clear()
    subscriber.unsubscribeObjectClassAttributesWithRegions(object_class, [({attribute}, {subscriber_region})])
    subscriber.unsubscribeInteractionClassWithRegions(subscriber_interaction_class, {subscriber_region})
    publisher.updateAttributeValues(object_instance, {attribute: b"after"}, b"after-attr")
    publisher.sendInteractionWithRegions(interaction_class, {parameter: b"after"}, {publisher_region}, b"after-interaction")
    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-003",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-065",
    "HLA2025-FI-SVC-066",
    "HLA2025-FI-SVC-067",
    "HLA2025-FI-SVC-068",
    "HLA2025-FI-SVC-069",
    "HLA2025-FI-SVC-070",
    "HLA2025-FI-SVC-071",
    "HLA2025-FI-SVC-072",
    "HLA2025-FI-SVC-073",
    "HLA2025-FI-SVC-074",
    "HLA2025-FI-SVC-075",
    "HLA2025-FI-SVC-077",
    "HLA2025-FI-SVC-078",
    "HLA2025-FI-SVC-079",
    "HLA2025-FI-SVC-080",
    "HLA2025-FI-SVC-081",
    "HLA2025-FI-SVC-082",
)
def test_2025_shim_object_management_and_support_callbacks(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import DeletePrivilegeNotHeld, ObjectInstanceNotKnown
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "ObjectSupport2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Object Support 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused object/support service fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>SupportTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>SupportReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-object-support-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner_handle = owner.joinFederationExecution("Owner", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.SupportTarget")
    subscriber_object_class = subscriber.getObjectClassHandle("HLAobjectRoot.SupportTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")
    subscriber_attribute = subscriber.getAttributeHandle(subscriber_object_class, "Position")
    interaction_class = owner.getInteractionClassHandle("HLAinteractionRoot.SupportReport")
    subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.SupportReport")
    best_effort = owner.getTransportationTypeHandle("HLAbestEffort")

    owner.publishObjectClassAttributes(object_class, {attribute})
    owner.publishInteractionClass(interaction_class)
    subscriber.subscribeObjectClassAttributes(subscriber_object_class, {subscriber_attribute})
    object_instance = owner.registerObjectInstance(object_class, "Support-Target-1")
    assert subscriber_callbacks.last_callback("discoverObjectInstance") == (
        object_instance,
        subscriber_object_class,
        "Support-Target-1",
        owner_handle,
    )

    subscriber.requestAttributeValueUpdate(object_instance, {subscriber_attribute}, b"instance-request")
    assert owner_callbacks.last_callback("provideAttributeValueUpdate") == (object_instance, {attribute}, b"instance-request")

    subscriber.requestAttributeValueUpdate(subscriber_object_class, {subscriber_attribute}, b"class-request")
    assert owner_callbacks.last_callback("provideAttributeValueUpdate") == (object_instance, {attribute}, b"class-request")

    owner.requestAttributeTransportationTypeChange(object_instance, {attribute}, best_effort)
    assert owner_callbacks.last_callback("confirmAttributeTransportationTypeChange") == (object_instance, {attribute}, best_effort)
    subscriber.queryAttributeTransportationType(object_instance, subscriber_attribute)
    assert subscriber_callbacks.last_callback("reportAttributeTransportationType") == (object_instance, subscriber_attribute, best_effort)

    owner.requestInteractionTransportationTypeChange(interaction_class, best_effort)
    assert owner_callbacks.last_callback("confirmInteractionTransportationTypeChange") == (interaction_class, best_effort)
    subscriber.queryInteractionTransportationType(owner_handle, subscriber_interaction_class)
    assert subscriber_callbacks.last_callback("reportInteractionTransportationType") == (
        owner_handle,
        subscriber_interaction_class,
        best_effort,
    )

    subscriber.localDeleteObjectInstance(object_instance)
    with pytest.raises(DeletePrivilegeNotHeld):
        subscriber.deleteObjectInstance(object_instance, b"not-owner")
    owner.deleteObjectInstance(object_instance, b"delete-tag")
    assert subscriber_callbacks.last_callback("removeObjectInstance") == (
        object_instance,
        b"delete-tag",
        owner_handle,
        None,
        OrderType.RECEIVE,
        OrderType.RECEIVE,
        None,
    )
    with pytest.raises(ObjectInstanceNotKnown):
        subscriber.requestAttributeValueUpdate(object_instance, {subscriber_attribute}, b"after-delete")

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution(federationName=federation_name)
    owner.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-093",
    "HLA2025-FI-SVC-100",
)
def test_2025_shim_applies_resign_time_ownership_policies(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import NoAcquisitionPending, ObjectInstanceNotKnown
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "ResignOwnership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Resign Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused resign-time ownership fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>OwnableTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-resign-ownership-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner.joinFederationExecution("Owner", "TestFederate", federation_name)
    acquirer.joinFederationExecution("Acquirer", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")
    subscriber_attribute = subscriber.getAttributeHandle(object_class, "Position")
    subscriber.subscribeObjectClassAttributes(object_class, {subscriber_attribute})

    cancelled = owner.registerObjectInstance(object_class, "Cancel-Pending")
    acquirer.attributeOwnershipAcquisition(cancelled, {attribute}, b"cancel-on-resign")
    assert owner_callbacks.last_callback("requestAttributeOwnershipRelease") == (
        cancelled,
        {attribute},
        b"cancel-on-resign",
    )
    acquirer.resignFederationExecution(ResignAction.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS)
    with pytest.raises(NoAcquisitionPending):
        owner.attributeOwnershipDivestitureIfWanted(cancelled, {attribute})

    acquirer = create_rti_ambassador(backend="shim")
    acquirer_callbacks = Recording2025FederateAmbassador()
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    acquirer_handle = acquirer.joinFederationExecution("Acquirer-2", "TestFederate", federation_name)

    transferred = owner.registerObjectInstance(object_class, "Transfer-On-Resign")
    acquirer.attributeOwnershipAcquisition(transferred, {attribute}, b"transfer-on-resign")
    owner.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        transferred,
        {attribute},
        b"transfer-on-resign",
    )
    acquirer.queryAttributeOwnership(transferred, {attribute})
    assert acquirer_callbacks.last_callback("informAttributeOwnership") == (
        transferred,
        {attribute},
        acquirer_handle,
    )

    deleter = create_rti_ambassador(backend="shim")
    deleter_callbacks = Recording2025FederateAmbassador()
    deleter.connect(deleter_callbacks, CallbackModel.HLA_EVOKED)
    deleter.joinFederationExecution("Deleter", "TestFederate", federation_name)
    delete_object_class = deleter.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    delete_attribute = deleter.getAttributeHandle(delete_object_class, "Position")
    deleter.publishObjectClassAttributes(delete_object_class, {delete_attribute})
    deleted = deleter.registerObjectInstance(delete_object_class, "Delete-On-Resign")
    assert subscriber_callbacks.last_callback("discoverObjectInstance")[0] == deleted
    assert deleter.isAttributeOwnedByFederate(deleted, delete_attribute) is True
    deleter.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    assert subscriber_callbacks.last_callback("removeObjectInstance")[0] == deleted
    with pytest.raises(ObjectInstanceNotKnown):
        subscriber.requestAttributeValueUpdate(deleted, {subscriber_attribute}, b"deleted")

    acquirer.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    subscriber.destroyFederationExecution(federationName=federation_name)
    deleter.disconnect()
    acquirer.disconnect()
    subscriber.disconnect()
    owner.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-084",
    "HLA2025-FI-SVC-085",
    "HLA2025-FI-SVC-086",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-088",
    "HLA2025-FI-SVC-089",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-091",
    "HLA2025-FI-SVC-092",
)
def test_2025_shim_implements_basic_ownership_divest_acquire_and_query_callbacks(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        AttributeAlreadyOwned,
        AttributeNotOwned,
        InvalidObjectInstanceHandle,
        ObjectInstanceNameInUse,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import ObjectInstanceHandle

    fom = tmp_path / "Ownership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused ownership fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>OwnableTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-ownership-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    acquiring_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquiring = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquiring.connect(acquiring_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner_handle = owner.joinFederationExecution(
        federateName="Owner",
        federateType="TestFederate",
        federationName=federation_name,
    )
    acquiring_handle = acquiring.joinFederationExecution(
        federateName="Acquirer",
        federateType="TestFederate",
        federationName=federation_name,
    )

    object_class = owner.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")
    object_instance = owner.registerObjectInstance(object_class, "Target-1")

    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is True
    assert acquiring.isAttributeOwnedByFederate(object_instance, attribute) is False
    with pytest.raises(ObjectInstanceNameInUse):
        owner.registerObjectInstance(object_class, "Target-1")
    with pytest.raises(InvalidObjectInstanceHandle):
        owner.isAttributeOwnedByFederate(ObjectInstanceHandle(9999), attribute)
    with pytest.raises(AttributeAlreadyOwned):
        owner.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"already-owned")

    acquiring.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"blocked")
    unavailable = acquiring_callbacks.last_callback("attributeOwnershipUnavailable")
    assert unavailable == (object_instance, {attribute}, b"blocked")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is True

    with pytest.raises(AttributeNotOwned):
        acquiring.unconditionalAttributeOwnershipDivestiture(object_instance, {attribute}, b"not-owned")

    owner.unconditionalAttributeOwnershipDivestiture(object_instance, {attribute}, b"divest")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is False

    owner.queryAttributeOwnership(object_instance, {attribute})
    assert owner_callbacks.last_callback("attributeIsNotOwned") == (object_instance, {attribute})

    acquiring.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"claim")
    acquired = acquiring_callbacks.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired == (object_instance, {attribute}, b"claim")
    assert acquiring.isAttributeOwnedByFederate(object_instance, attribute) is True

    owner.queryAttributeOwnership(object_instance, {attribute})
    assert owner_callbacks.last_callback("informAttributeOwnership") == (
        object_instance,
        {attribute},
        acquiring_handle,
    )
    acquiring.queryAttributeOwnership(object_instance, {attribute})
    assert acquiring_callbacks.last_callback("informAttributeOwnership") == (
        object_instance,
        {attribute},
        acquiring_handle,
    )
    assert owner_handle != acquiring_handle

    acquiring.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    owner.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    owner.destroyFederationExecution(federationName=federation_name)
    acquiring.disconnect()
    owner.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-089",
    "HLA2025-FI-SVC-093",
    "HLA2025-FI-SVC-094",
    "HLA2025-FI-SVC-095",
    "HLA2025-FI-SVC-096",
    "HLA2025-FI-SVC-097",
    "HLA2025-FI-SVC-098",
    "HLA2025-FI-SVC-099",
)
def test_2025_shim_negotiated_ownership_matches_python_parity_flow(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        AttributeAcquisitionWasNotRequested,
        AttributeAlreadyBeingDivested,
        NoAcquisitionPending,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "NegotiatedOwnership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Negotiated Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused negotiated ownership fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>OwnableTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-negotiated-ownership-{uuid.uuid4().hex[:8]}"
    owner_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")

    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    owner.joinFederationExecution("Owner", "TestFederate", federation_name)
    acquirer.joinFederationExecution("Acquirer", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.OwnableTarget")
    attribute = owner.getAttributeHandle(object_class, "Position")

    offered = owner.registerObjectInstance(object_class, "Negotiated-1")
    owner.negotiatedAttributeOwnershipDivestiture(offered, {attribute}, b"offer-tag")
    assert acquirer_callbacks.last_callback("requestAttributeOwnershipAssumption") == (
        offered,
        {attribute},
        b"offer-tag",
    )
    with pytest.raises(AttributeAlreadyBeingDivested):
        owner.negotiatedAttributeOwnershipDivestiture(offered, {attribute}, b"second-offer")
    assert owner.isAttributeOwnedByFederate(offered, attribute) is True

    acquirer.attributeOwnershipAcquisition(offered, {attribute}, b"acquire-tag")
    assert owner_callbacks.last_callback("requestDivestitureConfirmation") == (
        offered,
        {attribute},
        b"acquire-tag",
    )
    owner.confirmDivestiture(offered, {attribute}, b"acquire-confirmed")
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        offered,
        {attribute},
        b"acquire-confirmed",
    )
    assert acquirer.isAttributeOwnedByFederate(offered, attribute) is True

    pending = owner.registerObjectInstance(object_class, "Pending-1")
    acquirer.attributeOwnershipAcquisition(pending, {attribute}, b"request-tag")
    assert owner_callbacks.last_callback("requestAttributeOwnershipRelease") == (
        pending,
        {attribute},
        b"request-tag",
    )
    acquirer.cancelAttributeOwnershipAcquisition(pending, {attribute})
    assert acquirer_callbacks.last_callback("confirmAttributeOwnershipAcquisitionCancellation") == (
        pending,
        {attribute},
    )
    with pytest.raises(AttributeAcquisitionWasNotRequested):
        acquirer.cancelAttributeOwnershipAcquisition(pending, {attribute})

    acquirer.attributeOwnershipAcquisition(pending, {attribute}, b"retry-tag")
    divested = owner.attributeOwnershipDivestitureIfWanted(pending, {attribute})
    assert divested == {attribute}
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        pending,
        {attribute},
        b"",
    )
    assert acquirer.isAttributeOwnedByFederate(pending, attribute) is True

    no_candidate = owner.registerObjectInstance(object_class, "NoCandidate-1")
    with pytest.raises(NoAcquisitionPending):
        owner.attributeOwnershipDivestitureIfWanted(no_candidate, {attribute})

    cancellable = owner.registerObjectInstance(object_class, "Cancelable-1")
    owner.negotiatedAttributeOwnershipDivestiture(cancellable, {attribute}, b"cancel-offer")
    owner.cancelNegotiatedAttributeOwnershipDivestiture(cancellable, {attribute})
    assert owner.isAttributeOwnedByFederate(cancellable, attribute) is True
    owner.unconditionalAttributeOwnershipDivestiture(cancellable, {attribute}, b"final-divest")
    assert owner.isAttributeOwnedByFederate(cancellable, attribute) is False

    acquirer.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    owner.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    owner.destroyFederationExecution(federationName=federation_name)
    acquirer.disconnect()
    owner.disconnect()


@pytest.mark.requirements("HLA2025-NEW-007", "HLA2025-FI-001", "HLA2025-FI-005", "HLA2025-REQ-002")
def test_2025_shim_serializes_mom_service_reports_without_overclaiming_conformance() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import AttributeHandle

    federation_name = f"shim-mom-report-{uuid.uuid4().hex[:8]}"
    source_callbacks = Recording2025FederateAmbassador()
    observer_callbacks = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    rti.connect(source_callbacks, CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="BoundaryFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )
    observer.joinFederationExecution(
        federateName="MomObserver",
        federateType="ObserverFederate",
        federationName=federation_name,
    )

    assert rti.getServiceReportingSwitch() is False
    assert observer.getServiceReportingSwitch() is False
    rti.setServiceReportingSwitch(True)
    observer.setServiceReportingSwitch(True)
    assert rti.getServiceReportingSwitch() is True
    assert observer.getServiceReportingSwitch() is True

    report = rti.serializeMOMServiceReport(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches",
        arguments={"HLAserviceReporting": True, "tag": b"mom-tag", "attrs": {AttributeHandle(7)}},
        result={"status": "serialized"},
    )
    assert report["recordType"] == "MOMServiceReport"
    assert report["spec"] == "IEEE 1516.1-2025"
    assert report["serialNumber"] == 1
    assert report["federationName"] == federation_name
    assert report["federateName"] == "BoundaryFederate"
    assert report["federateHandle"] == 1
    assert report["service"] == "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    assert report["success"] is True
    assert report["exception"] == ""
    assert report["serviceReportingEnabled"] is True
    assert report["sendServiceReportsToFile"] is False
    assert report["arguments"]["HLAserviceReporting"] is True
    assert report["arguments"]["tag"] == "6d6f6d2d746167"
    assert report["arguments"]["attrs"] == [{"type": "AttributeHandle", "value": 7}]
    assert report["returned"] == {"value": {"status": "serialized"}}
    json.dumps(report, sort_keys=True)
    assert source_callbacks.last_callback("momServiceReport") == (report,)
    assert observer_callbacks.last_callback("momServiceReport") == (report,)

    failed = rti.serializeMOMServiceReport(
        "queryLogicalTime",
        success=False,
        exception="FederateNotExecutionMember",
        returned={"value": None},
    )
    assert failed["serialNumber"] == 2
    assert failed["success"] is False
    assert failed["exception"] == "FederateNotExecutionMember"
    assert rti.serviceReportRecordsSnapshot() == (report, failed)
    assert observer_callbacks.last_callback("momServiceReport") == (failed,)

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-NEW-004", "HLA2025-FI-001", "HLA2025-REQ-002")
def test_2025_shim_declares_all_bundled_mim_manager_command_leaves_as_routed() -> None:
    from hla.backends.shim.backend import (
        MOM_2025_FEDERATE_ADJUST_LEAVES,
        MOM_2025_FEDERATE_REQUEST_LEAVES,
        MOM_2025_FEDERATE_SERVICE_LEAVES,
        MOM_2025_FEDERATION_ADJUST_LEAVES,
        MOM_2025_FEDERATION_REQUEST_LEAVES,
        MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES,
    )

    mim_path = files("hla.rti1516e.resources.foms").joinpath("HLAstandardMIM.xml")
    with mim_path.open("rb") as handle:
        root = ET.parse(handle).getroot()
    namespace = root.tag.removesuffix("objectModel")

    categories = {
        "federate_adjust": set(),
        "federate_request": set(),
        "federate_service": set(),
        "federation_adjust": set(),
        "federation_request": set(),
    }

    def child_text(element: ET.Element, name: str) -> str:
        child = element.find(f"{namespace}{name}")
        return "" if child is None or child.text is None else child.text.strip()

    def walk_interaction_class(element: ET.Element, path: tuple[str, ...]) -> None:
        name = child_text(element, "name")
        if not name:
            return
        current_path = (*path, name)
        children = element.findall(f"{namespace}interactionClass")
        if children:
            for child in children:
                walk_interaction_class(child, current_path)
            return
        qualified_name = ".".join(current_path)
        leaf = current_path[-1]
        if ".HLAreport." in qualified_name:
            return
        if ".HLAfederate.HLAadjust." in qualified_name:
            categories["federate_adjust"].add(leaf)
        elif ".HLAfederate.HLArequest." in qualified_name:
            categories["federate_request"].add(leaf)
        elif ".HLAfederate.HLAservice." in qualified_name:
            categories["federate_service"].add(leaf)
        elif ".HLAfederation.HLAadjust." in qualified_name:
            categories["federation_adjust"].add(leaf)
        elif ".HLAfederation.HLArequest." in qualified_name:
            categories["federation_request"].add(leaf)

    for interaction_class in root.findall(f".//{namespace}interactions/{namespace}interactionClass"):
        walk_interaction_class(interaction_class, ())

    assert categories["federate_adjust"] == set(MOM_2025_FEDERATE_ADJUST_LEAVES)
    assert categories["federate_request"] == set(MOM_2025_FEDERATE_REQUEST_LEAVES)
    assert categories["federate_service"] == set(MOM_2025_FEDERATE_SERVICE_LEAVES)
    assert categories["federation_adjust"] == set(MOM_2025_FEDERATION_ADJUST_LEAVES)
    assert categories["federation_request"] == set(MOM_2025_FEDERATION_REQUEST_LEAVES)
    assert set().union(*categories.values()) == set(MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES)


@pytest.mark.requirements(
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-NEW-007",
    "HLA2025-REQ-002",
    "HLA2025-FI-SVC-013",
    "HLA2025-FI-SVC-014",
    "HLA2025-FI-SVC-015",
    "HLA2025-FI-SVC-016",
    "HLA2025-FI-SVC-017",
)
def test_2025_shim_routes_mom_synchronization_point_reports_through_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-sync-{uuid.uuid4().hex[:8]}"
    leader_callbacks = Recording2025FederateAmbassador()
    observer_callbacks = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    leader.connect(leader_callbacks, CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    leader_handle = leader.joinFederationExecution("SyncLeader", "TestFederate", federation_name)
    observer_handle = observer.joinFederationExecution("SyncObserver", "ObserverFederate", federation_name)

    leader.registerFederationSynchronizationPoint(
        "ReadyToRun",
        b"sync-tag",
        {leader_handle, observer_handle},
    )
    assert leader_callbacks.last_callback("synchronizationPointRegistrationSucceeded") == ("ReadyToRun",)
    assert leader_callbacks.last_callback("announceSynchronizationPoint") == ("ReadyToRun", b"sync-tag")
    assert observer_callbacks.last_callback("announceSynchronizationPoint") == ("ReadyToRun", b"sync-tag")

    leader.synchronizationPointAchieved("ReadyToRun")
    assert leader_callbacks.last_callback("federationSynchronized") is None
    observer.synchronizationPointAchieved("ReadyToRun")
    assert leader_callbacks.last_callback("federationSynchronized") == ("ReadyToRun", set())
    assert observer_callbacks.last_callback("federationSynchronized") == ("ReadyToRun", set())

    points_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints"
    )
    points_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints"
    )
    points_param = observer.getParameterHandle(points_report, "HLAsyncPoints")
    observer.subscribeInteractionClass(points_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(points_request, {}, b"mom-sync-points-request")
    points_callback = observer_callbacks.last_callback("receiveInteraction")
    assert points_callback is not None
    assert points_callback[0] == points_report
    assert points_callback[1][points_param] == b"ReadyToRun"
    assert points_callback[2] == b"MOM"

    status_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus"
    )
    status_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus"
    )
    status_label = observer.getParameterHandle(status_report, "HLAsyncPointName")
    status_list = observer.getParameterHandle(status_report, "HLAsyncPointFederates")
    observer.subscribeInteractionClass(status_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(status_request, {}, b"mom-sync-status-request")
    status_callback = observer_callbacks.last_callback("receiveInteraction")
    assert status_callback is not None
    assert status_callback[0] == status_report
    assert status_callback[1][status_label] == b"ReadyToRun"
    assert status_callback[1][status_list] == b"ReadyToRun:1:achieved,2:achieved"
    assert status_callback[2] == b"MOM"

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    leader.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    leader.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    leader.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-008", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_mim_and_fom_module_reports_through_interactions(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    def write_module(path: Path, module_name: str, class_name: str) -> Path:
        path.write_text(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>{module_name}</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-01-01</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>{module_name} for 2025 MOM routing tests.</description>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <sharing>Neither</sharing>
      <semantics>Root</semantics>
      <objectClass>
        <name>{class_name}</name>
        <sharing>PublishSubscribe</sharing>
        <semantics>{class_name}</semantics>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Conditional</updateType>
          <updateCondition>On change</updateCondition>
          <ownership>NoTransfer</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <semantics>Position</semantics>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>Neither</sharing>
      <transportation>HLAreliable</transportation>
      <order>Receive</order>
      <semantics>Root</semantics>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
            encoding="utf-8",
        )
        return path

    core_fom = write_module(tmp_path / "mom-core.xml", "MOM Core FOM", "Target")
    extension_fom = write_module(tmp_path / "mom-extension.xml", "MOM Extension FOM", "Sensor")
    federation_name = f"shim-mom-fom-{uuid.uuid4().hex[:8]}"
    observer_callbacks = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModules=(str(core_fom), str(extension_fom)),
    )
    leader_handle = rti.joinFederationExecution("MomDataLeader", "TestFederate", federation_name)
    observer.joinFederationExecution("MomDataObserver", "ObserverFederate", federation_name)

    fom_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData"
    )
    fom_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData"
    )
    request_indicator = observer.getParameterHandle(fom_request, "HLAFOMmoduleIndicator")
    report_indicator = observer.getParameterHandle(fom_report, "HLAFOMmoduleIndicator")
    report_data = observer.getParameterHandle(fom_report, "HLAFOMmoduleData")
    observer.subscribeInteractionClass(fom_report)
    observer.sendInteraction(fom_request, {request_indicator: b"1"}, b"mom-fom-module-request")
    fom_callback = observer_callbacks.last_callback("receiveInteraction")
    assert fom_callback is not None
    assert fom_callback[0] == fom_report
    assert fom_callback[1][report_indicator] == b"1"
    assert b"MOM Extension FOM" in fom_callback[1][report_data]
    assert b"<name>Sensor</name>" in fom_callback[1][report_data]
    assert fom_callback[2] == b"MOM"

    mim_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    )
    mim_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    )
    mim_data = observer.getParameterHandle(mim_report, "HLAMIMdata")
    observer.subscribeInteractionClass(mim_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(mim_request, {}, b"mom-mim-request")
    mim_callback = observer_callbacks.last_callback("receiveInteraction")
    assert mim_callback is not None
    assert mim_callback[0] == mim_report
    assert b"Standard MOM and Initialization Module" in mim_callback[1][mim_data]
    assert b"HLArequestMIMdata" in mim_callback[1][mim_data]
    assert mim_callback[2] == b"MOM"

    federate_fom_request = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData"
    )
    federate_fom_report = observer.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData"
    )
    federate_param = observer.getParameterHandle(federate_fom_request, "HLAfederate")
    federate_request_indicator = observer.getParameterHandle(federate_fom_request, "HLAFOMmoduleIndicator")
    federate_report_target = observer.getParameterHandle(federate_fom_report, "HLAfederate")
    federate_report_indicator = observer.getParameterHandle(federate_fom_report, "HLAFOMmoduleIndicator")
    federate_report_data = observer.getParameterHandle(federate_fom_report, "HLAFOMmoduleData")
    observer.subscribeInteractionClass(federate_fom_report)
    observer_callbacks.callbacks.clear()
    observer.sendInteraction(
        federate_fom_request,
        {
            federate_param: str(leader_handle.value).encode("ascii"),
            federate_request_indicator: b"0",
        },
        b"mom-federate-fom-module-request",
    )
    federate_fom_callback = observer_callbacks.last_callback("receiveInteraction")
    assert federate_fom_callback is not None
    assert federate_fom_callback[0] == federate_fom_report
    assert federate_fom_callback[1][federate_report_target] == str(leader_handle.value).encode("ascii")
    assert federate_fom_callback[1][federate_report_indicator] == b"0"
    assert b"MOM Core FOM" in federate_fom_callback[1][federate_report_data]
    assert b"<name>Target</name>" in federate_fom_callback[1][federate_report_data]
    assert federate_fom_callback[2] == b"MOM"

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-MOD-008", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_adjust_interactions_for_reporting_switches() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-adjust-{uuid.uuid4().hex[:8]}"
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomTarget", "TestFederate", federation_name)

    service_adjust = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    service_target = controller.getParameterHandle(service_adjust, "HLAfederate")
    service_state = controller.getParameterHandle(service_adjust, "HLAreportingState")
    assert target.getServiceReportingSwitch() is False
    controller.sendInteraction(
        service_adjust,
        {
            service_target: str(target_handle.value).encode("ascii"),
            service_state: b"HLAtrue",
        },
        b"mom-enable-service-reporting",
    )
    assert target.getServiceReportingSwitch() is True
    controller.sendInteraction(
        service_adjust,
        {
            service_target: str(target_handle.value).encode("ascii"),
            service_state: b"HLAfalse",
        },
        b"mom-disable-service-reporting",
    )
    assert target.getServiceReportingSwitch() is False

    exception_adjust = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetExceptionReporting"
    )
    exception_target = controller.getParameterHandle(exception_adjust, "HLAfederate")
    exception_state = controller.getParameterHandle(exception_adjust, "HLAreportingState")
    assert target.getExceptionReportingSwitch() is True
    controller.sendInteraction(
        exception_adjust,
        {
            exception_target: str(target_handle.value).encode("ascii"),
            exception_state: b"HLAfalse",
        },
        b"mom-disable-exception-reporting",
    )
    assert target.getExceptionReportingSwitch() is False
    controller.sendInteraction(
        exception_adjust,
        {
            exception_target: str(target_handle.value).encode("ascii"),
            exception_state: b"HLAtrue",
        },
        b"mom-enable-exception-reporting",
    )
    assert target.getExceptionReportingSwitch() is True

    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-MOD-008", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_set_switches_adjust_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-switches-{uuid.uuid4().hex[:8]}"
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("SwitchController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("SwitchTarget", "TestFederate", federation_name)

    federate_switches = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    )
    federate_target = controller.getParameterHandle(federate_switches, "HLAfederate")
    convey_regions = controller.getParameterHandle(federate_switches, "HLAconveyRegionDesignatorSets")
    assert target.getConveyRegionDesignatorSetsSwitch() is True
    controller.sendInteraction(
        federate_switches,
        {
            federate_target: str(target_handle.value).encode("ascii"),
            convey_regions: b"HLAfalse",
        },
        b"mom-disable-convey-region-designator-sets",
    )
    assert target.getConveyRegionDesignatorSetsSwitch() is False
    controller.sendInteraction(
        federate_switches,
        {
            federate_target: str(target_handle.value).encode("ascii"),
            convey_regions: b"HLAtrue",
        },
        b"mom-enable-convey-region-designator-sets",
    )
    assert target.getConveyRegionDesignatorSetsSwitch() is True

    federation_switches = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAadjust.HLAsetSwitches"
    )
    auto_provide = controller.getParameterHandle(federation_switches, "HLAautoProvide")
    assert controller.getAutoProvideSwitch() is True
    assert target.getAutoProvideSwitch() is True
    controller.sendInteraction(
        federation_switches,
        {auto_provide: b"HLAfalse"},
        b"mom-disable-auto-provide",
    )
    assert controller.getAutoProvideSwitch() is False
    assert target.getAutoProvideSwitch() is False
    controller.sendInteraction(
        federation_switches,
        {auto_provide: b"HLAtrue"},
        b"mom-enable-auto-provide",
    )
    assert controller.getAutoProvideSwitch() is True
    assert target.getAutoProvideSwitch() is True

    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-FR-005", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_timing_and_attribute_state_adjust_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import ObjectClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-state-adjust-{uuid.uuid4().hex[:8]}"
    controller_callbacks = Recording2025FederateAmbassador()
    owner_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")
    nonpublisher = create_rti_ambassador(backend="shim")
    controller.connect(controller_callbacks, CallbackModel.HLA_EVOKED)
    owner.connect(owner_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    nonpublisher.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("StateAdjustController", "TestFederate", federation_name)
    owner.joinFederationExecution("StateAdjustOwner", "TestFederate", federation_name)
    acquirer_handle = acquirer.joinFederationExecution("StateAdjustAcquirer", "TestFederate", federation_name)
    nonpublisher_handle = nonpublisher.joinFederationExecution("StateAdjustNonpublisher", "TestFederate", federation_name)

    object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = owner.getAttributeHandle(object_class, "Position")
    owner.publishObjectClassAttributes(object_class, {attribute})
    acquirer.publishObjectClassAttributes(object_class, {attribute})
    object_instance = owner.registerObjectInstance(object_class, "MOM-State-Adjust-Target")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is True
    assert acquirer.isAttributeOwnedByFederate(object_instance, attribute) is False

    timing = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetTiming"
    )
    controller.sendInteraction(
        timing,
        {
            controller.getParameterHandle(timing, "HLAfederate"): str(acquirer_handle.value).encode("ascii"),
            controller.getParameterHandle(timing, "HLAreportPeriod"): b"2.5",
        },
        b"mom-set-timing",
    )
    assert acquirer.momReportPeriodSecondsSnapshot() == 2.5

    modify_state = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAmodifyAttributeState"
    )

    def send_modify_state(target_handle, state: bytes) -> None:  # noqa: ANN001
        controller.sendInteraction(
            modify_state,
            {
                controller.getParameterHandle(modify_state, "HLAfederate"): str(target_handle.value).encode("ascii"),
                controller.getParameterHandle(modify_state, "HLAobjectInstance"): str(object_instance.value).encode(
                    "ascii"
                ),
                controller.getParameterHandle(modify_state, "HLAattribute"): str(attribute.value).encode("ascii"),
                controller.getParameterHandle(modify_state, "HLAattributeState"): state,
            },
            b"mom-modify-attribute-state",
        )

    owner_callbacks.callbacks.clear()
    acquirer_callbacks.callbacks.clear()
    send_modify_state(acquirer_handle, b"Owned")
    assert owner.isAttributeOwnedByFederate(object_instance, attribute) is False
    assert acquirer.isAttributeOwnedByFederate(object_instance, attribute) is True
    assert owner_callbacks.last_callback("requestDivestitureConfirmation") is None
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") is None

    send_modify_state(acquirer_handle, b"0")
    assert acquirer.isAttributeOwnedByFederate(object_instance, attribute) is False

    with pytest.raises(ObjectClassNotPublished):
        send_modify_state(nonpublisher_handle, b"1")
    report = controller_callbacks.last_callback("receiveInteraction")
    assert report is not None
    report_name = controller.getInteractionClassName(report[0])
    assert report_name == "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    assert b"ObjectClassNotPublished" in report[1][controller.getParameterHandle(report[0], "HLAexception")]
    assert nonpublisher.isAttributeOwnedByFederate(object_instance, attribute) is False

    nonpublisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    acquirer.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    owner.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    nonpublisher.disconnect()
    acquirer.disconnect()
    owner.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-004", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_reports_mom_federate_publication_subscription_and_object_information() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-fed-reports-{uuid.uuid4().hex[:8]}"
    observer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomFederateReportController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomFederateReportTarget", "TestFederate", federation_name)
    observer.joinFederationExecution("MomFederateReportObserver", "TestFederate", federation_name)

    object_class = target.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = target.getAttributeHandle(object_class, "Position")
    interaction_class = target.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    target.publishObjectClassAttributes(object_class, {attribute})
    target.publishInteractionClass(interaction_class)
    target.subscribeObjectClassAttributes(object_class, {attribute})
    target.subscribeInteractionClass(interaction_class)
    object_instance = target.registerObjectInstance(object_class, "MOM-Federate-Report-Target")

    report_names = (
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation",
    )
    for report_name in report_names:
        observer.subscribeInteractionClass(observer.getInteractionClassHandle(report_name))

    def send_request(name: str, extra: dict[str, bytes] | None = None) -> None:
        request = controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.{name}")
        values = {controller.getParameterHandle(request, "HLAfederate"): str(target_handle.value).encode("ascii")}
        if extra:
            values.update({controller.getParameterHandle(request, key): value for key, value in extra.items()})
        controller.sendInteraction(request, values, f"mom-{name}".encode("ascii"))

    def last_report(report_name: str):  # noqa: ANN202
        for callback_name, args in reversed(observer_callbacks.callbacks):
            if callback_name == "receiveInteraction" and observer.getInteractionClassName(args[0]) == report_name:
                return args
        return None

    send_request("HLArequestPublications")
    object_publication = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication"
    )
    assert object_publication is not None
    object_pub_params = object_publication[1]
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAfederate")] == str(
        target_handle.value
    ).encode("ascii")
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAnumberOfClasses")] == b"1"
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAobjectClass")] == str(
        object_class.value
    ).encode("ascii")
    assert object_pub_params[observer.getParameterHandle(object_publication[0], "HLAattributeList")] == str(
        attribute.value
    ).encode("ascii")

    interaction_publication = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication"
    )
    assert interaction_publication is not None
    assert interaction_publication[1][observer.getParameterHandle(interaction_publication[0], "HLAinteractionClassList")] == str(
        interaction_class.value
    ).encode("ascii")

    send_request("HLArequestSubscriptions")
    object_subscription = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription"
    )
    assert object_subscription is not None
    object_sub_params = object_subscription[1]
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAnumberOfClasses")] == b"1"
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAobjectClass")] == str(
        object_class.value
    ).encode("ascii")
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAactive")] == b"HLAtrue"
    assert object_sub_params[observer.getParameterHandle(object_subscription[0], "HLAattributeList")] == str(
        attribute.value
    ).encode("ascii")

    interaction_subscription = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription"
    )
    assert interaction_subscription is not None
    assert interaction_subscription[1][observer.getParameterHandle(interaction_subscription[0], "HLAinteractionClassList")] == str(
        interaction_class.value
    ).encode("ascii")

    send_request("HLArequestObjectInstanceInformation", {"HLAobjectInstance": str(object_instance.value).encode("ascii")})
    object_information = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation"
    )
    assert object_information is not None
    object_info_params = object_information[1]
    assert object_info_params[observer.getParameterHandle(object_information[0], "HLAobjectInstance")] == str(
        object_instance.value
    ).encode("ascii")
    owned_attributes = {
        int(value)
        for value in object_info_params[
            observer.getParameterHandle(object_information[0], "HLAownedInstanceAttributeList")
        ].split(b",")
        if value
    }
    assert attribute.value in owned_attributes
    assert object_info_params[observer.getParameterHandle(object_information[0], "HLAregisteredClass")] == str(
        object_class.value
    ).encode("ascii")
    assert object_info_params[observer.getParameterHandle(object_information[0], "HLAknownClass")] == str(
        object_class.value
    ).encode("ascii")

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-004", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_reports_mom_federate_activity_counts() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-activity-{uuid.uuid4().hex[:8]}"
    observer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomActivityController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomActivityTarget", "TestFederate", federation_name)
    observer_handle = observer.joinFederationExecution("MomActivityObserver", "TestFederate", federation_name)

    object_class = target.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = target.getAttributeHandle(object_class, "Position")
    interaction_class = target.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    target.publishObjectClassAttributes(object_class, {attribute})
    observer.subscribeObjectClassAttributes(object_class, {attribute})
    target.publishInteractionClass(interaction_class)
    observer.subscribeInteractionClass(interaction_class)

    object_instance = target.registerObjectInstance(object_class, "MOM-Activity-Target")
    target.updateAttributeValues(object_instance, {attribute: b"1,2,3"}, b"mom-activity-update")
    target.sendInteraction(interaction_class, {}, b"mom-activity-interaction")
    assert observer_callbacks.last_callback("reflectAttributeValues") is not None
    assert observer_callbacks.last_callback("receiveInteraction") is not None

    report_names = (
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived",
    )
    for report_name in report_names:
        observer.subscribeInteractionClass(observer.getInteractionClassHandle(report_name))

    def send_request(target_federate, name: str) -> None:  # noqa: ANN001
        request = controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.{name}")
        controller.sendInteraction(
            request,
            {controller.getParameterHandle(request, "HLAfederate"): str(target_federate.value).encode("ascii")},
            f"mom-{name}".encode("ascii"),
        )

    def last_report(report_name: str):  # noqa: ANN202
        for callback_name, args in reversed(observer_callbacks.callbacks):
            if callback_name == "receiveInteraction" and observer.getInteractionClassName(args[0]) == report_name:
                return args
        return None

    def count_payload(report, parameter_name: str) -> dict[int, int]:  # noqa: ANN001
        payload = report[1][observer.getParameterHandle(report[0], parameter_name)]
        result: dict[int, int] = {}
        for item in payload.decode("ascii").split(","):
            if not item:
                continue
            handle, count = item.split(":", 1)
            result[int(handle)] = int(count)
        return result

    send_request(target_handle, "HLArequestObjectInstancesThatCanBeDeleted")
    deletable = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted"
    )
    assert deletable is not None
    assert count_payload(deletable, "HLAobjectInstanceCounts") == {object_class.value: 1}

    send_request(target_handle, "HLArequestObjectInstancesUpdated")
    updated = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated")
    assert updated is not None
    assert count_payload(updated, "HLAobjectInstanceCounts") == {object_class.value: 1}

    send_request(observer_handle, "HLArequestObjectInstancesReflected")
    reflected = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected")
    assert reflected is not None
    assert count_payload(reflected, "HLAobjectInstanceCounts") == {object_class.value: 1}

    send_request(target_handle, "HLArequestUpdatesSent")
    updates_sent = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent")
    assert updates_sent is not None
    assert updates_sent[1][observer.getParameterHandle(updates_sent[0], "HLAtransportation")] == b"HLAreliable"
    assert count_payload(updates_sent, "HLAupdateCounts") == {object_class.value: 1}

    send_request(observer_handle, "HLArequestReflectionsReceived")
    reflections_received = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived"
    )
    assert reflections_received is not None
    assert count_payload(reflections_received, "HLAreflectCounts") == {object_class.value: 1}

    send_request(target_handle, "HLArequestInteractionsSent")
    interactions_sent = last_report("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent")
    assert interactions_sent is not None
    assert count_payload(interactions_sent, "HLAinteractionCounts") == {interaction_class.value: 1}

    send_request(observer_handle, "HLArequestInteractionsReceived")
    interactions_received = last_report(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived"
    )
    assert interactions_received is not None
    assert count_payload(interactions_received, "HLAinteractionCounts") == {interaction_class.value: 1}

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_declaration_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import InteractionClassNotPublished, ObjectClassNotPublished
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-service-{uuid.uuid4().hex[:8]}"
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer_callbacks = Recording2025FederateAmbassador()
    observer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("ServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("ServiceTarget", "TestFederate", federation_name)
    observer_handle = observer.joinFederationExecution("ServiceObserver", "TestFederate", federation_name)

    object_class = controller.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = controller.getAttributeHandle(object_class, "Position")
    interaction_class = controller.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    publish_object = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLApublishObjectClassAttributes"
    )
    subscribe_object = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsubscribeObjectClassAttributes"
    )
    unpublish_object = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunpublishObjectClassAttributes"
    )
    publish_interaction = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLApublishInteractionClass"
    )
    subscribe_interaction = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsubscribeInteractionClass"
    )
    unpublish_interaction = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAunpublishInteractionClass"
    )

    def parameter(interaction, name: str):  # noqa: ANN001
        return controller.getParameterHandle(interaction, name)

    target_payload = str(target_handle.value).encode("ascii")
    observer_payload = str(observer_handle.value).encode("ascii")
    object_payload = str(object_class.value).encode("ascii")
    attribute_payload = str(attribute.value).encode("ascii")
    interaction_payload = str(interaction_class.value).encode("ascii")

    controller.sendInteraction(
        publish_object,
        {
            parameter(publish_object, "HLAfederate"): target_payload,
            parameter(publish_object, "HLAobjectClass"): object_payload,
            parameter(publish_object, "HLAattributeList"): attribute_payload,
        },
        b"mom-publish-object",
    )
    controller.sendInteraction(
        subscribe_object,
        {
            parameter(subscribe_object, "HLAfederate"): observer_payload,
            parameter(subscribe_object, "HLAobjectClass"): object_payload,
            parameter(subscribe_object, "HLAattributeList"): attribute_payload,
            parameter(subscribe_object, "HLAactive"): b"HLAtrue",
        },
        b"mom-subscribe-object",
    )
    object_instance = target.registerObjectInstance(object_class, "MOM-Service-Target-1")
    target.updateAttributeValues(object_instance, {attribute: b"1,2,3"}, b"mom-service-update")
    assert observer_callbacks.last_callback("discoverObjectInstance") is not None
    reflect = observer_callbacks.last_callback("reflectAttributeValues")
    assert reflect is not None
    assert reflect[0] == object_instance
    assert reflect[1][attribute] == b"1,2,3"

    controller.sendInteraction(
        unpublish_object,
        {
            parameter(unpublish_object, "HLAfederate"): target_payload,
            parameter(unpublish_object, "HLAobjectClass"): object_payload,
            parameter(unpublish_object, "HLAattributeList"): attribute_payload,
        },
        b"mom-unpublish-object",
    )
    with pytest.raises(ObjectClassNotPublished):
        target.updateAttributeValues(object_instance, {attribute: b"4,5,6"}, b"mom-service-update-after-unpublish")

    controller.sendInteraction(
        publish_interaction,
        {
            parameter(publish_interaction, "HLAfederate"): target_payload,
            parameter(publish_interaction, "HLAinteractionClass"): interaction_payload,
        },
        b"mom-publish-interaction",
    )
    controller.sendInteraction(
        subscribe_interaction,
        {
            parameter(subscribe_interaction, "HLAfederate"): observer_payload,
            parameter(subscribe_interaction, "HLAinteractionClass"): interaction_payload,
            parameter(subscribe_interaction, "HLAactive"): b"HLAtrue",
        },
        b"mom-subscribe-interaction",
    )
    target.sendInteraction(interaction_class, {}, b"mom-service-interaction")
    received = observer_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[0] == interaction_class
    assert received[2] == b"mom-service-interaction"

    controller.sendInteraction(
        unpublish_interaction,
        {
            parameter(unpublish_interaction, "HLAfederate"): target_payload,
            parameter(unpublish_interaction, "HLAinteractionClass"): interaction_payload,
        },
        b"mom-unpublish-interaction",
    )
    with pytest.raises(InteractionClassNotPublished):
        target.sendInteraction(interaction_class, {}, b"mom-service-interaction-after-unpublish")

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_federation_management_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-fm-service-{uuid.uuid4().hex[:8]}"
    controller_callbacks = Recording2025FederateAmbassador()
    target_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(controller_callbacks, CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("FmServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("FmServiceTarget", "TestFederate", federation_name)

    sync_label = "MOM-SYNC"
    controller.registerFederationSynchronizationPoint(sync_label, b"mom-sync")
    sync_achieved = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAsynchronizationPointAchieved"
    )
    controller.sendInteraction(
        sync_achieved,
        {
            controller.getParameterHandle(sync_achieved, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(sync_achieved, "HLAlabel"): sync_label.encode("utf-8"),
        },
        b"mom-sync-achieved",
    )
    controller.synchronizationPointAchieved(sync_label)
    assert controller_callbacks.last_callback("federationSynchronized") == (sync_label, set())
    assert target_callbacks.last_callback("federationSynchronized") == (sync_label, set())

    controller.requestFederationSave("MOM-SAVE")
    save_begun = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateSaveBegun"
    )
    save_complete = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateSaveComplete"
    )
    controller.sendInteraction(
        save_begun,
        {controller.getParameterHandle(save_begun, "HLAfederate"): str(target_handle.value).encode("ascii")},
        b"mom-save-begun",
    )
    controller.sendInteraction(
        save_complete,
        {
            controller.getParameterHandle(save_complete, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(save_complete, "HLAsuccessIndicator"): b"HLAtrue",
        },
        b"mom-save-complete",
    )
    controller.federateSaveComplete()
    assert controller_callbacks.last_callback("federationSaved") == ()
    assert target_callbacks.last_callback("federationSaved") == ()

    controller.requestFederationRestore("MOM-SAVE")
    restore_complete = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateRestoreComplete"
    )
    controller.sendInteraction(
        restore_complete,
        {
            controller.getParameterHandle(restore_complete, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(restore_complete, "HLAsuccessIndicator"): b"HLAtrue",
        },
        b"mom-restore-complete",
    )
    controller.federateRestoreComplete()
    assert controller_callbacks.last_callback("federationRestored") == ()
    assert target_callbacks.last_callback("federationRestored") == ()

    resign = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAresignFederationExecution"
    )
    controller.sendInteraction(
        resign,
        {
            controller.getParameterHandle(resign, "HLAfederate"): str(target_handle.value).encode("ascii"),
            controller.getParameterHandle(resign, "HLAresignAction"): str(int(ResignAction.NO_ACTION)).encode("ascii"),
        },
        b"mom-resign",
    )
    assert target_callbacks.last_callback("federateResigned") is not None

    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements(
    "HLA2025-FI-001",
    "HLA2025-FI-009",
    "HLA2025-NEW-007",
    "HLA2025-REQ-002",
    "HLA2025-FI-SVC-101",
    "HLA2025-FI-SVC-102",
    "HLA2025-FI-SVC-103",
    "HLA2025-FI-SVC-104",
    "HLA2025-FI-SVC-105",
    "HLA2025-FI-SVC-106",
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-109",
    "HLA2025-FI-SVC-110",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-112",
    "HLA2025-FI-SVC-113",
    "HLA2025-FI-SVC-114",
    "HLA2025-FI-SVC-115",
    "HLA2025-FI-SVC-119",
)
def test_2025_shim_routes_mom_time_management_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import TimeRegulationIsNotEnabled
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-time-service-{uuid.uuid4().hex[:8]}"
    target_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("TimeServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("TimeServiceTarget", "TestFederate", federation_name)

    def mom_service(name: str):  # noqa: ANN202
        return controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.{name}")

    def send_service(name: str, parameters: dict[str, bytes]) -> None:
        interaction = mom_service(name)
        payload = {controller.getParameterHandle(interaction, "HLAfederate"): str(target_handle.value).encode("ascii")}
        payload.update({controller.getParameterHandle(interaction, key): value for key, value in parameters.items()})
        controller.sendInteraction(interaction, payload, f"mom-{name}".encode("ascii"))

    send_service("HLAenableTimeRegulation", {"HLAlookahead": b"2"})
    assert target.queryLookahead() == target.getTimeFactory().makeInterval(2)
    assert target_callbacks.last_callback("timeRegulationEnabled") == (target.getTimeFactory().makeInitial(),)

    send_service("HLAenableTimeConstrained", {})
    assert target_callbacks.last_callback("timeConstrainedEnabled") == (target.getTimeFactory().makeInitial(),)

    send_service("HLAtimeAdvanceRequest", {"HLAtimeStamp": b"10"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(10)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(10),)

    send_service("HLAmodifyLookahead", {"HLAlookahead": b"3"})
    assert target.queryLookahead() == target.getTimeFactory().makeInterval(3)

    send_service("HLAflushQueueRequest", {"HLAtimeStamp": b"12"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(12)
    assert target_callbacks.last_callback("flushQueueGrant") == (
        target.getTimeFactory().makeTime(12),
        target.getTimeFactory().makeTime(12),
    )

    send_service("HLAtimeAdvanceRequestAvailable", {"HLAtimeStamp": b"14"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(14)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(14),)

    send_service("HLAnextMessageRequest", {"HLAtimeStamp": b"16"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(16)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(16),)

    send_service("HLAnextMessageRequestAvailable", {"HLAtimeStamp": b"18"})
    assert target.queryLogicalTime() == target.getTimeFactory().makeTime(18)
    assert target_callbacks.last_callback("timeAdvanceGrant") == (target.getTimeFactory().makeTime(18),)

    send_service("HLAenableAsynchronousDelivery", {})
    send_service("HLAdisableAsynchronousDelivery", {})
    assert any(call[0] == "enableAsynchronousDelivery" for call in target.calls)
    assert any(call[0] == "disableAsynchronousDelivery" for call in target.calls)

    send_service("HLAdisableTimeConstrained", {})
    assert any(call[0] == "disableTimeConstrained" for call in target.calls)

    send_service("HLAdisableTimeRegulation", {})
    with pytest.raises(TimeRegulationIsNotEnabled):
        target.queryLookahead()

    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-FR-005", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_routes_mom_object_and_ownership_service_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import ObjectInstanceNotKnown
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-object-service-{uuid.uuid4().hex[:8]}"
    target_callbacks = Recording2025FederateAmbassador()
    observer_callbacks = Recording2025FederateAmbassador()
    acquirer_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")
    controller.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    observer.connect(observer_callbacks, CallbackModel.HLA_EVOKED)
    acquirer.connect(acquirer_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("ObjectServiceController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("ObjectServiceTarget", "TestFederate", federation_name)
    observer.joinFederationExecution("ObjectServiceObserver", "TestFederate", federation_name)
    acquirer.joinFederationExecution("ObjectServiceAcquirer", "TestFederate", federation_name)

    object_class = target.getObjectClassHandle("HLAobjectRoot.Target")
    attribute = target.getAttributeHandle(object_class, "Position")
    interaction_class = target.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    target.publishObjectClassAttributes(object_class, {attribute})
    target.publishInteractionClass(interaction_class)
    observer.subscribeObjectClassAttributes(object_class, {attribute})
    object_instance = target.registerObjectInstance(object_class, "MOM-Object-Service-Target")

    def mom_service(name: str):  # noqa: ANN202
        return controller.getInteractionClassHandle(f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.{name}")

    def send_service(name: str, parameters: dict[str, bytes]) -> None:
        interaction = mom_service(name)
        payload = {controller.getParameterHandle(interaction, "HLAfederate"): str(target_handle.value).encode("ascii")}
        payload.update({controller.getParameterHandle(interaction, key): value for key, value in parameters.items()})
        controller.sendInteraction(interaction, payload, f"mom-{name}".encode("ascii"))

    send_service(
        "HLArequestAttributeTransportationTypeChange",
        {
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAattributeList": str(attribute.value).encode("ascii"),
            "HLAtransportation": b"HLAbestEffort",
        },
    )
    assert target_callbacks.last_callback("confirmAttributeTransportationTypeChange") == (
        object_instance,
        {attribute},
        target.getTransportationTypeHandle("HLAbestEffort"),
    )

    send_service(
        "HLArequestInteractionTransportationTypeChange",
        {
            "HLAinteractionClass": str(interaction_class.value).encode("ascii"),
            "HLAtransportation": b"HLAbestEffort",
        },
    )
    assert target_callbacks.last_callback("confirmInteractionTransportationTypeChange") == (
        interaction_class,
        target.getTransportationTypeHandle("HLAbestEffort"),
    )

    send_service(
        "HLAchangeAttributeOrderType",
        {
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAattributeList": str(attribute.value).encode("ascii"),
            "HLAsendOrder": b"TimeStamp",
        },
    )
    observer_callbacks.callbacks.clear()
    target.updateAttributeValues(object_instance, {attribute: b"ordered"}, b"mom-order-update")
    ordered_reflection = observer_callbacks.last_callback("reflectAttributeValues")
    assert ordered_reflection is not None
    assert ordered_reflection[7:9] == (OrderType.TIMESTAMP, OrderType.TIMESTAMP)

    observer.subscribeInteractionClass(interaction_class)
    send_service(
        "HLAchangeInteractionOrderType",
        {
            "HLAinteractionClass": str(interaction_class.value).encode("ascii"),
            "HLAsendOrder": b"1",
        },
    )
    observer_callbacks.callbacks.clear()
    target.sendInteraction(interaction_class, {}, b"mom-order-interaction")
    ordered_interaction = observer_callbacks.last_callback("receiveInteraction")
    assert ordered_interaction is not None
    assert ordered_interaction[7:9] == (OrderType.TIMESTAMP, OrderType.TIMESTAMP)

    assert target.isAttributeOwnedByFederate(object_instance, attribute) is True
    send_service(
        "HLAunconditionalAttributeOwnershipDivestiture",
        {
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAattributeList": str(attribute.value).encode("ascii"),
        },
    )
    assert target.isAttributeOwnedByFederate(object_instance, attribute) is False
    acquirer.attributeOwnershipAcquisitionIfAvailable(object_instance, {attribute}, b"after-mom-divest")
    assert acquirer_callbacks.last_callback("attributeOwnershipAcquisitionNotification") == (
        object_instance,
        {attribute},
        b"after-mom-divest",
    )

    object_instance_to_delete = target.registerObjectInstance(object_class, "MOM-Object-Service-Delete")
    send_service(
        "HLAdeleteObjectInstance",
        {
            "HLAobjectInstance": str(object_instance_to_delete.value).encode("ascii"),
            "HLAtag": b"mom-delete-object",
        },
    )
    assert observer_callbacks.last_callback("removeObjectInstance") is not None
    assert observer_callbacks.last_callback("removeObjectInstance")[0] == object_instance_to_delete
    with pytest.raises(ObjectInstanceNotKnown):
        target.deleteObjectInstance(object_instance_to_delete, b"already-deleted")

    object_instance_to_forget = target.registerObjectInstance(object_class, "MOM-Object-Service-Local")
    send_service(
        "HLAlocalDeleteObjectInstance",
        {"HLAobjectInstance": str(object_instance_to_forget.value).encode("ascii")},
    )
    assert target.isAttributeOwnedByFederate(object_instance_to_forget, attribute) is True

    acquirer.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    acquirer.disconnect()
    observer.disconnect()
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-001", "HLA2025-NEW-007", "HLA2025-REQ-002")
def test_2025_shim_reports_mom_service_failures_as_mom_exception_interactions() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import RTIinternalError
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-mom-exception-{uuid.uuid4().hex[:8]}"
    controller_callbacks = Recording2025FederateAmbassador()
    target_callbacks = Recording2025FederateAmbassador()
    controller = create_rti_ambassador(backend="shim")
    target = create_rti_ambassador(backend="shim")
    controller.connect(controller_callbacks, CallbackModel.HLA_EVOKED)
    target.connect(target_callbacks, CallbackModel.HLA_EVOKED)
    controller.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    controller.joinFederationExecution("MomExceptionController", "TestFederate", federation_name)
    target_handle = target.joinFederationExecution("MomExceptionTarget", "TestFederate", federation_name)

    service = controller.getInteractionClassHandle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance"
    )
    with pytest.raises(RTIinternalError, match="HLAobjectInstance"):
        controller.sendInteraction(
            service,
            {controller.getParameterHandle(service, "HLAfederate"): str(target_handle.value).encode("ascii")},
            b"mom-missing-object",
        )

    report = controller_callbacks.last_callback("receiveInteraction")
    assert report is not None
    report_class, parameter_values = report[0], report[1]
    report_name = controller.getInteractionClassName(report_class)
    assert report_name == "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    service_param = controller.getParameterHandle(report_class, "HLAservice")
    exception_param = controller.getParameterHandle(report_class, "HLAexception")
    parameter_error_param = controller.getParameterHandle(report_class, "HLAparameterError")
    assert parameter_values[service_param] == b"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance"
    assert b"Missing MOM parameter HLAobjectInstance" in parameter_values[exception_param]
    assert parameter_values[parameter_error_param] == b"HLAfalse"
    assert target_callbacks.last_callback("receiveInteraction")[0] == report_class

    target.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    controller.resignFederationExecution(ResignAction.NO_ACTION)
    controller.destroyFederationExecution(federationName=federation_name)
    target.disconnect()
    controller.disconnect()


@pytest.mark.requirements("HLA2025-FI-005", "HLA2025-FI-SVC-005", "HLA2025-FI-SVC-006", "HLA2025-FI-SVC-007")
def test_2025_shim_rejects_duplicate_federation_and_federate_names() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateAlreadyExecutionMember,
        FederateNameAlreadyInUse,
        FederationExecutionAlreadyExists,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-join-{uuid.uuid4().hex[:8]}"
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")
    late = create_rti_ambassador(backend="shim")

    for rti in (leader, wing, late):
        rti.connect(object(), CallbackModel.HLA_EVOKED)

    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    with pytest.raises(FederationExecutionAlreadyExists):
        leader.createFederationExecution(federationName=federation_name)

    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )
    wing.joinFederationExecution(
        federateName="Wing",
        federateType="TestFederate",
        federationName=federation_name,
    )

    with pytest.raises(FederateNameAlreadyInUse):
        late.joinFederationExecution(
            federateName="Leader",
            federateType="TestFederate",
            federationName=federation_name,
        )
    with pytest.raises(FederateAlreadyExecutionMember):
        leader.joinFederationExecution(
            federateName="Leader-Again",
            federateType="TestFederate",
            federationName=federation_name,
        )

    leader.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    late.disconnect()
    wing.disconnect()
    leader.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-003",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-011",
    "HLA2025-FI-SVC-012",
)
def test_2025_shim_reports_federate_resigned_callback_with_reason_context() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-resign-{uuid.uuid4().hex[:8]}"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")

    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="ResigningFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    rti.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)

    resigned = federate.last_callback("federateResigned")
    assert resigned is not None
    reason = resigned[0]
    assert "federateName=ResigningFederate" in reason
    assert f"federationName={federation_name}" in reason
    assert "resignAction=UNCONDITIONALLY_DIVEST_ATTRIBUTES" in reason

    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-005",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-165",
    "HLA2025-FI-SVC-166",
    "HLA2025-FI-SVC-167",
    "HLA2025-FI-SVC-168",
    "HLA2025-FI-SVC-169",
)
def test_2025_shim_normalizes_typed_handles_and_rejects_wrong_handle_family() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction, ServiceGroup
    from hla.rti1516_2025.exceptions import (
        InvalidFederateHandle,
        InvalidInteractionClassHandle,
        InvalidObjectClassHandle,
        InvalidObjectInstanceHandle,
        InvalidServiceGroup,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import (
        FederateHandle,
        InteractionClassHandle,
        ObjectClassHandle,
        ObjectInstanceHandle,
    )

    federation_name = f"shim-normalize-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")

    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    federate_handle = rti.joinFederationExecution(
        federateName="Normalizer",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert isinstance(federate_handle, FederateHandle)
    assert rti.normalizeFederateHandle(federate_handle) == federate_handle.value
    assert rti.normalizeServiceGroup(ServiceGroup.SUPPORT_SERVICES) == int(ServiceGroup.SUPPORT_SERVICES)
    assert rti.normalizeObjectClassHandle(ObjectClassHandle(11)) == 11
    assert rti.normalizeInteractionClassHandle(InteractionClassHandle(12)) == 12
    assert rti.normalizeObjectInstanceHandle(ObjectInstanceHandle(13)) == 13

    with pytest.raises(InvalidFederateHandle):
        rti.normalizeFederateHandle(ObjectClassHandle(1))
    with pytest.raises(InvalidObjectClassHandle):
        rti.normalizeObjectClassHandle(FederateHandle(1))
    with pytest.raises(InvalidInteractionClassHandle):
        rti.normalizeInteractionClassHandle(ObjectInstanceHandle(1))
    with pytest.raises(InvalidObjectInstanceHandle):
        rti.normalizeObjectInstanceHandle(InteractionClassHandle(1))
    with pytest.raises(InvalidServiceGroup):
        rti.normalizeServiceGroup("not-a-service-group")

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-MOD-008",
    "HLA2025-RET-001",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-170",
    "HLA2025-FI-SVC-171",
    "HLA2025-FI-SVC-172",
    "HLA2025-FI-SVC-173",
    "HLA2025-FI-SVC-174",
    "HLA2025-FI-SVC-175",
    "HLA2025-FI-SVC-176",
    "HLA2025-FI-SVC-177",
    "HLA2025-FI-SVC-178",
    "HLA2025-FI-SVC-179",
    "HLA2025-FI-SVC-180",
    "HLA2025-FI-SVC-181",
    "HLA2025-FI-SVC-182",
    "HLA2025-FI-SVC-183",
    "HLA2025-FI-SVC-184",
    "HLA2025-FI-SVC-185",
    "HLA2025-FI-SVC-186",
    "HLA2025-FI-SVC-187",
    "HLA2025-FI-SVC-188",
    "HLA2025-FI-SVC-189",
    "HLA2025-FI-SVC-190",
    "HLA2025-FI-SVC-191",
    "HLA2025-FI-SVC-192",
)
def test_2025_shim_supports_explicit_switch_inquiry_and_control_model() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import RTIinternalError
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-switch-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="SwitchFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert rti.getObjectClassRelevanceAdvisorySwitch() is False
    assert rti.getAttributeRelevanceAdvisorySwitch() is False
    assert rti.getAttributeScopeAdvisorySwitch() is False
    assert rti.getInteractionRelevanceAdvisorySwitch() is False
    assert rti.getConveyRegionDesignatorSetsSwitch() is True
    assert rti.getServiceReportingSwitch() is False
    assert rti.getExceptionReportingSwitch() is True
    assert rti.getSendServiceReportsToFileSwitch() is False
    assert rti.getAutoProvideSwitch() is True
    assert rti.getDelaySubscriptionEvaluationSwitch() is False
    assert rti.getAdvisoriesUseKnownClassSwitch() is True
    assert rti.getAllowRelaxedDDMSwitch() is False
    assert rti.getNonRegulatedGrantSwitch() is False
    assert rti.getAutomaticResignDirective() is ResignAction.NO_ACTION

    rti.setObjectClassRelevanceAdvisorySwitch(True)
    rti.setAttributeRelevanceAdvisorySwitch(True)
    rti.setAttributeScopeAdvisorySwitch(True)
    rti.setInteractionRelevanceAdvisorySwitch(True)
    rti.setConveyRegionDesignatorSetsSwitch(False)
    rti.setAutomaticResignDirective(ResignAction.DELETE_OBJECTS)
    rti.setServiceReportingSwitch(True)
    rti.setExceptionReportingSwitch(False)
    rti.setSendServiceReportsToFileSwitch(True)

    assert rti.getObjectClassRelevanceAdvisorySwitch() is True
    assert rti.getAttributeRelevanceAdvisorySwitch() is True
    assert rti.getAttributeScopeAdvisorySwitch() is True
    assert rti.getInteractionRelevanceAdvisorySwitch() is True
    assert rti.getConveyRegionDesignatorSetsSwitch() is False
    assert rti.getAutomaticResignDirective() is ResignAction.DELETE_OBJECTS
    assert rti.getServiceReportingSwitch() is True
    assert rti.getExceptionReportingSwitch() is False
    assert rti.getSendServiceReportsToFileSwitch() is True

    with pytest.raises(RTIinternalError, match="requires a bool"):
        rti.setServiceReportingSwitch("yes")
    with pytest.raises(RTIinternalError, match="requires a ResignAction"):
        rti.setAutomaticResignDirective("delete")
    with pytest.raises(RTIinternalError, match="does not implement"):
        rti.enableObjectClassRelevanceAdvisorySwitch()

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-NEW-002",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-SVC-004",
    "HLA2025-FI-SVC-008",
    "HLA2025-FI-SVC-009",
    "HLA2025-FI-SVC-010",
)
def test_2025_shim_reports_federation_executions_and_members() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-report-{uuid.uuid4().hex[:8]}"
    leader_fed = Recording2025FederateAmbassador()
    wing_fed = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")

    leader.connect(leader_fed, CallbackModel.HLA_EVOKED)
    wing.connect(wing_fed, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
        logicalTimeImplementationName="HLAinteger64Time",
    )

    leader.listFederationExecutions()
    execution_report = leader_fed.last_callback("reportFederationExecutions")
    assert execution_report is not None
    executions = execution_report[0]
    assert any(row.federationExecutionName == federation_name and row.logicalTimeImplementationName == "HLAinteger64Time" for row in executions)

    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )
    wing.joinFederationExecution(
        federateName="Wing",
        federateType="Observer",
        federationName=federation_name,
    )

    leader.listFederationExecutionMembers(federation_name)
    members_report = leader_fed.last_callback("reportFederationExecutionMembers")
    assert members_report is not None
    assert members_report[0] == federation_name
    assert {(row.federateName, row.federateType) for row in members_report[1]} == {
        ("Leader", "TestFederate"),
        ("Wing", "Observer"),
    }

    leader.listFederationExecutionMembers(f"{federation_name}-missing")
    missing_report = leader_fed.last_callback("reportFederationExecutionDoesNotExist")
    assert missing_report == (f"{federation_name}-missing",)

    leader.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    wing.disconnect()
    leader.disconnect()


@pytest.mark.requirements("HLA2025-MOD-001", "HLA2025-MOD-009", "HLA2025-FI-005", "HLA2025-FI-006")
def test_2025_shim_validates_callback_model_and_credentials_at_connect() -> None:
    from hla.rti1516_2025.auth import HLAplainTextPassword
    from hla.rti1516_2025.datatypes import Credentials
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import InvalidCredentials, UnsupportedCallbackModel
    from hla.rti1516_2025.factory import create_rti_ambassador

    rti = create_rti_ambassador(backend="shim")
    with pytest.raises(UnsupportedCallbackModel):
        rti.connect(object(), 99)

    with pytest.raises(InvalidCredentials, match="cannot be empty"):
        rti.connect(object(), CallbackModel.HLA_EVOKED, credentials=HLAplainTextPassword(""))

    with pytest.raises(InvalidCredentials, match="rejected"):
        rti.connect(object(), CallbackModel.HLA_EVOKED, credentials=HLAplainTextPassword("bad"))

    rti.connect(object(), CallbackModel.HLA_IMMEDIATE, credentials=Credentials("Proto2025Bearer", b"token"))
    assert rti.connected is True
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-FI-009")
def test_2025_shim_requires_valid_fom_modules_and_default_logical_time() -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import CouldNotCreateLogicalTimeFactory, InvalidFOM
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-fom-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(InvalidFOM, match="At least one FOM module"):
        rti.createFederationExecution(federationName=f"{federation_name}-missing-fom")

    with pytest.raises(CouldNotCreateLogicalTimeFactory, match="NoSuchTimeFactory"):
        rti.createFederationExecution(
            federationName=f"{federation_name}-bad-time",
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="NoSuchTimeFactory",
        )

    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    reporter = Recording2025FederateAmbassador()
    observer = create_rti_ambassador(backend="shim")
    observer.connect(reporter, CallbackModel.HLA_EVOKED)
    observer.listFederationExecutions()

    execution_report = reporter.last_callback("reportFederationExecutions")
    assert execution_report is not None
    assert any(row.federationExecutionName == federation_name and row.logicalTimeImplementationName == "HLAinteger64Time" for row in execution_report[0])

    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-MOD-003", "HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-OMT-007")
def test_2025_shim_rejects_invalid_join_fom_modules_and_destroy_while_joined(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import DesignatorIsHLAstandardMIM, ErrorReadingFOM, FederatesCurrentlyJoined
    from hla.rti1516_2025.factory import create_rti_ambassador

    broken_fom = tmp_path / "BrokenProto2025.xml"
    broken_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Broken Proto2025</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>BrokenEntity</name>
        <attribute><name>BadField</name><dataType>DoesNotExist</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-join-fom-{uuid.uuid4().hex[:8]}"
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")
    leader.connect(object(), CallbackModel.HLA_EVOKED)
    wing.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(DesignatorIsHLAstandardMIM):
        leader.createFederationExecutionWithMIM(
            federationName=f"{federation_name}-bad-mim",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule="HLAstandardMIM",
        )

    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )

    with pytest.raises(ErrorReadingFOM):
        wing.joinFederationExecution(
            federateName="Wing",
            federateType="TestFederate",
            federationName=federation_name,
            additionalFomModules=[broken_fom],
        )

    with pytest.raises(FederatesCurrentlyJoined):
        leader.destroyFederationExecution(federationName=federation_name)

    leader.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    leader.destroyFederationExecution(federationName=federation_name)
    leader.disconnect()
    wing.disconnect()


@pytest.mark.requirements("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007")
def test_2025_shim_distinguishes_fom_mim_open_read_invalid_and_merge_errors(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import (
        CouldNotOpenFOM,
        CouldNotOpenMIM,
        ErrorReadingFOM,
        ErrorReadingMIM,
        InconsistentFOM,
        InvalidFOM,
        InvalidMIM,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    def write_module(path: Path, name: str, representation: str) -> Path:
        path.write_text(
            f"""<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>SharedType</name><representation>{representation}</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
""",
            encoding="utf-8",
        )
        return path

    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(CouldNotOpenFOM):
        rti.createFederationExecution(
            federationName=f"missing-fom-{uuid.uuid4().hex[:8]}",
            fomModule=tmp_path / "missing-fom.xml",
        )
    with pytest.raises(CouldNotOpenMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"missing-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=tmp_path / "missing-mim.xml",
        )

    bad_fom = tmp_path / "bad-fom.xml"
    bad_fom.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingFOM):
        rti.createFederationExecution(
            federationName=f"bad-fom-{uuid.uuid4().hex[:8]}",
            fomModule=bad_fom,
        )

    bad_mim = tmp_path / "bad-mim.xml"
    bad_mim.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"bad-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=bad_mim,
        )

    invalid_name_fom = tmp_path / "invalid-name-fom.xml"
    invalid_name_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Invalid Name FOM</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass><name>hlaReservedUserClass</name></objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(InvalidFOM, match="reserved"):
        rti.createFederationExecution(
            federationName=f"invalid-fom-{uuid.uuid4().hex[:8]}",
            fomModule=invalid_name_fom,
        )

    with pytest.raises(InvalidMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"invalid-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=None,
        )

    conflict_a = write_module(tmp_path / "conflict-a.xml", "Conflict A", "HLAinteger32BE")
    conflict_b = write_module(tmp_path / "conflict-b.xml", "Conflict B", "HLAinteger64BE")
    with pytest.raises(InconsistentFOM, match="Conflicting simple datatype definition"):
        rti.createFederationExecution(
            federationName=f"conflicting-fom-{uuid.uuid4().hex[:8]}",
            fomModules=[conflict_a, conflict_b],
        )

    rti.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-010",
    "HLA2025-FI-005",
    "HLA2025-FI-009",
    "HLA2025-MOD-006",
    "HLA2025-FI-SVC-121",
    "HLA2025-FI-SVC-122",
)
def test_2025_shim_queues_timestamped_messages_and_supports_retraction(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import MessageCanNoLongerBeRetracted
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    fom = tmp_path / "QueuedTso2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Queued TSO 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused queued TSO fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>TimedTarget</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>TimeStamp</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TimedReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>TimeStamp</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-tso-queue-{uuid.uuid4().hex[:8]}"
    publisher_callbacks = Recording2025FederateAmbassador()
    subscriber_callbacks = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    publisher.connect(publisher_callbacks, CallbackModel.HLA_EVOKED)
    subscriber.connect(subscriber_callbacks, CallbackModel.HLA_EVOKED)
    publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
    publisher.joinFederationExecution("Publisher", "TestFederate", federation_name)
    subscriber.joinFederationExecution("Subscriber", "TestFederate", federation_name)
    publisher.enableTimeRegulation(HLAinteger64Interval(1))
    subscriber.enableTimeConstrained()

    object_class = publisher.getObjectClassHandle("HLAobjectRoot.TimedTarget")
    attribute = publisher.getAttributeHandle(object_class, "Position")
    interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TimedReport")
    parameter = publisher.getParameterHandle(interaction_class, "TrackId")
    publisher.publishObjectClassAttributes(object_class, {attribute})
    publisher.publishInteractionClass(interaction_class)
    subscriber.subscribeObjectClassAttributes(object_class, {attribute})
    subscriber.subscribeInteractionClass(interaction_class)
    object_instance = publisher.registerObjectInstance(object_class, "Timed-Target-1")

    late = publisher.sendInteraction(interaction_class, {parameter: b"late"}, b"late", HLAinteger64Time(20))
    early = publisher.updateAttributeValues(object_instance, {attribute: b"early"}, b"early", HLAinteger64Time(10))
    retracted = publisher.sendInteraction(interaction_class, {parameter: b"retracted"}, b"retracted", HLAinteger64Time(15))
    assert late.retractionHandleIsValid is True
    assert early.retractionHandleIsValid is True
    assert retracted.retractionHandleIsValid is True
    publisher.retract(retracted.handle)
    publisher.timeAdvanceRequest(HLAinteger64Time(25))

    assert subscriber_callbacks.last_callback("reflectAttributeValues") is None
    assert subscriber_callbacks.last_callback("receiveInteraction") is None
    subscriber.timeAdvanceRequest(HLAinteger64Time(12))
    reflection = subscriber_callbacks.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection[:3] == (object_instance, {attribute: b"early"}, b"early")
    assert reflection[6:] == (HLAinteger64Time(10), OrderType.TIMESTAMP, OrderType.TIMESTAMP, early.handle)
    assert subscriber_callbacks.last_callback("receiveInteraction") is None

    subscriber.timeAdvanceRequest(HLAinteger64Time(25))
    received = subscriber_callbacks.last_callback("receiveInteraction")
    assert received is not None
    assert received[:3] == (interaction_class, {parameter: b"late"}, b"late")
    assert received[6:] == (HLAinteger64Time(20), OrderType.TIMESTAMP, OrderType.TIMESTAMP, late.handle)
    publisher.retract(late.handle)
    request_retraction = subscriber_callbacks.last_callback("requestRetraction")
    assert request_retraction == (late.handle,)
    with pytest.raises(MessageCanNoLongerBeRetracted):
        publisher.retract(late.handle)

    subscriber.resignFederationExecution(ResignAction.NO_ACTION)
    publisher.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
    publisher.destroyFederationExecution(federationName=federation_name)
    publisher.disconnect()
    subscriber.disconnect()


@pytest.mark.requirements(
    "HLA2025-FR-010",
    "HLA2025-FI-005",
    "HLA2025-FI-009",
    "HLA2025-MOD-006",
    "HLA2025-FI-SVC-101",
    "HLA2025-FI-SVC-102",
    "HLA2025-FI-SVC-104",
    "HLA2025-FI-SVC-105",
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-112",
    "HLA2025-FI-SVC-113",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
    "HLA2025-FI-SVC-118",
    "HLA2025-FI-SVC-119",
    "HLA2025-FI-SVC-120",
)
def test_2025_shim_uses_selected_logical_time_factory_for_queries_and_grants() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import LogicalTimeAlreadyPassed, TimeRegulationIsNotEnabled
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAfloat64Interval, HLAfloat64Time

    federation_name = f"shim-time-{uuid.uuid4().hex[:8]}"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
        logicalTimeImplementationName="HLAfloat64Time",
    )
    rti.joinFederationExecution(
        federateName="Clock",
        federateType="TestFederate",
        federationName=federation_name,
    )

    time_factory = rti.getTimeFactory()
    assert time_factory.getName() == "HLAfloat64Time"
    assert rti.queryLogicalTime() == HLAfloat64Time(0.0)
    assert rti.queryGALT().timeIsValid is True
    assert rti.queryGALT().time == HLAfloat64Time(0.0)
    assert rti.queryLITS().time == HLAfloat64Time(0.0)

    with pytest.raises(TimeRegulationIsNotEnabled):
        rti.queryLookahead()

    rti.enableTimeRegulation(HLAfloat64Interval(0.5))
    rti.enableTimeConstrained()
    assert rti.queryLookahead() == HLAfloat64Interval(0.5)
    rti.modifyLookahead(HLAfloat64Interval(0.25))
    assert rti.queryLookahead() == HLAfloat64Interval(0.25)

    rti.timeAdvanceRequest(HLAfloat64Time(12.5))
    assert rti.queryLogicalTime() == HLAfloat64Time(12.5)
    assert federate.last_callback("timeRegulationEnabled") == (HLAfloat64Time(0.0),)
    assert federate.last_callback("timeConstrainedEnabled") == (HLAfloat64Time(0.0),)
    assert federate.last_callback("timeAdvanceGrant") == (HLAfloat64Time(12.5),)

    with pytest.raises(LogicalTimeAlreadyPassed):
        rti.flushQueueRequest(HLAfloat64Time(12.0))

    rti.flushQueueRequest(HLAfloat64Time(20.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(20.0)
    assert federate.last_callback("flushQueueGrant") == (HLAfloat64Time(20.0), HLAfloat64Time(20.0))
    assert rti.queryGALT().time == HLAfloat64Time(20.0)
    assert rti.queryLITS().time == HLAfloat64Time(20.0)

    rti.timeAdvanceRequestAvailable(HLAfloat64Time(21.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(21.0)
    assert federate.last_callback("timeAdvanceGrant") == (HLAfloat64Time(21.0),)
    rti.nextMessageRequest(HLAfloat64Time(22.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(22.0)
    rti.nextMessageRequestAvailable(HLAfloat64Time(23.0))
    assert rti.queryLogicalTime() == HLAfloat64Time(23.0)

    rti.enableAsynchronousDelivery()
    rti.disableAsynchronousDelivery()
    assert any(call[0] == "enableAsynchronousDelivery" for call in rti.calls)
    assert any(call[0] == "disableAsynchronousDelivery" for call in rti.calls)

    rti.disableTimeConstrained()
    assert any(call[0] == "disableTimeConstrained" for call in rti.calls)
    rti.disableTimeRegulation()
    with pytest.raises(TimeRegulationIsNotEnabled):
        rti.queryLookahead()

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_blocks_window_closure_until_future_inputs_are_excluded() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import InvalidLogicalTime
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-future-exclusion-{uuid.uuid4().hex[:8]}"
    slow_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    slow = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")

    try:
        slow.connect(slow_federate, CallbackModel.HLA_EVOKED)
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        slow.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        slow.joinFederationExecution(
            federateName="SlowRegulator",
            federateType="TimeWindowFederate",
            federationName=federation_name,
        )
        radar.joinFederationExecution(
            federateName="Radar",
            federateType="TimeWindowFederate",
            federationName=federation_name,
        )

        interaction_class = slow.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = slow.getParameterHandle(interaction_class, "TrackId")
        slow.publishInteractionClass(interaction_class)
        radar.subscribeInteractionClass(interaction_class)

        slow.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert slow_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        slow.timeAdvanceRequestAvailable(HLAinteger64Time(100))
        assert slow_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(100),)

        blocked_galt = radar.queryGALT()
        blocked_lits = radar.queryLITS()
        assert blocked_galt.timeIsValid is True
        assert blocked_lits.timeIsValid is True
        assert blocked_galt.time == HLAinteger64Time(101)
        assert blocked_lits.time == HLAinteger64Time(101)

        grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.timeAdvanceRequestAvailable(HLAinteger64Time(110))
        blocked_grants = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[grant_baseline:]
        assert blocked_grants == []

        slow.timeAdvanceRequestAvailable(HLAinteger64Time(109))
        assert slow_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(109),)

        cleared_galt = radar.queryGALT()
        cleared_lits = radar.queryLITS()
        assert cleared_galt.timeIsValid is True
        assert cleared_lits.timeIsValid is True
        assert cleared_galt.time == HLAinteger64Time(110)
        assert cleared_lits.time == HLAinteger64Time(110)

        final_grants = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[grant_baseline:]
        assert final_grants == [(HLAinteger64Time(110),)]

        with pytest.raises(InvalidLogicalTime):
            slow.sendInteraction(
                interaction_class,
                {parameter: b"late-track-109"},
                b"late-track-109",
                HLAinteger64Time(109),
            )

        receive_baseline = len(_callbacks_named_2025(radar_federate, "receiveInteraction"))
        slow.sendInteraction(
            interaction_class,
            {parameter: b"boundary-track-110"},
            b"boundary-track-110",
            HLAinteger64Time(110),
        )
        slow.timeAdvanceRequestAvailable(HLAinteger64Time(120))
        radar.nextMessageRequestAvailable(HLAinteger64Time(120))

        receives = _callbacks_named_2025(radar_federate, "receiveInteraction")[receive_baseline:]
        assert len(receives) == 1
        assert receives[0][2] == b"boundary-track-110"
        assert receives[0][6] == HLAinteger64Time(110)
    finally:
        try:
            radar.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            slow.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            slow.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        try:
            radar.disconnect()
        except Exception:
            pass
        try:
            slow.disconnect()
        except Exception:
            pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-107",
    "HLA2025-FI-SVC-108",
    "HLA2025-FI-SVC-122",
    "HLA2025-FI-SVC-123",
    "HLA2025-BND-003",
)
def test_2025_shim_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    fom = tmp_path / "Exchange2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Exchange 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused exchange fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-time-restore-divergence-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-DIVERGENCE"
    sender_federate = Recording2025FederateAmbassador()
    receiver_federate = Recording2025FederateAmbassador()
    sender = create_rti_ambassador(backend="shim")
    receiver = create_rti_ambassador(backend="shim")

    try:
        sender.connect(sender_federate, CallbackModel.HLA_EVOKED)
        receiver.connect(receiver_federate, CallbackModel.HLA_EVOKED)
        sender.createFederationExecution(
            federationName=federation_name,
            fomModule=str(fom),
            logicalTimeImplementationName="HLAinteger64Time",
        )
        sender_handle = sender.joinFederationExecution(
            federateName="RestoreDivergenceSender",
            federateType="TestFederate",
            federationName=federation_name,
        )
        receiver_handle = receiver.joinFederationExecution(
            federateName="RestoreDivergenceReceiver",
            federateType="TestFederate",
            federationName=federation_name,
        )

        interaction_class = sender.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = sender.getParameterHandle(interaction_class, "TrackId")
        sender.publishInteractionClass(interaction_class)
        receiver.subscribeInteractionClass(interaction_class)

        sender.enableTimeRegulation(HLAinteger64Interval(2))
        receiver.enableTimeRegulation(HLAinteger64Interval(1))
        assert sender_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert receiver_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)

        sender.timeAdvanceRequest(HLAinteger64Time(5))
        receiver.timeAdvanceRequest(HLAinteger64Time(9))
        assert sender_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(5),)
        assert receiver_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(9),)

        sender.sendInteraction(
            interaction_class,
            {parameter: b"pre-save-queue"},
            b"pre-save-queue",
            HLAinteger64Time(7),
        )

        assert sender.queryLookahead() == HLAinteger64Interval(2)
        assert receiver.queryLookahead() == HLAinteger64Interval(1)
        assert sender.queryLogicalTime() == HLAinteger64Time(5)
        assert receiver.queryLogicalTime() == HLAinteger64Time(9)
        assert receiver.queryGALT().time == HLAinteger64Time(7)
        assert receiver.queryLITS().time == HLAinteger64Time(7)

        sender_federate.callbacks.clear()
        receiver_federate.callbacks.clear()
        sender.requestFederationSave(save_label)
        assert sender_federate.last_callback("initiateFederateSave") == (save_label,)
        assert receiver_federate.last_callback("initiateFederateSave") == (save_label,)
        sender.federateSaveBegun()
        receiver.federateSaveBegun()
        sender.federateSaveComplete()
        receiver.federateSaveComplete()
        assert sender_federate.last_callback("federationSaved") == ()
        assert receiver_federate.last_callback("federationSaved") == ()

        sender.modifyLookahead(HLAinteger64Interval(12))
        assert sender.queryLookahead() == HLAinteger64Interval(12)
        assert receiver.queryGALT().time == HLAinteger64Time(17)
        assert receiver.queryLITS().time == HLAinteger64Time(7)

        sender_federate.callbacks.clear()
        receiver_federate.callbacks.clear()
        sender.requestFederationRestore(save_label)
        assert sender_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert sender_federate.last_callback("federationRestoreBegun") == ()
        assert receiver_federate.last_callback("federationRestoreBegun") == ()
        assert sender_federate.last_callback("initiateFederateRestore") == (
            save_label,
            "RestoreDivergenceSender",
            sender_handle,
        )
        assert receiver_federate.last_callback("initiateFederateRestore") == (
            save_label,
            "RestoreDivergenceReceiver",
            receiver_handle,
        )
        sender.federateRestoreComplete()
        receiver.federateRestoreComplete()
        assert sender_federate.last_callback("federationRestored") == ()
        assert receiver_federate.last_callback("federationRestored") == ()

        assert sender.queryLookahead() == HLAinteger64Interval(2)
        assert receiver.queryLookahead() == HLAinteger64Interval(1)
        assert sender.queryLogicalTime() == HLAinteger64Time(5)
        assert receiver.queryLogicalTime() == HLAinteger64Time(9)
        assert receiver.queryGALT().time == HLAinteger64Time(7)
        assert receiver.queryLITS().time == HLAinteger64Time(7)

        receive_baseline = len(_callbacks_named_2025(receiver_federate, "receiveInteraction"))
        grant_baseline = len(_callbacks_named_2025(receiver_federate, "timeAdvanceGrant"))
        receiver.nextMessageRequestAvailable(HLAinteger64Time(20))
        post_restore_receives = _callbacks_named_2025(receiver_federate, "receiveInteraction")[receive_baseline:]
        assert len(post_restore_receives) == 1
        assert post_restore_receives[0][1] == {parameter: b"pre-save-queue"}
        assert post_restore_receives[0][2] == b"pre-save-queue"
        assert post_restore_receives[0][6] == HLAinteger64Time(7)
        assert _callbacks_named_2025(receiver_federate, "timeAdvanceGrant")[grant_baseline:] == [(HLAinteger64Time(7),)]
        assert receiver.queryGALT().time == HLAinteger64Time(7)
        assert receiver.queryLITS().time == HLAinteger64Time(7)
    finally:
        try:
            receiver.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            sender.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            sender.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        try:
            receiver.disconnect()
        except Exception:
            pass
        try:
            sender.disconnect()
        except Exception:
            pass


@pytest.mark.requirements("HLA2025-FI-SVC-018", "HLA2025-FI-SVC-023", "HLA2025-FI-SVC-032")
def test_2025_shim_restore_recovers_time_and_switch_control_state() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import TimeRegulationIsNotEnabled
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-control-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-CONTROL"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")

    try:
        rti.connect(federate, CallbackModel.HLA_EVOKED)
        rti.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        rti.joinFederationExecution(
            federateName="ControlRestore",
            federateType="TestFederate",
            federationName=federation_name,
        )

        rti.enableTimeRegulation(HLAinteger64Interval(2))
        rti.enableTimeConstrained()
        assert federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)
        rti.enableAsynchronousDelivery()
        rti.setServiceReportingSwitch(True)
        rti.setExceptionReportingSwitch(False)
        rti.setAutomaticResignDirective(ResignAction.DELETE_OBJECTS)
        rti.setConveyRegionDesignatorSetsSwitch(False)
        rti.setObjectClassRelevanceAdvisorySwitch(True)

        assert rti.queryLookahead() == HLAinteger64Interval(2)
        assert rti.getServiceReportingSwitch() is True
        assert rti.getExceptionReportingSwitch() is False
        assert rti.getAutomaticResignDirective() is ResignAction.DELETE_OBJECTS
        assert rti.getConveyRegionDesignatorSetsSwitch() is False
        assert rti.getObjectClassRelevanceAdvisorySwitch() is True

        federate.callbacks.clear()
        rti.requestFederationSave(save_label)
        assert federate.last_callback("initiateFederateSave") == (save_label,)
        rti.federateSaveBegun()
        rti.federateSaveComplete()
        assert federate.last_callback("federationSaved") == ()

        rti.modifyLookahead(HLAinteger64Interval(7))
        rti.disableAsynchronousDelivery()
        rti.disableTimeConstrained()
        rti.disableTimeRegulation()
        rti.setServiceReportingSwitch(False)
        rti.setExceptionReportingSwitch(True)
        rti.setAutomaticResignDirective(ResignAction.NO_ACTION)
        rti.setConveyRegionDesignatorSetsSwitch(True)
        rti.setObjectClassRelevanceAdvisorySwitch(False)

        with pytest.raises(TimeRegulationIsNotEnabled):
            rti.queryLookahead()
        assert rti.getServiceReportingSwitch() is False
        assert rti.getExceptionReportingSwitch() is True
        assert rti.getAutomaticResignDirective() is ResignAction.NO_ACTION
        assert rti.getConveyRegionDesignatorSetsSwitch() is True
        assert rti.getObjectClassRelevanceAdvisorySwitch() is False

        federate.callbacks.clear()
        rti.requestFederationRestore(save_label)
        assert federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert federate.last_callback("federationRestoreBegun") == ()
        assert federate.last_callback("initiateFederateRestore")[:2] == (save_label, "ControlRestore")
        rti.federateRestoreComplete()
        assert federate.last_callback("federationRestored") == ()

        assert rti.queryLookahead() == HLAinteger64Interval(2)
        assert rti.getServiceReportingSwitch() is True
        assert rti.getExceptionReportingSwitch() is False
        assert rti.getAutomaticResignDirective() is ResignAction.DELETE_OBJECTS
        assert rti.getConveyRegionDesignatorSetsSwitch() is False
        assert rti.getObjectClassRelevanceAdvisorySwitch() is True
    finally:
        try:
            rti.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
        try:
            rti.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        try:
            rti.disconnect()
        except Exception:
            pass


@pytest.mark.requirements("HLA2025-FI-SVC-018", "HLA2025-FI-SVC-023", "HLA2025-FI-SVC-032")
def test_2025_shim_restore_recovers_transport_and_order_policy_state(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "PolicyRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Policy Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused policy restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAfloat64BE</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-policy-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-POLICY"
    owner_federate = Recording2025FederateAmbassador()
    subscriber_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    try:
        owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        owner_handle = owner.joinFederationExecution("PolicyRestoreOwner", "TestFederate", federation_name)
        subscriber.joinFederationExecution("PolicyRestoreSubscriber", "TestFederate", federation_name)

        object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        subscriber_object_class = subscriber.getObjectClassHandle("HLAobjectRoot.Target")
        attribute = owner.getAttributeHandle(object_class, "Position")
        subscriber_attribute = subscriber.getAttributeHandle(subscriber_object_class, "Position")
        interaction_class = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = owner.getParameterHandle(interaction_class, "TrackId")
        subscriber_parameter = subscriber.getParameterHandle(subscriber_interaction_class, "TrackId")
        reliable = owner.getTransportationTypeHandle("HLAreliable")
        best_effort = owner.getTransportationTypeHandle("HLAbestEffort")

        owner.publishObjectClassAttributes(object_class, {attribute})
        owner.publishInteractionClass(interaction_class)
        subscriber.subscribeObjectClassAttributes(subscriber_object_class, {subscriber_attribute})
        subscriber.subscribeInteractionClass(subscriber_interaction_class)
        object_instance = owner.registerObjectInstance(object_class, "PolicyRestoreTarget-1")
        assert subscriber_federate.last_callback("discoverObjectInstance") == (
            object_instance,
            subscriber_object_class,
            "PolicyRestoreTarget-1",
            owner_handle,
        )

        owner.changeDefaultAttributeTransportationType(object_class, {attribute}, best_effort)
        owner.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.TIMESTAMP)
        owner.requestInteractionTransportationTypeChange(interaction_class, best_effort)
        assert owner_federate.last_callback("confirmInteractionTransportationTypeChange") == (interaction_class, best_effort)
        owner.changeInteractionOrderType(interaction_class, OrderType.TIMESTAMP)
        assert owner.defaultAttributePolicySnapshot() == {
            "transportation": {"HLAobjectRoot.Target.Position": "HLAbestEffort"},
            "order": {"HLAobjectRoot.Target.Position": "TIMESTAMP"},
        }
        subscriber.queryInteractionTransportationType(owner_handle, subscriber_interaction_class)
        assert subscriber_federate.last_callback("reportInteractionTransportationType") == (
            owner_handle,
            subscriber_interaction_class,
            best_effort,
        )

        owner_federate.callbacks.clear()
        subscriber_federate.callbacks.clear()
        owner.requestFederationSave(save_label)
        assert owner_federate.last_callback("initiateFederateSave") == (save_label,)
        assert subscriber_federate.last_callback("initiateFederateSave") == (save_label,)
        owner.federateSaveBegun()
        subscriber.federateSaveBegun()
        owner.federateSaveComplete()
        subscriber.federateSaveComplete()
        assert owner_federate.last_callback("federationSaved") == ()
        assert subscriber_federate.last_callback("federationSaved") == ()

        owner.changeDefaultAttributeTransportationType(object_class, {attribute}, reliable)
        owner.changeDefaultAttributeOrderType(object_class, {attribute}, OrderType.RECEIVE)
        owner.requestInteractionTransportationTypeChange(interaction_class, reliable)
        assert owner_federate.last_callback("confirmInteractionTransportationTypeChange") == (interaction_class, reliable)
        owner.changeInteractionOrderType(interaction_class, OrderType.RECEIVE)

        owner_federate.callbacks.clear()
        subscriber_federate.callbacks.clear()
        owner.requestFederationRestore(save_label)
        assert owner_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert owner_federate.last_callback("federationRestoreBegun") == ()
        assert subscriber_federate.last_callback("federationRestoreBegun") == ()
        owner.federateRestoreComplete()
        subscriber.federateRestoreComplete()
        assert owner_federate.last_callback("federationRestored") == ()
        assert subscriber_federate.last_callback("federationRestored") == ()

        assert owner.defaultAttributePolicySnapshot() == {
            "transportation": {"HLAobjectRoot.Target.Position": "HLAbestEffort"},
            "order": {"HLAobjectRoot.Target.Position": "TIMESTAMP"},
        }
        subscriber.queryInteractionTransportationType(owner_handle, subscriber_interaction_class)
        assert subscriber_federate.last_callback("reportInteractionTransportationType") == (
            owner_handle,
            subscriber_interaction_class,
            best_effort,
        )

        subscriber_federate.callbacks.clear()
        owner.updateAttributeValues(object_instance, {attribute: b"restored-attr"}, b"restored-attr-tag")
        reflection = subscriber_federate.last_callback("reflectAttributeValues")
        assert reflection is not None
        assert reflection[:6] == (
            object_instance,
            {subscriber_attribute: b"restored-attr"},
            b"restored-attr-tag",
            best_effort,
            owner_handle,
            set(),
        )
        assert reflection[6:] == (None, OrderType.TIMESTAMP, OrderType.TIMESTAMP, None)

        owner.sendInteraction(interaction_class, {parameter: b"restored-track"}, b"restored-track-tag")
        received = subscriber_federate.last_callback("receiveInteraction")
        assert received is not None
        assert received[:6] == (
            subscriber_interaction_class,
            {subscriber_parameter: b"restored-track"},
            b"restored-track-tag",
            best_effort,
            owner_handle,
            set(),
        )
        assert received[6:] == (None, OrderType.TIMESTAMP, OrderType.TIMESTAMP, None)
    finally:
        for rti in (subscriber, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (subscriber, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-193",
    "HLA2025-FI-SVC-194",
)
def test_2025_shim_restore_recovers_callback_delivery_policy(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "CallbackRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Callback Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused callback restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-callback-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-CALLBACKS"
    publisher_federate = Recording2025FederateAmbassador()
    subscriber_federate = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")

    try:
        publisher.connect(publisher_federate, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
        publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        publisher_handle = publisher.joinFederationExecution("CallbackRestorePublisher", "TestFederate", federation_name)
        subscriber.joinFederationExecution("CallbackRestoreSubscriber", "TestFederate", federation_name)

        interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_interaction_class = subscriber.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = publisher.getParameterHandle(interaction_class, "TrackId")
        subscriber_parameter = subscriber.getParameterHandle(subscriber_interaction_class, "TrackId")
        publisher.publishInteractionClass(interaction_class)
        subscriber.subscribeInteractionClass(subscriber_interaction_class)

        publisher_federate.callbacks.clear()
        subscriber_federate.callbacks.clear()
        subscriber.disableCallbacks()
        publisher.sendInteraction(interaction_class, {parameter: b"SAVED"}, b"saved-cb")
        assert subscriber_federate.last_callback("receiveInteraction") is None
        assert subscriber.evokeCallback(0.0) is False

        publisher.requestFederationSave(save_label)
        publisher.federateSaveBegun()
        subscriber.federateSaveBegun()
        publisher.federateSaveComplete()
        subscriber.federateSaveComplete()

        publisher_federate.callbacks.clear()
        subscriber_federate.callbacks.clear()
        subscriber.enableCallbacks()
        publisher.sendInteraction(interaction_class, {parameter: b"MUTATED"}, b"mutated-cb")
        mutated = subscriber_federate.last_callback("receiveInteraction")
        assert mutated is not None
        assert mutated[:3] == (
            subscriber_interaction_class,
            {subscriber_parameter: b"MUTATED"},
            b"mutated-cb",
        )
        assert mutated[4] == publisher_handle

        publisher_federate.callbacks.clear()
        subscriber_federate.callbacks.clear()
        publisher.requestFederationRestore(save_label)
        assert publisher_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert publisher_federate.last_callback("federationRestoreBegun") == ()
        assert publisher_federate.last_callback("initiateFederateRestore")[:2] == (save_label, "CallbackRestorePublisher")
        assert subscriber_federate.last_callback("initiateFederateRestore")[:2] == (save_label, "CallbackRestoreSubscriber")
        publisher.federateRestoreComplete()
        subscriber.federateRestoreComplete()
        assert subscriber_federate.last_callback("federationRestored") is None
        assert subscriber.evokeCallback(0.0) is False

        subscriber_federate.callbacks.clear()
        publisher.sendInteraction(interaction_class, {parameter: b"RESTORED"}, b"restored-cb")
        assert subscriber_federate.last_callback("receiveInteraction") is None
        assert subscriber.evokeCallback(0.0) is False

        subscriber.enableCallbacks()
        assert subscriber.evokeCallback(0.0) is True
        restored_receives = _callbacks_named_2025(subscriber_federate, "receiveInteraction")
        assert len(restored_receives) == 1
        restored = restored_receives[0]
        assert restored[:3] == (
            subscriber_interaction_class,
            {subscriber_parameter: b"RESTORED"},
            b"restored-cb",
        )
        assert restored[3] == publisher.getTransportationTypeHandle("HLAreliable")
        assert restored[4] == publisher_handle
        assert restored[5] == set()
        assert restored[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)
        assert subscriber.evokeCallback(0.0) is False
    finally:
        for rti in (subscriber, publisher):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            publisher.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (subscriber, publisher):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
)
def test_2025_shim_restore_recovers_plain_object_subscriber_routing(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "ObjectRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Object Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused object subscriber restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-object-routing-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-OBJECT-ROUTING"
    owner_federate = Recording2025FederateAmbassador()
    subscriber_a_federate = Recording2025FederateAmbassador()
    subscriber_b_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    subscriber_a = create_rti_ambassador(backend="shim")
    subscriber_b = create_rti_ambassador(backend="shim")

    try:
        for rti, federate in (
            (owner, owner_federate),
            (subscriber_a, subscriber_a_federate),
            (subscriber_b, subscriber_b_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        owner_handle = owner.joinFederationExecution("ObjectOwner", "Controller", federation_name)
        subscriber_a.joinFederationExecution("ObjectA", "Observer", federation_name)
        subscriber_b.joinFederationExecution("ObjectB", "Observer", federation_name)

        owner_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        subscriber_a_class = subscriber_a.getObjectClassHandle("HLAobjectRoot.Target")
        subscriber_b_class = subscriber_b.getObjectClassHandle("HLAobjectRoot.Target")
        owner_attribute = owner.getAttributeHandle(owner_class, "Position")
        subscriber_a_attribute = subscriber_a.getAttributeHandle(subscriber_a_class, "Position")
        subscriber_b_attribute = subscriber_b.getAttributeHandle(subscriber_b_class, "Position")

        owner.publishObjectClassAttributes(owner_class, {owner_attribute})
        subscriber_a.subscribeObjectClassAttributes(subscriber_a_class, {subscriber_a_attribute})

        object_instance = owner.registerObjectInstance(owner_class, "ShimObjectRestoreTarget-1")
        assert subscriber_a_federate.last_callback("discoverObjectInstance") == (
            object_instance,
            subscriber_a_class,
            "ShimObjectRestoreTarget-1",
            owner_handle,
        )

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        owner.updateAttributeValues(object_instance, {owner_attribute: b"SAVED"}, b"saved-route")
        assert subscriber_b_federate.last_callback("reflectAttributeValues") is None
        saved_reflect = subscriber_a_federate.last_callback("reflectAttributeValues")
        assert saved_reflect is not None
        assert saved_reflect[:3] == (
            object_instance,
            {subscriber_a_attribute: b"SAVED"},
            b"saved-route",
        )

        owner.requestFederationSave(save_label)
        for rti in (owner, subscriber_a, subscriber_b):
            rti.federateSaveBegun()
        for rti in (owner, subscriber_a, subscriber_b):
            rti.federateSaveComplete()

        subscriber_a.unsubscribeObjectClassAttributes(subscriber_a_class, {subscriber_a_attribute})
        subscriber_b.subscribeObjectClassAttributes(subscriber_b_class, {subscriber_b_attribute})
        assert subscriber_b_federate.last_callback("discoverObjectInstance") == (
            object_instance,
            subscriber_b_class,
            "ShimObjectRestoreTarget-1",
            owner_handle,
        )

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        owner.updateAttributeValues(object_instance, {owner_attribute: b"MUTATED"}, b"mutated-route")
        assert subscriber_a_federate.last_callback("reflectAttributeValues") is None
        mutated_reflect = subscriber_b_federate.last_callback("reflectAttributeValues")
        assert mutated_reflect is not None
        assert mutated_reflect[:3] == (
            object_instance,
            {subscriber_b_attribute: b"MUTATED"},
            b"mutated-route",
        )

        owner.requestFederationRestore(save_label)
        for rti in (owner, subscriber_a, subscriber_b):
            rti.federateRestoreComplete()

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        owner.updateAttributeValues(object_instance, {owner_attribute: b"RESTORED"}, b"restored-route")
        assert subscriber_b_federate.last_callback("reflectAttributeValues") is None
        restored_reflect = subscriber_a_federate.last_callback("reflectAttributeValues")
        assert restored_reflect is not None
        assert restored_reflect[:3] == (
            object_instance,
            {subscriber_a_attribute: b"RESTORED"},
            b"restored-route",
        )
    finally:
        for rti in (subscriber_b, subscriber_a, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (subscriber_b, subscriber_a, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-060",
    "HLA2025-FI-SVC-134",
)
def test_2025_shim_restore_recovers_plain_interaction_subscriber_routing(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "InteractionRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Interaction Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused interaction subscriber restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-interaction-routing-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-INTERACTION-ROUTING"
    publisher_federate = Recording2025FederateAmbassador()
    subscriber_a_federate = Recording2025FederateAmbassador()
    subscriber_b_federate = Recording2025FederateAmbassador()
    publisher = create_rti_ambassador(backend="shim")
    subscriber_a = create_rti_ambassador(backend="shim")
    subscriber_b = create_rti_ambassador(backend="shim")

    try:
        for rti, federate in (
            (publisher, publisher_federate),
            (subscriber_a, subscriber_a_federate),
            (subscriber_b, subscriber_b_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        publisher.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        publisher_handle = publisher.joinFederationExecution("InteractionOwner", "Controller", federation_name)
        subscriber_a.joinFederationExecution("InteractionA", "Observer", federation_name)
        subscriber_b.joinFederationExecution("InteractionB", "Observer", federation_name)

        interaction_class = publisher.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_a_interaction = subscriber_a.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_b_interaction = subscriber_b.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = publisher.getParameterHandle(interaction_class, "TrackId")
        subscriber_a_parameter = subscriber_a.getParameterHandle(subscriber_a_interaction, "TrackId")
        subscriber_b_parameter = subscriber_b.getParameterHandle(subscriber_b_interaction, "TrackId")

        publisher.publishInteractionClass(interaction_class)
        subscriber_a.subscribeInteractionClass(subscriber_a_interaction)

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        publisher.sendInteraction(interaction_class, {parameter: b"SAVED"}, b"saved-interaction")
        assert subscriber_b_federate.last_callback("receiveInteraction") is None
        saved_receive = subscriber_a_federate.last_callback("receiveInteraction")
        assert saved_receive is not None
        assert saved_receive[:3] == (
            subscriber_a_interaction,
            {subscriber_a_parameter: b"SAVED"},
            b"saved-interaction",
        )
        assert saved_receive[4] == publisher_handle

        publisher.requestFederationSave(save_label)
        for rti in (publisher, subscriber_a, subscriber_b):
            rti.federateSaveBegun()
        for rti in (publisher, subscriber_a, subscriber_b):
            rti.federateSaveComplete()

        subscriber_a.unsubscribeInteractionClass(subscriber_a_interaction)
        subscriber_b.subscribeInteractionClass(subscriber_b_interaction)

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        publisher.sendInteraction(interaction_class, {parameter: b"MUTATED"}, b"mutated-interaction")
        assert subscriber_a_federate.last_callback("receiveInteraction") is None
        mutated_receive = subscriber_b_federate.last_callback("receiveInteraction")
        assert mutated_receive is not None
        assert mutated_receive[:3] == (
            subscriber_b_interaction,
            {subscriber_b_parameter: b"MUTATED"},
            b"mutated-interaction",
        )
        assert mutated_receive[4] == publisher_handle

        publisher.requestFederationRestore(save_label)
        for rti in (publisher, subscriber_a, subscriber_b):
            rti.federateRestoreComplete()

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        publisher.sendInteraction(interaction_class, {parameter: b"RESTORED"}, b"restored-interaction")
        assert subscriber_b_federate.last_callback("receiveInteraction") is None
        restored_receive = subscriber_a_federate.last_callback("receiveInteraction")
        assert restored_receive is not None
        assert restored_receive[:3] == (
            subscriber_a_interaction,
            {subscriber_a_parameter: b"RESTORED"},
            b"restored-interaction",
        )
        assert restored_receive[4] == publisher_handle
    finally:
        for rti in (subscriber_b, subscriber_a, publisher):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            publisher.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (subscriber_b, subscriber_a, publisher):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-097",
)
def test_2025_shim_restore_recovers_inflight_ownership_state(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import NoAcquisitionPending
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "Ownership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused ownership restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-ownership-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-OWNERSHIP"
    owner_federate = Recording2025FederateAmbassador()
    acquirer_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")

    try:
        owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
        acquirer.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        owner.joinFederationExecution("OwnerRestore", "TestFederate", federation_name)
        acquirer.joinFederationExecution("AcquirerRestore", "TestFederate", federation_name)

        object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        owner_attribute = owner.getAttributeHandle(object_class, "Position")
        acquirer_class = acquirer.getObjectClassHandle("HLAobjectRoot.Target")
        acquirer_attribute = acquirer.getAttributeHandle(acquirer_class, "Position")
        object_instance = owner.registerObjectInstance(object_class, "ShimOwnershipRestoreTarget-1")

        owner.negotiatedAttributeOwnershipDivestiture(object_instance, {owner_attribute}, b"saved-offer")
        assert acquirer_federate.last_callback("requestAttributeOwnershipAssumption") == (
            object_instance,
            {acquirer_attribute},
            b"saved-offer",
        )
        acquirer.attributeOwnershipAcquisition(object_instance, {acquirer_attribute}, b"saved-pending")
        assert owner_federate.last_callback("requestDivestitureConfirmation") == (
            object_instance,
            {owner_attribute},
            b"saved-pending",
        )

        owner.requestFederationSave(save_label)
        for rti in (owner, acquirer):
            rti.federateSaveBegun()
        for rti in (owner, acquirer):
            rti.federateSaveComplete()

        owner.cancelNegotiatedAttributeOwnershipDivestiture(object_instance, {owner_attribute})
        acquirer.cancelAttributeOwnershipAcquisition(object_instance, {acquirer_attribute})
        assert acquirer_federate.last_callback("confirmAttributeOwnershipAcquisitionCancellation") == (
            object_instance,
            {acquirer_attribute},
        )
        with pytest.raises(NoAcquisitionPending):
            owner.attributeOwnershipDivestitureIfWanted(object_instance, {owner_attribute})

        owner.requestFederationRestore(save_label)
        for rti in (owner, acquirer):
            rti.federateRestoreComplete()

        acquirer_federate.callbacks.clear()
        divested = owner.attributeOwnershipDivestitureIfWanted(object_instance, {owner_attribute})
        assert divested == {owner_attribute}
        assert acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification") == (
            object_instance,
            {acquirer_attribute},
            b"",
        )
        assert acquirer.isAttributeOwnedByFederate(object_instance, acquirer_attribute) is True
        assert owner.isAttributeOwnedByFederate(object_instance, owner_attribute) is False
    finally:
        for rti in (acquirer, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (acquirer, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-083",
    "HLA2025-FI-SVC-087",
    "HLA2025-FI-SVC-090",
    "HLA2025-FI-SVC-097",
)
def test_2025_shim_restores_cross_federate_attribute_owner_visibility(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "Ownership2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Ownership 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused owner visibility restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-owner-visibility-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-OWNER-VIS"
    owner_federate = Recording2025FederateAmbassador()
    acquirer_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    acquirer = create_rti_ambassador(backend="shim")

    try:
        owner.connect(owner_federate, CallbackModel.HLA_EVOKED)
        acquirer.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        owner.joinFederationExecution("Owner", "Controller", federation_name)
        acquirer_handle = acquirer.joinFederationExecution("Acquirer", "Observer", federation_name)

        object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        owner_attribute = owner.getAttributeHandle(object_class, "Position")
        acquirer_class = acquirer.getObjectClassHandle("HLAobjectRoot.Target")
        acquirer_attribute = acquirer.getAttributeHandle(acquirer_class, "Position")
        object_instance = owner.registerObjectInstance(object_class, "ShimOwnerVisibilityTarget-1")

        owner.negotiatedAttributeOwnershipDivestiture(object_instance, {owner_attribute}, b"offer")
        assert acquirer_federate.last_callback("requestAttributeOwnershipAssumption") == (
            object_instance,
            {acquirer_attribute},
            b"offer",
        )
        acquirer.attributeOwnershipAcquisition(object_instance, {acquirer_attribute}, b"acquire")
        assert owner_federate.last_callback("requestDivestitureConfirmation") == (
            object_instance,
            {owner_attribute},
            b"acquire",
        )
        owner.confirmDivestiture(object_instance, {owner_attribute}, b"confirm")
        assert acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification") == (
            object_instance,
            {acquirer_attribute},
            b"confirm",
        )
        owner.queryAttributeOwnership(object_instance, {owner_attribute})
        assert owner_federate.last_callback("informAttributeOwnership") == (
            object_instance,
            {owner_attribute},
            acquirer_handle,
        )

        owner.requestFederationSave(save_label)
        for rti in (owner, acquirer):
            rti.federateSaveBegun()
        for rti in (owner, acquirer):
            rti.federateSaveComplete()

        acquirer.unconditionalAttributeOwnershipDivestiture(object_instance, {acquirer_attribute}, b"dirty-divest")
        owner.queryAttributeOwnership(object_instance, {owner_attribute})
        assert owner_federate.last_callback("attributeIsNotOwned") == (object_instance, {owner_attribute})

        owner.requestFederationRestore(save_label)
        for rti in (owner, acquirer):
            rti.federateRestoreComplete()

        owner.queryAttributeOwnership(object_instance, {owner_attribute})
        assert owner_federate.last_callback("informAttributeOwnership") == (
            object_instance,
            {owner_attribute},
            acquirer_handle,
        )
    finally:
        for rti in (acquirer, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (acquirer, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-063",
    "HLA2025-FI-SVC-064",
    "HLA2025-FI-SVC-129",
)
def test_2025_shim_restore_recovers_directed_ddm_subscriber_routing(tmp_path: Path) -> None:
    from hla.rti1516_2025.datatypes import RangeBounds
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    fom = tmp_path / "DirectedDDMRestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Directed DDM Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused directed DDM restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <dimensions>
    <dimension>
      <name>RoutingSpace</name>
      <upperBound>100</upperBound>
    </dimension>
  </dimensions>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <dimension>RoutingSpace</dimension>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <dimension>RoutingSpace</dimension>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-directed-ddm-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-DIRECTED-DDM"
    owner_federate = Recording2025FederateAmbassador()
    subscriber_a_federate = Recording2025FederateAmbassador()
    subscriber_b_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    subscriber_a = create_rti_ambassador(backend="shim")
    subscriber_b = create_rti_ambassador(backend="shim")

    try:
        for rti, federate in (
            (owner, owner_federate),
            (subscriber_a, subscriber_a_federate),
            (subscriber_b, subscriber_b_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(federationName=federation_name, fomModule=str(fom))
        owner.joinFederationExecution("DirectedOwner", "Controller", federation_name)
        subscriber_a.joinFederationExecution("DirectedA", "Observer", federation_name)
        subscriber_b.joinFederationExecution("DirectedB", "Observer", federation_name)

        object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        owner_attribute = owner.getAttributeHandle(object_class, "Position")
        interaction_class = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_a_interaction = subscriber_a.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_b_interaction = subscriber_b.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = owner.getParameterHandle(interaction_class, "TrackId")
        subscriber_a_parameter = subscriber_a.getParameterHandle(subscriber_a_interaction, "TrackId")
        dimension = owner.getDimensionHandle("RoutingSpace")
        subscriber_a_dimension = subscriber_a.getDimensionHandle("RoutingSpace")
        subscriber_b_dimension = subscriber_b.getDimensionHandle("RoutingSpace")

        owner.publishObjectClassDirectedInteractions(object_class, {interaction_class})
        subscriber_a.subscribeObjectClassDirectedInteractions(object_class, {subscriber_a_interaction})
        subscriber_b.subscribeObjectClassDirectedInteractions(object_class, {subscriber_b_interaction})

        publisher_region = owner.createRegion({dimension})
        subscriber_a_region = subscriber_a.createRegion({subscriber_a_dimension})
        subscriber_b_region = subscriber_b.createRegion({subscriber_b_dimension})
        owner.setRangeBounds(publisher_region, dimension, RangeBounds(0, 10))
        subscriber_a.setRangeBounds(subscriber_a_region, subscriber_a_dimension, RangeBounds(5, 15))
        subscriber_b.setRangeBounds(subscriber_b_region, subscriber_b_dimension, RangeBounds(50, 60))
        owner.commitRegionModifications({publisher_region})
        subscriber_a.commitRegionModifications({subscriber_a_region})
        subscriber_b.commitRegionModifications({subscriber_b_region})

        object_instance = owner.registerObjectInstance(object_class, "ShimDirectedRestoreTarget-1")
        owner.associateRegionsForUpdates(object_instance, [({owner_attribute}, {publisher_region})])
        subscriber_a.subscribeInteractionClassWithRegions(subscriber_a_interaction, {subscriber_a_region})
        subscriber_b.subscribeInteractionClassWithRegions(subscriber_b_interaction, {subscriber_b_region})

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        owner.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"SAVED"}, b"save-state")
        assert subscriber_b_federate.last_callback("receiveDirectedInteraction") is None
        saved_receive = subscriber_a_federate.last_callback("receiveDirectedInteraction")
        assert saved_receive is not None
        assert saved_receive[:4] == (
            subscriber_a_interaction,
            object_instance,
            {subscriber_a_parameter: b"SAVED"},
            b"save-state",
        )

        owner.requestFederationSave(save_label)
        for rti in (owner, subscriber_a, subscriber_b):
            rti.federateSaveBegun()
        for rti in (owner, subscriber_a, subscriber_b):
            rti.federateSaveComplete()

        subscriber_a.unsubscribeObjectClassDirectedInteractions(object_class, {subscriber_a_interaction})
        subscriber_a.unsubscribeInteractionClassWithRegions(subscriber_a_interaction, {subscriber_a_region})
        subscriber_b.setRangeBounds(subscriber_b_region, subscriber_b_dimension, RangeBounds(8, 12))
        subscriber_b.commitRegionModifications({subscriber_b_region})

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        owner.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"MUTATED"}, b"mutated-state")
        assert subscriber_a_federate.last_callback("receiveDirectedInteraction") is None
        mutated_receive = subscriber_b_federate.last_callback("receiveDirectedInteraction")
        assert mutated_receive is not None
        assert mutated_receive[:4] == (
            subscriber_b_interaction,
            object_instance,
            {subscriber_a_parameter: b"MUTATED"},
            b"mutated-state",
        )

        owner.requestFederationRestore(save_label)
        for rti in (owner, subscriber_a, subscriber_b):
            rti.federateRestoreComplete()

        subscriber_a_federate.callbacks.clear()
        subscriber_b_federate.callbacks.clear()
        owner.sendDirectedInteraction(interaction_class, object_instance, {parameter: b"RESTORED"}, b"restored-state")
        assert subscriber_b_federate.last_callback("receiveDirectedInteraction") is None
        restored_receive = subscriber_a_federate.last_callback("receiveDirectedInteraction")
        assert restored_receive is not None
        assert restored_receive[:4] == (
            subscriber_a_interaction,
            object_instance,
            {subscriber_a_parameter: b"RESTORED"},
            b"restored-state",
        )
    finally:
        for rti in (subscriber_b, subscriber_a, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (subscriber_b, subscriber_a, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements(
    "HLA2025-FI-SVC-018",
    "HLA2025-FI-SVC-023",
    "HLA2025-FI-SVC-032",
    "HLA2025-FI-SVC-111",
    "HLA2025-FI-SVC-116",
    "HLA2025-FI-SVC-117",
)
def test_2025_shim_restore_clears_stale_directed_tso_and_preserves_post_restore_routing(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InvalidMessageRetractionHandle
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    fom = tmp_path / "DirectedTSORestore2025.xml"
    fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Directed TSO Restore 2025</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Focused directed TSO restore fixture.</description>
    <poc><pocName>HLA-X</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>TimeStamp</order>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-2025-directed-tso-restore-{uuid.uuid4().hex[:8]}"
    save_label = "SAVE-DIRECTED-TSO"
    owner_federate = Recording2025FederateAmbassador()
    subscriber_federate = Recording2025FederateAmbassador()
    observer_federate = Recording2025FederateAmbassador()
    owner = create_rti_ambassador(backend="shim")
    subscriber = create_rti_ambassador(backend="shim")
    observer = create_rti_ambassador(backend="shim")

    try:
        for rti, federate in (
            (owner, owner_federate),
            (subscriber, subscriber_federate),
            (observer, observer_federate),
        ):
            rti.connect(federate, CallbackModel.HLA_EVOKED)
        owner.createFederationExecution(
            federationName=federation_name,
            fomModule=str(fom),
            logicalTimeImplementationName="HLAinteger64Time",
        )
        owner_handle = owner.joinFederationExecution("DirectedTSOOwner", "Controller", federation_name)
        subscriber.joinFederationExecution("DirectedTSOSubscriber", "Observer", federation_name)
        observer.joinFederationExecution("DirectedTSOObserver", "Observer", federation_name)

        object_class = owner.getObjectClassHandle("HLAobjectRoot.Target")
        interaction_class = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        subscriber_interaction = subscriber.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        parameter = owner.getParameterHandle(interaction_class, "TrackId")
        subscriber_parameter = subscriber.getParameterHandle(subscriber_interaction, "TrackId")
        object_instance = owner.registerObjectInstance(object_class, "ShimDirectedTSORestoreTarget-1")

        owner.publishObjectClassDirectedInteractions(object_class, {interaction_class})
        subscriber.subscribeObjectClassDirectedInteractions(object_class, {subscriber_interaction})
        owner.enableTimeRegulation(HLAinteger64Interval(1))
        subscriber.enableTimeConstrained()
        observer.enableTimeConstrained()

        owner.requestFederationSave(save_label)
        for rti in (owner, subscriber, observer):
            rti.federateSaveBegun()
        for rti in (owner, subscriber, observer):
            rti.federateSaveComplete()

        stale = owner.sendDirectedInteraction(
            interaction_class,
            object_instance,
            {parameter: b"STALE"},
            b"stale-tso",
            HLAinteger64Time(5),
        )
        assert stale.retractionHandleIsValid is True

        owner.requestFederationRestore(save_label)
        for rti in (owner, subscriber, observer):
            rti.federateRestoreComplete()

        subscriber_federate.callbacks.clear()
        observer_federate.callbacks.clear()
        subscriber.nextMessageRequest(HLAinteger64Time(5))
        observer.nextMessageRequest(HLAinteger64Time(5))
        assert _callbacks_named_2025(subscriber_federate, "receiveDirectedInteraction") == []
        assert _callbacks_named_2025(observer_federate, "receiveDirectedInteraction") == []

        with pytest.raises(InvalidMessageRetractionHandle):
            owner.retract(stale.handle)

        owner.sendDirectedInteraction(
            interaction_class,
            object_instance,
            {parameter: b"FRESH"},
            b"fresh-tso",
        )

        fresh_receive = subscriber_federate.last_callback("receiveDirectedInteraction")
        assert fresh_receive is not None
        assert fresh_receive[:6] == (
            subscriber_interaction,
            object_instance,
            {subscriber_parameter: b"FRESH"},
            b"fresh-tso",
            owner.getTransportationTypeHandle("HLAreliable"),
            owner_handle,
        )
        assert fresh_receive[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)
        assert observer_federate.last_callback("receiveDirectedInteraction") is None
    finally:
        for rti in (observer, subscriber, owner):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            owner.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (observer, subscriber, owner):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_proves_time_window_core_progression() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.exceptions import InvalidLogicalTime
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-time-window-core-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    fast_federate = Recording2025FederateAmbassador()
    slow_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")
    fast = create_rti_ambassador(backend="shim")
    slow = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
            (fast, fast_federate),
            (slow, slow_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
            (fast, "FastMover"),
            (slow, "SlowMover"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishInteractionClass(track_interaction)
        radar.subscribeInteractionClass(track_interaction)
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert truth_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        truth.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        truth.sendInteraction(
            track_interaction,
            {track_parameter: b"truth-105"},
            b"truth-105",
            HLAinteger64Time(105),
        )
        truth.sendInteraction(
            track_interaction,
            {track_parameter: b"sensor-106"},
            b"sensor-106",
            HLAinteger64Time(106),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(109))
        assert truth_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(109),)

        initial_galt = radar.queryGALT()
        initial_lits = radar.queryLITS()
        assert initial_galt.timeIsValid is True
        assert initial_lits.timeIsValid is True
        assert initial_galt.time == HLAinteger64Time(110)
        assert initial_lits.time == HLAinteger64Time(105)

        radar_receive_baseline = len(_callbacks_named_2025(radar_federate, "receiveInteraction"))
        radar_grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.nextMessageRequest(HLAinteger64Time(110))
        first_receive = _callbacks_named_2025(radar_federate, "receiveInteraction")[radar_receive_baseline:]
        first_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[radar_grant_baseline:]
        assert len(first_receive) == 1
        assert len(first_grant) == 1
        assert first_receive[0][2] == b"truth-105"
        assert first_receive[0][6] == HLAinteger64Time(105)
        assert first_grant[0] == (HLAinteger64Time(105),)

        radar_receive_baseline = len(_callbacks_named_2025(radar_federate, "receiveInteraction"))
        radar_grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.nextMessageRequest(HLAinteger64Time(110))
        second_receive = _callbacks_named_2025(radar_federate, "receiveInteraction")[radar_receive_baseline:]
        second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[radar_grant_baseline:]
        assert len(second_receive) == 1
        assert len(second_grant) == 1
        assert second_receive[0][2] == b"sensor-106"
        assert second_receive[0][6] == HLAinteger64Time(106)
        assert second_grant[0] == (HLAinteger64Time(106),)

        blocked_galt = radar.queryGALT()
        blocked_lits = radar.queryLITS()
        assert blocked_galt.timeIsValid is True
        assert blocked_lits.timeIsValid is True
        assert blocked_galt.time == HLAinteger64Time(110)
        assert blocked_lits.time == HLAinteger64Time(110)

        radar_grant_baseline = len(_callbacks_named_2025(radar_federate, "timeAdvanceGrant"))
        radar.nextMessageRequest(HLAinteger64Time(110))
        truth.timeAdvanceRequest(HLAinteger64Time(110))
        close_grants = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[radar_grant_baseline:]
        assert close_grants == [(HLAinteger64Time(110),)]
        assert truth_federate.last_callback("timeAdvanceGrant") == (HLAinteger64Time(110),)

        radar.enableTimeRegulation(HLAinteger64Interval(10))
        consumer.enableTimeConstrained()
        fast.enableTimeRegulation(HLAinteger64Interval(1))
        slow.enableTimeRegulation(HLAinteger64Interval(2))
        assert radar_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(110),)
        assert consumer_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)
        assert fast_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert slow_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)

        for illegal_time in (100, 105, 109):
            with pytest.raises(InvalidLogicalTime):
                truth.sendInteraction(
                    track_interaction,
                    {track_parameter: f"late-{illegal_time}".encode("ascii")},
                    f"late-{illegal_time}".encode("ascii"),
                    HLAinteger64Time(illegal_time),
                )

        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.timeAdvanceRequest(HLAinteger64Time(119))
        consumer.nextMessageRequest(HLAinteger64Time(140))
        fast.timeAdvanceRequest(HLAinteger64Time(160))
        slow.timeAdvanceRequest(HLAinteger64Time(118))
        assert truth.queryLogicalTime() == HLAinteger64Time(119)
        assert fast.queryLogicalTime() == HLAinteger64Time(160)
        assert slow.queryLogicalTime() == HLAinteger64Time(118)

        post_close_inputs = [
            int(callback[6].value)
            for callback in _callbacks_named_2025(radar_federate, "receiveInteraction")
            if callback[6] is not None
        ]
        assert all(timestamp >= 110 for timestamp in post_close_inputs)
    finally:
        for rti in (slow, fast, consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (slow, fast, consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_ignores_receive_order_poison_after_window_close() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-receive-order-poison-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert truth_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        target_object = truth.registerObjectInstance(target_class, "ReceiveOrderPoisonTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(110))

        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(110))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(110),)

        timestamped_reflections = [
            callback
            for callback in _callbacks_named_2025(radar_federate, "reflectAttributeValues")
            if callback[6] is not None and callback[6] < HLAinteger64Time(110)
        ]
        closed_window_tags_before = [callback[2] for callback in timestamped_reflections]
        assert closed_window_tags_before == [b"truth-105", b"truth-106"]

        truth.changeAttributeOrderType(target_object, {position}, OrderType.RECEIVE)
        radar_federate.callbacks.clear()
        truth.updateAttributeValues(target_object, {position: b"receive-order-poison"}, b"receive-order-poison")

        poison_reflection = radar_federate.last_callback("reflectAttributeValues")
        assert poison_reflection is not None
        assert poison_reflection[2] == b"receive-order-poison"
        assert poison_reflection[6:] == (None, OrderType.RECEIVE, OrderType.RECEIVE, None)

        closed_window_tags_after = [
            callback[2]
            for callback in _callbacks_named_2025(radar_federate, "reflectAttributeValues")
            if callback[6] is not None and callback[6] < HLAinteger64Time(110)
        ]
        assert closed_window_tags_after == []

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        assert radar_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(110),)
        assert consumer_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        truth.timeAdvanceRequest(HLAinteger64Time(120))
        consumer.nextMessageRequest(HLAinteger64Time(120))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-poison-safe"},
            b"radar-track-output",
            HLAinteger64Time(111),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(120))

        consumer_receive = _callbacks_named_2025(consumer_federate, "receiveInteraction")[-1]
        assert consumer_receive[2] == b"radar-track-output"
        assert consumer_receive[1] == {track_parameter: b"track-poison-safe"}
        assert consumer_receive[6] == HLAinteger64Time(111)
        assert closed_window_tags_before == [b"truth-105", b"truth-106"]
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_delivers_post_closure_timestamped_output_to_consumer() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-output-delivery-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        truth.connect(truth_federate, CallbackModel.HLA_EVOKED)
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        consumer.connect(consumer_federate, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        assert truth_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(0),)
        assert radar_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        target_object = truth.registerObjectInstance(target_class, "OutputTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(120))

        radar.nextMessageRequest(HLAinteger64Time(110))
        first_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        first_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert first_reflect[2] == b"truth-105"
        assert first_reflect[6] == HLAinteger64Time(105)
        assert first_grant == (HLAinteger64Time(105),)

        radar.nextMessageRequest(HLAinteger64Time(110))
        second_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert second_reflect[2] == b"truth-106"
        assert second_reflect[6] == HLAinteger64Time(106)
        assert second_grant == (HLAinteger64Time(106),)

        radar.nextMessageRequest(HLAinteger64Time(110))
        window_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert window_close_grant == (HLAinteger64Time(110),)
        assert _callbacks_named_2025(consumer_federate, "receiveInteraction") == []

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        assert radar_federate.last_callback("timeRegulationEnabled") == (HLAinteger64Time(110),)
        assert consumer_federate.last_callback("timeConstrainedEnabled") == (HLAinteger64Time(0),)

        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        consumer.nextMessageRequest(HLAinteger64Time(120))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-100-110[from truth-105,truth-106]"},
            b"radar-track-output",
            HLAinteger64Time(111),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(120))

        consumer_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(consumer_receives) == 1
        consumer_receive = consumer_receives[-1]
        assert consumer_receive[2] == b"radar-track-output"
        assert consumer_receive[6] == HLAinteger64Time(111)
        assert consumer_receive[1] == {track_parameter: b"track-100-110[from truth-105,truth-106]"}

        consumer.nextMessageRequest(HLAinteger64Time(130))
        truth.timeAdvanceRequest(HLAinteger64Time(130))
        radar.timeAdvanceRequest(HLAinteger64Time(130))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 1
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_preserves_consumer_timestamp_order_between_competing_output_and_radar_output() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-consumer-order-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    other_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    other = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (other, other_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (other, "Other"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        other.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, "ConsumerOrderTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(120))

        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(110))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(110),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        other.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)
        other.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)

        consumer.nextMessageRequest(HLAinteger64Time(120))
        other.sendInteraction(
            track_interaction,
            {track_parameter: b"other-track-110[gate]"},
            b"other-track-output",
            HLAinteger64Time(110),
        )
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"radar-track-111[from truth-105,truth-106]"},
            b"radar-track-output",
            HLAinteger64Time(111),
        )
        other.timeAdvanceRequest(HLAinteger64Time(120))
        radar.timeAdvanceRequest(HLAinteger64Time(120))
        consumer.nextMessageRequest(HLAinteger64Time(120))

        receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(receives) == 2
        assert [receive[2] for receive in receives] == [b"other-track-output", b"radar-track-output"]
        assert [receive[6] for receive in receives] == [HLAinteger64Time(110), HLAinteger64Time(111)]
        assert receives[0][1] == {track_parameter: b"other-track-110[gate]"}
        assert receives[1][1] == {track_parameter: b"radar-track-111[from truth-105,truth-106]"}

        consumer.nextMessageRequest(HLAinteger64Time(130))
        truth.timeAdvanceRequest(HLAinteger64Time(130))
        other.timeAdvanceRequest(HLAinteger64Time(130))
        radar.timeAdvanceRequest(HLAinteger64Time(130))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 2
    finally:
        for rti in (consumer, other, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, other, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_keeps_two_scan_pipeline_outputs_separated() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time

    federation_name = f"shim-2025-pipeline-{uuid.uuid4().hex[:8]}"
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        for rti, name in (
            (truth, "Truth"),
            (radar, "Radar"),
            (consumer, "Consumer"),
        ):
            rti.joinFederationExecution(
                federateName=name,
                federateType="TimeWindowFederate",
                federationName=federation_name,
            )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(target_class, {position})
        radar.publishInteractionClass(track_interaction)
        consumer.subscribeInteractionClass(track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, "PipelineTarget-1")
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)

        truth.updateAttributeValues(target_object, {position: b"scan1-input-a"}, b"scan1-input-a", HLAinteger64Time(105))
        truth.updateAttributeValues(target_object, {position: b"scan1-input-b"}, b"scan1-input-b", HLAinteger64Time(106))
        truth.timeAdvanceRequest(HLAinteger64Time(110))
        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(110))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(110),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(track_interaction, OrderType.TIMESTAMP)

        truth.updateAttributeValues(target_object, {position: b"scan2-input"}, b"scan2-input", HLAinteger64Time(112))
        truth.timeAdvanceRequest(HLAinteger64Time(130))
        radar.nextMessageRequest(HLAinteger64Time(120))
        scan2_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        assert scan2_reflect[2] == b"scan2-input"
        assert scan2_reflect[6] == HLAinteger64Time(112)

        consumer.nextMessageRequest(HLAinteger64Time(130))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-scan-1[from scan1-input-a,scan1-input-b]"},
            b"scan1-track-output",
            HLAinteger64Time(115),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(115))

        radar.nextMessageRequest(HLAinteger64Time(120))
        assert _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1] == (HLAinteger64Time(120),)

        consumer.nextMessageRequest(HLAinteger64Time(130))
        radar.sendInteraction(
            track_interaction,
            {track_parameter: b"track-scan-2[from scan2-input]"},
            b"scan2-track-output",
            HLAinteger64Time(122),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(130))

        receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(receives) == 2
        assert [receive[2] for receive in receives] == [b"scan1-track-output", b"scan2-track-output"]
        assert [receive[6] for receive in receives] == [HLAinteger64Time(115), HLAinteger64Time(122)]
        assert receives[0][1] == {track_parameter: b"track-scan-1[from scan1-input-a,scan1-input-b]"}
        assert receives[1][1] == {track_parameter: b"track-scan-2[from scan2-input]"}

        consumer.nextMessageRequest(HLAinteger64Time(140))
        truth.timeAdvanceRequest(HLAinteger64Time(140))
        radar.timeAdvanceRequest(HLAinteger64Time(140))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 2
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass
@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_restores_open_and_closed_time_window_state() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification import TargetRadarWindowRestoreConfig

    federation_name = f"shim-2025-window-restore-{uuid.uuid4().hex[:8]}"
    config = TargetRadarWindowRestoreConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")

    def snapshot_window_state(
        *,
        phase: str,
        window_closed: bool,
        closed_at: int | None,
        last_grant: int,
        received_tags: list[bytes],
    ) -> dict[str, object]:
        return {
            "phase": phase,
            "window_closed": window_closed,
            "closed_at": closed_at,
            "last_grant": last_grant,
            "received_tags": list(received_tags),
        }

    def complete_save(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        truth.requestFederationSave(save_label)
        assert truth_federate.last_callback("initiateFederateSave") == (save_label,)
        assert radar_federate.last_callback("initiateFederateSave") == (save_label,)
        truth.federateSaveBegun()
        radar.federateSaveBegun()
        truth.federateSaveComplete()
        radar.federateSaveComplete()
        assert truth_federate.last_callback("federationSaved") == ()
        assert radar_federate.last_callback("federationSaved") == ()

    def complete_restore(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        truth.requestFederationRestore(save_label)
        assert truth_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert truth_federate.last_callback("federationRestoreBegun") == ()
        assert radar_federate.last_callback("initiateFederateRestore") == (save_label, config.radar_name, radar_handle)
        truth.federateRestoreComplete()
        radar.federateRestoreComplete()
        assert truth_federate.last_callback("federationRestored") == ()
        assert radar_federate.last_callback("federationRestored") == ()

    try:
        truth.connect(truth_federate, CallbackModel.HLA_EVOKED)
        radar.connect(radar_federate, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        truth.joinFederationExecution(
            federateName=config.truth_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        radar_handle = radar.joinFederationExecution(
            federateName=config.radar_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        radar_target_class = radar.getObjectClassHandle("HLAobjectRoot.Target")
        radar_position = radar.getAttributeHandle(radar_target_class, "Position")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(radar_target_class, {radar_position})

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, config.target_object_name)
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)

        truth.updateAttributeValues(
            target_object,
            {position: b"truth-105"},
            b"truth-105",
            HLAinteger64Time(config.first_input_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.first_input_time))
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        first_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        first_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert first_reflect[2] == b"truth-105"
        assert first_grant == (HLAinteger64Time(config.first_input_time),)
        saved_open_state = snapshot_window_state(
            phase="open",
            window_closed=False,
            closed_at=None,
            last_grant=config.first_input_time,
            received_tags=[b"truth-105"],
        )

        complete_save(config.save_open_name)

        truth.updateAttributeValues(
            target_object,
            {position: b"truth-106"},
            b"truth-106",
            HLAinteger64Time(config.second_input_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan_window_end))
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        dirty_second_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        dirty_second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_second_reflect[2] == b"truth-106"
        assert dirty_second_grant == (HLAinteger64Time(config.second_input_time),)
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        dirty_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_close_grant == (HLAinteger64Time(config.scan_window_end),)

        complete_restore(config.save_open_name)
        assert truth.queryLogicalTime() == HLAinteger64Time(config.first_input_time)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.first_input_time)
        restored_open_state = snapshot_window_state(
            phase="open",
            window_closed=False,
            closed_at=None,
            last_grant=config.first_input_time,
            received_tags=[b"truth-105"],
        )
        assert restored_open_state == saved_open_state

        truth.updateAttributeValues(
            target_object,
            {position: b"truth-106-branch"},
            b"truth-106-branch",
            HLAinteger64Time(config.second_input_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan_window_end))
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        reclosed_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        reclosed_second_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert reclosed_reflect[2] == b"truth-106-branch"
        assert reclosed_second_grant == (HLAinteger64Time(config.second_input_time),)
        radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        reclosed_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert reclosed_grant == (HLAinteger64Time(config.scan_window_end),)
        saved_closed_state = snapshot_window_state(
            phase="closed",
            window_closed=True,
            closed_at=config.scan_window_end,
            last_grant=config.scan_window_end,
            received_tags=[b"truth-105", b"truth-106-branch"],
        )

        complete_save(config.save_closed_name)

        truth.updateAttributeValues(
            target_object,
            {position: b"dirty-post-close"},
            b"dirty-post-close",
            HLAinteger64Time(config.post_close_resume_time),
        )
        truth.timeAdvanceRequest(HLAinteger64Time(config.post_close_resume_time))
        radar.nextMessageRequest(HLAinteger64Time(config.post_close_resume_time))
        dirty_post_close_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        dirty_post_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_post_close_reflect[2] == b"dirty-post-close"
        assert dirty_post_close_grant == (HLAinteger64Time(config.post_close_resume_time),)

        complete_restore(config.save_closed_name)
        assert truth.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        restored_closed_state = snapshot_window_state(
            phase="closed",
            window_closed=True,
            closed_at=config.scan_window_end,
            last_grant=config.scan_window_end,
            received_tags=[b"truth-105", b"truth-106-branch"],
        )
        assert restored_closed_state == saved_closed_state

        radar_federate.callbacks.clear()
        truth.timeAdvanceRequest(HLAinteger64Time(config.post_close_resume_time))
        radar.nextMessageRequest(HLAinteger64Time(config.post_close_resume_time))
        assert _callbacks_named_2025(radar_federate, "reflectAttributeValues") == []
    finally:
        for rti in (radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_restores_closed_window_output_resume_without_dirty_replay() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification import TargetRadarWindowRestoreOutputConfig

    federation_name = f"shim-2025-window-restore-output-{uuid.uuid4().hex[:8]}"
    config = TargetRadarWindowRestoreOutputConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    def complete_save(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationSave(save_label)
        assert truth_federate.last_callback("initiateFederateSave") == (save_label,)
        assert radar_federate.last_callback("initiateFederateSave") == (save_label,)
        assert consumer_federate.last_callback("initiateFederateSave") == (save_label,)
        truth.federateSaveBegun()
        radar.federateSaveBegun()
        consumer.federateSaveBegun()
        truth.federateSaveComplete()
        radar.federateSaveComplete()
        consumer.federateSaveComplete()
        assert truth_federate.last_callback("federationSaved") == ()
        assert radar_federate.last_callback("federationSaved") == ()
        assert consumer_federate.last_callback("federationSaved") == ()

    def complete_restore(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationRestore(save_label)
        assert truth_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert radar_federate.last_callback("initiateFederateRestore") == (save_label, config.radar_name, radar_handle)
        assert consumer_federate.last_callback("initiateFederateRestore") == (save_label, config.consumer_name, consumer_handle)
        truth.federateRestoreComplete()
        radar.federateRestoreComplete()
        consumer.federateRestoreComplete()
        assert truth_federate.last_callback("federationRestored") == ()
        assert radar_federate.last_callback("federationRestored") == ()
        assert consumer_federate.last_callback("federationRestored") == ()

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        truth.joinFederationExecution(
            federateName=config.truth_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        radar_handle = radar.joinFederationExecution(
            federateName=config.radar_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        consumer_handle = consumer.joinFederationExecution(
            federateName=config.consumer_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        radar_target_class = radar.getObjectClassHandle("HLAobjectRoot.Target")
        radar_position = radar.getAttributeHandle(radar_target_class, "Position")
        radar_track_interaction = radar.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        radar_track_parameter = radar.getParameterHandle(radar_track_interaction, "TrackId")
        consumer_track_interaction = consumer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        consumer_track_parameter = consumer.getParameterHandle(consumer_track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(radar_target_class, {radar_position})
        radar.publishInteractionClass(radar_track_interaction)
        consumer.subscribeInteractionClass(consumer_track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, config.target_object_name)
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"truth-105"}, b"truth-105", HLAinteger64Time(config.first_input_time))
        truth.updateAttributeValues(target_object, {position: b"truth-106"}, b"truth-106", HLAinteger64Time(config.second_input_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan_window_end))

        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        window_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert window_close_grant == (HLAinteger64Time(config.scan_window_end),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(radar_track_interaction, OrderType.TIMESTAMP)
        consumer.nextMessageRequest(HLAinteger64Time(config.scan_window_end))
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)

        complete_save(config.save_closed_name)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.resume_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: b"dirty-track-100-110"},
            b"dirty-track-output",
            HLAinteger64Time(config.radar_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        dirty_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(dirty_receives) == 1
        assert dirty_receives[-1][2] == b"dirty-track-output"
        assert dirty_receives[-1][6] == HLAinteger64Time(config.radar_output_time)
        assert dirty_receives[-1][1] == {consumer_track_parameter: b"dirty-track-100-110"}

        complete_restore(config.save_closed_name)
        assert truth.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan_window_end)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.resume_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: b"restored-track-100-110"},
            b"restored-track-output",
            HLAinteger64Time(config.radar_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.resume_time))
        post_restore_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert len(post_restore_receives) == 1
        assert post_restore_receives[-1][2] == b"restored-track-output"
        assert post_restore_receives[-1][6] == HLAinteger64Time(config.radar_output_time)
        assert post_restore_receives[-1][1] == {consumer_track_parameter: b"restored-track-100-110"}
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-MIL-004", "HLA2025-MIL-005", "HLA2025-MIL-006")
def test_2025_shim_restores_pipeline_resume_without_cross_window_replay() -> None:
    from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAinteger64Interval, HLAinteger64Time
    from hla.verification import TargetRadarPipelineRestoreConfig

    federation_name = f"shim-2025-pipeline-restore-{uuid.uuid4().hex[:8]}"
    config = TargetRadarPipelineRestoreConfig(
        federation_name=federation_name,
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    truth_federate = Recording2025FederateAmbassador()
    radar_federate = Recording2025FederateAmbassador()
    consumer_federate = Recording2025FederateAmbassador()
    truth = create_rti_ambassador(backend="shim")
    radar = create_rti_ambassador(backend="shim")
    consumer = create_rti_ambassador(backend="shim")

    def complete_save(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationSave(save_label)
        assert truth_federate.last_callback("initiateFederateSave") == (save_label,)
        assert radar_federate.last_callback("initiateFederateSave") == (save_label,)
        assert consumer_federate.last_callback("initiateFederateSave") == (save_label,)
        truth.federateSaveBegun()
        radar.federateSaveBegun()
        consumer.federateSaveBegun()
        truth.federateSaveComplete()
        radar.federateSaveComplete()
        consumer.federateSaveComplete()
        assert truth_federate.last_callback("federationSaved") == ()
        assert radar_federate.last_callback("federationSaved") == ()
        assert consumer_federate.last_callback("federationSaved") == ()

    def complete_restore(save_label: str) -> None:
        truth_federate.callbacks.clear()
        radar_federate.callbacks.clear()
        consumer_federate.callbacks.clear()
        truth.requestFederationRestore(save_label)
        assert truth_federate.last_callback("requestFederationRestoreSucceeded") == (save_label,)
        assert radar_federate.last_callback("initiateFederateRestore") == (save_label, config.radar_name, radar_handle)
        assert consumer_federate.last_callback("initiateFederateRestore") == (save_label, config.consumer_name, consumer_handle)
        truth.federateRestoreComplete()
        radar.federateRestoreComplete()
        consumer.federateRestoreComplete()
        assert truth_federate.last_callback("federationRestored") == ()
        assert radar_federate.last_callback("federationRestored") == ()
        assert consumer_federate.last_callback("federationRestored") == ()

    try:
        for rti, fed in (
            (truth, truth_federate),
            (radar, radar_federate),
            (consumer, consumer_federate),
        ):
            rti.connect(fed, CallbackModel.HLA_EVOKED)
        truth.createFederationExecution(
            federationName=federation_name,
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="HLAinteger64Time",
        )
        truth.joinFederationExecution(
            federateName=config.truth_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        radar_handle = radar.joinFederationExecution(
            federateName=config.radar_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )
        consumer_handle = consumer.joinFederationExecution(
            federateName=config.consumer_name,
            federateType=config.federate_type,
            federationName=federation_name,
        )

        target_class = truth.getObjectClassHandle("HLAobjectRoot.Target")
        position = truth.getAttributeHandle(target_class, "Position")
        track_interaction = truth.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        track_parameter = truth.getParameterHandle(track_interaction, "TrackId")
        radar_target_class = radar.getObjectClassHandle("HLAobjectRoot.Target")
        radar_position = radar.getAttributeHandle(radar_target_class, "Position")
        radar_track_interaction = radar.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        radar_track_parameter = radar.getParameterHandle(radar_track_interaction, "TrackId")
        consumer_track_interaction = consumer.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
        consumer_track_parameter = consumer.getParameterHandle(consumer_track_interaction, "TrackId")
        truth.publishObjectClassAttributes(target_class, {position})
        radar.subscribeObjectClassAttributes(radar_target_class, {radar_position})
        radar.publishInteractionClass(radar_track_interaction)
        consumer.subscribeInteractionClass(consumer_track_interaction)

        truth.enableTimeRegulation(HLAinteger64Interval(1))
        radar.enableTimeConstrained()
        target_object = truth.registerObjectInstance(target_class, config.target_object_name)
        truth.changeAttributeOrderType(target_object, {position}, OrderType.TIMESTAMP)
        truth.updateAttributeValues(target_object, {position: b"scan1-input-a"}, b"scan1-input-a", HLAinteger64Time(config.scan1_input_a_time))
        truth.updateAttributeValues(target_object, {position: b"scan1-input-b"}, b"scan1-input-b", HLAinteger64Time(config.scan1_input_b_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.scan1_end))
        for _ in range(3):
            radar.nextMessageRequest(HLAinteger64Time(config.scan1_end))
        scan1_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert scan1_close_grant == (HLAinteger64Time(config.scan1_end),)

        radar.enableTimeRegulation(HLAinteger64Interval(1))
        consumer.enableTimeConstrained()
        radar.changeInteractionOrderType(radar_track_interaction, OrderType.TIMESTAMP)
        consumer.nextMessageRequest(HLAinteger64Time(config.scan1_end))
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan1_end)

        truth.updateAttributeValues(target_object, {position: b"scan2-input"}, b"scan2-input", HLAinteger64Time(config.scan2_input_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.nextMessageRequest(HLAinteger64Time(config.scan2_end))
        scan2_reflect = _callbacks_named_2025(radar_federate, "reflectAttributeValues")[-1]
        scan2_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert scan2_reflect[2] == b"scan2-input"
        assert scan2_grant == (HLAinteger64Time(config.scan2_input_time),)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan2_input_time)

        complete_save(config.save_name)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.dirty_scan1_track_id.encode("utf-8")},
            b"dirty-scan1-track-output",
            HLAinteger64Time(config.scan1_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.scan1_output_time))
        radar.nextMessageRequest(HLAinteger64Time(config.scan2_end))
        dirty_scan2_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert dirty_scan2_close_grant == (HLAinteger64Time(config.scan2_end),)
        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.dirty_scan2_track_id.encode("utf-8")},
            b"dirty-scan2-track-output",
            HLAinteger64Time(config.scan2_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.consumer_resume_time))
        dirty_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert [record[2] for record in dirty_receives] == [
            b"dirty-scan1-track-output",
            b"dirty-scan2-track-output",
        ]

        complete_restore(config.save_name)
        assert radar.queryLogicalTime() == HLAinteger64Time(config.scan2_input_time)
        assert consumer.queryLogicalTime() == HLAinteger64Time(config.scan1_end)

        consumer_federate.callbacks.clear()
        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.restored_scan1_track_id.encode("utf-8")},
            b"restored-scan1-track-output",
            HLAinteger64Time(config.scan1_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.scan1_output_time))

        radar_federate.callbacks.clear()
        radar.nextMessageRequest(HLAinteger64Time(config.scan2_end))
        post_restore_scan2_reflects = _callbacks_named_2025(radar_federate, "reflectAttributeValues")
        restored_scan2_close_grant = _callbacks_named_2025(radar_federate, "timeAdvanceGrant")[-1]
        assert post_restore_scan2_reflects == []
        assert restored_scan2_close_grant == (HLAinteger64Time(config.scan2_end),)

        consumer.nextMessageRequest(HLAinteger64Time(config.consumer_resume_time))
        radar.sendInteraction(
            radar_track_interaction,
            {radar_track_parameter: config.restored_scan2_track_id.encode("utf-8")},
            b"restored-scan2-track-output",
            HLAinteger64Time(config.scan2_output_time),
        )
        radar.timeAdvanceRequest(HLAinteger64Time(config.consumer_resume_time))
        restored_receives = _callbacks_named_2025(consumer_federate, "receiveInteraction")
        assert [record[2] for record in restored_receives] == [
            b"restored-scan1-track-output",
            b"restored-scan2-track-output",
        ]
        assert restored_receives[0][1] == {consumer_track_parameter: config.restored_scan1_track_id.encode("utf-8")}
        assert restored_receives[1][1] == {consumer_track_parameter: config.restored_scan2_track_id.encode("utf-8")}

        consumer.nextMessageRequest(HLAinteger64Time(config.duplicate_check_resume_time))
        truth.timeAdvanceRequest(HLAinteger64Time(config.duplicate_check_resume_time))
        radar.timeAdvanceRequest(HLAinteger64Time(config.duplicate_check_resume_time))
        assert len(_callbacks_named_2025(consumer_federate, "receiveInteraction")) == 2
    finally:
        for rti in (consumer, radar, truth):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except Exception:
                pass
        try:
            truth.destroyFederationExecution(federationName=federation_name)
        except Exception:
            pass
        for rti in (consumer, radar, truth):
            try:
                rti.disconnect()
            except Exception:
                pass


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_2010_and_2025_backend_selection_do_not_cross_wire() -> None:
    from hla.rti import create_rti_ambassador

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        create_rti_ambassador(spec="2025", backend="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        create_rti_ambassador(spec="rti1516e", backend="shim")
