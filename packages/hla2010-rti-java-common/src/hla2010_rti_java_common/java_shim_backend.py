"""Single-ambassador Java-shaped shim backend and bridge."""

from __future__ import annotations

from collections import deque
from typing import Any, Callable, Deque, Iterable, Mapping

from .java_common import JavaBridge, invoke_java_federate_proxy_callback
from .java_shim_types import (
    JavaAttributeHandle,
    JavaByteArray,
    JavaDimensionHandle,
    JavaEnumConstant,
    JavaFederateHandle,
    JavaInteractionClassHandle,
    JavaLikeException,
    JavaLikeObject,
    JavaObjectClassHandle,
    JavaObjectInstanceHandle,
    JavaParameterHandle,
    JavaRangeBounds,
    JavaRegionHandle,
    JavaTransportationTypeHandle,
    make_java_time,
    python_bytes,
    time_value,
)


class InProcessJavaRTIShim:
    def __init__(self) -> None:
        self.connected = False
        self.federate = None
        self.federation_name: str | None = None
        self.federate_name: str | None = None
        self.federate_type: str | None = None
        self.federate_handle: JavaFederateHandle | None = None
        self._next_handle = 1
        self._queue: Deque[Callable[[], None]] = deque()
        self.transportation_reliable = JavaTransportationTypeHandle(self._alloc())
        self.object_classes: dict[str, JavaObjectClassHandle] = {}
        self.object_class_names: dict[JavaObjectClassHandle, str] = {}
        self.attributes: dict[tuple[JavaObjectClassHandle, str], JavaAttributeHandle] = {}
        self.attribute_names: dict[tuple[JavaObjectClassHandle, JavaAttributeHandle], str] = {}
        self.interaction_classes: dict[str, JavaInteractionClassHandle] = {}
        self.interaction_class_names: dict[JavaInteractionClassHandle, str] = {}
        self.parameters: dict[tuple[JavaInteractionClassHandle, str], JavaParameterHandle] = {}
        self.parameter_names: dict[tuple[JavaInteractionClassHandle, JavaParameterHandle], str] = {}
        self.dimensions: dict[str, JavaDimensionHandle] = {}
        self.dimension_names: dict[JavaDimensionHandle, str] = {}
        self.regions: dict[JavaRegionHandle, set[JavaDimensionHandle]] = {}
        self.objects: dict[JavaObjectInstanceHandle, tuple[JavaObjectClassHandle, str]] = {}
        self.object_names: dict[str, JavaObjectInstanceHandle] = {}
        self.published_objects: set[JavaObjectClassHandle] = set()
        self.subscribed_objects: set[JavaObjectClassHandle] = set()
        self.published_interactions: set[JavaInteractionClassHandle] = set()
        self.subscribed_interactions: set[JavaInteractionClassHandle] = set()
        self.time_regulation_enabled = False
        self.time_constrained_enabled = False
        self.logical_time_name = "HLAinteger64Time"
        self.current_time = 0

    def _alloc(self) -> int:
        value = self._next_handle
        self._next_handle += 1
        return value

    def _queue_callback(self, method_name: str, *args: Any) -> None:
        def callback() -> None:
            invoke_java_federate_proxy_callback(self.federate, method_name, *args)

        self._queue.append(callback)

    def _tag(self, value: Any) -> JavaByteArray:
        return JavaByteArray(python_bytes(value))

    def _require_connected(self) -> None:
        if not self.connected:
            raise JavaLikeException("NotConnected", "RTI shim is not connected")

    def _require_joined(self) -> None:
        self._require_connected()
        if self.federation_name is None or self.federate_handle is None:
            raise JavaLikeException("FederateNotExecutionMember", "Federate has not joined a federation")

    def connect(self, federateReference: Any, callbackModel: Any, localSettingsDesignator: str | None = None) -> None:
        if self.connected:
            raise JavaLikeException("AlreadyConnected", "RTI shim is already connected")
        self.federate = federateReference
        self.connected = True

    def disconnect(self) -> None:
        if self.federate_handle is not None:
            raise JavaLikeException("FederateIsExecutionMember", "Resign before disconnecting")
        self.connected = False
        self.federate = None

    def createFederationExecution(self, federationExecutionName: str, *unused: Any) -> None:
        self._require_connected()
        self.federation_name = str(federationExecutionName)

    def destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        name = str(federationExecutionName)
        if self.federation_name != name:
            raise JavaLikeException("FederationExecutionDoesNotExist", name)
        self.federation_name = None

    def joinFederationExecution(self, *args: Any) -> JavaFederateHandle:
        self._require_connected()
        if len(args) == 2:
            federate_name = f"federate-{self._next_handle}"
            federate_type, federation_name = args
        elif len(args) >= 3:
            federate_name, federate_type, federation_name = args[:3]
        else:
            raise JavaLikeException("RTIinternalError", f"Bad joinFederationExecution args: {args!r}")
        self.federation_name = str(federation_name)
        self.federate_name = str(federate_name)
        self.federate_type = str(federate_type)
        self.federate_handle = JavaFederateHandle(self._alloc())
        return self.federate_handle

    def resignFederationExecution(self, resignAction: Any) -> None:
        self.federate_handle = None
        self.federate_name = None
        self.federate_type = None
        self.published_objects.clear()
        self.subscribed_objects.clear()
        self.published_interactions.clear()
        self.subscribed_interactions.clear()

    def publishObjectClassAttributes(self, theClass: JavaObjectClassHandle, attributeList: Iterable[Any]) -> None:
        self._require_joined()
        self.published_objects.add(theClass)

    def subscribeObjectClassAttributes(self, theClass: JavaObjectClassHandle, attributeList: Iterable[Any], *unused: Any) -> None:
        self._require_joined()
        self.subscribed_objects.add(theClass)

    def publishInteractionClass(self, theInteraction: JavaInteractionClassHandle) -> None:
        self._require_joined()
        self.published_interactions.add(theInteraction)

    def subscribeInteractionClass(self, theClass: JavaInteractionClassHandle) -> None:
        self._require_joined()
        self.subscribed_interactions.add(theClass)

    def registerObjectInstance(self, theClass: JavaObjectClassHandle, theObjectName: str | None = None) -> JavaObjectInstanceHandle:
        self._require_joined()
        if theObjectName is None:
            theObjectName = f"Object-{self._next_handle}"
        handle = JavaObjectInstanceHandle(self._alloc())
        self.objects[handle] = (theClass, str(theObjectName))
        self.object_names[str(theObjectName)] = handle
        self._queue_callback("discoverObjectInstance", handle, theClass, str(theObjectName))
        return handle

    def updateAttributeValues(self, theObject: JavaObjectInstanceHandle, theAttributes: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        reflected = {key: JavaByteArray(python_bytes(value)) for key, value in dict(theAttributes).items()}
        self._queue_callback(
            "reflectAttributeValues",
            theObject,
            reflected,
            self._tag(userSuppliedTag),
            JavaEnumConstant("OrderType", "RECEIVE"),
            self.transportation_reliable,
            JavaLikeObject("SupplementalReflectInfo", None),
        )

    def sendInteraction(self, theInteraction: JavaInteractionClassHandle, theParameters: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        params = {key: JavaByteArray(python_bytes(value)) for key, value in dict(theParameters).items()}
        self._queue_callback(
            "receiveInteraction",
            theInteraction,
            params,
            self._tag(userSuppliedTag),
            JavaEnumConstant("OrderType", "RECEIVE"),
            self.transportation_reliable,
            JavaLikeObject("SupplementalReceiveInfo", None),
        )

    def enableTimeRegulation(self, theLookahead: Any) -> None:
        self.time_regulation_enabled = True
        self._queue_callback("timeRegulationEnabled", make_java_time(self.logical_time_name, self.current_time))

    def enableTimeConstrained(self) -> None:
        self.time_constrained_enabled = True
        self._queue_callback("timeConstrainedEnabled", make_java_time(self.logical_time_name, self.current_time))

    def timeAdvanceRequest(self, theTime: Any) -> None:
        self.current_time = time_value(theTime)
        self._queue_callback("timeAdvanceGrant", make_java_time(self.logical_time_name, self.current_time))

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        if not self._queue:
            return False
        self._queue.popleft()()
        return bool(self._queue)

    def evokeMultipleCallbacks(self, approximateMinimumTimeInSeconds: float, approximateMaximumTimeInSeconds: float) -> bool:
        delivered = False
        while self._queue:
            self._queue.popleft()()
            delivered = True
        return delivered

    def createRegion(self, dimensions: Iterable[JavaDimensionHandle]) -> JavaRegionHandle:
        handle = JavaRegionHandle(self._alloc())
        self.regions[handle] = set(dimensions)
        return handle

    def commitRegionModifications(self, regions: Iterable[JavaRegionHandle]) -> None:
        return None

    def deleteRegion(self, theRegion: JavaRegionHandle) -> None:
        self.regions.pop(theRegion, None)

    def getFederateName(self, theHandle: JavaFederateHandle) -> str:
        return self.federate_name or ""

    def getFederateHandle(self, theName: str) -> JavaFederateHandle:
        if self.federate_handle is None:
            raise JavaLikeException("FederateHandleNotKnown", str(theName))
        return self.federate_handle

    def getObjectClassHandle(self, theName: str) -> JavaObjectClassHandle:
        if theName not in self.object_classes:
            handle = JavaObjectClassHandle(self._alloc())
            self.object_classes[str(theName)] = handle
            self.object_class_names[handle] = str(theName)
        return self.object_classes[str(theName)]

    def getObjectClassName(self, theHandle: JavaObjectClassHandle) -> str:
        return self.object_class_names[theHandle]

    def getAttributeHandle(self, whichClass: JavaObjectClassHandle, theName: str) -> JavaAttributeHandle:
        key = (whichClass, str(theName))
        if key not in self.attributes:
            handle = JavaAttributeHandle(self._alloc())
            self.attributes[key] = handle
            self.attribute_names[(whichClass, handle)] = str(theName)
        return self.attributes[key]

    def getAttributeName(self, whichClass: JavaObjectClassHandle, theHandle: JavaAttributeHandle) -> str:
        return self.attribute_names[(whichClass, theHandle)]

    def getInteractionClassHandle(self, theName: str) -> JavaInteractionClassHandle:
        if theName not in self.interaction_classes:
            handle = JavaInteractionClassHandle(self._alloc())
            self.interaction_classes[str(theName)] = handle
            self.interaction_class_names[handle] = str(theName)
        return self.interaction_classes[str(theName)]

    def getInteractionClassName(self, theHandle: JavaInteractionClassHandle) -> str:
        return self.interaction_class_names[theHandle]

    def getParameterHandle(self, whichClass: JavaInteractionClassHandle, theName: str) -> JavaParameterHandle:
        key = (whichClass, str(theName))
        if key not in self.parameters:
            handle = JavaParameterHandle(self._alloc())
            self.parameters[key] = handle
            self.parameter_names[(whichClass, handle)] = str(theName)
        return self.parameters[key]

    def getParameterName(self, whichClass: JavaInteractionClassHandle, theHandle: JavaParameterHandle) -> str:
        return self.parameter_names[(whichClass, theHandle)]

    def getObjectInstanceHandle(self, theName: str) -> JavaObjectInstanceHandle:
        return self.object_names[str(theName)]

    def getObjectInstanceName(self, theHandle: JavaObjectInstanceHandle) -> str:
        return self.objects[theHandle][1]

    def getKnownObjectClassHandle(self, theObject: JavaObjectInstanceHandle) -> JavaObjectClassHandle:
        return self.objects[theObject][0]

    def getDimensionHandle(self, theName: str) -> JavaDimensionHandle:
        if theName not in self.dimensions:
            handle = JavaDimensionHandle(self._alloc())
            self.dimensions[str(theName)] = handle
            self.dimension_names[handle] = str(theName)
        return self.dimensions[str(theName)]

    def getDimensionName(self, theHandle: JavaDimensionHandle) -> str:
        return self.dimension_names[theHandle]

    def getHLAversion(self) -> str:
        return "HLA 1516-2010 shim"


class ShimJavaBridge(JavaBridge):
    def __init__(self, profile: str = "jpype") -> None:
        if profile not in {"jpype", "py4j"}:
            raise ValueError("profile must be 'jpype' or 'py4j'")
        self.profile = profile
        self.name = f"{profile}-shim"

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: Any) -> Any:
        return dispatcher

    def enum_constant(self, enum_class_name: str, member_name: str) -> Any:
        return JavaEnumConstant(enum_class_name.rsplit(".", 1)[-1], member_name)

    def byte_array(self, data: bytes) -> Any:
        return JavaByteArray(data)

    def is_byte_array(self, value: Any) -> bool:
        return isinstance(value, JavaByteArray) or super().is_byte_array(value)

    def to_python_bytes(self, value: Any) -> bytes:
        if isinstance(value, JavaByteArray):
            return bytes((int(item) + 256) % 256 for item in value)
        return super().to_python_bytes(value)

    def new_set(self, values: Iterable[Any]) -> set[Any]:
        return set(values)

    def new_map(self, items: Iterable[tuple[Any, Any]]) -> dict[Any, Any]:
        return dict(items)

    def range_bounds(self, value: Any) -> JavaRangeBounds:
        return JavaRangeBounds(value.lower_bound, value.upper_bound)

    def simple_class_name(self, obj: Any) -> str | None:
        if isinstance(obj, JavaLikeObject):
            return obj.simple_name
        return super().simple_class_name(obj)

    def full_class_name(self, obj: Any) -> str | None:
        if isinstance(obj, JavaLikeObject):
            return obj.getClass().getName()
        return super().full_class_name(obj)

    def exception_class_name(self, exc: BaseException) -> str | None:
        if isinstance(exc, JavaLikeException):
            return exc.simple_name
        return super().exception_class_name(exc)

    def exception_message(self, exc: BaseException) -> str:
        if isinstance(exc, JavaLikeException):
            return exc.getMessage()
        return super().exception_message(exc)


__all__ = ["InProcessJavaRTIShim", "ShimJavaBridge"]
