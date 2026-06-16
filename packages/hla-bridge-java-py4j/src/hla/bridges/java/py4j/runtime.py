"""Runtime and bridge helpers for Py4J-backed Java RTI backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from hla.rti1516e.fom import module_uri
from hla.bridges.java.common import CALLBACK_METHOD_NAMES, BackendUnavailableError
from hla.rti1516e.datatypes import RangeBounds
from hla.bridges.java.common.java_common import JavaBridge, PythonFederateAmbassadorDispatcher


@dataclass(frozen=True)
class Py4JConfig:
    """Configuration for a Java RTI accessed through Py4J."""

    gateway: Any | None = None
    gateway_parameters: Mapping[str, Any] = field(default_factory=dict)
    callback_server_parameters: Mapping[str, Any] = field(default_factory=dict)
    rti_factory_name: str | None = None
    connect_local_settings_designator: str | None = None
    shutdown_gateway_on_close: bool = False


class Py4JFederateAmbassadorProxy:
    """Py4J callback object implementing hla.rti1516e.FederateAmbassador."""

    class Java:
        implements = ["hla.rti1516e.FederateAmbassador"]

    def __init__(self, dispatcher: PythonFederateAmbassadorDispatcher):
        self._dispatcher = dispatcher

    def _invoke(self, method_name: str, *args: Any) -> Any:
        return self._dispatcher._invoke_callback(method_name, *args)


    def connectionLost(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("connectionLost", *args)

    def reportFederationExecutions(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("reportFederationExecutions", *args)

    def synchronizationPointRegistrationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("synchronizationPointRegistrationSucceeded", *args)

    def synchronizationPointRegistrationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("synchronizationPointRegistrationFailed", *args)

    def announceSynchronizationPoint(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("announceSynchronizationPoint", *args)

    def federationSynchronized(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationSynchronized", *args)

    def initiateFederateSave(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("initiateFederateSave", *args)

    def federationSaved(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationSaved", *args)

    def federationNotSaved(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationNotSaved", *args)

    def federationSaveStatusResponse(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationSaveStatusResponse", *args)

    def requestFederationRestoreSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("requestFederationRestoreSucceeded", *args)

    def requestFederationRestoreFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("requestFederationRestoreFailed", *args)

    def federationRestoreBegun(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationRestoreBegun", *args)

    def initiateFederateRestore(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("initiateFederateRestore", *args)

    def federationRestored(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationRestored", *args)

    def federationNotRestored(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationNotRestored", *args)

    def federationRestoreStatusResponse(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("federationRestoreStatusResponse", *args)

    def startRegistrationForObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("startRegistrationForObjectClass", *args)

    def stopRegistrationForObjectClass(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("stopRegistrationForObjectClass", *args)

    def turnInteractionsOn(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("turnInteractionsOn", *args)

    def turnInteractionsOff(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("turnInteractionsOff", *args)

    def objectInstanceNameReservationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("objectInstanceNameReservationSucceeded", *args)

    def objectInstanceNameReservationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("objectInstanceNameReservationFailed", *args)

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("multipleObjectInstanceNameReservationSucceeded", *args)

    def multipleObjectInstanceNameReservationFailed(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("multipleObjectInstanceNameReservationFailed", *args)

    def discoverObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("discoverObjectInstance", *args)

    def hasProducingFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("hasProducingFederate", *args)

    def hasSentRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("hasSentRegions", *args)

    def getProducingFederate(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("getProducingFederate", *args)

    def getSentRegions(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("getSentRegions", *args)

    def reflectAttributeValues(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("reflectAttributeValues", *args)

    def receiveInteraction(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("receiveInteraction", *args)

    def removeObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("removeObjectInstance", *args)

    def attributesInScope(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("attributesInScope", *args)

    def attributesOutOfScope(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("attributesOutOfScope", *args)

    def provideAttributeValueUpdate(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("provideAttributeValueUpdate", *args)

    def turnUpdatesOnForObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("turnUpdatesOnForObjectInstance", *args)

    def turnUpdatesOffForObjectInstance(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("turnUpdatesOffForObjectInstance", *args)

    def confirmAttributeTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("confirmAttributeTransportationTypeChange", *args)

    def reportAttributeTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("reportAttributeTransportationType", *args)

    def confirmInteractionTransportationTypeChange(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("confirmInteractionTransportationTypeChange", *args)

    def reportInteractionTransportationType(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("reportInteractionTransportationType", *args)

    def requestAttributeOwnershipAssumption(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("requestAttributeOwnershipAssumption", *args)

    def requestDivestitureConfirmation(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("requestDivestitureConfirmation", *args)

    def attributeOwnershipAcquisitionNotification(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("attributeOwnershipAcquisitionNotification", *args)

    def attributeOwnershipUnavailable(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("attributeOwnershipUnavailable", *args)

    def requestAttributeOwnershipRelease(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("requestAttributeOwnershipRelease", *args)

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("confirmAttributeOwnershipAcquisitionCancellation", *args)

    def informAttributeOwnership(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("informAttributeOwnership", *args)

    def attributeIsNotOwned(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("attributeIsNotOwned", *args)

    def attributeIsOwnedByRTI(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("attributeIsOwnedByRTI", *args)

    def timeRegulationEnabled(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("timeRegulationEnabled", *args)

    def timeConstrainedEnabled(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("timeConstrainedEnabled", *args)

    def timeAdvanceGrant(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("timeAdvanceGrant", *args)

    def requestRetraction(self, *args: Any) -> Any:  # noqa: N802
        return self._invoke("requestRetraction", *args)


class Py4JBridge(JavaBridge):
    name = "py4j"

    def __init__(self, config: Py4JConfig = Py4JConfig()):
        self.config = config
        self.owns_gateway = False

        if config.gateway is not None:
            self.gateway = config.gateway
            return

        try:
            from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise BackendUnavailableError("Py4J backend requested, but py4j is not installed") from exc

        gateway_parameters = GatewayParameters(**dict(config.gateway_parameters))
        callback_parameters = CallbackServerParameters(**dict(config.callback_server_parameters))
        self.gateway = JavaGateway(
            gateway_parameters=gateway_parameters,
            callback_server_parameters=callback_parameters,
        )
        self.owns_gateway = True

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: PythonFederateAmbassadorDispatcher) -> Any:
        return Py4JFederateAmbassadorProxy(dispatcher)

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        current = self.gateway.jvm
        for part in enum_class_name.split("."):
            current = getattr(current, part)
        return getattr(current, member_name)

    def byte_array(self, data: bytes) -> Any:
        try:
            byte_type = self.gateway.jvm.Byte.TYPE
            arr = self.gateway.new_array(byte_type, len(data))
            for idx, item in enumerate(data):
                arr[idx] = item if item < 128 else item - 256
            return arr
        except Exception:
            return bytearray(data)

    def new_set(self, values: list[Any] | tuple[Any, ...]) -> Any:
        java_set = self.gateway.jvm.java.util.HashSet()
        for value in values:
            java_set.add(value)
        return java_set

    def new_list(self, values: list[Any] | tuple[Any, ...]) -> Any:
        java_list = self.gateway.jvm.java.util.ArrayList()
        for value in values:
            java_list.add(value)
        return java_list

    def new_map(self, items: list[tuple[Any, Any]] | tuple[tuple[Any, Any], ...]) -> Any:
        java_map = self.gateway.jvm.java.util.HashMap()
        for key, value in items:
            java_map.put(key, value)
        return java_map

    def fom_url(self, value: Any) -> Any:
        uri = module_uri(value)
        return self.gateway.jvm.java.net.URI(uri).toURL()

    def fom_url_array(self, values: list[Any] | tuple[Any, ...]) -> Any:
        URL = self.gateway.jvm.java.net.URL
        arr = self.gateway.new_array(URL, len(values))
        for idx, value in enumerate(values):
            arr[idx] = self.fom_url(value)
        return arr

    def _factory_collection(
        self,
        rti_ambassador: Any,
        factory_method: str,
        values: list[Any] | tuple[Any, ...],
        *,
        capacity: int | None = None,
    ) -> Any:
        factory = getattr(rti_ambassador, factory_method)()
        collection = factory.create(len(values)) if capacity is not None else factory.create()
        for value in values:
            add = getattr(collection, "add", None)
            if callable(add):
                add(value)
            else:
                collection.append(value)
        return collection

    def new_handle_set(self, type_name: str, values: list[Any] | tuple[Any, ...], *, rti_ambassador: Any | None = None) -> Any:
        methods = {
            "AttributeHandleSet": "getAttributeHandleSetFactory",
            "DimensionHandleSet": "getDimensionHandleSetFactory",
            "FederateHandleSet": "getFederateHandleSetFactory",
            "RegionHandleSet": "getRegionHandleSetFactory",
        }
        if rti_ambassador is not None and type_name in methods:
            try:
                return self._factory_collection(rti_ambassador, methods[type_name], values)
            except Exception:
                pass
        return self.new_set(values)

    def new_handle_value_map(
        self,
        type_name: str,
        items: list[tuple[Any, Any]] | tuple[tuple[Any, Any], ...],
        *,
        rti_ambassador: Any | None = None,
    ) -> Any:
        methods = {
            "AttributeHandleValueMap": "getAttributeHandleValueMapFactory",
            "ParameterHandleValueMap": "getParameterHandleValueMapFactory",
        }
        if rti_ambassador is not None and type_name in methods:
            try:
                factory = getattr(rti_ambassador, methods[type_name])()
                java_map = factory.create(len(items))
                for key, value in items:
                    java_map.put(key, value)
                return java_map
            except Exception:
                pass
        return self.new_map(items)

    def new_attribute_set_region_set_pair_list(self, values: list[Any] | tuple[Any, ...], *, rti_ambassador: Any | None = None) -> Any:
        if rti_ambassador is not None:
            try:
                return self._factory_collection(rti_ambassador, "getAttributeSetRegionSetPairListFactory", values, capacity=len(values))
            except Exception:
                pass
        return self.new_list(values)

    def logical_time(self, value: Any, *, rti_ambassador: Any | None = None) -> Any:
        try:
            from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time

            if rti_ambassador is not None:
                try:
                    factory = rti_ambassador.getTimeFactory()
                    if isinstance(value, (HLAinteger64Time, HLAfloat64Time)) and hasattr(factory, "makeTime"):
                        raw = int(value.value) if isinstance(value, HLAinteger64Time) else float(value.value)
                        return factory.makeTime(raw)
                    if isinstance(value, (HLAinteger64Interval, HLAfloat64Interval)) and hasattr(factory, "makeInterval"):
                        raw = int(value.value) if isinstance(value, HLAinteger64Interval) else float(value.value)
                        return factory.makeInterval(raw)
                    if isinstance(value, (HLAinteger64Interval, HLAfloat64Interval)) and getattr(value, "is_zero")():
                        return factory.makeZero()
                    if isinstance(value, (HLAinteger64Interval, HLAfloat64Interval)) and getattr(value, "is_epsilon")():
                        return factory.makeEpsilon()
                except Exception:
                    pass
            if isinstance(value, HLAinteger64Time):
                return self.gateway.jvm.hla.rti1516e.HLAinteger64Time(int(value.value))
            if isinstance(value, HLAinteger64Interval):
                return self.gateway.jvm.hla.rti1516e.HLAinteger64Interval(int(value.value))
            if isinstance(value, HLAfloat64Time):
                return self.gateway.jvm.hla.rti1516e.HLAfloat64Time(float(value.value))
            if isinstance(value, HLAfloat64Interval):
                return self.gateway.jvm.hla.rti1516e.HLAfloat64Interval(float(value.value))
        except Exception:
            return value
        return value

    def range_bounds(self, value: RangeBounds) -> Any:
        try:
            return self.gateway.jvm.hla.rti1516e.RangeBounds(int(value.lower_bound), int(value.upper_bound))
        except Exception:
            return value

    def full_class_name(self, obj: Any) -> str | None:
        if obj is None:
            return None
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getName())
            except Exception:
                pass
        return super().full_class_name(obj)

    def simple_class_name(self, obj: Any) -> str | None:
        if obj is None:
            return None
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getSimpleName())
            except Exception:
                pass
        return super().simple_class_name(obj)

    def exception_class_name(self, exc: BaseException) -> str | None:
        java_exception = getattr(exc, "java_exception", None)
        if java_exception is not None:
            try:
                return str(java_exception.getClass().getSimpleName())
            except Exception:
                pass
        return super().exception_class_name(exc)

    def exception_message(self, exc: BaseException) -> str:
        java_exception = getattr(exc, "java_exception", None)
        if java_exception is not None:
            try:
                return str(java_exception.getMessage())
            except Exception:
                pass
        return str(exc)

    def close(self) -> None:
        if not self.config.shutdown_gateway_on_close:
            return
        shutdown_callback_server = getattr(self.gateway, "shutdown_callback_server", None)
        if callable(shutdown_callback_server):
            shutdown_callback_server()
        shutdown = getattr(self.gateway, "shutdown", None)
        if callable(shutdown):
            shutdown()


__all__ = ["Py4JBridge", "Py4JConfig", "Py4JFederateAmbassadorProxy"]
