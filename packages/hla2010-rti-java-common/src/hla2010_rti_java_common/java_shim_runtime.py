"""In-process Java-shaped RTI shim implementation."""
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Any, Callable, Deque, Iterable, Mapping

from .java_shim_records import (
    SharedJavaFederationRecord,
    SharedJavaObjectRecord,
    SharedJavaPendingAcquisition,
    SharedJavaSynchronizationPoint,
)
from .java_common import invoke_java_federate_proxy_callback
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
    JavaRegionHandle,
    JavaTransportationTypeHandle,
    make_java_time,
    python_bytes,
    time_value,
)

if TYPE_CHECKING:
    from .java_shim_kernel import SharedJavaShimKernel


class SharedInProcessJavaRTIShim:
    def __init__(self, kernel: "SharedJavaShimKernel | None" = None) -> None:
        from .java_shim_kernel import SharedJavaShimKernel

        self.kernel = kernel or SharedJavaShimKernel()
        self.connected = False
        self.federate = None
        self.federation_name: str | None = None
        self.federate_name: str | None = None
        self.federate_type: str | None = None
        self.federate_handle: JavaFederateHandle | None = None
        self._queue: Deque[Callable[[], None]] = deque()
        self.published_objects: dict[JavaObjectClassHandle, set[JavaAttributeHandle]] = {}
        self.subscribed_objects: dict[JavaObjectClassHandle, set[JavaAttributeHandle]] = {}
        self.published_interactions: set[JavaInteractionClassHandle] = set()
        self.subscribed_interactions: set[JavaInteractionClassHandle] = set()
        self.attribute_order_overrides: dict[tuple[JavaObjectInstanceHandle, JavaAttributeHandle], str] = {}
        self.interaction_order_overrides: dict[JavaInteractionClassHandle, str] = {}
        self.time_regulation_enabled = False
        self.time_constrained_enabled = False
        self.logical_time_name = "HLAinteger64Time"
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
        return self.kernel.federations[self.federation_name]

    def _queue_callback(self, method_name: str, *args: Any) -> None:
        def callback() -> None:
            invoke_java_federate_proxy_callback(self.federate, method_name, *args)

        self._queue.append(callback)

    def _tag(self, value: Any) -> JavaByteArray:
        return JavaByteArray(python_bytes(value))

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
        name = str(federationExecutionName)
        logical_time_name = next(
            (
                str(value)
                for value in unused
                if str(value) in {"HLAinteger64Time", "HLAfloat64Time"}
            ),
            "HLAinteger64Time",
        )
        self.kernel.federations[name] = SharedJavaFederationRecord(
            name=name,
            logical_time_name=logical_time_name,
        )

    def destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        self.kernel.federations.pop(str(federationExecutionName), None)

    def joinFederationExecution(self, *args: Any) -> JavaFederateHandle:
        self._require_connected()
        if len(args) == 2:
            federate_name = f"federate-{self.kernel._next_handle}"
            federate_type, federation_name = args
        elif len(args) >= 3:
            federate_name, federate_type, federation_name = args[:3]
        else:
            raise JavaLikeException("RTIinternalError", f"Bad joinFederationExecution args: {args!r}")
        federation = self.kernel.federations[str(federation_name)]
        handle = self.kernel.alloc(JavaFederateHandle)
        self.federate_handle = handle
        self.federation_name = str(federation_name)
        self.federate_name = str(federate_name)
        self.federate_type = str(federate_type)
        self.logical_time_name = federation.logical_time_name
        self.current_time = 0.0 if self.logical_time_name == "HLAfloat64Time" else 0
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

    def registerFederationSynchronizationPoint(self, synchronizationPointLabel: str, userSuppliedTag: Any, *unused: Any) -> None:
        federation = self._federation()
        label = str(synchronizationPointLabel)
        tag = self._tag(userSuppliedTag)
        point = SharedJavaSynchronizationPoint(label=label, tag=tag)
        point.announced = set(federation.federates_by_handle)
        point.awaiting = set(federation.federates_by_handle)
        federation.synchronization_points[label] = point
        self._queue_callback("synchronizationPointRegistrationSucceeded", label)
        for federate in federation.federates_by_handle.values():
            federate._queue_callback("announceSynchronizationPoint", label, tag)

    def synchronizationPointAchieved(self, synchronizationPointLabel: str, successIndicator: bool = True) -> None:
        federation = self._federation()
        point = federation.synchronization_points[str(synchronizationPointLabel)]
        if self.federate_handle is None:
            raise JavaLikeException("FederateNotExecutionMember", str(synchronizationPointLabel))
        point.awaiting.discard(self.federate_handle)
        if not bool(successIndicator):
            point.failed.add(self.federate_handle)
        if not point.awaiting:
            failed = set(point.failed)
            for federate in federation.federates_by_handle.values():
                federate._queue_callback("federationSynchronized", str(synchronizationPointLabel), failed)
            federation.synchronization_points.pop(str(synchronizationPointLabel), None)

    def registerObjectInstance(self, theClass: JavaObjectClassHandle, theObjectName: str | None = None) -> JavaObjectInstanceHandle:
        federation = self._federation()
        if theObjectName is None:
            theObjectName = f"Object-{self.kernel._next_handle}"
        handle = self.kernel.alloc(JavaObjectInstanceHandle)
        record = SharedJavaObjectRecord(handle=handle, class_handle=theClass, name=str(theObjectName), owner=self)
        published_attrs = self.published_objects.get(theClass, set())
        for attr in published_attrs:
            record.attribute_owners[attr] = self.federate_handle
        federation.objects[handle] = record
        federation.object_names[str(theObjectName)] = handle
        for federate in federation.federates_by_handle.values():
            if federate is not self and theClass in federate.subscribed_objects:
                federate._queue_callback("discoverObjectInstance", handle, theClass, str(theObjectName))
        return handle

    def updateAttributeValues(self, theObject: JavaObjectInstanceHandle, theAttributes: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        federation = self._federation()
        record = federation.objects[theObject]
        attrs = {key: JavaByteArray(python_bytes(value)) for key, value in dict(theAttributes).items()}
        timestamp = unused[0] if unused else None
        for federate in federation.federates_by_handle.values():
            if federate is self:
                continue
            subscribed = federate.subscribed_objects.get(record.class_handle, set())
            reflected = {key: value for key, value in attrs.items() if key in subscribed}
            if reflected:
                if timestamp is not None and self.time_regulation_enabled and federate.time_constrained_enabled:
                    federate._queue_callback(
                        "reflectAttributeValues",
                        theObject,
                        reflected,
                        self._tag(userSuppliedTag),
                        JavaEnumConstant("OrderType", "TIMESTAMP"),
                        self.transportation_reliable,
                        make_java_time(federation.logical_time_name, time_value(timestamp)),
                        JavaEnumConstant("OrderType", "TIMESTAMP"),
                    )
                else:
                    federate._queue_callback(
                        "reflectAttributeValues",
                        theObject,
                        reflected,
                        self._tag(userSuppliedTag),
                        JavaEnumConstant("OrderType", "RECEIVE"),
                        self.transportation_reliable,
                        JavaLikeObject("SupplementalReflectInfo", None),
                    )

    def unconditionalAttributeOwnershipDivestiture(self, theObject: JavaObjectInstanceHandle, theAttributes: Iterable[Any]) -> None:
        record = self._federation().objects[theObject]
        for attr in set(theAttributes):
            if record.attribute_owners.get(attr) == self.federate_handle:
                record.attribute_owners[attr] = None

    def negotiatedAttributeOwnershipDivestiture(
        self,
        theObject: JavaObjectInstanceHandle,
        theAttributes: Iterable[Any],
        userSuppliedTag: Any,
    ) -> None:
        federation = self._federation()
        record = federation.objects[theObject]
        attrs = set(theAttributes)
        record.negotiated_divestiture_attrs.update(attrs)
        tag = self._tag(userSuppliedTag)
        for federate in federation.federates_by_handle.values():
            if federate is self:
                continue
            federate._queue_callback("requestAttributeOwnershipAssumption", theObject, attrs, tag)

    def attributeOwnershipAcquisitionIfAvailable(self, theObject: JavaObjectInstanceHandle, desiredAttributes: Iterable[Any]) -> None:
        record = self._federation().objects[theObject]
        acquired = set()
        for attr in set(desiredAttributes):
            if record.attribute_owners.get(attr) is None:
                record.attribute_owners[attr] = self.federate_handle
                acquired.add(attr)
        if acquired:
            self._queue_callback("attributeOwnershipAcquisitionNotification", theObject, acquired, JavaByteArray(b""))

    def attributeOwnershipAcquisition(
        self,
        theObject: JavaObjectInstanceHandle,
        desiredAttributes: Iterable[Any],
        userSuppliedTag: Any,
    ) -> None:
        federation = self._federation()
        record = federation.objects[theObject]
        attrs = set(desiredAttributes)
        tag = self._tag(userSuppliedTag)
        owner = record.owner
        if owner is None:
            return
        for attr in attrs:
            record.pending_acquisitions[attr] = SharedJavaPendingAcquisition(self, tag)
        owner._queue_callback("requestAttributeOwnershipRelease", theObject, attrs, tag)
        negotiated = attrs & set(record.negotiated_divestiture_attrs)
        if negotiated:
            owner._queue_callback("requestDivestitureConfirmation", theObject, negotiated)
            self._queue_callback(
                "attributeOwnershipAcquisitionNotification",
                theObject,
                negotiated,
                JavaByteArray(b""),
            )

    def cancelAttributeOwnershipAcquisition(
        self,
        theObject: JavaObjectInstanceHandle,
        desiredAttributes: Iterable[Any],
    ) -> None:
        record = self._federation().objects[theObject]
        attrs = set(desiredAttributes)
        for attr in attrs:
            pending = record.pending_acquisitions.get(attr)
            if pending is not None and pending.requester is self:
                record.pending_acquisitions.pop(attr, None)
        self._queue_callback("confirmAttributeOwnershipAcquisitionCancellation", theObject, attrs)

    def attributeOwnershipDivestitureIfWanted(
        self,
        theObject: JavaObjectInstanceHandle,
        theAttributes: Iterable[Any],
    ) -> set[JavaAttributeHandle]:
        record = self._federation().objects[theObject]
        divested: set[JavaAttributeHandle] = set()
        for attr in set(theAttributes):
            pending = record.pending_acquisitions.get(attr)
            if pending is None:
                continue
            record.attribute_owners[attr] = pending.requester.federate_handle
            record.pending_acquisitions.pop(attr, None)
            record.negotiated_divestiture_attrs.discard(attr)
            divested.add(attr)
            pending.requester._queue_callback(
                "attributeOwnershipAcquisitionNotification",
                theObject,
                {attr},
                JavaByteArray(b""),
            )
        return divested

    def confirmDivestiture(
        self,
        theObject: JavaObjectInstanceHandle,
        theAttributes: Iterable[Any],
        userSuppliedTag: Any,
    ) -> None:
        record = self._federation().objects[theObject]
        tag = self._tag(userSuppliedTag)
        for attr in set(theAttributes):
            pending = record.pending_acquisitions.get(attr)
            if pending is None:
                continue
            record.attribute_owners[attr] = pending.requester.federate_handle
            record.pending_acquisitions.pop(attr, None)
            record.negotiated_divestiture_attrs.discard(attr)
            pending.requester._queue_callback(
                "attributeOwnershipAcquisitionNotification",
                theObject,
                {attr},
                tag,
            )

    def attributeOwnershipReleaseDenied(
        self,
        theObject: JavaObjectInstanceHandle,
        theAttributes: Iterable[Any],
    ) -> None:
        record = self._federation().objects[theObject]
        for attr in set(theAttributes):
            record.pending_acquisitions.pop(attr, None)
            record.negotiated_divestiture_attrs.discard(attr)

    def queryAttributeOwnership(self, theObject: JavaObjectInstanceHandle, theAttribute: JavaAttributeHandle) -> None:
        record = self._federation().objects[theObject]
        owner = record.attribute_owners.get(theAttribute)
        if owner is None:
            self._queue_callback("attributeIsNotOwned", theObject, theAttribute)
        else:
            self._queue_callback("informAttributeOwnership", theObject, theAttribute, owner)

    def isAttributeOwnedByFederate(self, theObject: JavaObjectInstanceHandle, theAttribute: JavaAttributeHandle) -> bool:
        return self._federation().objects[theObject].attribute_owners.get(theAttribute) == self.federate_handle

    def changeAttributeOrderType(
        self,
        theObject: JavaObjectInstanceHandle,
        theAttributes: Iterable[JavaAttributeHandle],
        theType: Any,
    ) -> None:
        record = self._federation().objects[theObject]
        for attr in set(theAttributes):
            if record.attribute_owners.get(attr) != self.federate_handle:
                raise JavaLikeException("AttributeNotOwned", str(theObject))
            self.attribute_order_overrides[(theObject, attr)] = str(theType)

    def changeInteractionOrderType(self, theClass: JavaInteractionClassHandle, theType: Any) -> None:
        self._federation()
        self.interaction_order_overrides[theClass] = str(theType)

    def deleteObjectInstance(self, theObject: JavaObjectInstanceHandle, userSuppliedTag: Any, *unused: Any) -> None:
        federation = self._federation()
        record = federation.objects[theObject]
        if record.owner is not self:
            raise JavaLikeException("DeletePrivilegeNotHeld", str(theObject))
        federation.objects.pop(theObject, None)
        federation.object_names.pop(record.name, None)
        for federate in federation.federates_by_handle.values():
            if federate is self:
                continue
            if record.class_handle in federate.subscribed_objects:
                federate._queue_callback(
                    "removeObjectInstance",
                    theObject,
                    self._tag(userSuppliedTag),
                    JavaEnumConstant("OrderType", "RECEIVE"),
                    JavaLikeObject("SupplementalRemoveInfo", None),
                )

    def requestAttributeValueUpdate(
        self,
        theObject: JavaObjectInstanceHandle,
        theAttributes: Iterable[JavaAttributeHandle],
        userSuppliedTag: Any = b"",
    ) -> None:
        federation = self._federation()
        record = federation.objects[theObject]
        owner = record.owner
        owner._queue_callback(
            "provideAttributeValueUpdate",
            theObject,
            set(theAttributes),
            self._tag(userSuppliedTag),
        )

    def sendInteraction(self, theInteraction: JavaInteractionClassHandle, theParameters: Mapping[Any, Any], userSuppliedTag: Any, *unused: Any) -> None:
        federation = self._federation()
        params = {key: JavaByteArray(python_bytes(value)) for key, value in dict(theParameters).items()}
        timestamp = unused[0] if unused else None
        for federate in federation.federates_by_handle.values():
            if federate is not self and theInteraction in federate.subscribed_interactions:
                if timestamp is not None and self.time_regulation_enabled and federate.time_constrained_enabled:
                    federate._queue_callback(
                        "receiveInteraction",
                        theInteraction,
                        params,
                        self._tag(userSuppliedTag),
                        JavaEnumConstant("OrderType", "TIMESTAMP"),
                        self.transportation_reliable,
                        make_java_time(federation.logical_time_name, time_value(timestamp)),
                        JavaEnumConstant("OrderType", "TIMESTAMP"),
                    )
                else:
                    federate._queue_callback(
                        "receiveInteraction",
                        theInteraction,
                        params,
                        self._tag(userSuppliedTag),
                        JavaEnumConstant("OrderType", "RECEIVE"),
                        self.transportation_reliable,
                        JavaLikeObject("SupplementalReceiveInfo", None),
                    )

    def enableTimeRegulation(self, theLookahead: Any) -> None:
        federation = self._federation()
        self.time_regulation_enabled = True
        self._queue_callback("timeRegulationEnabled", make_java_time(federation.logical_time_name, self.current_time))

    def enableTimeConstrained(self) -> None:
        federation = self._federation()
        self.time_constrained_enabled = True
        self._queue_callback("timeConstrainedEnabled", make_java_time(federation.logical_time_name, self.current_time))

    def timeAdvanceRequest(self, theTime: Any) -> None:
        federation = self._federation()
        self.current_time = time_value(theTime)
        self._queue_callback("timeAdvanceGrant", make_java_time(federation.logical_time_name, self.current_time))

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

    def createRegion(self, dimensions: Iterable[JavaDimensionHandle]) -> JavaRegionHandle:
        handle = self.kernel.alloc(JavaRegionHandle)
        self.kernel.regions[handle] = set(dimensions)
        return handle

    def commitRegionModifications(self, regions: Iterable[JavaRegionHandle]) -> None:
        return None

    def deleteRegion(self, theRegion: JavaRegionHandle) -> None:
        self.kernel.regions.pop(theRegion, None)

    def getFederateName(self, theHandle: JavaFederateHandle) -> str:
        return self._federation().federates_by_handle[theHandle].federate_name or ""

    def getFederateHandle(self, theName: str) -> JavaFederateHandle:
        return self._federation().federate_names[str(theName)]

    def normalizeFederateHandle(self, theHandle: JavaFederateHandle) -> JavaFederateHandle:
        return theHandle

    def getObjectClassHandle(self, theName: str) -> JavaObjectClassHandle:
        if theName not in self.kernel.object_classes:
            handle = self.kernel.alloc(JavaObjectClassHandle)
            self.kernel.object_classes[str(theName)] = handle
            self.kernel.object_class_names[handle] = str(theName)
        return self.kernel.object_classes[str(theName)]

    def getObjectClassName(self, theHandle: JavaObjectClassHandle) -> str:
        return self.kernel.object_class_names[theHandle]

    def getAttributeHandle(self, whichClass: JavaObjectClassHandle, theName: str) -> JavaAttributeHandle:
        key = (whichClass, str(theName))
        if key not in self.kernel.attributes:
            handle = self.kernel.alloc(JavaAttributeHandle)
            self.kernel.attributes[key] = handle
            self.kernel.attribute_names[(whichClass, handle)] = str(theName)
        return self.kernel.attributes[key]

    def getAttributeName(self, whichClass: JavaObjectClassHandle, theHandle: JavaAttributeHandle) -> str:
        return self.kernel.attribute_names[(whichClass, theHandle)]

    def getInteractionClassHandle(self, theName: str) -> JavaInteractionClassHandle:
        if theName not in self.kernel.interaction_classes:
            handle = self.kernel.alloc(JavaInteractionClassHandle)
            self.kernel.interaction_classes[str(theName)] = handle
            self.kernel.interaction_class_names[handle] = str(theName)
        return self.kernel.interaction_classes[str(theName)]

    def getInteractionClassName(self, theHandle: JavaInteractionClassHandle) -> str:
        return self.kernel.interaction_class_names[theHandle]

    def getParameterHandle(self, whichClass: JavaInteractionClassHandle, theName: str) -> JavaParameterHandle:
        key = (whichClass, str(theName))
        if key not in self.kernel.parameters:
            handle = self.kernel.alloc(JavaParameterHandle)
            self.kernel.parameters[key] = handle
            self.kernel.parameter_names[(whichClass, handle)] = str(theName)
        return self.kernel.parameters[key]

    def getParameterName(self, whichClass: JavaInteractionClassHandle, theHandle: JavaParameterHandle) -> str:
        return self.kernel.parameter_names[(whichClass, theHandle)]

    def getObjectInstanceHandle(self, theName: str) -> JavaObjectInstanceHandle:
        return self._federation().object_names[str(theName)]

    def getObjectInstanceName(self, theHandle: JavaObjectInstanceHandle) -> str:
        return self._federation().objects[theHandle].name

    def getKnownObjectClassHandle(self, theObject: JavaObjectInstanceHandle) -> JavaObjectClassHandle:
        return self._federation().objects[theObject].class_handle

    def getDimensionHandle(self, theName: str) -> JavaDimensionHandle:
        if theName not in self.kernel.dimensions:
            handle = self.kernel.alloc(JavaDimensionHandle)
            self.kernel.dimensions[str(theName)] = handle
            self.kernel.dimension_names[handle] = str(theName)
        return self.kernel.dimensions[str(theName)]

    def getDimensionName(self, theHandle: JavaDimensionHandle) -> str:
        return self.kernel.dimension_names[theHandle]

    def getHLAversion(self) -> str:
        return "HLA 1516-2010 shared Java-shaped shim"
