"""Object registration and name-management domain root."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol

from hla.rti1516e.exceptions import (
    InvalidObjectClassHandle,
    ObjectClassNotDefined,
    ObjectClassNotPublished,
    ObjectInstanceNameInUse,
)
from hla.rti1516e.handles import ObjectClassHandle, ObjectInstanceHandle
from .object_delivery import PythonRTIObjectDeliveryMixin
from .state import ObjectInstance

if TYPE_CHECKING:
    from .state import FederateState, FederationState


class _ObjectContext(Protocol):
    state: "FederateState"
    engine: Any

    def _require_joined(self) -> "FederationState": ...

    def _ensure_no_save_or_restore_in_progress(self, federation: "FederationState") -> None: ...

    def _deliver(self, target: "FederateState", method_name: str, *args: Any) -> None: ...

    def _ensure_known_object(self, subscriber: "FederateState", instance: ObjectInstance) -> ObjectClassHandle | None: ...

    def _subscriber_has_region_scoped_object_interest(self, subscriber: "FederateState", instance: ObjectInstance) -> bool: ...

    def _reconcile_object_attribute_scope(self, subscriber: "FederateState", instance: ObjectInstance) -> None: ...


if TYPE_CHECKING:
    class _ObjectMixinBase(PythonRTIObjectDeliveryMixin, _ObjectContext):
        pass
else:
    class _ObjectMixinBase(PythonRTIObjectDeliveryMixin):
        pass


class PythonRTIObjectMixin(_ObjectMixinBase):
    """HLA object naming/registration services plus delivery helpers."""

    def _svc_reserveObjectInstanceName(self, theObjectInstanceName: str) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        name = str(theObjectInstanceName)
        assert self.state.handle is not None
        if name in federation.object_names or name in federation.reserved_object_names:
            self._deliver(self.state, "objectInstanceNameReservationFailed", name)
            return
        federation.reserved_object_names[name] = self.state.handle
        self._deliver(self.state, "objectInstanceNameReservationSucceeded", name)

    def _svc_releaseObjectInstanceName(self, theObjectInstanceName: str) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        name = str(theObjectInstanceName)
        if federation.reserved_object_names.get(name) == self.state.handle:
            federation.reserved_object_names.pop(name, None)

    def _svc_reserveMultipleObjectInstanceName(
        self,
        theObjectInstanceNames: Iterable[str],
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        names = {str(name) for name in theObjectInstanceNames}
        assert self.state.handle is not None
        if not names or any(
            name in federation.object_names or name in federation.reserved_object_names
            for name in names
        ):
            self._deliver(self.state, "multipleObjectInstanceNameReservationFailed", names)
            return
        for name in names:
            federation.reserved_object_names[name] = self.state.handle
        self._deliver(self.state, "multipleObjectInstanceNameReservationSucceeded", names)

    def _svc_releaseMultipleObjectInstanceName(
        self,
        theObjectInstanceNames: Iterable[str],
    ) -> None:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        for name in {str(name) for name in theObjectInstanceNames}:
            if federation.reserved_object_names.get(name) == self.state.handle:
                federation.reserved_object_names.pop(name, None)

    def _svc_registerObjectInstance(
        self,
        theClass: ObjectClassHandle,
        theObjectName: str | None = None,
        *unused: Any,
    ) -> ObjectInstanceHandle:
        federation = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        try:
            self.engine.object_class_for_handle(theClass)
        except InvalidObjectClassHandle as exc:
            raise ObjectClassNotDefined(repr(theClass)) from exc
        if self.config.strict_object_publication and theClass not in self.state.published_objects:
            raise ObjectClassNotPublished(repr(theClass))
        if theObjectName is None:
            theObjectName = f"Object-{self.engine._next_values[ObjectInstanceHandle]}"
        with self.engine._lock:
            if str(theObjectName) in federation.object_names:
                raise ObjectInstanceNameInUse(str(theObjectName))
            reserved_by = federation.reserved_object_names.get(str(theObjectName))
            if reserved_by is not None and reserved_by != self.state.handle:
                raise ObjectInstanceNameInUse(str(theObjectName))
            handle = self.engine._alloc(ObjectInstanceHandle)
            assert self.state.handle is not None
            instance = ObjectInstance(
                handle=handle,
                class_handle=theClass,
                name=str(theObjectName),
                owner=self.state.handle,
            )
            federation.objects[handle] = instance
            federation.object_names[str(theObjectName)] = handle
            federation.reserved_object_names.pop(str(theObjectName), None)
            self.state.known_object_classes[handle] = theClass
            self.state.known_object_names[str(theObjectName)] = handle
            self.state.locally_deleted_objects.discard(handle)
            for federate in list(federation.federates.values()):
                if federate is self.state:
                    continue
                if self._ensure_known_object(federate, instance) is not None:
                    if not self._subscriber_has_region_scoped_object_interest(federate, instance):
                        self._reconcile_object_attribute_scope(federate, instance)
            return handle
