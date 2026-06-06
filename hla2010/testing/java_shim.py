"""In-process Java-shaped RTI shim used by tests and examples.

The shim does not try to be a full RTI.  It provides a small Java-looking object
model that exercises the same adapter path used for real Java backends:

* Python federate code calls :class:`hla2010.backends.base.DelegatingRTIAmbassador`.
* The call is converted by :class:`hla2010.backends.java_common.JavaValueConverter`.
* A bridge named either ``jpype`` or ``py4j`` invokes lowerCamelCase Java methods.
* Java-looking handles/enums/maps/byte arrays are converted back to Python.
* Java-looking FederateAmbassador callbacks are dispatched into Python.

This lets the project prove backend neutrality in CI even when JPype/Py4J or a
vendor RTI are not installed.  The separate ``java_shims`` directory contains a
real Java version of the same tiny RTI for optional integration smoke tests.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Deque, Iterable, Mapping

from ..backends.base import BackendInfo, make_rti_ambassador
from ..backends.java_common import JavaBridge, JavaRTIBackend
from ..enums import CallbackModel, OrderType, ResignAction
from ..exceptions import RTIinternalError
from ..time import HLAinteger64Interval, HLAinteger64Time


class JavaClassInfo:
    """Tiny stand-in for ``java.lang.Class``."""

    def __init__(self, simple_name: str, package: str = "hla.rti1516e") -> None:
        self._simple_name = simple_name
        self._package = package

    def getSimpleName(self) -> str:
        return self._simple_name

    def getName(self) -> str:
        if self._simple_name == "byte[]":
            return "[B"
        return f"{self._package}.{self._simple_name}"


@dataclass(eq=False)
class JavaLikeObject:
    """Base class for Java-looking values passed through the bridge."""

    simple_name: str
    value: Any = None

    def getClass(self) -> JavaClassInfo:
        return JavaClassInfo(self.simple_name)

    def getValue(self) -> Any:
        return self.value

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{self.simple_name}({self.value!r})"


class JavaLikeException(RuntimeError):
    """Exception object whose class name looks like a Java RTI exception."""

    def __init__(self, simple_name: str, message: str):
        super().__init__(message)
        self.simple_name = simple_name
        self.message = message

    def getClass(self) -> JavaClassInfo:
        return JavaClassInfo(self.simple_name, package="hla.rti1516e.exceptions")

    def getMessage(self) -> str:
        return self.message


class JavaEnumConstant(JavaLikeObject):
    def __init__(self, enum_simple_name: str, member_name: str):
        super().__init__(enum_simple_name, member_name)
        self._member_name = member_name

    def name(self) -> str:
        return self._member_name

    def __repr__(self) -> str:
        return f"{self.simple_name}.{self._member_name}"


class JavaByteArray(JavaLikeObject):
    def __init__(self, data: bytes):
        super().__init__("byte[]", bytes(data))

    def __iter__(self):
        for item in self.value:
            # Java bytes are signed, so expose signed values to exercise the
            # bridge conversion path.
            yield item if item < 128 else item - 256

    def __len__(self) -> int:
        return len(self.value)


class JavaFederateHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("FederateHandle", value)


class JavaObjectClassHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("ObjectClassHandle", value)


class JavaAttributeHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("AttributeHandle", value)


class JavaObjectInstanceHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("ObjectInstanceHandle", value)


class JavaInteractionClassHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("InteractionClassHandle", value)


class JavaParameterHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("ParameterHandle", value)


class JavaDimensionHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("DimensionHandle", value)


class JavaRegionHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("RegionHandle", value)


class JavaTransportationTypeHandle(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("TransportationTypeHandle", value)


class JavaHLAinteger64Time(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("HLAinteger64Time", int(value))


class JavaHLAinteger64Interval(JavaLikeObject):
    def __init__(self, value: int):
        super().__init__("HLAinteger64Interval", int(value))


def _enum_name(value: Any) -> str:
    if isinstance(value, Enum):
        return value.name
    if hasattr(value, "name") and callable(value.name):
        return str(value.name())
    if isinstance(value, JavaLikeObject):
        return str(value.value)
    return str(value)


def _python_bytes(value: Any) -> bytes:
    if isinstance(value, JavaByteArray):
        return bytes((int(item) + 256) % 256 for item in value)
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    try:
        return bytes((int(item) + 256) % 256 for item in value)
    except Exception:
        return bytes(str(value), "utf-8")


def _time_value(value: Any) -> int:
    if isinstance(value, HLAinteger64Time):
        return int(value.value)
    if isinstance(value, JavaHLAinteger64Time):
        return int(value.value)
    if hasattr(value, "getValue"):
        return int(value.getValue())
    return int(value)


class InProcessJavaRTIShim:
    """Small stateful RTIambassador implemented with Java-shaped Python objects."""

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
        self.federations: set[str] = set()
        self.time_regulation_enabled = False
        self.time_constrained_enabled = False
        self.current_time = 0

    def _alloc(self) -> int:
        value = self._next_handle
        self._next_handle += 1
        return value

    def _require_connected(self) -> None:
        if not self.connected:
            raise JavaLikeException("NotConnected", "RTI shim is not connected")

    def _require_joined(self) -> None:
        self._require_connected()
        if self.federate_handle is None:
            raise JavaLikeException("FederateNotExecutionMember", "Federate has not joined a federation")

    def _queue_callback(self, method_name: str, *args: Any) -> None:
        def callback() -> None:
            getattr(self.federate, method_name)(*args)

        self._queue.append(callback)

    # Federation management -------------------------------------------------
    def connect(self, federateReference: Any, callbackModel: Any, localSettingsDesignator: str | None = None) -> None:
        if self.connected:
            raise JavaLikeException("AlreadyConnected", "RTI shim is already connected")
        self.federate = federateReference
        self.callback_model = callbackModel
        self.local_settings_designator = localSettingsDesignator
        self.connected = True

    def disconnect(self) -> None:
        if self.federate_handle is not None:
            raise JavaLikeException("FederateIsExecutionMember", "Resign before disconnecting")
        self.connected = False
        self.federate = None

    def createFederationExecution(self, federationExecutionName: str, *unused: Any) -> None:
        self._require_connected()
        if federationExecutionName in self.federations:
            raise JavaLikeException("FederationExecutionAlreadyExists", federationExecutionName)
        self.federations.add(federationExecutionName)

    def destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        if self.federate_handle is not None and self.federation_name == federationExecutionName:
            raise JavaLikeException("FederatesCurrentlyJoined", federationExecutionName)
        if federationExecutionName not in self.federations:
            raise JavaLikeException("FederationExecutionDoesNotExist", federationExecutionName)
        self.federations.remove(federationExecutionName)

    def joinFederationExecution(self, *args: Any) -> JavaFederateHandle:
        self._require_connected()
        if self.federate_handle is not None:
            raise JavaLikeException("FederateAlreadyExecutionMember", "Already joined")
        if len(args) == 2:
            federate_name = f"federate-{self._next_handle}"
            federate_type, federation_name = args
        elif len(args) >= 3:
            federate_name, federate_type, federation_name = args[:3]
        else:
            raise JavaLikeException("RTIinternalError", f"Bad joinFederationExecution args: {args!r}")
        if federation_name not in self.federations:
            raise JavaLikeException("FederationExecutionDoesNotExist", str(federation_name))
        self.federation_name = str(federation_name)
        self.federate_name = str(federate_name)
        self.federate_type = str(federate_type)
        self.federate_handle = JavaFederateHandle(self._alloc())
        return self.federate_handle

    def resignFederationExecution(self, resignAction: Any) -> None:
        self._require_joined()
        # The shim accepts all enum values and just clears membership.
        _enum_name(resignAction)
        self.federate_handle = None
        self.federation_name = None
        self.federate_name = None
        self.federate_type = None

    # Declaration management ------------------------------------------------
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

    # Object management -----------------------------------------------------
    def registerObjectInstance(self, theClass: JavaObjectClassHandle, theObjectName: str | None = None) -> JavaObjectInstanceHandle:
        self._require_joined()
        if theObjectName is None:
            theObjectName = f"Object-{self._next_handle}"
        if theObjectName in self.object_names:
            raise JavaLikeException("ObjectInstanceNameInUse", theObjectName)
        handle = JavaObjectInstanceHandle(self._alloc())
        self.objects[handle] = (theClass, str(theObjectName))
        self.object_names[str(theObjectName)] = handle
        # Queue a self-discovery so the federate callback path is exercised.
        self._queue_callback("discoverObjectInstance", handle, theClass, str(theObjectName))
        return handle

    def updateAttributeValues(self, theObject: JavaObjectInstanceHandle, theAttributes: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        self._require_joined()
        if theObject not in self.objects:
            raise JavaLikeException("ObjectInstanceNotKnown", repr(theObject))
        the_class, _ = self.objects[theObject]
        if the_class in self.subscribed_objects:
            self._queue_callback(
                "reflectAttributeValues",
                theObject,
                dict(theAttributes),
                JavaByteArray(_python_bytes(userSuppliedTag)),
                JavaEnumConstant("OrderType", "RECEIVE"),
                self.transportation_reliable,
                JavaLikeObject("SupplementalReflectInfo", None),
            )

    def sendInteraction(self, theInteraction: JavaInteractionClassHandle, theParameters: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        self._require_joined()
        if theInteraction in self.subscribed_interactions:
            self._queue_callback(
                "receiveInteraction",
                theInteraction,
                dict(theParameters),
                JavaByteArray(_python_bytes(userSuppliedTag)),
                JavaEnumConstant("OrderType", "RECEIVE"),
                self.transportation_reliable,
                JavaLikeObject("SupplementalReceiveInfo", None),
            )

    # Time management -------------------------------------------------------
    def enableTimeRegulation(self, theLookahead: Any) -> None:
        self._require_joined()
        self.time_regulation_enabled = True
        self._queue_callback("timeRegulationEnabled", JavaHLAinteger64Time(self.current_time))

    def enableTimeConstrained(self) -> None:
        self._require_joined()
        self.time_constrained_enabled = True
        self._queue_callback("timeConstrainedEnabled", JavaHLAinteger64Time(self.current_time))

    def timeAdvanceRequest(self, theTime: Any) -> None:
        self._require_joined()
        self.current_time = _time_value(theTime)
        self._queue_callback("timeAdvanceGrant", JavaHLAinteger64Time(self.current_time))

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        if not self._queue:
            return False
        self._queue.popleft()()
        return bool(self._queue)

    def evokeMultipleCallbacks(self, approximateMinimumTimeInSeconds: float, approximateMaximumTimeInSeconds: float) -> bool:
        while self._queue:
            self._queue.popleft()()
        return False

    def enableAsynchronousDelivery(self) -> None:
        self._require_joined()

    def disableAsynchronousDelivery(self) -> None:
        self._require_joined()

    # Data distribution management -----------------------------------------
    def createRegion(self, dimensions: Iterable[JavaDimensionHandle]) -> JavaRegionHandle:
        self._require_joined()
        handle = JavaRegionHandle(self._alloc())
        self.regions[handle] = set(dimensions)
        return handle

    def commitRegionModifications(self, regions: Iterable[JavaRegionHandle]) -> None:
        self._require_joined()
        for region in regions:
            if region not in self.regions:
                raise JavaLikeException("InvalidRegion", repr(region))

    def deleteRegion(self, theRegion: JavaRegionHandle) -> None:
        self._require_joined()
        self.regions.pop(theRegion, None)

    # Support services ------------------------------------------------------
    def getFederateName(self, theHandle: JavaFederateHandle) -> str:
        self._require_joined()
        if self.federate_handle is theHandle:
            return self.federate_name or ""
        raise JavaLikeException("FederateHandleNotKnown", repr(theHandle))

    def getFederateHandle(self, theName: str) -> JavaFederateHandle:
        self._require_joined()
        if theName == self.federate_name and self.federate_handle is not None:
            return self.federate_handle
        raise JavaLikeException("NameNotFound", theName)

    def getObjectClassHandle(self, theName: str) -> JavaObjectClassHandle:
        self._require_joined()
        if theName not in self.object_classes:
            handle = JavaObjectClassHandle(self._alloc())
            self.object_classes[theName] = handle
            self.object_class_names[handle] = theName
        return self.object_classes[theName]

    def getObjectClassName(self, theHandle: JavaObjectClassHandle) -> str:
        self._require_joined()
        try:
            return self.object_class_names[theHandle]
        except KeyError as exc:
            raise JavaLikeException("InvalidObjectClassHandle", repr(theHandle)) from exc

    def getAttributeHandle(self, whichClass: JavaObjectClassHandle, theName: str) -> JavaAttributeHandle:
        self._require_joined()
        key = (whichClass, theName)
        if key not in self.attributes:
            handle = JavaAttributeHandle(self._alloc())
            self.attributes[key] = handle
            self.attribute_names[(whichClass, handle)] = theName
        return self.attributes[key]

    def getAttributeName(self, whichClass: JavaObjectClassHandle, theHandle: JavaAttributeHandle) -> str:
        self._require_joined()
        try:
            return self.attribute_names[(whichClass, theHandle)]
        except KeyError as exc:
            raise JavaLikeException("AttributeNotDefined", repr(theHandle)) from exc

    def getInteractionClassHandle(self, theName: str) -> JavaInteractionClassHandle:
        self._require_joined()
        if theName not in self.interaction_classes:
            handle = JavaInteractionClassHandle(self._alloc())
            self.interaction_classes[theName] = handle
            self.interaction_class_names[handle] = theName
        return self.interaction_classes[theName]

    def getInteractionClassName(self, theHandle: JavaInteractionClassHandle) -> str:
        self._require_joined()
        try:
            return self.interaction_class_names[theHandle]
        except KeyError as exc:
            raise JavaLikeException("InvalidInteractionClassHandle", repr(theHandle)) from exc

    def getParameterHandle(self, whichClass: JavaInteractionClassHandle, theName: str) -> JavaParameterHandle:
        self._require_joined()
        key = (whichClass, theName)
        if key not in self.parameters:
            handle = JavaParameterHandle(self._alloc())
            self.parameters[key] = handle
            self.parameter_names[(whichClass, handle)] = theName
        return self.parameters[key]

    def getParameterName(self, whichClass: JavaInteractionClassHandle, theHandle: JavaParameterHandle) -> str:
        self._require_joined()
        try:
            return self.parameter_names[(whichClass, theHandle)]
        except KeyError as exc:
            raise JavaLikeException("InteractionParameterNotDefined", repr(theHandle)) from exc

    def getObjectInstanceHandle(self, theName: str) -> JavaObjectInstanceHandle:
        self._require_joined()
        try:
            return self.object_names[theName]
        except KeyError as exc:
            raise JavaLikeException("ObjectInstanceNotKnown", theName) from exc

    def getObjectInstanceName(self, theHandle: JavaObjectInstanceHandle) -> str:
        self._require_joined()
        try:
            return self.objects[theHandle][1]
        except KeyError as exc:
            raise JavaLikeException("ObjectInstanceNotKnown", repr(theHandle)) from exc

    def getKnownObjectClassHandle(self, theObject: JavaObjectInstanceHandle) -> JavaObjectClassHandle:
        self._require_joined()
        try:
            return self.objects[theObject][0]
        except KeyError as exc:
            raise JavaLikeException("ObjectInstanceNotKnown", repr(theObject)) from exc

    def getDimensionHandle(self, theName: str) -> JavaDimensionHandle:
        self._require_joined()
        if theName not in self.dimensions:
            handle = JavaDimensionHandle(self._alloc())
            self.dimensions[theName] = handle
            self.dimension_names[handle] = theName
        return self.dimensions[theName]

    def getDimensionName(self, theHandle: JavaDimensionHandle) -> str:
        self._require_joined()
        try:
            return self.dimension_names[theHandle]
        except KeyError as exc:
            raise JavaLikeException("InvalidDimensionHandle", repr(theHandle)) from exc

    def getHLAversion(self) -> str:
        return "HLA 1516-2010 shim"


class ShimJavaBridge(JavaBridge):
    """JavaBridge that invokes the in-process shim with a JPype/Py4J profile name."""

    def __init__(self, profile: str = "jpype") -> None:
        if profile not in {"jpype", "py4j"}:
            raise ValueError("profile must be 'jpype' or 'py4j'")
        self.profile = profile
        self.name = f"{profile}-shim"

    def call(self, obj: Any, method_name: str, *args: Any) -> Any:
        return getattr(obj, method_name)(*args)

    def create_federate_proxy(self, dispatcher: Any) -> Any:
        # Real JPype/Py4J wrap the dispatcher differently.  For the shim, the
        # dispatcher already exposes lowerCamelCase FederateAmbassador methods.
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

    def simple_class_name(self, obj: Any) -> str | None:
        if isinstance(obj, JavaLikeObject):
            return obj.simple_name
        get_class = getattr(obj, "getClass", None)
        if callable(get_class):
            try:
                return str(get_class().getSimpleName())
            except Exception:
                pass
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


def create_java_shim_backend(profile: str = "jpype") -> JavaRTIBackend:
    """Create a JavaRTIBackend backed by the in-process Java-shaped shim."""

    bridge = ShimJavaBridge(profile)
    info = BackendInfo(
        name=f"inprocess-{profile}-java-shim",
        kind=f"java/{profile}/shim",
        version="0.5",
        details={"profile": profile, "implementation": "Python Java-shaped RTI shim"},
    )
    return JavaRTIBackend(java_rti_ambassador=InProcessJavaRTIShim(), bridge=bridge, info=info)


def create_java_shim_rti_ambassador(profile: str = "jpype"):
    """Create a DelegatingRTIAmbassador using the in-process Java shim."""

    return make_rti_ambassador(create_java_shim_backend(profile))


__all__ = [
    "InProcessJavaRTIShim",
    "JavaLikeObject",
    "JavaLikeException",
    "ShimJavaBridge",
    "create_java_shim_backend",
    "create_java_shim_rti_ambassador",
]

# Shared multi-federate Java-shaped shim -------------------------------------
# The original InProcessJavaRTIShim above is intentionally tiny and useful for
# one-ambassador adapter tests.  The shared shim below lets two or more JavaRTI
# backends participate in one local federation, which exercises the same
# application code as a vendor Java RTI accessed through JPype/Py4J.

@dataclass
class SharedJavaObjectRecord:
    handle: JavaObjectInstanceHandle
    class_handle: JavaObjectClassHandle
    name: str
    owner: "SharedInProcessJavaRTIShim"
    attributes: dict[JavaAttributeHandle, JavaByteArray] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.attributes is None:
            self.attributes = {}


@dataclass
class SharedJavaFederationRecord:
    name: str
    federates_by_handle: dict[JavaFederateHandle, "SharedInProcessJavaRTIShim"] = None  # type: ignore[assignment]
    federate_names: dict[str, JavaFederateHandle] = None  # type: ignore[assignment]
    objects: dict[JavaObjectInstanceHandle, SharedJavaObjectRecord] = None  # type: ignore[assignment]
    object_names: dict[str, JavaObjectInstanceHandle] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.federates_by_handle is None:
            self.federates_by_handle = {}
        if self.federate_names is None:
            self.federate_names = {}
        if self.objects is None:
            self.objects = {}
        if self.object_names is None:
            self.object_names = {}


class SharedJavaShimKernel:
    """Shared state for multi-federate Java-shaped shim ambassadors."""

    def __init__(self) -> None:
        self._next_handle = 1
        self.transportation_reliable = JavaTransportationTypeHandle(self._alloc_value())
        self.federations: dict[str, SharedJavaFederationRecord] = {}
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

    def _alloc_value(self) -> int:
        value = self._next_handle
        self._next_handle += 1
        return value

    def alloc(self, handle_type: Any) -> Any:
        return handle_type(self._alloc_value())


class SharedInProcessJavaRTIShim:
    """Multi-federate Java-looking RTIambassador implemented in Python."""

    def __init__(self, kernel: SharedJavaShimKernel | None = None) -> None:
        self.kernel = kernel or SharedJavaShimKernel()
        self.connected = False
        self.federate = None
        self.callback_model = None
        self.local_settings_designator = None
        self.federation_name: str | None = None
        self.federate_name: str | None = None
        self.federate_type: str | None = None
        self.federate_handle: JavaFederateHandle | None = None
        self._queue: Deque[Callable[[], None]] = deque()
        self.published_objects: dict[JavaObjectClassHandle, set[JavaAttributeHandle]] = {}
        self.subscribed_objects: dict[JavaObjectClassHandle, set[JavaAttributeHandle]] = {}
        self.published_interactions: set[JavaInteractionClassHandle] = set()
        self.subscribed_interactions: set[JavaInteractionClassHandle] = set()
        self.time_regulation_enabled = False
        self.time_constrained_enabled = False
        self.current_time = 0

    @property
    def transportation_reliable(self) -> JavaTransportationTypeHandle:
        return self.kernel.transportation_reliable

    def _require_connected(self) -> None:
        if not self.connected:
            raise JavaLikeException("NotConnected", "RTI shim is not connected")

    def _federation(self) -> SharedJavaFederationRecord:
        self._require_connected()
        if self.federation_name is None or self.federate_handle is None:
            raise JavaLikeException("FederateNotExecutionMember", "Federate has not joined a federation")
        try:
            return self.kernel.federations[self.federation_name]
        except KeyError as exc:
            raise JavaLikeException("FederationExecutionDoesNotExist", self.federation_name) from exc

    def _queue_callback(self, method_name: str, *args: Any) -> None:
        def callback() -> None:
            getattr(self.federate, method_name)(*args)

        self._queue.append(callback)

    def _tag(self, value: Any) -> JavaByteArray:
        return JavaByteArray(_python_bytes(value))

    # Federation management -------------------------------------------------
    def connect(self, federateReference: Any, callbackModel: Any, localSettingsDesignator: str | None = None) -> None:
        if self.connected:
            raise JavaLikeException("AlreadyConnected", "RTI shim is already connected")
        self.federate = federateReference
        self.callback_model = callbackModel
        self.local_settings_designator = localSettingsDesignator
        self.connected = True

    def disconnect(self) -> None:
        if self.federate_handle is not None:
            raise JavaLikeException("FederateIsExecutionMember", "Resign before disconnecting")
        self.connected = False
        self.federate = None

    def createFederationExecution(self, federationExecutionName: str, *unused: Any) -> None:
        self._require_connected()
        name = str(federationExecutionName)
        if name in self.kernel.federations:
            raise JavaLikeException("FederationExecutionAlreadyExists", name)
        self.kernel.federations[name] = SharedJavaFederationRecord(name=name)

    def destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        name = str(federationExecutionName)
        federation = self.kernel.federations.get(name)
        if federation is None:
            raise JavaLikeException("FederationExecutionDoesNotExist", name)
        if federation.federates_by_handle:
            raise JavaLikeException("FederatesCurrentlyJoined", name)
        del self.kernel.federations[name]

    def joinFederationExecution(self, *args: Any) -> JavaFederateHandle:
        self._require_connected()
        if self.federate_handle is not None:
            raise JavaLikeException("FederateAlreadyExecutionMember", "Already joined")
        if len(args) == 2:
            federate_name = f"federate-{self.kernel._next_handle}"
            federate_type, federation_name = args
        elif len(args) >= 3:
            federate_name, federate_type, federation_name = args[:3]
        else:
            raise JavaLikeException("RTIinternalError", f"Bad joinFederationExecution args: {args!r}")
        federation = self.kernel.federations.get(str(federation_name))
        if federation is None:
            raise JavaLikeException("FederationExecutionDoesNotExist", str(federation_name))
        if str(federate_name) in federation.federate_names:
            raise JavaLikeException("FederateNameAlreadyInUse", str(federate_name))
        handle = self.kernel.alloc(JavaFederateHandle)
        self.federate_handle = handle
        self.federation_name = str(federation_name)
        self.federate_name = str(federate_name)
        self.federate_type = str(federate_type)
        federation.federates_by_handle[handle] = self
        federation.federate_names[str(federate_name)] = handle
        return handle

    def resignFederationExecution(self, resignAction: Any) -> None:
        federation = self._federation()
        if self.federate_handle is not None:
            federation.federates_by_handle.pop(self.federate_handle, None)
        if self.federate_name is not None:
            federation.federate_names.pop(self.federate_name, None)
        self.federate_handle = None
        self.federation_name = None
        self.federate_name = None
        self.federate_type = None
        self.published_objects.clear()
        self.subscribed_objects.clear()
        self.published_interactions.clear()
        self.subscribed_interactions.clear()

    # Declaration management ------------------------------------------------
    def publishObjectClassAttributes(self, theClass: JavaObjectClassHandle, attributeList: Iterable[Any]) -> None:
        self._federation()
        self.published_objects.setdefault(theClass, set()).update(set(attributeList))

    def subscribeObjectClassAttributes(self, theClass: JavaObjectClassHandle, attributeList: Iterable[Any], *unused: Any) -> None:
        federation = self._federation()
        self.subscribed_objects.setdefault(theClass, set()).update(set(attributeList))
        for record in federation.objects.values():
            if record.class_handle == theClass and record.owner is not self:
                self._queue_callback("discoverObjectInstance", record.handle, record.class_handle, record.name)

    def publishInteractionClass(self, theInteraction: JavaInteractionClassHandle) -> None:
        self._federation()
        self.published_interactions.add(theInteraction)

    def subscribeInteractionClass(self, theClass: JavaInteractionClassHandle) -> None:
        self._federation()
        self.subscribed_interactions.add(theClass)

    # Object management -----------------------------------------------------
    def registerObjectInstance(self, theClass: JavaObjectClassHandle, theObjectName: str | None = None) -> JavaObjectInstanceHandle:
        federation = self._federation()
        if theObjectName is None:
            theObjectName = f"Object-{self.kernel._next_handle}"
        if str(theObjectName) in federation.object_names:
            raise JavaLikeException("ObjectInstanceNameInUse", str(theObjectName))
        handle = self.kernel.alloc(JavaObjectInstanceHandle)
        record = SharedJavaObjectRecord(handle=handle, class_handle=theClass, name=str(theObjectName), owner=self)
        federation.objects[handle] = record
        federation.object_names[str(theObjectName)] = handle
        for federate in federation.federates_by_handle.values():
            if federate is not self and theClass in federate.subscribed_objects:
                federate._queue_callback("discoverObjectInstance", handle, theClass, str(theObjectName))
        return handle

    def updateAttributeValues(self, theObject: JavaObjectInstanceHandle, theAttributes: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        federation = self._federation()
        record = federation.objects.get(theObject)
        if record is None:
            raise JavaLikeException("ObjectInstanceNotKnown", repr(theObject))
        attrs = {key: JavaByteArray(_python_bytes(value)) for key, value in dict(theAttributes).items()}
        record.attributes.update(attrs)
        for federate in federation.federates_by_handle.values():
            if federate is self:
                continue
            subscribed = federate.subscribed_objects.get(record.class_handle, set())
            reflected = {key: value for key, value in attrs.items() if key in subscribed}
            if reflected:
                federate._queue_callback(
                    "reflectAttributeValues",
                    theObject,
                    reflected,
                    self._tag(userSuppliedTag),
                    JavaEnumConstant("OrderType", "RECEIVE"),
                    self.transportation_reliable,
                    JavaLikeObject("SupplementalReflectInfo", None),
                )

    def requestAttributeValueUpdate(self, target: Any, attributes: Iterable[Any], userSuppliedTag: Any) -> None:
        federation = self._federation()
        attrs = set(attributes)
        tag = self._tag(userSuppliedTag)

        def deliver(record: SharedJavaObjectRecord) -> None:
            record.owner._queue_callback("provideAttributeValueUpdate", record.handle, attrs, tag)

        if isinstance(target, JavaObjectInstanceHandle):
            record = federation.objects.get(target)
            if record is None:
                raise JavaLikeException("ObjectInstanceNotKnown", repr(target))
            deliver(record)
            return
        if isinstance(target, JavaObjectClassHandle):
            for record in federation.objects.values():
                if record.class_handle == target:
                    deliver(record)
            return
        raise JavaLikeException("ObjectInstanceNotKnown", repr(target))

    def sendInteraction(self, theInteraction: JavaInteractionClassHandle, theParameters: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        federation = self._federation()
        params = {key: JavaByteArray(_python_bytes(value)) for key, value in dict(theParameters).items()}
        for federate in federation.federates_by_handle.values():
            if federate is not self and theInteraction in federate.subscribed_interactions:
                federate._queue_callback(
                    "receiveInteraction",
                    theInteraction,
                    params,
                    self._tag(userSuppliedTag),
                    JavaEnumConstant("OrderType", "RECEIVE"),
                    self.transportation_reliable,
                    JavaLikeObject("SupplementalReceiveInfo", None),
                )

    # Time management -------------------------------------------------------
    def enableTimeRegulation(self, theLookahead: Any) -> None:
        self._federation()
        self.time_regulation_enabled = True
        self._queue_callback("timeRegulationEnabled", JavaHLAinteger64Time(self.current_time))

    def enableTimeConstrained(self) -> None:
        self._federation()
        self.time_constrained_enabled = True
        self._queue_callback("timeConstrainedEnabled", JavaHLAinteger64Time(self.current_time))

    def timeAdvanceRequest(self, theTime: Any) -> None:
        self._federation()
        self.current_time = _time_value(theTime)
        self._queue_callback("timeAdvanceGrant", JavaHLAinteger64Time(self.current_time))

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

    def enableAsynchronousDelivery(self) -> None:
        self._federation()

    def disableAsynchronousDelivery(self) -> None:
        self._federation()

    # Data distribution management -----------------------------------------
    def createRegion(self, dimensions: Iterable[JavaDimensionHandle]) -> JavaRegionHandle:
        self._federation()
        handle = self.kernel.alloc(JavaRegionHandle)
        self.kernel.regions[handle] = set(dimensions)
        return handle

    def commitRegionModifications(self, regions: Iterable[JavaRegionHandle]) -> None:
        self._federation()
        for region in regions:
            if region not in self.kernel.regions:
                raise JavaLikeException("InvalidRegion", repr(region))

    def deleteRegion(self, theRegion: JavaRegionHandle) -> None:
        self._federation()
        self.kernel.regions.pop(theRegion, None)

    # Support services ------------------------------------------------------
    def getFederateName(self, theHandle: JavaFederateHandle) -> str:
        federation = self._federation()
        federate = federation.federates_by_handle.get(theHandle)
        if federate is None or federate.federate_name is None:
            raise JavaLikeException("FederateHandleNotKnown", repr(theHandle))
        return federate.federate_name

    def getFederateHandle(self, theName: str) -> JavaFederateHandle:
        federation = self._federation()
        try:
            return federation.federate_names[str(theName)]
        except KeyError as exc:
            raise JavaLikeException("NameNotFound", str(theName)) from exc

    def getObjectClassHandle(self, theName: str) -> JavaObjectClassHandle:
        self._federation()
        if theName not in self.kernel.object_classes:
            handle = self.kernel.alloc(JavaObjectClassHandle)
            self.kernel.object_classes[str(theName)] = handle
            self.kernel.object_class_names[handle] = str(theName)
        return self.kernel.object_classes[str(theName)]

    def getObjectClassName(self, theHandle: JavaObjectClassHandle) -> str:
        self._federation()
        try:
            return self.kernel.object_class_names[theHandle]
        except KeyError as exc:
            raise JavaLikeException("InvalidObjectClassHandle", repr(theHandle)) from exc

    def getAttributeHandle(self, whichClass: JavaObjectClassHandle, theName: str) -> JavaAttributeHandle:
        self._federation()
        key = (whichClass, str(theName))
        if key not in self.kernel.attributes:
            handle = self.kernel.alloc(JavaAttributeHandle)
            self.kernel.attributes[key] = handle
            self.kernel.attribute_names[(whichClass, handle)] = str(theName)
        return self.kernel.attributes[key]

    def getAttributeName(self, whichClass: JavaObjectClassHandle, theHandle: JavaAttributeHandle) -> str:
        self._federation()
        try:
            return self.kernel.attribute_names[(whichClass, theHandle)]
        except KeyError as exc:
            raise JavaLikeException("AttributeNotDefined", repr(theHandle)) from exc

    def getInteractionClassHandle(self, theName: str) -> JavaInteractionClassHandle:
        self._federation()
        if theName not in self.kernel.interaction_classes:
            handle = self.kernel.alloc(JavaInteractionClassHandle)
            self.kernel.interaction_classes[str(theName)] = handle
            self.kernel.interaction_class_names[handle] = str(theName)
        return self.kernel.interaction_classes[str(theName)]

    def getInteractionClassName(self, theHandle: JavaInteractionClassHandle) -> str:
        self._federation()
        try:
            return self.kernel.interaction_class_names[theHandle]
        except KeyError as exc:
            raise JavaLikeException("InvalidInteractionClassHandle", repr(theHandle)) from exc

    def getParameterHandle(self, whichClass: JavaInteractionClassHandle, theName: str) -> JavaParameterHandle:
        self._federation()
        key = (whichClass, str(theName))
        if key not in self.kernel.parameters:
            handle = self.kernel.alloc(JavaParameterHandle)
            self.kernel.parameters[key] = handle
            self.kernel.parameter_names[(whichClass, handle)] = str(theName)
        return self.kernel.parameters[key]

    def getParameterName(self, whichClass: JavaInteractionClassHandle, theHandle: JavaParameterHandle) -> str:
        self._federation()
        try:
            return self.kernel.parameter_names[(whichClass, theHandle)]
        except KeyError as exc:
            raise JavaLikeException("InteractionParameterNotDefined", repr(theHandle)) from exc

    def getObjectInstanceHandle(self, theName: str) -> JavaObjectInstanceHandle:
        federation = self._federation()
        try:
            return federation.object_names[str(theName)]
        except KeyError as exc:
            raise JavaLikeException("ObjectInstanceNotKnown", str(theName)) from exc

    def getObjectInstanceName(self, theHandle: JavaObjectInstanceHandle) -> str:
        federation = self._federation()
        try:
            return federation.objects[theHandle].name
        except KeyError as exc:
            raise JavaLikeException("ObjectInstanceNotKnown", repr(theHandle)) from exc

    def getKnownObjectClassHandle(self, theObject: JavaObjectInstanceHandle) -> JavaObjectClassHandle:
        federation = self._federation()
        try:
            return federation.objects[theObject].class_handle
        except KeyError as exc:
            raise JavaLikeException("ObjectInstanceNotKnown", repr(theObject)) from exc

    def getDimensionHandle(self, theName: str) -> JavaDimensionHandle:
        self._federation()
        if theName not in self.kernel.dimensions:
            handle = self.kernel.alloc(JavaDimensionHandle)
            self.kernel.dimensions[str(theName)] = handle
            self.kernel.dimension_names[handle] = str(theName)
        return self.kernel.dimensions[str(theName)]

    def getDimensionName(self, theHandle: JavaDimensionHandle) -> str:
        self._federation()
        try:
            return self.kernel.dimension_names[theHandle]
        except KeyError as exc:
            raise JavaLikeException("InvalidDimensionHandle", repr(theHandle)) from exc

    def getHLAversion(self) -> str:
        return "HLA 1516-2010 shared Java-shaped shim"


def create_shared_java_shim_backend(profile: str = "jpype", kernel: SharedJavaShimKernel | None = None) -> JavaRTIBackend:
    """Create a JavaRTIBackend backed by the shared multi-federate shim."""

    bridge = ShimJavaBridge(profile)
    info = BackendInfo(
        name=f"shared-inprocess-{profile}-java-shim",
        kind=f"java/{profile}/shared-shim",
        version="0.6",
        details={"profile": profile, "implementation": "shared Python Java-shaped RTI shim"},
    )
    return JavaRTIBackend(java_rti_ambassador=SharedInProcessJavaRTIShim(kernel), bridge=bridge, info=info)


def create_shared_java_shim_rti_ambassador(profile: str = "jpype", kernel: SharedJavaShimKernel | None = None):
    """Create a DelegatingRTIAmbassador using the shared Java-shaped shim."""

    return make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))


__all__ += [
    "SharedJavaFederationRecord",
    "SharedJavaObjectRecord",
    "SharedJavaShimKernel",
    "SharedInProcessJavaRTIShim",
    "create_shared_java_shim_backend",
    "create_shared_java_shim_rti_ambassador",
]
